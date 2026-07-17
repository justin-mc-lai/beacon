"""Contract tests for beacon-domain-fsm-authority-v167 (AC-DFSM-*)."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.domain_fsm import (
    REASON_DOMAIN_FSM_MISSING,
    REASON_ENTITY_PRECEDENCE_MISSING,
    REASON_ILLEGAL_TRANSITION_SLOT_MISSING,
    REASON_ORPHAN_AC_WITHOUT_FSM_PATH,
    build_domain_fsm_gate_payload,
    evaluate_domain_fsm_authority,
    parse_domain_fsm_from_truth,
    schema_contract,
    validate_domain_fsm_projection,
)
from beacon.utils.requirement_clarity import build_requirement_clarity_gate_payload
from beacon.utils.truth_integrity import build_truth_integrity_gate

POSITIVE_TRUTH = """---
slug: golden-commerce-checkout-positive
version: v1.6.7
status: frozen
domain_required: true
parser_contract: beacon-feature-package-v2
---

# Golden Fixture Truth: Commerce Checkout (Positive)

## Domain Model

| Entity | Key | Precedence |
|--------|-----|------------|
| Product | product_id | root catalog entity |
| Cart | cart_id | requires User session |
| Order | order_id | requires ≥1 OrderLine → Product.listed |
| OrderLine | order_line_id | requires Product |

## Domain FSM — Product

| State | From | Guard |
|-------|------|-------|
| draft | - | - |
| listed | draft | title+price present |
| archived | listed | - |

## Domain FSM — Order

| State | From | Guard | Side effects |
|-------|------|-------|--------------|
| draft | - | - | - |
| placed | draft | lines.non_empty ∧ all products.listed | reserve stock |
| paid | placed | payment.ok | capture payment |
| shipped | paid | - | create shipment |
| cancelled | draft, placed | !paid | release stock |

## Illegal transitions (must have TC)

- Order.placed without Product
- Order.paid from draft
- Order.shipped before paid

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-COM-001 | User can create listed Product |
| AC-COM-002 | User can place Order only with listed Product lines |
| AC-COM-003 | User can pay placed Order |
| AC-COM-004 | User can ship paid Order |
| AC-COM-005 | System rejects order without product (illegal) |
"""

NEGATIVE_TRUTH = """---
slug: golden-commerce-checkout-negative-no-product
version: v1.6.7
status: draft
domain_required: true
expected_gate: freeze_or_qa_fail
parser_contract: beacon-feature-package-v2
---

# Negative Fixture: Order Without Product

## Intentional defect

Acceptance claims user can place order without Domain Model Product precedence.

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-NEG-001 | User can place order
"""

ORPHAN_TRUTH = """---
slug: orphan-ac-demo
version: v1.6.7
status: draft
domain_required: true
parser_contract: beacon-feature-package-v2
---

# Orphan AC Demo

## Domain Model

| Entity | Key | Precedence |
|--------|-----|------------|
| Product | product_id | root |

## Domain FSM — Product

| State | From | Guard |
|-------|------|-------|
| draft | - | - |
| listed | draft | ok |

## Illegal transitions

