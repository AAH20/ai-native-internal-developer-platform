from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class ServiceRecord(Base):
    __tablename__ = "service_records"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_service_idempotency_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    owner: Mapped[str] = mapped_column(String(128), nullable=False)
    service_type: Mapped[str] = mapped_column(String(32), nullable=False)
    runtime: Mapped[str] = mapped_column(String(32), nullable=False)
    data_classification: Mapped[str] = mapped_column(String(32), nullable=False)
    availability_target: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_budget_usd: Mapped[float] = mapped_column(Float, nullable=False)
    region: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="accepted")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    plan_json: Mapped[str] = mapped_column(Text, nullable=False)
    receipt_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC), onupdate=lambda: dt.datetime.now(dt.UTC), nullable=False)
