from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from platform_api.database import Base
from platform_api.schemas import ServiceIntent
from platform_api.service import create_service


def intent(name="invoice-reconciliation", budget=1200):
    return ServiceIntent(name=name, owner="finance-platform", service_type="event-driven", runtime="python", data_classification="confidential", availability_target=99.95, monthly_budget_usd=budget, region="westeurope")


def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_idempotency_returns_same_service():
    db = session()
    first = create_service(db, intent(), "request-00000001")
    second = create_service(db, intent(), "request-00000001")
    assert first.id == second.id


def test_budget_failure_does_not_persist():
    db = session()
    try:
        create_service(db, intent(name="underfunded", budget=100), "request-00000002")
    except ValueError as exc:
        assert "exceeds monthly budget" in str(exc)
    else:
        raise AssertionError("budget gate did not fail")
