import json
import datetime
import os
import uuid
from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File
from sqlalchemy import text
from sqlalchemy.orm import Session
import httpx

from .database import engine, Base, get_db
from .models import User, StoredData, LogEntry
from .schemas import LoginRequest, LoginResponse, LogEntryCreate, LogEntryResponse
from .seed import seed_database

# ── App initialisation ──────────────────────────────────────

LOG_COLLECTOR_URL = os.getenv("LOG_COLLECTOR_URL", "http://log-collector:8000/log")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")

Base.metadata.create_all(bind=engine)
seed_database()

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Vulnerable App",
    description="Intentionally vulnerable web application for SOC training. DO NOT expose to the internet.",
    version="1.0.0",
)

# ── Logging middleware ───────────────────────────────────────

@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    endpoint = request.url.path
    timestamp = datetime.datetime.utcnow().isoformat()

    if endpoint == "/log":
        return await call_next(request)

    if "/login" in endpoint:
        event_type = "login_attempt"
    elif "/upload" in endpoint:
        event_type = "file_upload"
    elif "/api/data" in endpoint:
        event_type = "api_request"
    else:
        event_type = "http_request"

    log_entry = {
        "ip": ip,
        "event_type": event_type,
        "endpoint": endpoint,
        "timestamp": timestamp,
    }

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                LOG_COLLECTOR_URL,
                json=log_entry,
                timeout=2.0,
            )
    except Exception:
        pass

    response = await call_next(request)
    return response

# ── /log endpoint ────────────────────────────────────────────

@app.post("/log")
def create_log(entry: LogEntryCreate, db: Session = Depends(get_db)):
    log = LogEntry(
        ip=entry.ip,
        endpoint=entry.endpoint,
        timestamp=datetime.datetime.fromisoformat(entry.timestamp),
        payload=entry.payload,
    )
    db.add(log)
    db.commit()
    return {"status": "logged"}


@app.get("/log", response_model=list[LogEntryResponse])
def list_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return (
        db.query(LogEntry)
        .order_by(LogEntry.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

# ── Vulnerable /login ────────────────────────────────────────
# Issues: no rate-limit, user enumeration, plaintext passwords,
#         returns password in response body

@app.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail=f"User '{body.username}' not found",
        )

    if user.password != body.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid password",
        )

    return LoginResponse(
        message="Login successful",
        token=str(uuid.uuid4()),
        password=user.password,
    )

# ── Vulnerable /upload ───────────────────────────────────────
# Issues: no file-type validation, no size limit, path traversal possible

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {
        "message": "File uploaded",
        "filename": file.filename,
        "size_bytes": len(content),
        "path": file_path,
    }

# ── Vulnerable /api/data ─────────────────────────────────────
# Issues: no authentication, no authorisation, returns all data,
#         SQL injection in query parameter

@app.get("/api/data")
def get_data(user_id: str | None = None, db: Session = Depends(get_db)):
    if user_id:
        query = f"SELECT id, owner, secret, note FROM stored_data WHERE owner = '{user_id}'"
        result = db.execute(text(query)).fetchall()
        return [
            {"id": row[0], "owner": row[1], "secret": row[2], "note": row[3]}
            for row in result
        ]

    return db.query(StoredData).all()


@app.get("/api/data/{data_id}")
def get_single_item(data_id: int, db: Session = Depends(get_db)):
    item = db.query(StoredData).filter(StoredData.id == data_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item

# ── Health / Root ────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "healthy", "service": "vulnerable-app"}


@app.get("/")
def root():
    return {
        "app": "Vulnerable App",
        "endpoints": ["/login", "/upload", "/api/data", "/log"],
        "status": "healthy",
    }
