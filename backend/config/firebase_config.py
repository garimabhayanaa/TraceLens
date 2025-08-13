# config/firebase_config.py
import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FirebaseConfig:
    """Firebase configuration and initialization"""
    
    def __init__(self, service_account_path: str = None):
        self.db = None
        self.auth_client = None
        self.app = None
        self.service_account_path = service_account_path or 'serviceAccountKey.json'
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
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
            
            # Initialize Firestore
            self.db = firestore.client()
            self.auth_client = auth
            
            logger.info("✅ Firebase Firestore and Auth initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Firebase initialization failed: {str(e)}")
            raise
    
    def get_firestore_client(self):
        """Get Firestore client"""
        return self.db
    
    def get_auth_client(self):
        """Get Auth client"""
        return self.auth_client

# Global Firebase instance
firebase_config = FirebaseConfig()

def get_db():
    """Get Firestore database instance"""
    return firebase_config.get_firestore_client()

def get_auth():
    """Get Firebase Auth instance"""
    return firebase_config.get_auth_client()
