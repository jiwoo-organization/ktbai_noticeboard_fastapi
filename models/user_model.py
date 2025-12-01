# models/user_model.py
from sqlalchemy import Column, Integer, String
from database import Base
from pydantic import BaseModel, Field, EmailStr

# ---------------------------
# SQLAlchemy ORM Model
# ---------------------------
class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    nickname = Column(String(20), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)


# ---------------------------
# Pydantic Models
# ---------------------------
class UserBase(BaseModel):
    name: str
    nickname: str
    email: EmailStr

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=20)
    password_confirm: str
    nickname: str = Field(..., max_length=10)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdateProfile(BaseModel):
    nickname: str = Field(..., max_length=10)

class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True
