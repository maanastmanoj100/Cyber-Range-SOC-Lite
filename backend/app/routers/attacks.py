import random
import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/attacks", tags=["attacks"])

ATTACK_TYPES = [
    "Port Scan",
    "Brute Force",
    "SQL Injection",
    "XSS",
    "DDoS",
    "Phishing",
    "Malware",
    "Man-in-the-Middle",
    "DNS Spoofing",
    "Zero-Day Exploit",
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


@router.post("/simulate", response_model=schemas.AlertResponse)
def simulate_attack(db: Session = Depends(get_db)):
    attack_type = random.choice(ATTACK_TYPES)
    severity = random.choices(
        list(models.Severity),
        weights=[4, 3, 2, 1],
    )[0]

    alert = models.Alert(
        title=random.choice(SAMPLE_TITLES),
        description=random.choice(SAMPLE_DESCRIPTIONS),
        severity=severity,
        source_ip=random_ip(),
        destination_ip=random_ip(),
        attack_type=attack_type,
        timestamp=datetime.datetime.utcnow(),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/batch-simulate", response_model=list[schemas.AlertResponse])
def batch_simulate(count: int = 5, db: Session = Depends(get_db)):
    alerts = []
    for _ in range(count):
        attack_type = random.choice(ATTACK_TYPES)
        severity = random.choices(
            list(models.Severity),
            weights=[4, 3, 2, 1],
        )[0]
        alert = models.Alert(
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
    db.commit()
    for a in alerts:
        db.refresh(a)
    return alerts
