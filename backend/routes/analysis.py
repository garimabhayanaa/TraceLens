from flask import Blueprint, request, jsonify
from middleware.firebase_auth import require_auth
from services.ai_analysis_service import AIAnalysisService
from models.firestore_models import AnalysisSession, FirestoreUser, AuditLog
import logging
import threading
import time
from datetime import datetime
import uuid

# Create blueprint
analysis_bp = Blueprint('analysis', __name__)

# Initialize AI analysis service
ai_service = AIAnalysisService()

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
            logging.error("No JSON data received")
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Accept both 'url' and 'social_media_url' parameters for compatibility
        url = data.get('url') or data.get('social_media_url', '').strip()
        analysis_type = data.get('analysis_type', 'comprehensive').strip()
        
        logging.info(f"Extracted URL: '{url}', Analysis Type: '{analysis_type}'")
        
        # Validate URL
        if not url:
            logging.error("URL is empty or missing")
            return jsonify({
                'success': False,
                'error': 'Social media URL is required'
            }), 400
            
        # Basic URL validation (since URL validator might be causing issues)
        if not url.startswith(('http://', 'https://')):
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
            }), 429
        
        # Create analysis session
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
        
        # ✅ FIXED: Extract request context data BEFORE starting background thread
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # Create audit log (within request context)
        audit_details = {
            'url': url,
            'analysis_type': analysis_type,
            'session_id': session_id,
            'user_agent': user_agent,
            'consent_given': True
        }
        AuditLog.create_log(
            user_id=user_id,
            action='analysis_start',
            details=audit_details,
            ip_address=ip_address
        )
        
        # ✅ FIXED: Start analysis in background thread WITHOUT flask context dependencies
        def run_analysis(user_id, ip_address, user_agent, session_id, url, analysis_type):
            """Background analysis function - NO Flask request context access"""
            try:
                logging.info(f"Starting background analysis for session: {session_id}")
                start_time = time.time()
                
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
                    
                    # Create completion audit log (without request context)
                    completion_details = {
                        'session_id': session_id,
                        'analysis_completed': True,
                        'results_generated': True,
                        'processing_time_seconds': time.time() - start_time,
                        'user_agent': user_agent  # Use passed parameter
                    }
                    AuditLog.create_log(
                        user_id=user_id,
                        action='analysis_completed',
                        details=completion_details,
                        ip_address=ip_address  # Use passed parameter
                    )
                    
                    logging.info(f"Analysis completed successfully for session: {session_id}")
                else:
                    # Mark as failed
                    error_msg = analysis_results.get('error', 'Analysis failed due to unknown error')
                    AnalysisSession.mark_failed(session_id, error_msg)
                    
                    # Create failure audit log (without request context)
                    failure_details = {
                        'session_id': session_id,
                        'error_message': error_msg,
                        'analysis_failed': True,
                        'user_agent': user_agent  # Use passed parameter
                    }
                    AuditLog.create_log(
                        user_id=user_id,
                        action='analysis_failed',
                        details=failure_details,
                        ip_address=ip_address  # Use passed parameter
                    )
                    
                    logging.error(f"Analysis failed for session {session_id}: {error_msg}")
                    
            except Exception as e:
                logging.error(f"Background analysis error for session {session_id}: {str(e)}")
                AnalysisSession.mark_failed(session_id, f"Internal processing error: {str(e)}")
                
                # Create error audit log (without request context)
                error_details = {
                    'session_id': session_id,
                    'internal_error': str(e),
                    'analysis_failed': True,
                    'user_agent': user_agent  # Use passed parameter
                }
                AuditLog.create_log(
                    user_id=user_id,
                    action='analysis_error',
                    details=error_details,
                    ip_address=ip_address  # Use passed parameter
                )
        
        # Start background analysis with extracted context data
        analysis_thread = threading.Thread(
            target=run_analysis, 
            args=(user_id, ip_address, user_agent, session_id, url, analysis_type),
            daemon=True
        )
        analysis_thread.start()
        
        logging.info(f"Analysis session started successfully: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Analysis started successfully',
            'estimated_completion_minutes': 2,
            'daily_usage_remaining': daily_limit - daily_usage - 1
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
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'results': results,
            'analysis_type': session_data.get('analysis_type'),
            'url': session_data.get('url'),
            'completed_at': session_data.get('completed_at'),
            'processing_steps': session_data.get('processing_steps', [])
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
        for session in sessions:
            formatted_session = {
                'session_id': session.get('session_id'),
                'url': session.get('url'),
                'analysis_type': session.get('analysis_type'),
                'status': session.get('status'),
                'progress': session.get('progress', 0),
                'created_at': session.get('created_at'),
                'completed_at': session.get('completed_at'),
                'has_results': bool(session.get('results'))
            }
            
            # Include error message for failed analyses
            if session.get('status') == 'failed':
                formatted_session['error_message'] = session.get('error_message')
            
            formatted_sessions.append(formatted_session)
        
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
        
        return jsonify({
            'success': True,
            'message': 'Analysis session deleted successfully'
        }), 200
        
    except Exception as e:
        logging.error(f"Analysis deletion error for session {session_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
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
