# routers/user_router.py
from fastapi import APIRouter, Body
from controllers import user_controller

router = APIRouter(prefix="/users")

# 로그인
@router.post("/login")
def login(data: dict = Body(...)):
    return user_controller.login(data)

# 회원가입
@router.post("/register")
def register(data: dict = Body(...)):
    return user_controller.register(data)

# 회원정보 수정 (닉네임 등)
@router.put("/{user_id}/profile")
def update_profile(user_id: int, data: dict = Body(...)):
    return user_controller.update_profile(user_id, data)

# 비밀번호 수정
@router.put("/{user_id}/password")
def update_password(user_id: int, data: dict = Body(...)):
    return user_controller.update_password(user_id, data)