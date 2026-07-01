from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import ExplainRequest, ExplainResponse
from .engine import explain

app = FastAPI(
    title="AI Explanation Module",
    description="Rule-based cybersecurity alert explainer for Cyber Range SOC Lite.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/explain", response_model=ExplainResponse)
def explain_endpoint(body: ExplainRequest):
    return explain(
        attack_type=body.attack_type,
        logs=[log.model_dump() for log in body.logs],
        ip_address=body.ip_address,
    )


@app.get("/health")
def health():
    return {"status": "healthy", "service": "AI Explanation Module"}
