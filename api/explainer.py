from collections import Counter
import re


def _count_logs(logs: list[dict]) -> int:
    return len(logs)


def _distinct_endpoints(logs: list[dict]) -> list[str]:
    return list({log.get("endpoint", "") for log in logs})


def _most_common_event(logs: list[dict]) -> str | None:
    events = [log.get("event_type", "") for log in logs if log.get("event_type")]
    if not events:
        return None
    return Counter(events).most_common(1)[0][0]


def _failed_login_count(logs: list[dict]) -> int:
    return sum(
        1 for log in logs
        if log.get("event_type", "").lower() in ("login_failed", "failed_login", "401")
        or "/login" in log.get("endpoint", "")
    )


def _extract_sqli_patterns(logs: list[dict]) -> set[str]:
    patterns = set()
    sqli_signatures = [
        (re.compile(r"'?\s*OR\s+['\"]?1['\"]?\s*=\s*['\"]?1", re.I), "' OR 1=1"),
        (re.compile(r"OR\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+", re.I), "OR <digit>=<digit>"),
        (re.compile(r"DROP\s+TABLE", re.I), "DROP TABLE"),
        (re.compile(r"UNION\s+SELECT", re.I), "UNION SELECT"),
        (re.compile(r"'\s*--", re.I), "SQL comment injection"),
        (re.compile(r"'\s*#", re.I), "SQL comment injection"),
        (re.compile(r"SLEEP\s*\(", re.I), "SLEEP()"),
        (re.compile(r"WAITFOR\s+DELAY", re.I), "WAITFOR DELAY"),
        (re.compile(r"'\s*;\s*", re.I), "SQL statement chaining"),
    ]
    for log in logs:
        endpoint = log.get("endpoint", "")
        event = log.get("event_type", "")
        combined = f"{endpoint} {event}"
        for regex, label in sqli_signatures:
            if regex.search(combined):
                patterns.add(label)
    return patterns


def _explain_brute_force(ip: str, logs: list[dict]) -> dict:
    count = _failed_login_count(logs)
    endpoints = _distinct_endpoints(logs)
    ep_list = ", ".join(endpoints[:5])

    explanation = (
        f"Multiple failed login attempts detected from IP {ip}. "
        f"A total of {count} failed authentication requests were observed "
        f"targeting {len(endpoints)} endpoint(s): {ep_list}. "
        f"This pattern is characteristic of a brute-force or credential-stuffing attack "
        f"where an attacker systematically tries common usernames and passwords."
    )

    return {
        "explanation": explanation,
        "risk_level": "High",
        "recommended_action": (
            f"Immediately block IP {ip} at the firewall or WAF. "
            f"Enforce account lockout after 5 failed attempts. "
            f"Enable multi-factor authentication (MFA) on all accounts. "
            f"Review authentication logs for any successful logins from this IP."
        ),
    }


def _explain_sql_injection(ip: str, logs: list[dict]) -> dict:
    count = _count_logs(logs)
    patterns_found = _extract_sqli_patterns(logs)
    patterns_str = ", ".join(sorted(patterns_found)) if patterns_found else "SQL control characters"
    endpoints = _distinct_endpoints(logs)
    ep_str = ", ".join(endpoints[:3])

    explanation = (
        f"SQL injection attempt detected from IP {ip}. "
        f"The request contained malicious SQL patterns ({patterns_str}) "
        f"in {count} request(s) to endpoint(s): {ep_str}. "
        f"An attacker is attempting to manipulate database queries "
        f"to bypass authentication, extract data, or execute arbitrary commands."
    )

    return {
        "explanation": explanation,
        "risk_level": "Critical",
        "recommended_action": (
            f"Block IP {ip} immediately. "
            f"Review all database queries and replace dynamic string concatenation "
            f"with parameterised queries or prepared statements. "
            f"Deploy a Web Application Firewall (WAF) with SQL injection detection rules. "
            f"Audit the affected endpoint(s) for potential data exfiltration."
        ),
    }


def _explain_port_scan(ip: str, logs: list[dict]) -> dict:
    count = _count_logs(logs)
    endpoints = _distinct_endpoints(logs)
    ep_str = ", ".join(endpoints[:8])

    explanation = (
        f"Possible port scanning activity detected from IP {ip}. "
        f"The source accessed {count} different resources across "
        f"{len(endpoints)} distinct endpoint(s) in a short time window: {ep_str}. "
        f"Reconnaissance tools like Nmap or masscan often produce this pattern "
        f"as the attacker probes for open ports and vulnerable services."
    )

    return {
        "explanation": explanation,
        "risk_level": "Medium",
        "recommended_action": (
            f"Add IP {ip} to a blocklist or rate-limit aggressively. "
            f"Review firewall logs to confirm whether the scan originated externally. "
            f"Ensure no unnecessary ports or services are exposed. "
            f"Consider deploying an IDS/IPS with port-scan detection signatures."
        ),
    }


def _explain_malware(ip: str, logs: list[dict]) -> dict:
    endpoints = _distinct_endpoints(logs)
    ep_str = ", ".join(endpoints[:3])

    explanation = (
        f"Suspicious file activity detected from IP {ip} on endpoint(s): {ep_str}. "
        f"The uploaded file(s) may contain malicious code. "
        f"Malware infections often enter via phishing attachments, "
        f"drive-by downloads, or vulnerable file upload forms."
    )

    return {
        "explanation": explanation,
        "risk_level": "High",
        "recommended_action": (
            f"Isolate the affected system immediately. "
            f"Scan uploaded files in a sandbox environment. "
            f"Restrict file upload to allowed extensions only. "
            f"Run anti-malware scans on the target host."
        ),
    }


def _explain_generic(attack_type: str, ip: str, logs: list[dict]) -> dict:
    count = _count_logs(logs)
    event_type = logs[0].get("event_type", "unknown") if logs else "unknown"

    explanation = (
        f"Alert of type '{attack_type}' triggered from IP {ip}. "
        f"{count} log entr(ies) observed with event type '{event_type}'. "
        f"The activity deviates from normal baseline behaviour and requires investigation."
    )

    return {
        "explanation": explanation,
        "risk_level": "Low",
        "recommended_action": (
            f"Review the associated logs for context. "
            f"Verify whether the IP {ip} is a known internal or external address. "
            f"Update detection rules if this is a false positive."
        ),
    }


EXPLAINERS = {
    "Brute Force Attack": _explain_brute_force,
    "SQL Injection": _explain_sql_injection,
    "Port Scan": _explain_port_scan,
    "Malware": _explain_malware,
}


def explain(attack_type: str, logs: list[dict], ip_address: str) -> dict:
    explainer_fn = EXPLAINERS.get(attack_type, _explain_generic)
    result = explainer_fn(ip_address, logs)

    return {
        "attack_type": attack_type,
        "explanation": result["explanation"],
        "risk_level": result["risk_level"],
        "recommended_action": result["recommended_action"],
    }
