from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, ConfigDict

# 1. 資料庫基礎設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./factory_v2.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    echo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 2. 【一對多資料表模型定義】
class MachineTable(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, unique=True, index=True)
    status = Column(String)

    # SQLAlchemy 特有的關聯設定：告訴 Python 這台機台下面綁著很多筆 logs
    # 提示：使用 relationship() 連結到下方的 "ErrorLogTable"
    logs = relationship("ErrorLogTable", back_populates="machine")


class ErrorLogTable(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    error_code = Column(String)
    description = Column(String)

    # 核心：外鍵（Foreign Key）指向 machines 資料表的 id 欄位
    machine_pk = Column(Integer, ForeignKey("machines.id"))

    # 連結回 MachineTable 的反向設定
    machine = relationship("MachineTable", back_populates="logs")


# 建立資料表
Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic 規格書
class MachineCreate(BaseModel):
    machine_id: str
    status: str


class LogCreate(BaseModel):
    machine_pk: int  # 對應到機台的資料庫唯一 ID
    error_code: str
    description: str


# === 回傳用的「公開規格書」(白名單濾網) ===
# 這裡故意「不放」id 和 machine_pk，Pydantic 就會在回傳前把它們過濾掉


class LogPublic(BaseModel):
    error_code: str
    description: str
    # from_attributes=True：允許 Pydantic 直接從 SQLAlchemy 的 ORM 物件讀屬性
    model_config = ConfigDict(from_attributes=True)


class MachineInfoPublic(BaseModel):
    machine_id: str
    status: str
    model_config = ConfigDict(from_attributes=True)


class MachineDetailPublic(BaseModel):
    machine_info: MachineInfoPublic
    history_logs: list[LogPublic]  # 巢狀套用上面的 LogPublic 濾網


class LogCreateResponse(BaseModel):
    message: str
    log_data: LogPublic  # log_data 也套 LogPublic 濾網，濾掉 id / machine_pk


# --- 路由開始 ---


# 步驟 1 用的路由：新增機台（補進 main2.py，讓整套流程在同一個 App 跑完）
@app.post("/machines")
def create_machine(payload: MachineCreate, db: Session = Depends(get_db)):
    db_machine = MachineTable(machine_id=payload.machine_id, status=payload.status)
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return {"message": "機台建立成功", "data": db_machine}


# TODO 1: 撰寫新增 Error Log 的 POST 路由
@app.post("/logs", response_model=LogCreateResponse)
def create_log(payload: LogCreate, db: Session = Depends(get_db)):
    db_log = ErrorLogTable(
        machine_pk=payload.machine_pk,
        error_code=payload.error_code,
        description=payload.description,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return {"message": "異常紀錄成功", "log_data": db_log}


# TODO 2: 撰寫「一鍵雙表查詢」的 GET 路由
# 這是 ORM 最強大的地方：當我們查出機台時，SQLAlchemy 會自動幫我們把該機台底下的所有 logs 補進去！
@app.get("/machines/detail/{m_id}", response_model=MachineDetailPublic)
def get_machine_detail(m_id: str, db: Session = Depends(get_db)):
    # 提示：我們要去 query MachineTable，並且篩選出 machine_id 等於傳入的 m_id 的那「一筆」資料。
    # 提示：篩選用 .filter()，拿第一筆用 .first()
    target_machine = (
        db.query(MachineTable).filter(MachineTable.machine_id == m_id).first()
    )

    if not target_machine:
        raise HTTPException(status_code=404, detail="找不到該機台")

    return {
        "machine_info": {
            "machine_id": target_machine.machine_id,
            "status": target_machine.status,
        },
        # 魔術發生在這裡：因為設了一對多關聯，我們可以直接用 .logs 拿到該機台所有的異常紀錄列表！
        "history_logs": target_machine.logs,
    }
