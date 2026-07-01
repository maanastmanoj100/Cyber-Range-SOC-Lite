from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=schemas.DashboardSummary)
def get_summary(db: Session = Depends(get_db)):
    total = db.query(models.Alert).count()
    critical = db.query(models.Alert).filter(models.Alert.severity == models.Severity.CRITICAL).count()
    high = db.query(models.Alert).filter(models.Alert.severity == models.Severity.HIGH).count()
    medium = db.query(models.Alert).filter(models.Alert.severity == models.Severity.MEDIUM).count()
    low = db.query(models.Alert).filter(models.Alert.severity == models.Severity.LOW).count()
    unresolved = db.query(models.Alert).filter(models.Alert.is_resolved == False).count()

    rows = (
        db.query(models.Alert.attack_type, func.count(models.Alert.id).label("cnt"))
        .group_by(models.Alert.attack_type)
        .all()
    )
    breakdown = {row.attack_type: row.cnt for row in rows}

    return schemas.DashboardSummary(
        total_alerts=total,
        critical_count=critical,
        high_count=high,
        medium_count=medium,
        low_count=low,
        unresolved_count=unresolved,
        attack_type_breakdown=breakdown,
    )
