import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from .database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    attack_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    ip = Column(String(45), nullable=False)
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
