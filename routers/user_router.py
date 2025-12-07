# routers/user_router.py
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from controllers import user_controller
from database import get_db
from auth_utils import get_current_user
from models.user_model import UserORM

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/login")
def login(data: dict = Body(...), db: Session = Depends(get_db)):
    return user_controller.login(db, data)


@router.post("/register")
def register(data: dict = Body(...), db: Session = Depends(get_db)):
    return user_controller.register(db, data)


@router.put("/me/profile")
def update_profile(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    return user_controller.update_profile(db, current_user.id, data)


@router.put("/me/password")
def update_password(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    return user_controller.update_password(db, current_user.id, data)
