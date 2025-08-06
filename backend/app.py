from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
from datetime import datetime, timedelta
import uuid
import re
from dotenv import load_dotenv
import atexit

# Import custom utilities
from utils.data_sanitization import DataSanitizationLayer
from utils.authentication import SecureAuthenticationSystem, auth_required
from utils.database_manager import create_database_manager
from utils.cleanup_scheduler import create_cleanup_scheduler
from utils.consent_logging import (
    create_consent_logging_system, 
    record_analysis_consent, 
    check_analysis_consent,
    ConsentStatus,
    ConsentType
)
from utils.authentication_logging import (
    create_authentication_logger,
    log_login_attempt,
    log_logout,
    check_account_lockout,
    AuthEventType,
    AuthMethod
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///leakpeek.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database configuration for PostgreSQL (if using)
if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_timeout': 20,
        'pool_recycle': -1,
        'pool_pre_ping': True
    }

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Rate limiting
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
    frontend_url = os.environ.get('FRONTEND_URL')
    if frontend_url:
        allowed_origins.append(frontend_url)

CORS(app, origins=allowed_origins, supports_credentials=True)

# Initialize the authentication system
auth_system = SecureAuthenticationSystem()
auth_system.init_app(app)

# Initialize database manager
db_manager = create_database_manager()

# Initialize cleanup scheduler
cleanup_scheduler = create_cleanup_scheduler(db_manager)
cleanup_scheduler.start_scheduler()

# Initialize consent logging system
consent_logger = create_consent_logging_system()

# Initialize authentication logger
auth_logger = create_authentication_logger()

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=True)  # Auto-verify for development
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
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'leakpeek-backend',
        'version': '1.0'
    })

