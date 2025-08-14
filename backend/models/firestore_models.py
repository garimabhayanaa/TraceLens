import logging
from datetime import datetime, timedelta
from google.cloud import firestore
from config.firebase_config import db
import uuid
import json
from typing import Dict, List, Any, Optional

class FirestoreUser:
    """User model for Firestore operations"""
    
    @staticmethod
    def create_user(user_id: str, email: str, display_name: str = None) -> Dict[str, Any]:
        """Create a new user in Firestore"""
        try:
            user_data = {
                'user_id': user_id,
                'email': email,
                'display_name': display_name,
                'subscription_tier': 'free',
                'daily_usage': 0,
                'lifetime_analysis_count': 0,
                'privacy_level': 'standard',
                'created_at': firestore.SERVER_TIMESTAMP,
                'last_login': firestore.SERVER_TIMESTAMP,
                'preferences': {
                    'email_notifications': True,
                    'data_retention_days': 1,  # 24 hours
                    'analysis_history_visible': True
                },
                'usage_limits': {
                    'daily_limit': 3,
                    'hourly_limit': 1,
                    'monthly_limit': 50
                },
                'account_status': 'active',
                'email_verified': False,
                'terms_accepted': True,
                'privacy_policy_accepted': True,
                'last_usage_reset': firestore.SERVER_TIMESTAMP
            }
            
            # Create user document
            db.collection('users').document(user_id).set(user_data)
            
            logging.info(f"User created successfully: {user_id}")
            return {'success': True, 'user_data': user_data}
            
        except Exception as e:
            logging.error(f"Error creating user {user_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_user(user_id: str) -> Dict[str, Any]:
        """Get user data from Firestore"""
        try:
            user_ref = db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                logging.info(f"User retrieved successfully: {user_id}")
                return {'success': True, 'user': user_data}
            else:
                logging.warning(f"User not found: {user_id}")
                return {'success': False, 'error': 'User not found'}
                
        except Exception as e:
            logging.error(f"Error getting user {user_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_user(user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user data in Firestore"""
        try:
            user_ref = db.collection('users').document(user_id)
            
            # Add timestamp for last update
            update_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            # Update user document
            user_ref.update(update_data)
            
            logging.info(f"User updated successfully: {user_id}")
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error updating user {user_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def increment_usage(user_id: str) -> Dict[str, Any]:
        """Increment user's daily usage count"""
        try:
            user_ref = db.collection('users').document(user_id)
            
            # Use atomic transaction to increment counters
            @firestore.transactional
            def increment_counters(transaction, user_ref):
                user_doc = user_ref.get(transaction=transaction)
                if user_doc.exists:
                    current_usage = user_doc.get('daily_usage', 0)
                    lifetime_count = user_doc.get('lifetime_analysis_count', 0)
                    
                    transaction.update(user_ref, {
                        'daily_usage': current_usage + 1,
                        'lifetime_analysis_count': lifetime_count + 1,
                        'last_analysis': firestore.SERVER_TIMESTAMP
                    })
                    
                    return current_usage + 1
                else:
                    raise Exception("User not found")
            
            transaction = db.transaction()
            new_usage = increment_counters(transaction, user_ref)
            
            logging.info(f"Usage incremented for user {user_id}: {new_usage}")
            return {'success': True, 'daily_usage': new_usage}
            
        except Exception as e:
            logging.error(f"Error incrementing usage for {user_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def reset_daily_usage(user_id: str) -> Dict[str, Any]:
        """Reset user's daily usage count"""
        try:
            user_ref = db.collection('users').document(user_id)
            user_ref.update({
                'daily_usage': 0,
                'last_usage_reset': firestore.SERVER_TIMESTAMP
            })
            
            logging.info(f"Daily usage reset for user: {user_id}")
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error resetting daily usage for {user_id}: {e}")
            return {'success': False, 'error': str(e)}

class AnalysisSession:
    """Analysis session model for Firestore operations"""
    
    @staticmethod
    def create_session(user_id: str, url: str, analysis_type: str) -> Dict[str, Any]:
        """Create a new analysis session"""
        try:
            session_id = str(uuid.uuid4())
            
            session_data = {
                'session_id': session_id,
                'user_id': user_id,
                'url': url,
                'analysis_type': analysis_type,
                'status': 'pending',
                'progress': 0,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'expires_at': datetime.utcnow() + timedelta(hours=24),  # 24-hour TTL
                'results': None,
                'error_message': None,
                'processing_steps': [],
                'metadata': {
                    'ip_address': None,  # Set by middleware
                    'user_agent': None,  # Set by middleware
                    'analysis_version': '1.0.0',
                    'frameworks_used': [
                        'privacy_framework',
                        'ethical_framework',
                        'consent_framework',
                        'legal_framework'
                    ]
                },
                'privacy_settings': {
                    'auto_delete': True,
                    'data_anonymized': True,
                    'consent_given': True,
                    'processing_purpose': 'digital_footprint_analysis'
                }
            }
            
            # Create session document with TTL
            session_ref = db.collection('analysis_sessions').document(session_id)
            session_ref.set(session_data)
            
            logging.info(f"Analysis session created: {session_id} for user: {user_id}")
            return {'success': True, 'session_id': session_id, 'session_data': session_data}
            
        except Exception as e:
            logging.error(f"Error creating analysis session: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_session(session_id: str) -> Dict[str, Any]:
        """Get analysis session data"""
        try:
            session_ref = db.collection('analysis_sessions').document(session_id)
            session_doc = session_ref.get()
            
            if session_doc.exists:
                session_data = session_doc.to_dict()
                
                # Check if session has expired
                if session_data.get('expires_at') and session_data['expires_at'] < datetime.utcnow():
                    logging.warning(f"Session expired: {session_id}")
                    return {'success': False, 'error': 'Session expired'}
                
                return {'success': True, 'session': session_data}
            else:
                logging.warning(f"Session not found: {session_id}")
                return {'success': False, 'error': 'Session not found'}
                
        except Exception as e:
            logging.error(f"Error getting session {session_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_session(session_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update analysis session"""
        try:
            session_ref = db.collection('analysis_sessions').document(session_id)
            
            # Add timestamp for last update
            update_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            # Update session document
            session_ref.update(update_data)
            
            logging.info(f"Session updated: {session_id}")
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error updating session {session_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_progress(session_id: str, progress: int, status: str, step_description: str = None) -> Dict[str, Any]:
        """Update analysis progress"""
        try:
            session_ref = db.collection('analysis_sessions').document(session_id)
            
            update_data = {
                'progress': progress,
                'status': status,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            # Add processing step if provided
            if step_description:
                # Get current session to append to processing steps
                session_doc = session_ref.get()
                if session_doc.exists:
                    current_steps = session_doc.get('processing_steps', [])
                    current_steps.append({
                        'step': step_description,
                        'timestamp': firestore.SERVER_TIMESTAMP,
                        'progress': progress
                    })
                    update_data['processing_steps'] = current_steps
            
            session_ref.update(update_data)
            
            logging.info(f"Progress updated for session {session_id}: {progress}% - {status}")
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error updating progress for session {session_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def save_results(session_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Save analysis results"""
        try:
            session_ref = db.collection('analysis_sessions').document(session_id)
            
            update_data = {
                'results': results,
                'status': 'completed',
                'progress': 100,
                'completed_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            session_ref.update(update_data)
            
            logging.info(f"Results saved for session: {session_id}")
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error saving results for session {session_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def mark_failed(session_id: str, error_message: str) -> Dict[str, Any]:
        """Mark session as failed"""
        try:
            session_ref = db.collection('analysis_sessions').document(session_id)
            
            update_data = {
                'status': 'failed',
                'error_message': error_message,
                'failed_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            session_ref.update(update_data)
            
            logging.error(f"Session marked as failed {session_id}: {error_message}")
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error marking session as failed {session_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_user_sessions(user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get analysis sessions for a specific user"""
        try:
            # Use the where() method properly with Firestore
            sessions_ref = db.collection('analysis_sessions')
            query = sessions_ref.where('user_id', '==', user_id).limit(limit)
            
            sessions = []
            for doc in query.stream():
                session_data = doc.to_dict()
                session_data['session_id'] = doc.id
                sessions.append(session_data)
            
            # Sort in Python instead of Firestore (to avoid index requirements)
            sessions.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
            
            logging.info(f"Retrieved {len(sessions)} sessions for user: {user_id}")
            return {'success': True, 'sessions': sessions}
            
        except Exception as e:
            logging.error(f"Error getting user sessions for {user_id}: {e}")
            return {'success': False, 'error': str(e), 'sessions': []}
    
    @staticmethod
    def delete_session(session_id: str) -> Dict[str, Any]:
        """Delete analysis session"""
        try:
            session_ref = db.collection('analysis_sessions').document(session_id)
            session_ref.delete()
            
            logging.info(f"Session deleted: {session_id}")
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error deleting session {session_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def cleanup_expired_sessions() -> Dict[str, Any]:
        """Clean up expired sessions (called by background task)"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Query expired sessions
            expired_sessions = db.collection('analysis_sessions').where(
                'created_at', '<', cutoff_time
            ).limit(100)  # Process in batches
            
            deleted_count = 0
            for session_doc in expired_sessions.stream():
                session_doc.reference.delete()
                deleted_count += 1
            
            logging.info(f"Cleaned up {deleted_count} expired sessions")
            return {'success': True, 'deleted_count': deleted_count}
            
        except Exception as e:
            logging.error(f"Error cleaning up expired sessions: {e}")
            return {'success': False, 'error': str(e)}

class AuditLog:
    """Audit log model for compliance and monitoring"""
    
    @staticmethod
    def create_log(user_id: str, action: str, details: Dict[str, Any], ip_address: str = None) -> Dict[str, Any]:
        """Create audit log entry"""
        try:
            log_id = str(uuid.uuid4())
            
            log_data = {
                'log_id': log_id,
                'user_id': user_id,
                'action': action,
                'details': details,
                'ip_address': ip_address,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'user_agent': details.get('user_agent'),
                'session_id': details.get('session_id'),
                'compliance_flags': {
                    'gdpr_relevant': True,
                    'data_processing': action in ['analysis_start', 'data_collection', 'results_generated'],
                    'user_consent': details.get('consent_given', False)
                }
            }
            
            # Create log document
            db.collection('audit_logs').document(log_id).set(log_data)
            
            logging.info(f"Audit log created: {action} for user: {user_id}")
            return {'success': True, 'log_id': log_id}
            
        except Exception as e:
            logging.error(f"Error creating audit log: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_user_logs(user_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get audit logs for a specific user"""
        try:
            logs_ref = db.collection('audit_logs')
            query = logs_ref.where('user_id', '==', user_id).limit(limit)
            
            logs = []
            for doc in query.stream():
                log_data = doc.to_dict()
                log_data['log_id'] = doc.id
                logs.append(log_data)
            
            # Sort by timestamp in Python
            logs.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
            
            return {'success': True, 'logs': logs}
            
        except Exception as e:
            logging.error(f"Error getting audit logs for {user_id}: {e}")
            return {'success': False, 'error': str(e), 'logs': []}

# Export all model classes
__all__ = ['FirestoreUser', 'AnalysisSession', 'AuditLog']
