# app/schemas/log.py
from pydantic import BaseModel


class LogBase(BaseModel):
    message: str


class LogCreate(LogBase):
    pass


class LogResponse(LogBase):
    id: int
    machine_id: int

    class Config:
        from_attributes = True
