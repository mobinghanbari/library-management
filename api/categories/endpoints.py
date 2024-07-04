from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database.models import Category
from sqlalchemy.exc import IntegrityError
from .schema.input_schema import InCategory


def create(category: InCategory, role, db: Session):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager members can add Category"
        )

    if category.parent_id is not None:
        # Check if parent_id exists
        parent = db.query(Category).filter(Category.id == category.parent_id).first()
        if parent is None:
            raise HTTPException(detail="Invalid parent_id, it does not exist.", status_code=status.HTTP_404_NOT_FOUND)

    new_category = Category(
        name=category.name,
        description=category.description,
        parent_id=category.parent_id
    )

    try:
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(detail="Category with this name already exists.", status_code=status.HTTP_400_BAD_REQUEST)

    return new_category


# Read
def get_category_by_id(category_id: int, db: Session):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(detail="The category does not exist", status_code=status.HTTP_404_NOT_FOUND)
    return category


def get_all_categories(db: Session):
    return db.query(Category).all()


# Update
def update_category(category_id: int, role, category_data: InCategory, db: Session):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager members can update Category"
        )

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(detail="Category not found.", status_code=status.HTTP_404_NOT_FOUND)

    if category_data.parent_id is not None:
        parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
        if parent is None:
            raise HTTPException(detail="Invalid parent_id, it does not exist.", status_code=status.HTTP_404_NOT_FOUND)

    category.name = category_data.name
    category.description = category_data.description
    category.parent_id = category_data.parent_id

    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(detail="Category with this name already exists.", status_code=status.HTTP_400_BAD_REQUEST)

    return category


# Delete
def delete_category(category_id: int, role, db: Session):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager members can delete Category"
        )
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(detail="Category not found.", status_code=status.HTTP_404_NOT_FOUND)

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully."}
