# app/models/machine.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    status = Column(String, default="operational")

    # 新增location欄位
    location = Column(String, default="Line A", server_default="Line A")
    # 一對多關聯：一個機台擁有多個日誌
    logs = relationship(
        "Log", back_populates="machine", cascade="all, delete-orphan", lazy="selectin"
    )
