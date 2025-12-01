from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from models.comment_model import CommentORM, Comment


# 댓글 목록 조회
def get_comments(db: Session, post_id: int):
    items = db.query(CommentORM).filter_by(post_id=post_id).all()
    return {"count": len(items), "comments": [Comment.model_validate(i, from_attributes=True) for i in items]}


# 댓글 생성
def add_comment(db: Session, post_id: int, data):
    new_comment = CommentORM(
        post_id=post_id,
        author=data.author,
        content=data.content
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return {
        "message": "댓글이 등록되었습니다.",
        "comment": Comment.model_validate(new_comment, from_attributes=True)
    }


# 댓글 수정
def update_comment(db: Session, post_id: int, comment_id: int, author: str, data: dict):

    # 댓글 가져오기
    comment = (
        db.query(CommentORM)
        .filter_by(id=comment_id, post_id=post_id)
        .first()
    )

    if not comment:
        raise HTTPException(404, "댓글을 찾을 수 없습니다.")

    # 작성자 검증
    if comment.author != author:
        raise HTTPException(403, "작성자만 댓글을 수정할 수 있습니다.")

    # content 검증
    new_content = data.get("content")
    if not new_content or not new_content.strip():
        raise HTTPException(400, "수정할 댓글 내용을 입력해주세요.")

    # 업데이트
    comment.content = new_content.strip()
    comment.updated_at = datetime.now()

    db.commit()
    db.refresh(comment)

    return {
        "message": "댓글이 수정되었습니다.",
        "comment": Comment.model_validate(comment, from_attributes=True)
    }


# 댓글 삭제
def delete_comment(db: Session, post_id: int, comment_id: int, author: str | None):
    comment = (
        db.query(CommentORM)
        .filter_by(id=comment_id, post_id=post_id)
        .first()
    )

    if not comment:
        raise HTTPException(404, "댓글을 찾을 수 없습니다.")

    if author and author.strip() != comment.author:
        raise HTTPException(403, "작성자만 댓글을 삭제할 수 있습니다.")

    db.delete(comment)
    db.commit()

    return {"message": "댓글이 삭제되었습니다."}
