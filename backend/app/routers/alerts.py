from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/", response_model=List[schemas.AlertResponse])
def list_alerts(
    skip: int = 0,
    limit: int = 100,
    severity: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Alert)
    if severity:
        query = query.filter(models.Alert.severity == severity)
    return query.order_by(models.Alert.timestamp.desc()).offset(skip).limit(limit).all()


@router.get("/{alert_id}", response_model=schemas.AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/{alert_id}", response_model=schemas.AlertResponse)
def update_alert(alert_id: int, payload: schemas.AlertUpdate, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(alert, key, value)
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
