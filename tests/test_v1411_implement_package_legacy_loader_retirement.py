from __future__ import annotations

import importlib
from pathlib import Path

from typer.testing import CliRunner

from beacon.command_catalog import COMPAT_COMMANDS, DEPRECATED_COMMANDS
from beacon.compatibility.registry import registry_by_id
from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def _read_current_source(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def test_implement_public_entrypoint_remains_routeable():
    result = runner.invoke(app, ["implement", "--help"])

    assert result.exit_code == 0, result.stdout
    assert "Run implementation via configured skill adapters" in result.stdout


def test_implement_public_subcommands_remain_routeable():
    expected = {
        "list-runners",
        "import-evidence",
        "run",
        "plan",
        "status",
        "check-branch",
        "sync-git-workflow",
    }

    help_result = runner.invoke(app, ["implement", "--help"])
    assert help_result.exit_code == 0, help_result.stdout
    for command in expected:
        assert command in help_result.stdout
        command_help = runner.invoke(app, ["implement", command, "--help"])
        assert command_help.exit_code == 0, command_help.stdout


def test_implement_package_exports_current_app():
    implement_package = importlib.import_module("beacon.commands.implement")
    implement_commands = importlib.import_module("beacon.commands.implement.commands")

    assert implement_package.app is implement_commands.app
    assert implement_package.run_implement_stage is implement_commands.run_implement_stage
    assert not hasattr(implement_package, "_legacy_cli")


def test_legacy_loader_function_is_absent():
    source = _read_current_source(
        [
            ROOT / "beacon" / "commands" / "implement" / "__init__.py",
            ROOT / "beacon" / "commands" / "implement" / "commands.py",
        ]
    )

    assert "_load_legacy_cli_module" not in source


def test_legacy_dynamic_module_name_is_absent():
    source = _read_current_source(
        [
            ROOT / "beacon" / "commands" / "implement" / "__init__.py",
            ROOT / "beacon" / "commands" / "implement" / "commands.py",
        ]
    )

    assert "_implement_legacy_cli" not in source


def test_tests_do_not_depend_on_legacy_cli():
    test_source = _read_current_source(
        [
            path
            for path in (ROOT / "tests").rglob("*.py")
            if path.name != "test_v1411_implement_package_legacy_loader_retirement.py"
        ]
    )

    assert "._legacy_cli" not in test_source
    assert "hasattr(implement_command, \"_legacy_cli\")" not in test_source


def test_implement_loader_retirement_is_registry_bound():
    entry = registry_by_id()["implement-legacy-cli-loader"]

    assert entry["surface"] == "implement"
    assert entry["retirement_route"] == "implement-package-legacy-loader-retirement-contract"


def test_no_unrelated_retirement_in_implement_loader_slice():
    from beacon.adapters import browser_runner_common
    from beacon.utils import intent_router, memory, prototype_utils, qa_runtime

    assert {"think", "workflow", "gate", "verify", "auto-test"} <= set(COMPAT_COMMANDS)
    assert {"prompt", "save", "work"} <= set(DEPRECATED_COMMANDS)
    assert callable(qa_runtime.write_qa_status)
    assert callable(qa_runtime.load_qa_status)
    assert callable(qa_runtime.legacy_auto_test_status_path)
    assert callable(prototype_utils.evaluate_prototype_status)
    assert callable(browser_runner_common.write_runner_artifacts)
    assert "fallback_cmd" in browser_runner_common.write_runner_artifacts.__annotations__
    assert callable(memory._migrate_legacy_to_v1_if_needed)
    assert callable(intent_router.detect_intent)
    assert callable(intent_router.route_intent)
