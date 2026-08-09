"""Concrete user gate cards (LoopX distillation; CAP-3 of beacon-goal-loopx-hybrid-v1612).

Distills IP-004/014/027/029: a block becomes a concrete card (question +
context + resume action), decisions are cached so the same key is never asked
twice, and an unresolved gate blocks the illegal transition to the next stage.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

GATE_SCHEMA = "goal-user-gate.v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_gate_card(
    state: dict[str, Any],
    decision_key: str,
    question: str,
    *,
    context: str = "",
    resume_action: str = "await_human_confirmation",
) -> dict[str, Any]:
    """Build a gate card; a cached decision returns the cached answer instead (AC-003)."""
    cache = state.get("decision_cache") or {}
    if isinstance(cache, dict) and decision_key in cache:
        return {
            "schema": GATE_SCHEMA,
            "duplicate": True,
            "cached_answer": cache[decision_key],
            "card": None,
        }
    card = {
        "schema": GATE_SCHEMA,
        "decision_key": str(decision_key),
        "question": str(question),
        "context": str(context),
        "resume_action": str(resume_action),
        "status": "open",
    }
    return {"schema": GATE_SCHEMA, "duplicate": False, "card": card}


def resolve_gate(state: dict[str, Any], decision_key: str, answer: Any) -> dict[str, Any]:
    """Record the user answer; re-resolving the same key is rejected (AC-003)."""
    cache = dict(state.get("decision_cache") or {})
    if decision_key in cache:
        return {
            "schema": GATE_SCHEMA,
            "ok": False,
            "blocked": True,
            "reason_code": "already_resolved",
        }
    cache[decision_key] = {"answer": answer, "at": _now()}
    return {
        "schema": GATE_SCHEMA,
        "ok": True,
        "blocked": False,
        "reason_code": "",
        "decision_cache": cache,
    }


def assert_gate_resolved(state: dict[str, Any], decision_key: str) -> dict[str, Any]:
    """Illegal transition guard: gate_open -> next_stage requires resolve (AC-003)."""
    cache = state.get("decision_cache") or {}
    if isinstance(cache, dict) and decision_key in cache:
        return {"schema": GATE_SCHEMA, "ok": True, "blocked": False, "reason_code": ""}
    return {
        "schema": GATE_SCHEMA,
        "ok": False,
        "blocked": True,
        "reason_code": "gate_unresolved",
        "decision_key": str(decision_key),
    }
