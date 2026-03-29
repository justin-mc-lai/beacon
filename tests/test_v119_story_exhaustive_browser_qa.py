from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_v119_control_learning_contract
from beacon.main import app


runner = CliRunner()
ROOT = Path(__file__).resolve().parents[1]
VERSION = "v1.1.9"
FEATURE = "Browser Story Feature"
SLUG = "browser-story-feature"


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
    docs.joinpath("execution", "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    docs.joinpath("release", f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (docs / "user-story" / f"{SLUG}.md").write_text(
        """# User Story

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Login | 用户可以通过页面登录并进入 dashboard |
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
                "feature": SLUG,
                "feature_slug": SLUG,
                "version": VERSION,
                "entries": [
                    {
                        "ac_id": "AC-001",
                        "tc_id": "TC-001",
                        "layer": "functional",
                        "command": "",
                        "assertion": "登录后进入 dashboard",
                        "status": "planned",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _mark_implemented(root: Path, *, run_id: str = "run-browser-impl-001") -> None:
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
        "echo 'BEACON_ASSERTIONS: 0'\n"
        "echo 'fail' >&2\n"
        "exit 1\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def test_v119_test_case_create_should_emit_story_scenario_map(tmp_path: Path):
    _seed_story_docs(tmp_path)

    result = _invoke(
        [
            "test-case",
            "create",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--qa-types",
            "functional",
            "--scenario-depth",
            "standard",
        ]
    )
    assert result.exit_code == 0, result.stdout

    scenario_map = json.loads(
        (tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.story-scenario-map.json").read_text(encoding="utf-8")
    )
    families = {item["scenario_family"] for item in scenario_map["scenarios"]}
    assert scenario_map["expansion_profile"] == "pua-web"
    assert {"happy", "negative", "boundary", "recovery", "compatibility"} <= families
    assert all(item["exploratory_runner"] == "browser-use" for item in scenario_map["scenarios"] if item["browser_required"])
    assert all(item["replay_command"] for item in scenario_map["scenarios"] if item["replay_required"])


def test_v119_qa_evolve_story_exhaustive_should_target_scenarios(tmp_path: Path):
    _seed_story_docs(tmp_path)
    _seed_feature_matrix(tmp_path)
    _mark_implemented(tmp_path)

    result = _invoke(
        [
            "qa",
            "evolve",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--mode",
            "story-exhaustive",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["execution_mode"] == "story-exhaustive"
    assert payload["targeted_scenario_ids"]
    assert payload["required_scenario_families"]
    assert payload["story_scenario_map_path"]


def test_v119_qa_run_story_exhaustive_should_write_browser_evidence_and_exhaustiveness(tmp_path: Path):
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
    assert payload["targeted_scenario_ids"]
    assert payload["exhaustiveness"]["status"] == "passed"

    qa_status = json.loads((tmp_path / ".beacon" / "qa" / "status.json").read_text(encoding="utf-8"))
    assert qa_status["execution_mode"] == "story-exhaustive"
    assert qa_status["evidence_done"] is True
    report = qa_status["exhaustiveness"]
    assert report["browser_scenario_count"] >= 1
    assert report["score"] >= report["threshold"]

    tc_results = qa_status["qa9"]["tc_results"]
    browser_rows = [item for item in tc_results if item.get("browser_required")]
    assert browser_rows
    pack_path = tmp_path / browser_rows[0]["browser_evidence_pack_ref"]
    assert pack_path.exists()
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    task_path = pack_path.parent / "browser-task.json"
    assert task_path.exists()
    task_payload = json.loads(task_path.read_text(encoding="utf-8"))
    assert task_payload["scenario_id"] == browser_rows[0]["scenario_id"]
    assert pack["dom_ref"]
    assert pack["url_ref"]
    assert pack["console_ref"]
    assert pack["network_ref"]
    assert browser_rows[0]["replay_ref"]


def test_v119_story_exhaustive_should_block_dependent_scenarios_when_happy_fails(tmp_path: Path):
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

    qa_status = json.loads((tmp_path / ".beacon" / "qa" / "status.json").read_text(encoding="utf-8"))
    tc_results = qa_status["qa9"]["tc_results"]
    blocked = [item for item in tc_results if item["status"] == "blocked"]
    assert blocked
    assert any(item.get("scenario_family") != "happy" for item in blocked)
    assert qa_status["exhaustiveness"]["status"] == "blocked"


def test_v119_story_exhaustive_should_hard_stop_remaining_cases_for_repair(tmp_path: Path):
    _seed_story_docs(tmp_path)
    _seed_feature_matrix(tmp_path)
    matrix_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix["entries"].append(
        {
            "ac_id": "AC-001",
            "tc_id": "TC-002",
            "layer": "regression",
            "command": "",
            "assertion": "登录失败后其余非关键轮次不应继续误跑",
            "status": "planned",
        }
    )
    matrix_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")
    _mark_implemented(tmp_path)
    fail = _write_fail_script(tmp_path)
    regression = _write_pass_script(tmp_path, name="regression-pass.sh")

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
            f"regression=sh {regression}",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["feature_scorecard"]["continue_decision"] == "stop_for_repair"
    assert "stop_on_fail_triggered" in payload["feature_scorecard"]["stop_reasons"]

    qa_status = json.loads((tmp_path / ".beacon" / "qa" / "status.json").read_text(encoding="utf-8"))
    regression_rows = [item for item in qa_status["qa9"]["tc_results"] if item["source_tc_id"] == "TC-002"]
    assert regression_rows
    assert all(item["status"] == "blocked" for item in regression_rows)
    assert all(item["reason_code"] == "qa_round_stopped_for_repair" for item in regression_rows)


def test_v119_story_exhaustive_should_chain_browser_session_and_runner_evidence(tmp_path: Path):
    _seed_story_docs(tmp_path)
    create = _invoke(
        [
            "test-case",
            "create",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--qa-types",
            "functional",
            "--ui-runner",
            "browser-use",
        ]
    )
    assert create.exit_code == 0, create.stdout
    _mark_implemented(tmp_path)
    session = _invoke(
        [
            "qa",
            "session",
            "save",
            "uat-browser",
            "--project",
            str(tmp_path),
            "--origin",
            "https://example.test/dashboard",
            "--runner-type",
            "browser-use",
            "--profile-ref",
            ".beacon/qa/sessions/uat-browser/profile",
            "--cookies-ref",
            ".beacon/qa/sessions/uat-browser/cookies.json",
            "--storage-state-ref",
            ".beacon/qa/sessions/uat-browser/storage-state.json",
            "--scope",
            "dashboard",
            "--json",
        ]
    )
    assert session.exit_code == 0, session.stdout

    script = _write_pass_script(tmp_path, name="pass-session.sh")
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
    browser_rows = [item for item in payload["per_item_results"] if item.get("browser_required")]
    assert browser_rows

    pack_path = tmp_path / browser_rows[0]["browser_evidence_pack_ref"]
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    assert pack["session_manifest_ref"] == ".beacon/qa/sessions/uat-browser/manifest.json"
    assert pack["cookies_ref"] == ".beacon/qa/sessions/uat-browser/cookies.json"
    assert pack["storage_state_ref"] == ".beacon/qa/sessions/uat-browser/storage-state.json"
    assert pack["explore_runner_report_ref"]
    assert pack["explore_task_ref"]
    assert pack["explore_runner_report_ref"] in pack["evidence_ref"]

    runner_report = json.loads((tmp_path / pack["explore_runner_report_ref"]).read_text(encoding="utf-8"))
    assert runner_report["runner"] == "browser-use"
    assert runner_report["session"]["session_id"] == "uat-browser"
    assert runner_report["artifact_refs"]["session_manifest_ref"] == ".beacon/qa/sessions/uat-browser/manifest.json"


def test_v119_gate_should_block_when_story_exhaustiveness_or_browser_evidence_is_missing(tmp_path: Path):
    _seed_story_docs(tmp_path)
    feature_dir = tmp_path / ".beacon" / "qa" / "features" / SLUG
    feature_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "qa").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "qa" / "status.json").write_text(
        json.dumps(
            {
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "status": "passed",
                "evidence_done": True,
                "execution_mode": "story-exhaustive",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "state" / "learning").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "state" / "eval-lab").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "state" / "learning" / "execution-baseline.json").write_text('{"recommendations":["keep"]}\n', encoding="utf-8")
    (tmp_path / ".beacon" / "state" / "eval-lab" / "benchmark-corpus.json").write_text('{"counts":{"technical_archive_inputs":1}}\n', encoding="utf-8")
    (feature_dir / "exhaustiveness-report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "feature_slug": SLUG,
                "run_id": "run-gate-001",
                "generated_at": "2026-03-28T00:00:00+00:00",
                "execution_mode": "story-exhaustive",
                "scenario_count": 5,
                "browser_scenario_count": 5,
                "required_families": ["happy", "negative", "boundary", "recovery", "compatibility"],
                "passed_families": ["happy"],
                "missing_axes": ["negative", "boundary", "browser_evidence_pack", "deterministic_replay"],
                "missing_replay_scenarios": ["SC-001"],
                "missing_browser_evidence_scenarios": ["SC-001"],
                "score": 0.4,
                "threshold": 0.8,
                "status": "blocked",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    issues = check_v119_control_learning_contract(tmp_path, GateMode.STRICT, "release", VERSION)
    reason_codes = {item["reason_code"] for item in issues}
    assert "story_exhaustiveness_below_threshold" in reason_codes
    assert "required_scenario_family_missing" in reason_codes
    assert "browser_replay_missing" in reason_codes
    assert "browser_evidence_incomplete" in reason_codes
