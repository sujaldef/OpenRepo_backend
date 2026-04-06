from jose import jwt
from datetime import datetime, timedelta

SECRET = "SUPER_SECRET_KEY_CHANGE_THIS"
ALGO = "HS256"

def create_token(data: dict, days=7):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(days=days)
    return jwt.encode(payload, SECRET, algorithm=ALGO)
