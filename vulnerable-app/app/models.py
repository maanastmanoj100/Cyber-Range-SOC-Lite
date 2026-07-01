import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")


class StoredData(Base):
    __tablename__ = "stored_data"

    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String(100), nullable=False)
    secret = Column(Text, nullable=False)
    note = Column(String(255), default="")


class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(45), nullable=False)
    endpoint = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    payload = Column(Text, default="")
