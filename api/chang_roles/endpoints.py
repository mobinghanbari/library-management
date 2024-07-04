from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import User, Role
from .schema.input_schema import UpdateUserRole


def update(pk, role, new_role: UpdateUserRole, db: Session):
    if role not in ["admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin members can change User Role"
        )

    user = db.query(User).where(User.id == pk).first()
    # Check if user exist
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    role = db.query(Role).where(Role.slug == new_role.role).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    user.role_id = role.id
    db.commit()
    db.refresh(user)  # Refresh the user instance to reflect the changes

    return {"message": f"The role of {user.username} has been changed to {role.slug}"}

