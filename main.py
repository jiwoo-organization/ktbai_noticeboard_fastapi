# main.py
from fastapi import FastAPI
from database import Base, engine
from routers.post_router import router as post_router
from routers.ai_router import router as ai_router
from routers.user_router import router as user_router
from routers.comment_router import router as comment_router

# 테이블 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(post_router)
app.include_router(ai_router)
app.include_router(user_router)
app.include_router(comment_router)