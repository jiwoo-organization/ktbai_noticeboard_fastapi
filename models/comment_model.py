# models/comment_model.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from database import Base
from pydantic import BaseModel
from typing import Optional

# ------------------------------
# SQLAlchemy ORM 모델
# ------------------------------
class CommentORM(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    author = Column(String(50), default="익명")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)

# ------------------------------
# Pydantic 스키마
# ------------------------------
class CommentCreate(BaseModel):
    author: str = "익명"
    content: str

class Comment(BaseModel):
    id: int
    post_id: int
    author: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
