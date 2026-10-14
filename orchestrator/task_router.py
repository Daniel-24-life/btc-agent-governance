from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Decision = Literal["allow", "approval_required", "refuse"]
Plane = Literal["research", "execution", "governance"]


KNOWN_PLANES = {"research", "execution", "governance"}
KNOWN_PRIORITIES = {"T1", "T2", "T3"}
FORBIDDEN_PATTERNS = {
    "real order",
    "api key",
    "live trading",
    "paper trading",
    "leverage",
    "production ready",
    "override governance",
}

PLANE_ALLOWED_TYPES = {
    "research": {"question", "candidate", "validation", "artifact", "audit"},
    "execution": {"schema", "dry_run", "log", "audit"},
    "governance": {"policy", "evidence", "promotion", "audit"},
}


@dataclass(frozen=True)
class Task:
    task_id: str
    plane: Plane
    action_type: str
    priority: str
    description: str
    auto_allowed: bool = True


@dataclass(frozen=True)
class RouteDecision:
    decision: Decision
    task_id: str | None
    plane: str | None
    reasons: tuple[str, ...]


def route_task(task: Task) -> RouteDecision:
    """Route one task under fail-closed plane policy."""
    if not task.task_id.strip():
        return RouteDecision("refuse", task.task_id, task.plane, ("missing task_id",))
    if task.plane not in KNOWN_PLANES:
        return RouteDecision("refuse", task.task_id, task.plane, ("unknown plane",))
    if task.priority not in KNOWN_PRIORITIES:
        return RouteDecision("refuse", task.task_id, task.plane, ("unknown priority",))
    if task.action_type not in PLANE_ALLOWED_TYPES[task.plane]:
        return RouteDecision(
            "refuse",
            task.task_id,
            task.plane,
            ("action_type is not allowed for plane",),
        )

    text = f"{task.task_id} {task.action_type} {task.description}".lower()

    for pattern in FORBIDDEN_PATTERNS:
        if pattern in text:
            return RouteDecision(
                decision="refuse",
                task_id=task.task_id,
                plane=task.plane,
                reasons=(f"forbidden boundary matched: {pattern}",),
            )

    if task.plane == "governance" and task.action_type == "promotion":
        return RouteDecision(
            decision="approval_required",
            task_id=task.task_id,
            plane=task.plane,
            reasons=("promotion evaluation requires explicit review",),
        )

    if task.priority in {"T2", "T3"} or not task.auto_allowed:
        return RouteDecision(
            decision="approval_required",
            task_id=task.task_id,
            plane=task.plane,
            reasons=("task requires explicit review",),
        )

    return RouteDecision(
        decision="allow",
        task_id=task.task_id,
        plane=task.plane,
        reasons=("task satisfies public-safe plane policy",),
    )


def select_first_allowed(tasks: list[Task]) -> RouteDecision:
    """Pick the first allowed task; fail closed if none are safe."""
    approval: RouteDecision | None = None

    for task in tasks:
        decision = route_task(task)
        if decision.decision == "allow":
            return decision
        if decision.decision == "approval_required" and approval is None:
            approval = decision

    if approval is not None:
        return approval

    return RouteDecision(
        decision="refuse",
        task_id=None,
        plane=None,
        reasons=("no safe task candidate found",),
    )
