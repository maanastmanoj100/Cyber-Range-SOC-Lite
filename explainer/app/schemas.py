from pydantic import BaseModel
from typing import Optional


class LogEntry(BaseModel):
    ip: str
    event_type: str
    endpoint: str
    timestamp: Optional[str] = None


class ExplainRequest(BaseModel):
    attack_type: str
    logs: list[LogEntry]
    ip_address: str


class ExplainResponse(BaseModel):
    attack_type: str
    explanation: str
    risk_level: str
    recommended_action: str
