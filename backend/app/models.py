import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum
from .database import Base
import enum


class Severity(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Enum(Severity), default=Severity.LOW)
    source_ip = Column(String(45), nullable=False)
    destination_ip = Column(String(45), nullable=False)
    attack_type = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    is_acknowledged = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
