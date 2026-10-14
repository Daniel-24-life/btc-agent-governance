from __future__ import annotations

from dataclasses import dataclass


FORBIDDEN_READINESS_CLAIMS = {
    "tradable",
    "paper_ready",
    "live_ready",
    "real_execution_ready",
    "production_ready",
}

REAL_EXECUTION_CLAIMS = {
    "real_fill",
    "real_order",
    "account_continuity",
    "realized_slippage",
}

ALLOWED_CLAIMS_BY_CLASS = {
    "research_artifact": {"research_direction", "hypothesis_quality"},
    "public_data": {"market_observation", "replay_study"},
    "research_replay": {"market_observation", "replay_study", "hypothesis_quality"},
    "dry_run": {"schema_design", "reconciliation_design", "lifecycle_design"},
    "governance_audit": {"boundary_check", "claim_control"},
    "human_approved": {"reviewed_next_stage"},
}


@dataclass(frozen=True)
class Evidence:
    evidence_class: str
    claims: frozenset[str]


@dataclass(frozen=True)
class EvidenceDecision:
    allowed: bool
    allowed_claims: frozenset[str]
    blocked_claims: frozenset[str]
    reasons: tuple[str, ...]


def classify_evidence(evidence: Evidence) -> EvidenceDecision:
    """Classify what an artifact is allowed to prove."""
    if evidence.evidence_class not in ALLOWED_CLAIMS_BY_CLASS:
        return EvidenceDecision(
            allowed=False,
            allowed_claims=frozenset(),
            blocked_claims=evidence.claims,
            reasons=("unknown evidence class",),
        )

    blocked: set[str] = set()
    reasons: list[str] = []

    readiness = evidence.claims.intersection(FORBIDDEN_READINESS_CLAIMS)
    if readiness:
        blocked.update(readiness)
        reasons.append("readiness claims require stronger evidence")

    real_claims = evidence.claims.intersection(REAL_EXECUTION_CLAIMS)
    if real_claims:
        blocked.update(real_claims)
        reasons.append("public evidence cannot prove real execution")

    unsupported = set(
        evidence.claims.difference(
            ALLOWED_CLAIMS_BY_CLASS[evidence.evidence_class]
        )
    )
    unsupported.difference_update(blocked)
    if unsupported:
        blocked.update(unsupported)
        reasons.append("claims are outside the evidence class")

    allowed_claims = evidence.claims.difference(blocked)

    return EvidenceDecision(
        allowed=not blocked,
        allowed_claims=frozenset(allowed_claims),
        blocked_claims=frozenset(blocked),
        reasons=tuple(reasons or ["claims match evidence class"]),
    )
