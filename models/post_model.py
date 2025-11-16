# models/post_model.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Set

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

class Post(PostBase):
    id: int
    image: Optional[str] = None
    views: int = 0
    likes: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# ---------------------------
# Dummy Data
# ---------------------------
posts: List[dict] = [
    {
        "id": 1,
        "title": "오늘의 제주 날씨",
        "content": "함덕 해수욕장 정말 맑아요!",
        "author": "jeju_lover",
        "image": None,
        "views": 120,
        "likes": 4,
        "created_at": "2025-11-12 10:00:00",
        "updated_at": None,
    },
    {
        "id": 2,
        "title": "카페 추천 부탁드려요 ☕️",
        "content": "애월 근처 분위기 좋은 곳 있을까요?",
        "author": "coffee_holic",
        "image": None,
        "views": 89,
        "likes": 2,
        "created_at": "2025-11-13 09:12:00",
        "updated_at": None,
    },
]

liked_posts: Set[int] = set()
