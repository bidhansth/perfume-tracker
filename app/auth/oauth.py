from jose import jwt, JWTError
from fastapi import HTTPException
from app.auth.core import JWT_SECRET_KEY, JWT_ALGORITHM

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

def create_link_token(provider, provider_sub, email, name):
    return jwt.encode(
        {"provider": provider, "provider_sub": provider_sub, "email": email, "name": name, "type": "link"},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

def decode_link_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "link":
            raise HTTPException(status_code=400, detail="Invalid link token")
        return payload
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired link token")
