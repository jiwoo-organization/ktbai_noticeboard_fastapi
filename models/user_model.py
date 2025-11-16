# models/user_model.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

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
        orm_mode = True

# ---------------------------
# Dummy Data (DB Simulation)
# ---------------------------
users: List[dict] = [
    {"id": 1, "name": "Alice", "nickname": "jeju_lover", "email": "alice@test.com", "password": "Abcd1234!"},
    {"id": 2, "name": "Bob", "nickname": "foodie_bob", "email": "bob@test.com", "password": "Password123!"},
    {"id": 3, "name": "Carol", "nickname": "traveler_carol", "email": "carol@test.com", "password": "Hello5678!"},
    {"id": 4, "name": "Dave", "nickname": "surf_dave", "email": "dave@test.com", "password": "Surf1234!"},
]
