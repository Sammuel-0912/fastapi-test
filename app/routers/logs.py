# app/routers/logs.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/logs", tags=["Logs (日誌管理)"])


@router.post(
    "/", response_model=schemas.LogResponse, status_code=status.HTTP_201_CREATED
)
async def create_log(
    log: schemas.LogCreate, machine_id: int, db: AsyncSession = Depends(get_db)
):
    # 先檢查機台是否存在
    # db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    stmt = select(models.Machine).where(models.Machine.id == machine_id)
    result = await db.execute(stmt)
    db_machine = result.scalar_one_or_none()

    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found, cannot log")

    db_log = models.Log(message=log.message, machine_id=machine_id)
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log


@router.get("/", response_model=List[schemas.LogResponse])
async def read_logs(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    # return db.query(models.Log).offset(skip).limit(limit).all()
    stmt = select(models.Log).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
