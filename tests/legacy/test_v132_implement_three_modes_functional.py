from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.help_support import build_help_payload
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime import write_json
from beacon.utils.writeback import record_implementation_writeback


runner = CliRunner()
ROOT = Path(__file__).resolve().parents[1]
VERSION = "v1.3.2"
FEATURE = "beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa"
SLUG = "beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_story_docs(root: Path) -> None:
    docs = root / "docs" / "beacon" / VERSION
    (docs / "user-story").mkdir(parents=True, exist_ok=True)
    (docs / "prd").mkdir(parents=True, exist_ok=True)
    (docs / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (docs / ".machine" / "execution").mkdir(parents=True, exist_ok=True)
    (docs / "execution").mkdir(parents=True, exist_ok=True)
    (docs / "release").mkdir(parents=True, exist_ok=True)
    docs.joinpath("SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    docs.joinpath("execution", "index.md").write_text("# Execution\n", encoding="utf-8")
    docs.joinpath("execution", "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    docs.joinpath("release", f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (docs / "user-story" / f"{SLUG}.md").write_text(
        """# User Story

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-004 | QA | qa 是与 implement 对应的第二执行面 |
| AC-006 | QA | qa 必须围绕真实浏览器环境执行 |
| AC-007 | QA | qa 必须支持按轮次顺序推进 |
| AC-008 | QA | 每轮 qa 都必须带来新的 research 增量 |
| AC-010 | QA | qa 应逐轮打磨正确性与边界 |
| AC-012 | Help | help/status 必须显示 mode、轮次、runner、blocker 与下一步 |
""",
        encoding="utf-8",
    )
    (docs / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")


def _seed_feature_matrix(root: Path) -> None:
    docs = root / "docs" / "beacon" / VERSION
    (docs / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "entries": [
                    {
                        "ac_id": "AC-004",
                        "tc_id": "TC-004",
                        "layer": "functional",
                        "command": "",
                        "assertion": "qa 成为第二执行面，并输出浏览器证据与下一步",
                        "status": "planned",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _mark_implemented(root: Path, *, run_id: str = "run-v132-impl-001") -> None:
    freeze_revision_state(root, version=VERSION, feature=FEATURE)
    marker = root / ".beacon" / "state"
    marker.mkdir(parents=True, exist_ok=True)
    (marker / f"implementation-{SLUG}.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": run_id,
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "status": "completed",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_pass_script(root: Path, name: str = "pass-browser.sh") -> Path:
    script = root / name
    script.write_text(
        "#!/bin/sh\n"
        "set -eu\n"
        "mkdir -p \"$(dirname \"$BEACON_JUNIT_PATH\")\"\n"
        "cat > \"$BEACON_JUNIT_PATH\" <<'XML'\n"
        "<testsuite tests=\"1\"><testcase classname=\"qa\" name=\"ok\"/></testsuite>\n"
        "XML\n"
        "echo 'BEACON_ASSERTIONS: 1'\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def _write_fail_script(root: Path, name: str = "fail-browser.sh") -> Path:
    script = root / name
    script.write_text(
        "#!/bin/sh\n"
        "set -eu\n"
        "mkdir -p \"$(dirname \"$BEACON_JUNIT_PATH\")\"\n"
        "cat > \"$BEACON_JUNIT_PATH\" <<'XML'\n"
        "<testsuite tests=\"1\"><testcase classname=\"qa\" name=\"fail\"><failure message=\"blocked\"/></testcase></testsuite>\n"
        "XML\n"
        "echo 'BEACON_ASSERTIONS: 0'\n"
        "echo 'blocked for repair' >&2\n"
        "exit 1\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def test_v132_functional_help_should_expose_implement_mode_runner_and_browser_observability(tmp_path: Path):
    _seed_story_docs(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    record_implementation_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-complete",
        implemented_item_ids=["AC-004", "AC-006", "AC-007", "AC-008", "AC-010", "AC-012"],
        changed_files=["beacon/utils/help_support.py"],
    )
    write_json(
        tmp_path / ".beacon" / "implement" / "run-complete" / "state.json",
        {
            "schema_version": "1.0",
            "run_id": "run-complete",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "completed",
            "runner": "codex-subagents",
            "mode": "team",
            "host_runtime": "codex",
            "subagent_prechecks": {
                "runtime_readiness": {"status": "pass"},
                "delegation_readiness": {"status": "pass"},
            },
            "generated_at": "2026-04-16T12:00:00+00:00",
        },
    )
    write_json(
        tmp_path / ".beacon" / "qa" / "status.json",
        {
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "blocked",
            "evidence_done": False,
            "execution_mode": "story-exhaustive",
            "run_id": "run-qa",
        },
    )
    write_json(
        tmp_path / ".beacon" / "qa" / "current-session.json",
        {
            "schema_version": "1.0",
            "session_id": "session-001",
            "runner_type": "browser-use",
            "updated_at": "now",
        },
    )
    write_json(
        tmp_path / ".beacon" / "ralph" / f"{SLUG}.json",
        {
            "schema_version": "1.1",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "phase": "completed",
            "stop_state": "human_blocked",
            "current_blocker": "fix blocker",
            "next_action": "implement",
            "recommended_command": f'beacon implement run "{FEATURE}" --project {tmp_path} --version {VERSION} --runner native-single',
            "round_count": 2,
            "last_round_ref": f"docs/beacon/{VERSION}/.machine/trace/ralph/{SLUG}/ralph-round-{SLUG}-round-002.json",
            "failure_streak": 1,
            "no_delta_streak": 0,
        },
    )

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    execution = payload["execution_surface"]
    assert execution["implement_mode"] == "team"
    assert execution["implement_runner"] == "codex-subagents"
    assert execution["qa_execution_mode"] == "story-exhaustive"
    assert execution["qa_current_session_id"] == "session-001"
    assert execution["qa_runner_type"] == "browser-use"
    assert execution["ralph_round_count"] == 2
    assert payload["next_step"]["command"].startswith("beacon implement run")


def test_v132_functional_qa_should_write_browser_evidence_for_story_exhaustive_round(tmp_path: Path):
    _seed_story_docs(tmp_path)
    _seed_feature_matrix(tmp_path)
    _mark_implemented(tmp_path)
    script = _write_pass_script(tmp_path)

    result = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--mode",
            "story-exhaustive",
            "--layer-command",
            f'functional=PYTHONPATH={ROOT} python3 -m beacon.adapters.browser_use_runner --mode functional --fallback-cmd "sh {script}"',
            "--layer-command",
            f'compatibility=PYTHONPATH={ROOT} python3 -m beacon.adapters.browser_use_runner --mode compatibility --fallback-cmd "sh {script}"',
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "passed"
    assert payload["execution_mode"] == "story-exhaustive"
    assert payload["targeted_scenario_ids"]
    assert "compatibility" in payload["required_scenario_families"]
    assert payload["feature_scorecard"]["coverage_current"]["executed_scenarios"] >= 1

    qa_status = json.loads((tmp_path / ".beacon" / "qa" / "status.json").read_text(encoding="utf-8"))
    assert qa_status["execution_mode"] == "story-exhaustive"
    assert qa_status["evidence_done"] is True
    browser_rows = [item for item in qa_status["qa9"]["tc_results"] if item.get("browser_required")]
    assert browser_rows
    pack_path = tmp_path / browser_rows[0]["browser_evidence_pack_ref"]
    assert pack_path.exists()
    task_path = pack_path.parent / "browser-task.json"
    assert task_path.exists()


def test_v132_functional_qa_should_stop_for_repair_when_browser_round_fails(tmp_path: Path):
    _seed_story_docs(tmp_path)
    _seed_feature_matrix(tmp_path)
    _mark_implemented(tmp_path)
    fail = _write_fail_script(tmp_path)
    compat = _write_pass_script(tmp_path, name="compat-pass.sh")

    result = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--mode",
            "story-exhaustive",
            "--layer-command",
            f"functional=sh {fail}",
            "--layer-command",
            f"compatibility=sh {compat}",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["feature_scorecard"]["continue_decision"] == "stop_for_repair"
    assert "stop_on_fail_triggered" in payload["feature_scorecard"]["stop_reasons"]
