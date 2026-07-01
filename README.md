# Cyber Range SOC Lite

A beginner-friendly SOC (Security Operations Center) dashboard simulator built with **FastAPI**, **React (Vite)**, **SQLite**, and **Docker**.

## Folder Structure

```
cyber-range-soc-lite/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── database.py          # SQLAlchemy engine & session
│   │   ├── models.py            # Alert DB model (SQLite)
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   └── routers/
│   │       ├── alerts.py        # CRUD for alerts
│   │       ├── attacks.py       # Simulate attack endpoints
│   │       └── dashboard.py     # Dashboard summary endpoint
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── main.jsx             # React entry point
│   │   ├── App.jsx              # Root component
│   │   ├── index.css            # Tailwind imports
│   │   ├── api/
│   │   │   └── client.js        # API client wrapper
│   │   └── components/
│   │       ├── Navbar.jsx       # Top nav + simulate buttons
│   │       ├── Dashboard.jsx    # Summary stat cards
│   │       └── AlertList.jsx    # Alert table with actions
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js           # Dev proxy to backend
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── Dockerfile
├── docker-compose.yml
└── .gitignore
```

## Setup Instructions

### Option 1 — Run locally (no Docker)

**Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload  # → http://localhost:8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev                    # → http://localhost:5173
```

The Vite dev server proxies `/api/*` to `http://localhost:8000`.

### Option 2 — Run with Docker
```bash
docker compose up --build
# Backend → http://localhost:8000
# Frontend → http://localhost:5173
```

## API Endpoints

| Method | Path                        | Description                  |
|--------|-----------------------------|------------------------------|
| GET    | `/api/health`               | Health check                 |
| GET    | `/api/dashboard/summary`    | Aggregated alert stats       |
| GET    | `/api/alerts/`              | List alerts (filter, paginate) |
| GET    | `/api/alerts/:id`           | Get single alert             |
| PUT    | `/api/alerts/:id`           | Acknowledge / resolve alert  |
| DELETE | `/api/alerts/:id`           | Delete an alert              |
| POST   | `/api/attacks/simulate`     | Generate one random alert    |
| POST   | `/api/attacks/batch-simulate?count=5` | Generate N alerts |

## What It Does

1. **Simulate Attacks** — Click the button to generate realistic security alerts (Port Scan, SQLi, DDoS, etc.) with random IPs and severity levels.
2. **Dashboard** — See live counts broken down by severity (Critical / High / Medium / Low).
3. **Alert Table** — Browse, acknowledge, resolve, or delete alerts.
4. **SQLite Persistence** — All data survives restarts in a local `soc_data.db` file.
