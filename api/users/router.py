from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from starlette import status
from database.connection import get_db
from database.models import User, Role
from .auth.verification import generate_verification_code
# from .hash import verify_password
from auth.hash import verify_password
# from .ouath2 import create_access_token, get_current_user
from auth.ouath2 import create_access_token, get_current_user
from .endpoints import create, confirm_email, send_reset_password_email, reset_password, update
from .schema.input_chema import UserIn, UserResetPassword, ChangePassword, UpdateUser
from .schema.output_schema import UserOu
from .utils import create_reset_password_token, validate_token
from cache.connection import redis_client
from dependency.dependency import verify_ip
from datetime import timedelta

user_app = APIRouter(prefix="/users", tags=["User"])


# Config redis-connection


@user_app.get("/me", dependencies=[Depends(verify_ip), Depends(RateLimiter(times=5, seconds=60))])
async def user_info(current_user: User = Depends(get_current_user)):
    validate_token(current_user)

    return {"email": current_user["email"]}


@user_app.post("/create", response_model=UserOu, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def register(data: UserIn, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    return create(user=data, db=db, background_tasks=background_tasks)


@user_app.get("/confirm/{token}", response_model=UserOu, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def confirm_registration(token: str, db: Session = Depends(get_db)):
    user = confirm_email(token, db)
    return user


@user_app.post("/token", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def request_login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The Username Doesn't Exist")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The Password Is Incorrect")

    verification_code = generate_verification_code()
    redis_client.set(f"2fa_code_{user.email}", verification_code, ex=120)

    return {"message": f"Verification code for {user.email}: {verification_code}"}


# Define the token expiry duration
TOKEN_EXPIRE_MINUTES = 30
token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)

@user_app.post("/verify-code", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def verify_code_endpoint(
        request: Request,
        email: str,
        code: int,
        db: Session = Depends(get_db)
):
    stored_code = redis_client.get(f"2fa_code_{email}")

    if stored_code is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code expired or not found.")

    if int(stored_code) != code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code.")

    user = db.query(User).filter(User.email == email).first()
    client_ip = request.client.host
    role_name = user.role.slug
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "scope": role_name, "ip": client_ip},
        expires_delta=token_expires
    )

    redis_client.set(f"{user.username}_token", access_token, ex=TOKEN_EXPIRE_MINUTES * 60)

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'userID': user.id,
        'username': user.email
    }


@user_app.post("/reset-password-request", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def reset_password_request(data: UserResetPassword, background_tasks: BackgroundTasks):
    return send_reset_password_email(email=data.email, background_tasks=background_tasks)


@user_app.post("/reset-password/{token}")
def confirm_reset(token: str, password: ChangePassword, db: Session = Depends(get_db)):
    return reset_password(token, password, db)


@user_app.patch("/update/{user_id}", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def update_user(user_id: int, ip_check: UpdateUser, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return update(db=db, pk=user_id, role=current_user["role"], ip_check=ip_check)


@user_app.delete("/logout", dependencies=[Depends(verify_ip), Depends(RateLimiter(times=5, seconds=60))])
def logout(current_user: User = Depends(get_current_user)):
    validate_token(current_user)

    token_key = f"{current_user['username']}_token"
    redis_client.delete(token_key)

    return {"message": "Done"}
