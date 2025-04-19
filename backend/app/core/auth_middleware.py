from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .firebase_admin import verify_token

security = HTTPBearer()

async def verify_token_middleware(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Middleware to verify Firebase ID token."""
    try:
        token = credentials.credentials
        decoded_token = verify_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}"
        ) 