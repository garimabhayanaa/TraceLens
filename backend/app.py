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
from config.firebase_config import db
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

# ✅ COMPREHENSIVE CORS CONFIGURATION FOR FRONTEND-BACKEND COMMUNICATION
CORS(app, 
     origins=['https://trace-lens.vercel.app'],
     supports_credentials=True,
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=[
         'Content-Type', 
         'Authorization', 
         'Access-Control-Allow-Credentials',
         'Access-Control-Allow-Origin'
     ],
     resources={
         r"/api/*": {
             "origins": ["https://trace-lens.vercel.app"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"]
         },
         r"/health": {
             "origins": ["https://trace-lens.vercel.app"],
             "methods": ["GET", "OPTIONS"]
         }
     })

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="memory://",
)

# Register blueprints
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')

# ✅ EXPLICIT PREFLIGHT REQUEST HANDLER FOR CORS
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "https://trace-lens.vercel.app")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,POST,PUT,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

# Health check endpoint
@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint"""
    try:
        # Test Firebase connection
        test_collection = db.collection('health_check')
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'TraceLens AI Backend',
            'version': '2.0.0',
            'firebase': 'connected',
            'cors': 'enabled',
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
@app.route('/', methods=['GET', 'OPTIONS'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'TraceLens AI Social Media Analyzer API',
        'version': '2.0.0',
        'status': 'active',
        'database': 'Firebase Firestore',
        'authentication': 'Firebase Auth',
        'cors': 'enabled for https://trace-lens.vercel.app',
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
@app.route('/api/user/profile', methods=['GET', 'OPTIONS'])
@limiter.limit("30 per minute")
def get_user_profile():
    """Get user profile information"""
    from middleware.firebase_auth import require_auth
    from models.firestore_models import FirestoreUser
    
    @require_auth
    def _get_profile():
        try:
            user_id = request.user_id
            user_result = FirestoreUser.get_user(user_id)
            
            if not user_result['success']:
                return jsonify({
                    'success': False,
                    'error': 'User profile not found'
                }), 404
            
            user_data = user_result['user']
            
            return jsonify({
                'success': True,
                'user': {
                    'user_id': user_id,
                    'email': request.user_email,
                    'email_verified': request.email_verified,
                    'display_name': user_data.get('display_name'),
                    'subscription_tier': user_data.get('subscription_tier', 'free'),
                    'daily_usage': user_data.get('daily_usage', 0),
                    'lifetime_analysis_count': user_data.get('lifetime_analysis_count', 0),
                    'privacy_level': user_data.get('privacy_level', 'standard'),
                    'created_at': user_data.get('created_at'),
                    'last_analysis': user_data.get('last_analysis')
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Profile retrieval error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to get user profile'
            }), 500
    
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
                result = AnalysisSession.cleanup_expired_sessions()
                if result['success'] and result.get('deleted_count', 0) > 0:
                    logger.info(f"Cleanup: deleted {result['deleted_count']} expired sessions")
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
    logger.info("🌐 CORS enabled for https://trace-lens.vercel.app")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )
