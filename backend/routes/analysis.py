<<<<<<< Updated upstream
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from middleware.firebase_auth import verify_firebase_token, get_current_user
from models.firestore_models import AnalysisSession, FirestoreUser, AuditLog
from services.ai_analysis_service import AIAnalysisService
from utils.abuse_prevention import create_abuse_prevention_framework
from utils.url_validator import create_url_validator

logger = logging.getLogger(__name__)
=======
from flask import Blueprint, request, jsonify
from middleware.firebase_auth import require_auth
from services.ai_analysis_service import AIAnalysisService
from models.firestore_models import AnalysisSession, FirestoreUser, AuditLog
import logging
import threading
import time
from datetime import datetime
import uuid
>>>>>>> Stashed changes

# Create blueprint
analysis_bp = Blueprint('analysis', __name__)

# Initialize AI analysis service
ai_service = AIAnalysisService()
url_validator = create_url_validator()


@analysis_bp.route('/start', methods=['POST'])
@require_auth
def start_analysis():
    """Start a new analysis session"""
    try:
        data = request.get_json()
        user_id = request.user_id
        
        logging.info(f"Received analysis request from user {user_id}: {data}")
        
        # Validate request data
        if not data:
<<<<<<< Updated upstream
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
=======
            logging.error("No JSON data received")
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        url = data.get('url', '').strip()
        analysis_type = data.get('analysis_type', 'comprehensive').strip()
        
        logging.info(f"Extracted URL: '{url}', Analysis Type: '{analysis_type}'")
        
        # Validate URL
        if not url:
            logging.error("URL is empty or missing")
            return jsonify({
                'success': False,
                'error': 'Social media URL is required'
            }), 400
            
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            logging.error(f"Invalid URL format: {url}")
            return jsonify({
                'success': False,
                'error': 'URL must start with http:// or https://'
            }), 400
        
        # Validate analysis type
        valid_types = ['comprehensive', 'privacy_only', 'sentiment', 'basic']
        if analysis_type not in valid_types:
            logging.error(f"Invalid analysis type: {analysis_type}")
            return jsonify({
                'success': False,
                'error': f'Invalid analysis type. Must be one of: {", ".join(valid_types)}'
            }), 400
        
        # Get user data to check usage limits
        user_result = FirestoreUser.get_user(user_id)
        if not user_result['success']:
            # Create user if doesn't exist
            user_info = getattr(request, 'user_info', {})
            create_result = FirestoreUser.create_user(
                user_id=user_id,
                email=user_info.get('email', 'unknown@example.com'),
                display_name=user_info.get('name', 'Unknown User')
            )
            if not create_result['success']:
                return jsonify({
                    'success': False,
                    'error': 'Failed to create user profile'
                }), 500
            user_data = create_result['user_data']
        else:
            user_data = user_result['user']
        
        # Check usage limits
        daily_usage = user_data.get('daily_usage', 0)
        subscription_tier = user_data.get('subscription_tier', 'free')
        daily_limit = 3 if subscription_tier == 'free' else 999  # Essentially unlimited for premium
        
        if daily_usage >= daily_limit:
            logging.warning(f"User {user_id} exceeded daily limit: {daily_usage}/{daily_limit}")
            return jsonify({
                'success': False,
                'error': f'Daily analysis limit reached ({daily_limit}). Upgrade your plan to continue.'
>>>>>>> Stashed changes
            }), 429

        # Create analysis session
<<<<<<< Updated upstream
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
=======
        session_result = AnalysisSession.create_session(
            user_id=user_id,
            url=url,
            analysis_type=analysis_type
        )
        
        if not session_result['success']:
            logging.error(f"Failed to create session: {session_result['error']}")
            return jsonify({
                'success': False,
                'error': 'Failed to create analysis session'
            }), 500
        
        session_id = session_result['session_id']
        
        # Increment user usage
        usage_result = FirestoreUser.increment_usage(user_id)
        if not usage_result['success']:
            logging.warning(f"Failed to increment usage for user {user_id}: {usage_result['error']}")
        
        # Create audit log
        audit_details = {
            'url': url,
            'analysis_type': analysis_type,
            'session_id': session_id,
            'user_agent': request.headers.get('User-Agent'),
            'consent_given': True
        }
        AuditLog.create_log(
            user_id=user_id,
            action='analysis_start',
            details=audit_details,
            ip_address=request.remote_addr
        )
        
        # Start analysis in background thread
        def run_analysis():
            try:
                logging.info(f"Starting background analysis for session: {session_id}")
                
                # Update progress: Starting
                AnalysisSession.update_progress(
                    session_id=session_id,
                    progress=5,
                    status='processing',
                    step_description='Initializing analysis frameworks'
                )
                
                # Simulate analysis steps with progress updates
                analysis_steps = [
                    (10, 'Validating URL and extracting platform information'),
                    (20, 'Collecting public data from social media profile'),
                    (35, 'Processing collected data through privacy framework'),
                    (50, 'Analyzing sentiment and behavioral patterns'),
                    (65, 'Evaluating privacy risks and data exposure'),
                    (80, 'Generating economic and schedule indicators'),
                    (90, 'Compiling comprehensive analysis report'),
                    (95, 'Applying ethical boundaries and compliance checks')
                ]
                
                for progress, step_desc in analysis_steps:
                    AnalysisSession.update_progress(
                        session_id=session_id,
                        progress=progress,
                        status='processing',
                        step_description=step_desc
                    )
                    time.sleep(2)  # Simulate processing time
                
                # Perform actual AI analysis
                logging.info(f"Running AI analysis for session: {session_id}")
                analysis_results = ai_service.analyze_profile(url, analysis_type)
                
                if analysis_results.get('success', False):
                    # Save results
                    AnalysisSession.save_results(session_id, analysis_results['results'])
                    
                    # Create completion audit log
                    completion_details = {
                        'session_id': session_id,
                        'analysis_completed': True,
                        'results_generated': True,
                        'processing_time_seconds': time.time() - start_time
                    }
                    AuditLog.create_log(
                        user_id=user_id,
                        action='analysis_completed',
                        details=completion_details,
                        ip_address=request.remote_addr
                    )
                    
                    logging.info(f"Analysis completed successfully for session: {session_id}")
                else:
                    # Mark as failed
                    error_msg = analysis_results.get('error', 'Analysis failed due to unknown error')
                    AnalysisSession.mark_failed(session_id, error_msg)
                    
                    # Create failure audit log
                    failure_details = {
                        'session_id': session_id,
                        'error_message': error_msg,
                        'analysis_failed': True
                    }
                    AuditLog.create_log(
                        user_id=user_id,
                        action='analysis_failed',
                        details=failure_details,
                        ip_address=request.remote_addr
                    )
                    
                    logging.error(f"Analysis failed for session {session_id}: {error_msg}")
                    
            except Exception as e:
                logging.error(f"Background analysis error for session {session_id}: {str(e)}")
                AnalysisSession.mark_failed(session_id, f"Internal processing error: {str(e)}")
        
        # Record start time for processing duration calculation
        start_time = time.time()
        
        # Start background analysis
        analysis_thread = threading.Thread(target=run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        logging.info(f"Analysis session started successfully: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Analysis started successfully',
            'estimated_completion_minutes': 2,
            'daily_usage_remaining': daily_limit - daily_usage - 1
>>>>>>> Stashed changes
        }), 200

    except Exception as e:
        logging.error(f"Analysis start error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@analysis_bp.route('/status/<session_id>', methods=['GET'])
@require_auth
def get_analysis_status(session_id):
    """Get the status of an analysis session"""
    try:
        user_id = request.user_id
        
        # Get session data
        session_result = AnalysisSession.get_session(session_id)
        
        if not session_result['success']:
            return jsonify({
                'success': False,
                'error': session_result['error']
            }), 404
        
        session_data = session_result['session']
        
        # Verify user owns this session
        if session_data.get('user_id') != user_id:
            logging.warning(f"User {user_id} attempted to access session {session_id} owned by {session_data.get('user_id')}")
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Return status information
        response_data = {
            'success': True,
            'session_id': session_id,
            'status': session_data.get('status', 'unknown'),
            'progress': session_data.get('progress', 0),
            'created_at': session_data.get('created_at'),
            'updated_at': session_data.get('updated_at'),
            'url': session_data.get('url'),
            'analysis_type': session_data.get('analysis_type'),
            'processing_steps': session_data.get('processing_steps', [])
        }
        
        # Include error message if failed
        if session_data.get('status') == 'failed':
            response_data['error'] = session_data.get('error_message', 'Analysis failed')
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logging.error(f"Status check error for session {session_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@analysis_bp.route('/results/<session_id>', methods=['GET'])
@require_auth
def get_analysis_results(session_id):
    """Get the results of a completed analysis"""
    try:
<<<<<<< Updated upstream
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
=======
        user_id = request.user_id
        
        # Get session data
        session_result = AnalysisSession.get_session(session_id)
        
        if not session_result['success']:
            return jsonify({
                'success': False,
                'error': session_result['error']
            }), 404
        
        session_data = session_result['session']
        
        # Verify user owns this session
        if session_data.get('user_id') != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Check if analysis is completed
        if session_data.get('status') != 'completed':
            return jsonify({
                'success': False,
                'error': f'Analysis not completed. Current status: {session_data.get("status", "unknown")}'
            }), 400
        
        # Get results
        results = session_data.get('results')
        if not results:
            return jsonify({
                'success': False,
                'error': 'No results available'
            }), 404
        
        # Create access audit log
        access_details = {
            'session_id': session_id,
            'results_accessed': True,
            'user_agent': request.headers.get('User-Agent')
        }
        AuditLog.create_log(
            user_id=user_id,
            action='results_accessed',
            details=access_details,
            ip_address=request.remote_addr
        )
        
>>>>>>> Stashed changes
        return jsonify({
            'success': True,
            'session_id': session_id,
            'results': results,
<<<<<<< Updated upstream
            'analysis_type': session.get('analysis_type'),
            'completed_at': session.get('completed_at').isoformat() if session.get('completed_at') else None,
            'social_media_url': session.get('social_media_url'),
            'detected_platform': session.get('detected_platform'),
            'detected_username': session.get('detected_username')
=======
            'analysis_type': session_data.get('analysis_type'),
            'url': session_data.get('url'),
            'completed_at': session_data.get('completed_at'),
            'processing_steps': session_data.get('processing_steps', [])
>>>>>>> Stashed changes
        }), 200

    except Exception as e:
        logging.error(f"Results retrieval error for session {session_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@analysis_bp.route('/history', methods=['GET'])
@require_auth
def get_analysis_history():
    """Get user's analysis history"""
    try:
<<<<<<< Updated upstream
        user = get_current_user()
        user_id = user['user_id']

        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # Cap at 50

        sessions = AnalysisSession.get_user_sessions(user_id, limit)

        # Format sessions for response
        history = []
=======
        user_id = request.user_id
        limit = request.args.get('limit', 10, type=int)
        
        # Validate limit
        if limit > 50:
            limit = 50
        
        logging.info(f"Getting analysis history for user {user_id}, limit: {limit}")
        
        # Get user sessions
        sessions_result = AnalysisSession.get_user_sessions(user_id, limit)
        
        if not sessions_result['success']:
            logging.error(f"History retrieval error: {sessions_result['error']}")
            return jsonify({
                'success': False,
                'error': 'Failed to retrieve analysis history'
            }), 500
        
        sessions = sessions_result['sessions']
        
        # Format sessions for frontend
        formatted_sessions = []
>>>>>>> Stashed changes
        for session in sessions:
            formatted_session = {
                'session_id': session.get('session_id'),
                'url': session.get('url'),
                'analysis_type': session.get('analysis_type'),
                'status': session.get('status'),
                'progress': session.get('progress', 0),
<<<<<<< Updated upstream
                'detected_platform': session.get('detected_platform'),
                'detected_username': session.get('detected_username'),
                'created_at': session['created_at'].isoformat() if session.get('created_at') else None,
                'completed_at': session.get('completed_at').isoformat() if session.get('completed_at') else None
            })

=======
                'created_at': session.get('created_at'),
                'completed_at': session.get('completed_at'),
                'has_results': bool(session.get('results'))
            }
            
            # Include error message for failed analyses
            if session.get('status') == 'failed':
                formatted_session['error_message'] = session.get('error_message')
            
            formatted_sessions.append(formatted_session)
        
>>>>>>> Stashed changes
        return jsonify({
            'success': True,
            'sessions': formatted_sessions,
            'total_count': len(formatted_sessions)
        }), 200

    except Exception as e:
        logging.error(f"History retrieval error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@analysis_bp.route('/delete/<session_id>', methods=['DELETE'])
@require_auth
def delete_analysis(session_id):
    """Delete an analysis session and its data"""
    try:
<<<<<<< Updated upstream
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

=======
        user_id = request.user_id
        
        # Get session to verify ownership
        session_result = AnalysisSession.get_session(session_id)
        
        if not session_result['success']:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        session_data = session_result['session']
        
        # Verify user owns this session
        if session_data.get('user_id') != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Delete the session
        delete_result = AnalysisSession.delete_session(session_id)
        
        if not delete_result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to delete analysis session'
            }), 500
        
        # Create deletion audit log (GDPR compliance)
        deletion_details = {
            'session_id': session_id,
            'data_deleted': True,
            'deletion_requested_by_user': True,
            'url': session_data.get('url'),
            'analysis_type': session_data.get('analysis_type'),
            'user_agent': request.headers.get('User-Agent')
        }
        AuditLog.create_log(
            user_id=user_id,
            action='data_deletion',
            details=deletion_details,
            ip_address=request.remote_addr
        )
        
        logging.info(f"Analysis session deleted by user {user_id}: {session_id}")
        
>>>>>>> Stashed changes
        return jsonify({
            'success': True,
            'message': 'Analysis session deleted successfully'
        }), 200

    except Exception as e:
<<<<<<< Updated upstream
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

=======
        logging.error(f"Analysis deletion error for session {session_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@analysis_bp.route('/debug', methods=['POST'])
@require_auth
def debug_request():
    """Debug endpoint to test API requests"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        logging.info(f"Debug - User ID: {user_id}")
        logging.info(f"Debug - Raw request data: {data}")
        logging.info(f"Debug - Request content type: {request.content_type}")
        logging.info(f"Debug - Request headers: {dict(request.headers)}")
        logging.info(f"Debug - Remote address: {request.remote_addr}")
        
        return jsonify({
            'success': True,
            'debug_info': {
                'user_id': user_id,
                'received_data': data,
                'content_type': request.content_type,
                'headers': dict(request.headers),
                'remote_addr': request.remote_addr,
                'method': request.method,
                'endpoint': request.endpoint
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Debug error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers for the blueprint
@analysis_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request'
    }), 400

@analysis_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 'Unauthorized'
    }), 401

@analysis_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 'Forbidden'
    }), 403

@analysis_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found'
    }), 404

@analysis_bp.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded'
    }), 429

@analysis_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
>>>>>>> Stashed changes
