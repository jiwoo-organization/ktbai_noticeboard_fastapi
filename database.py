# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
import pymysql
from dotenv import load_dotenv
import os
# MySQL 드라이버
pymysql.install_as_MySQLdb()
load_dotenv()  # 자동으로 .env 읽음

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,          # SQL 로그 보고 싶으면 True
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
