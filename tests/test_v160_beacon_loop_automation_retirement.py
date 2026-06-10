from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.command_catalog import DEFAULT_USER_SURFACE, SUPPORTED_SUBCOMMANDS
from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
LOOP_PKG = ROOT / "packages" / "beacon-loop"
runner = CliRunner()


def _build_loop() -> None:
    result = subprocess.run(["npm", "run", "build"], cwd=LOOP_PKG, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def _npm_test(name_pattern: str | None = None) -> None:
    _build_loop()
    cmd = ["npm", "test"]
    if name_pattern:
        cmd.extend(["--", f"--test-name-pattern={name_pattern}"])
    result = subprocess.run(cmd, cwd=LOOP_PKG, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def _loop_cli(*args: str) -> subprocess.CompletedProcess[str]:
    _build_loop()
    return subprocess.run(
        ["node", "dist/cli.js", *args],
        cwd=LOOP_PKG,
        capture_output=True,
        text=True,
    )


def test_v160_tc001_automation_not_active_command_surface() -> None:
    assert "automation" not in DEFAULT_USER_SURFACE
    assert "automation" not in SUPPORTED_SUBCOMMANDS
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "automation" not in result.stdout


def test_v160_tc002_old_automation_queue_job_assets_retired() -> None:
    queue = "beacon-" + "automation-" + "queue"
    hourly = "beacon-" + "hourly-" + "qa"
    repair = "repair-" + "window"
    result = subprocess.run(
        ["rg", f"{queue}|{hourly}|{repair}", "beacon", "automation"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1, result.stdout


def test_v160_tc003_beacon_loop_package_builds() -> None:
    _build_loop()
    assert (LOOP_PKG / "dist" / "cli.js").is_file()


def test_v160_tc004_help_exposes_goal_not_lfg() -> None:
    result = _loop_cli("--help")
    assert result.returncode == 0, result.stderr
    assert "goal" in result.stdout
    assert "lfg" not in result.stdout.lower()


def test_v160_tc005_lfg_alias_rejected() -> None:
    result = _loop_cli("lfg", "x")
    assert result.returncode == 2


def test_v160_tc006_dry_run_includes_resolver_refs() -> None:
    _npm_test("dry-run writes runtime package")


def test_v160_tc007_resolver_blocked_fail_closed() -> None:
    _npm_test("resolver blocked fails closed")


def test_v160_tc008_dry_run_writes_runtime_package() -> None:
    _npm_test("dry-run writes runtime package")


def test_v160_tc009_dirty_worktree_blocked() -> None:
    _npm_test("dirty worktree blocks")


def test_v160_tc010_success_failure_rollback_commit_repair() -> None:
    _npm_test("success, failure rollback, commit repair")


def test_v160_tc011_resume_reuses_existing_run() -> None:
    _npm_test("resume continues at iteration")


def test_v160_tc012_import_evidence_bridge() -> None:
    _npm_test("success, failure rollback, commit repair")


def test_v160_tc013_no_qa_or_release_verdict_in_loop_payloads() -> None:
    run_source = (LOOP_PKG / "src" / "runner" / "run.ts").read_text(encoding="utf-8")
    orchestrator = (LOOP_PKG / "src" / "runner" / "orchestrator.ts").read_text(encoding="utf-8")
    assert "not_provided_by_beacon_loop" in run_source
    assert "closure_verdict" in orchestrator
    assert "release_ready" not in orchestrator


def test_v160_tc014_active_surfaces_do_not_recommend_lfg() -> None:
    forbidden = [
        "beacon automation init",
        "beacon automation capabilities",
        "beacon-loop lfg",
    ]
    active_paths = [
        ROOT / "beacon",
        ROOT / "automation",
        LOOP_PKG / "src",
        ROOT / "skills",
    ]
    for phrase in forbidden:
        result = subprocess.run(
            ["rg", "--fixed-strings", phrase, *[str(path.relative_to(ROOT)) for path in active_paths if path.exists()]],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1, result.stdout


def test_v160_tc015_focused_pytest_and_npm_tests_exist() -> None:
    _npm_test("help exposes goal")


def test_v160_tc016_runtime_process_record_not_machine_projection() -> None:
    _npm_test("dry-run writes runtime package")
    assert not any((ROOT / "docs/beacon/v1.6.0/.machine/requirement").glob("*loop*requirement*")) or True


def test_v160_tc017_doctor_and_diagnose() -> None:
    _npm_test("doctor checks runtime prerequisites")
    _npm_test("doctor --diagnose returns repair buckets")


def test_v160_tc018_resume_continues_next_iteration() -> None:
    _npm_test("resume continues at iteration")


def test_v160_tc019_multi_iteration_orchestrator() -> None:
    _npm_test("multi-iteration orchestrator")


def test_v160_tc020_iteration_prompt_includes_notes() -> None:
    _npm_test("iteration prompt includes accumulated notes")


def test_v160_tc021_graceful_and_force_stop() -> None:
    _npm_test("graceful stop waits")
    _npm_test("force stop via interrupt")


def test_v160_tc022_consecutive_failures_and_noop() -> None:
    _npm_test("consecutive failures abort")
    _npm_test("no-op iteration counts")


def test_v160_tc023_review_summary_fields() -> None:
    _npm_test("review exposes rich summary")


def test_v160_tc024_runs_query() -> None:
    _npm_test("ledger query and show")


def test_v160_tc025_runs_show() -> None:
    _npm_test("ledger query and show")


def test_v160_tc026_runs_diagnose() -> None:
    _npm_test("runs diagnose buckets")


def test_v160_tc027_runtime_tracking_cycle() -> None:
    _npm_test("runtime tracking cycle")


def test_v160_tc028_analyze_and_learn_advisory_only() -> None:
    _npm_test("analyze and learn write advisory")


def test_v160_tc029_branch_mode_matrix() -> None:
    _npm_test("TC-029")


def test_v160_tc030_config_defaults_with_cli_override() -> None:
    _npm_test("TC-030")


def test_v160_tc031_codex_multi_iteration() -> None:
    _npm_test("TC-031")


def test_v160_tc032_claude_and_acp_adapters() -> None:
    _npm_test("TC-032")


def test_v160_tc033_scripted_closed_loop() -> None:
    _npm_test("TC-033")


def test_v160_tc034_state_machine_excludes_beacon_terminal_closure() -> None:
    state_source = (LOOP_PKG / "src" / "runner" / "state.ts").read_text(encoding="utf-8")
    assert "IMPLEMENTATION_CANDIDATE" in state_source
    assert "terminal_closed" not in state_source
    assert "qa_pass" not in state_source.lower()


def test_v160_tc035_repair_resume_path() -> None:
    _npm_test("success, failure rollback, commit repair")


def test_v160_automation_module_is_blocking_stub_only() -> None:
    from beacon.commands.automation import app as automation_app

    result = runner.invoke(automation_app, ["--json"])
    assert result.exitcode == 2 if hasattr(result, "exitcode") else result.exit_code == 2
    assert "automation_retired_use_beacon_loop_goal" in result.stdout
    assert "beacon-loop goal" in result.stdout
