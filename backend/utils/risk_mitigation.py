import logging
import hashlib
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import functools
import redis
from flask import Flask, request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField, TextAreaField, validators
from wtforms.validators import DataRequired, Length, ValidationError
import traceback
import sys
import uuid

logger = logging.getLogger(__name__)


@dataclass
class RiskMitigationConfig:
    """Configuration for risk mitigation strategies"""
    # Rate limiting configuration
    default_rate_limits: List[str] = None
    rate_limit_storage_url: str = "redis://localhost:6379/0"
    rate_limit_strategy: str = "fixed-window"

    # Input validation configuration
    max_input_length: int = 10000
    allowed_file_extensions: List[str] = None
    max_file_size_mb: int = 10
    enable_csrf_protection: bool = True

    # Error handling configuration
    generic_error_messages: bool = True
    log_detailed_errors: bool = True
    error_tracking_enabled: bool = True

    # Performance optimization configuration
    cache_ttl_seconds: int = 300
    max_cache_size: int = 1000
    enable_request_compression: bool = True

    def __post_init__(self):
        if self.default_rate_limits is None:
            self.default_rate_limits = ["200 per day", "50 per hour"]
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = ['.txt', '.json', '.csv']


class RateLimitingManager:
    """Advanced rate limiting with Flask-Limiter integration"""

    def __init__(self, app: Flask, config: RiskMitigationConfig):
        self.config = config
        self.app = app

        # Initialize Flask-Limiter with Redis backend
        try:
            self.limiter = Limiter(
                app=app,
                key_func=self._get_rate_limit_key,
                default_limits=config.default_rate_limits,
                storage_uri=config.rate_limit_storage_url,
                strategy=config.rate_limit_strategy,
                headers_enabled=True,
                on_breach=self._handle_rate_limit_breach
            )

            logger.info("Rate limiting initialized with Redis backend")

        except Exception as e:
            # Fallback to memory storage
            logger.warning(f"Redis unavailable, using memory storage: {str(e)}")
            self.limiter = Limiter(
                app=app,
                key_func=self._get_rate_limit_key,
                default_limits=config.default_rate_limits,
                storage_uri="memory://",
                strategy=config.rate_limit_strategy,
                headers_enabled=True,
                on_breach=self._handle_rate_limit_breach
            )

        # Track rate limit violations
        self.violation_tracker = defaultdict(list)
        self._lock = threading.Lock()

        # Set up custom rate limit decorators
        self._setup_rate_limit_decorators()

    def _get_rate_limit_key(self) -> str:
        """Get unique key for rate limiting (IP + User if available)"""

        # Primary identification by IP
        remote_addr = get_remote_address()

        # Add user identification if available
        user_id = getattr(g, 'user_id', None)
        if user_id:
            return f"{remote_addr}:{user_id}"

        # Add authorization token if available
        auth_header = request.headers.get('Authorization', '')
        if auth_header:
            token_hash = hashlib.md5(auth_header.encode()).hexdigest()[:8]
            return f"{remote_addr}:{token_hash}"

        return remote_addr

    def _handle_rate_limit_breach(self, request_limit):
        """Handle rate limit violations with enhanced tracking"""

        key = self._get_rate_limit_key()
        current_time = datetime.utcnow()

        with self._lock:
            self.violation_tracker[key].append({
                'timestamp': current_time.isoformat(),
                'limit': str(request_limit),
                'endpoint': request.endpoint,
                'user_agent': request.headers.get('User-Agent', '')
            })

            # Keep only last 100 violations per key
            if len(self.violation_tracker[key]) > 100:
                self.violation_tracker[key] = self.violation_tracker[key][-100:]

        # Log rate limit violation for security monitoring
        logger.warning(f"Rate limit violation: {key} exceeded {request_limit} on {request.endpoint}")

        # Additional security measures for repeated violations
        violations_last_hour = [
            v for v in self.violation_tracker[key]
            if datetime.fromisoformat(v['timestamp']) > current_time - timedelta(hours=1)
        ]

        if len(violations_last_hour) > 10:
            logger.critical(f"Potential abuse detected: {key} has {len(violations_last_hour)} violations in last hour")

    def _setup_rate_limit_decorators(self):
        """Set up custom rate limiting decorators for different endpoint types"""

        # Analysis endpoint - more restrictive
        self.analysis_limit = self.limiter.limit("10 per hour")

        # Identity verification - moderate limits
        self.verification_limit = self.limiter.limit("20 per hour")

        # General API endpoints
        self.api_limit = self.limiter.limit("100 per hour")

        # File upload endpoints - very restrictive
        self.upload_limit = self.limiter.limit("5 per hour")

        # Status/health check endpoints - generous limits
        self.status_limit = self.limiter.limit("1000 per hour")

    def get_rate_limit_decorator(self, endpoint_type: str):
        """Get appropriate rate limit decorator for endpoint type"""

        decorators = {
            'analysis': self.analysis_limit,
            'verification': self.verification_limit,
            'api': self.api_limit,
            'upload': self.upload_limit,
            'status': self.status_limit
        }

        return decorators.get(endpoint_type, self.api_limit)

    def get_violation_statistics(self) -> Dict[str, Any]:
        """Get rate limiting violation statistics"""

        current_time = datetime.utcnow()
        stats = {
            'total_violations': 0,
            'violations_last_hour': 0,
            'top_violators': [],
            'violation_patterns': defaultdict(int)
        }

        with self._lock:
            for key, violations in self.violation_tracker.items():
                stats['total_violations'] += len(violations)

                # Count violations in last hour
                recent_violations = [
                    v for v in violations
                    if datetime.fromisoformat(v['timestamp']) > current_time - timedelta(hours=1)
                ]

                if recent_violations:
                    stats['violations_last_hour'] += len(recent_violations)
                    stats['top_violators'].append({
                        'key': key,
                        'recent_violations': len(recent_violations),
                        'total_violations': len(violations)
                    })

                    # Track violation patterns
                    for violation in recent_violations:
                        stats['violation_patterns'][violation['endpoint']] += 1

        # Sort top violators
        stats['top_violators'].sort(key=lambda x: x['recent_violations'], reverse=True)
        stats['top_violators'] = stats['top_violators'][:10]

        return dict(stats)


