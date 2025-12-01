# routers/ai_router.py
from fastapi import APIRouter
from models.ai_model import CommentGenRequest
from controllers.ai_controller import generate_comment

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/generate-comment")
def generate_comment_route(data: CommentGenRequest):
    return generate_comment(data)
