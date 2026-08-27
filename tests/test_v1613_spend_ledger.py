#!/usr/bin/env python3
"""L2 (v1.6.13) D2 spend ledger tests: persistence, validated-writeback-only,
quiet-skip no-spend, idempotent replay, halt on exhaust, handoff regression."""
import sys

from beacon.utils.goal_budget import (
    REASON_EXHAUSTED,
    commit_spend,
    enforce_handoff_budget,
    halt_on_exhaust,
    new_ledger,
    quota_exhausted,
    spend_eligible,
)

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"ok: {name}")
    else:
        FAILURES.append(name)
        print(f"FAIL: {name} {detail}", file=sys.stderr)


def test_persisted_ledger():
    led = new_ledger("g1", quota_limit=3)
    r = commit_spend(led, source="delivery_completion", index_digest="d1", writeback_ref="wb1")
    check("persisted_ledger", led["spent"] == 1 and len(led["entries"]) == 1 and r["ok"], led)


def test_no_spend_without_writeback():
    led = new_ledger("g2", quota_limit=3)
    r = spend_eligible(led, source="delivery_completion", writeback_validated=False, index_digest="d2")
    check("no_spend_without_writeback", r["blocked"] and r["reason_code"] == "spend_without_writeback", r)


def test_quiet_skip_no_spend():
    led = new_ledger("g3", quota_limit=3)
    for src in ("preflight", "dry_run", "quiet_skip"):
        r = spend_eligible(led, source=src, writeback_validated=True, index_digest="dx")
        assert r["blocked"] and r["reason_code"] == "quiet_skip_no_spend"
    check("quiet_skip_no_spend", led["spent"] == 0, led)


def test_idempotent_replay():
    led = new_ledger("g4", quota_limit=3)
    commit_spend(led, source="delivery_completion", index_digest="d4", writeback_ref="wb4")
    r2 = commit_spend(led, source="delivery_completion", index_digest="d4", writeback_ref="wb4")
    check("idempotent_replay", led["spent"] == 1 and r2.get("already_spent"), led)


def test_halt_on_exhaust():
    led = new_ledger("g5", quota_limit=2)
    commit_spend(led, source="delivery_completion", index_digest="a", writeback_ref="w")
    commit_spend(led, source="delivery_completion", index_digest="b", writeback_ref="w")
    check("quota_exhausted", quota_exhausted(led), led)
    h = halt_on_exhaust(led)
    check("halt_on_exhaust", h["state"] == "halt_budget" and h["reason_code"] == REASON_EXHAUSTED, h)
    r = spend_eligible(led, source="delivery_completion", writeback_validated=True, index_digest="c")
    check("no_spend_after_exhaust", r["blocked"] and r["reason_code"] == REASON_EXHAUSTED, r)


def test_handoff_budget():
    out = enforce_handoff_budget("line1\n" * 20)
    check("handoff_budget_truncate", out["truncated"] and out["lines"] <= 16, out)


if __name__ == "__main__":
    test_persisted_ledger()
    test_no_spend_without_writeback()
    test_quiet_skip_no_spend()
    test_idempotent_replay()
    test_halt_on_exhaust()
    test_handoff_budget()
    sys.exit(1 if FAILURES else 0)
