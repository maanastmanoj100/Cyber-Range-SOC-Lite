# Cyber Range SOC Lite

A lightweight Security Operations Center (SOC) training environment for learning detection, analysis, and response to cyber attacks.

## Architecture Overview

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Attacker    │────▶│ Vulnerable   │────▶│  Log Collector   │
│  (simulator) │     │  App (target)│     │  (ingestion)     │
└──────────────┘     └──────────────┘     └────────┬─────────┘
                                                   │
                                                   ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Explainer   │◀────│  Detection   │◀────│  Log Stream      │
│  (AI rules)  │     │  Engine      │     │                  │
└──────┬───────┘     └──────────────┘     └──────────────────┘
       │
       ▼
┌──────────────┐
│  SOC Dashboard│
│  (React UI)  │
└──────────────┘
```

## Deployment Modes

- **Docker Compose** — Full stack with all services containerized
- **Vercel** — Consolidated API (`api/`) + frontend, serverless-ready
- **Local Dev** — Run each service manually for development

## Directory Layout

| Directory | Purpose |
|---|---|
| `api/` | Consolidated FastAPI backend (Vercel deployment) |
| `attacker/` | Attack simulation entry point |
| `attack-simulator/` | Core attack simulator logic |
| `backend/` | SOC dashboard API (Docker deployment) |
| `database/` | Database schemas and documentation |
| `detection-engine/` | Rule-based detection service |
| `docs/` | Project documentation |
| `explainer/` | Alert explanation service |
| `frontend/` | React SOC dashboard UI |
| `log-collector/` | Centralised log ingestion service |
| `logs/` | Runtime log output directory |
| `vulnerable-app/` | Intentionally vulnerable target application |
