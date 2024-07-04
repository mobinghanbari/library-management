from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from jwt import decode as jwt_decode, InvalidTokenError
from database.connection import get_db
from database.models import Ip, User

SECRET_KEY = "0370cd399efa3bf2f09085ee347285f7fc259e0575095d9910a80ac1cd1fc476"
ALGORITHM = "HS256"


async def verify_ip(request: Request, db: Session = Depends(get_db)):
    request_ip = request.client.host
    authorization: str = request.headers.get("Authorization")


    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid token format")

    token = authorization.split(" ")[1]  # حذف قسمت 'Bearer'

    try:
        payload = jwt_decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_ip = payload.get("ip")
        user_id = payload.get("user_id")

    except InvalidTokenError as e:
        print(f"Token decode error: {e}")
        raise HTTPException(status_code=403, detail="Invalid token")

    if not token_ip or not user_id:
        raise HTTPException(status_code=403, detail="Invalid token")


    user = db.query(User).where(User.id == user_id).first()

    if user.ip_check != False:

        # چک کردن آیپی در دیتابیس
        allowed_ip = db.query(Ip).filter(Ip.user_id == user_id, Ip.ip_address == request_ip).first()

        if not allowed_ip or request_ip != token_ip:
            raise HTTPException(status_code=403, detail="Unauthorized IP address")

