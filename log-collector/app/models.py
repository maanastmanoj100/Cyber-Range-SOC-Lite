import datetime
from sqlalchemy import Column, Integer, String, DateTime
from .database import Base


class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(45), nullable=False)
    event_type = Column(String(100), nullable=False)
    endpoint = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
