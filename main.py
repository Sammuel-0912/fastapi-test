from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel


class MachineCreate(BaseModel):
    machine_id: str
    status: str


# 1. 資料庫設定 (使用本地檔案 factory.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./factory.db"
# connect_args={"check_same_thread": False} 是 SQLite 專用的非同步安全設定
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# 2. 定義資料庫的資料表模型 (Table Model)
class MachineTable(Base):
    __tablename__ = "machines"  # 資料表名稱

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, unique=True, index=True)  # 機台編號
    status = Column(String)  # 狀態


# 建立資料表檔案
Base.metadata.create_all(bind=engine)

# 3. 初始化 FastAPI
app = FastAPI()


# 4. 建立資料庫連線的依賴項目 (Dependency)
# 確保每次 API 請求進來時打開資料庫，處理完後自動關閉 (close)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === 同學的實作挑戰開始 ===


# TODO 1: 撰寫 POST 路由 - 新增機台到資料庫
@app.post("/machines")
def create_machine(payload: MachineCreate, db: Session = Depends(get_db)):
    # (A) 實例化一個資料表物件，並把前端傳來的資料填進去
    db_machine = MachineTable(machine_id=payload.machine_id, status=payload.status)

    # (B) 將這筆資料「新增」到資料庫的暫存階段
    # 提示：使用 db.add()
    db.add(db_machine)

    # (C) 將變更「提交（Commit）」給資料庫，這時候才會真正寫入硬碟！
    # 提示：使用 db.commit()
    db.commit()

    # (D) 刷新這筆資料，讓它自動取得資料庫核發的自增 id
    db.refresh(db_machine)
    return {"message": "機台建立成功", "data": db_machine}


# TODO 2: 撰寫 GET 路由 - 從資料庫撈出所有機台
@app.get("/machines")
def get_all_machines(db: Session = Depends(get_db)):
    # 提示：我們要去「查詢（query）」MachineTable，並且「拿出全部（.all()）」的資料
    # 請補齊中間的查詢邏輯：
    machines = db.query(MachineTable).all()

    return {"total_count": len(machines), "machines_list": machines}
