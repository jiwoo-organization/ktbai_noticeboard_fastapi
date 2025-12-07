# controllers/comment_controller.py
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.comment_model import CommentORM, CommentCreate, Comment
from models.post_model import PostORM
from models.user_model import UserORM


# 댓글 목록
def get_comments(db: Session, post_id: int):
    post = db.query(PostORM).filter(PostORM.id == post_id).first()
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")

    comments = (
        db.query(CommentORM)
        .filter(CommentORM.post_id == post_id)
        .order_by(CommentORM.id.asc())
        .all()
    )

    return [Comment.from_orm(c) for c in comments]


# 댓글 등록 (로그인 유저 기준)
def add_comment(db: Session, post_id: int, data: CommentCreate, user: UserORM | None = None):
    post = db.query(PostORM).filter(PostORM.id == post_id).first()
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")

    # 🔥 user가 None이면(AI 댓글) → AI Bot으로 처리
    author_name = user.nickname if user else data.author

    new_comment = CommentORM(
        post_id=post_id,
        author=author_name,
        content=data.content,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return {
        "message": "댓글이 등록되었습니다.",
        "comment": Comment.from_orm(new_comment),
    }



# 댓글 수정 (작성자만 가능)
def update_comment(db: Session, post_id: int, comment_id: int, user: UserORM, data: dict):
    comment = (
        db.query(CommentORM)
        .filter(CommentORM.id == comment_id, CommentORM.post_id == post_id)
        .first()
    )
    if not comment:
        raise HTTPException(404, "댓글을 찾을 수 없습니다.")

    if comment.author != user.nickname:
        raise HTTPException(403, "본인이 작성한 댓글만 수정할 수 있습니다.")

    new_content = data.get("content")
    if not new_content or not new_content.strip():
        raise HTTPException(400, "내용을 입력해주세요.")

    comment.content = new_content
    db.commit()
    db.refresh(comment)

    return {"message": "댓글이 수정되었습니다.", "comment": Comment.from_orm(comment)}


# 댓글 삭제 (작성자만 가능)
def delete_comment(db: Session, post_id: int, comment_id: int, user: UserORM):
    comment = (
        db.query(CommentORM)
        .filter(CommentORM.id == comment_id, CommentORM.post_id == post_id)
        .first()
    )
    if not comment:
        raise HTTPException(404, "댓글을 찾을 수 없습니다.")

    if comment.author != user.nickname:
        raise HTTPException(403, "본인이 작성한 댓글만 삭제할 수 있습니다.")

    db.delete(comment)
    db.commit()

    return {"message": "댓글이 삭제되었습니다."}
