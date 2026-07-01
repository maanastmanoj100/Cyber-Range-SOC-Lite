import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from .database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    severity = Column(String(20), default="Low")
    source_ip = Column(String(45), nullable=False)
    destination_ip = Column(String(45), nullable=True)
    attack_type = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    is_acknowledged = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)


class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(45), nullable=False)
    event_type = Column(String(100), nullable=False)
    endpoint = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
