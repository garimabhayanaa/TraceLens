import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from middleware.firebase_auth import verify_firebase_token, get_current_user
from models.firestore_models import AnalysisSession, FirestoreUser, AuditLog
from services.ai_analysis_service import AIAnalysisService
from utils.abuse_prevention import create_abuse_prevention_framework
from utils.url_validator import create_url_validator

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)
ai_service = AIAnalysisService()
url_validator = create_url_validator()


@analysis_bp.route('/start', methods=['POST'])
@verify_firebase_token
def start_analysis():
    """Start new social media analysis"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user = get_current_user()
        user_id = user['user_id']

        # Validate input
        social_media_url = data.get('social_media_url', '').strip()
        analysis_type = data.get('analysis_type', 'comprehensive')

        if not social_media_url:
            return jsonify({'error': 'Social media URL is required'}), 400

        # ✅ URL VALIDATION WITH ENHANCED ERROR HANDLING
        validation_result = url_validator.validate_social_url(social_media_url)

        if not validation_result['is_valid']:
            logger.warning(f"Invalid URL submitted by user {user_id}: {social_media_url}")
            return jsonify({
                'error': 'Invalid social media URL',
                'message': validation_result['error'],
                'supported_platforms': validation_result.get('supported_platforms', []),
                'example_formats': validation_result.get('example_formats', []),
                'submitted_url': social_media_url
            }), 400

        # Use cleaned URL for analysis
        social_media_url = validation_result.get('cleaned_url', social_media_url)
        detected_platform = validation_result.get('platform')
        detected_username = validation_result.get('username')

        logger.info(f"Valid URL detected - Platform: {detected_platform}, Username: {detected_username}")

        # Check user limits
        firestore_user = user['firestore_user']
        daily_usage = firestore_user.get('daily_usage_count', 0)
        subscription_tier = firestore_user.get('subscription_tier', 'free')

        if subscription_tier == 'free' and daily_usage >= 3:
            return jsonify({
                'error': 'Daily limit exceeded',
                'message': 'Free tier allows 3 analyses per day. Please upgrade for unlimited access.',
                'current_usage': daily_usage,
                'limit': 3,
                'subscription_tier': subscription_tier
            }), 429

        # Create analysis session
        session_data = {
            'user_id': user_id,
            'user_email': user['email'],
            'social_media_url': social_media_url,
            'analysis_type': analysis_type,
            'detected_platform': detected_platform,
            'detected_username': detected_username,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'status': 'pending',
            'progress': 0
        }

        session = AnalysisSession.create(session_data)

        # Log the action
        AuditLog.create({
            'user_id': user_id,
            'action': 'analysis_started',
            'session_id': session['id'],
            'details': {
                'analysis_type': analysis_type,
                'social_media_url': social_media_url,
                'detected_platform': detected_platform,
                'detected_username': detected_username
            },
            'ip_address': request.remote_addr
        })

        # Increment user usage count
        FirestoreUser.increment_usage(user_id)

        # Start analysis in background
        ai_service.process_analysis_async(session['id'], social_media_url, analysis_type)

        logger.info(f"Analysis started successfully for user {user_id}, session {session['id']}")

        return jsonify({
            'success': True,
            'session_id': session['id'],
            'message': 'Analysis started successfully',
            'detected_platform': detected_platform,
            'detected_username': detected_username,
            'estimated_completion': '30-60 seconds',
            'status': 'pending',
            'progress': 0
        }), 201

    except Exception as e:
        logger.error(f"Analysis start error: {str(e)}")
        return jsonify({
            'error': 'Failed to start analysis',
            'message': 'An internal error occurred. Please try again later.',
            'debug': str(e) if logger.level == logging.DEBUG else None
        }), 500


@analysis_bp.route('/status/<session_id>', methods=['GET'])
@verify_firebase_token
def get_analysis_status(session_id):
    """Get analysis status"""
    try:
        user = get_current_user()
        user_id = user['user_id']

        session = AnalysisSession.get_by_id(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        if session['user_id'] != user_id:
            return jsonify({'error': 'Access denied'}), 403

        # Check if session expired
        if session.get('expires_at') and session['expires_at'] < datetime.utcnow():
            return jsonify({
                'error': 'Session expired',
                'session_id': session_id,
                'status': 'expired'
            }), 410

        return jsonify({
            'success': True,
            'session_id': session_id,
            'status': session.get('status', 'pending'),
            'progress': session.get('progress', 0),
            'created_at': session['created_at'].isoformat() if session.get('created_at') else None,
            'expires_at': session['expires_at'].isoformat() if session.get('expires_at') else None,
            'message': session.get('message', 'Analysis in progress...'),
            'detected_platform': session.get('detected_platform'),
            'detected_username': session.get('detected_username')
        }), 200

    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({'error': 'Failed to get analysis status'}), 500


@analysis_bp.route('/results/<session_id>', methods=['GET'])
@verify_firebase_token
def get_analysis_results(session_id):
    """Get analysis results"""
    try:
        user = get_current_user()
        user_id = user['user_id']

        session = AnalysisSession.get_by_id(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        if session['user_id'] != user_id:
            return jsonify({'error': 'Access denied'}), 403

        if session.get('status') != 'completed':
            return jsonify({
                'error': 'Analysis not completed',
                'status': session.get('status', 'pending'),
                'progress': session.get('progress', 0),
                'message': 'Please wait for analysis to complete'
            }), 400

        # Return results
        results = session.get('results', {})
        return jsonify({
            'success': True,
            'session_id': session_id,
            'results': results,
            'analysis_type': session.get('analysis_type'),
            'completed_at': session.get('completed_at').isoformat() if session.get('completed_at') else None,
            'social_media_url': session.get('social_media_url'),
            'detected_platform': session.get('detected_platform'),
            'detected_username': session.get('detected_username')
        }), 200

    except Exception as e:
        logger.error(f"Results retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to get analysis results'}), 500


@analysis_bp.route('/history', methods=['GET'])
@verify_firebase_token
def get_analysis_history():
    """Get user's analysis history"""
    try:
        user = get_current_user()
        user_id = user['user_id']

        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # Cap at 50

        sessions = AnalysisSession.get_user_sessions(user_id, limit)

        # Format sessions for response
        history = []
        for session in sessions:
            history.append({
                'session_id': session['id'],
                'social_media_url': session.get('social_media_url'),
                'analysis_type': session.get('analysis_type'),
                'status': session.get('status'),
                'progress': session.get('progress', 0),
                'detected_platform': session.get('detected_platform'),
                'detected_username': session.get('detected_username'),
                'created_at': session['created_at'].isoformat() if session.get('created_at') else None,
                'completed_at': session.get('completed_at').isoformat() if session.get('completed_at') else None
            })

        return jsonify({
            'success': True,
            'history': history,
            'total_count': len(history)
        }), 200

    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to get analysis history'}), 500


