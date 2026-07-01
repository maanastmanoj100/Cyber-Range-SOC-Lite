import datetime
from pydantic import BaseModel
from typing import Optional


class LogCreate(BaseModel):
    ip: str
    event_type: str
    endpoint: str
    timestamp: Optional[str] = None


class LogResponse(BaseModel):
    id: int
    ip: str
    event_type: str
    endpoint: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True
