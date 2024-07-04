from sqlalchemy.orm import Session
from database.models import User
from .schema.input_chema import UserIn, ChangePassword, UpdateUser
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from fastapi import HTTPException, BackgroundTasks
from .email_config import conf
from auth.hash import get_password_hash

SECRET = "ngyfckmpqvxdsfsdfc"


def send_confirmation_email(user: UserIn, background_tasks):
    token = URLSafeTimedSerializer(SECRET).dumps(user.email, salt='email-confirm')
    confirm_url = f"http://localhost:8000/users/confirm/{token}"
    message = MessageSchema(
        subject="Confirm your email",
        recipients=[user.email],
        body=f"Please click the link to confirm your email: {confirm_url}",
        subtype="html"
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)


def send_reset_password_email(email: str, background_tasks):
    token = URLSafeTimedSerializer(SECRET).dumps(email, salt='reset_password_email')
    confirm_url = f"http://localhost:8000/users/reset-password/{token}"
    message = MessageSchema(
        subject="Reset Your Password",
        recipients=[email],
        body=f"Please click the link to reset your password: {confirm_url}",
        subtype="html"
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    return {"message": "reset password has sent to your email"}


def create(user: UserIn, db: Session, background_tasks: BackgroundTasks):
    user_obj = User(
        username=user.username,
        email=user.email,
        phone=user.phone,
        password=get_password_hash(user.password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    send_confirmation_email(user_obj, background_tasks)

    return user_obj


def confirm_email(token: str, db: Session):
    try:
        email = URLSafeTimedSerializer(SECRET).loads(token, salt="email-confirm", max_age=3600)
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="The confirmation link has expired.")

    user = db.query(User).filter(User.email == email).first()
    if user:
        user.is_activated = True
        db.commit()
        db.refresh(user)
        return user
    raise HTTPException(status_code=400, detail="Invalid token.")


def reset_password(token: str, password: ChangePassword, db: Session):
    try:
        email = URLSafeTimedSerializer(SECRET).loads(token, salt="reset_password_email", max_age=3600)
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="The confirmation link has expired.")

    user = db.query(User).filter(User.email == email).first()

    if password.password != password.confirm:
        return {"detail": "your entered passwords do not match"}

    user.password = get_password_hash(password.password)
    db.commit()
    db.refresh(user)
    return {"message": "Password has been reset successfully"}


def get_specific_user(db: Session, username):
    user = db.query(User).where(User.email == username)

    if not user:
        return {"detail": "The User doesn't exist"}

    return user


def update(db: Session, pk: int, role: str, ip_check: UpdateUser):
    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin members can update user info"
        )

    user = db.query(User).filter(User.id == pk).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.ip_check = ip_check.ip_check
    db.commit()
    db.refresh(user)

    return {"message": "User updated successfully"}