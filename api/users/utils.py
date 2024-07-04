from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from cache.connection import redis_client
from database.models import User
from fastapi import HTTPException, status

SECRET_KEY = "ngyfckmpqvxdsfsdfc"
ALGORITHM = "HS256"
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = 2


def create_reset_password_token(email: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_PASSWORD_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": email}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_reset_password_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except (ExpiredSignatureError, InvalidTokenError):
        return None


def validate_token(current_user: User):
    token_key = f"{current_user['username']}_token"
    exist_check = redis_client.get(token_key)
    if not exist_check:
        raise HTTPException(detail="The token is not valid", status_code=status.HTTP_401_UNAUTHORIZED)
