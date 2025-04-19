from fastapi import APIRouter, Depends
from ..core.auth_middleware import verify_token_middleware

router = APIRouter()

@router.get("/me")
async def get_current_user(user = Depends(verify_token_middleware)):
    """Get the current user's information."""
    return {
        "uid": user["uid"],
        "email": user.get("email"),
        "email_verified": user.get("email_verified", False)
    } 