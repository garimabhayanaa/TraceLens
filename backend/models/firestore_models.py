import logging
from datetime import datetime, timedelta, timezone
from google.cloud import firestore
from config.firebase_config import db
import uuid
from typing import Dict, List, Any, Optional

def normalize_datetime(dt):
    """Helper function to normalize datetime objects for comparison"""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        else:
            return dt
    return dt

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
                'daily_usage': 0,  # ✅ FIXED: Initialize with 0
                'lifetime_analysis_count': 0,
                'privacy_level': 'standard',
                'created_at': firestore.SERVER_TIMESTAMP,
                'last_login': firestore.SERVER_TIMESTAMP,
                'preferences': {
                    'email_notifications': True,
                    'data_retention_days': 1,
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
                
                # ✅ FIXED: Ensure daily_usage field exists
                if 'daily_usage' not in user_data:
                    user_data['daily_usage'] = 0
                    # Update the document to include the missing field
                    user_ref.update({'daily_usage': 0})
                
                logging.info(f"User retrieved successfully: {user_id}")
                return {'success': True, 'user': user_data}
            else:
                logging.warning(f"User not found: {user_id}")
                return {'success': False, 'error': 'User not found'}
                
        except Exception as e:
            logging.error(f"Error getting user {user_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def increment_usage(user_id: str) -> Dict[str, Any]:
        """Increment user's daily usage count"""
        try:
            user_ref = db.collection('users').document(user_id)
            
            @firestore.transactional
            def increment_counters(transaction, user_ref):
                user_doc = user_ref.get(transaction=transaction)
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    current_usage = user_data.get('daily_usage', 0)  # ✅ Default to 0 if missing
                    lifetime_count = user_data.get('lifetime_analysis_count', 0)
                    
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
                'expires_at': datetime.now(timezone.utc) + timedelta(hours=24),
                'results': None,
                'error_message': None,
                'processing_steps': [],
                'metadata': {
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
            
            session_ref = db.collection('analysis_sessions').document(session_id)
            session_ref.set(session_data)
            
            logging.info(f"Analysis session created: {session_id} for user: {user_id}")
            return {'success': True, 'session_id': session_id, 'session_data': session_data}
            
        except Exception as e:
            logging.error(f"Error creating analysis session: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_progress(session_id: str, progress: int, status: str, step_description: str = None) -> Dict[str, Any]:
        """Update analysis progress - ✅ FIXED: Safe for background threads"""
        try:
            session_ref = db.collection('analysis_sessions').document(session_id)
            
            # ✅ FIXED: Use datetime instead of SERVER_TIMESTAMP in background threads
            update_data = {
                'progress': progress,
                'status': status,
                'updated_at': datetime.now(timezone.utc)  # Use UTC datetime instead of SERVER_TIMESTAMP
            }
            
            if step_description:
                session_doc = session_ref.get()
                if session_doc.exists:
                    current_steps = session_doc.to_dict().get('processing_steps', [])
                    current_steps.append({
                        'step': step_description,
                        'timestamp': datetime.now(timezone.utc),  # Use UTC datetime
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
                'completed_at': datetime.now(timezone.utc),  # Use UTC datetime
                'updated_at': datetime.now(timezone.utc)     # Use UTC datetime
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
                'failed_at': datetime.now(timezone.utc),    # Use UTC datetime
                'updated_at': datetime.now(timezone.utc)    # Use UTC datetime
            }
            
            session_ref.update(update_data)
            
            logging.error(f"Session marked as failed {session_id}: {error_message}")
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error marking session as failed {session_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_session(session_id: str) -> Dict[str, Any]:
        """Get analysis session data"""
        try:
            session_ref = db.collection('analysis_sessions').document(session_id)
            session_doc = session_ref.get()
            
            if session_doc.exists:
                session_data = session_doc.to_dict()
                
                # Handle timezone-aware datetime comparison
                expires_at = session_data.get('expires_at')
                if expires_at:
                    expires_at = normalize_datetime(expires_at)
                    current_time = normalize_datetime(datetime.now(timezone.utc))
                    
                    if expires_at < current_time:
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
    def get_user_sessions(user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get analysis sessions for a specific user"""
        try:
            sessions_ref = db.collection('analysis_sessions')
            query = sessions_ref.where('user_id', '==', user_id).limit(limit)
            
            sessions = []
            for doc in query.stream():
                session_data = doc.to_dict()
                session_data['session_id'] = doc.id
                sessions.append(session_data)
            
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
        """Clean up expired sessions"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
            
            # ✅ FIXED: Use where() method instead of filter()
            expired_sessions = db.collection('analysis_sessions').where(
                'created_at', '<', cutoff_time
            ).limit(100)
            
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
        """Create audit log entry - ✅ FIXED: Safe for background threads"""
        try:
            log_id = str(uuid.uuid4())
            
            log_data = {
                'log_id': log_id,
                'user_id': user_id,
                'action': action,
                'details': details,
                'ip_address': ip_address,
                'timestamp': datetime.now(timezone.utc),  # Use UTC datetime instead of SERVER_TIMESTAMP
                'user_agent': details.get('user_agent'),
                'session_id': details.get('session_id'),
                'compliance_flags': {
                    'gdpr_relevant': True,
                    'data_processing': action in ['analysis_start', 'data_collection', 'results_generated'],
                    'user_consent': details.get('consent_given', False)
                }
            }
            
            db.collection('audit_logs').document(log_id).set(log_data)
            
            logging.info(f"Audit log created: {action} for user: {user_id}")
            return {'success': True, 'log_id': log_id}
            
        except Exception as e:
            logging.error(f"Error creating audit log: {e}")
            return {'success': False, 'error': str(e)}

# Export all model classes
__all__ = ['FirestoreUser', 'AnalysisSession', 'AuditLog']
