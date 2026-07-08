# app/main.py
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import machines, logs, auth
from app.middleware import log_process_time  # 導入你寫的計時中間件

# 自動建立資料表
# 以後建立與修改資料表一律交給 Alembic。
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="工廠自動化管理系統 API",
    description="這是一個採用企業級架構重構後的 FastAPI 專案",
    version="1.0.0",
)

# 1. 掛載中間件
app.middleware("http")(log_process_time)

# 2. 註冊路由切片 (Include Routers)
app.include_router(machines.router)
app.include_router(logs.router)
app.include_router(auth.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to Factory API System"}
