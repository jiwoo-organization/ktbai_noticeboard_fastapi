from fastapi import APIRouter, UploadFile, File, Form, Body
from controllers import post_controller, comment_controller

router = APIRouter(prefix="/posts", tags=["Posts"])

# 게시글 CRUD

@router.get("")
def get_all_posts():
    """게시글 목록 조회"""
    return post_controller.get_all_posts()

@router.get("/{post_id}")
def get_post_detail(post_id: int):
    """게시글 상세 조회"""
    return post_controller.get_post_detail(post_id)

@router.post("")
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    author: str = Form("익명"),
    file: UploadFile | None = File(None)
):
    """게시글 추가"""
    return post_controller.create_post(title, content, author, file)

@router.put("/{post_id}")
def update_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    file: UploadFile | None = File(None)
):
    """게시글 수정"""
    return post_controller.update_post(post_id, title, content, file)

@router.delete("/{post_id}")
def delete_post(post_id: int):
    """게시글 삭제"""
    return post_controller.delete_post(post_id)

@router.post("/{post_id}/like")
def toggle_like(post_id: int):
    """좋아요 토글"""
    return post_controller.toggle_like(post_id)

# 댓글 CRUD


@router.get("/{post_id}/comments")
def get_comments(post_id: int):
    """댓글 목록"""
    return comment_controller.get_comments(post_id)

@router.post("/{post_id}/comments")
def add_comment(post_id: int, data: dict = Body(...)):
    """댓글 등록"""
    return comment_controller.add_comment(post_id, data)

@router.put("/{post_id}/comments/{comment_id}")
def update_comment(post_id: int, comment_id: int, data: dict = Body(...)):
    """댓글 수정"""
    return comment_controller.update_comment(post_id, comment_id, data)

@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(post_id: int, comment_id: int):
    """댓글 삭제"""
    return comment_controller.delete_comment(post_id, comment_id)
