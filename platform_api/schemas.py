from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ServiceType = Literal["rest-api", "event-driven", "ai-agent", "data-product"]
Runtime = Literal["python", "typescript", "go", "dotnet"]
Classification = Literal["public", "internal", "confidential", "restricted"]


class ServiceIntent(BaseModel):
    name: str = Field(pattern=r"^[a-z][a-z0-9-]{2,62}$")
    owner: str = Field(min_length=3, max_length=128)
    service_type: ServiceType
    runtime: Runtime
    data_classification: Classification
    availability_target: float = Field(ge=99.0, le=99.999)
    monthly_budget_usd: float = Field(gt=0, le=1_000_000)
    region: str = Field(min_length=3, max_length=64)


class PlatformPlan(BaseModel):
    schema_version: str
    golden_path: str
    repository: dict
    infrastructure: list[str]
    delivery: list[str]
    observability: list[str]
    production_gates: list[str]
    economics: dict
    auto_apply: bool = False


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    idempotency_key: str
    name: str
    owner: str
    service_type: str
    runtime: str
    data_classification: str
    availability_target: float
    monthly_budget_usd: float
    region: str
    status: str
    version: int
    receipt_sha256: str
    created_at: dt.datetime
    updated_at: dt.datetime


class Actor(BaseModel):
    subject: str
    roles: tuple[str, ...]
