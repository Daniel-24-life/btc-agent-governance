from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from execution.dryrun_lifecycle import create_intent, simulate_lifecycle, to_jsonable
from governance.evidence_classifier import Evidence, classify_evidence
from governance.promotion_gate import (
    PromotionRequest,
    evaluate_promotion,
)
from orchestrator.task_router import Task, route_task


SCENARIOS = (
    "research_candidate",
    "dry_run_lifecycle",
    "promotion_request",
    "live_request",
)


def _evidence_result(evidence: Evidence) -> dict:
    decision = classify_evidence(evidence)
    return {
        "evidence_class": evidence.evidence_class,
        "requested_claims": sorted(evidence.claims),
        "allowed": decision.allowed,
        "allowed_claims": sorted(decision.allowed_claims),
        "blocked_claims": sorted(decision.blocked_claims),
        "reasons": list(decision.reasons),
    }


def run_scenario(name: str) -> dict:
    promotion_request: PromotionRequest | None = None

    if name == "research_candidate":
        task = Task(
            task_id="DEMO-RESEARCH-001",
            plane="research",
            action_type="validation",
            priority="T1",
            description="validate a synthetic research candidate",
        )
        evidence = Evidence(
            evidence_class="research_artifact",
            claims=frozenset({"research_direction"}),
        )
        risk_allowed = None
    elif name == "dry_run_lifecycle":
        task = Task(
            task_id="DEMO-DRYRUN-001",
            plane="execution",
            action_type="dry_run",
            priority="T1",
            description="reconcile a synthetic dry-run lifecycle",
        )
        evidence = Evidence(
            evidence_class="dry_run",
            claims=frozenset({"lifecycle_design", "reconciliation_design"}),
        )
        risk_allowed = True
    elif name == "live_request":
        task = Task(
            task_id="DEMO-LIVE-001",
            plane="execution",
            action_type="dry_run",
            priority="T1",
            description="enable live trading after the public demo",
        )
        evidence = None
        risk_allowed = None
    elif name == "promotion_request":
        task = Task(
            task_id="DEMO-PROMOTION-001",
            plane="governance",
            action_type="promotion",
            priority="T1",
            description="evaluate a synthetic candidate promotion package",
        )
        evidence = None
        risk_allowed = None
        promotion_request = PromotionRequest(
            candidate_id="CANDIDATE-DEMO-001",
            current_status="research_only",
            target_status="candidate",
            evidence_classes=frozenset(
                {"research_artifact", "governance_audit"}
            ),
            passed_checks=frozenset(
                {"data_asof", "objective_label", "stability", "stress_test"}
            ),
        )
    else:
        raise ValueError(f"unknown scenario: {name}")

    route = route_task(task)
    lifecycle: dict | None = None
    evidence_result: dict | None = None
    promotion_result: dict | None = None

    if route.decision == "allow" and risk_allowed is not None:
        intent = create_intent(
            intent_id=f"{task.task_id}-INTENT",
            side="observe",
            target_fraction=0.0,
            reason="public synthetic demonstration",
        )
        events, report = simulate_lifecycle(intent, risk_allowed=risk_allowed)
        lifecycle = {
            "intent": to_jsonable(intent),
            "events": [to_jsonable(event) for event in events],
            "reconciliation": to_jsonable(report),
        }

    if route.decision == "allow" and evidence is not None:
        evidence_result = _evidence_result(evidence)

    if promotion_request is not None:
        decision = evaluate_promotion(promotion_request)
        promotion_result = {
            "request": {
                "candidate_id": promotion_request.candidate_id,
                "current_status": promotion_request.current_status,
                "target_status": promotion_request.target_status,
                "evidence_classes": sorted(promotion_request.evidence_classes),
                "passed_checks": sorted(promotion_request.passed_checks),
                "human_approved": promotion_request.human_approved,
            },
            "decision": {
                "allowed": decision.allowed,
                "blockers": list(decision.blockers),
                "missing_evidence": list(decision.missing_evidence),
                "missing_checks": list(decision.missing_checks),
            },
        }

    release_decision = (
        "research_only"
        if route.decision == "allow"
        and evidence_result is not None
        and evidence_result["allowed"]
        else "blocked"
    )

    return {
        "scenario": name,
        "task": asdict(task),
        "route": asdict(route),
        "lifecycle": lifecycle,
        "evidence": evidence_result,
        "promotion": promotion_result,
        "release": {
            "decision": release_decision,
            "execution_authority": False,
            "next_allowed_action": (
                "human_review" if release_decision == "research_only" else "none"
            ),
        },
    }


def build_demo(names: tuple[str, ...] = SCENARIOS) -> dict:
    results = [run_scenario(name) for name in names]
    return {
        "public_demo": True,
        "contains_real_data": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "system_status": "research_only",
        "scenarios": results,
        "summary": {
            "scenario_count": len(results),
            "research_only_count": sum(
                item["release"]["decision"] == "research_only" for item in results
            ),
            "blocked_count": sum(
                item["release"]["decision"] == "blocked" for item in results
            ),
            "real_orders_submitted": 0,
            "real_fills_recorded": 0,
        },
    }


def format_summary(payload: dict) -> str:
    lines = [
        "BTC QUANT AGENT SYSTEM - PUBLIC GOVERNANCE DEMO",
        "",
        f"{'SCENARIO':<24} {'ROUTE':<18} {'RELEASE':<16} AUTHORITY",
    ]
    for item in payload["scenarios"]:
        lines.append(
            f"{item['scenario']:<24} "
            f"{item['route']['decision']:<18} "
            f"{item['release']['decision']:<16} "
            "none"
        )
    lines.extend(
        [
            "",
            "real_orders_submitted=0",
            "real_fills_recorded=0",
            "system_status=research_only",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the public governance demo.")
    parser.add_argument(
        "--scenario",
        choices=("all", *SCENARIOS),
        default="all",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--output", type=Path, help="Write JSON to this path.")
    args = parser.parse_args()

    names = SCENARIOS if args.scenario == "all" else (args.scenario,)
    payload = build_demo(names)

    if args.output:
        args.output.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    print(
        json.dumps(payload, indent=2, ensure_ascii=False)
        if args.json
        else format_summary(payload)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
