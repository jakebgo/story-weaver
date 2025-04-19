from google.cloud import secretmanager
import json
import os

def get_secret(secret_id: str) -> dict:
    """
    Get a secret from Secret Manager.
    
    Args:
        secret_id: The ID of the secret to retrieve
        
    Returns:
        The secret value as a dictionary
    """
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "771376451058")
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    
    response = client.access_secret_version(request={"name": name})
    return json.loads(response.payload.data.decode("UTF-8")) 