from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def evaluate(value: dict) -> dict:
    setup_hours = value["new_services_per_year"] * (value["baseline_setup_hours_per_service"] - value["target_setup_hours_per_service"])
    recovered_capacity = setup_hours * value["loaded_engineering_hour_usd"]
    waste = value["ephemeral_environments"] * value["abandoned_environment_pct"] * value["monthly_cost_per_environment_usd"] * 12
    ticket_hours = (value["baseline_platform_tickets_per_month"] - value["target_platform_tickets_per_month"]) * value["minutes_per_ticket"] / 60 * 12
    ticket_capacity = ticket_hours * value["loaded_engineering_hour_usd"]
    report = {
        "schema_version":"launchrail-economics/v1",
        "scenario":value["scenario"],
        "evidence_level":"modeled-business-case",
        "annual_platform_operating_cost_usd":value["annual_platform_operating_cost_usd"],
        "modeled_setup_capacity_recovered_hours":round(setup_hours,2),
        "modeled_setup_capacity_value_usd":round(recovered_capacity,2),
        "modeled_environment_waste_avoided_usd":round(waste,2),
        "modeled_ticket_capacity_recovered_hours":round(ticket_hours,2),
        "modeled_ticket_capacity_value_usd":round(ticket_capacity,2),
        "modeled_first_order_value_usd":round(recovered_capacity+waste+ticket_capacity,2),
        "modeled_first_order_net_value_usd":round(recovered_capacity+waste+ticket_capacity-value["annual_platform_operating_cost_usd"],2),
        "claim_boundary":[
            "Recovered engineering capacity is not automatically a cash saving",
            "Environment waste becomes savings only after resources are actually deleted and invoices reconcile",
            "Revenue acceleration, incident reduction and developer satisfaction are excluded until measured",
            "All figures are configurable synthetic assumptions"
        ]
    }
    report["receipt_sha256"]=hashlib.sha256(json.dumps(report,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return report


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("scenario",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    report=evaluate(json.loads(args.scenario.read_text()))
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/"platform-economics.json").write_text(json.dumps(report,indent=2)+"\n")
    lines=[f"# {report['scenario']}","",f"**Receipt:** `{report['receipt_sha256']}`","","## Modeled annual economics",""]
    for key,val in report.items():
        if key.startswith("modeled_") or key=="annual_platform_operating_cost_usd": lines.append(f"- `{key}`: `{val}`")
    lines.extend(["","## Claim boundary",""]+[f"- {item}" for item in report["claim_boundary"]])
    (args.output/"platform-economics.md").write_text("\n".join(lines)+"\n")
    print(report["receipt_sha256"])


if __name__=="__main__":main()
