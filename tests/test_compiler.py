from platform_api.compiler import compile_plan
from platform_api.schemas import ServiceIntent


def intent(**overrides):
    value = {
        "name": "invoice-reconciliation",
        "owner": "finance-platform",
        "service_type": "event-driven",
        "runtime": "python",
        "data_classification": "confidential",
        "availability_target": 99.95,
        "monthly_budget_usd": 1200,
        "region": "westeurope",
    }
    value.update(overrides)
    return ServiceIntent(**value)


def test_compiler_selects_event_driven_golden_path():
    plan, receipt = compile_plan(intent())
    assert plan.golden_path == "event-driven"
    assert "transactional-outbox" in plan.infrastructure
    assert plan.economics["within_budget"] is True
    assert len(receipt) == 64


def test_receipt_is_deterministic():
    assert compile_plan(intent())[1] == compile_plan(intent())[1]


def test_high_reliability_and_classification_affect_cost():
    protected = compile_plan(intent())[0].economics["estimated_monthly_platform_cost_usd"]
    basic = compile_plan(intent(availability_target=99.0, data_classification="public"))[0].economics["estimated_monthly_platform_cost_usd"]
    assert protected > basic


def test_compiler_never_auto_applies():
    assert compile_plan(intent())[0].auto_apply is False
