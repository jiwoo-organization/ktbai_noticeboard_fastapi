# models/post_model.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base
from pydantic import BaseModel, Field
from typing import Optional

# ------------------------------
# SQLAlchemy ORM 모델
# ------------------------------
class PostORM(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(26), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(50), default="익명")
    image = Column(String(255), nullable=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)


# ------------------------------
# Pydantic 스키마 (입력/출력용)
# ------------------------------
class PostBase(BaseModel):
    title: str = Field(..., max_length=26)
    content: str
    author: str = "익명"

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None

class Post(BaseModel):
    id: int
    title: str
    content: str
    author: str
    image: Optional[str]
    views: int
    likes: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