@app.route('/health')
def health():
    """Health check for deployment services"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = 'unhealthy'

    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'service': 'leakpeek-backend',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/register', methods=['POST'])
@limiter.limit("3 per minute")
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

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
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '')
        password = data.get('password', '')
        
        # Check if account is locked
        lockout_status = check_account_lockout(email)
        if lockout_status['locked']:
            # Log the blocked attempt
            auth_logger.log_authentication_event(
                user_id=email,  # Using email as identifier
                event_type=AuthEventType.LOGIN_FAILURE,
                auth_method=AuthMethod.PASSWORD,
                success=False,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                failure_reason='Account locked due to multiple failed attempts'
            )
            return jsonify({
                'error': 'Account temporarily locked due to multiple failed login attempts',
                'unlock_time': lockout_status['unlock_time']
            }), 423

        result = auth_system.authenticate_user(
            email=email,
            password=password,
            remember=data.get('remember', False)
        )

        if result['success']:
            # Log successful login
            log_login_attempt(
                user_id=email,
                success=True,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            # Update last login time
            user = User.query.get(result['user_id'])
            if user:
                user.last_login_at = datetime.utcnow()
                db.session.commit()

            return jsonify({
                'message': 'Login successful',
                'user_id': result['user_id'],
                'session_token': result.get('session_token'),
                'expires_at': result['expires_at'].isoformat() if result.get('expires_at') else None
            }), 200
        else:
            # Log failed login
            log_login_attempt(
                user_id=email,
                success=False,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                failure_reason=result['error']
            )
            return jsonify({'error': result['error']}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/logout', methods=['POST'])
@auth_required
def logout():
    try:
        # Log logout event
        log_logout(
            user_id=current_user.id,
            session_id=session.get('session_id', ''),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
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
        if not data:
            return jsonify({'error': 'No data provided'}), 400

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

# Consent Management Endpoints
@app.route('/api/consent/record', methods=['POST'])
@auth_required
def record_consent():
    """Record user consent for various processing activities"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        consent_id = consent_logger.record_consent(
            user_id=current_user.id,
            consent_status=ConsentStatus.GRANTED if data.get('consent_given', False) else ConsentStatus.DENIED,
            consent_types=[ConsentType(ct) for ct in data.get('consent_types', ['analysis'])],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            consent_method=data.get('method', 'web_form'),
            consent_version=data.get('version', 'v1.0'),
            purpose_description=data.get('purpose', 'Digital footprint analysis'),
            data_categories=data.get('data_categories', ['email', 'public_profiles']),
            consent_language=data.get('language', 'en'),
            geolocation=data.get('country'),
            session_id=session.get('session_id'),
            page_url=data.get('page_url'),
            referrer_url=data.get('referrer_url')
        )
        
        return jsonify({
            'consent_id': consent_id,
            'status': 'recorded',
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to record consent: {str(e)}")
        return jsonify({'error': 'Failed to record consent'}), 500

@app.route('/api/consent/status', methods=['GET'])
@auth_required
def get_consent_status():
    """Get current consent status for the user"""
    try:
        consent_status = consent_logger.get_current_consent_status(current_user.id)
        return jsonify(consent_status), 200
        
    except Exception as e:
        logger.error(f"Failed to get consent status: {str(e)}")
        return jsonify({'error': 'Failed to retrieve consent status'}), 500

@app.route('/api/consent/history', methods=['GET'])
@auth_required
def get_consent_history():
    """Get user's consent history (for GDPR data access requests)"""
    try:
        consent_history = consent_logger.get_user_consent_history(current_user.id)
        return jsonify({
            'user_id': current_user.id,
            'consent_history': consent_history,
            'total_records': len(consent_history)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get consent history: {str(e)}")
        return jsonify({'error': 'Failed to retrieve consent history'}), 500
    
@app.route('/api/auth/history', methods=['GET'])
@auth_required
def get_authentication_history():
    """Get user's authentication history"""
    try:
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 records
        
        history = auth_logger.get_user_authentication_history(
            user_id=current_user.email,
            limit=limit
        )
        
        return jsonify({
            'authentication_history': history,
            'total_records': len(history)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get authentication history: {str(e)}")
        return jsonify({'error': 'Failed to retrieve authentication history'}), 500
    
@app.route('/api/auth/security-report', methods=['GET'])
@auth_required
def get_security_report():
    """Get personal security report"""
    try:
        # Generate report for current user only
        start_date = datetime.utcnow() - timedelta(days=30)
        
        # Get user's records
        user_records = auth_logger.get_user_authentication_history(
            user_id=current_user.email,
            start_date=start_date,
            limit=1000
        )
        
        # Calculate user-specific stats
        total_logins = len([r for r in user_records if r['event_type'] == 'login_success'])
        failed_attempts = len([r for r in user_records if r['event_type'] == 'login_failure'])

        return jsonify({
            'report_period_days': 30,
            'total_successful_logins': total_logins,
            'failed_login_attempts': failed_attempts,
            'recent_activity': user_records[:10],  # Last 10 events
            'account_security_score': max(0, 100 - (failed_attempts * 5)),  # Simple scoring
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to generate security report: {str(e)}")
        return jsonify({'error': 'Failed to generate security report'}), 500
    
@app.route('/api/admin/auth/report', methods=['GET'])
@auth_required  # Add admin check in production
def get_admin_security_report():
    """Generate comprehensive security report for admins"""
    try:
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        report = auth_logger.generate_security_report(start_date=start_date)
        return jsonify(report), 200
        
    except Exception as e:
        logger.error(f"Failed to generate admin security report: {str(e)}")
        return jsonify({'error': 'Failed to generate security report'}), 500
    
@app.route('/api/admin/auth/export', methods=['GET'])
@auth_required  # Add admin check in production
def export_authentication_logs():
    """Export authentication logs for compliance"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        user_id = request.args.get('user_id')
        
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        records = auth_logger.export_records(
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return jsonify({ 'authentication_records': records,
            'total_records': len(records),
            'exported_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to export authentication logs: {str(e)}")
        return jsonify({'error': 'Failed to export authentication logs'}), 500

@app.route('/api/consent/withdraw', methods=['POST'])
@auth_required
def withdraw_consent():
    """Withdraw consent for specific processing activities"""
    try:
        data = request.get_json()
        if not data or not data.get('consent_types'):
            return jsonify({'error': 'Consent types required'}), 400
        
        # Record withdrawal for each consent type
        withdrawal_ids = []
        for consent_type in data.get('consent_types', []):
            consent_id = consent_logger.record_consent(
                user_id=current_user.id,
                consent_status=ConsentStatus.WITHDRAWN,
                consent_types=[ConsentType(consent_type)],
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                consent_method='withdrawal_form',
                consent_version='v1.0',
                purpose_description=f'Withdrawal of consent for {consent_type}',
                data_categories=data.get('data_categories', []),
                withdrawal_method='user_request'
            )
            withdrawal_ids.append(consent_id)
        
        return jsonify({
            'withdrawal_ids': withdrawal_ids,
            'status': 'withdrawn',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Consent has been withdrawn successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to withdraw consent: {str(e)}")
        return jsonify({'error': 'Failed to withdraw consent'}), 500

@app.route('/api/analyze', methods=['POST'])
@login_required
@limiter.limit("3 per day")
def start_analysis():
    sanitizer = DataSanitizationLayer()
    tracking_id = None

    try:
        # Get and sanitize input data
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({'error': 'No input data provided'}), 400

        # Check if user has given consent for analysis
        has_consent = check_analysis_consent(current_user.id)
        if not has_consent:
            # Record that analysis was attempted without consent
            consent_logger.record_consent(
                user_id=current_user.id,
                consent_status=ConsentStatus.DENIED,
                consent_types=[ConsentType.ANALYSIS],
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                consent_method='implicit_check',
                consent_version='v1.0',
                purpose_description='Analysis attempted without prior consent',
                data_categories=['email']
            )
            
            return jsonify({
                'error': 'Analysis consent required',
                'consent_required': True,
                'consent_types': ['analysis', 'data_processing']
            }), 403

        # Sanitize all inputs
        sanitized_data = sanitizer.sanitize_analysis_request(raw_data)
        tracking_id = sanitized_data['tracking_id']

        # Extract sanitized values
        target_name = sanitized_data['name']
        target_email = sanitized_data['email']
        social_links = sanitized_data['social_links']

        # Authorization check - users can only analyze their own email
        if target_email != current_user.email:
            sanitizer.cleanup_temporary_data(tracking_id)
            return jsonify({'error': 'You can only analyze your own digital footprint'}), 403

        # Record consent for this specific analysis
        record_analysis_consent(
            user_id=current_user.id,
            consent_given=True,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )

        # Check for existing recent analysis
        recent_analysis = Analysis.query.filter_by(
            user_id=current_user.id,
            target_email=target_email
        ).filter(Analysis.created_at > datetime.utcnow() - timedelta(hours=1)).first()

        if recent_analysis and not recent_analysis.is_expired():
            sanitizer.cleanup_temporary_data(tracking_id)
            return jsonify({'error': 'Please wait before running another analysis'}), 429

        # Create analysis record (no sensitive data stored)
        analysis = Analysis(
            user_id=current_user.id,
            target_email=target_email,
            status='processing'
        )

        db.session.add(analysis)
        db.session.commit()

        # Perform the analysis (sensitive data handled in memory only)
        from utils.analyzer import perform_analysis
        raw_results = perform_analysis(target_name, target_email, social_links)

        # Sanitize results before storage/return
        sanitized_results = sanitizer.sanitize_analysis_results(raw_results)

        # Store in both SQLAlchemy model and PostgreSQL temporary storage
        analysis.results = sanitized_results
        analysis.status = 'completed'
        db.session.commit()

        # Also store in temporary PostgreSQL table with TTL
        temp_analysis_id = db_manager.store_temporary_analysis(
            user_id=current_user.id,
            target_email=target_email,
            analysis_results=sanitized_results
        )

        # Clean up temporary sanitization data immediately after processing
        sanitizer.cleanup_temporary_data(tracking_id)

        return jsonify({
            'analysis_id': analysis.id,
            'temp_analysis_id': temp_analysis_id,
            'status': 'completed',
            'expires_in_hours': 24,
            'results': sanitized_results
        }), 200

    except ValueError as e:
        # Clean up on validation error
        if tracking_id:
            sanitizer.cleanup_temporary_data(tracking_id)
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        # Clean up on any error
        if tracking_id:
            sanitizer.cleanup_temporary_data(tracking_id)
        db.session.rollback()
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': 'Analysis failed to complete'}), 500

@app.route('/api/analysis/<analysis_id>', methods=['GET'])
@auth_required
def get_analysis(analysis_id):
    try:
        # Try to get from temporary PostgreSQL storage first
        temp_analysis = db_manager.get_temporary_analysis(analysis_id, current_user.id)

        if temp_analysis:
            return jsonify(temp_analysis), 200

        # Fallback to SQLAlchemy model
        analysis = Analysis.query.filter_by(
            id=analysis_id,
            user_id=current_user.id
        ).first()

        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        if analysis.is_expired():
            return jsonify({'error': 'Analysis has expired'}), 410

        return jsonify({
            'id': analysis.id,
            'target_email': analysis.target_email,
            'results': analysis.results,
            'status': analysis.status,
            'created_at': analysis.created_at.isoformat(),
            'expires_at': analysis.expires_at.isoformat(),
            'is_expired': analysis.is_expired()
        }), 200

    except Exception as e:
        logger.error(f"Retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve analysis'}), 500

@app.route('/api/analyses', methods=['GET'])
@auth_required
def get_user_analyses():
    try:
        # Get user's recent analyses from temporary storage
        temp_analyses = db_manager.get_user_analyses(current_user.id, limit=10)

        # Get from SQLAlchemy as fallback
        db_analyses = Analysis.query.filter_by(
            user_id=current_user.id
        ).filter(
            Analysis.expires_at > datetime.utcnow()
        ).order_by(
            Analysis.created_at.desc()
        ).limit(10).all()

        # Format SQLAlchemy results
        db_results = [{
            'id': analysis.id,
            'target_email': analysis.target_email,
            'privacy_score': analysis.results.get('privacy_score') if analysis.results else None,
            'privacy_grade': analysis.results.get('privacy_grade') if analysis.results else None,
            'created_at': analysis.created_at.isoformat(),
            'expires_at': analysis.expires_at.isoformat(),
            'status': analysis.status
        } for analysis in db_analyses]

        return jsonify({
            'temporary_analyses': temp_analyses,
            'db_analyses': db_results,
            'total_count': len(temp_analyses) + len(db_results)
        }), 200

    except Exception as e:
        logger.error(f"Failed to get user analyses: {str(e)}")
        return jsonify({'error': 'Failed to retrieve analyses'}), 500

@app.route('/api/privacy-templates', methods=['GET'])
@auth_required
def get_privacy_templates():
    """Get all available privacy templates"""
    try:
        from utils.privacy_templates import create_privacy_template_engine

        template_engine = create_privacy_template_engine()
        templates = template_engine.get_all_templates()

        # Convert to JSON-serializable format
        template_data = {}
        for category, template in templates.items():
            template_data[category.value] = {
                'name': template.name,
                'description': template.description,
                'risk_level': template.risk_level.value,
                'regulatory_frameworks': template.regulatory_frameworks,
                'potential_harms': template.potential_harms,
                'detection_methods': template.detection_methods,
                'recommended_controls': template.recommended_controls,
                'examples': template.examples,
                'special_category': template.special_category,
                'gdpr_article': template.gdpr_article
            }

        return jsonify({
            'templates': template_data,
            'total_categories': len(template_data),
            'special_categories': [k for k, v in template_data.items() if v['special_category']],
            'risk_levels': list(set(v['risk_level'] for v in template_data.values()))
        }), 200

    except Exception as e:
        logger.error(f"Failed to get privacy templates: {str(e)}")
        return jsonify({'error': 'Failed to retrieve privacy templates'}), 500

@app.route('/api/privacy-assessment/<analysis_id>', methods=['GET'])
@auth_required
def get_privacy_assessment(analysis_id):
    """Get detailed privacy assessment for an analysis"""
    try:
        # Get analysis results
        analysis = db_manager.get_temporary_analysis(analysis_id, current_user.id)
        
        if not analysis:
            # Fallback to SQLAlchemy model
            db_analysis = Analysis.query.filter_by(
                id=analysis_id, 
                user_id=current_user.id
            ).first()
            
            if not db_analysis or db_analysis.is_expired():
                return jsonify({'error': 'Analysis not found or expired'}), 404
            
            analysis_results = db_analysis.results
        else:
            analysis_results = analysis.get('analysis_results', {})

        # Generate privacy template analysis
        from utils.privacy_templates import create_privacy_template_engine
        template_engine = create_privacy_template_engine()

        privacy_report = template_engine.generate_privacy_report(analysis_results)

        return jsonify(privacy_report), 200

    except Exception as e:
        logger.error(f"Privacy assessment failed: {str(e)}")
        return jsonify({'error': 'Failed to generate privacy assessment'}), 500

@app.route('/api/admin/consent/report', methods=['GET'])
@auth_required  # Add admin check in production
def get_consent_compliance_report():
    """Generate consent compliance report for audits"""
    try:
        report = consent_logger.generate_compliance_report()
        return jsonify(report), 200
        
    except Exception as e:
        logger.error(f"Failed to generate consent report: {str(e)}")
        return jsonify({'error': 'Failed to generate compliance report'}), 500

@app.route('/api/admin/consent/export', methods=['GET'])
@auth_required  # Add admin check in production
def export_consent_logs():
    """Export consent logs for compliance audits"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        user_id = request.args.get('user_id')
        
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        logs = consent_logger.export_consent_logs(
            start_date=start_dt,
            end_date=end_dt,
            user_id=user_id
        )
        
        return jsonify({
            'consent_logs': logs,
            'total_records': len(logs),
            'exported_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to export consent logs: {str(e)}")
        return jsonify({'error': 'Failed to export consent logs'}), 500

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

        # Clean expired consent logs
        cleaned_consent = consent_logger.cleanup_expired_consents()

        db.session.commit()

        return jsonify({
            'message': f'Cleaned up {len(expired_analyses)} expired analyses, {cleaned_temp} temporary data entries, and {cleaned_consent} consent records'
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Cleanup failed: {str(e)}")
        return jsonify({'error': 'Cleanup failed'}), 500

@app.route('/api/admin/cleanup', methods=['POST'])
@auth_required  # Add admin check in production
def manual_cleanup():
    try:
        stats = db_manager.cleanup_expired_data()

        return jsonify({
            'message': 'Cleanup completed',
            'stats': {
                'analyses_deleted': stats.analyses_deleted,
                'sessions_deleted': stats.sessions_deleted,
                'analyses_expired': stats.analyses_expired,
                'completed_at': stats.maintenance_completed_at.isoformat()
            }
        }), 200

    except Exception as e:
        logger.error(f"Manual cleanup failed: {str(e)}")
        return jsonify({'error': 'Cleanup failed'}), 500

@app.route('/api/admin/stats', methods=['GET'])
@auth_required  # Add admin check in production
def get_database_stats():
    try:
        stats = db_manager.get_database_stats()
        return jsonify(stats), 200

    except Exception as e:
        logger.error(f"Failed to get database stats: {str(e)}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'retry_after': str(e.retry_after)}), 429

# Cleanup on app shutdown
@app.teardown_appcontext
def cleanup_db(error):
    if error:
        logger.error(f"App context error: {error}")

# Initialize database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")

# Graceful shutdown handlers
def cleanup_on_exit():
    """Cleanup function for graceful shutdown"""
    try:
        if cleanup_scheduler:
            cleanup_scheduler.stop_scheduler()
        if db_manager:
            db_manager.close_connection_pool()
        logger.info("Application shutdown cleanup completed")
    except Exception as e:
        logger.error(f"Error during shutdown cleanup: {str(e)}")

# Register cleanup function for app termination
atexit.register(cleanup_on_exit)

# Development vs Production configuration
if __name__ == '__main__':
    # Development mode
    with app.app_context():
        try:
            db.create_all()
            logger.info("Development server starting...")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")

    app.run(debug=True, port=5000, host='0.0.0.0')
else:
    # Production mode
    logger.info("Application starting in production mode")
    with app.app_context():
        try:
            db.create_all()
            logger.info("Production database initialized")
        except Exception as e:
            logger.error(f"Production database initialization failed: {str(e)}")