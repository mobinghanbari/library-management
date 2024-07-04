from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User
from auth.ouath2 import get_current_user
from .schema.input_schema import InIp
from .endpoints import create, get_all, remove
from .schema.output_schema import OuIp
from ..users.utils import validate_token

ip_app = APIRouter(prefix="/ips", tags=["Ip"])


@ip_app.get("/list", response_model=List[OuIp])
def list_ips(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return get_all(role=current_user["role"], db=db)


@ip_app.post("/create", response_model=OuIp)
def add_ip(data: InIp, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return create(ip=data, role=current_user["role"], db=db)


@ip_app.delete("/delete/{pk}")
def delete_ip(pk, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return remove(pk=pk, role=current_user["role"], db=db)
