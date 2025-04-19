import os
import json
from dotenv import load_dotenv
from dotenv import set_key

def setup_firebase_credentials():
    """
    Set up the Firebase Admin SDK credentials.
    """
    # Load environment variables
    load_dotenv()
    
    # Check if the service account JSON file exists
    service_account_path = os.path.join(os.path.dirname(__file__), "service-account.json")
    
    if not os.path.exists(service_account_path):
        print("Error: service-account.json file not found.")
        print("Please download your Firebase service account key from the Firebase Console.")
        print("1. Go to Project Settings > Service Accounts")
        print("2. Click 'Generate New Private Key'")
        print("3. Save the downloaded JSON file as 'service-account.json' in the backend directory")
        return False
    
    try:
        # Read the service account JSON file
        with open(service_account_path, "r") as f:
            service_account = json.load(f)
        
        # Set environment variables
        env_vars = {
            "FIREBASE_PROJECT_ID": service_account["project_id"],
            "FIREBASE_PRIVATE_KEY_ID": service_account["private_key_id"],
            "FIREBASE_PRIVATE_KEY": service_account["private_key"],
            "FIREBASE_CLIENT_EMAIL": service_account["client_email"],
            "FIREBASE_CLIENT_ID": service_account["client_id"],
            "FIREBASE_CLIENT_X509_CERT_URL": service_account["client_x509_cert_url"]
        }
        
        # Update .env file
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        
        for key, value in env_vars.items():
            set_key(env_path, key, value)
        
        print("Firebase Admin SDK credentials set up successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    setup_firebase_credentials() 