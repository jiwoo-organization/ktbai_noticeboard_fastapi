from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import UserORM

SECRET_KEY = "YOUR_SECRET_KEY_GENERATE_RANDOM"  # 나중에 .env로 이동 가능
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24시간

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


# JWT 생성 함수
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 현재 로그인된 유저 조회
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")

        if user_id is None:
            raise HTTPException(401, "토큰 정보가 올바르지 않습니다.")

    except JWTError:
        raise HTTPException(401, "유효하지 않은 토큰입니다.")

    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다.")

    return user
