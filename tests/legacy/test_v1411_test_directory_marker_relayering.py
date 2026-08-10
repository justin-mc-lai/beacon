from __future__ import annotations

from pathlib import Path

import pytest

from beacon.compatibility.registry import registry_by_id
from beacon.utils.test_marker_governance import (
    REQUIRED_TEST_MARKERS,
    V1411_RETIREMENT_TEST_FILES,
    collect_test_marker_inventory,
    registered_pytest_markers,
    validate_test_marker_governance,
)


ROOT = Path(__file__).resolve().parents[1]
FEATURE = "test-directory-marker-relayering-contract"
RUNTIME_FILES = (
    "beacon/command_catalog.py",
    "beacon/compatibility/registry.py",
    "beacon/utils/qa_runtime.py",
    "beacon/utils/material_audit.py",
    "beacon/utils/memory.py",
    "beacon/utils/intent_router.py",
    "beacon/adapters/browser_runner_common.py",
    "beacon/utils/prototype_support.py",
)

pytestmark = [pytest.mark.projection_integrity]


def _payload() -> dict:
    return validate_test_marker_governance(ROOT, registry_ids=set(registry_by_id()))


def test_marker_registry_contains_required_layers() -> None:
    markers = registered_pytest_markers(ROOT)

    assert set(REQUIRED_TEST_MARKERS) <= markers


def test_v1411_retirement_tests_are_marked() -> None:
    payload = _payload()

    assert payload["summary"]["classified_file_count"] == len(V1411_RETIREMENT_TEST_FILES)
    assert not [item for item in payload["issues"] if item["reason_code"] == "test_missing_role_marker"]


def test_current_contract_tests_do_not_assert_legacy_defaults() -> None:
    payload = _payload()

    assert payload["summary"]["current_tests"]
    assert not [
        item
        for item in payload["issues"]
        if item["reason_code"] == "current_contract_mentions_legacy_default_pattern"
    ]


def test_compat_tests_bind_to_registry_ids() -> None:
    payload = _payload()

    assert payload["summary"]["compat_tests"]
    assert not [
        item
        for item in payload["issues"]
        if item["reason_code"] in {"compat_contract_missing_compat_id", "compat_contract_unregistered_compat_id"}
    ]


def test_historical_fixture_tests_are_not_current_closure() -> None:
    payload = _payload()

    assert payload["summary"]["historical_fixture_tests"]
    assert not [
        item
        for item in payload["issues"]
        if item["reason_code"] == "historical_fixture_marked_current_contract"
    ]


def test_migration_tests_assert_evidence_or_transactions() -> None:
    payload = _payload()

    assert payload["summary"]["migration_tests"]
    assert not [
        item
        for item in payload["issues"]
        if item["reason_code"] == "migration_missing_evidence_or_transaction_assertion"
    ]


def test_deprecated_tests_do_not_promote_default_routes() -> None:
    payload = _payload()

    assert payload["summary"]["deprecated_tests"]
    assert not [
        item
        for item in payload["issues"]
        if item["reason_code"] == "deprecated_marked_current_contract"
    ]


def test_projection_tests_are_marked_separately() -> None:
    payload = _payload()

    assert payload["summary"]["projection_integrity_tests"]
    assert payload["summary"]["marker_counts"]["projection_integrity"] > 0


def test_marker_validation_payload_is_deterministic() -> None:
    first = _payload()
    second = _payload()

    assert first == second
    assert first["status"] == "pass"
    assert first["blocked"] is False
    assert first["issues"] == []


def test_no_runtime_behavior_changes() -> None:
    inventory = collect_test_marker_inventory(ROOT)
    changed_runtime_files = [
        rel
        for rel in RUNTIME_FILES
        if (ROOT / rel).exists() and FEATURE in (ROOT / rel).read_text(encoding="utf-8")
    ]

    assert inventory["files"]
    assert changed_runtime_files == []
