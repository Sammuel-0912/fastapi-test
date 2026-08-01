# app/schemas/machine.py

from pydantic import BaseModel, ConfigDict

from app.schemas.log import LogResponse


class MachineBase(BaseModel):
    name: str
    status: str | None = "operational"
    location: str | None = "Line A"


class MachineCreate(MachineBase):
    # 這裡什麼都不用寫，它會自動繼承 MachineBase 的 name, status, location
    pass


# 🆕 瘦身版 Schema：供列表端點 (GET /machines) 使用，不含 logs 陣列
class MachineListResponse(MachineBase):
    id: int
    # 巢狀結構：回傳機台時，順便包進該機台的所有日誌
    model_config = ConfigDict(from_attributes=True)


# 完整版 Schema：供單筆詳情端點 (GET /machines/{id}) 使用，包含完整 logs 陣列
class MachineResponse(MachineBase):
    id: int
    logs: list[LogResponse] = []

    model_config = ConfigDict(from_attributes=True)
