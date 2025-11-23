# main.py
from fastapi import FastAPI
from routers.user_router import router as user_router
from routers.post_router import router as post_router
from routers.ai_router import router as ai_router

app = FastAPI()
app.include_router(user_router)
app.include_router(post_router)
app.include_router(ai_router)