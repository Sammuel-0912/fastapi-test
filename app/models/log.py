# app/models/log.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(
        Integer, ForeignKey("machines.id", ondelete="CASCADE"), nullable=False
    )
    message = Column(String, nullable=False)

    # 關聯回機台
    machine = relationship("Machine", back_populates="logs")
