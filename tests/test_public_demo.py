from public_demo import SCENARIOS, build_demo, format_summary, run_scenario


def test_demo_covers_three_public_scenarios():
    payload = build_demo()

    assert tuple(item["scenario"] for item in payload["scenarios"]) == SCENARIOS
    assert payload["summary"]["scenario_count"] == 4


def test_research_candidate_stays_research_only():
    result = run_scenario("research_candidate")

    assert result["route"]["decision"] == "allow"
    assert result["evidence"]["allowed"] is True
    assert result["release"]["decision"] == "research_only"
    assert result["release"]["execution_authority"] is False


def test_dry_run_reconciles_without_real_execution():
    result = run_scenario("dry_run_lifecycle")

    assert result["route"]["decision"] == "allow"
    assert result["lifecycle"]["reconciliation"]["status"] == "matched"
    assert result["lifecycle"]["reconciliation"]["real_order_submitted"] is False
    assert result["lifecycle"]["reconciliation"]["real_fill_recorded"] is False


def test_live_request_is_blocked_before_lifecycle():
    result = run_scenario("live_request")

    assert result["route"]["decision"] == "refuse"
    assert result["lifecycle"] is None
    assert result["release"]["decision"] == "blocked"


def test_promotion_request_is_blocked_by_public_ceiling():
    result = run_scenario("promotion_request")

    assert result["route"]["decision"] == "approval_required"
    assert result["promotion"]["decision"]["allowed"] is False
    assert result["promotion"]["decision"]["blockers"] == [
        "public_promotion_ceiling"
    ]
    assert result["release"]["decision"] == "blocked"


def test_demo_summary_has_no_execution_claims():
    payload = build_demo()

    assert payload["summary"]["research_only_count"] == 2
    assert payload["summary"]["blocked_count"] == 2
    assert payload["summary"]["real_orders_submitted"] == 0
    assert payload["summary"]["real_fills_recorded"] == 0


def test_console_summary_keeps_boundary_visible():
    summary = format_summary(build_demo())

    assert "live_request" in summary
    assert "blocked" in summary
    assert "real_orders_submitted=0" in summary
    assert "system_status=research_only" in summary
