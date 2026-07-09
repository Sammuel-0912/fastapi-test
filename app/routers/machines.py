# app/routers/machines.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

# 🆕 匯入 select 語法與非同步 Session 型態
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.routers.auth import get_current_user  # 🆕 匯入防護罩

# 宣告此 Router 的所有 API 都會自帶 /machines 前綴
router = APIRouter(prefix="/machines", tags=["Machines (機台管理)"])


@router.post(
    "/", response_model=schemas.MachineResponse, status_code=status.HTTP_201_CREATED
)
async def create_machine(
    machine: schemas.MachineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    print(f"操作人是：{current_user.username}")
    db_machine = models.Machine(
        name=machine.name, status=machine.status, location=machine.location
    )
    db.add(db_machine)
    await db.commit()
    await db.refresh(db_machine)
    return db_machine


@router.get("/", response_model=List[schemas.MachineResponse])
async def read_machines(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    # return db.query(models.Machine).offset(skip).limit(limit).all()
    # 🆕 SQLAlchemy 2.0 非同步標準寫法：
    # 先建立一個 select 查詢語句物件
    stmt = select(models.Machine).offset(skip).limit(limit)

    # 執行查詢（必須 await），這會拿到一個 result 物件
    result = await db.execute(stmt)

    # scalars().all() 可以把結果轉換成一般的 Python 列表
    return result.scalars().all()


@router.get("/{machine_id}", response_model=schemas.MachineResponse)
async def read_machine(machine_id: int, db: AsyncSession = Depends(get_db)):
    # db_machine = (
    #     db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    # )
    # if not db_machine:
    #     raise HTTPException(status_code=404, detail="Machine not found")
    # return db_machine
    # 🆕 查詢單一資料的非同步標準寫法
    stmt = select(models.Machine).filter(models.Machine.id == machine_id)
    result = await db.execute(stmt)
    db_machine = result.scalar_one_or_none()  # 拿到單一物件，若沒有則為 None

    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return db_machine


@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_machine(
    machine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # 🆕 加上防護罩
):
    # db_machine = (
    #     db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    # )
    # if not db_machine:
    #     raise HTTPException(status_code=404, detail="Machine not found")
    # db.delete(db_machine)
    # db.commit()
    # return None
    stmt = select(models.Machine).filter(models.Machine.id == machine_id)
    result = await db.execute(stmt)
    db_machine = result.scalar_one_or_none()
    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    # 🆕 刪除物件並 commit（必須 await）
    await db.delete(db_machine)
    await db.commit()
    return None
