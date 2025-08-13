# app.py
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import ssl

# Temporary SSL fix for development
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

os.environ["CURL_CA_BUNDLE"] = ""
# Import routes
from routes.analysis import analysis_bp

# Import models for initialization
from config.firebase_config import firebase_config
from models.firestore_models import AnalysisSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')

# CORS Configuration
CORS(app, 
     origins=['http://localhost:3000', 'https://your-domain.com'],
     supports_credentials=True,
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'])

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # Keep only one key_func
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="memory://",
)

# Register blueprints
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test Firebase connection
        db = firebase_config.get_firestore_client()
        # Simple connectivity test
        test_collection = db.collection('health_check')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'TraceLens AI Backend',
            'version': '2.0.0',
            'firebase': 'connected',
            'environment': os.environ.get('FLASK_ENV', 'development')
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'TraceLens AI Social Media Analyzer API',
        'version': '2.0.0',
        'status': 'active',
        'database': 'Firebase Firestore',
        'authentication': 'Firebase Auth',
        'endpoints': {
            'health': '/health',
            'analysis': '/api/analysis',
            'start_analysis': '/api/analysis/start',
            'analysis_status': '/api/analysis/status/<session_id>',
            'analysis_results': '/api/analysis/results/<session_id>',
            'analysis_history': '/api/analysis/history'
        },
        'documentation': 'https://tracelens-docs.com/api/v2',
        'support': 'support@tracelens.ai'
    }), 200

# User profile endpoint
@app.route('/api/user/profile', methods=['GET'])
@limiter.limit("30 per minute")
def get_user_profile():
    """Get user profile information"""
    from middleware.firebase_auth import verify_firebase_token, get_current_user
    
    @verify_firebase_token
    def _get_profile():
        try:
            user = get_current_user()
            firestore_user = user['firestore_user']
            
            return jsonify({
                'success': True,
                'user': {
                    'user_id': user['user_id'],
                    'email': user['email'],
                    'email_verified': user['email_verified'],
                    'display_name': firestore_user.get('display_name'),
                    'subscription_tier': firestore_user.get('subscription_tier', 'free'),
                    'daily_usage_count': firestore_user.get('daily_usage_count', 0),
                    'total_analyses': firestore_user.get('total_analyses', 0),
                    'privacy_level': firestore_user.get('privacy_level', 'standard'),
                    'created_at': firestore_user.get('created_at'),
                    'last_analysis': firestore_user.get('last_analysis')
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Profile retrieval error: {str(e)}")
            return jsonify({'error': 'Failed to get user profile'}), 500
    
    return _get_profile()

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': ['/health', '/api/analysis', '/api/user/profile']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests',
        'retry_after': str(e.retry_after)
    }), 429

# Background cleanup task
def setup_cleanup_scheduler():
    """Setup background cleanup for expired sessions"""
    import threading
    import time
    
    def cleanup_task():
        while True:
            try:
                deleted_count = AnalysisSession.delete_expired()
                if deleted_count > 0:
                    logger.info(f"Cleanup: deleted {deleted_count} expired sessions")
                time.sleep(3600)  # Run every hour
            except Exception as e:
                logger.error(f"Cleanup task error: {str(e)}")
                time.sleep(3600)
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    logger.info("Background cleanup scheduler started")

# Initialize background tasks
setup_cleanup_scheduler()

if __name__ == '__main__':
    # Development server
    logger.info("🚀 TraceLens Backend Server Starting...")
    logger.info("🔥 Firebase Firestore: Connected")
    logger.info("🛡️ Security Frameworks: Active")
    logger.info("🤖 AI Analysis Service: Ready")
    logger.info("✅ Backend ready for frontend connection")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5001))
    )
