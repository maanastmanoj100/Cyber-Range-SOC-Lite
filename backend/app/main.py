from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import alerts, attacks, dashboard
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cyber Range SOC Lite",
    description="A lightweight SOC dashboard for simulated cyber attack detection and alert management.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts.router)
app.include_router(attacks.router)
app.include_router(dashboard.router)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "Cyber Range SOC Lite"}
