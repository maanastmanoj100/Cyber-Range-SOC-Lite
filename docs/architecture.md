# Architecture

## System Design

Cyber Range SOC Lite follows a modular pipeline architecture:

1. **Attack Generation** — The attacker/simulator sends malicious traffic to the vulnerable target application
2. **Log Ingestion** — The target app forwards request metadata to the log collector
3. **Detection** — The detection engine analyzes log streams using rule-based heuristics
4. **Explanation** — Generated alerts are enriched with human-readable explanations
5. **Visualization** — The SOC dashboard displays alerts, logs, and statistics in real-time

## Data Flow

```
Attacker ──HTTP──▶ Vulnerable App ──POST /log──▶ Log Collector ──GET /logs──▶ SOC Frontend
                                                      │
                                                      ▼
                                              Detection Engine
                                                      │
                                                      ▼
                                                 Explainer
                                                      │
                                                      ▼
                                              SOC Dashboard
```

## Deployment Architectures

### Docker Compose (multi-service)

Each component runs in its own container with a shared Docker network. Services are independently scalable.

### Vercel (serverless)

All backend logic is consolidated into a single FastAPI application in `api/`. The frontend is served as static files. Both are deployed via Vercel's serverless platform.

### Local Development

Each Python service can be run directly with `uvicorn` for development and debugging.

## Technology Stack

| Component | Technology |
|---|---|
| Backend API | Python / FastAPI |
| Database | SQLite (SQLAlchemy ORM) |
| Frontend | React / Vite / Tailwind CSS |
| Charts | Chart.js / react-chartjs-2 |
| Container | Docker / Docker Compose |
| Serverless | Vercel (Python + static) |
