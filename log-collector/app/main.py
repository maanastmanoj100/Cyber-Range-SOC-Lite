import datetime
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base, get_db
from .models import LogEntry
from .schemas import LogCreate, LogResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Log Collector",
    description="Centralised log ingestion service for Cyber Range SOC Lite.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/log")
def create_log(entry: LogCreate, db: Session = Depends(get_db)):
    ts = (
        datetime.datetime.fromisoformat(entry.timestamp)
        if entry.timestamp
        else datetime.datetime.utcnow()
    )
    log = LogEntry(
        ip=entry.ip,
        event_type=entry.event_type,
        endpoint=entry.endpoint,
        timestamp=ts,
    )
    db.add(log)
    db.commit()
    return {"status": "logged", "id": log.id}


@app.get("/logs", response_model=list[LogResponse])
def list_logs(
    skip: int = 0,
    limit: int = 100,
    event_type: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(LogEntry)
    if event_type:
        query = query.filter(LogEntry.event_type == event_type)
    return (
        query.order_by(LogEntry.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@app.get("/health")
def health():
    return {"status": "healthy", "service": "Log Collector"}
