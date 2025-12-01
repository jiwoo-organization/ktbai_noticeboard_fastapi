# controllers/post_controller.py
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

from models.post_model import PostORM
from models.comment_model import CommentORM

# 기본 설정
UPLOAD_DIR = "uploads"

# 좋아요 상태는 메모리에만 (누가 눌렀는지까지 DB에 안 남겨도 된다면)
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


# 게시글 CRUD
def get_all_posts(db: Session):
    """게시글 목록"""
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


def get_post_detail(db: Session, post_id: int):
    """게시글 상세"""
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


def create_post(db: Session, data: PostCreate, file: UploadFile | None = None):
    """게시글 생성 + AI 자동 댓글 생성"""
    title = data.title.strip()
    content = data.content.strip()

    if not title or not content:
        raise HTTPException(400, "제목과 내용을 모두 입력해주세요.")
    if len(title) > 26:
        raise HTTPException(400, "제목은 최대 26자까지만 작성 가능합니다.")

    image_url = None
    if file:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"post_{int(datetime.now().timestamp())}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        image_url = f"/{file_path}"

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

    # 1) AI 모델 요청 형식
    ai_request = CommentGenRequest(
        post_title=new_post.title,
        post_content=new_post.content,
    )

    # 2) 로컬 AI 모델로 댓글 생성
    ai_comment_text = generate_comment(ai_request)["comment"]

    # 3) 댓글 등록 (DB)
    ai_comment = CommentCreate(author="AI Bot", content=ai_comment_text)
    add_comment(db, new_post.id, ai_comment)

    return {
        "message": "게시글이 등록되었습니다.",
        "post": Post.from_orm(new_post),
        "ai_comment": ai_comment_text,
    }


def update_post(db: Session, post_id: int, data: PostUpdate, file: UploadFile | None = None):
    """게시글 수정"""
    post = _get_post(db, post_id)

    new_title = data.title.strip() if data.title else post.title
    new_content = data.content.strip() if data.content else post.content

    if len(new_title) > 26:
        raise HTTPException(400, "제목은 최대 26자까지만 작성 가능합니다.")

    post.title = new_title
    post.content = new_content
    post.updated_at = datetime.now()

    if file:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"post_{post_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        post.image = f"/{file_path}"

    db.commit()
    db.refresh(post)

    return {
        "message": "게시글이 수정되었습니다.",
        "post": Post.from_orm(post),
    }


def delete_post(db: Session, post_id: int):
    """게시글 삭제 (연관 댓글 먼저 삭제)"""
    post = _get_post(db, post_id)

    try:
        # 1) 이 게시글에 달린 댓글 먼저 삭제
        db.query(CommentORM).filter(CommentORM.post_id == post_id).delete()

        # 2) 게시글 삭제
        db.delete(post)
        db.commit()

        return {"message": "게시글이 삭제되었습니다."}

    except IntegrityError:
        db.rollback()
        # 혹시라도 FK 때문에 또 오류 나면 500 대신 400/409로 예쁘게 응답
        raise HTTPException(
            status_code=409,
            detail="댓글이 남아 있어 게시글을 삭제할 수 없습니다."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"게시글 삭제 중 오류: {e}")



def toggle_like(db: Session, post_id: int):
    """좋아요 토글"""
    post = _get_post(db, post_id)

    if post_id in liked_posts:
        liked_posts.remove(post_id)
        post.likes = max(0, post.likes - 1)
        is_liked = False
        message = "좋아요 취소됨"
    else:
        liked_posts.add(post_id)
        post.likes += 1
        is_liked = True
        message = "좋아요 추가됨"

    db.commit()
    db.refresh(post)

    return {
        "message": message,
        "likes": post.likes,
        "is_liked": is_liked,
    }
