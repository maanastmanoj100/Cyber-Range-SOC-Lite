# Attacker

Attack simulation module for Cyber Range SOC Lite.

Generates realistic attack traffic against the vulnerable target application to populate the SOC dashboard with security events.

## Usage

```bash
# Run all attack types
python simulator.py --target http://localhost:8001 --attack all

# Run a specific attack
python simulator.py --target http://localhost:8001 --attack brute

# With Docker
docker build -t attacker .
docker run attacker --target http://target-app:8000 --attack all
```

## Attack Types

- `brute` — Brute force login attempts
- `sqli` — SQL injection payloads
- `flood` — HTTP flood / DoS simulation
- `all` — All of the above

## Implementation

Core simulator logic lives in `../attack_simulator/simulator.py`. This directory provides a standalone entry point and Dockerfile for containerized use.
