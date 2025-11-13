# controllers/user_controller.py
from fastapi import HTTPException
import re

users = [
    {"id": 1, "name": "Alice", "nickname": "jeju_lover", "email": "alice@test.com", "password": "abcd1234!"},
    {"id": 2, "name": "Bob", "nickname": "foodie_bob", "email": "bob@test.com", "password": "password1234!"},
    {"id": 3, "name": "Carol", "nickname": "traveler_carol", "email": "carol@test.com", "password": "hello5678!"},
]

# 유효성 검증 함수들
def _is_valid_email(email: str, users: list = None):
    if not email or not email.strip():
        raise HTTPException(status_code=400, detail="이메일을 입력해주세요")

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if len(email) < 6 or not re.match(pattern, email):
        raise HTTPException(status_code=400, detail="올바른 형식으로 입력해주세요 (예: example@example.com)")

    if users and any(u["email"] == email for u in users):
        raise HTTPException(status_code=409, detail="중복된 이메일입니다")

    return {"message": "사용 가능한 이메일입니다."}


def _is_valid_password(password: str) -> bool:
    # 입력 여부
    if not password or not password.strip():
        raise HTTPException(status_code=400, detail="비밀번호를 입력해주세요.")
    # 길이 검사
    if 8 > len(password) > 20:
        raise HTTPException(status_code=400, detail="비밀번호는 8자 이상 20자 이하로 써주세요")
    # 유효성
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$"
    if not re.match(pattern, password):
        raise HTTPException(status_code=400, detail="비밀번호는 대문자, 소문자, 특수문, 숫자를 하나씩 포함해야합니다")
    return bool(re.match(pattern, password))

def _is_valid_nickname(nickname: str, users: list = None):
    if not nickname or not nickname.strip():
        raise HTTPException(status_code=400, detail="닉네임을 입력해주세요.")

    if " " in nickname:
        raise HTTPException(status_code=400, detail="띄어쓰기를 없애주세요.")

    if len(nickname) > 10:
        raise HTTPException(status_code=400, detail="닉네임은 최대 10자까지 작성 가능합니다.")

    # 중복 검사 (users가 있을 때만)
    if users and any(u["nickname"] == nickname for u in users):
        raise HTTPException(status_code=409, detail="중복된 닉네임입니다.")

    return True


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
    email = data.get("email")
    password = data.get("password")
    password_confirm = data.get("password_confirm")  # ✅ 추가
    nickname = data.get("nickname")

    # 이메일 검증
    if not email or not _is_valid_email(email):
        raise HTTPException(400, "올바른 이메일 주소 형식을 입력해주세요.")
    if any(u["email"] == email for u in users):
        raise HTTPException(409, "중복된 이메일입니다.")

    # 비밀번호 검증
    if not _is_valid_password(password):
        raise HTTPException(400, "비밀번호는 대소문자/숫자/특수문자를 포함해야 합니다.")
    if password != password_confirm:
        raise HTTPException(400, "비밀번호가 일치하지 않습니다.")  # ✅ 추가

    # 닉네임 검증
    if not _is_valid_nickname(nickname):
        raise HTTPException(400, "닉네임은 1~10자 이내여야 합니다.")

    # 유저 생성
    new_user = {
        "id": len(users) + 1,
        "email": email,
        "password": password,
        "nickname": nickname
    }
    users.append(new_user)

    return {"id": new_user["id"], "email": email, "nickname": nickname}


# 프로필 수정
def update_profile(user_id: int, data: dict):
    user = next((u for u in users if u["id"] == user_id), None)
    nickname = data.get("nickname")
    if not nickname or not nickname.strip():
        raise HTTPException(status_code=400, detail="닉네임을 입력해주세요.")
    if nickname and not _is_valid_nickname(nickname):
        raise HTTPException(400, "닉네임은 1~10자 이내여야 합니다.")
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다.")

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
    _is_valid_password(new_pw)
    if old_pw == new_pw:
        raise HTTPException(400, "이전 비밀번호와 동일한 비밀번호는 사용할 수 없습니다.")
    user["password"] = new_pw
    return {"message": "비밀번호가 변경되었습니다."}