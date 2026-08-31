from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .compiler import compile_plan
from .models import ServiceRecord
from .schemas import ServiceIntent


def create_service(db: Session, intent: ServiceIntent, idempotency_key: str) -> ServiceRecord:
    existing = db.scalar(select(ServiceRecord).where(ServiceRecord.idempotency_key == idempotency_key))
    if existing:
        return existing
    plan, receipt = compile_plan(intent)
    if not plan.economics["within_budget"]:
        raise ValueError("compiled golden path exceeds monthly budget")
    record = ServiceRecord(
        idempotency_key=idempotency_key,
        name=intent.name,
        owner=intent.owner,
        service_type=intent.service_type,
        runtime=intent.runtime,
        data_classification=intent.data_classification,
        availability_target=intent.availability_target,
        monthly_budget_usd=intent.monthly_budget_usd,
        region=intent.region,
        status="planned",
        plan_json=json.dumps(plan.model_dump(), sort_keys=True),
        receipt_sha256=receipt,
    )
    db.add(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(select(ServiceRecord).where(ServiceRecord.idempotency_key == idempotency_key))
        if existing:
            return existing
        raise
    db.refresh(record)
    return record
