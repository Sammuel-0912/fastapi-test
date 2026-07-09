# 負責處理資料庫的連線引擎（Engine）與 Session 工廠。

# app/database.py
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./factory.db"

engine = create_async_engine(
    # connect_args={"check_same_thread": False} 是 SQLite 特有的參數
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
# 🆕 建立非同步 Session 工廠，並指定 class_=AsyncSession
SessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

Base = declarative_base()


# 🆕 依賴項也要全面改為非同步：加上 async def，且回傳型態提示為 AsyncSession
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            # async with 會自動在結束時呼叫 db.close()，非常安全
            pass
