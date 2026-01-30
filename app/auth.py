from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic_settings import BaseSettings

from app.database import get_db
from app.models import Role, User
import os

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(
        password: str
        ) -> str:
    return pwd_context.hash(password)

def verify_password(
        plain_password: str,
        hashed_password: str
        ) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
        ) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
        ) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role_str: str = payload.get("role")

        if username is None:
            raise credentials_exception
        try:
            token_role = Role(role_str) if role_str else Role.USER
        except ValueError:
            token_role = Role.USER
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    user.role = token_role
    
    return user

def get_current_active_user(
        current_user: User = Depends(get_current_user)
        ) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if current_user.role != Role.USER:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource.")
    return current_user

def get_current_admin_user(
        current_user: User = Depends(get_current_user)
        ) -> User:
    if current_user.role != Role.ADMIN or not current_user.is_active:
        raise HTTPException(status_code=403, detail="Admin access required.")
    return current_user
