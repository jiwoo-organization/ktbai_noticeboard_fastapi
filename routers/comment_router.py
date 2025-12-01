from fastapi import APIRouter, Body, Query, Depends
from sqlalchemy.orm import Session
from database import get_db
from controllers import comment_controller
from models.comment_model import CommentCreate

router = APIRouter(prefix="/posts", tags=["Comments"])

# 댓글 목록
@router.get("/{post_id}/comments")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return comment_controller.get_comments(db, post_id)


# 댓글 등록
@router.post("/{post_id}/comments")
def add_comment(
    post_id: int,
    data: CommentCreate = Body(...),
    db: Session = Depends(get_db)
):
    return comment_controller.add_comment(db, post_id, data)


# 댓글 수정
@router.put("/{post_id}/comments/{comment_id}")
def update_comment(
    post_id: int,
    comment_id: int,
    author: str = Query(...),          # 작성자 확인용
    data: dict = Body(...),            # { "content": "xxx" }
    db: Session = Depends(get_db)
):
    return comment_controller.update_comment(db, post_id, comment_id, author, data)


# 댓글 삭제
@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(
    post_id: int,
    comment_id: int,
    author: str = Query(None),
    db: Session = Depends(get_db)
):
    return comment_controller.delete_comment(db, post_id, comment_id, author)
