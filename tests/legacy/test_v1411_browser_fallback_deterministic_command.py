from __future__ import annotations

import json
import os
import pytest
from pathlib import Path

from beacon.adapters import agent_browser_runner, browser_use_runner
from beacon.adapters import browser_runner_common
from beacon.compatibility.registry import registry_by_id
from beacon.utils.browser_task_compiler import build_browser_task, write_browser_task
from beacon.utils.qa9 import default_command_for_qa_type


VERSION = "v1.4.11"
FEATURE = "browser-fallback-deterministic-command-contract"


def _write_pass_script(root: Path, name: str = "pass.sh") -> Path:
    script = root / name
    script.write_text("#!/bin/sh\nset -eu\nexit 0\n", encoding="utf-8")
    script.chmod(0o755)
    return script


def _task_file(root: Path, layer_dir: Path) -> Path:
    task = build_browser_task(
        item={
            "feature": FEATURE,
            "ac_id": "AC-003",
            "tc_id": "TC-BROWSER-FALLBACK-003",
            "source_tc_id": "TC-BROWSER-FALLBACK-003",
            "scenario_id": "SC-BROWSER-FALLBACK",
            "scenario_family": "happy",
            "assertion": "Browser evidence separates deterministic command execution from browser-agent execution.",
            "target_url": "/",
            "exploratory_runner": "browser-use",
            "deterministic_runner": "playwright",
            "replay_required": False,
        },
        qa_type="functional",
        mode="functional",
        project_root=root,
    )
    return write_browser_task(tc_dir=layer_dir.parent, payload=task)


def _run_browser_use(
    tmp_path: Path,
    *,
    option: str = "--deterministic-command",
    include_task: bool = True,
    command: str | None = None,
) -> tuple[int, dict[str, object], str]:
    layer_dir = tmp_path / "evidence" / "explore"
    layer_dir.mkdir(parents=True, exist_ok=True)
    script = _write_pass_script(tmp_path)
    args = ["--mode", "functional", "--project-root", str(tmp_path)]
    if include_task:
        args.extend(["--task-file", str(_task_file(tmp_path, layer_dir))])
    if command is not None:
        args.extend([option, command])
    else:
        args.extend([option, f"sh {script}"])

    original_layer_dir = os.environ.get("BEACON_LAYER_DIR")
    os.environ["BEACON_LAYER_DIR"] = str(layer_dir)
    try:
        code = browser_use_runner.main(args)
    finally:
        if original_layer_dir is None:
            os.environ.pop("BEACON_LAYER_DIR", None)
        else:
            os.environ["BEACON_LAYER_DIR"] = original_layer_dir

    report_path = layer_dir / "browser-runner-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    console = (layer_dir / "browser-runner-console.log").read_text(encoding="utf-8") if (layer_dir / "browser-runner-console.log").exists() else ""
    return code, report, console


