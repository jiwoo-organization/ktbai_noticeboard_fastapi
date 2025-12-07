# routers/post_router.py
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from controllers import post_controller
from models.post_model import PostCreate, PostUpdate
from database import get_db
from auth_utils import get_current_user
from models.user_model import UserORM

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("")
def get_all_posts(db: Session = Depends(get_db)):
    return post_controller.get_all_posts(db)


@router.get("/{post_id}")
def get_post_detail(post_id: int, db: Session = Depends(get_db)):
    return post_controller.get_post_detail(db, post_id)


@router.post("")
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    data = PostCreate(title=title, content=content, author=current_user.nickname)
    return post_controller.create_post(db, data, file)


@router.put("/{post_id}")
def update_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    data = PostUpdate(title=title, content=content)
    return post_controller.update_post(db, post_id, data, file, current_user)


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    return post_controller.delete_post(db, post_id, current_user)


@router.post("/{post_id}/like")
def toggle_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    return post_controller.toggle_like(db, post_id)
