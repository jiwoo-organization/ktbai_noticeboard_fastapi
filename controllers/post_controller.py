from fastapi import HTTPException, UploadFile
from datetime import datetime
from models.post_model import Post, PostCreate, PostUpdate, posts, liked_posts
import os

from controllers.ai_controller import generate_comment
from models.ai_model import CommentGenRequest
from controllers.comment_controller import add_comment
from models.comment_model import CommentCreate
# 기본 설정
UPLOAD_DIR = "uploads"

# 유틸 함수
def _get_post(post_id: int) -> dict:
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")
    return post

def _next_post_id() -> int:
    return max([p["id"] for p in posts], default=0) + 1

def _format_number(n: int) -> str:
    if n >= 100_000:
        return f"{n // 1000}k"
    elif n >= 10_000:
        return f"{n // 1000}k"
    elif n >= 1_000:
        return f"{n // 1000}k"
    return str(n)

# 게시글 CRUD
def get_all_posts():
    """게시글 목록"""
    formatted_posts = []
    for p in posts:
        formatted_posts.append(
            {
                **p,
                "views_display": _format_number(p["views"]),
                "likes_display": _format_number(p["likes"]),
                "is_liked": p["id"] in liked_posts,
            }
        )
    return {"count": len(posts), "posts": formatted_posts}


def get_post_detail(post_id: int):
    """게시글 상세"""
    post = _get_post(post_id)
    post["views"] += 1  # 조회수 증가

    return {
        **post,
        "views_display": _format_number(post["views"]),
        "likes_display": _format_number(post["likes"]),
        "is_liked": post_id in liked_posts,
    }


def create_post(data: PostCreate, file: UploadFile | None = None):
    """게시글 생성"""
    title = data.title.strip()
    content = data.content.strip()

    if not title or not content:
        raise HTTPException(400, "제목과 내용을 모두 입력해주세요.")
    if len(title) > 26:
        raise HTTPException(400, "제목은 최대 26자까지만 작성 가능합니다.")

    image_url = None
    if file:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"post_{_next_post_id()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        image_url = f"/{file_path}"

    new_post = Post(
        id=_next_post_id(),
        title=title,
        content=content,
        author=data.author or "익명",
        image=image_url,
        views=0,
        likes=0,
        created_at=datetime.now(),
        updated_at=None,
    )
    posts.append(new_post.dict())

    # 1) AI 모델 요청 형식 만들기
    ai_request = CommentGenRequest(
        post_title=new_post.title,
        post_content=new_post.content
    )

    # 2) 로컬 AI 모델로 댓글 생성
    ai_comment_text = generate_comment(ai_request)["comment"]

    # 3) 댓글 등록
    ai_comment = CommentCreate(
        author="AI Bot",
        content=ai_comment_text
    )
    add_comment(new_post.id, ai_comment)
    return {"message": "게시글이 등록되었습니다.", "post": new_post, "ai_comment": ai_comment_text}


def update_post(post_id: int, data: PostUpdate, file: UploadFile | None = None):
    """게시글 수정"""
    post = _get_post(post_id)

    new_title = data.title.strip() if data.title else post["title"]
    new_content = data.content.strip() if data.content else post["content"]

    if len(new_title) > 26:
        raise HTTPException(400, "제목은 최대 26자까지만 작성 가능합니다.")

    post["title"] = new_title
    post["content"] = new_content
    post["updated_at"] = datetime.now()

    if file:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"post_{post_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        post["image"] = f"/{file_path}"

    return {"message": "게시글이 수정되었습니다.", "post": Post(**post)}


def delete_post(post_id: int):
    """게시글 삭제"""
    global posts
    before = len(posts)
    posts = [p for p in posts if p["id"] != post_id]
    if len(posts) == before:
        raise HTTPException(404, "삭제할 게시글이 없습니다.")
    return {"message": "게시글이 삭제되었습니다."}


def toggle_like(post_id: int):
    """좋아요 토글"""
    post = _get_post(post_id)

    if post_id in liked_posts:
        liked_posts.remove(post_id)
        post["likes"] = max(0, post["likes"] - 1)
        return {"message": "좋아요 취소됨", "likes": post["likes"], "is_liked": False}
    else:
        liked_posts.add(post_id)
        post["likes"] += 1
        return {"message": "좋아요 추가됨", "likes": post["likes"], "is_liked": True}
