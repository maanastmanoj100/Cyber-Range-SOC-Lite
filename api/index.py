import os
import random
import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .database import engine, Base, get_db
from .models import Alert, LogEntry
from .schemas import (
    LogCreate, LogResponse,
    AlertResponse, AlertUpdate,
    AnalyzeResponse, ExplainRequest, ExplainResponse,
    DashboardSummary,
)
from .detection import analyze_logs
from .explainer import explain as explain_fn


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Cyber Range SOC Lite",
    description="Consolidated SOC dashboard API — Vercel-compatible.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Logs ──────────────────────────────────────────────────────────

@app.post("/api/logs")
async def create_log(entry: LogCreate, db: AsyncSession = Depends(get_db)):
    ts = (
        datetime.datetime.fromisoformat(entry.timestamp)
        if entry.timestamp
        else datetime.datetime.utcnow()
    )
    log = LogEntry(ip=entry.ip, event_type=entry.event_type, endpoint=entry.endpoint, timestamp=ts)
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return {"status": "logged", "id": log.id}


@app.get("/api/logs", response_model=list[LogResponse])
async def list_logs(
    skip: int = 0,
    limit: int = 100,
    event_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(LogEntry)
    if event_type:
        query = query.where(LogEntry.event_type == event_type)
    query = query.order_by(LogEntry.timestamp.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# ── Detection (analyze logs → generate alerts) ────────────────────

@app.post("/api/logs/analyze", response_model=AnalyzeResponse)
async def detect(body: list[LogCreate], db: AsyncSession = Depends(get_db)):
    alerts = await analyze_logs(db)
    return AnalyzeResponse(
        alerts_generated=len(alerts),
        alerts=[AlertResponse.model_validate(a) for a in alerts],
    )


# ── Alerts CRUD ───────────────────────────────────────────────────

@app.get("/api/alerts", response_model=list[AlertResponse])
async def list_alerts(
    skip: int = 0,
    limit: int = 100,
    severity: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Alert)
    if severity:
        query = query.where(Alert.severity == severity)
    query = query.order_by(Alert.timestamp.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@app.get("/api/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@app.put("/api/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(alert_id: int, payload: AlertUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(alert, key, value)
    await db.commit()
    await db.refresh(alert)
    return alert


@app.delete("/api/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    await db.delete(alert)
    await db.commit()


# ── Dashboard ─────────────────────────────────────────────────────

@app.get("/api/dashboard/summary", response_model=DashboardSummary)
async def get_summary(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(Alert.id)))).scalar() or 0
    critical = (await db.execute(select(func.count(Alert.id)).where(Alert.severity == "Critical"))).scalar() or 0
    high = (await db.execute(select(func.count(Alert.id)).where(Alert.severity == "High"))).scalar() or 0
    medium = (await db.execute(select(func.count(Alert.id)).where(Alert.severity == "Medium"))).scalar() or 0
    low = (await db.execute(select(func.count(Alert.id)).where(Alert.severity == "Low"))).scalar() or 0
    unresolved = (await db.execute(select(func.count(Alert.id)).where(Alert.is_resolved == False))).scalar() or 0

    rows = await db.execute(
        select(Alert.attack_type, func.count(Alert.id).label("cnt"))
        .group_by(Alert.attack_type)
    )
    breakdown = {row.attack_type: row.cnt for row in rows}

    return DashboardSummary(
        total_alerts=total,
        critical_count=critical,
        high_count=high,
        medium_count=medium,
        low_count=low,
        unresolved_count=unresolved,
        attack_type_breakdown=breakdown,
    )


# ── Attack Simulation ──────────────────────────────────────────────

ATTACK_TYPES = [
    "Port Scan", "Brute Force", "SQL Injection", "XSS",
    "DDoS", "Phishing", "Malware", "Man-in-the-Middle",
    "DNS Spoofing", "Zero-Day Exploit",
]
SAMPLE_TITLES = [
    "Suspicious inbound connection detected",
    "Multiple failed login attempts",
    "Unusual outbound data transfer",
    "Malicious payload detected",
    "Anomalous DNS query pattern",
    "Potential credential stuffing attack",
]
SAMPLE_DESCRIPTIONS = [
    "Automated detection system flagged an IP address performing reconnaissance.",
    "IDS/IPS triggered signature match for known exploit pattern.",
    "Endpoint logs show repeated authentication failures from external source.",
    "Network traffic analysis reveals unusual data exfiltration pattern.",
    "WAF blocked request containing SQL injection payload.",
    "Correlation engine matched multiple low-severity events into a campaign.",
]


def random_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"


@app.post("/api/attacks/simulate", response_model=AlertResponse)
async def simulate_attack(db: AsyncSession = Depends(get_db)):
    attack_type = random.choice(ATTACK_TYPES)
    severity = random.choices(
        ["Low", "Medium", "High", "Critical"],
        weights=[1, 2, 3, 4],
    )[0]

    alert = Alert(
        title=random.choice(SAMPLE_TITLES),
        description=random.choice(SAMPLE_DESCRIPTIONS),
        severity=severity,
        source_ip=random_ip(),
        destination_ip=random_ip(),
        attack_type=attack_type,
        timestamp=datetime.datetime.utcnow(),
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


@app.post("/api/attacks/batch-simulate", response_model=list[AlertResponse])
async def batch_simulate(count: int = 5, db: AsyncSession = Depends(get_db)):
    alerts = []
    for _ in range(count):
        attack_type = random.choice(ATTACK_TYPES)
        severity = random.choices(
            ["Low", "Medium", "High", "Critical"],
            weights=[1, 2, 3, 4],
        )[0]
        alert = Alert(
            title=random.choice(SAMPLE_TITLES),
            description=random.choice(SAMPLE_DESCRIPTIONS),
            severity=severity,
            source_ip=random_ip(),
            destination_ip=random_ip(),
            attack_type=attack_type,
            timestamp=datetime.datetime.utcnow(),
        )
        db.add(alert)
        alerts.append(alert)
    await db.commit()
    for a in alerts:
        await db.refresh(a)
    return alerts


# ── Explainer ─────────────────────────────────────────────────────

@app.post("/api/explain", response_model=ExplainResponse)
async def explain_endpoint(body: ExplainRequest):
    return explain_fn(
        attack_type=body.attack_type,
        logs=[log.model_dump() for log in body.logs],
        ip_address=body.ip_address,
    )


@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "Cyber Range SOC Lite"}
