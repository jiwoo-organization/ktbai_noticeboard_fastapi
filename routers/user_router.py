# routers/user_router.py
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from controllers import user_controller
from database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

# 로그인
@router.post("/login")
def login(data: dict = Body(...), db: Session = Depends(get_db)):
    return user_controller.login(db, data)

# 회원가입
@router.post("/register")
def register(data: dict = Body(...), db: Session = Depends(get_db)):
    return user_controller.register(db, data)

# 회원정보 수정 (닉네임 등)
@router.put("/{user_id}/profile")
def update_profile(user_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    return user_controller.update_profile(db, user_id, data)

# 비밀번호 수정
@router.put("/{user_id}/password")
def update_password(user_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    return user_controller.update_password(db, user_id, data)