@pytest.mark.current_contract
def test_current_deterministic_command_option(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        browser_use_runner.main(["--help"])
    help_text = capsys.readouterr().out

    assert "--deterministic-command" in help_text
    assert "--explicit-project-command" in help_text


@pytest.mark.compat_contract
@pytest.mark.deprecated
def test_fallback_cmd_remains_compat_alias(tmp_path: Path) -> None:
    code, report, _console = _run_browser_use(tmp_path, option="--fallback-cmd")
    registry = registry_by_id()

    assert code == 0
    assert "browser-fallback-command-name" in registry
    assert report["fallback_cmd"].startswith("sh ")
    assert report["deterministic_command"].startswith("sh ")
    assert report["compat_alias_used"] is True


@pytest.mark.current_contract
def test_deterministic_command_execution_mode(tmp_path: Path) -> None:
    code, report, console = _run_browser_use(tmp_path)

    assert code == 0
    assert report["execution_mode"] == "deterministic_command"
    assert "execution_mode=deterministic_command" in console


@pytest.mark.current_contract
def test_browser_agent_and_command_evidence_are_split(tmp_path: Path) -> None:
    code, report, _console = _run_browser_use(tmp_path)

    assert code == 0
    assert report["browser_agent_requested"] is True
    assert isinstance(report["browser_agent_available"], bool)
    assert report["deterministic_command_configured"] is True
    assert report["deterministic_command_executed"] is True


@pytest.mark.current_contract
def test_deterministic_command_does_not_claim_browser_success(tmp_path: Path) -> None:
    code, report, _console = _run_browser_use(tmp_path)

    assert code == 0
    assert report["deterministic_command_executed"] is True
    assert report["browser_agent_executed"] is False


@pytest.mark.compat_contract
@pytest.mark.deprecated
def test_fallback_alias_records_compatibility_evidence(tmp_path: Path) -> None:
    code, report, _console = _run_browser_use(tmp_path, option="--fallback-cmd")
    registry = registry_by_id()

    assert code == 0
    assert "browser-fallback-command-name" in registry
    assert report["compat_alias_used"] is True
    assert report["compat_id"] == "browser-fallback-command-name"


@pytest.mark.current_contract
def test_current_templates_prefer_deterministic_command() -> None:
    commands = [
        default_command_for_qa_type("functional", ui_runner="browser-use"),
        default_command_for_qa_type("compatibility", ui_runner="browser-use"),
        default_command_for_qa_type("functional", ui_runner="agent-browser"),
        default_command_for_qa_type("compatibility", ui_runner="agent-browser"),
    ]

    assert all("--deterministic-command" in command for command in commands)
    assert all("--fallback-cmd" not in command for command in commands)


@pytest.mark.current_contract
def test_missing_browser_and_command_fail_closed(tmp_path: Path) -> None:
    code, report, _console = _run_browser_use(tmp_path, command="", include_task=True)

    assert code == 2
    assert report["execution_mode"] == "task-only"
    assert report["deterministic_command_configured"] is False
    assert report["reason_code"] in {
        "browser_agent_unavailable_deterministic_command_missing",
        "browser_task_present_deterministic_command_missing",
    }


@pytest.mark.compat_contract
@pytest.mark.deprecated
def test_no_unrelated_phase_behavior_changes() -> None:
    from beacon.utils import intent_router, memory, prototype_support, qa_runtime

    registry = registry_by_id()

    assert "fallback_cmd" in browser_runner_common.write_runner_artifacts.__annotations__
    assert callable(prototype_support.design_result_adapter_status)
    assert callable(qa_runtime.load_qa_status)
    assert callable(memory._migrate_legacy_to_v1_if_needed)
    assert callable(intent_router.detect_intent)
    assert "qa-auto-test-status-legacy-mirror" in registry
    assert "prd-legacy-machine-mirror" in registry
    assert "prototype-legacy-wireframe-source" in registry
    assert "memory-legacy-projection" in registry
    assert "intent-legacy-router" in registry


@pytest.mark.current_contract
def test_readout_distinguishes_browser_and_command_repair(tmp_path: Path) -> None:
    code, report, console = _run_browser_use(tmp_path, command="", include_task=False)

    assert code == 2
    assert "repair_route" in report
    assert report["browser_agent_repair_route"]
    assert report["deterministic_command_repair_route"]
    assert "browser_agent_repair_route=" in console
    assert "deterministic_command_repair_route=" in console


@pytest.mark.current_contract
def test_agent_browser_accepts_current_deterministic_command(tmp_path: Path) -> None:
    layer_dir = tmp_path / "evidence" / "agent"
    layer_dir.mkdir(parents=True, exist_ok=True)
    script = _write_pass_script(tmp_path)
    task_path = _task_file(tmp_path, layer_dir)
    original_layer_dir = os.environ.get("BEACON_LAYER_DIR")
    os.environ["BEACON_LAYER_DIR"] = str(layer_dir)
    try:
        code = agent_browser_runner.main(
            [
                "--mode",
                "functional",
                "--task-file",
                str(task_path),
                "--deterministic-command",
                f"sh {script}",
                "--project-root",
                str(tmp_path),
            ]
        )
    finally:
        if original_layer_dir is None:
            os.environ.pop("BEACON_LAYER_DIR", None)
        else:
            os.environ["BEACON_LAYER_DIR"] = original_layer_dir

    report = json.loads((layer_dir / "browser-runner-report.json").read_text(encoding="utf-8"))
    assert code == 0
    assert report["runner"] == "agent-browser"
    assert report["execution_mode"] == "deterministic_command"
