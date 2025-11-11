# controllers/user_controller.py
from fastapi import HTTPException
import re

users = [
    {"id": 1, "name": "Alice", "email": "alice@test.com", "password": "abcdef1234!", "profile_img": "img1"},
    {"id": 2, "name": "Bob", "email": "bob@test.com", "password": "abcdef1234!", "profile_img": "img2"},
    {"id": 3, "name": "Carol", "email": "carol@test.com", "password": "abcdef1234!", "profile_img": "img3"}
]

# 유효성 검증 함수들
def _is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def _is_valid_password(password: str) -> bool:
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$"
    return bool(re.match(pattern, password))

def _is_valid_nickname(nickname: str) -> bool:
    return 1 <= len(nickname) <= 10 and not nickname.isspace()

# 로그인
def login(data: dict):
    email, password = data.get("email"), data.get("password")
    if not email or not password:
        raise HTTPException(400, "이메일과 비밀번호를 입력해주세요.")
    user = next((u for u in users if u["email"] == email and u["password"] == password), None)
    if not user:
        raise HTTPException(401, "아이디 또는 비밀번호를 확인해주세요.")
    return {"message": f"{user['name']}님 환영합니다."}

# 회원가입
def register(data: dict):
    email, password, nickname = data.get("email"), data.get("password"), data.get("nickname")

    if not email or not _is_valid_email(email):
        raise HTTPException(400, "올바른 이메일 주소 형식을 입력해주세요.")
    if any(u["email"] == email for u in users):
        raise HTTPException(409, "중복된 이메일입니다.")
    if not _is_valid_password(password):
        raise HTTPException(400, "비밀번호는 대소문자/숫자/특수문자를 포함해야 합니다.")
    if not _is_valid_nickname(nickname):
        raise HTTPException(400, "닉네임은 1~10자 이내여야 합니다.")

    new_user = {"id": len(users)+1, "email": email, "password": password, "nickname": nickname}
    users.append(new_user)
    return {"id": new_user["id"], "email": email, "nickname": nickname}

# 프로필 수정
def update_profile(user_id: int, data: dict):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다.")
    nickname = data.get("nickname")
    if nickname and not _is_valid_nickname(nickname):
        raise HTTPException(400, "닉네임은 1~10자 이내여야 합니다.")
    user["nickname"] = nickname or user["nickname"]
    return {"message": "프로필 수정이 완료되었습니다.", "nickname": user["nickname"]}

# 비밀번호 수정
def update_password(user_id: int, data: dict):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다.")
    old_pw, new_pw = data.get("old_password"), data.get("new_password")
    if not old_pw or not new_pw:
        raise HTTPException(400, "비밀번호를 입력해주세요.")
    if user["password"] != old_pw:
        raise HTTPException(401, "현재 비밀번호가 일치하지 않습니다.")
    if not _is_valid_password(new_pw):
        raise HTTPException(400, "새 비밀번호가 형식에 맞지 않습니다.")
    user["password"] = new_pw
    return {"message": "비밀번호가 변경되었습니다."}