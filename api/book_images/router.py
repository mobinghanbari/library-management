import os
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.ouath2 import get_current_user
from database.models import BookImage, User
from database.connection import get_db
from .endpoints import create, delete_image
from .schema.output_schema import OuBookImage
from ..users.utils import validate_token
from dependency.dependency import verify_ip


book_image_app = APIRouter(prefix="/images", tags=["Book Image"])


@book_image_app.post("/upload/{book_id}", response_model=OuBookImage, dependencies=[Depends(verify_ip)])
async def upload_file(book_id: int, file: UploadFile = File(...), db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return create(pk=book_id, file=file, role=current_user["role"], db=db)


@book_image_app.delete("/delete/{image_id}", dependencies=[Depends(verify_ip)])
async def delete_image_by_id(image_id, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return delete_image(pk=image_id, role=current_user["role"], db=db)
