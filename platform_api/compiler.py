from __future__ import annotations

import hashlib
import json

from .schemas import PlatformPlan, ServiceIntent


GOLDEN_PATHS = {
    "rest-api": ["container-app", "postgresql", "openapi"],
    "event-driven": ["container-app", "service-bus", "asyncapi", "transactional-outbox"],
    "ai-agent": ["container-app", "foundry-contract", "mcp", "evaluation-gate"],
    "data-product": ["event-stream", "lakehouse", "data-contract", "freshness-slo"],
}


def compile_plan(intent: ServiceIntent) -> tuple[PlatformPlan, str]:
    components = GOLDEN_PATHS[intent.service_type]
    base_platform_cost = {"rest-api": 180.0, "event-driven": 260.0, "ai-agent": 420.0, "data-product": 340.0}[intent.service_type]
    reliability_factor = 1.35 if intent.availability_target >= 99.95 else 1.0
    classification_factor = 1.25 if intent.data_classification in {"confidential", "restricted"} else 1.0
    estimated_cost = round(base_platform_cost * reliability_factor * classification_factor, 2)
    plan = PlatformPlan(
        schema_version="launchrail/v1",
        golden_path=intent.service_type,
        repository={"provider": "github", "name": intent.name, "owners": [intent.owner], "template_version": "v1"},
        infrastructure=components + ["managed-identity", "private-evidence-storage", "budget-alert"],
        delivery=["pull-request", "build", "test", "sbom", "ephemeral-environment", "progressive-delivery", "rollback"],
        observability=["opentelemetry", "logs", "metrics", "traces", "slo", "cost-allocation"],
        production_gates=["contract-tests", "security-scan", "cost-within-budget", "slo-defined", "rollback-tested", "human-approval"],
        economics={
            "estimated_monthly_platform_cost_usd": estimated_cost,
            "monthly_budget_usd": intent.monthly_budget_usd,
            "budget_headroom_usd": round(intent.monthly_budget_usd - estimated_cost, 2),
            "within_budget": estimated_cost <= intent.monthly_budget_usd,
            "claim": "modeled estimate; provider quotation and deployed measurement required",
        },
        auto_apply=False,
    )
    canonical = json.dumps(plan.model_dump(), sort_keys=True, separators=(",", ":"))
    return plan, hashlib.sha256(canonical.encode()).hexdigest()
