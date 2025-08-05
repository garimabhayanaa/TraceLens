import html
import re
import logging
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
import bleach

logger = logging.getLogger(__name__)

class DataSanitizationLayer:
    """
    Comprehensive data sanitization layer ensuring no sensitive data is permanently stored
    """
    
    def __init__(self):
        self.initialize_sanitization_rules()
        self.temporary_data_registry = {}  # Track temporary data for cleanup
        
    def initialize_sanitization_rules(self):
        """Initialize sanitization rules and patterns"""
        
        # Allowed HTML tags and attributes (very restrictive)
        self.allowed_tags = []  # No HTML tags allowed in our application
        self.allowed_attributes = {}
        
        # Input length limits
        self.input_limits = {
            'name': 100,
            'email': 254,  # RFC 5321 limit
            'url': 2048,   # Common browser limit
            'general_text': 1000
        }
        
        # Patterns for validation
        self.validation_patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'url': r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
            'name': r'^[a-zA-Z\s\-\.\']{1,100}$',  # Letters, spaces, hyphens, dots, apostrophes only
        }
        
        # Sensitive data patterns to detect and mask
        self.sensitive_patterns = {
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }
        
        # Dangerous patterns that should be completely removed
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'eval\s*\(',
            r'document\.',
            r'window\.',
            r'alert\s*\(',
            r'confirm\s*\(',
            r'prompt\s*\('
        ]
    
    def sanitize_analysis_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for sanitizing analysis request data
        """
        try:
            # Create temporary tracking ID for this request
            tracking_id = self._generate_tracking_id()
            
            # Sanitize each field
            sanitized_data = {
                'tracking_id': tracking_id,
                'name': self._sanitize_name(request_data.get('name', '')),
                'email': self._sanitize_email(request_data.get('email', '')),
                'social_links': self._sanitize_social_links(request_data.get('social_links', [])),
                'sanitization_metadata': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'version': '1.0',
                    'original_fields': list(request_data.keys())
                }
            }
            
            # Register for cleanup
            self._register_temporary_data(tracking_id, sanitized_data)
            
            # Log sanitization event (without sensitive data)
            logger.info(f"Data sanitized for tracking_id: {tracking_id}")
            
            return sanitized_data
            
        except Exception as e:
            logger.error(f"Data sanitization failed: {str(e)}")
            raise ValueError(f"Input validation failed: {str(e)}")
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name input"""
        if not isinstance(name, str):
            raise ValueError("Name must be a string")
        
        # Length check
        if len(name) > self.input_limits['name']:
            raise ValueError(f"Name too long (max {self.input_limits['name']} characters)")
        
        # Basic sanitization
        name = name.strip()
        if not name:
            raise ValueError("Name cannot be empty")
        
        # Remove dangerous patterns
        name = self._remove_dangerous_patterns(name)
        
        # HTML escape
        name = html.escape(name)
        
        # Remove non-printable characters
        name = ''.join(char for char in name if char.isprintable())
        
        # Validate pattern
        if not re.match(self.validation_patterns['name'], name):
            # More lenient check - allow international characters
            if not re.match(r'^[\w\s\-\.\']{1,100}$', name, re.UNICODE):
                raise ValueError("Name contains invalid characters")
        
        return name
    
    def _sanitize_email(self, email: str) -> str:
        """Sanitize email input"""
        if not isinstance(email, str):
            raise ValueError("Email must be a string")
        
        # Length check
        if len(email) > self.input_limits['email']:
            raise ValueError(f"Email too long (max {self.input_limits['email']} characters)")
        
        # Basic sanitization
        email = email.strip().lower()
        if not email:
            raise ValueError("Email cannot be empty")
        
        # Remove dangerous patterns
        email = self._remove_dangerous_patterns(email)
        
        # Validate email format
        if not re.match(self.validation_patterns['email'], email):
            raise ValueError("Invalid email format")
        
        # Additional email security checks
        if self._contains_suspicious_email_patterns(email):
            raise ValueError("Email contains suspicious patterns")
        
        return email
    
    def _sanitize_social_links(self, social_links: List[str]) -> List[str]:
        """Sanitize social media links"""
        if not isinstance(social_links, list):
            raise ValueError("Social links must be a list")
        
        if len(social_links) > 10:  # Reasonable limit
            raise ValueError("Too many social links (max 10)")
        
        sanitized_links = []
        
        for link in social_links:
            if not isinstance(link, str):
                continue  # Skip non-string entries
            
            link = link.strip()
            if not link:
                continue  # Skip empty strings
            
            # Length check
            if len(link) > self.input_limits['url']:
                logger.warning(f"URL too long, skipping: {link[:50]}...")
                continue
            
            # Remove dangerous patterns
            link = self._remove_dangerous_patterns(link)
            
            # Validate URL format
            if not self._is_valid_url(link):
                logger.warning(f"Invalid URL format, skipping: {link}")
                continue
            
            # Check for allowed domains (optional whitelist)
            if not self._is_allowed_domain(link):
                logger.warning(f"Domain not in whitelist, skipping: {link}")
                continue
            
            sanitized_links.append(link)
        
        return sanitized_links
    
    def _remove_dangerous_patterns(self, text: str) -> str:
        """Remove dangerous patterns from text"""
        for pattern in self.dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and security"""
        try:
            # Basic pattern check
            if not re.match(self.validation_patterns['url'], url):
                return False
            
            # Parse URL components
            parsed = urlparse(url)
            
            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Only allow HTTP and HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Security checks
            if any(suspicious in url.lower() for suspicious in ['localhost', '127.0.0.1', '0.0.0.0', 'file://']):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _is_allowed_domain(self, url: str) -> bool:
        """Check if domain is in allowed list"""
        allowed_domains = [
            'twitter.com', 'x.com', 'linkedin.com', 'github.com', 
            'instagram.com', 'facebook.com', 'youtube.com', 'tiktok.com',
            'reddit.com', 'discord.com', 'snapchat.com', 'pinterest.com',
            'behance.net', 'dribbble.com', 'medium.com', 'dev.to'
        ]
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain in allowed_domains
            
        except Exception:
            return False
    
    def _contains_suspicious_email_patterns(self, email: str) -> bool:
        """Check for suspicious patterns in email"""
        suspicious_patterns = [
            r'\.{2,}',  # Multiple consecutive dots
            r'^\.|\.$',  # Starting or ending with dot
            r'[<>"\']',  # HTML/script characters
            r'admin|root|test|noreply',  # Common system emails
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, email):
                return True
        
        return False
    
    def _generate_tracking_id(self) -> str:
        """Generate unique tracking ID for data lifecycle management"""
        return f"track_{secrets.token_hex(16)}_{int(datetime.utcnow().timestamp())}"
    
    def _register_temporary_data(self, tracking_id: str, data: Dict[str, Any]) -> None:
        """Register temporary data for cleanup"""
        self.temporary_data_registry[tracking_id] = {
            'data': data,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=1)  # 1 hour TTL
        }
    
    def sanitize_analysis_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize analysis results before returning to client"""
        
        # Remove raw ML analysis data
        if 'ml_analysis' in results:
            # Keep only summary statistics, remove raw text data
            ml_summary = {
                'confidence_scores': results['ml_analysis'].get('confidence_scores', {}),
                'method_used': results['ml_analysis'].get('method', 'unknown'),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            results['ml_analysis'] = ml_summary
        
        # Remove collection summary raw data
        if 'collection_summary' in results:
            collection_summary = results['collection_summary']
            # Keep only non-sensitive summary data
            sanitized_summary = {
                'sources_attempted': collection_summary.get('total_sources_attempted', 0),
                'successful_collections': collection_summary.get('successful_collections', 0),
                'success_rate': collection_summary.get('success_rate', 0),
                'platforms_identified': collection_summary.get('platforms_identified', [])
            }
            results['collection_summary'] = sanitized_summary
        
        # Mask any remaining sensitive patterns
        results = self._mask_sensitive_data(results)
        
        return results
    
    def _mask_sensitive_data(self, data: Any) -> Any:
        """Recursively mask sensitive data patterns"""
        if isinstance(data, dict):
            return {key: self._mask_sensitive_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            # Mask sensitive patterns
            masked_data = data
            for pattern_name, pattern in self.sensitive_patterns.items():
                if re.search(pattern, masked_data):
                    masked_data = re.sub(pattern, f'[MASKED_{pattern_name.upper()}]', masked_data)
            return masked_data
        else:
            return data
    
    def cleanup_temporary_data(self, tracking_id: Optional[str] = None) -> int:
        """Clean up temporary data - either specific ID or all expired"""
        cleaned_count = 0
        current_time = datetime.utcnow()
        
        if tracking_id:
            # Clean specific tracking ID
            if tracking_id in self.temporary_data_registry:
                # Securely overwrite data
                self._secure_delete_data(self.temporary_data_registry[tracking_id]['data'])
                del self.temporary_data_registry[tracking_id]
                cleaned_count = 1
                logger.info(f"Cleaned up data for tracking_id: {tracking_id}")
        else:
            # Clean all expired data
            expired_ids = [
                tid for tid, entry in self.temporary_data_registry.items()
                if entry['expires_at'] <= current_time
            ]
            
            for tid in expired_ids:
                self._secure_delete_data(self.temporary_data_registry[tid]['data'])
                del self.temporary_data_registry[tid]
                cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired data entries")
        
        return cleaned_count
    
    def _secure_delete_data(self, data: Any) -> None:
        """Securely delete sensitive data from memory"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    # Overwrite string data
                    data[key] = '0' * len(value)
                else:
                    self._secure_delete_data(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str):
                    data[i] = '0' * len(item)
                else:
                    self._secure_delete_data(item)
    
    def validate_file_upload(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Validate and sanitize file uploads (if needed)"""
        if len(file_data) > 5 * 1024 * 1024:  # 5MB limit
            raise ValueError("File too large")
        
        # Sanitize filename
        safe_filename = secure_filename(filename)
        if not safe_filename:
            raise ValueError("Invalid filename")
        
        # Check file type (whitelist approach)
        allowed_extensions = ['.txt', '.csv', '.json']
        if not any(safe_filename.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError("File type not allowed")
        
        return {
            'safe_filename': safe_filename,
            'size': len(file_data),
            'validated': True
        }
    
    def get_sanitization_report(self) -> Dict[str, Any]:
        """Generate sanitization status report"""
        current_time = datetime.utcnow()
        
        active_entries = sum(
            1 for entry in self.temporary_data_registry.values()
            if entry['expires_at'] > current_time
        )
        
        expired_entries = sum(
            1 for entry in self.temporary_data_registry.values()
            if entry['expires_at'] <= current_time
        )
        
        return {
            'total_entries': len(self.temporary_data_registry),
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'cleanup_needed': expired_entries > 0,
            'report_timestamp': current_time.isoformat()
        }

def create_sanitization_layer():
    """Factory function to create sanitization layer"""
    return DataSanitizationLayer()

# Utility functions for Flask integration
def sanitize_flask_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for Flask request sanitization"""
    sanitizer = create_sanitization_layer()
    return sanitizer.sanitize_analysis_request(request_data)

def cleanup_request_data(tracking_id: str) -> None:
    """Convenience function for cleaning up request data"""
    sanitizer = create_sanitization_layer()
    sanitizer.cleanup_temporary_data(tracking_id)
