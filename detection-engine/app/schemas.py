import datetime
from pydantic import BaseModel
from typing import Optional


class LogEntry(BaseModel):
    ip: str
    event_type: str
    endpoint: str
    timestamp: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    attack_type: str
    severity: str
    ip: str
    description: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True


class AnalyzeResponse(BaseModel):
    alerts_generated: int
    alerts: list[AlertResponse]
