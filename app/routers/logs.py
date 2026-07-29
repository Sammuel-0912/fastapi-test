# app/routers/logs.py
import logging  # 🆕 匯入 logging 模組

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from typing import Callable
from app.database import (
    SessionLocal,
    get_db,
)  # 🆕 匯入 SessionLocal 以便背景任務自行開 session
from app.exceptions import NotFoundError

# 🆕 建立專屬於此模組的 Logger
logger = logging.getLogger(__name__)


# 1. 巢狀路由：專門處理特定機台的日誌 (/machines/{machine_id}/logs)
router = APIRouter(prefix="/machines/{machine_id}/logs", tags=["Logs (日誌管理)"])

# 2. 全域路由：處理跨機台日誌查詢 (/logs)
global_router = APIRouter(
    prefix="/logs",
    tags=["Logs (全域日誌管理)"],
)


# 🆕 背景任務函式 (題目 2：獨立建立 Session 並查詢機台名稱)
async def notify_maintenance(
    machine_id: int, log_id: int, session_factory: Callable | None = None
):
    """在背景執行：自己開啟獨立 Session 查詢機台名稱並模擬發送通知"""
    # 於執行期解析，讓測試可透過 monkeypatch 替換模組層級的 SessionLocal
    factory = session_factory or SessionLocal
    try:
        async with factory() as session:
            machine = await session.get(models.Machine, machine_id)
            if machine:
                logger.info(
                    f"[背景通知成功] 📢 機台「{machine.name}」(ID: {machine_id}) 新增了日誌 #{log_id}"
                )
            else:
                logger.warning(
                    f"[背景通知警告] 找不到機台 ID {machine_id}，日誌 #{log_id} 通知未發送。"
                )
    except Exception:
        # ❌ 捕捉所有未預期的錯誤，印出完整的 Error
        logger.exception(f"[背景通知失敗] 處理機台 ID {machine_id} 的日誌 #{log_id}")


@router.post(
    "", response_model=schemas.LogResponse, status_code=status.HTTP_201_CREATED
)
async def create_machine_log(
    machine_id: int,  # FastAPI 自動識別為路徑參數 {machine_id}
    log_in: schemas.LogCreate,
    background_tasks: BackgroundTasks,  # 👈 題目 1：擺在無預設值區段，避免 SyntaxError
    db: AsyncSession = Depends(get_db),
):
    """第 1 題：為指定機台建立日誌"""
    machine = await db.get(models.Machine, machine_id)
    if not machine:
        raise NotFoundError("Machine", machine_id)
    # 先檢查機台是否存在
    # db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    # stmt = select(models.Machine).where(models.Machine.id == machine_id)
    # result = await db.execute(stmt)
    # db_machine = result.scalar_one_or_none()

    # 建立日誌模型，並指定 machine_id
    db_log = models.Log(**log_in.model_dump(), machine_id=machine_id)
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)

    # 題目 1 & 2：將背景任務排入佇列，僅傳入基本 ID 參數
    background_tasks.add_task(
        notify_maintenance, machine_id=machine_id, log_id=db_log.id
    )

    return db_log


@router.get("", response_model=list[schemas.LogResponse])
async def read_machine_logs(
    machine_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    # return db.query(models.Log).offset(skip).limit(limit).all()
    """第 2 題：只列出指定機台的日誌"""
    stmt = (
        select(models.Log)
        .where(models.Log.machine_id == machine_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


# === 全域路由端點 ===
@global_router.get("", response_model=list[schemas.LogResponse])
async def read_all_logs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """第 3 題：全系統日誌查詢（跨機台）"""
    stmt = select(models.Log).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
