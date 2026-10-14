from __future__ import annotations

from dataclasses import dataclass


STATUS_ORDER = {
    "research_only": 0,
    "candidate": 1,
    "paper_shadow": 2,
    "paper_trade": 3,
    "small_live": 4,
    "scaled_live": 5,
}

PUBLIC_PROMOTION_CEILING = "research_only"

REQUIRED_EVIDENCE = {
    "candidate": {"research_artifact", "governance_audit"},
    "paper_shadow": {"research_artifact", "governance_audit", "dry_run"},
    "paper_trade": {"governance_audit", "dry_run", "human_approved"},
    "small_live": {"governance_audit", "human_approved"},
    "scaled_live": {"governance_audit", "human_approved"},
}

REQUIRED_CHECKS = {
    "candidate": {"data_asof", "objective_label", "stability", "stress_test"},
    "paper_shadow": {"execution_scope", "risk_state", "reconciliation"},
    "paper_trade": {"execution_fill", "risk_state", "rollback"},
    "small_live": {"execution_fill", "risk_state", "rollback", "continuity"},
    "scaled_live": {"execution_fill", "risk_state", "rollback", "continuity"},
}

HUMAN_APPROVAL_TARGETS = {"paper_trade", "small_live", "scaled_live"}


@dataclass(frozen=True)
class PromotionRequest:
    candidate_id: str
    current_status: str
    target_status: str
    evidence_classes: frozenset[str]
    passed_checks: frozenset[str]
    human_approved: bool = False


@dataclass(frozen=True)
class PromotionDecision:
    allowed: bool
    current_status: str
    target_status: str
    blockers: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    missing_checks: tuple[str, ...]


def evaluate_promotion(request: PromotionRequest) -> PromotionDecision:
    """Evaluate a status change without granting execution authority."""
    if request.current_status not in STATUS_ORDER:
        return PromotionDecision(
            False,
            request.current_status,
            request.target_status,
            ("unknown_current_status",),
            (),
            (),
        )
    if request.target_status not in STATUS_ORDER:
        return PromotionDecision(
            False,
            request.current_status,
            request.target_status,
            ("unknown_target_status",),
            (),
            (),
        )

    current_rank = STATUS_ORDER[request.current_status]
    target_rank = STATUS_ORDER[request.target_status]
    blockers: list[str] = []

    if target_rank < current_rank:
        blockers.append("status_regression_requires_separate_review")
    if target_rank > current_rank + 1:
        blockers.append("stage_skip_forbidden")

    required_evidence = REQUIRED_EVIDENCE.get(request.target_status, set())
    missing_evidence = tuple(sorted(required_evidence - request.evidence_classes))
    if missing_evidence:
        blockers.append("required_evidence_missing")

    required_checks = REQUIRED_CHECKS.get(request.target_status, set())
    missing_checks = tuple(sorted(required_checks - request.passed_checks))
    if missing_checks:
        blockers.append("required_checks_missing")

    if (
        request.target_status in HUMAN_APPROVAL_TARGETS
        and not request.human_approved
    ):
        blockers.append("human_approval_missing")

    if target_rank > STATUS_ORDER[PUBLIC_PROMOTION_CEILING]:
        blockers.append("public_promotion_ceiling")

    return PromotionDecision(
        allowed=not blockers,
        current_status=request.current_status,
        target_status=request.target_status,
        blockers=tuple(blockers),
        missing_evidence=missing_evidence,
        missing_checks=missing_checks,
    )
