# 負責處理資料庫的連線引擎（Engine）與 Session 工廠。

# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./factory.db"

engine = create_engine(
    # connect_args={"check_same_thread": False} 是 SQLite 特有的參數
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# 依賴項：每次請求時獲取資料庫 Session，結束後自動關閉
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
