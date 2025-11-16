# models/comment_model.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class CommentBase(BaseModel):
    author: str = Field(default="익명")
    content: str = Field(..., min_length=1)

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    author: Optional[str] = None
    content: Optional[str] = None

class Comment(CommentBase):
    id: int
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# ---------------------------
# Dummy Data
# ---------------------------
comments: List[dict] = [
    {"id": 1, "post_id": 1, "author": "Bob", "content": "좋은 글이에요!", "created_at": "2025-11-11 12:00:00"},
    {"id": 2, "post_id": 1, "author": "Carol", "content": "함덕 사진 올려주세요!", "created_at": "2025-11-12 14:20:00"},
]
