from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.v110_baseline import load_latest_spec_fingerprint


runner = CliRunner()
VERSION = "v1.1.9"
FEATURE = "Closure Feature"
SLUG = "closure-feature"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


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

    feature_status = json.loads((tmp_path / ".beacon" / "qa" / "features" / SLUG / "status.json").read_text(encoding="utf-8"))
    assert feature_status["verified_item_ids"] == ["AC-001", "AC-002", "TEST-001", "TEST-002"]
    assert feature_status["failed_item_ids"] == []

    story_state = json.loads((tmp_path / "docs" / "beacon" / VERSION / ".machine" / "user-story" / f"{SLUG}.json").read_text(encoding="utf-8"))
    active_story = next(item for item in story_state["stories"] if item["revision_id"] == story_state["current_revision_id"])
    statuses = {item["id"]: item["status"] for item in active_story["items"]}
    assert statuses["AC-001"] == "verified"
    assert statuses["AC-002"] == "verified"
    assert statuses["TEST-001"] == "passed"
    assert statuses["TEST-002"] == "passed"


def test_v119_qa_run_team_mode_should_not_forward_runtime_to_auto_test(tmp_path: Path):
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
