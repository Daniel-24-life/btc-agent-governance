from governance.promotion_gate import PromotionRequest, evaluate_promotion


def test_public_ceiling_blocks_complete_candidate_package():
    request = PromotionRequest(
        candidate_id="C-001",
        current_status="research_only",
        target_status="candidate",
        evidence_classes=frozenset({"research_artifact", "governance_audit"}),
        passed_checks=frozenset(
            {"data_asof", "objective_label", "stability", "stress_test"}
        ),
    )

    decision = evaluate_promotion(request)

    assert decision.allowed is False
    assert decision.blockers == ("public_promotion_ceiling",)
    assert decision.missing_evidence == ()
    assert decision.missing_checks == ()


def test_gate_reports_missing_evidence_and_checks():
    request = PromotionRequest(
        candidate_id="C-002",
        current_status="research_only",
        target_status="candidate",
        evidence_classes=frozenset(),
        passed_checks=frozenset(),
    )

    decision = evaluate_promotion(request)

    assert decision.allowed is False
    assert "required_evidence_missing" in decision.blockers
    assert "required_checks_missing" in decision.blockers
    assert decision.missing_evidence == ("governance_audit", "research_artifact")
    assert decision.missing_checks == (
        "data_asof",
        "objective_label",
        "stability",
        "stress_test",
    )


def test_gate_blocks_stage_skip_and_missing_human_approval():
    request = PromotionRequest(
        candidate_id="C-003",
        current_status="research_only",
        target_status="paper_trade",
        evidence_classes=frozenset(
            {"governance_audit", "dry_run", "human_approved"}
        ),
        passed_checks=frozenset({"execution_fill", "risk_state", "rollback"}),
        human_approved=False,
    )

    decision = evaluate_promotion(request)

    assert decision.allowed is False
    assert "stage_skip_forbidden" in decision.blockers
    assert "human_approval_missing" in decision.blockers
    assert "public_promotion_ceiling" in decision.blockers


def test_gate_blocks_unknown_statuses():
    request = PromotionRequest(
        candidate_id="C-004",
        current_status="unknown",
        target_status="candidate",
        evidence_classes=frozenset(),
        passed_checks=frozenset(),
    )

    decision = evaluate_promotion(request)

    assert decision.allowed is False
    assert decision.blockers == ("unknown_current_status",)
