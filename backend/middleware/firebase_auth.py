import logging
from functools import wraps
from flask import request, jsonify
import firebase_admin
from firebase_admin import auth as firebase_auth
from config.firebase_config import db

def require_auth(f):
    """
    Decorator to require Firebase authentication for Flask routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get Authorization header
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                logging.warning("No Authorization header provided")
                return jsonify({
                    'success': False,
                    'error': 'Authorization header is required'
                }), 401
            
            # Check if header starts with 'Bearer '
            if not auth_header.startswith('Bearer '):
                logging.warning("Invalid Authorization header format")
                return jsonify({
                    'success': False,
                    'error': 'Authorization header must be in format: Bearer <token>'
                }), 401
            
            # Extract the token
            id_token = auth_header.split('Bearer ')[1]
            
            if not id_token:
                logging.warning("No token provided in Authorization header")
                return jsonify({
                    'success': False,
                    'error': 'Firebase ID token is required'
                }), 401
            
            # Verify the Firebase ID token
            try:
                decoded_token = firebase_auth.verify_id_token(id_token)
                user_id = decoded_token['uid']
                user_email = decoded_token.get('email', '')
                user_name = decoded_token.get('name', '')
                email_verified = decoded_token.get('email_verified', False)
                
                logging.info(f"User authenticated: {user_id}")
                
                # Add user information to request object
                request.user_id = user_id
                request.user_email = user_email
                request.user_name = user_name
                request.email_verified = email_verified
                request.user_info = {
                    'uid': user_id,
                    'email': user_email,
                    'name': user_name,
                    'email_verified': email_verified
                }
                
                # Continue to the protected route
                return f(*args, **kwargs)
                
            except firebase_auth.InvalidIdTokenError:
                logging.error("Invalid Firebase ID token")
                return jsonify({
                    'success': False,
                    'error': 'Invalid Firebase ID token'
                }), 401
                
            except firebase_auth.ExpiredIdTokenError:
                logging.error("Expired Firebase ID token")
                return jsonify({
                    'success': False,
                    'error': 'Firebase ID token has expired'
                }), 401
                
            except firebase_auth.RevokedIdTokenError:
                logging.error("Revoked Firebase ID token")
                return jsonify({
                    'success': False,
                    'error': 'Firebase ID token has been revoked'
                }), 401
                
            except firebase_auth.CertificateFetchError:
                logging.error("Certificate fetch error during token verification")
                return jsonify({
                    'success': False,
                    'error': 'Authentication service temporarily unavailable'
                }), 503
                
            except Exception as e:
                logging.error(f"Firebase token verification error: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Authentication error: {str(e)}'
                }), 401
                
        except Exception as e:
            logging.error(f"Authentication middleware error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal authentication error'
            }), 500
    
    return decorated_function

def optional_auth(f):
    """
    Decorator for routes that optionally require authentication
    If token is provided, it validates it. If not, continues without user info.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get Authorization header
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                # No authentication provided - continue without user info
                request.user_id = None
                request.user_email = None
                request.user_name = None
                request.email_verified = False
                request.user_info = None
                return f(*args, **kwargs)
            
            # Extract and verify token (same as require_auth)
            id_token = auth_header.split('Bearer ')[1]
            
            try:
                decoded_token = firebase_auth.verify_id_token(id_token)
                user_id = decoded_token['uid']
                user_email = decoded_token.get('email', '')
                user_name = decoded_token.get('name', '')
                email_verified = decoded_token.get('email_verified', False)
                
                # Add user information to request object
                request.user_id = user_id
                request.user_email = user_email
                request.user_name = user_name
                request.email_verified = email_verified
                request.user_info = {
                    'uid': user_id,
                    'email': user_email,
                    'name': user_name,
                    'email_verified': email_verified
                }
                
                logging.info(f"Optional auth - User authenticated: {user_id}")
                
            except Exception as e:
                logging.warning(f"Optional auth - Invalid token: {str(e)}")
                # Invalid token - continue without user info
                request.user_id = None
                request.user_email = None
                request.user_name = None
                request.email_verified = False
                request.user_info = None
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logging.error(f"Optional authentication middleware error: {str(e)}")
            # Continue without user info on error
            request.user_id = None
            request.user_email = None
            request.user_name = None
            request.email_verified = False
            request.user_info = None
            return f(*args, **kwargs)
    
    return decorated_function

# Utility functions for manual authentication checks
def verify_token(id_token):
    """
    Utility function to verify Firebase ID token
    Returns decoded token or raises exception
    """
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        logging.error(f"Token verification failed: {str(e)}")
        raise e

def get_current_user():
    """
    Utility function to get current authenticated user from request context
    Returns user info dict or None
    """
    try:
        if hasattr(request, 'user_info') and request.user_info:
            return request.user_info
        return None
    except Exception as e:
        logging.error(f"Error getting current user: {str(e)}")
        return None

def extract_token_from_request():
    """
    Utility function to extract Firebase token from request headers
    Returns token string or None
    """
    try:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header.split('Bearer ')[1]
        return None
    except Exception as e:
        logging.error(f"Error extracting token: {str(e)}")
        return None

# Export all functions
__all__ = [
    'require_auth',
    'optional_auth', 
    'verify_token',
    'get_current_user',
    'extract_token_from_request'
]
