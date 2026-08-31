from __future__ import annotations

from contextlib import asynccontextmanager
import json

from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .auth import current_actor
from .config import get_settings
from .database import Base, engine, get_db
from .models import ServiceRecord
from .schemas import Actor, PlatformPlan, ServiceIntent, ServiceResponse
from .service import create_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    if get_settings().auto_create_schema:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="LaunchRail Platform API", version="0.1.0", lifespan=lifespan)
requests_total = Counter("launchrail_service_requests_total", "Service-intent requests", ["outcome"])


@app.get("/health/live")
def live() -> dict:
    return {"status": "live"}


@app.get("/health/ready")
def ready(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "ready"}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service_endpoint(
    intent: ServiceIntent,
    idempotency_key: str = Header(min_length=8, max_length=128, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    actor: Actor = Depends(current_actor),
) -> ServiceRecord:
    del actor
    try:
        record = create_service(db, intent, idempotency_key)
        requests_total.labels(outcome="accepted").inc()
        return record
    except ValueError as exc:
        requests_total.labels(outcome="rejected").inc()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@app.get("/v1/services", response_model=list[ServiceResponse])
def list_services(db: Session = Depends(get_db), actor: Actor = Depends(current_actor)) -> list[ServiceRecord]:
    del actor
    return list(db.scalars(select(ServiceRecord).order_by(ServiceRecord.created_at.desc())))


@app.get("/v1/services/{service_id}/plan", response_model=PlatformPlan)
def get_plan(service_id: str, db: Session = Depends(get_db), actor: Actor = Depends(current_actor)) -> PlatformPlan:
    del actor
    record = db.get(ServiceRecord, service_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    return PlatformPlan.model_validate(json.loads(record.plan_json))