@analysis_bp.route('/delete/<session_id>', methods=['DELETE'])
@verify_firebase_token
def delete_analysis(session_id):
    """Delete analysis results"""
    try:
        user = get_current_user()
        user_id = user['user_id']

        session = AnalysisSession.get_by_id(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        if session['user_id'] != user_id:
            return jsonify({'error': 'Access denied'}), 403

        # Delete the session
        from config.firebase_config import get_db
        db = get_db()
        db.collection(AnalysisSession.COLLECTION).document(session_id).delete()

        # Log the deletion
        AuditLog.create({
            'user_id': user_id,
            'action': 'analysis_deleted',
            'session_id': session_id,
            'details': {'deleted_by_user': True},
            'ip_address': request.remote_addr
        })

        logger.info(f"Analysis session {session_id} deleted by user {user_id}")

        return jsonify({
            'success': True,
            'message': 'Analysis deleted successfully',
            'session_id': session_id
        }), 200

    except Exception as e:
        logger.error(f"Analysis deletion error: {str(e)}")
        return jsonify({'error': 'Failed to delete analysis'}), 500


# Health check endpoint for the analysis service
@analysis_bp.route('/health', methods=['GET'])
def analysis_health():
    """Health check for analysis service"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'analysis',
            'timestamp': datetime.utcnow().isoformat(),
            'ai_service_status': 'active',
            'url_validator_status': 'active'
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

