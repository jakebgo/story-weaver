import os
from app.core.secret_manager import get_secret

def test_secret_manager():
    """Test script to verify Secret Manager integration."""
    print("Testing Secret Manager integration...")
    
    # Set the Google Application Credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-dev-key.json"
    
    try:
        # Try to get the Firebase private key
        service_account = get_secret("firebase-private-key")
        print("Successfully retrieved Firebase private key from Secret Manager!")
        print(f"Project ID: {service_account['project_id']}")
        print("Service account credentials are valid.")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_secret_manager() 