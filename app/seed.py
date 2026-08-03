# app/seed.py
import asyncio
import logging
import os

from sqlalchemy import select

from app import models, security
from app.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_admin():
    """建立預設的 Admin 管理員帳號 (種子資料)"""

    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD")

    if not admin_password:
        logger.warning(
            "⚠️ 未設定 ADMIN_PASSWORD 環境變數，安全起見跳過自動建立管理員帳號。"
        )
        return

    async with SessionLocal() as session:
        # 1. 檢查是否已存在該管理員帳號
        stmt = select(models.User).where(models.User.username == "admin")
        result = await session.execute(stmt)
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            logger.info("ℹ️ Admin 管理員帳號已存在，跳過建立。")
            return

        # 2. 不存在則建立預設 admin
        # 💡 正式環境密碼建議從環境變數讀取，預設給 password123
        default_admin = models.User(
            username=admin_username,
            hash_password=security.hash_password(admin_password),
            role="admin",  # 👈 賦予最高權限 role
        )
        session.add(default_admin)
        await session.commit()
        logger.info("✅ 成功建立預設 Admin 管理員帳號 (username: {admin_username})！")


if __name__ == "__main__":
    asyncio.run(seed_admin())
