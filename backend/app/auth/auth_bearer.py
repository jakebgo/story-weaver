from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from typing import Optional

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        try:
            credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        except HTTPException:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(credentials.credentials)
            return decoded_token
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid authentication credentials: {str(e)}") 