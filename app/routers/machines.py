# app/routers/machines.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.routers.auth import get_current_user  # 🆕 匯入防護罩

# 宣告此 Router 的所有 API 都會自帶 /machines 前綴
router = APIRouter(prefix="/machines", tags=["Machines (機台管理)"])


@router.post(
    "/", response_model=schemas.MachineResponse, status_code=status.HTTP_201_CREATED
)
def create_machine(
    machine: schemas.MachineCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    print(f"操作人是：{current_user.username}")
    db_machine = models.Machine(name=machine.name, status=machine.status)
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine


@router.get("/", response_model=List[schemas.MachineResponse])
def read_machines(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Machine).offset(skip).limit(limit).all()


@router.get("/{machine_id}", response_model=schemas.MachineResponse)
def read_machine(machine_id: int, db: Session = Depends(get_db)):
    db_machine = (
        db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    )
    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return db_machine


@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # 🆕 加上防護罩
):
    db_machine = (
        db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    )
    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    db.delete(db_machine)
    db.commit()
    return None
