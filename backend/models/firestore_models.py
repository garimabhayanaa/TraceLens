# models/firestore_models.py
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from google.cloud.firestore import DocumentReference, CollectionReference
from config.firebase_config import get_db

logger = logging.getLogger(__name__)

class FirestoreUser:
    """Firestore User model"""
    
    COLLECTION = 'users'
    
    @classmethod
    def create(cls, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user document"""
        try:
            db = get_db()
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
            raise
    
    @classmethod
    def get_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            db = get_db()
            doc = db.collection(cls.COLLECTION).document(user_id).get()
            
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
            return None
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None
    
    @classmethod
    def update(cls, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user document"""
        try:
            db = get_db()
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
            db = get_db()
            user_ref = db.collection(cls.COLLECTION).document(user_id)
            
            # Use Firestore increment
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
    """Analysis session model"""
    
    COLLECTION = 'analysis_sessions'
    
    @classmethod
    def create(cls, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new analysis session"""
        try:
            db = get_db()
            session_ref = db.collection(cls.COLLECTION).document()
            
            session_doc = {
                **session_data,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(hours=24),
                'status': 'pending',
                'progress': 0
            }
            
            session_ref.set(session_doc)
            logger.info(f"Analysis session created: {session_ref.id}")
            
            return {'id': session_ref.id, **session_doc}
            
        except Exception as e:
            logger.error(f"Error creating analysis session: {str(e)}")
            raise
    
    @classmethod
    def get_by_id(cls, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            db = get_db()
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
            db = get_db()
            session_ref = db.collection(cls.COLLECTION).document(session_id)
            
            update_data['updated_at'] = datetime.utcnow()
            session_ref.update(update_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {str(e)}")
            return False
    
    @classmethod
    def get_user_sessions(cls, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's recent sessions"""
        try:
            db = get_db()
            query = (db.collection(cls.COLLECTION)
                    .where('user_id', '==', user_id)
                    .order_by('created_at', direction='DESCENDING')
                    .limit(limit))
            
            docs = query.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
            
        except Exception as e:
            logger.error(f"Error getting user sessions for {user_id}: {str(e)}")
            return []
    
    @classmethod
    def delete_expired(cls) -> int:
        """Delete expired sessions"""
        try:
            db = get_db()
            now = datetime.utcnow()
            
            # Query expired sessions
            expired_query = (db.collection(cls.COLLECTION)
                           .where('expires_at', '<', now)
                           .limit(100))  # Process in batches
            
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
    """Audit logging model"""
    
    COLLECTION = 'audit_logs'
    
    @classmethod
    def create(cls, log_data: Dict[str, Any]) -> str:
        """Create audit log entry"""
        try:
            db = get_db()
            log_ref = db.collection(cls.COLLECTION).document()
            
            log_doc = {
                **log_data,
                'timestamp': datetime.utcnow(),
                'log_id': log_ref.id
            }
            
            log_ref.set(log_doc)
            return log_ref.id
            
        except Exception as e:
            logger.error(f"Error creating audit log: {str(e)}")
            return None
    
    @classmethod
    def get_user_logs(cls, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's audit logs"""
        try:
            db = get_db()
            query = (db.collection(cls.COLLECTION)
                    .where('user_id', '==', user_id)
                    .order_by('timestamp', direction='DESCENDING')
                    .limit(limit))
            
            docs = query.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
            
        except Exception as e:
            logger.error(f"Error getting audit logs for {user_id}: {str(e)}")
            return []