class InputValidationManager:
    """Advanced input validation using Flask-WTF"""

    def __init__(self, app: Flask, config: RiskMitigationConfig):
        self.config = config
        self.app = app

        # Initialize CSRF protection
        if config.enable_csrf_protection:
            self.csrf = CSRFProtect(app)
            logger.info("CSRF protection enabled")

        # Define validation forms
        self._setup_validation_forms()

        # Track validation failures
        self.validation_failures = defaultdict(list)
        self._lock = threading.Lock()

    def _setup_validation_forms(self):
        """Set up validation forms for different data types"""

        class SocialMediaAnalysisForm(FlaskForm):
            user_id = StringField('User ID', [
                DataRequired(),
                Length(min=1, max=100),
                self._validate_user_id
            ])

            user_email = StringField('User Email', [
                DataRequired(),
                validators.Email(),
                Length(max=254)
            ])

            analysis_type = StringField('Analysis Type', [
                DataRequired(),
                self._validate_analysis_type
            ])

            target_data_description = TextAreaField('Target Data Description', [
                DataRequired(),
                Length(min=10, max=self.config.max_input_length),
                self._validate_safe_content
            ])

            use_case_description = TextAreaField('Use Case Description', [
                DataRequired(),
                Length(min=20, max=self.config.max_input_length),
                self._validate_safe_content
            ])

            privacy_level = StringField('Privacy Level', [
                DataRequired(),
                self._validate_privacy_level
            ])

        class IdentityVerificationForm(FlaskForm):
            verification_code = StringField('Verification Code', [
                DataRequired(),
                Length(min=6, max=6),
                self._validate_verification_code
            ])

            user_id = StringField('User ID', [
                DataRequired(),
                Length(min=1, max=100),
                self._validate_user_id
            ])

        class ConsentForm(FlaskForm):
            consent_type = StringField('Consent Type', [
                DataRequired(),
                self._validate_consent_type
            ])

            granted = StringField('Granted', [
                DataRequired(),
                self._validate_boolean_string
            ])

        self.forms = {
            'social_analysis': SocialMediaAnalysisForm,
            'identity_verification': IdentityVerificationForm,
            'consent': ConsentForm
        }

    def _validate_user_id(self, field):
        """Validate user ID format"""
        value = field.data

        # Check for malicious patterns
        if any(pattern in value.lower() for pattern in ['<script', 'javascript:', 'data:', '../', '<iframe']):
            raise ValidationError('Invalid user ID format')

        # Check for SQL injection patterns
        sql_patterns = ['union', 'select', 'drop', 'delete', 'insert', 'update', '--', ';']
        if any(pattern in value.lower() for pattern in sql_patterns):
            raise ValidationError('Invalid user ID format')

        # Only allow alphanumeric, dashes, underscores
        if not all(c.isalnum() or c in '-_@.' for c in value):
            raise ValidationError('User ID contains invalid characters')

    def _validate_analysis_type(self, field):
        """Validate analysis type"""
        valid_types = ['self_analysis', 'third_party_analysis', 'research_analysis', 'security_analysis']
        if field.data not in valid_types:
            raise ValidationError(f'Invalid analysis type. Must be one of: {", ".join(valid_types)}')

    def _validate_privacy_level(self, field):
        """Validate privacy level"""
        valid_levels = ['minimal', 'standard', 'strict']
        if field.data not in valid_levels:
            raise ValidationError(f'Invalid privacy level. Must be one of: {", ".join(valid_levels)}')

    def _validate_consent_type(self, field):
        """Validate consent type"""
        valid_types = [
            'data_collection', 'data_processing', 'analysis_inference',
            'data_retention', 'result_storage', 'third_party_sharing'
        ]
        if field.data not in valid_types:
            raise ValidationError(f'Invalid consent type. Must be one of: {", ".join(valid_types)}')

    def _validate_boolean_string(self, field):
        """Validate boolean string"""
        if field.data.lower() not in ['true', 'false']:
            raise ValidationError('Value must be "true" or "false"')

    def _validate_verification_code(self, field):
        """Validate verification code format"""
        value = field.data

        if not value.isdigit():
            raise ValidationError('Verification code must contain only digits')

        if len(value) != 6:
            raise ValidationError('Verification code must be exactly 6 digits')

    def _validate_safe_content(self, field):
        """Validate content for safety (XSS, injection attempts)"""
        value = field.data.lower()

        # Check for XSS patterns
        xss_patterns = [
            '<script', '</script>', 'javascript:', 'onload=', 'onerror=',
            '<iframe', '</iframe>', 'eval(', 'alert(', 'document.cookie'
        ]

        for pattern in xss_patterns:
            if pattern in value:
                raise ValidationError('Content contains potentially unsafe elements')

        # Check for common injection patterns
        injection_patterns = [
            'union select', 'drop table', 'delete from', 'insert into',
            '<?php', '<%', '${', '#{', 'exec(', 'system('
        ]

        for pattern in injection_patterns:
            if pattern in value:
                raise ValidationError('Content contains potentially unsafe elements')

    def validate_request_data(self, form_type: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate request data using appropriate form"""

        if form_type not in self.forms:
            return False, [f'Unknown form type: {form_type}']

        form_class = self.forms[form_type]
        form = form_class(data=data)

        if form.validate():
            return True, []
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f'{field}: {error}')

            # Track validation failures for security monitoring
            self._track_validation_failure(form_type, errors, data)

            return False, errors

    def _track_validation_failure(self, form_type: str, errors: List[str], data: Dict[str, Any]):
        """Track validation failures for security monitoring"""

        failure_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'form_type': form_type,
            'errors': errors,
            'ip_address': get_remote_address(),
            'user_agent': request.headers.get('User-Agent', ''),
            'data_preview': {k: str(v)[:50] for k, v in data.items()}  # Truncated data
        }

        with self._lock:
            self.validation_failures[get_remote_address()].append(failure_record)

            # Keep only last 50 failures per IP
            if len(self.validation_failures[get_remote_address()]) > 50:
                self.validation_failures[get_remote_address()] = \
                    self.validation_failures[get_remote_address()][-50:]

        logger.warning(f"Validation failure: {form_type} from {get_remote_address()}")

    def sanitize_input(self, text: str) -> str:
        """Sanitize text input to prevent XSS and injection attacks"""

        if not text:
            return ""

        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '`', '(', ')', '{', '}', '[', ']']
        sanitized = text

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        # Remove multiple whitespaces
        sanitized = ' '.join(sanitized.split())

        # Truncate if too long
        if len(sanitized) > self.config.max_input_length:
            sanitized = sanitized[:self.config.max_input_length]

        return sanitized

    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get input validation statistics"""

        current_time = datetime.utcnow()
        stats = {
            'total_failures': 0,
            'failures_last_hour': 0,
            'top_failing_ips': [],
            'common_error_types': defaultdict(int)
        }

        with self._lock:
            for ip, failures in self.validation_failures.items():
                stats['total_failures'] += len(failures)

                # Count recent failures
                recent_failures = [
                    f for f in failures
                    if datetime.fromisoformat(f['timestamp']) > current_time - timedelta(hours=1)
                ]

                if recent_failures:
                    stats['failures_last_hour'] += len(recent_failures)
                    stats['top_failing_ips'].append({
                        'ip': ip,
                        'recent_failures': len(recent_failures),
                        'total_failures': len(failures)
                    })

                    # Track error types
                    for failure in recent_failures:
                        for error in failure['errors']:
                            stats['common_error_types'][error.split(':')[0]] += 1

        # Sort top failing IPs
        stats['top_failing_ips'].sort(key=lambda x: x['recent_failures'], reverse=True)
        stats['top_failing_ips'] = stats['top_failing_ips'][:10]

        return dict(stats)


class ErrorHandlingManager:
    """Graceful error handling with generic messages and detailed logging"""

    def __init__(self, app: Flask, config: RiskMitigationConfig):
        self.config = config
        self.app = app

        # Error tracking
        self.error_tracker = defaultdict(list)
        self._lock = threading.Lock()

        # Set up error handlers
        self._setup_error_handlers()

        # Set up request/response logging
        if config.log_detailed_errors:
            self._setup_request_logging()

    def _setup_error_handlers(self):
        """Set up comprehensive error handlers"""

        @self.app.errorhandler(400)
        def handle_bad_request(error):
            return self._create_error_response(
                error_code='BAD_REQUEST',
                message='Invalid request data provided',
                status_code=400,
                details=str(error) if not self.config.generic_error_messages else None
            )

        @self.app.errorhandler(401)
        def handle_unauthorized(error):
            return self._create_error_response(
                error_code='UNAUTHORIZED',
                message='Authentication required',
                status_code=401
            )

        @self.app.errorhandler(403)
        def handle_forbidden(error):
            return self._create_error_response(
                error_code='FORBIDDEN',
                message='Access denied',
                status_code=403
            )

        @self.app.errorhandler(404)
        def handle_not_found(error):
            return self._create_error_response(
                error_code='NOT_FOUND',
                message='Resource not found',
                status_code=404
            )

        @self.app.errorhandler(429)
        def handle_rate_limit(error):
            return self._create_error_response(
                error_code='RATE_LIMITED',
                message='Too many requests. Please try again later',
                status_code=429,
                headers={'Retry-After': '3600'}
            )

        @self.app.errorhandler(500)
        def handle_internal_error(error):
            return self._create_error_response(
                error_code='INTERNAL_ERROR',
                message='An internal error occurred',
                status_code=500,
                details=str(error) if not self.config.generic_error_messages else None
            )

        @self.app.errorhandler(503)
        def handle_service_unavailable(error):
            return self._create_error_response(
                error_code='SERVICE_UNAVAILABLE',
                message='Service temporarily unavailable',
                status_code=503
            )

        # Handle validation errors
        @self.app.errorhandler(ValidationError)
        def handle_validation_error(error):
            return self._create_error_response(
                error_code='VALIDATION_ERROR',
                message='Input validation failed',
                status_code=422,
                details=str(error) if not self.config.generic_error_messages else None
            )

        # Handle generic exceptions
        @self.app.errorhandler(Exception)
        def handle_generic_exception(error):
            # Log detailed error information
            self._log_detailed_error(error)

            return self._create_error_response(
                error_code='UNEXPECTED_ERROR',
                message='An unexpected error occurred',
                status_code=500
            )

    def _create_error_response(self, error_code: str, message: str, status_code: int,
                               details: str = None, headers: Dict[str, str] = None):
        """Create standardized error response"""

        error_id = str(uuid.uuid4())

        response_data = {
            'error': {
                'code': error_code,
                'message': message,
                'timestamp': datetime.utcnow().isoformat(),
                'error_id': error_id,
                'status': status_code
            }
        }

        # Add details for debugging (only if not in generic mode)
        if details and not self.config.generic_error_messages:
            response_data['error']['details'] = details

        # Add request context
        response_data['error']['request'] = {
            'method': request.method,
            'endpoint': request.endpoint,
            'user_agent': request.headers.get('User-Agent', '')[:100]  # Truncated
        }

        # Track error
        self._track_error(error_code, status_code, error_id)

        # Create response
        response = jsonify(response_data)
        response.status_code = status_code

        # Add custom headers
        if headers:
            for key, value in headers.items():
                response.headers[key] = value

        return response

    def _log_detailed_error(self, error: Exception):
        """Log detailed error information for debugging"""

        if not self.config.log_detailed_errors:
            return

        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'request': {
                'method': request.method,
                'url': request.url,
                'endpoint': request.endpoint,
                'remote_addr': get_remote_address(),
                'user_agent': request.headers.get('User-Agent', ''),
                'headers': dict(request.headers)
            },
            'traceback': traceback.format_exc()
        }

        logger.error(f"Detailed error: {json.dumps(error_details, indent=2)}")

    def _track_error(self, error_code: str, status_code: int, error_id: str):
        """Track error occurrence for monitoring"""

        error_record = {
            'error_id': error_id,
            'error_code': error_code,
            'status_code': status_code,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': get_remote_address(),
            'endpoint': request.endpoint,
            'user_agent': request.headers.get('User-Agent', '')
        }

        with self._lock:
            self.error_tracker[error_code].append(error_record)

            # Keep only last 1000 errors per code
            if len(self.error_tracker[error_code]) > 1000:
                self.error_tracker[error_code] = self.error_tracker[error_code][-1000:]

    def _setup_request_logging(self):
        """Set up request and response logging"""

        @self.app.before_request
        def log_request_info():
            g.request_start_time = time.time()

            if self.config.log_detailed_errors:
                logger.info(f"Request: {request.method} {request.url} from {get_remote_address()}")

        @self.app.after_request
        def log_response_info(response):
            if hasattr(g, 'request_start_time'):
                duration = time.time() - g.request_start_time

                if self.config.log_detailed_errors:
                    logger.info(f"Response: {response.status_code} in {duration:.3f}s")

            return response

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error handling statistics"""

        current_time = datetime.utcnow()
        stats = {
            'total_errors': 0,
            'errors_last_hour': 0,
            'error_distribution': defaultdict(int),
            'top_error_endpoints': defaultdict(int),
            'error_trends': []
        }

        with self._lock:
            for error_code, errors in self.error_tracker.items():
                stats['total_errors'] += len(errors)
                stats['error_distribution'][error_code] = len(errors)

                # Count recent errors
                recent_errors = [
                    e for e in errors
                    if datetime.fromisoformat(e['timestamp']) > current_time - timedelta(hours=1)
                ]

                stats['errors_last_hour'] += len(recent_errors)

                # Track endpoint distribution
                for error in recent_errors:
                    if error['endpoint']:
                        stats['top_error_endpoints'][error['endpoint']] += 1

        return dict(stats)


class PerformanceOptimizer:
    """Performance optimization with caching and efficient algorithms"""

    def __init__(self, config: RiskMitigationConfig):
        self.config = config

        # Initialize cache
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_access_count = defaultdict(int)
        self._cache_lock = threading.RLock()

        # Performance metrics
        self.performance_metrics = defaultdict(list)
        self._metrics_lock = threading.Lock()

    def cache_decorator(self, ttl_seconds: int = None):
        """Caching decorator for expensive function calls"""

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key
                cache_key = self._create_cache_key(func.__name__, args, kwargs)

                # Check cache
                cached_result = self._get_from_cache(cache_key, ttl_seconds or self.config.cache_ttl_seconds)
                if cached_result is not None:
                    return cached_result

                # Execute function and cache result
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Cache the result
                self._store_in_cache(cache_key, result)

                # Track performance
                self._track_performance(func.__name__, execution_time, True)

                return result

            return wrapper

        return decorator

    def _create_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Create unique cache key for function call"""

        # Create a deterministic key from function name and arguments
        key_data = {
            'function': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }

        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str, ttl_seconds: int) -> Optional[Any]:
        """Get result from cache if valid"""

        with self._cache_lock:
            if cache_key not in self.cache:
                return None

            # Check if cache entry is still valid
            cache_time = self.cache_timestamps.get(cache_key)
            if cache_time and time.time() - cache_time > ttl_seconds:
                # Cache expired
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
                return None

            # Update access count
            self.cache_access_count[cache_key] += 1

            return self.cache[cache_key]

    def _store_in_cache(self, cache_key: str, result: Any):
        """Store result in cache with LRU eviction"""

        with self._cache_lock:
            # Check cache size and evict if necessary
            if len(self.cache) >= self.config.max_cache_size:
                self._evict_lru_entries()

            self.cache[cache_key] = result
            self.cache_timestamps[cache_key] = time.time()
            self.cache_access_count[cache_key] = 1

    def _evict_lru_entries(self):
        """Evict least recently used cache entries"""

        # Remove 20% of cache entries with lowest access count
        entries_to_remove = max(1, int(self.config.max_cache_size * 0.2))

        # Sort by access count
        sorted_entries = sorted(self.cache_access_count.items(), key=lambda x: x[1])

        for cache_key, _ in sorted_entries[:entries_to_remove]:
            if cache_key in self.cache:
                del self.cache[cache_key]
            if cache_key in self.cache_timestamps:
                del self.cache_timestamps[cache_key]
            if cache_key in self.cache_access_count:
                del self.cache_access_count[cache_key]

    def _track_performance(self, function_name: str, execution_time: float, cache_miss: bool):
        """Track function performance metrics"""

        metric = {
            'timestamp': datetime.utcnow().isoformat(),
            'function_name': function_name,
            'execution_time': execution_time,
            'cache_miss': cache_miss
        }

        with self._metrics_lock:
            self.performance_metrics[function_name].append(metric)

            # Keep only last 1000 metrics per function
            if len(self.performance_metrics[function_name]) > 1000:
                self.performance_metrics[function_name] = \
                    self.performance_metrics[function_name][-1000:]

    def clear_cache(self):
        """Clear all cached data"""

        with self._cache_lock:
            self.cache.clear()
            self.cache_timestamps.clear()
            self.cache_access_count.clear()

        logger.info("Performance cache cleared")

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""

        with self._cache_lock:
            total_accesses = sum(self.cache_access_count.values())

            stats = {
                'cache_size': len(self.cache),
                'max_cache_size': self.config.max_cache_size,
                'total_cache_accesses': total_accesses,
                'cache_utilization': len(self.cache) / self.config.max_cache_size,
                'most_accessed_entries': sorted(
                    self.cache_access_count.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }

        return stats

    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get performance optimization statistics"""

        stats = {
            'total_tracked_functions': len(self.performance_metrics),
            'function_performance': {}
        }

        with self._metrics_lock:
            for function_name, metrics in self.performance_metrics.items():
                if metrics:
                    execution_times = [m['execution_time'] for m in metrics]
                    cache_hits = sum(1 for m in metrics if not m['cache_miss'])

                    stats['function_performance'][function_name] = {
                        'total_calls': len(metrics),
                        'cache_hits': cache_hits,
                        'cache_hit_rate': cache_hits / len(metrics),
                        'average_execution_time': sum(execution_times) / len(execution_times),
                        'min_execution_time': min(execution_times),
                        'max_execution_time': max(execution_times)
                    }

        return stats


class RiskMitigationFramework:
    """Main framework coordinating all risk mitigation strategies"""

    def __init__(self, app: Flask, config: RiskMitigationConfig = None):
        self.app = app
        self.config = config or RiskMitigationConfig()

        # Initialize all risk mitigation components
        self.rate_limiter = RateLimitingManager(app, self.config)
        self.input_validator = InputValidationManager(app, self.config)
        self.error_handler = ErrorHandlingManager(app, self.config)
        self.performance_optimizer = PerformanceOptimizer(self.config)

        logger.info("Risk Mitigation Framework initialized with all components")

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all risk mitigation strategies"""

        return {
            'risk_mitigation_enabled': True,
            'components': {
                'rate_limiting': True,
                'input_validation': True,
                'error_handling': True,
                'performance_optimization': True
            },
            'statistics': {
                'rate_limiting': self.rate_limiter.get_violation_statistics(),
                'input_validation': self.input_validator.get_validation_statistics(),
                'error_handling': self.error_handler.get_error_statistics(),
                'cache_performance': self.performance_optimizer.get_cache_statistics(),
                'performance_metrics': self.performance_optimizer.get_performance_statistics()
            },
            'configuration': {
                'rate_limits': self.config.default_rate_limits,
                'max_input_length': self.config.max_input_length,
                'cache_ttl_seconds': self.config.cache_ttl_seconds,
                'generic_error_messages': self.config.generic_error_messages,
                'csrf_protection_enabled': self.config.enable_csrf_protection
            },
            'security_features': [
                'Rate limiting with Redis backend',
                'Advanced input validation and sanitization',
                'XSS and injection attack prevention',
                'CSRF protection',
                'Comprehensive error handling',
                'Security monitoring and tracking',
                'Performance optimization with caching',
                'Request/response logging',
                'Abuse detection and prevention'
            ]
        }


def create_risk_mitigation_framework(app: Flask, config: RiskMitigationConfig = None) -> RiskMitigationFramework:
    """Factory function to create risk mitigation framework"""
    return RiskMitigationFramework(app, config)
