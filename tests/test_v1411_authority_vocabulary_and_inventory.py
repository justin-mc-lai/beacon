from __future__ import annotations

import json
import importlib
from pathlib import Path

import pytest

from beacon.command_catalog import COMPAT_COMMANDS, DEPRECATED_COMMANDS
from beacon.utils.authority import ARTIFACT_ROLES, authority_roots, classify_artifact_role
from beacon.utils.baseline_inventory import (
    baseline_inventory_json_path,
    baseline_inventory_markdown_path,
    build_legacy_burden_baseline_inventory,
)


ROOT = Path(__file__).resolve().parents[1]
VERSION = "v1.4.11"
FEATURE = "authority-vocabulary-and-baseline-inventory-contract"
FORBIDDEN_MACHINE_TRUTH_WORDING = "machine artifacts remain source of truth"
pytestmark = [pytest.mark.projection_integrity]

REQUIRED_INVENTORY_FIELDS = {
    "source_file",
    "symbol",
    "surface_category",
    "current_behavior",
    "risk",
    "proposed_owner",
    "proposed_phase",
    "required_evidence",
}

REQUIRED_HOTSPOTS = {
    "authority-artifact-language-policy",
    "authority-artifact-language-renderer",
    "command-catalog-compat-deprecated-aliases",
    "cli-factory-hidden-compat-registrations",
    "implement-legacy-cli-loader",
    "qa-auto-test-status-legacy-mirror",
    "prd-legacy-machine-mirror",
    "prototype-legacy-wireframe-source",
    "browser-fallback-command-name",
    "memory-legacy-projection",
    "intent-legacy-router",
}


def _load_inventory() -> dict:
    path = baseline_inventory_json_path(ROOT, VERSION)
    return json.loads(path.read_text(encoding="utf-8"))


def test_artifact_roles_are_defined():
    assert set(ARTIFACT_ROLES) == {
        "truth",
        "projection",
        "evidence",
        "runtime_state",
        "compat_mirror",
        "historical_fixture",
    }


def test_forbidden_machine_truth_wording_is_rejected():
    current_facing_paths = [
        ROOT / "beacon" / "artifact-language-policy.json",
        ROOT / "beacon" / "utils" / "artifact_language.py",
        ROOT / "docs" / "beacon" / "v1.3.0" / "execution" / "artifact-language-contract.md",
    ]
    offenders = [
        str(path.relative_to(ROOT))
        for path in current_facing_paths
        if FORBIDDEN_MACHINE_TRUTH_WORDING in path.read_text(encoding="utf-8")
    ]
    assert offenders == []


def test_markdown_requirement_root_is_truth():
    roots = authority_roots(VERSION)
    assert roots.truth_root == "docs/beacon/v1.4.11"
    assert classify_artifact_role("docs/beacon/v1.4.11/SUMMARY.md") == "truth"
    assert classify_artifact_role("docs/beacon/v1.4.11/prd/example.md") == "truth"
    assert classify_artifact_role("docs/beacon/v1.4.11/qa/test-cases/example.md") == "truth"


def test_machine_root_is_projection_not_truth():
    roots = authority_roots(VERSION)
    assert roots.projection_root == "docs/beacon/v1.4.11/.machine"
    assert roots.runtime_evidence_root == ".beacon"
    assert classify_artifact_role("docs/beacon/v1.4.11/.machine/prd/example.json") == "projection"
    assert classify_artifact_role(".beacon/qa/status.json") == "evidence"
    assert classify_artifact_role(".beacon/state/session.json") == "runtime_state"


def test_baseline_inventory_artifacts_exist():
    json_path = baseline_inventory_json_path(ROOT, VERSION)
    markdown_path = baseline_inventory_markdown_path(ROOT, VERSION)
    assert json_path.exists()
    assert markdown_path.exists()
    assert FEATURE in markdown_path.read_text(encoding="utf-8")


def test_baseline_inventory_schema_is_complete():
    payload = _load_inventory()
    assert payload["schema_version"] == "1.0"
    assert payload["version"] == VERSION
    assert payload["feature"] == FEATURE
    assert payload["behavior_change_allowed"] is False
    assert set(payload["required_fields"]) == REQUIRED_INVENTORY_FIELDS
    assert payload["summary"]["missing_source_files"] == []

    items = payload["items"]
    assert len(items) >= len(REQUIRED_HOTSPOTS)
    for row in items:
        assert REQUIRED_INVENTORY_FIELDS <= set(row)
        assert row["exists"] is True
        assert row["behavior_change_allowed_in_this_slice"] is False
        assert row["artifact_role"] in ARTIFACT_ROLES
        assert isinstance(row["required_evidence"], list)
        assert row["required_evidence"]


def test_compat_behavior_is_not_retired_by_this_slice():
    assert {"think", "workflow", "gate", "verify", "auto-test"} <= set(COMPAT_COMMANDS)
    assert {"prompt", "save", "work"} <= set(DEPRECATED_COMMANDS)

    from beacon.utils import qa_runtime
    from beacon.utils import prototype_utils
    from beacon.adapters import browser_runner_common
    from beacon.utils import memory
    from beacon.utils import intent_router

    implement_command = importlib.import_module("beacon.commands.implement")
    assert hasattr(implement_command, "app")
    assert callable(implement_command.run_implement_stage)
    assert callable(qa_runtime.legacy_auto_test_status_path)
    assert callable(qa_runtime.write_qa_status)
    assert callable(qa_runtime.load_qa_status)
    assert callable(prototype_utils.evaluate_prototype_status)
    assert callable(browser_runner_common.write_runner_artifacts)
    assert "fallback_cmd" in browser_runner_common.write_runner_artifacts.__annotations__
    assert callable(memory._migrate_legacy_to_v1_if_needed)
    assert callable(intent_router.detect_intent)
    assert callable(intent_router.route_intent)


@pytest.mark.compat_contract
def test_required_hotspots_are_inventory_covered():
    generated = build_legacy_burden_baseline_inventory(ROOT, version=VERSION)
    generated_ids = {str(row.get("compat_id")) for row in generated["items"]}
    persisted_ids = {str(row.get("compat_id")) for row in _load_inventory()["items"]}
    assert REQUIRED_HOTSPOTS <= generated_ids
    assert REQUIRED_HOTSPOTS <= persisted_ids
