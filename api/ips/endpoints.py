from sqlalchemy.orm import Session
from database.models import Ip, User
from .schema.input_schema import InIp
from fastapi import HTTPException, status


def create(ip: InIp, role, db: Session):
    if role not in ["admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin members can add IP"
        )

    # Check if user exist
    user = db.query(User).filter(User.id == ip.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    new_ip = Ip(user_id=ip.user_id, ip_address=ip.ip_address)
    db.add(new_ip)
    db.commit()
    db.refresh(new_ip)

    return new_ip


def get_all(role, db: Session):
    if role not in ["admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin members can see IPs"
        )
    ips = db.query(Ip).all()
    return ips


def remove(pk, role, db: Session):
    if role not in ["admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin members can delete IPs"
        )

    ip = db.query(Ip).where(Ip.id == pk).first()
    # Check if ip exist
    if not ip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ip not found"
        )
    db.delete(ip)
    db.commit()

    return {"message": "The ip has deleted successfully"}
