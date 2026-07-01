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


class AlertResponse(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    severity: str
    source_ip: str
    destination_ip: Optional[str] = None
    attack_type: str
    timestamp: datetime.datetime
    is_acknowledged: bool = False
    is_resolved: bool = False

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    is_acknowledged: Optional[bool] = None
    is_resolved: Optional[bool] = None


class DetectRequest(BaseModel):
    logs: list[LogCreate]


class AnalyzeResponse(BaseModel):
    alerts_generated: int
    alerts: list[AlertResponse]


class ExplainRequest(BaseModel):
    attack_type: str
    logs: list[LogCreate]
    ip_address: str


class ExplainResponse(BaseModel):
    attack_type: str
    explanation: str
    risk_level: str
    recommended_action: str


class DashboardSummary(BaseModel):
    total_alerts: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    unresolved_count: int
    attack_type_breakdown: dict
