# API Reference

All endpoints are prefixed with `/api` and served by the consolidated FastAPI application (`api/index.py`).

## Logs

### `GET /api/logs`

Returns log entries.

**Query Parameters:**
- `skip` (int, default 0) — Number of records to skip
- `limit` (int, default 100) — Max records to return
- `event_type` (string, optional) — Filter by event type

### `POST /api/logs`

Creates a log entry.

**Body:**
```json
{
  "ip": "192.168.1.1",
  "event_type": "login_attempt",
  "endpoint": "/login",
  "timestamp": "2026-07-01T12:00:00"
}
```

### `POST /api/logs/analyze`

Analyzes recent logs and generates alerts. Saves analysis results to the alerts table.

**Response:**
```json
{
  "alerts_generated": 3,
  "alerts": [...]
}
```

## Alerts

### `GET /api/alerts`

Returns all alerts.

**Query Parameters:**
- `skip` (int) — Pagination offset
- `limit` (int) — Page size
- `severity` (string, optional) — Filter by severity level

### `GET /api/alerts/{id}`

Returns a single alert by ID.

### `PUT /api/alerts/{id}`

Updates an alert (acknowledge/resolve).

**Body:**
```json
{
  "is_acknowledged": true,
  "is_resolved": false
}
```

### `DELETE /api/alerts/{id}`

Deletes an alert.

## Dashboard

### `GET /api/dashboard/summary`

Returns aggregate alert statistics.

## Attack Simulation

### `POST /api/attacks/simulate`

Creates a single simulated attack alert.

### `POST /api/attacks/batch-simulate?count=5`

Creates multiple simulated attack alerts at once.

## Explainer

### `POST /api/explain`

Generates a human-readable explanation for an alert.

**Body:**
```json
{
  "attack_type": "Brute Force Attack",
  "logs": [{"ip": "10.0.0.1", "event_type": "login_failed", "endpoint": "/login"}],
  "ip_address": "10.0.0.1"
}
```

## Health

### `GET /api/health`

Returns service health status.