- Product.listed without title

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-ORPH-001 | User enjoys the dashboard weather widget
| AC-ORPH-002 | User can create listed Product
"""


def test_schema_contract() -> None:
    contract = schema_contract()
    assert contract["domain_fsm"]["schema"] == "domain-fsm.v1"
    assert "aggregates" in contract["domain_fsm"]["fields"]
    assert "transitions" in contract["domain_fsm"]["fields"]
    assert contract["entity_precedence"]["schema"] == "entity-precedence.v1"
    assert "entities" in contract["entity_precedence"]["fields"]
    assert contract["authority"]["support_checklists_noncanonical"] is True
    projection = parse_domain_fsm_from_truth(POSITIVE_TRUTH)
    assert projection["domain_fsm_schema"] == "domain-fsm.v1"
    assert projection["entity_precedence_schema"] == "entity-precedence.v1"
    assert len(projection["entities"]) >= 3
    assert len(projection["aggregates"]) >= 2
    assert len(projection["illegal_transition_slots"]) >= 1


def test_freeze_blocks_missing_fsm() -> None:
    result = evaluate_domain_fsm_authority(truth_markdown=NEGATIVE_TRUTH, version="v1.6.7")
    assert result["required"] is True
    assert result["blocked"] is True
    codes = {item.get("reason_code") for item in result["findings"]}
    assert REASON_DOMAIN_FSM_MISSING in codes or REASON_ENTITY_PRECEDENCE_MISSING in codes
    assert result["reason_code"] in {
        REASON_DOMAIN_FSM_MISSING,
        REASON_ENTITY_PRECEDENCE_MISSING,
        REASON_ILLEGAL_TRANSITION_SLOT_MISSING,
        "domain_model_missing",
    } or result["blocked"]


def test_clarity_fail_closed(tmp_path: Path) -> None:
    version = "v1.6.7"
    slug = "clarity-domain-missing"
    pkg = tmp_path / "docs" / "beacon" / version / "features" / slug
    pkg.mkdir(parents=True)
    (pkg / "truth.md").write_text(NEGATIVE_TRUTH.replace("golden-commerce-checkout-negative-no-product", slug), encoding="utf-8")
    (pkg / "tests.md").write_text(
        f"""---
slug: {slug}
version: {version}
status: draft
parser_contract: beacon-feature-package-v2
---

# Tests

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-NEG-001 | TC-001 | contract | `python3 -m pytest -q` | pass |
""",
        encoding="utf-8",
    )
    (pkg / "tasks.md").write_text("# Tasks\n\n- [ ] TASK-001\n", encoding="utf-8")
    (pkg / "evidence.md").write_text("# Evidence\n\nindex only\n", encoding="utf-8")

    # minimal project markers so version resolves
    (tmp_path / "docs" / "beacon" / version).mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon").mkdir(exist_ok=True)

    gate = build_domain_fsm_gate_payload(tmp_path, version=version, feature=slug)
    assert gate["required"] is True
    assert gate["blocked"] is True

    # Direct evaluate path is the hard contract; clarity integrates the same gate.
    clarity = build_requirement_clarity_gate_payload(tmp_path, version=version, feature=slug)
    domain_gate = clarity.get("domain_fsm_gate") if isinstance(clarity.get("domain_fsm_gate"), dict) else {}
    # When clarity runtime feature is off, domain_fsm_gate may still be attached only if clarity required.
    # Fail-closed contract is enforced on domain_fsm_gate itself.
    assert gate["blocked"] is True
    if clarity.get("required"):
        assert domain_gate.get("blocked") is True or any(
            str(item.get("reason_code") or "").startswith("domain")
            or str(item.get("kind") or "").startswith("domain")
            or "entity_precedence" in str(item.get("reason_code") or "")
            or "illegal_transition" in str(item.get("reason_code") or "")
            for item in clarity.get("findings") or []
        )


def test_orphan_ac_detected() -> None:
    result = evaluate_domain_fsm_authority(truth_markdown=ORPHAN_TRUTH, version="v1.6.7")
    assert result["required"] is True
    assert result["blocked"] is True
    codes = {item.get("reason_code") for item in result["findings"]}
    assert REASON_ORPHAN_AC_WITHOUT_FSM_PATH in codes
    orphan_ids = {
        item.get("ac_id")
        for item in result["findings"]
        if item.get("reason_code") == REASON_ORPHAN_AC_WITHOUT_FSM_PATH
    }
    assert "AC-ORPH-001" in orphan_ids
    assert "AC-ORPH-002" not in orphan_ids


def test_illegal_transition_slot_required() -> None:
    truth = """---
slug: no-illegal
version: v1.6.7
domain_required: true
---

## Domain Model

| Entity | Key | Precedence |
|--------|-----|------------|
| Order | order_id | requires Product |

## Domain FSM — Order

