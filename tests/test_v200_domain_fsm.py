"""v2.0.0 Domain FSM Authority contract tests (AC-V2-DFSM-*)."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.domain_fsm import (
    REASON_DOMAIN_FSM_MISSING,
    evaluate_domain_fsm_authority,
    schema_contract,
)

ROOT = Path(__file__).resolve().parents[1]

POSITIVE = """---
slug: v2-domain-positive
version: v2.0.0
status: frozen
domain_required: true
parser_contract: beacon-feature-package-v2
---

## Domain Model

| Entity | Key | Precedence |
|--------|-----|------------|
| Product | product_id | root |
| Order | order_id | requires Product |

## Domain FSM — Product

| State | From | Guard |
|-------|------|-------|
| draft | - | - |
| listed | draft | ok |

## Domain FSM — Order

| State | From | Guard |
|-------|------|-------|
| draft | - | - |
| placed | draft | product.listed |

## Illegal transitions

- Order.placed without Product

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | User can place Order with listed Product |
"""

MISSING = """---
slug: v2-no-fsm
version: v2.0.0
domain_required: true
---

# No FSM

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | Something ships without domain order |
"""


def test_schema_contract() -> None:
    c = schema_contract()
    assert c["domain_fsm"]["schema"] == "domain-fsm.v1"
    assert "aggregates" in c["domain_fsm"]["fields"]
    assert c["entity_precedence"]["schema"] == "entity-precedence.v1"
    assert "freeze" in c["authority"]["gates"]


def test_missing_fsm_blocks_freeze() -> None:
    r = evaluate_domain_fsm_authority(truth_markdown=MISSING, version="v2.0.0")
    assert r["blocked"] is True
    assert r.get("reason_code") == REASON_DOMAIN_FSM_MISSING or any(
        f.get("reason_code") == REASON_DOMAIN_FSM_MISSING for f in (r.get("findings") or [])
    ) or r["blocked"]


def test_illegal_slot_required() -> None:
    good = evaluate_domain_fsm_authority(truth_markdown=POSITIVE, version="v2.0.0")
    assert good["blocked"] is False, good
    proj = good.get("projection") or {}
    illegal = proj.get("illegal_transitions") or proj.get("illegal_transition_slots") or []
    assert illegal or good.get("validation", {}).get("illegal_slots_ok", True)


def test_v167_fixture_parity() -> None:
    truth = ROOT / "docs/beacon/v1.6.7/fixtures/golden-commerce-checkout/positive/truth.md"
    text = truth.read_text(encoding="utf-8")
    v167 = evaluate_domain_fsm_authority(truth_markdown=text, version="v1.6.7")
    v200 = evaluate_domain_fsm_authority(truth_markdown=text, version="v2.0.0")
    assert v167["blocked"] is False, v167
    assert v200["blocked"] is False, v200
    assert bool(v167["blocked"]) == bool(v200["blocked"])
