# routers/comment_router.py
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from database import get_db
from controllers import comment_controller
from models.comment_model import CommentCreate
from auth_utils import get_current_user
from models.user_model import UserORM

router = APIRouter(prefix="/posts", tags=["Comments"])


# 댓글 목록 (로그인 불필요)
@router.get("/{post_id}/comments")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return comment_controller.get_comments(db, post_id)


# 댓글 등록 (로그인 필요)
@router.post("/{post_id}/comments")
def add_comment(
    post_id: int,
    data: CommentCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    return comment_controller.add_comment(db, post_id, data, current_user)


# 댓글 수정
@router.put("/{post_id}/comments/{comment_id}")
def update_comment(
    post_id: int,
    comment_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    return comment_controller.update_comment(db, post_id, comment_id, current_user, data)


# 댓글 삭제
@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    return comment_controller.delete_comment(db, post_id, comment_id, current_user)
