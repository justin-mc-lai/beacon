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


# ---------------------------------------------------------------------------
# Spend ledger (v1.6.13 D2; LoopX spend_commit/slot_accounting distillation)
# ---------------------------------------------------------------------------

SPEND_SCHEMA = "goal-spend-ledger.v1"
# Sources that must never spend (quiet skip / dry-run / preflight).
QUIET_SKIP_SOURCES = {"preflight", "dry_run", "quiet_skip", "poll"}
# Sources that may spend a turn.
SPEND_SOURCES = {"delivery_completion", "repair", "self_repair", "capability_repair"}
REASON_EXHAUSTED = "program_drive_budget_exhausted"


def new_ledger(goal_id: str, quota_limit: int) -> dict[str, Any]:
    """Create a persistent spend ledger for one goal run (AC-001)."""
    return {
        "schema": SPEND_SCHEMA,
        "goal_id": goal_id,
        "quota_limit": max(0, int(quota_limit)),
        "spent": 0,
        "entries": [],
    }


def spend_eligible(
    ledger: dict[str, Any],
    *,
    source: str,
    writeback_validated: bool,
    index_digest: str,
) -> dict[str, Any]:
    """Gate a spend attempt. Only a validated delivery may spend once (AC-002..004).

    - AC-002: writeback must be validated (spend_guard).
    - AC-003: quiet-skip / dry-run / preflight sources never spend.
    - AC-004: idempotent — the same index_digest may only be spent once (CAS).
    """
    if source in QUIET_SKIP_SOURCES:
        return {"ok": False, "blocked": True, "reason_code": "quiet_skip_no_spend"}
    guard = spend_guard(writeback_validated)
    if not guard["ok"]:
        return {"ok": False, "blocked": True, "reason_code": "spend_without_writeback"}
    if any(e.get("index_digest") == index_digest for e in ledger["entries"]):
        return {"ok": False, "blocked": True, "reason_code": "spend_idempotency_conflict"}
    if source not in SPEND_SOURCES:
        return {"ok": False, "blocked": True, "reason_code": "spend_source_not_allowed"}
    if quota_exhausted(ledger):
        return {"ok": False, "blocked": True, "reason_code": REASON_EXHAUSTED}
    return {"ok": True, "blocked": False, "reason_code": ""}


def commit_spend(
    ledger: dict[str, Any],
    *,
    source: str,
    index_digest: str,
    writeback_ref: str,
) -> dict[str, Any]:
    """Commit one spend after eligibility passes. Idempotent on index_digest (AC-004)."""
    for e in ledger["entries"]:
        if e.get("index_digest") == index_digest:
            return {"ok": True, "blocked": False, "reason_code": "spend_idempotent_replay", "already_spent": True}
    ledger["entries"].append(
        {
            "index": len(ledger["entries"]) + 1,
            "source": source,
            "index_digest": index_digest,
            "writeback_ref": writeback_ref,
        }
    )
    ledger["spent"] = len(ledger["entries"])
    return {"ok": True, "blocked": False, "reason_code": "", "already_spent": False}


def quota_exhausted(ledger: dict[str, Any]) -> bool:
    """True when the ledger has consumed its quota (AC-005)."""
    return ledger["spent"] >= ledger["quota_limit"]


def halt_on_exhaust(ledger: dict[str, Any]) -> dict[str, Any]:
    """Return a halt_budget stop packet when quota is exhausted (AC-005)."""
    if quota_exhausted(ledger):
        return {
            "state": "halt_budget",
            "reason_code": REASON_EXHAUSTED,
            "spent": ledger["spent"],
            "quota_limit": ledger["quota_limit"],
            "resume_action": "none",
        }
    return {"state": "running", "reason_code": "", "resume_action": "continue"}
