#!/bin/sh
set -e

# 1. 自動執行資料庫遷移
echo "Running database migrations..."
alembic upgrade head

# 2. 自動執行種子資料注入 (建立預設 admin)
echo "Seeding initial database data..."
python -m app.seed

# 3. 啟動 FastAPI 服務
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000