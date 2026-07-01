import re
import datetime
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import LogEntry, Alert

SQLI_PATTERNS = [
    re.compile(r"'\s*OR\s+['\"]?\d*['\"]?\s*=\s*['\"]?\d*", re.I),
    re.compile(r"'\s*OR\s+['\"]?\d*['\"]?\s*LIKE\s+['\"]?\d*", re.I),
    re.compile(r"DROP\s+TABLE", re.I),
    re.compile(r"UNION\s+SELECT", re.I),
    re.compile(r"'\s*OR\s+['\"]?1['\"]?\s*=\s*['\"]?1", re.I),
    re.compile(r"'\s*OR\s+['\"]?1['\"]?\s*--", re.I),
    re.compile(r"'\s*OR\s+['\"]?1['\"]?\s*#", re.I),
    re.compile(r"'\s*--", re.I),
    re.compile(r"'\s*#", re.I),
    re.compile(r"'\s*;\s*DROP\s+", re.I),
    re.compile(r"'\s*UNION\s+SELECT", re.I),
    re.compile(r"'\s*AND\s+1\s*=\s*1", re.I),
    re.compile(r"'\s*AND\s+1\s*=\s*2", re.I),
    re.compile(r"WAITFOR\s+DELAY", re.I),
    re.compile(r"SLEEP\s*\(", re.I),
]


def _parse_ts(ts):
    if ts:
        try:
            return datetime.datetime.fromisoformat(ts)
        except (ValueError, TypeError):
            pass
    return datetime.datetime.utcnow()


def detect_brute_force(logs: list[dict], window_seconds: int = 60, threshold: int = 5) -> list[dict]:
    now = datetime.datetime.utcnow()
    window_start = now - datetime.timedelta(seconds=window_seconds)

    recent = [
        log for log in logs
        if log.get("event_type", "").lower() in ("login_failed", "failed_login", "401")
        or "/login" in log.get("endpoint", "")
    ]

    recent = [
        log for log in recent
        if _parse_ts(log.get("timestamp", "")) >= window_start
    ]

    by_ip = defaultdict(int)
    for log in recent:
        by_ip[log["ip"]] += 1

    alerts = []
    for ip, count in by_ip.items():
        if count >= threshold:
            alerts.append({
                "attack_type": "Brute Force Attack",
                "severity": "High",
                "ip": ip,
                "description": (
                    f"{count} failed login attempts from {ip} "
                    f"in the last {window_seconds} seconds"
                ),
            })
    return alerts


def detect_sql_injection(logs: list[dict]) -> list[dict]:
    alerts = []
    for log in logs:
        endpoint = log.get("endpoint", "")
        event_type = log.get("event_type", "")
        combined = f"{endpoint} {event_type}"

        for pattern in SQLI_PATTERNS:
            match = pattern.search(combined)
            if match:
                match_text = match.group()
                alerts.append({
                    "attack_type": "SQL Injection",
                    "severity": "Critical",
                    "ip": log.get("ip", "unknown"),
                    "description": (
                        f"SQL injection pattern detected from {log.get('ip', 'unknown')}: "
                        f"matched '{match_text}' in endpoint '{endpoint}'"
                    ),
                })
                break
    return alerts


def detect_port_scan(logs: list[dict], window_seconds: int = 60, threshold: int = 20) -> list[dict]:
    now = datetime.datetime.utcnow()
    window_start = now - datetime.timedelta(seconds=window_seconds)

    recent = [
        log for log in logs
        if _parse_ts(log.get("timestamp", "")) >= window_start
    ]

    by_ip = defaultdict(set)
    for log in recent:
        by_ip[log["ip"]].add(log.get("endpoint", ""))

    alerts = []
    for ip, endpoints in by_ip.items():
        if len(endpoints) >= threshold:
            alerts.append({
                "attack_type": "Port Scan",
                "severity": "Medium",
                "ip": ip,
                "description": (
                    f"{len(endpoints)} distinct endpoints requested by {ip} "
                    f"in the last {window_seconds} seconds — possible port scan"
                ),
            })
    return alerts


async def analyze_logs(db: AsyncSession) -> list[Alert]:
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(seconds=300)
    result = await db.execute(
        select(LogEntry).where(LogEntry.timestamp >= cutoff).order_by(LogEntry.timestamp.desc())
    )
    recent_logs = result.scalars().all()

    log_dicts = [
        {
            "ip": l.ip,
            "event_type": l.event_type,
            "endpoint": l.endpoint,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
        }
        for l in recent_logs
    ]

    raw_alerts = []
    raw_alerts.extend(detect_brute_force(log_dicts))
    raw_alerts.extend(detect_sql_injection(log_dicts))
    raw_alerts.extend(detect_port_scan(log_dicts))

    alert_objects = []
    for a in raw_alerts:
        alert = Alert(
            attack_type=a["attack_type"],
            severity=a["severity"],
            source_ip=a["ip"],
            description=a["description"],
            timestamp=datetime.datetime.utcnow(),
        )
        db.add(alert)
        alert_objects.append(alert)
    await db.commit()

    for a in alert_objects:
        await db.refresh(a)

    return alert_objects
