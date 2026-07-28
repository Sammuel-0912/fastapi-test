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


class MachineResponse(MachineBase):
    id: int
    # 巢狀結構：回傳機台時，順便包進該機台的所有日誌
    logs: list[LogResponse] = []

    model_config = ConfigDict(from_attributes=True)
