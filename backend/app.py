from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import uuid
import re
from dotenv import load_dotenv
from utils.data_sanitization import DataSanitizationLayer
from utils.authentication import SecureAuthenticationSystem, auth_required

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///leakpeek.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize the authentication system
auth_system = SecureAuthenticationSystem()

# Initialize authentication system with app
auth_system.init_app(app)

# Rate limiting - FIXED VERSION
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# CORS for production
allowed_origins = [
    "http://localhost:3000",  # Development
    "https://your-app-name.vercel.app",  # Replace with your actual Vercel URL
]

if os.environ.get('FLASK_ENV') == 'production':
    # Add your production frontend URL
    allowed_origins.append(os.environ.get('FRONTEND_URL', ''))

CORS(app, origins=allowed_origins, supports_credentials=True)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(36))
    is_active = db.Column(db.Boolean, default=True)
    password_changed_at = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Analysis(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    target_email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='pending')
    results = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))

    def is_expired(self):
        return datetime.utcnow() > self.expires_at


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(str(user_id))


# Basic Routes
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/api/register', methods=['POST'])
@limiter.limit("3 per minute")
def register():
    try:
        data = request.get_json()
        
        # Use secure authentication system
        result = auth_system.register_user(
            email=data.get('email', ''),
            password=data.get('password', ''),
            name=data.get('name', '')
        )
        
        if result['success']:
            return jsonify({
                'message': 'Registration successful',
                'user_id': result['user_id'],
                'requires_verification': result.get('requires_verification', False)
            }), 201
        else:
            return jsonify({'error': result['error']}), 400          
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = request.get_json()
        
        result = auth_system.authenticate_user(
            email=data.get('email', ''),
            password=data.get('password', ''),
            remember=data.get('remember', False)
        )
        
        if result['success']:
            return jsonify({
                'message': 'Login successful',
                'user_id': result['user_id'],
                'session_token': result['session_token'],
                'expires_at': result['expires_at'].isoformat()
            }), 200
        else:
            return jsonify({'error': result['error']}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


@app.route('/api/logout', methods=['POST'])
@auth_required
def logout():
    try:
        result = auth_system.logout_user()
        
        if result['success']:
            return jsonify({'message': 'Logged out successfully'}), 200
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500
    

@app.route('/api/change-password', methods=['POST'])
@auth_required
def change_password():
    try:
        data = request.get_json()
        
        result = auth_system.change_password(
            user_id=current_user.id,
            current_password=data.get('current_password', ''),
            new_password=data.get('new_password', '')
        )
        
        if result['success']:
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Password change failed'}), 500


@app.route('/api/analyze', methods=['POST'])
@login_required
@limiter.limit("3 per day")
def start_analysis():
    sanitizer = DataSanitizationLayer()
    
    try:
        # Get and sanitize input data
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({'error': 'No input data provided'}), 400
        
        # Sanitize all inputs
        sanitized_data = sanitizer.sanitize_analysis_request(raw_data)
        tracking_id = sanitized_data['tracking_id']
        
        # Extract sanitized values
        target_name = sanitized_data['name']
        target_email = sanitized_data['email'] 
        social_links = sanitized_data['social_links']
        
        # Authorization check - users can only analyze their own email
        if target_email != current_user.email:
            sanitizer.cleanup_temporary_data(tracking_id)  # Clean up immediately
            return jsonify({'error': 'You can only analyze your own digital footprint'}), 403
        
        # Check for existing recent analysis
        recent_analysis = Analysis.query.filter_by(
            user_id=current_user.id,
            target_email=target_email
        ).filter(Analysis.created_at > datetime.utcnow() - timedelta(hours=1)).first()
        
        if recent_analysis and not recent_analysis.is_expired():
            sanitizer.cleanup_temporary_data(tracking_id)  # Clean up immediately
            return jsonify({'error': 'Please wait before running another analysis'}), 429
        
        # Create analysis record (no sensitive data stored)
        analysis = Analysis(
            user_id=current_user.id,
            target_email=target_email,  # Only email stored, already validated
            status='processing'
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Perform the analysis (sensitive data handled in memory only)
        from utils.analyzer import perform_analysis
        raw_results = perform_analysis(target_name, target_email, social_links)
        
        # Sanitize results before storage/return
        sanitized_results = sanitizer.sanitize_analysis_results(raw_results)
        
        # Store only sanitized results
        analysis.results = sanitized_results
        analysis.status = 'completed'
        db.session.commit()
        
        # Clean up temporary data immediately after processing
        sanitizer.cleanup_temporary_data(tracking_id)
        
        return jsonify({
            'analysis_id': analysis.id,
            'status': 'completed',
            'results': sanitized_results
        }), 200
        
    except ValueError as e:
        # Clean up on validation error
        if 'tracking_id' in locals():
            sanitizer.cleanup_temporary_data(tracking_id)
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        # Clean up on any error
        if 'tracking_id' in locals():
            sanitizer.cleanup_temporary_data(tracking_id)
        db.session.rollback()
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': 'Analysis failed to complete'}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_expired_data():
    """Remove expired analyses and temporary data"""
    try:
        # Clean expired database records
        expired_analyses = Analysis.query.filter(Analysis.expires_at < datetime.utcnow()).all()
        for analysis in expired_analyses:
            db.session.delete(analysis)
        
        # Clean temporary sanitization data
        sanitizer = DataSanitizationLayer()
        cleaned_temp = sanitizer.cleanup_temporary_data()
        
        db.session.commit()
        
        return jsonify({
            'message': f'Cleaned up {len(expired_analyses)} expired analyses and {cleaned_temp} temporary data entries'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Cleanup failed: {str(e)}")
        return jsonify({'error': 'Cleanup failed'}), 500

# Initialize database tables
@app.before_first_request
def create_tables():
    db.create_all()

# Health check for deployment
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'leakpeek-backend'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)