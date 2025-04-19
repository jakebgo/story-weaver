from fastapi import Request, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
import logging
from .firebase_admin import verify_token

# Configure logging
logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Get the current user from the Firebase token.
    
    Args:
        credentials: The HTTP Authorization credentials
        
    Returns:
        dict: The user information from the Firebase token
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        token = credentials.credentials
        logger.debug("Verifying token in auth middleware...")
        logger.debug(f"Token scheme: {credentials.scheme}, Token length: {len(token)}")
        
        # Verify the token
        decoded_token = verify_token(token)
        
        # Return the user information
        return {
            "user_id": decoded_token.get("user_id") or decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "email_verified": decoded_token.get("email_verified", False)
        }
        
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )

async def verify_token_middleware(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Middleware to verify Firebase ID token."""
    try:
        logger.debug("Verifying token in auth middleware...")
        token = credentials.credentials
        logger.debug(f"Token scheme: {credentials.scheme}, Token length: {len(token)}")
        decoded_token = verify_token(token)
        logger.debug(f"Successfully verified token for user: {decoded_token.get('uid')}")
        return decoded_token
    except Exception as e:
        logger.error(f"Error in auth middleware: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}"
        ) 