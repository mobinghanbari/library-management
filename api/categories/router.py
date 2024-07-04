from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from database.connection import get_db
from sqlalchemy.orm import Session
from auth.ouath2 import get_current_user
from database.models import Category, User
from .schema.input_schema import InCategory
from .schema.output_schema import OuCategory
from .endpoints import create, get_all_categories, get_category_by_id, update_category, \
    delete_category
from ..users.utils import validate_token
from dependency.dependency import verify_ip


category_app = APIRouter(prefix="/categories", tags=["Category"])


@category_app.get("/list", response_model=List[OuCategory])
def get_all_category(db: Session = Depends(get_db)):
    return get_all_categories(db=db)


@category_app.get("/{pk}", response_model=OuCategory)
def get_category(pk, db: Session = Depends(get_db)):
    return get_category_by_id(category_id=pk, db=db)

@category_app.post("/create", response_model=OuCategory, dependencies=[Depends(verify_ip)])
def create_category(category: InCategory, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return create(category=category, role=current_user["role"], db=db)



@category_app.put("/update/{pk}", response_model=OuCategory, dependencies=[Depends(verify_ip)])
def update_category_by_id(pk, data: InCategory, db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return update_category(category_id=pk, category_data=data, role=current_user["role"], db=db)


@category_app.delete("/delete/{pk}", dependencies=[Depends(verify_ip)])
def delete_category_by_id(pk, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return delete_category(category_id=pk, role=current_user["role"], db=db)
