"""Bounded turn budget (LoopX distillation; CAP-4 of beacon-goal-loopx-hybrid-v1612).

Distills IP-001 bounded delivery plus LoopX handoff/interface budgets: one
turn = choose -> deliver -> validate -> writeback -> spend, and handoff text
is capped so long-running state stays compact.
"""

from __future__ import annotations

from typing import Any

BUDGET_SCHEMA = "goal-turn-budget.v1"
HANDOFF_MAX_LINES = 16
HANDOFF_MAX_CHARS = 1800
TURN_STEPS = ("choose", "deliver", "validate", "writeback", "spend")


def enforce_handoff_budget(text: str) -> dict[str, Any]:
    """Truncate handoff text to 16 lines / 1800 chars and report the cut (AC-004)."""
    raw = str(text or "")
    lines = raw.splitlines()
    truncated = False
    if len(lines) > HANDOFF_MAX_LINES:
        lines = lines[:HANDOFF_MAX_LINES]
        truncated = True
    body = "\n".join(lines)
    if len(body) > HANDOFF_MAX_CHARS:
        body = body[:HANDOFF_MAX_CHARS]
        truncated = True
    return {
        "schema": BUDGET_SCHEMA,
        "text": body,
        "truncated": truncated,
        "lines": len(body.splitlines()),
        "chars": len(body),
        "max_lines": HANDOFF_MAX_LINES,
        "max_chars": HANDOFF_MAX_CHARS,
    }


def turn_contract() -> dict[str, Any]:
    """The bounded-delivery turn contract for goal drivers (AC-004)."""
    return {
        "schema": BUDGET_SCHEMA,
        "mode": "bounded_delivery",
        "steps": list(TURN_STEPS),
        "spend_after_writeback": True,
    }


def spend_guard(writeback_validated: bool) -> dict[str, Any]:
    """A turn without validated writeback may not spend (AC-004)."""
    if writeback_validated:
        return {"schema": BUDGET_SCHEMA, "ok": True, "blocked": False, "reason_code": ""}
    return {
        "schema": BUDGET_SCHEMA,
        "ok": False,
        "blocked": True,
        "reason_code": "spend_without_writeback",
    }
