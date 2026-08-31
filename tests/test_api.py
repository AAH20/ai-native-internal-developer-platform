from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from platform_api.database import Base, get_db
from platform_api.main import app


engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(engine)


def override_db():
    with Session(engine) as db:
        yield db


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


PAYLOAD = {
    "name": "customer-api",
    "owner": "customer-platform",
    "service_type": "rest-api",
    "runtime": "python",
    "data_classification": "internal",
    "availability_target": 99.9,
    "monthly_budget_usd": 800,
    "region": "westeurope",
}


def test_health_and_readiness():
    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").status_code == 200


def test_create_list_and_plan():
    response = client.post("/v1/services", headers={"Idempotency-Key": "customer-api-request-1"}, json=PAYLOAD)
    assert response.status_code == 201
    service = response.json()
    assert service["status"] == "planned"
    assert len(service["receipt_sha256"]) == 64
    assert client.get("/v1/services").status_code == 200
    plan = client.get(f"/v1/services/{service['id']}/plan")
    assert plan.status_code == 200
    assert plan.json()["auto_apply"] is False


def test_idempotent_api_request():
    first = client.post("/v1/services", headers={"Idempotency-Key": "customer-api-request-2"}, json={**PAYLOAD, "name": "customer-api-v2"})
    second = client.post("/v1/services", headers={"Idempotency-Key": "customer-api-request-2"}, json={**PAYLOAD, "name": "ignored-replay"})
    assert first.json()["id"] == second.json()["id"]
