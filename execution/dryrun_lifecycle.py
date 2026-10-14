from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Literal


Side = Literal["observe", "reduce", "increase"]
EventType = Literal["intent_created", "risk_checked", "simulated_fill", "reconciled", "blocked"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class OrderIntent:
    intent_id: str
    side: Side
    target_fraction: float
    reason: str
    created_at: str


@dataclass(frozen=True)
class DryRunEvent:
    intent_id: str
    event_type: EventType
    message: str
    created_at: str


@dataclass(frozen=True)
class ReconciliationReport:
    intent_id: str
    status: Literal["matched", "blocked"]
    event_count: int
    real_order_submitted: bool
    real_fill_recorded: bool


def create_intent(intent_id: str, side: Side, target_fraction: float, reason: str) -> OrderIntent:
    return OrderIntent(
        intent_id=intent_id,
        side=side,
        target_fraction=target_fraction,
        reason=reason,
        created_at=utc_now(),
    )


def simulate_lifecycle(intent: OrderIntent, risk_allowed: bool) -> tuple[list[DryRunEvent], ReconciliationReport]:
    events = [
        DryRunEvent(intent.intent_id, "intent_created", "dry-run intent created", utc_now()),
    ]

    if not risk_allowed:
        events.append(DryRunEvent(intent.intent_id, "blocked", "risk policy blocked intent", utc_now()))
        return events, ReconciliationReport(
            intent_id=intent.intent_id,
            status="blocked",
            event_count=len(events),
            real_order_submitted=False,
            real_fill_recorded=False,
        )

    events.extend([
        DryRunEvent(intent.intent_id, "risk_checked", "risk policy passed for simulation", utc_now()),
        DryRunEvent(intent.intent_id, "simulated_fill", "simulated fill recorded", utc_now()),
        DryRunEvent(intent.intent_id, "reconciled", "dry-run lifecycle reconciled", utc_now()),
    ])
    return events, ReconciliationReport(
        intent_id=intent.intent_id,
        status="matched",
        event_count=len(events),
        real_order_submitted=False,
        real_fill_recorded=False,
    )


def to_jsonable(value: object) -> dict:
    return asdict(value)
