from pydantic import BaseModel, EmailStr


class UserOu(BaseModel):
    username: str
    email: str
    phone: str
    is_activated: bool
    role_id: int

