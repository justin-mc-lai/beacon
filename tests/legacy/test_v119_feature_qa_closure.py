from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.commands.qa import _browser_blocker_lines
from beacon.utils.qa_feature import _executed_acceptance_layers, build_feature_qa_plan, materialize_feature_qa_matrix, writeback_feature_matrix_evidence
from beacon.utils.v110_baseline import load_latest_spec_fingerprint


runner = CliRunner()
VERSION = "v1.1.9"
FEATURE = "Closure Feature"
SLUG = "closure-feature"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_v119_executed_acceptance_layers_should_read_qa9_tc_results() -> None:
    layers = _executed_acceptance_layers(
        scenario_results=[],
        qa_status={
            "qa9": {
                "tc_results": [
                    {"tc_id": "TC-001", "status": "passed", "qa_type": "integration", "evidence_ref": ["evidence.json"]},
                    {"tc_id": "TC-002", "status": "passed", "layer": "contract", "evidence_ref": ["evidence.json"]},
                    {"tc_id": "TC-003", "status": "passed", "qa_type": "unit", "evidence_ref": ["evidence.json"]},
                ]
            }
        },
    )

    assert layers == ["contract", "integration", "unit"]


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Beacon Tests"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "beacon-tests@example.com"], cwd=root, check=True, capture_output=True, text=True)
    (root / ".gitkeep").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "switch", "-c", f"beacon/{VERSION}"], cwd=root, check=True, capture_output=True, text=True)


