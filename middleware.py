import time
from fastapi import FastAPI, Request

# 1. 初始化 FastAPI 實例
app = FastAPI()

# === 同學的實作挑戰開始 ===

# TODO 1: 建置自動計時 Middleware
# 提示：FastAPI 的中間件要使用 @app.middleware("http") 裝飾器
# 中間件函式必須是異步的 (async)，且固定接收 request 和 call_next 兩個參數。


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # (A) 請求進來前：記錄開始時間
    start_time = time.time()

    # (B) 將請求送交給後續的路由處理，並等待回應
    response = await call_next(request)

    # (C) 回應出去前：計算總耗時（秒）
    process_time = time.time() - start_time

    # 將耗時記錄在 Response 的 Header 中（自訂標頭為 X-Process-Time）
    response.headers["X-Process-Time"] = str(process_time)

    # 最後必須回傳 response
    return response


# TODO 2: 撰寫 GET 路由
# 老闆希望輸入網址 `http://127.0.0.1:8000/` 時，能看到歡迎訊息。
# 提示：使用 @app.get() 裝飾器
@app.get("/")
async def root():
    return {"message": "Welcome to Factory API System"}


# TODO 3: 撰寫 POST 路由（模擬接收產線異常回報）
# 老闆希望當前端發送 POST 請求到 `/report` 時，能接收 JSON 資料並回傳成功狀態。
# 提示：使用 @app.post() 裝飾器
@app.post("/report")
async def create_report(payload: dict):
    # 這裡的 payload 會自動接收前端傳過來的 JSON 字典
    print(f"收到產線回報：{payload}")
    return {"status": "success", "data_received": payload}
