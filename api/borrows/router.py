from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, Query
from database.connection import get_db
from sqlalchemy.orm import Session
from auth.ouath2 import get_current_user
from .schema.input_schema import InBorrow
from .schema.output_schema import OuBorrow, User
from .endpoints import create, get_all, update
from ..users.utils import validate_token
from dependency.dependency import verify_ip



borrow_app = APIRouter(prefix="/borrows", tags=["Borrow"])


@borrow_app.post("/assign", response_model=OuBorrow, dependencies=[Depends(verify_ip)])
def assign_borrow(data: InBorrow, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return create(borrow=data, role=current_user["role"], db=db, current_user=current_user)


@borrow_app.get("/list", response_model=List[OuBorrow], dependencies=[Depends(verify_ip)])
def get_all_borrows(db:Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return get_all(db=db, role=current_user["role"])


@borrow_app.patch("/extension", response_model=OuBorrow, dependencies=[Depends(verify_ip)])
def extension_specefic_borrow(pk:int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return update(pk=pk, db=db, role=current_user["role"])