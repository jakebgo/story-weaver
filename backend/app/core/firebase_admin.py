import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
import os
from .secret_manager import get_secret

load_dotenv()

def initialize_firebase():
    """Initialize Firebase Admin SDK with credentials from Secret Manager."""
    try:
        # Get the service account credentials from Secret Manager
        service_account = get_secret("firebase-private-key")
        
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(service_account)
        firebase_admin.initialize_app(cred)
        return True
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}")
        return False

# Initialize Firebase
initialize_firebase()

def verify_token(token: str) -> dict:
    """Verify the Firebase ID token."""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise ValueError(f"Invalid token: {str(e)}") 