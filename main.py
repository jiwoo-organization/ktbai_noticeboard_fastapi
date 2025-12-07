# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers.user_router import router as user_router
from routers.post_router import router as post_router
from routers.comment_router import router as comment_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 업로드 이미지 제공
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 🔥 모든 라우터는 /api 아래에 붙인다
app.include_router(user_router, prefix="/api")
app.include_router(post_router, prefix="/api")
app.include_router(comment_router, prefix="/api")
