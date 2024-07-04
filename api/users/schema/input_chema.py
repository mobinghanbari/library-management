from pydantic import BaseModel, EmailStr, validator
from typing import List
import re


class UserIn(BaseModel):
    username: str
    email: EmailStr
    phone: str
    password: str

    @validator('username')
    def validate_username(cls, v):
        if not re.match("^[a-zA-Z0-9_.-]+$", v):
            raise ValueError('Username must contain only letters, numbers, underscores, periods, and hyphens.')
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters long.')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if not re.match("^\d{11}$", v):
            raise ValueError('Phone number must be exactly 11 digits.')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        return v


class UserResetPassword(BaseModel):
    email: EmailStr


class ChangePassword(BaseModel):
    password: str
    confirm: str

    @validator('confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match.')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        return v


class UpdateUser(BaseModel):
    ip_check: bool

    @validator('ip_check')
    def validate_ip_check(cls, v):
        if not isinstance(v, bool):
            raise ValueError('ip_check must be a boolean.')
        return v