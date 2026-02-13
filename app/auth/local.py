from datetime import timedelta
from app.auth.core import create_access_token, JWT_ACCESS_TOKEN_EXPIRE_MINUTES

def create_user_token(user):
    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
