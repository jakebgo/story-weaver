import os
import uvicorn
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    """
    Initialize the Firebase Admin SDK.
    """
    # Load environment variables
    load_dotenv()
    
    # Check if all required environment variables are set
    required_vars = [
        "FIREBASE_PROJECT_ID",
        "FIREBASE_PRIVATE_KEY_ID",
        "FIREBASE_PRIVATE_KEY",
        "FIREBASE_CLIENT_EMAIL",
        "FIREBASE_CLIENT_ID",
        "FIREBASE_CLIENT_X509_CERT_URL"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: The following environment variables are missing: {', '.join(missing_vars)}")
        print("Please run the setup_firebase.py script to set up your Firebase Admin SDK credentials.")
        return False
    
    try:
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
        })
        
        # Initialize the app
        firebase_admin.initialize_app(cred)
        
        print("Firebase Admin SDK initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Initialize Firebase Admin SDK
    if not initialize_firebase():
        print("Failed to initialize Firebase Admin SDK. Exiting...")
        exit(1)
    
    # Run the FastAPI server
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 