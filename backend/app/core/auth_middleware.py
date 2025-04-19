from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .firebase_admin import verify_token

security = HTTPBearer()

async def verify_token_middleware(request: Request, credentials: HTTPAuthorizationCredentials = security):
    """Middleware to verify Firebase ID token."""
    try:
        token = credentials.credentials
        decoded_token = verify_token(token)
        request.state.user = decoded_token
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}"
        ) 