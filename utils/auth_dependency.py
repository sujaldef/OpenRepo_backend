from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

SECRET = "SUPER_SECRET_KEY_CHANGE_THIS"
ALGO = "HS256"

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        return payload["user_id"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