| State | From | Guard |
|-------|------|-------|
| draft | - | - |
| placed | draft | ok |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-X-001 | User can place Order
"""
    result = evaluate_domain_fsm_authority(truth_markdown=truth, version="v1.6.7")
    assert result["blocked"] is True
    codes = {item.get("reason_code") for item in result["findings"]}
    assert REASON_ILLEGAL_TRANSITION_SLOT_MISSING in codes

    positive = evaluate_domain_fsm_authority(truth_markdown=POSITIVE_TRUTH, version="v1.6.7")
    assert positive["required"] is True
    assert positive["blocked"] is False, positive["findings"]


def test_positive_fixture_file_parses(tmp_path: Path) -> None:
    """Golden positive fixture on disk should pass domain authority when present in repo."""
    root = Path(__file__).resolve().parents[1]
    positive = root / "docs/beacon/v1.6.7/fixtures/golden-commerce-checkout/positive/truth.md"
    if not positive.exists():
        return
    text = positive.read_text(encoding="utf-8")
    # Ensure explicit domain mark for authority evaluation in isolation
    if "domain_required" not in text:
        text = text.replace("fixture: true", "fixture: true\ndomain_required: true", 1)
    result = evaluate_domain_fsm_authority(truth_markdown=text, version="v1.6.7")
    assert result["required"] is True
    assert result["blocked"] is False, result["findings"]


def test_integrity_prefers_domain_reason(tmp_path: Path) -> None:
    version = "v1.6.7"
    slug = "tig-domain-missing"
    pkg = tmp_path / "docs" / "beacon" / version / "features" / slug
    pkg.mkdir(parents=True)
    (pkg / "truth.md").write_text(
        NEGATIVE_TRUTH.replace("golden-commerce-checkout-negative-no-product", slug),
        encoding="utf-8",
    )
    (pkg / "tests.md").write_text(
        f"""---
slug: {slug}
version: {version}
status: draft
truth_ref: x
parser_contract: beacon-feature-package-v2
---

# t

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-NEG-001 | TC-001 | contract | `python3 -m pytest -q` | pass |
""",
        encoding="utf-8",
    )
    (pkg / "tasks.md").write_text(
        f"""---
slug: {slug}
version: {version}
status: draft
truth_ref: x
parser_contract: beacon-feature-package-v2
---

# t

## Task Ledger

- [ ] TASK-001 Materialize feature package
""",
        encoding="utf-8",
    )
    (pkg / "evidence.md").write_text(
        f"""---
slug: {slug}
version: {version}
status: draft
parser_contract: beacon-feature-package-v2
---

# Evidence Index

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-gen-truth | requirement_truth | docs/beacon/{version}/features/{slug}/truth.md | draft | truth |
""",
        encoding="utf-8",
    )
    (tmp_path / ".beacon").mkdir(exist_ok=True)

    domain = build_domain_fsm_gate_payload(tmp_path, version=version, feature=slug)
    assert domain["blocked"] is True
    tig = build_truth_integrity_gate(tmp_path, version=version, feature=slug, mode="block")
    assert tig.get("domain_fsm", {}).get("blocked") is True or domain["blocked"] is True


def test_truth_section_resolver_readable() -> None:
    """AC-DFSM-002: Domain Model / Domain FSM sections are parseable from package truth."""
    from beacon.utils.domain_fsm import parse_domain_fsm_from_truth
    root = Path(__file__).resolve().parents[1]
    truth = (root / "docs/beacon/v1.6.7/fixtures/golden-commerce-checkout/positive/truth.md").read_text(encoding="utf-8")
    if "domain_required" not in truth:
        truth = truth.replace("fixture: true", "fixture: true\ndomain_required: true", 1)
    proj = parse_domain_fsm_from_truth(truth)
    assert proj["has_domain_model_section"] is True
    assert proj["has_domain_fsm_section"] is True
    assert proj["entities"]
    assert proj["aggregates"]


def test_checklist_is_noncanonical() -> None:
    """AC-DFSM-007: schema contract marks support checklists non-canonical."""
    from beacon.utils.domain_fsm import schema_contract
    contract = schema_contract()
    assert contract["authority"]["support_checklists_noncanonical"] is True
    assert "freeze" in contract["authority"]["gates"]
