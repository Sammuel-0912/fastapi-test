#!/bin/sh
# 1. 自動執行資料庫遷移
alembic upgrade head

# 2. 啟動 FastAPI 服務
exec uvicorn app.main:app --host 0.0.0.0 --port 8000