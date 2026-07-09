# 工廠自動化管理系統 API

採用企業級架構打造的 FastAPI 專案，提供機台（Machine）、日誌（Log）與使用者認證（Auth）管理功能。資料庫存取全面採用 **SQLAlchemy 2.0 非同步（async/await）** 寫法。

## ✨ 特色

- **非同步全鏈路**：路由、依賴項、資料庫 Session 皆為 `async`，搭配 `await db.execute(select(...))`
- **JWT 認證**：註冊 / 登入取得 Token，受保護端點需攜帶 `Bearer` Token
- **分層架構**：`routers` / `models` / `schemas` 職責分離
- **資料庫遷移**：使用 Alembic 管理 schema 版本
- **中間件**：內建請求處理時間計時中間件
- **容器化**：提供 Dockerfile 與 Docker Compose 設定
- **測試**：pytest + pytest-asyncio + httpx `AsyncClient`

## 🛠 技術棧

| 分類 | 使用技術 |
|------|----------|
| Web 框架 | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0（async） |
| 資料庫驅動 | aiosqlite（SQLite） |
| 遷移工具 | Alembic |
| 認證 | PyJWT + passlib[bcrypt] |
| 設定管理 | pydantic-settings |
| 測試 | pytest / pytest-asyncio / httpx |

## 📁 專案結構

```
fastapi-test/
├── app/
│   ├── main.py            # FastAPI 進入點，掛載中間件與路由
│   ├── config.py          # 讀取 .env 的設定（Settings）
│   ├── database.py        # 非同步引擎、Session 工廠、get_db 依賴項
│   ├── security.py        # 密碼雜湊等安全工具
│   ├── middleware/        # 請求計時中間件
│   ├── models/            # SQLAlchemy 資料表模型（Machine / Log / User）
│   ├── schemas/           # Pydantic 請求/回應結構
│   └── routers/           # API 路由（machines / logs / auth）
├── alembic/               # 資料庫遷移版本
├── tests/                 # pytest 測試（非同步）
├── requirements.txt
├── pytest.ini             # asyncio_mode = auto
├── Dockerfile
├── compose.yaml
└── .env.example
```

## 🚀 快速開始

### 1. 建立虛擬環境並安裝依賴

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 設定環境變數

複製範例檔並填入你的 `SECRET_KEY`：

```bash
cp .env.example .env
```

`.env` 內容：

```dotenv
SECRET_KEY=<請填入一組隨機字串>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> 產生隨機金鑰：`python -c "import secrets; print(secrets.token_hex(32))"`

### 3. 執行資料庫遷移

```bash
alembic upgrade head
```

### 4. 啟動服務

```bash
uvicorn app.main:app --reload
```

啟動後開啟互動式文件：

- Swagger UI：<http://127.0.0.1:8000/docs>
- ReDoc：<http://127.0.0.1:8000/redoc>

## 🐳 使用 Docker

`start.sh` 會先執行 `alembic upgrade head` 再啟動 Uvicorn。

```bash
docker compose up --build
```

服務會對外開放於 `http://localhost:8000`。

## 📡 API 端點

| 方法 | 路徑 | 說明 | 需要 Token |
|------|------|------|:---:|
| `GET` | `/` | 服務歡迎訊息 | ❌ |
| `POST` | `/auth/register` | 註冊新帳號 | ❌ |
| `POST` | `/auth/login` | 登入取得 JWT（表單格式 `application/x-www-form-urlencoded`） | ❌ |
| `POST` | `/machines/` | 新增機台 | ✅ |
| `GET` | `/machines/` | 查詢機台列表（支援 `skip` / `limit`） | ❌ |
| `GET` | `/machines/{machine_id}` | 查詢單一機台 | ❌ |
| `DELETE` | `/machines/{machine_id}` | 刪除機台 | ✅ |
| `POST` | `/logs/?machine_id={id}` | 為指定機台新增日誌 | ❌ |
| `GET` | `/logs/` | 查詢日誌列表（支援 `skip` / `limit`） | ❌ |

### 認證流程範例

```bash
# 1. 註冊
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpassword"}'

# 2. 登入取得 Token（注意：使用表單格式）
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=testuser&password=testpassword"

# 3. 攜帶 Token 呼叫受保護端點
curl -X POST http://127.0.0.1:8000/machines/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "CNC-001", "status": "operational", "location": "Line A"}'
```

## 🧪 測試

專案使用非同步測試（`pytest.ini` 已設定 `asyncio_mode = auto`），並以 SQLite 記憶體資料庫隔離測試資料。

```bash
pytest -v
```

## 🗄 資料庫

- 預設連線：`sqlite+aiosqlite:///./factory.db`（見 `app/database.py`）
- 建立 / 修改資料表一律透過 Alembic：

```bash
# 依模型變更產生新的遷移
alembic revision --autogenerate -m "描述你的變更"

# 套用至最新版本
alembic upgrade head
```
