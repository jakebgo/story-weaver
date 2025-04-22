from fastapi import APIRouter, HTTPException, Depends
from .auth_bearer import JWTBearer
from firebase_admin import auth
from typing import Dict

router = APIRouter()
security = JWTBearer()

@router.post("/verify-token")
async def verify_token(credentials: Dict = Depends(security)) -> Dict:
    """
    Verify Firebase ID token and return user information
    """
    return {
        "uid": credentials["uid"],
        "email": credentials.get("email"),
        "email_verified": credentials.get("email_verified", False),
        "name": credentials.get("name"),
        "picture": credentials.get("picture")
    } 