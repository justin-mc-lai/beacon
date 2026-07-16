"""Contract tests for beacon-golden-commerce-fixture-v167."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.domain_fsm import evaluate_domain_fsm_authority
from beacon.utils.golden_commerce_fixture import (
    build_golden_commerce_fixture_gate,
    validate_negative_package,
    validate_positive_package,
    validate_skill_pointers,
)

ROOT = Path(__file__).resolve().parents[1]


def test_positive_package_present() -> None:
    result = validate_positive_package(ROOT, version="v1.6.7")
    assert result["blocked"] is False, result["findings"]
    assert result["has_product_fsm"] is True
    assert result["has_order_fsm"] is True
    for key in ("truth", "tests", "tasks", "evidence"):
        assert Path(result["paths"][key]).exists()


def test_order_without_product_fails() -> None:
    result = validate_negative_package(ROOT, version="v1.6.7")
    assert result["must_fail"] is True
    assert result["fails_closed"] is True, result
    assert result["blocked"] is False  # gate for fixture itself passes because negative fails closed
    domain = result["domain"]
    assert domain["blocked"] is True or str(
        (domain.get("projection") or {}).get("frontmatter", {}).get("expected_gate") or ""
    )


def test_fsm_covers_product_and_order() -> None:
    result = validate_positive_package(ROOT, version="v1.6.7")
    assert result["has_product_fsm"] and result["has_order_fsm"]
    truth = Path(result["paths"]["truth"]).read_text(encoding="utf-8")
    domain = evaluate_domain_fsm_authority(truth_markdown=truth, version="v1.6.7")
    names = {str(a.get("name") or "").lower() for a in domain["projection"]["aggregates"]}
    assert any("product" in n for n in names)
    assert any("order" in n for n in names)
    assert domain["blocked"] is False


def test_skill_example_points_to_fixture() -> None:
    skills = validate_skill_pointers(ROOT)
    assert skills["blocked"] is False, skills
    assert skills["hits"]
    gate = build_golden_commerce_fixture_gate(ROOT, version="v1.6.7")
    assert gate["blocked"] is False, gate["findings"]
