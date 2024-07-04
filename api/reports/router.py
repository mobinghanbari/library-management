from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from auth.ouath2 import get_current_user
from .endpoints import fetch_books
from api.reports.schema.output_schema import ReportSchema
from database.models import Book, Borrow, User
from database.connection import get_db
from typing import Optional
from datetime import date

from ..users.utils import validate_token
from dependency.dependency import verify_ip


report_app = APIRouter(prefix="/reports", tags=["Report"])


@report_app.get("/report", response_model=None, dependencies=[Depends(verify_ip)])
def get_reports(
        category_id: Optional[int] = Query(None,
                                           description="Enter the category ID to filter and display books of that category."),
        user_id: Optional[str] = Query(None,
                                       description="Enter the user id to filter and display borrows by that user."),
        filter_date: Optional[date] = Query(None,
                                            description="Enter the date to filter and display borrows on that date."),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    validate_token(current_user)

    return fetch_books(
        db=db,
        role=current_user["role"],
        category_id=category_id,
        user_id=user_id,
        filter_date=filter_date
    )
