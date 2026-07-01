"""
Detection Engine — FastAPI service that accepts log batches,
runs rule-based detection, and returns/persists alerts.
"""

import datetime
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import Alert
from .schemas import LogEntry, AlertResponse, AnalyzeResponse
from .engine import analyze_logs

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Detection Engine",
    description="Rule-based SOC detection engine for Cyber Range SOC Lite.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── In-memory log window (sliding buffer) ────────────────────────
# Keeps last 5 minutes of logs for cross-request correlation.

LOG_BUFFER: list[dict] = []
BUFFER_WINDOW_SECONDS = 300


def _trim_buffer():
    now = datetime.datetime.utcnow()
    cutoff = now - datetime.timedelta(seconds=BUFFER_WINDOW_SECONDS)
    global LOG_BUFFER
    LOG_BUFFER = [log for log in LOG_BUFFER
                  if _parse_ts(log.get("timestamp")) >= cutoff]


def _parse_ts(ts):
    if ts:
        try:
            return datetime.datetime.fromisoformat(ts)
        except (ValueError, TypeError):
            pass
    return datetime.datetime.utcnow()


def _persist_alert(alert: dict, db: Session):
    a = Alert(
        attack_type=alert["attack_type"],
        severity=alert["severity"],
        ip=alert["ip"],
        description=alert["description"],
    )
    db.add(a)
    db.commit()


# ── Endpoints ────────────────────────────────────────────────────

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: list[LogEntry], db: Session = Depends(get_db)):
    _trim_buffer()

    raw_logs = [log.model_dump() for log in payload]
    for log in raw_logs:
        if not log.get("timestamp"):
            log["timestamp"] = datetime.datetime.utcnow().isoformat()

    LOG_BUFFER.extend(raw_logs)

    def persist(alert):
        _persist_alert(alert, db)

    alerts = analyze_logs(LOG_BUFFER, persist=persist)

    saved = (
        db.query(Alert)
        .order_by(Alert.timestamp.desc())
        .limit(len(alerts) if alerts else 1)
        .all()
    )

    return AnalyzeResponse(
        alerts_generated=len(alerts),
        alerts=saved,
    )


@app.get("/alerts", response_model=list[AlertResponse])
def list_alerts(
    skip: int = 0,
    limit: int = 100,
    attack_type: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Alert)
    if attack_type:
        query = query.filter(Alert.attack_type == attack_type)
    return (
        query.order_by(Alert.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@app.get("/health")
def health():
    return {"status": "healthy", "service": "Detection Engine"}
