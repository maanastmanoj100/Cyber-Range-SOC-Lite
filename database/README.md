# Database

Schema documentation for Cyber Range SOC Lite.

## Tables

### alerts

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment ID |
| title | VARCHAR(255) | Alert title |
| description | TEXT | Detailed description |
| severity | VARCHAR(20) | Low / Medium / High / Critical |
| source_ip | VARCHAR(45) | Attacker IP address |
| destination_ip | VARCHAR(45) | Target IP address (nullable) |
| attack_type | VARCHAR(100) | Type of attack detected |
| timestamp | DATETIME | When the alert was created |
| is_acknowledged | BOOLEAN | Whether the alert has been acknowledged |
| is_resolved | BOOLEAN | Whether the alert has been resolved |

### log_entries

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment ID |
| ip | VARCHAR(45) | Source IP address |
| event_type | VARCHAR(100) | Type of event (login, request, etc.) |
| endpoint | VARCHAR(255) | Requested endpoint path |
| timestamp | DATETIME | When the log was recorded |

## Database Configuration

- **Local dev / Docker**: SQLite via SQLAlchemy (sync or async)
- **Vercel**: SQLite via aiosqlite (async, ephemeral storage)

The `DATABASE_URL` environment variable overrides the default SQLite path.

## ORM Models

Defined in:
- `api/models.py` — Consolidated API models (Vercel deployment)
- `backend/app/models.py` — SOC backend models (Docker deployment)
- `log-collector/app/models.py` — Log entry model (Docker deployment)
- `detection-engine/app/models.py` — Alert model (Docker deployment)

Models are managed via SQLAlchemy ORM. Tables are auto-created on application startup.
