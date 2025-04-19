import os
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def get_test_token():
    """Generate a test Firebase token for development."""
    try:
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate({
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
        })
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        # Create a test user if it doesn't exist
        try:
            user = auth.get_user_by_email("test@example.com")
        except auth.UserNotFoundError:
            user = auth.create_user(
                email="test@example.com",
                password="testpassword123"
            )
        
        # Generate custom token
        custom_token = auth.create_custom_token(user.uid)
        
        # Exchange custom token for ID token
        import requests
        response = requests.post(
            "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken",
            params={"key": os.getenv("FIREBASE_WEB_API_KEY")},
            json={"token": custom_token.decode(), "returnSecureToken": True}
        )
        
        if response.status_code == 200:
            id_token = response.json()["idToken"]
            print(f"\nTest Token: {id_token}\n")
            return id_token
        else:
            print(f"Error getting ID token: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error generating test token: {str(e)}")
        return None

if __name__ == "__main__":
    get_test_token() 