def _seed_feature_docs(root: Path) -> None:
    if not (root / ".git").exists():
        _init_git_repo(root)
    docs = root / "docs" / "beacon" / VERSION
    (docs / "user-story").mkdir(parents=True, exist_ok=True)
    (docs / "prd").mkdir(parents=True, exist_ok=True)
    (docs / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs / "execution").mkdir(parents=True, exist_ok=True)
    (docs / "release").mkdir(parents=True, exist_ok=True)
    (docs / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (docs / ".machine" / "execution").mkdir(parents=True, exist_ok=True)
    docs.joinpath("SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    docs.joinpath("execution", "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    docs.joinpath("release", f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")

    (docs / "user-story" / f"{SLUG}.md").write_text(
        """# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Control | Feature-aware QA plan exists |\n| AC-002 | Evidence | QA writes per-item verification |\n""",
        encoding="utf-8",
    )
    (docs / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (docs / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
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
                        "layer": "contract",
                        "command": "",
                        "assertion": "feature-aware QA resolves matrix",
                        "status": "planned",
                    },
                    {
                        "ac_id": "AC-002",
                        "tc_id": "TC-002",
                        "layer": "integration",
                        "command": "",
                        "assertion": "QA writes verification evidence and per-item status",
                        "status": "planned",
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _seed_story_scenario_map(root: Path, payload: dict) -> None:
    docs = root / "docs" / "beacon" / VERSION / ".machine" / "qa"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / f"{SLUG}.story-scenario-map.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _seed_team_mode_prechecks(root: Path) -> None:
    docs = root / "docs" / "beacon" / VERSION
    (root / "AGENTS.md").write_text("Use docs/beacon/global-boundaries.md\n", encoding="utf-8")
    (root / "CLAUDE.md").write_text("Use docs/beacon/global-boundaries.md\n", encoding="utf-8")
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    machine_execution = docs / ".machine" / "execution"
    machine_execution.mkdir(parents=True, exist_ok=True)
    (machine_execution / f"implementation-plan-{SLUG}.json").write_text(json.dumps({"plan_id": "plan-001"}), encoding="utf-8")
    (machine_execution / f"git-workflow-{SLUG}.json").write_text(json.dumps({"expected_branch": f"beacon/{VERSION}"}), encoding="utf-8")
    machine_qa = docs / ".machine" / "qa"
    machine_qa.mkdir(parents=True, exist_ok=True)
    ac_matrix_path = machine_qa / f"{SLUG}.ac-test-matrix.json"
    ac_matrix = json.loads(ac_matrix_path.read_text(encoding="utf-8"))
    (machine_qa / f"{SLUG}.qa9-matrix.json").write_text(json.dumps(ac_matrix, ensure_ascii=False, indent=2), encoding="utf-8")
    (machine_qa / f"{SLUG}.story-scenario-map.json").write_text(json.dumps({"feature": SLUG, "scenarios": []}, ensure_ascii=False, indent=2), encoding="utf-8")


def _mark_implemented(root: Path, *, run_id: str = "run-impl-001") -> None:
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


def _write_passing_layer_script(root: Path) -> Path:
    script = root / "pass-layer.sh"
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


def test_v119_qa_evolve_should_compute_feature_delta_plan(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _mark_implemented(tmp_path)

    result = _invoke(["qa", "evolve", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "rerun_required"
    assert payload["implementation_done"] is True
    assert payload["targeted_tc_ids"] == ["TC-001", "TC-002"]
    assert "no_prior_feature_qa" in payload["reason_codes"]


def test_v119_feature_plan_should_rerun_all_entries_when_source_matrix_changes(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _mark_implemented(tmp_path)
    matrix_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix["entries"].append(
        {
            "ac_id": "AC-003",
            "tc_id": "TC-003",
            "layer": "compatibility",
            "command": "",
            "assertion": "compatibility case remains release-facing",
            "status": "planned",
        }
    )
    matrix_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")
    status_path = tmp_path / ".beacon" / "qa" / "features" / SLUG / "status.json"
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(
        json.dumps(
            {
                "status": "passed",
                "evidence_done": True,
                "current_spec_fingerprint_hash": "stale",
                "implementation_run_id": "run-impl-001",
                "source_matrix_path": f"docs/beacon/{VERSION}/.machine/qa/{SLUG}.ac-test-matrix.json",
                "source_matrix_hash": "stale",
                "feature_scorecard": {"coverage_current": {"executed_scenarios": 2}},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = build_feature_qa_plan(tmp_path, version=VERSION, feature=FEATURE, persist=False)

    assert "source_matrix_changed" in payload["reason_codes"]
    assert sorted(payload["targeted_source_tc_ids"]) == ["TC-001", "TC-002", "TC-003"]


def test_v119_feature_plan_should_apply_feature_evidence_contract_overrides(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _mark_implemented(tmp_path)
    contract_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.evidence-contract.json"
    contract_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "tc_overrides": {
                    "TC-001": {
                        "layer": "ui",
                        "qa_type": "functional",
                        "browser_required": True,
                        "command": 'cd "tournament_miniapp" && pnpm exec playwright test e2e/tests/p0-critical/closure-real.spec.ts --project=chromium',
                        "explore_command": 'cd "tournament_miniapp" && pnpm exec playwright test e2e/tests/p0-critical/closure-real.spec.ts --project=chromium',
                        "replay_command": 'cd "tournament_miniapp" && pnpm exec playwright test e2e/tests/p0-critical/closure-real.spec.ts --project=chromium',
                    }
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = build_feature_qa_plan(tmp_path, version=VERSION, feature=FEATURE, persist=False)

    assert payload["feature_evidence_contract_path"].endswith(f"{SLUG}.evidence-contract.json")
    entry = next(item for item in payload["all_entries"] if item["tc_id"] == "TC-001")
    assert entry["qa_type"] == "functional"
    assert entry["layer"] == "ui"
    assert entry["browser_required"] is True
    assert "closure-real.spec.ts" in entry["command"]
    assert "pnpm exec playwright test" in entry["explore_command"]


def test_v119_materialized_feature_qa_matrix_should_preserve_feature_evidence_contract_commands(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _mark_implemented(tmp_path)
    contract_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.evidence-contract.json"
    contract_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "tc_overrides": {
                    "TC-001": {
                        "layer": "ui",
                        "qa_type": "functional",
                        "browser_required": True,
                        "command": 'cd "tournament_miniapp" && pnpm exec playwright test e2e/tests/p0-critical/closure-real.spec.ts --project=chromium',
                        "explore_command": 'cd "tournament_miniapp" && pnpm exec playwright test e2e/tests/p0-critical/closure-real.spec.ts --project=chromium',
                    }
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    plan = build_feature_qa_plan(tmp_path, version=VERSION, feature=FEATURE, persist=False)
    matrix_path = materialize_feature_qa_matrix(tmp_path, plan=plan)
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

    entry = next(item for item in matrix["entries"] if item["tc_id"] == "TC-001")
    assert entry["qa_type"] == "functional"
    assert entry["layer"] == "ui"
    assert entry["browser_required"] is True
    assert "closure-real.spec.ts" in entry["command"]
    assert "closure-real.spec.ts" in entry["explore_command"]


def test_v119_qa_run_help_should_expose_feature_aware_options():
    result = _invoke(["qa", "run", "--help"])
    assert result.exit_code == 0, result.stdout
    assert "FEATURE" in result.stdout
    assert "--project" in result.stdout
    assert "--version" in result.stdout
    assert "--json" in result.stdout


def test_v119_qa_status_should_print_browser_blocker_guidance(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    writeback_feature_matrix_evidence(
        tmp_path,
        plan={"feature": FEATURE, "feature_slug": SLUG, "version": VERSION, "targeted_tc_ids": [], "targeted_ac_ids": [], "targeted_layers": []},
        per_item_results=[],
        run_id="run-browser-status-001",
    )
    (tmp_path / ".beacon" / "qa").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "qa" / "status.json").write_text(
        json.dumps(
            {
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "status": "blocked",
                "evidence_done": False,
                "execution_mode": "feature-aware",
                "feature_scorecard": {
                    "continue_decision": "stop_for_repair",
                    "stop_reasons": ["protected_surface_session_bridge_missing"],
                    "resume_command": f'beacon help --project-root {tmp_path} --version {VERSION} --feature "{FEATURE}"',
                    "repair_handoff": {
                        "action": "qa-session",
                        "reason": "protected browser surface requires an attached session or runner before QA can continue",
                        "command": f"beacon qa session list --project {tmp_path}",
                    },
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    result = _invoke(["qa", "status", "--project", str(tmp_path)])

    assert result.exit_code == 0, result.stdout
    assert "browser_blockers: protected_surface_session_bridge_missing" in result.stdout
    assert "browser_command: beacon qa session list" in result.stdout


def test_v119_browser_blocker_lines_should_render_session_guidance() -> None:
    lines = _browser_blocker_lines(
        {
            "continue_decision": "stop_for_repair",
            "stop_reasons": ["protected_surface_runner_priority_unavailable"],
            "repair_handoff": {
                "action": "qa-session",
                "reason": "browser QA is blocked on attached-session admission and needs a reusable QA session before rerun",
                "command": "beacon qa session list --project /tmp/demo",
            },
        }
    )

    assert any("browser_blockers: protected_surface_runner_priority_unavailable" in line for line in lines)
    assert any("browser_command: beacon qa session list --project /tmp/demo" in line for line in lines)


def test_v119_qa_evolve_story_exhaustive_should_backfill_missing_scenarios_from_matrix_entries(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _mark_implemented(tmp_path)
    _seed_story_scenario_map(
        tmp_path,
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "scenarios": [
                {
                    "scenario_id": "SC-001",
                    "source_tc_id": "TC-001",
                    "tc_id": "TC-001-PRIMARY",
                    "ac_id": "AC-001",
                    "scenario_family": "primary",
                    "qa_type": "contract",
                    "browser_required": False,
                    "replay_required": False,
                }
            ],
            "stories": [
                {
                    "ac_id": "AC-001",
                    "theme": "Control",
                    "text": "Feature-aware QA plan exists",
                    "scenario_ids": ["SC-001"],
                    "scenario_families": ["primary"],
                    "required_families": [],
                    "scenarios": [
                        {
                            "scenario_id": "SC-001",
                            "source_tc_id": "TC-001",
                            "tc_id": "TC-001-PRIMARY",
                            "scenario_family": "primary",
                            "qa_type": "contract",
                            "browser_required": False,
                            "replay_required": False,
                        }
                    ],
                }
            ],
        },
    )
    matrix_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix["entries"][1]["ac_id"] = "AC-101"
    matrix_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")

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
    assert sorted(payload["targeted_source_tc_ids"]) == ["TC-001", "TC-002"]
    assert sorted(payload["targeted_scenario_ids"]) == ["SC-001", "SC-AUTO-TC-002"]
    stories = payload["story_scenarios"]["stories"]
    ac_101 = next(item for item in stories if item["ac_id"] == "AC-101")
    assert ac_101["scenario_ids"] == ["SC-AUTO-TC-002"]


def test_v119_qa_evolve_no_write_matrix_should_not_materialize_state_files(tmp_path: Path):
    _seed_feature_docs(tmp_path)
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
            "--no-write-matrix",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "rerun_required"

    feature_root = tmp_path / ".beacon" / "qa" / "features" / SLUG
    assert not feature_root.exists()
    docs_story_map = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.story-scenario-map.json"
    assert not docs_story_map.exists()



def test_v119_qa_run_feature_should_write_per_item_verification(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _mark_implemented(tmp_path)
    script = _write_passing_layer_script(tmp_path)

    result = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--layer-command",
            f"contract=sh {script}",
            "--layer-command",
            f"integration=sh {script}",
        ]
    )
    assert result.exit_code == 0, result.stdout

    qa_status = json.loads((tmp_path / ".beacon" / "qa" / "status.json").read_text(encoding="utf-8"))
    assert qa_status["feature"] == FEATURE
    assert qa_status["status"] == "passed"
    assert qa_status["evidence_done"] is True
    assert qa_status["targeted_rerun"]["targeted_tc_ids"] == ["TC-001", "TC-002"]
    assert qa_status["boundary_evidence"]["assumption_capture_required"] is True
    assert qa_status["boundary_evidence"]["goal_driven_verification_required"] is True
    assert qa_status["boundary_evidence"]["verification_item_count"] >= 2

    feature_status = json.loads((tmp_path / ".beacon" / "qa" / "features" / SLUG / "status.json").read_text(encoding="utf-8"))
    assert feature_status["verified_item_ids"] == ["AC-001", "AC-002", "TEST-001", "TEST-002"]
    assert feature_status["failed_item_ids"] == []

    coverage_summary = json.loads((tmp_path / ".beacon" / "coverage-summary.json").read_text(encoding="utf-8"))
    assert coverage_summary["version"] == VERSION
    assert coverage_summary["run_id"] == qa_status["run_id"]
    assert coverage_summary["full_coverage"] is True
    assert coverage_summary["details"]["total_tc"] == 2
    assert coverage_summary["details"]["executed_tc"] == 2

    feature_scorecard = json.loads((tmp_path / ".beacon" / "qa" / "features" / SLUG / "scorecard.json").read_text(encoding="utf-8"))
    assert feature_scorecard["boundary_evidence"]["goal_driven_verification_required"] is True
    assert feature_scorecard["boundary_evidence"]["targeted_scope_only"] is True

    story_state = json.loads((tmp_path / "docs" / "beacon" / VERSION / ".machine" / "user-story" / f"{SLUG}.json").read_text(encoding="utf-8"))
    active_story = next(item for item in story_state["stories"] if item["revision_id"] == story_state["current_revision_id"])
    statuses = {item["id"]: item["status"] for item in active_story["items"]}
    assert statuses["AC-001"] == "verified"
    assert statuses["AC-002"] == "verified"
    assert statuses["TEST-001"] == "passed"
    assert statuses["TEST-002"] == "passed"

    release_check = _invoke(["release", "check", VERSION, "--project", str(tmp_path)])
    assert release_check.exit_code == 0, release_check.stdout


def test_v119_qa_run_team_mode_should_not_forward_runtime_to_auto_test(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _seed_team_mode_prechecks(tmp_path)
    _mark_implemented(tmp_path)
    script = _write_passing_layer_script(tmp_path)

    result = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--team-mode",
            "--runtime",
            "file",
            "--layer-command",
            f"contract=sh {script}",
            "--layer-command",
            f"integration=sh {script}",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "passed"
    assert payload["execution_surface"] == "qa-team"
    assert payload["team_execution"]["runtime"] == "file"


def test_v119_qa_run_should_block_when_auto_test_invocation_fails_even_if_stale_status_looks_passed(
    tmp_path: Path,
    monkeypatch,
):
    _seed_feature_docs(tmp_path)
    _seed_team_mode_prechecks(tmp_path)
    _mark_implemented(tmp_path)

    def fake_exec(_args, *, cwd=None):
        return 2

    def fake_load_status(_project_root):
        return {
            "run_id": "run-pass-001",
            "status": "passed",
            "evidence_done": True,
            "execution": {"layers": []},
            "qa9": {"summary": {}, "tc_results": []},
        }

    monkeypatch.setattr("beacon.commands.qa._beacon_exec_silent", fake_exec)
    monkeypatch.setattr("beacon.commands.qa.load_qa_status", fake_load_status)

    result = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--team-mode",
            "--runtime",
            "file",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert "auto_test_invocation_failed" in payload["reason_codes"]


def test_v119_qa_run_should_execute_manual_and_mixed_cases_when_layer_command_is_explicit(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _mark_implemented(tmp_path)
    script = _write_passing_layer_script(tmp_path)

    matrix_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    entries = matrix.get("entries", [])
    entries[0]["layer"] = "contract"
    entries[0]["qa_type"] = "contract"
    entries[0]["automation"] = "manual"
    entries[1]["layer"] = "integration"
    entries[1]["qa_type"] = "integration"
    entries[1]["automation"] = "mixed"
    matrix_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")

    result = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--layer-command",
            f"contract=sh {script}",
            "--layer-command",
            f"integration=sh {script}",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    statuses = {item["tc_id"]: item["status"] for item in payload["per_item_results"]}
    assert statuses == {"TC-001": "passed", "TC-002": "passed"}


def test_v119_qa_run_should_sync_latest_spec_fingerprint_into_auto_test_status(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _mark_implemented(tmp_path)
    script = _write_passing_layer_script(tmp_path)

    result = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--layer-command",
            f"contract=sh {script}",
            "--layer-command",
            f"integration=sh {script}",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    latest_fingerprint = load_latest_spec_fingerprint(tmp_path, version=VERSION)
    auto_status = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    assert auto_status["spec_fingerprint_hash"] == latest_fingerprint["fingerprint_hash"]



def test_v119_materialized_feature_qa_matrix_should_use_run_scoped_evidence_paths(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _mark_implemented(tmp_path)

    evolve = _invoke(["qa", "evolve", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert evolve.exit_code == 0, evolve.stdout

    plan = json.loads((tmp_path / ".beacon" / "qa" / "features" / SLUG / "plan.json").read_text(encoding="utf-8"))
    matrix_path = tmp_path / ".beacon" / "qa" / "features" / SLUG / "matrix.qa9.json"
    assert matrix_path.exists()
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    assert matrix["source_matrix_path"].endswith(f"{SLUG}.ac-test-matrix.json")
    for entry in matrix["entries"]:
        assert "__RUN_ID__" in entry["evidence_path"]
        assert f".beacon/evidence/qa-feature/{SLUG}/" in entry["evidence_path"]
    assert plan["targeted_tc_ids"] == ["TC-001", "TC-002"]


def test_v119_qa_writeback_should_preserve_run_scoped_matrix_evidence_templates(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    source_matrix_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.qa9-matrix.json"
    source_matrix = json.loads(
        (tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").read_text(encoding="utf-8")
    )
    for entry in source_matrix["entries"]:
        tc_id = entry["tc_id"]
        entry["qa_type"] = entry["layer"]
        entry["evidence_path"] = f".beacon/evidence/test-results/{SLUG}/{{run_id}}/{tc_id}.json"
    source_matrix_path.write_text(json.dumps(source_matrix, ensure_ascii=False, indent=2), encoding="utf-8")

    plan = {
        "source_matrix_path": str(source_matrix_path.relative_to(tmp_path)),
    }
    per_item_results = [
        {
            "source_tc_id": "TC-001",
            "status": "passed",
            "evidence_ref": [".beacon/evidence/auto-test/run-123/qa9-tc/TC-001/command.txt"],
        },
        {
            "source_tc_id": "TC-002",
            "status": "passed",
            "evidence_ref": [".beacon/evidence/auto-test/run-123/qa9-tc/TC-002/command.txt"],
        },
    ]

    updated = writeback_feature_matrix_evidence(
        tmp_path,
        plan=plan,
        per_item_results=per_item_results,
        run_id="run-123",
    )
    assert updated == source_matrix_path

    source_matrix = json.loads(source_matrix_path.read_text(encoding="utf-8"))
    for entry in source_matrix["entries"]:
        assert "{run_id}" in entry["evidence_path"]
    tc001 = next(entry for entry in source_matrix["entries"] if entry["tc_id"] == "TC-001")
    tc002 = next(entry for entry in source_matrix["entries"] if entry["tc_id"] == "TC-002")
    assert tc001["last_run_id"] == "run-123"
    assert tc002["last_run_id"] == "run-123"
    assert tc001["last_evidence_ref"].startswith(".beacon/evidence/auto-test/")
    assert tc002["last_evidence_ref"].startswith(".beacon/evidence/auto-test/")


def test_v119_auto_test_should_refresh_coverage_summary_for_current_run(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _mark_implemented(tmp_path)
    script = _write_passing_layer_script(tmp_path)
    qa_matrix = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json"
    qa9_matrix = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.qa9-matrix.json"
    qa9_matrix.write_text(qa_matrix.read_text(encoding="utf-8"), encoding="utf-8")

    result = _invoke(
        [
            "auto-test",
            "create",
            "qa9",
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--qa-matrix-path",
            str(qa9_matrix),
            "--layer-command",
            f"contract=sh {script}",
            "--layer-command",
            f"integration=sh {script}",
        ]
    )
    assert result.exit_code == 0, result.stdout

    auto_status = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    coverage_summary = json.loads((tmp_path / ".beacon" / "coverage-summary.json").read_text(encoding="utf-8"))
    assert coverage_summary["run_id"] == auto_status["run_id"]
    assert coverage_summary["version"] == VERSION


def test_v119_auto_test_should_respect_explicit_qa_types_over_matrix_defaults(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _mark_implemented(tmp_path)
    script = _write_passing_layer_script(tmp_path)
    qa9_matrix = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.qa9-matrix.json"
    qa9_payload = {
        "schema_version": "1.0",
        "feature": SLUG,
        "feature_slug": SLUG,
        "version": VERSION,
        "qa_types": ["contract", "integration", "functional", "compatibility"],
        "entries": [
            {
                "tc_id": "TC-001",
                "ac_id": "AC-001",
                "layer": "contract",
                "qa_type": "contract",
                "command": f"sh {script}",
                "automation": "auto",
                "assertion": "contract passes",
                "evidence_path": f".beacon/evidence/test-results/{SLUG}/{{run_id}}/TC-001.json",
            },
            {
                "tc_id": "TC-002",
                "ac_id": "AC-002",
                "layer": "integration",
                "qa_type": "integration",
                "command": f"sh {script}",
                "automation": "auto",
                "assertion": "integration passes",
                "evidence_path": f".beacon/evidence/test-results/{SLUG}/{{run_id}}/TC-002.json",
            },
        ],
    }
    qa9_matrix.write_text(json.dumps(qa9_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    result = _invoke(
        [
            "auto-test",
            "create",
            "qa9",
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--qa-matrix-path",
            str(qa9_matrix),
            "--qa-types",
            "contract,integration",
        ]
    )
    assert result.exit_code == 0, result.stdout

    auto_status = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    assert auto_status["status"] == "passed"
    assert auto_status["selected_layers"] == ["contract", "integration"]
    tc_results = auto_status["qa9"]["tc_results"]
    assert {item["tc_id"] for item in tc_results} == {"TC-001", "TC-002"}
    assert {item["qa_type"] for item in tc_results} == {"contract", "integration"}



def test_v119_implement_should_write_artifact_update_obligations(tmp_path: Path):
    _seed_feature_docs(tmp_path)

    freeze = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert freeze.exit_code == 0, freeze.stdout

    impl = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--runner",
            "native-single",
            "--json",
        ]
    )
    assert impl.exit_code == 0, impl.stdout
    impl_payload = json.loads(impl.stdout)
    assert impl_payload["artifact_writeback_open_count"] == 2
    obligations_path = tmp_path / impl_payload["artifact_writeback_obligations"]
    assert obligations_path.exists()
    rewrite_input = tmp_path / impl_payload["requirement_rewrite_input"]
    assert rewrite_input.exists()

    obligations = json.loads(obligations_path.read_text(encoding="utf-8"))
    names = {item["artifact"] for item in obligations["obligations"]}
    assert names == {"review_quality", "acceptance"}
    corpus = json.loads((tmp_path / ".beacon" / "state" / "eval-lab" / "benchmark-corpus.json").read_text(encoding="utf-8"))
    assert corpus["counts"]["technical_archive_inputs"] >= 1
    baseline = json.loads((tmp_path / ".beacon" / "state" / "learning" / "execution-baseline.json").read_text(encoding="utf-8"))
    assert baseline["recommendations"]

    evolve = _invoke(["qa", "evolve", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert evolve.exit_code == 0, evolve.stdout
    evolve_payload = json.loads(evolve.stdout)
    assert "artifact_updates_pending" in evolve_payload["reason_codes"]
    blocking = {item["artifact"] for item in evolve_payload["blocking_artifact_updates"]}
    assert blocking == {"review_quality"}


def test_v119_review_quality_and_accept_should_close_formal_obligations(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    script = _write_passing_layer_script(tmp_path)

    freeze = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert freeze.exit_code == 0, freeze.stdout

    impl = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--runner",
            "native-single",
            "--json",
        ]
    )
    assert impl.exit_code == 0, impl.stdout

    qa = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--layer-command",
            f"contract=sh {script}",
            "--layer-command",
            f"integration=sh {script}",
        ]
    )
    assert qa.exit_code == 0, qa.stdout

    quality = _invoke(["review", "quality", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert quality.exit_code == 0, quality.stdout
    quality_payload = json.loads(quality.stdout)
    assert quality_payload["status"] == "pass"
    assert quality_payload["gate_ready"] is True

    accept = _invoke(["review", "accept", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert accept.exit_code == 0, accept.stdout
    accept_payload = json.loads(accept.stdout)
    assert accept_payload["status"] == "accepted"

    obligations = json.loads((tmp_path / ".beacon" / "state" / "artifact-update-obligations" / f"{SLUG}.json").read_text(encoding="utf-8"))
    statuses = {item["artifact"]: item["status"] for item in obligations["obligations"]}
    assert statuses["review_quality"] == "completed"
    assert statuses["acceptance"] == "completed"


def test_v119_feature_qa_should_ignore_unselected_story_scenario_families(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _seed_story_scenario_map(
        tmp_path,
        {
            "schema_version": "1.0",
            "feature": SLUG,
            "feature_slug": SLUG,
            "stories": [
                {
                    "ac_id": "AC-001",
                    "required_families": ["happy", "negative"],
                    "scenarios": [
                        {"scenario_id": "SC-001", "source_tc_id": "TC-001", "scenario_family": "primary"},
                        {"scenario_id": "SC-002", "source_tc_id": "TC-099", "scenario_family": "happy"},
                        {"scenario_id": "SC-003", "source_tc_id": "TC-099", "scenario_family": "negative"},
                    ],
                },
                {
                    "ac_id": "AC-002",
                    "required_families": [],
                    "scenarios": [
                        {"scenario_id": "SC-004", "source_tc_id": "TC-002", "scenario_family": "primary"},
                    ],
                },
            ],
            "scenarios": [],
        },
    )
    _mark_implemented(tmp_path)
    script = _write_passing_layer_script(tmp_path)

    result = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--layer-command",
            f"contract=sh {script}",
            "--layer-command",
            f"integration=sh {script}",
        ]
    )
    assert result.exit_code == 0, result.stdout

    qa_status = json.loads((tmp_path / ".beacon" / "qa" / "status.json").read_text(encoding="utf-8"))
    assert qa_status["release_ready"] is True
    ac_closure = json.loads((tmp_path / ".beacon" / "qa" / "features" / SLUG / "ac-closure.json").read_text(encoding="utf-8"))
    blocked = [item for item in ac_closure["reports"] if item["closure_status"] != "accepted"]
    assert blocked == []
