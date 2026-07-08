# app/routers/logs.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/logs", tags=["Logs (日誌管理)"])


@router.post(
    "/", response_model=schemas.LogResponse, status_code=status.HTTP_201_CREATED
)
def create_log(log: schemas.LogCreate, machine_id: int, db: Session = Depends(get_db)):
    # 先檢查機台是否存在
    db_machine = (
        db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    )
    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found, cannot log")

    db_log = models.Log(message=log.message, machine_id=machine_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/", response_model=List[schemas.LogResponse])
def read_logs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Log).offset(skip).limit(limit).all()
