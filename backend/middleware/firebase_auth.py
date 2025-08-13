# middleware/firebase_auth.py

import logging
from functools import wraps
from flask import request, jsonify, g
import firebase_admin
from firebase_admin import auth
from datetime import datetime

# Import Firebase config
from config.firebase_config import firebase_config, is_firebase_available
from models.firestore_models import User

logger = logging.getLogger(__name__)


def verify_firebase_token(f):
    """Decorator to verify Firebase ID token with offline handling"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Check if Firebase is available
            if not is_firebase_available():
                # Offline mode - create mock user
                g.current_user = {
                    'user_id': 'offline_user',
                    'email': 'offline@example.com',
                    'email_verified': True,
                    'firestore_user': {
                        'subscription_tier': 'free',
                        'daily_usage_count': 0,
                        'offline_mode': True
                    }
                }
                logger.warning("Operating in offline mode - using mock authentication")
                return f(*args, **kwargs)

            # Get Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'No valid authorization token provided'}), 401

            # Extract token
            id_token = auth_header.split('Bearer ')[1]

            # Verify the token
            decoded_token = auth.verify_id_token(id_token)
            user_id = decoded_token['uid']

            # Get or create user in Firestore
            user_doc = get_or_create_user(decoded_token)

            # Store user info in Flask's g object
            g.current_user = {
                'user_id': user_id,
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'firestore_user': user_doc
            }

            logger.info(f"User authenticated: {user_id}")
            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")

            # If Firebase is unavailable, allow with mock user
            if not is_firebase_available():
                g.current_user = {
                    'user_id': 'offline_user',
                    'email': 'offline@example.com',
                    'email_verified': True,
                    'firestore_user': {
                        'subscription_tier': 'free',
                        'daily_usage_count': 0,
                        'offline_mode': True
                    }
                }
                logger.warning("Firebase unavailable - using offline authentication")
                return f(*args, **kwargs)

            return jsonify({'error': 'Invalid token'}), 401

    return decorated_function


def get_or_create_user(decoded_token):
    """Get or create user in Firestore"""
    try:
        user_id = decoded_token['uid']

        # Try to get existing user
        user_doc = User.get_by_id(user_id)

        if user_doc:
            return user_doc
        else:
            # Create new user
            user_data = {
                'user_id': user_id,
                'email': decoded_token.get('email'),
                'display_name': decoded_token.get('name'),
                'email_verified': decoded_token.get('email_verified', False),
                'subscription_tier': 'free',
                'daily_usage_count': 0,
                'total_analyses': 0,
                'privacy_level': 'standard',
                'created_at': datetime.utcnow().isoformat(),
                'last_analysis': None
            }

            return User.create(user_id, user_data)

    except Exception as e:
        logger.error(f"Error getting/creating user: {str(e)}")
        # Return fallback user data
        return {
            'subscription_tier': 'free',
            'daily_usage_count': 0,
            'total_analyses': 0,
            'privacy_level': 'standard',
            'error_mode': True
        }


def get_current_user():
    """Get current authenticated user"""
    return getattr(g, 'current_user', None)

