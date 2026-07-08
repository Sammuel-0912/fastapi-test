# app/schemas/machine.py
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.log import LogResponse


class MachineBase(BaseModel):
    name: str
    status: Optional[str] = "operational"
    location: Optional[str] = "Line A"


class MachineCreate(MachineBase):
    # 這裡什麼都不用寫，它會自動繼承 MachineBase 的 name, status, location
    pass


class MachineResponse(MachineBase):
    id: int
    # 巢狀結構：回傳機台時，順便包進該機台的所有日誌
    logs: List[LogResponse] = []

    class Config:
        from_attributes = True
