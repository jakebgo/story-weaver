import firebase_admin
from firebase_admin import auth
from dotenv import load_dotenv
import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_test_token():
    """Get a Firebase ID token for testing."""
    try:
        # Initialize Firebase Admin SDK if not already initialized
        if not firebase_admin._apps:
            from app.core.firebase_admin import initialize_firebase
            initialize_firebase()
            logger.info("Firebase Admin SDK initialized")
        
        # Create a test user
        test_email = "test@example.com"
        test_password = "testpassword123"
        
        try:
            user = auth.get_user_by_email(test_email)
            logger.info(f"Retrieved existing test user: {test_email}")
        except:
            user = auth.create_user(
                email=test_email,
                password=test_password
            )
            logger.info(f"Created new test user: {test_email}")
        
        # Generate a custom token
        custom_token = auth.create_custom_token(user.uid).decode('utf-8')
        logger.info("Generated custom token")
        
        # Get API key from environment
        api_key = os.getenv("FIREBASE_WEB_API_KEY")
        if not api_key:
            raise ValueError("FIREBASE_WEB_API_KEY not found in environment variables")
            
        # Exchange custom token for ID token using Firebase Auth REST API
        response = requests.post(
            "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken",
            params={"key": api_key},
            json={
                "token": custom_token,
                "returnSecureToken": True
            }
        )
        
        if response.status_code != 200:
            error_text = response.text
            logger.error(f"Failed to exchange custom token: {error_text}")
            raise Exception(f"Failed to exchange custom token: {error_text}")
            
        id_token = response.json()["idToken"]
        logger.info("Successfully obtained ID token")
        
        print("\nTest user details:")
        print(f"Email: {test_email}")
        print(f"Password: {test_password}")
        print(f"UID: {user.uid}")
        
        return id_token
        
    except Exception as e:
        logger.error(f"Error getting test token: {str(e)}")
        return None

if __name__ == "__main__":
    token = get_test_token()
    if token:
        print("\nSuccessfully obtained Firebase ID token")
    else:
        print("\nFailed to obtain Firebase ID token") 