import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
import os
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

def initialize_firebase():
    """Initialize Firebase Admin SDK with credentials from environment variables."""
    try:
        # Create service account dict from environment variables
        service_account = {
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
        }
        
        logger.debug("Initializing Firebase Admin SDK with service account...")
        logger.debug(f"Project ID: {service_account['project_id']}")
        logger.debug(f"Client Email: {service_account['client_email']}")
        
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(service_account)
        firebase_admin.initialize_app(cred)
        logger.info("Successfully initialized Firebase Admin SDK")
        return True
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}", exc_info=True)
        return False

# Initialize Firebase
initialize_firebase()

def verify_token(token: str) -> dict:
    """Verify the Firebase ID token."""
    try:
        logger.debug(f"Verifying token: {token[:50]}...")
        decoded_token = auth.verify_id_token(token)
        logger.debug(f"Successfully verified token for user: {decoded_token.get('uid')}")
        return decoded_token
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}", exc_info=True)
        raise ValueError(f"Invalid token: {str(e)}") 