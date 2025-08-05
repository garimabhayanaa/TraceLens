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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(36))

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
@limiter.limit("5 per minute")
def register():
    data = request.get_json()

    # Validate input
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')

    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'error': 'Invalid email format'}), 400

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Create user
    user = User(
        email=email,
        verification_token=str(uuid.uuid4()),
        verified=True  # Auto-verify for development
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'Registration successful',
            'user_id': user.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500


@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password) and user.verified:
        login_user(user)
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email
            }
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/analyze', methods=['POST'])
@login_required
@limiter.limit("3 per day")
def start_analysis():
    data = request.get_json()

    target_email = data.get('email', '').lower().strip()
    target_name = data.get('name', '').strip()
    social_links = data.get('social_links', [])

    # Validation
    if not target_email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', target_email):
        return jsonify({'error': 'Invalid email format'}), 400

    # Authorization check - users can only analyze their own email
    if target_email != current_user.email:
        return jsonify({'error': 'You can only analyze your own digital footprint'}), 403

    # Check for existing recent analysis
    recent_analysis = Analysis.query.filter_by(
        user_id=current_user.id,
        target_email=target_email
    ).filter(Analysis.created_at > datetime.utcnow() - timedelta(hours=1)).first()

    if recent_analysis and not recent_analysis.is_expired():
        return jsonify({'error': 'Please wait before running another analysis'}), 429

    # Create analysis record
    analysis = Analysis(
        user_id=current_user.id,
        target_email=target_email,
        status='processing'
    )

    try:
        db.session.add(analysis)
        db.session.commit()

        # Perform the analysis
        from utils.analyzer import perform_analysis
        results = perform_analysis(target_name, target_email, social_links)

        analysis.results = results
        analysis.status = 'completed'
        db.session.commit()

        return jsonify({
            'analysis_id': analysis.id,
            'status': 'completed',
            'results': results
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Analysis error: {str(e)}")
        return jsonify({'error': 'Analysis failed to complete'}), 500

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