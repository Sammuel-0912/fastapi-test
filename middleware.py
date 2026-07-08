import time
from fastapi import Request


# 計時中間件：由 app/main.py 透過 app.middleware("http")(log_process_time) 掛載
# 中間件函式必須是異步的 (async)，且固定接收 request 和 call_next 兩個參數。
async def log_process_time(request: Request, call_next):
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
