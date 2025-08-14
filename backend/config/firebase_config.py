import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging

def initialize_firebase():
    """Initialize Firebase SDK and Firestore client"""
    try:
        # Initialize the firebase app only once
        if not firebase_admin._apps:
            service_account_path = os.path.join(os.path.dirname(__file__), '..', 'serviceAccountKey.json')
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                logging.info("Firebase initialized with service account")
            else:
                # Use default credentials if service account file not found
                firebase_admin.initialize_app()
                logging.info("Firebase initialized with default credentials")

        db = firestore.client()
        logging.info("Firestore client initialized successfully")
        return db

    except Exception as e:
        logging.error(f"Failed to initialize Firebase: {e}")
        raise

# Initialize and export the db instance
try:
    db = initialize_firebase()
except Exception as e:
    db = None
    logging.error(f"Firebase initialization failed: {e}")

# Export only db
__all__ = ['db']
