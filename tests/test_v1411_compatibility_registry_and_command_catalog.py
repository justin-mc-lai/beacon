from __future__ import annotations

import importlib
from pathlib import Path

from typer.testing import CliRunner

from beacon.command_catalog import (
    COMMAND_LAYER_ORDER,
    COMPAT_COMMANDS,
    CORE_COMMANDS,
    DEFAULT_USER_SURFACE,
    DEPRECATED_COMMANDS,
    command_layer,
    command_layers,
    validate_command_catalog_layers,
)
from beacon.compatibility.registry import (
    COMPATIBILITY_REGISTRY,
    REQUIRED_REGISTRY_FIELDS,
    registry_by_id,
    required_registry_ids_from_baseline,
    validate_compatibility_registry,
)
from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
VERSION = "v1.4.11"

REQUIRED_REGISTRY_IDS = {
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

runner = CliRunner()


def test_registry_schema_has_required_fields():
    assert set(REQUIRED_REGISTRY_FIELDS) == {
        "compat_id",
        "surface",
        "owner",
        "reason",
        "introduced_before",
        "allowed_version_range",
        "default_behavior",
        "current_replacement",
        "retirement_route",
        "evidence_required",
    }
    result = validate_compatibility_registry(required_ids=REQUIRED_REGISTRY_IDS)
    assert result["status"] == "pass"
    assert result["issues"] == []


def test_registry_covers_required_baseline_inventory_surfaces():
    from_baseline = required_registry_ids_from_baseline(ROOT, version=VERSION)
    assert REQUIRED_REGISTRY_IDS <= from_baseline
    registry_ids = set(registry_by_id())
    assert from_baseline <= registry_ids


def test_registry_entries_include_lifecycle_metadata():
    valid_surfaces = {"command", "implement", "qa", "prd", "prototype", "browser", "memory", "intent"}
    for entry in COMPATIBILITY_REGISTRY:
        assert set(REQUIRED_REGISTRY_FIELDS) <= set(entry)
        assert entry["compat_id"] in REQUIRED_REGISTRY_IDS
        assert entry["surface"] in valid_surfaces
        assert str(entry["owner"]).strip()
        assert str(entry["reason"]).strip()
        assert str(entry["current_replacement"]).strip()
        assert str(entry["default_behavior"]).strip()
        assert str(entry["allowed_version_range"]).strip()
        assert str(entry["retirement_route"]).strip()
        assert isinstance(entry["evidence_required"], list)
        assert entry["evidence_required"]


def test_command_catalog_layers_are_explicit():
    layers = command_layers()
    assert set(COMMAND_LAYER_ORDER) == {
        "current",
        "support",
        "advanced",
        "labs",
        "compat",
        "deprecated",
        "internal",
    }
    assert all(command_layer(command) == "current" for command in CORE_COMMANDS)
    assert all(command_layer(command) == "compat" for command in COMPAT_COMMANDS)
    assert all(command_layer(command) == "deprecated" for command in DEPRECATED_COMMANDS)
    assert layers["change"] == "internal"

    validation = validate_command_catalog_layers()
    assert validation["status"] == "pass"
    assert validation["issues"] == []


def test_compat_and_deprecated_commands_remain_callable():
    for command in ("think", "workflow", "gate", "verify", "auto-test", "prompt", "save"):
        result = runner.invoke(app, [command, "--help"])
        assert result.exit_code == 0, result.stdout
        assert "No such command" not in result.stdout

    work_result = runner.invoke(app, ["work", "--help"])
    assert work_result.exit_code == 0, work_result.stdout
    assert "No such command" not in work_result.stdout


def test_default_routes_do_not_promote_compat_commands():
    forbidden = set(COMPAT_COMMANDS + DEPRECATED_COMMANDS)
    assert not (set(DEFAULT_USER_SURFACE) & forbidden)

    help_result = runner.invoke(app, ["--help"])
    assert help_result.exit_code == 0
    help_text = help_result.stdout
    assert "prd -> user-story -> test-case -> implement -> qa -> release" in help_text
    visible_command_lines = [line for line in help_text.splitlines() if line.lstrip().startswith("│")]
    for command in forbidden:
        assert not any(f"│ {command} " in line for line in visible_command_lines)


def test_unregistered_compat_surface_fails_validation():
    entries = [entry for entry in COMPATIBILITY_REGISTRY if entry["compat_id"] != "intent-legacy-router"]
    result = validate_compatibility_registry(entries=entries, required_ids=REQUIRED_REGISTRY_IDS)
    assert result["status"] == "blocked"
    assert "intent-legacy-router" in result["missing_required_ids"]
    assert "missing_required_registry_entry:intent-legacy-router" in result["issues"]

    alias_result = validate_command_catalog_layers(registry_entries=[])
    assert alias_result["status"] == "blocked"
    assert "missing_registry_command_alias:think" in alias_result["issues"]


def test_no_behavior_retirement_in_registry_slice():
    from beacon.utils import intent_router, memory, prototype_utils, qa_runtime
    from beacon.adapters import browser_runner_common

    implement_command = importlib.import_module("beacon.commands.implement")
    assert hasattr(implement_command, "app")
    assert callable(implement_command.run_implement_stage)
    assert callable(qa_runtime.write_qa_status)
    assert callable(qa_runtime.load_qa_status)
    assert callable(qa_runtime.legacy_auto_test_status_path)
    assert callable(prototype_utils.evaluate_prototype_status)
    assert callable(browser_runner_common.write_runner_artifacts)
    assert "fallback_cmd" in browser_runner_common.write_runner_artifacts.__annotations__
    assert callable(memory._migrate_legacy_to_v1_if_needed)
    assert callable(intent_router.detect_intent)
    assert callable(intent_router.route_intent)
