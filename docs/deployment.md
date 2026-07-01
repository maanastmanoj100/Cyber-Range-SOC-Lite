# Deployment Guide

## Docker Compose (full stack)

```bash
# Start core services (target, log-collector, attacker)
docker compose up -d

# Start full stack with SOC dashboard
docker compose --profile dashboard up -d

# Run attack simulation
docker compose run attacker
```

## Vercel (serverless)

1. Push the repository to GitHub
2. Import the project in the Vercel dashboard
3. Vercel auto-detects the Python API (`api/`) and frontend (`frontend/`)
4. No environment variables required — the app uses SQLite by default
5. Deploy

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 18+
- (Optional) Docker

### Backend

```bash
cd api
pip install -r ../requirements.txt
uvicorn api.index:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the Vite dev server proxies `/api` requests to the backend.
