# models/firestore_models.py

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Import Firebase config
try:
    from config.firebase_config import firebase_config, is_firebase_available

    db = firebase_config.get_firestore_client()
except ImportError:
    # Fallback to direct initialization
    import os

    try:
        if os.path.exists('serviceAccountKey.json'):
            db = firestore.Client.from_service_account_json('serviceAccountKey.json')
        else:
            db = firestore.Client()
        firebase_available = True
    except Exception as e:
        db = None
        firebase_available = False

logger = logging.getLogger(__name__)


def ensure_connection():
    """Ensure Firebase connection is available"""
    global db
    if not db or not is_firebase_available():
        logger.warning("Firebase connection not available - using offline mode")
        return False
    return True


class FirestoreUser:
    """Firestore User model with offline handling"""

    COLLECTION = 'users'

    @classmethod
    def create(cls, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user document"""
        try:
            if not ensure_connection():
                # Return mock data for offline mode
                return {
                    'id': user_id,
                    **user_data,
                    'created_at': datetime.utcnow(),
                    'subscription_tier': 'free',
                    'daily_usage_count': 0,
                    'offline_mode': True
                }

            user_ref = db.collection(cls.COLLECTION).document(user_id)
            user_doc = {
                **user_data,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'subscription_tier': user_data.get('subscription_tier', 'free'),
                'daily_usage_count': 0,
                'privacy_level': user_data.get('privacy_level', 'standard'),
                'last_analysis': None,
                'total_analyses': 0
            }

            user_ref.set(user_doc)
            logger.info(f"User created: {user_id}")
            return {'id': user_id, **user_doc}

        except Exception as e:
            logger.error(f"Error creating user {user_id}: {str(e)}")
            # Return fallback data
            return {
                'id': user_id,
                **user_data,
                'created_at': datetime.utcnow(),
                'subscription_tier': 'free',
                'daily_usage_count': 0,
                'error_mode': True
            }

    @classmethod
    def get_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID with offline fallback"""
        try:
            if not ensure_connection():
                # Return mock user data for offline mode
                return {
                    'id': user_id,
                    'subscription_tier': 'free',
                    'daily_usage_count': 0,
                    'privacy_level': 'standard',
                    'total_analyses': 0,
                    'offline_mode': True
                }

            doc = db.collection(cls.COLLECTION).document(user_id).get()
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
            return None

        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            # Return fallback user data
            return {
                'id': user_id,
                'subscription_tier': 'free',
                'daily_usage_count': 0,
                'privacy_level': 'standard',
                'total_analyses': 0,
                'error_mode': True
            }

    @classmethod
    def update(cls, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user document"""
        try:
            if not ensure_connection():
                logger.warning(f"Offline mode: Cannot update user {user_id}")
                return False

            user_ref = db.collection(cls.COLLECTION).document(user_id)
            update_data['updated_at'] = datetime.utcnow()
            user_ref.update(update_data)
            logger.info(f"User updated: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            return False

    @classmethod
    def increment_usage(cls, user_id: str) -> bool:
        """Increment daily usage count"""
        try:
            if not ensure_connection():
                logger.warning(f"Offline mode: Cannot increment usage for {user_id}")
                return False

            user_ref = db.collection(cls.COLLECTION).document(user_id)
            from google.cloud.firestore import Increment
            user_ref.update({
                'daily_usage_count': Increment(1),
                'total_analyses': Increment(1),
                'last_analysis': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            return True

        except Exception as e:
            logger.error(f"Error incrementing usage for {user_id}: {str(e)}")
            return False


class AnalysisSession:
    """Analysis session model with offline handling"""

    COLLECTION = 'analysis_sessions'

    @classmethod
    def create(cls, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new analysis session"""
        try:
            session_id = str(uuid.uuid4())

            if not ensure_connection():
                # Return mock session for offline mode
                return {
                    'id': session_id,
                    **session_data,
                    'created_at': datetime.utcnow(),
                    'status': 'pending',
                    'progress': 0,
                    'offline_mode': True
                }

            session_ref = db.collection(cls.COLLECTION).document(session_id)
            session_doc = {
                **session_data,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(hours=24),
                'status': 'pending',
                'progress': 0
            }

            session_ref.set(session_doc)
            logger.info(f"Analysis session created: {session_id}")
            return {'id': session_id, **session_doc}

        except Exception as e:
            logger.error(f"Error creating analysis session: {str(e)}")
            # Return fallback session
            session_id = str(uuid.uuid4())
            return {
                'id': session_id,
                **session_data,
                'created_at': datetime.utcnow(),
                'status': 'pending',
                'progress': 0,
                'error_mode': True
            }

    @classmethod
    def get_by_id(cls, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            if not ensure_connection():
                # Return mock session for offline mode
                return {
                    'id': session_id,
                    'status': 'pending',
                    'progress': 0,
                    'offline_mode': True
                }

            doc = db.collection(cls.COLLECTION).document(session_id).get()
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
            return None

        except Exception as e:
            logger.error(f"Error getting session {session_id}: {str(e)}")
            return None

    @classmethod
    def update(cls, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update session"""
        try:
            if not ensure_connection():
                logger.warning(f"Offline mode: Cannot update session {session_id}")
                return False

            session_ref = db.collection(cls.COLLECTION).document(session_id)
            update_data['updated_at'] = datetime.utcnow()
            session_ref.update(update_data)
            return True

        except Exception as e:
            logger.error(f"Error updating session {session_id}: {str(e)}")
            return False

    @classmethod
    def get_user_sessions(cls, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user analysis sessions with offline fallback"""
        try:
            if not ensure_connection():
                # Return empty list for offline mode
                logger.warning(f"Offline mode: Cannot fetch sessions for {user_id}")
                return []

            sessions_ref = db.collection(cls.COLLECTION)

            # Simple query that doesn't require composite index
            query = sessions_ref.where(filter=FieldFilter('user_id', '==', user_id)) \
                .limit(limit)

            docs = query.get()
            sessions = []
            for doc in docs:
                session_data = doc.to_dict()
                session_data['id'] = doc.id
                sessions.append(session_data)

            # Sort in Python instead of Firestore to avoid index requirement
            sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)

            return sessions

        except Exception as e:
            logger.error(f"Error getting user sessions for {user_id}: {str(e)}")
            return []

    @classmethod
    def delete_expired(cls) -> int:
        """Delete expired sessions"""
        try:
            if not ensure_connection():
                logger.warning("Offline mode: Cannot delete expired sessions")
                return 0

            now = datetime.utcnow()
            expired_query = (db.collection(cls.COLLECTION)
                             .where('expires_at', '<', now)
                             .limit(100))

            expired_docs = expired_query.stream()
            deleted_count = 0
            batch = db.batch()

            for doc in expired_docs:
                batch.delete(doc.reference)
                deleted_count += 1

            if deleted_count > 0:
                batch.commit()
                logger.info(f"Deleted {deleted_count} expired sessions")

            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting expired sessions: {str(e)}")
            return 0


class AuditLog:
    """Audit logging model with offline handling"""

    COLLECTION = 'audit_logs'

    @classmethod
    def create(cls, log_data: Dict[str, Any]) -> Optional[str]:
        """Create audit log entry"""
        try:
            if not ensure_connection():
                logger.warning("Offline mode: Cannot create audit log")
                return None

            log_ref = db.collection(cls.COLLECTION).document()
            log_doc = {
                **log_data,
                'timestamp': datetime.utcnow(),
                'log_id': log_ref.id
            }

            log_ref.set(log_doc)
            logger.info(f"Audit log created: {log_ref.id}")
            return log_ref.id

        except Exception as e:
            logger.error(f"Error creating audit log: {str(e)}")
            return None

    @classmethod
    def get_user_logs(cls, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's audit logs"""
        try:
            if not ensure_connection():
                logger.warning(f"Offline mode: Cannot fetch audit logs for {user_id}")
                return []

            query = (db.collection(cls.COLLECTION)
                     .where(filter=FieldFilter('user_id', '==', user_id))
                     .limit(limit))

            docs = query.get()
            logs = []
            for doc in docs:
                log_data = doc.to_dict()
                log_data['id'] = doc.id
                logs.append(log_data)

            # Sort by timestamp in Python to avoid index issues
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return logs

        except Exception as e:
            logger.error(f"Error getting audit logs for {user_id}: {str(e)}")
            return []

    @classmethod
    def log_action(cls, user_id: str, action: str, details: Dict[str, Any] = None) -> Optional[str]:
        """Convenience method to log user actions"""
        log_data = {
            'user_id': user_id,
            'action': action,
            'details': details or {},
            'ip_address': None,  # Can be populated from request context
            'user_agent': None  # Can be populated from request context
        }
        return cls.create(log_data)

    @classmethod
    def get_system_logs(cls, limit: int = 100) -> List[Dict[str, Any]]:
        """Get system-wide audit logs"""
        try:
            if not ensure_connection():
                logger.warning("Offline mode: Cannot fetch system logs")
                return []

            query = (db.collection(cls.COLLECTION)
                     .limit(limit))

            docs = query.get()
            logs = []
            for doc in docs:
                log_data = doc.to_dict()
                log_data['id'] = doc.id
                logs.append(log_data)

            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return logs

        except Exception as e:
            logger.error(f"Error getting system logs: {str(e)}")
            return []

# Helper functions
def get_db():
    """Get Firestore database client"""
    return db


# Create instances for easy access
User = FirestoreUser
Session = AnalysisSession
Audit = AuditLog
