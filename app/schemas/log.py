# app/schemas/log.py
from pydantic import BaseModel, ConfigDict


class LogBase(BaseModel):
    message: str


class LogCreate(LogBase):
    pass


class LogResponse(LogBase):
    id: int
    machine_id: int

    model_config = ConfigDict(from_attributes=True)
