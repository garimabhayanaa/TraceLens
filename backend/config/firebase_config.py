import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
from dotenv import load_dotenv
import json

def initialize_firebase():
    """Initialize Firebase SDK and Firestore client"""
    try:
        # Initialize the firebase app only once
        if not firebase_admin._apps:
            service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
            if service_account_json:
                service_account_info = json.loads(service_account_json)
                cred = credentials.Certificate(service_account_info)
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
