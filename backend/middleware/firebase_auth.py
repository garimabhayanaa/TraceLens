# middleware/firebase_auth.py
import logging
from functools import wraps
from flask import request, jsonify, g
from firebase_admin import auth
from models.firestore_models import FirestoreUser

logger = logging.getLogger(__name__)

def verify_firebase_token(f):
    """Middleware to verify Firebase ID tokens"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get the authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'error': 'No authorization token provided'}), 401
            
            # Extract the token
            try:
                token = auth_header.split('Bearer ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
            
            # Verify the token with Firebase
            try:
                decoded_token = auth.verify_id_token(token)
                
                # Add user info to Flask's global context
                g.user_id = decoded_token['uid']
                g.user_email = decoded_token.get('email')
                g.user_email_verified = decoded_token.get('email_verified', False)
                g.firebase_user = decoded_token
                
                # Get or create user in Firestore
                firestore_user = FirestoreUser.get_by_id(g.user_id)
                if not firestore_user:
                    # Create user in Firestore
                    user_data = {
                        'email': g.user_email,
                        'email_verified': g.user_email_verified,
                        'display_name': decoded_token.get('name'),
                        'provider': decoded_token.get('firebase', {}).get('sign_in_provider', 'unknown')
                    }
                    firestore_user = FirestoreUser.create(g.user_id, user_data)
                
                g.firestore_user = firestore_user
                
                logger.info(f"User authenticated: {g.user_id}")
                return f(*args, **kwargs)
                
            except auth.InvalidIdTokenError:
                logger.warning("Invalid Firebase ID token")
                return jsonify({'error': 'Invalid authentication token'}), 401
            except auth.ExpiredIdTokenError:
                logger.warning("Expired Firebase ID token")
                return jsonify({'error': 'Authentication token has expired'}), 401
            except Exception as e:
                logger.error(f"Token verification error: {str(e)}")
                return jsonify({'error': 'Authentication verification failed'}), 401
                
        except Exception as e:
            logger.error(f"Authentication middleware error: {str(e)}")
            return jsonify({'error': 'Authentication error'}), 500
    
    return decorated_function

def get_current_user():
    """Get current authenticated user"""
    return {
        'user_id': g.get('user_id'),
        'email': g.get('user_email'),
        'email_verified': g.get('user_email_verified'),
        'firebase_user': g.get('firebase_user'),
        'firestore_user': g.get('firestore_user')
    }
