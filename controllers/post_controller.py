from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Set
import os

from models.post_model import PostORM, Post, PostCreate, PostUpdate
from models.comment_model import CommentCreate
from controllers.ai_controller import generate_comment
from models.ai_model import CommentGenRequest
from controllers.comment_controller import add_comment

from sqlalchemy.exc import IntegrityError
from models.comment_model import CommentORM


UPLOAD_DIR = "uploads"
liked_posts: Set[int] = set()


def _format_number(n: int) -> str:
    if n >= 100_000:
        return f"{n // 1000}k"
    elif n >= 10_000:
        return f"{n // 1000}k"
    elif n >= 1_000:
        return f"{n // 1000}k"
    return str(n)


def _get_post(db: Session, post_id: int) -> PostORM:
    post = db.query(PostORM).filter(PostORM.id == post_id).first()
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")
    return post


# -------------------------------
# 게시글 목록
# -------------------------------
def get_all_posts(db: Session):
    posts = db.query(PostORM).order_by(PostORM.id.desc()).all()

    formatted_posts = []
    for p in posts:
        post_schema = Post.from_orm(p).dict()
        formatted_posts.append(
            {
                **post_schema,
                "views_display": _format_number(p.views),
                "likes_display": _format_number(p.likes),
                "is_liked": p.id in liked_posts,
            }
        )
    return {"count": len(formatted_posts), "posts": formatted_posts}


# -------------------------------
# 게시글 상세
# -------------------------------
def get_post_detail(db: Session, post_id: int):
    post = _get_post(db, post_id)

    # 조회수 증가
    post.views += 1
    db.commit()
    db.refresh(post)

    post_schema = Post.from_orm(post).dict()
    return {
        **post_schema,
        "views_display": _format_number(post.views),
        "likes_display": _format_number(post.likes),
        "is_liked": post_id in liked_posts,
    }


# -------------------------------
# 게시글 생성 (+AI 자동 댓글)
# -------------------------------
def create_post(db: Session, data: PostCreate, file: UploadFile | None = None):
    title = data.title.strip()
    content = data.content.strip()

    if not title or not content:
        raise HTTPException(400, "제목과 내용을 모두 입력해주세요.")
    if len(title) > 26:
        raise HTTPException(400, "제목은 최대 26자까지만 작성 가능합니다.")

    # 이미지 저장
    image_url = None
    if file:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"post_{int(datetime.now().timestamp())}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        image_url = f"/{file_path}"

    # DB 저장
    new_post = PostORM(
        title=title,
        content=content,
        author=data.author or "익명",
        image=image_url,
        views=0,
        likes=0,
        created_at=datetime.now(),
        updated_at=None,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # AI 댓글 생성
    ai_request = CommentGenRequest(
        post_title=new_post.title,
        post_content=new_post.content,
    )

    ai_comment_text = generate_comment(ai_request)["comment"]

    ai_comment = CommentCreate(author="AI Bot", content=ai_comment_text)
    add_comment(db, new_post.id, ai_comment)

    return {
        "message": "게시글이 등록되었습니다.",
        "post": Post.from_orm(new_post),
        "ai_comment": ai_comment_text,
    }


# -------------------------------
# 게시글 수정 (작성자 본인만 가능)
# -------------------------------
def update_post(db: Session, post_id: int, data: PostUpdate, file: UploadFile | None, user):
    post = _get_post(db, post_id)

    # 🔥 작성자 체크 추가
    if post.author != user.nickname:
        raise HTTPException(403, "본인이 작성한 게시글만 수정할 수 있습니다.")

    new_title = data.title.strip() if data.title else post.title
    new_content = data.content.strip() if data.content else post.content

    if len(new_title) > 26:
        raise HTTPException(400, "제목은 최대 26자까지만 작성 가능합니다.")

    post.title = new_title
    post.content = new_content
    post.updated_at = datetime.now()

    # 파일 업로드 처리
    if file:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"post_{post_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        post.image = f"/{file_path}"

    db.commit()
    db.refresh(post)

    return {"message": "게시글이 수정되었습니다.", "post": Post.from_orm(post)}


# -------------------------------
# 게시글 삭제 (작성자 본인만 가능)
# -------------------------------
def delete_post(db: Session, post_id: int, user):
    post = _get_post(db, post_id)

    # 🔥 작성자 체크 추가
    if post.author != user.nickname:
        raise HTTPException(403, "본인이 작성한 게시글만 삭제할 수 있습니다.")

    try:
        # 댓글 삭제 후 게시글 삭제
        db.query(CommentORM).filter(CommentORM.post_id == post_id).delete()
        db.delete(post)
        db.commit()
        return {"message": "게시글이 삭제되었습니다."}

    except Exception:
        db.rollback()
        raise HTTPException(500, "게시글 삭제 중 오류가 발생했습니다.")


# -------------------------------
# 좋아요 토글
# -------------------------------
def toggle_like(db: Session, post_id: int):
    post = _get_post(db, post_id)

    if post_id in liked_posts:
        liked_posts.remove(post_id)
        post.likes = max(0, post.likes - 1)
        message = "좋아요 취소됨"
        is_liked = False
    else:
        liked_posts.add(post_id)
        post.likes += 1
        message = "좋아요 추가됨"
        is_liked = True

    db.commit()
    db.refresh(post)

    return {
        "message": message,
        "likes": post.likes,
        "is_liked": is_liked,
    }
