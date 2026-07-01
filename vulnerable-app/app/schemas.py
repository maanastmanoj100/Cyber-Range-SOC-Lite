from pydantic import BaseModel
from typing import Optional
import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    token: Optional[str] = None
    password: Optional[str] = None


class LogEntryCreate(BaseModel):
    ip: str
    endpoint: str
    timestamp: str
    payload: str = ""


class LogEntryResponse(BaseModel):
    id: int
    ip: str
    endpoint: str
    timestamp: datetime.datetime
    payload: str

    class Config:
        from_attributes = True
