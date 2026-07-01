import datetime
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class SeverityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class AlertBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: SeverityEnum = SeverityEnum.LOW
    source_ip: str
    destination_ip: str
    attack_type: str


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    is_acknowledged: Optional[bool] = None
    is_resolved: Optional[bool] = None


class AlertResponse(AlertBase):
    id: int
    timestamp: datetime.datetime
    is_acknowledged: bool
    is_resolved: bool

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    total_alerts: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    unresolved_count: int
    attack_type_breakdown: dict
