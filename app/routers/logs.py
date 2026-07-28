# app/routers/logs.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import models, schemas
from app.exceptions import NotFoundError

# 1. 巢狀路由：專門處理特定機台的日誌 (/machines/{machine_id}/logs)
router = APIRouter(prefix="/machines/{machine_id}/logs", tags=["Logs (日誌管理)"])

# 2. 全域路由：處理跨機台日誌查詢 (/logs)
global_router = APIRouter(
    prefix="/logs",
    tags=["Logs (全域日誌管理)"],
)
@router.post(
    "/", response_model=schemas.LogResponse, status_code=201
)
async def create_machine_log(
    machine_id: int, # FastAPI 自動識別為路徑參數 {machine_id}
    log_in: schemas.LogCreate, 
    db: AsyncSession = Depends(get_db),
):
    """第 1 題：為指定機台建立日誌"""
    machine = await db.get(models.Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
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
    return db_log


@router.get("/", response_model=list[schemas.LogResponse])
async def read_machine_logs(machine_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
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
@global_router.get("/", response_model=list[schemas.LogResponse])
async def read_all_logs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """第 3 題：全系統日誌查詢（跨機台）"""
    stmt = select(models.Log).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()