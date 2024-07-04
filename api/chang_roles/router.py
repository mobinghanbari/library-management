from fastapi import APIRouter, Depends
from auth.ouath2 import get_current_user
from database.models import User
from .schema.input_schema import UpdateUserRole
from sqlalchemy.orm import Session
from database.connection import get_db
from .endpoints import update


change_role_app = APIRouter(prefix="/change-roles", tags=["Change Role"])

@change_role_app.patch("/change/{pk}")
def change_role(pk: int, new_role: UpdateUserRole, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update(pk=pk, role=current_user["role"], new_role=new_role, db=db)