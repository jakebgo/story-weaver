from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from typing import Optional, Dict

security = HTTPBearer()

async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = None) -> Optional[Dict]:
    """
    Middleware to get the current user from Firebase token.
    Returns None if no token is provided (for public routes).
    Raises HTTPException if token is invalid (for protected routes).
    """
    if not credentials:
        # Try to get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        token = auth_header.split(" ")[1]
    else:
        token = credentials.credentials
    
    try:
        # Verify the token with Firebase
        decoded_token = auth.verify_id_token(token)
        
        # Return user information
        return {
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "email_verified": decoded_token.get("email_verified", False),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture")
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}"
        ) 