# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 🆕 匯入 CORSMiddleware

from app.config import settings
from app.exceptions import NotFoundError, not_found_error_handler
from app.middleware import log_process_time  # 導入你寫的計時中間件
from app.routers import auth, logs, machines

# 自動建立資料表
# 以後建立與修改資料表一律交給 Alembic。
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="工廠自動化管理系統 API",
    description="這是一個採用企業級架構重構後的 FastAPI 專案",
    version="1.0.0",
)

# 2. 掛載計時中間件
app.middleware("http")(log_process_time)

# 1. 註冊 CORS 中間件 (須注意掛載順序)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # 🆕 動態讀取環境變數設定
    allow_credentials=True,  # 允許攜帶憑證 (Cookie/Auth Header)
    allow_methods=["*"],  # 允許所有 HTTP 方法 (GET, POST, DELETE...)
    allow_headers=["*"],  # 允許所有 Header
    expose_headers=["X-Process-Time"],  # 🆕 顯式暴露自訂 Header 給前端 JS
)

# 註冊自訂例外與對應的處理器
app.add_exception_handler(NotFoundError, not_found_error_handler)

# 2. 註冊路由切片 (Include Routers)
app.include_router(logs.router)
app.include_router(logs.global_router)
app.include_router(machines.router)
app.include_router(auth.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to Factory API System"}
