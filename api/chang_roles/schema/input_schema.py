from pydantic import BaseModel
from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    manager = "manager"
    user = "user"


class UpdateUserRole(BaseModel):
    role: RoleEnum
