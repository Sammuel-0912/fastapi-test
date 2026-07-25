from fastapi import Request, status
from fastapi.responses import JSONResponse

# 1. 定義自訂例外類別
class NotFoundError(Exception):
  def __init__(self, machine_name : str, machine_id: int | str):
    self.machine_name = machine_name
    self.machine_id = machine_id
    # 自動組裝統一格式的錯誤訊息

    self.message = f"{machine_name} with id {machine_id} not found"
    
# 2. 定義 Exception Handler (處理器)
async def not_found_error_handler(request: Request, exc: NotFoundError):
  return JSONResponse(
    status_code=status.HTTP_404_NOT_FOUND,
    content={"detail": exc.message}
  )