# controllers/user_controller.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.user_model import UserORM
import re

from auth_utils import create_access_token


# ---------------------------
# 유효성 검증 함수들
# ---------------------------
def _is_valid_email(db: Session, email: str, exclude_user_id: int | None = None):
    if not email or not email.strip():
        raise HTTPException(400, "이메일을 입력해주세요.")

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if len(email) < 6 or not re.match(pattern, email):
        raise HTTPException(400, "올바른 형식으로 입력해주세요 (예: example@example.com)")

    query = db.query(UserORM).filter(UserORM.email == email)
    if exclude_user_id:
        query = query.filter(UserORM.id != exclude_user_id)

    if query.first():
        raise HTTPException(409, "중복된 이메일입니다.")

    return True


def _is_valid_password(password: str) -> bool:
    if not password or not password.strip():
        raise HTTPException(400, "비밀번호를 입력해주세요.")

    if not (8 <= len(password) <= 20):
        raise HTTPException(400, "비밀번호는 8자 이상 20자 이하로 써주세요.")

    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$"
    if not re.match(pattern, password):
        raise HTTPException(400, "비밀번호는 대문자, 소문자, 특수문자, 숫자를 하나씩 포함해야 합니다.")

    return True


def _is_valid_nickname(db: Session, nickname: str, exclude_user_id: int | None = None):
    if not nickname or not nickname.strip():
        raise HTTPException(400, "닉네임을 입력해주세요.")

    if " " in nickname:
        raise HTTPException(400, "띄어쓰기를 없애주세요.")

    if len(nickname) > 10:
        raise HTTPException(400, "닉네임은 최대 10자까지 작성 가능합니다.")

    query = db.query(UserORM).filter(UserORM.nickname == nickname)
    if exclude_user_id:
        query = query.filter(UserORM.id != exclude_user_id)

    if query.first():
        raise HTTPException(409, "중복된 닉네임입니다.")

    return True


# ---------------------------
# 로그인 (JWT 발급)
# ---------------------------
def login(db: Session, data: dict):
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise HTTPException(400, "이메일과 비밀번호를 입력해주세요.")

    user = (
        db.query(UserORM)
        .filter(UserORM.email == email, UserORM.password == password)
        .first()
    )
    if not user:
        raise HTTPException(401, "아이디 또는 비밀번호를 확인해주세요.")

    # 여기서 JWT 발급
    access_token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
        },
    }


# ---------------------------
# 회원가입
# ---------------------------
def register(db: Session, data: dict):
    email = data.get("email")
    password = data.get("password")
    password_confirm = data.get("password_confirm")
    nickname = data.get("nickname")

    _is_valid_email(db, email)
    _is_valid_password(password)
    if password != password_confirm:
        raise HTTPException(400, "비밀번호가 일치하지 않습니다.")
    _is_valid_nickname(db, nickname)

    new_user = UserORM(
        name=nickname,
        nickname=nickname,
        email=email,
        password=password,  # 실제 서비스라면 해시 필요
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "회원가입이 완료되었습니다.",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "nickname": new_user.nickname,
        },
    }


# ---------------------------
# 프로필 수정
# ---------------------------
def update_profile(db: Session, user_id: int, data: dict):
    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다.")

    nickname = data.get("nickname")
    if not nickname or not nickname.strip():
        raise HTTPException(400, "닉네임을 입력해주세요.")

    _is_valid_nickname(db, nickname, exclude_user_id=user_id)

    user.nickname = nickname
    db.commit()
    db.refresh(user)

    return {"message": "프로필 수정이 완료되었습니다.", "nickname": user.nickname}


# ---------------------------
# 비밀번호 수정
# ---------------------------
def update_password(db: Session, user_id: int, data: dict):
    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다.")

    old_pw = data.get("old_password")
    new_pw = data.get("new_password")

    if not old_pw or not new_pw:
        raise HTTPException(400, "비밀번호를 입력해주세요.")

    if user.password != old_pw:
        raise HTTPException(401, "현재 비밀번호가 일치하지 않습니다.")

    _is_valid_password(new_pw)

    if old_pw == new_pw:
        raise HTTPException(400, "이전 비밀번호와 동일한 비밀번호는 사용할 수 없습니다.")

    user.password = new_pw
    db.commit()
    db.refresh(user)

    return {"message": "비밀번호가 변경되었습니다."}
