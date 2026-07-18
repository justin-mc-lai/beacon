"""v2.0.0 Golden commerce fixture parity tests."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.golden_commerce_fixture import (
    resolve_v2_parity_index,
    validate_negative_package,
    validate_positive_package,
)

ROOT = Path(__file__).resolve().parents[1]


def test_positive_package() -> None:
    # v2 resolves to v1.6.7 upstream golden
    result = validate_positive_package(ROOT, version="v2.0.0")
    assert result["blocked"] is False, result
    assert result["has_product_fsm"] is True
    assert result["has_order_fsm"] is True


def test_negative_order_without_product() -> None:
    result = validate_negative_package(ROOT, version="v2.0.0")
    assert result["must_fail"] is True
    assert result["fails_closed"] is True, result


def test_v2_index_resolves() -> None:
    idx = resolve_v2_parity_index(ROOT, version="v2.0.0")
    assert idx["resolves"] is True, idx
    assert idx["blocked"] is False
