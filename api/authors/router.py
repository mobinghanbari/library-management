from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from database.connection import get_db
from sqlalchemy.orm import Session
from auth.ouath2 import get_current_user
from database.models import Category, User
from .schema.input_schema import InAuthor
from .schema.output_schema import OuAuthor
from .endpoints import create, get_all_authors, get_author_by_id, update_author, delete_author
from ..users.utils import validate_token
from dependency.dependency import verify_ip


author_app = APIRouter(prefix="/authors", tags=["Author"])


@author_app.get("/list", response_model=List[OuAuthor])
def get_all_author(db: Session = Depends(get_db)):
    return get_all_authors(db=db)


@author_app.get("/{pk}", response_model=OuAuthor)
def get_author(pk, db: Session = Depends(get_db)):
    return get_author_by_id(author_id=pk, db=db)


@author_app.post("/create", response_model=OuAuthor, dependencies=[Depends(verify_ip)])
def create_author(author: InAuthor, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return create(author=author, role=current_user["role"], db=db)


@author_app.put("/update/{pk}", response_model=OuAuthor, dependencies=[Depends(verify_ip)])
def update_author_by_id(pk, data: InAuthor, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return update_author(author_id=pk, author_data=data, role=current_user["role"], db=db)


@author_app.delete("/delete/{pk}", dependencies=[Depends(verify_ip)])
def delete_author_by_id(pk, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return delete_author(author_id=pk, role=current_user["role"], db=db)
