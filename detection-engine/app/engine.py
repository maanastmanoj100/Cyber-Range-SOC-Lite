"""
Rule-based detection engine.

Maintains a sliding window of logs in memory and runs rules on each
incoming batch.  Alerts are persisted via the caller.
"""

import re
import datetime
from collections import defaultdict
from typing import Callable

# ── SQL injection pattern ────────────────────────────────────────

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

# ── Detection rules ──────────────────────────────────────────────

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


# ── Orchestrator ─────────────────────────────────────────────────

def _parse_ts(ts: str | None) -> datetime.datetime:
    if ts:
        try:
            return datetime.datetime.fromisoformat(ts)
        except (ValueError, TypeError):
            pass
    return datetime.datetime.utcnow()


def analyze_logs(logs: list[dict], persist: Callable | None = None) -> list[dict]:
    all_alerts = []
    all_alerts.extend(detect_brute_force(logs))
    all_alerts.extend(detect_sql_injection(logs))
    all_alerts.extend(detect_port_scan(logs))

    if persist:
        for alert in all_alerts:
            persist(alert)

    return all_alerts
