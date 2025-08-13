import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)


class FirebaseConfig:
    """Firebase configuration and initialization with enhanced connectivity"""

    def __init__(self, service_account_path: str = None):
        self.db = None
        self.auth_client = None
        self.app = None
        self.service_account_path = service_account_path or 'serviceAccountKey.json'
        self.connection_retries = 3
        self.retry_delay = 2
        self.initialize_firebase()

    def initialize_firebase(self):
        """Initialize Firebase Admin SDK with retry logic"""
        for attempt in range(self.connection_retries):
            try:
                # Check if Firebase is already initialized
                if firebase_admin._apps:
                    self.app = firebase_admin.get_app()
                    logger.info("Using existing Firebase app")
                else:
                    # Initialize Firebase with service account
                    if os.path.exists(self.service_account_path):
                        cred = credentials.Certificate(self.service_account_path)
                        self.app = firebase_admin.initialize_app(cred)
                        logger.info("Firebase initialized with service account key")
                    else:
                        # Fallback to environment variables
                        cred = credentials.ApplicationDefault()
                        self.app = firebase_admin.initialize_app(cred)
                        logger.info("Firebase initialized with application default credentials")

                # Initialize Firestore with connection test
                self.db = firestore.client()
                self.auth_client = auth

                # Test connection
                self._test_connection()

                logger.info("✅ Firebase Firestore and Auth initialized successfully")
                return

            except Exception as e:
                logger.error(f"❌ Firebase initialization attempt {attempt + 1} failed: {str(e)}")

                if attempt < self.connection_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("❌ All Firebase initialization attempts failed")
                    # Don't raise exception - allow app to continue with fallback
                    self.db = None
                    self.auth_client = None

    def _test_connection(self):
        """Test Firestore connection"""
        try:
            # Simple connectivity test
            test_collection = self.db.collection('_connection_test')
            # This will verify connection without creating documents
            list(test_collection.limit(1).get())
            logger.info("✅ Firestore connection test passed")
        except Exception as e:
            logger.warning(f"⚠️ Firestore connection test failed: {str(e)}")
            # Don't fail initialization for connection test failure

    def get_firestore_client(self):
        """Get Firestore client with availability check"""
        if not self.db:
            logger.warning("Firestore client not available - attempting re-initialization")
            self.initialize_firebase()
        return self.db

    def get_auth_client(self):
        """Get Auth client"""
        return self.auth_client

    def is_connected(self):
        """Check if Firebase is properly connected"""
        return self.db is not None and self.auth_client is not None


# Global Firebase instance
firebase_config = FirebaseConfig()


def get_db():
    """Get Firestore database instance"""
    return firebase_config.get_firestore_client()


def get_auth():
    """Get Firebase Auth instance"""
    return firebase_config.get_auth_client()


def is_firebase_available():
    """Check if Firebase services are available"""
    return firebase_config.is_connected()

