from fastapi.testclient import TestClient
from app.main import app
import pytest
import firebase_admin
from firebase_admin import auth

client = TestClient(app)

def test_verify_token_endpoint_no_token():
    """Test that the verify-token endpoint returns 401 when no token is provided"""
    response = client.post("/api/auth/verify-token")
    assert response.status_code == 401
    assert "Not authenticated" in response.text

def test_verify_token_endpoint_invalid_token():
    """Test that the verify-token endpoint returns 401 when an invalid token is provided"""
    response = client.post(
        "/api/auth/verify-token",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "Invalid authentication credentials" in response.text

# Note: To test with a valid token, you would need to:
# 1. Create a test user in Firebase
# 2. Generate a custom token for that user
# 3. Exchange the custom token for an ID token
# 4. Use that ID token in the test
# This is typically done in integration tests rather than unit tests 