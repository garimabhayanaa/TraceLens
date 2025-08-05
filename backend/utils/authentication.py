import secrets
import hashlib
import re
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any
from flask import current_app, request, session, jsonify, g
from flask_login import UserMixin, current_user, login_user, logout_user
from flask_limiter import Limiter
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

logger = logging.getLogger(__name__)

class SecureAuthenticationSystem:
    """
    Enterprise-grade authentication system with advanced security features
    """
    
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.failed_login_attempts = {}  # Track failed attempts
        self.session_store = {}  # Active session tracking
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the authentication system with Flask app"""
        self.app = app
        
        # Security configuration
        app.config.setdefault('AUTH_HASH_ALGORITHM', 'pbkdf2:sha256:100000')
        app.config.setdefault('AUTH_SALT_LENGTH', 32)
        app.config.setdefault('AUTH_SESSION_TIMEOUT', 30)  # minutes
        app.config.setdefault('AUTH_MAX_LOGIN_ATTEMPTS', 5)
        app.config.setdefault('AUTH_LOCKOUT_DURATION', 15)  # minutes
        app.config.setdefault('AUTH_PASSWORD_MIN_LENGTH', 8)
        app.config.setdefault('AUTH_REQUIRE_EMAIL_VERIFICATION', True)
        app.config.setdefault('AUTH_ENABLE_2FA', False)
        app.config.setdefault('AUTH_SESSION_PROTECTION', 'strong')
        
        # Initialize serializer for secure tokens
        self.serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """
        Hash password using secure algorithm with salt
        Returns (hashed_password, salt)
        """
        if not salt:
            salt = secrets.token_hex(current_app.config['AUTH_SALT_LENGTH'])
        
        # Use PBKDF2 with SHA-256 (secure and recommended)
        hashed = generate_password_hash(
            password, 
            method=current_app.config['AUTH_HASH_ALGORITHM'],
            salt_length=len(salt.encode())
        )
        
        return hashed, salt
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return check_password_hash(hashed_password, password)
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength according to security policies
        """
        errors = []
        score = 0
        
        # Length check
        if len(password) < current_app.config['AUTH_PASSWORD_MIN_LENGTH']:
            errors.append(f"Password must be at least {current_app.config['AUTH_PASSWORD_MIN_LENGTH']} characters long")
        else:
            score += 1
        
        # Character diversity checks
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        else:
            score += 1
            
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        else:
            score += 1
            
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        else:
            score += 1
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        else:
            score += 1
        
        # Common password check
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        ]
        if password.lower() in common_passwords:
            errors.append("Password is too common")
            score -= 2
        
        # Strength assessment
        if score >= 4:
            strength = 'strong'
        elif score >= 2:
            strength = 'moderate'
        else:
            strength = 'weak'
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'strength': strength,
            'score': max(0, score)
        }
    
    def register_user(self, email: str, password: str, name: str, **kwargs) -> Dict[str, Any]:
        """
        Secure user registration with validation
        """
        try:
            # Import here to avoid circular imports
            from app import User, db
            
            # Validate email format
            if not self._is_valid_email(email):
                return {'success': False, 'error': 'Invalid email format'}
            
            # Check if user already exists
            if User.query.filter_by(email=email.lower()).first():
                return {'success': False, 'error': 'Email already registered'}
            
            # Validate password strength
            password_validation = self.validate_password_strength(password)
            if not password_validation['is_valid']:
                return {
                    'success': False, 
                    'error': 'Password does not meet security requirements',
                    'details': password_validation['errors']
                }
            
            # Hash password
            hashed_password, salt = self.hash_password(password)
            
            # Create user
            user = User(
                email=email.lower(),
                name=name,
                password_hash=hashed_password,
                created_at=datetime.utcnow(),
                verified=not current_app.config['AUTH_REQUIRE_EMAIL_VERIFICATION'],
                verification_token=secrets.token_urlsafe(32) if current_app.config['AUTH_REQUIRE_EMAIL_VERIFICATION'] else None,
                **kwargs
            )
            
            db.session.add(user)
            db.session.commit()
            
            result = {
                'success': True,
                'user_id': user.id,
                'requires_verification': current_app.config['AUTH_REQUIRE_EMAIL_VERIFICATION']
            }
            
            if current_app.config['AUTH_REQUIRE_EMAIL_VERIFICATION']:
                result['verification_token'] = user.verification_token
            
            logger.info(f"User registered successfully: {email}")
            return result
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return {'success': False, 'error': 'Registration failed'}
    
    def authenticate_user(self, email: str, password: str, remember: bool = False) -> Dict[str, Any]:
        """
        Secure user authentication with rate limiting and security checks
        """
        try:
            # Import here to avoid circular imports
            from app import User
            
            client_ip = self._get_client_ip()
            
            # Check for rate limiting
            if self._is_rate_limited(client_ip, email):
                return {
                    'success': False, 
                    'error': 'Too many failed login attempts. Please try again later.',
                    'locked_until': self._get_lockout_expiry(client_ip, email)
                }
            
            # Find user
            user = User.query.filter_by(email=email.lower()).first()
            
            if not user:
                self._record_failed_attempt(client_ip, email)
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Check if account is verified
            if current_app.config['AUTH_REQUIRE_EMAIL_VERIFICATION'] and not user.verified:
                return {'success': False, 'error': 'Please verify your email address'}
            
            # Check if account is active
            if not user.is_active:
                return {'success': False, 'error': 'Account is disabled'}
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                self._record_failed_attempt(client_ip, email)
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Clear failed attempts on successful login
            self._clear_failed_attempts(client_ip, email)
            
            # Create secure session
            session_token = self._create_user_session(user, remember)
            
            # Log user in
            login_user(user, remember=remember)
            
            # Log successful login
            logger.info(f"User logged in successfully: {email}")
            
            return {
                'success': True,
                'user_id': user.id,
                'session_token': session_token,
                'expires_at': self._get_session_expiry(remember)
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {'success': False, 'error': 'Authentication failed'}
    
    def logout_user(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Secure user logout with session cleanup
        """
        try:
            # Get user ID from current user if not provided
            if not user_id and current_user.is_authenticated:
                user_id = current_user.id
            
            # Clear user session
            if user_id:
                self._invalidate_user_sessions(user_id)
            
            # Flask-Login logout
            logout_user()
            
            # Clear Flask session
            session.clear()
            
            logger.info(f"User logged out successfully: {user_id}")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return {'success': False, 'error': 'Logout failed'}
    
    def verify_session(self, session_token: str) -> Dict[str, Any]:
        """
        Verify and validate user session
        """
        try:
            if not session_token or session_token not in self.session_store:
                return {'valid': False, 'error': 'Invalid session'}
            
            session_data = self.session_store[session_token]
            
            # Check expiry
            if datetime.utcnow() > session_data['expires_at']:
                del self.session_store[session_token]
                return {'valid': False, 'error': 'Session expired'}
            
            # Session protection checks
            if current_app.config['AUTH_SESSION_PROTECTION'] == 'strong':
                if not self._verify_session_fingerprint(session_data):
                    del self.session_store[session_token]
                    return {'valid': False, 'error': 'Session security violation'}
            
            return {
                'valid': True,
                'user_id': session_data['user_id'],
                'expires_at': session_data['expires_at']
            }
            
        except Exception as e:
            logger.error(f"Session verification error: {str(e)}")
            return {'valid': False, 'error': 'Session verification failed'}
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> Dict[str, Any]:
        """
        Secure password change with validation
        """
        try:
            # Import here to avoid circular imports
            from app import User, db
            
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Verify current password
            if not self.verify_password(current_password, user.password_hash):
                return {'success': False, 'error': 'Current password is incorrect'}
            
            # Validate new password strength
            password_validation = self.validate_password_strength(new_password)
            if not password_validation['is_valid']:
                return {
                    'success': False,
                    'error': 'New password does not meet security requirements',
                    'details': password_validation['errors']
                }
            
            # Check if new password is different from current
            if self.verify_password(new_password, user.password_hash):
                return {'success': False, 'error': 'New password must be different from current password'}
            
            # Hash new password
            hashed_password, _ = self.hash_password(new_password)
            
            # Update password
            user.password_hash = hashed_password
            user.password_changed_at = datetime.utcnow()
            db.session.commit()
            
            # Invalidate all user sessions (force re-login)
            self._invalidate_user_sessions(user_id)
            
            logger.info(f"Password changed successfully for user: {user.email}")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            return {'success': False, 'error': 'Password change failed'}
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _get_client_ip(self) -> str:
        """Get client IP address with proxy support"""
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            return request.environ['REMOTE_ADDR']
        else:
            return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    
    def _is_rate_limited(self, client_ip: str, email: str) -> bool:
        """Check if client is rate limited"""
        key = f"{client_ip}:{email}"
        
        if key not in self.failed_login_attempts:
            return False
        
        attempts_data = self.failed_login_attempts[key]
        
        # Check if lockout period has expired
        if datetime.utcnow() > attempts_data['locked_until']:
            del self.failed_login_attempts[key]
            return False
        
        return attempts_data['count'] >= current_app.config['AUTH_MAX_LOGIN_ATTEMPTS']
    
    def _record_failed_attempt(self, client_ip: str, email: str) -> None:
        """Record failed login attempt"""
        key = f"{client_ip}:{email}"
        current_time = datetime.utcnow()
        
        if key not in self.failed_login_attempts:
            self.failed_login_attempts[key] = {
                'count': 0,
                'first_attempt': current_time,
                'locked_until': current_time
            }
        
        self.failed_login_attempts[key]['count'] += 1
        
        # Set lockout period if max attempts reached
        if self.failed_login_attempts[key]['count'] >= current_app.config['AUTH_MAX_LOGIN_ATTEMPTS']:
            lockout_duration = timedelta(minutes=current_app.config['AUTH_LOCKOUT_DURATION'])
            self.failed_login_attempts[key]['locked_until'] = current_time + lockout_duration
    
    def _clear_failed_attempts(self, client_ip: str, email: str) -> None:
        """Clear failed login attempts on successful login"""
        key = f"{client_ip}:{email}"
        if key in self.failed_login_attempts:
            del self.failed_login_attempts[key]
    
    def _get_lockout_expiry(self, client_ip: str, email: str) -> Optional[datetime]:
        """Get lockout expiry time"""
        key = f"{client_ip}:{email}"
        if key in self.failed_login_attempts:
            return self.failed_login_attempts[key]['locked_until']
        return None
    
    def _create_user_session(self, user, remember: bool = False) -> str:
        """Create secure user session"""
        session_token = secrets.token_urlsafe(32)
        
        # Set session expiry
        if remember:
            expires_at = datetime.utcnow() + timedelta(days=30)
        else:
            expires_at = datetime.utcnow() + timedelta(minutes=current_app.config['AUTH_SESSION_TIMEOUT'])
        
        # Store session data
        self.session_store[session_token] = {
            'user_id': user.id,
            'created_at': datetime.utcnow(),
            'expires_at': expires_at,
            'ip_address': self._get_client_ip(),
            'user_agent': request.headers.get('User-Agent', ''),
            'fingerprint': self._generate_session_fingerprint()
        }
        
        return session_token
    
    def _get_session_expiry(self, remember: bool = False) -> datetime:
        """Get session expiry time"""
        if remember:
            return datetime.utcnow() + timedelta(days=30)
        else:
            return datetime.utcnow() + timedelta(minutes=current_app.config['AUTH_SESSION_TIMEOUT'])
    
    def _invalidate_user_sessions(self, user_id: str) -> None:
        """Invalidate all sessions for a user"""
        sessions_to_remove = []
        for token, session_data in self.session_store.items():
            if session_data['user_id'] == user_id:
                sessions_to_remove.append(token)
        
        for token in sessions_to_remove:
            del self.session_store[token]
    
    def _generate_session_fingerprint(self) -> str:
        """Generate session fingerprint for security"""
        fingerprint_data = f"{self._get_client_ip()}:{request.headers.get('User-Agent', '')}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def _verify_session_fingerprint(self, session_data: Dict) -> bool:
        """Verify session fingerprint for security"""
        current_fingerprint = self._generate_session_fingerprint()
        return current_fingerprint == session_data.get('fingerprint', '')

def create_auth_system():
    """Factory function to create authentication system"""
    return SecureAuthenticationSystem()

# Decorator for requiring authentication
def auth_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Decorator for requiring specific permissions
def permission_required(permission):
    """Decorator to require specific permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not hasattr(current_user, 'has_permission') or not current_user.has_permission(permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
