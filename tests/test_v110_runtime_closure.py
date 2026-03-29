from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.material_audit import build_material_audit


runner = CliRunner()
VERSION = "v1.1.10"
FEATURE = "Closure Feature"
SLUG = "closure-feature"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_common_docs(root: Path) -> None:
    docs = root / "docs" / "beacon" / VERSION
    (docs / "user-story").mkdir(parents=True, exist_ok=True)
    (docs / "prd").mkdir(parents=True, exist_ok=True)
    (docs / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs / "execution").mkdir(parents=True, exist_ok=True)
    (docs / "release").mkdir(parents=True, exist_ok=True)
    (docs / "source-architecture").mkdir(parents=True, exist_ok=True)
    (docs / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (docs / ".machine" / "execution").mkdir(parents=True, exist_ok=True)
    docs.joinpath("SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    docs.joinpath("execution", "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    docs.joinpath("execution", "project-skill-qa-evolution-blueprint.md").write_text("# Blueprint\n", encoding="utf-8")
    docs.joinpath("release", f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    docs.joinpath("source-architecture", "index.md").write_text("# Source Architecture\n", encoding="utf-8")
    (docs / "user-story" / f"{SLUG}.md").write_text(
        """# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Control | Feature-aware QA plan exists |\n| AC-002 | Evidence | QA writes per-item verification |\n""",
        encoding="utf-8",
    )
    (docs / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (docs / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Human QA Plan\n", encoding="utf-8")
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


def _write_demo_profile(root: Path) -> None:
    (root / "beacon.config.yaml").write_text(
        """
project_skills:
  registry:
    shell-skill:
      id: shell-skill
      kind: external
      entry: /bin/sh
      capabilities:
        - verify
      supported_stages:
        - verify
      evidence_contract:
        - uat_pipeline_run
        - gateway_smoke
  profiles:
    demo:
      project: demo
      profile_id: demo
      description: Demo profile
      skills:
        verify: shell-skill
      required_evidence:
        - uat_pipeline_run
        - gateway_smoke
      required_cases:
        - upload_mp4_success
      orchestration:
        nodes:
          -
            id: pipeline
            stage: verify
            skill: shell-skill
            command_template: "python3 -c 'from pathlib import Path; p=Path(r\"{project_root}/.beacon/pipeline.txt\"); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(\"ok\")'"
            produces_evidence:
              - uat_pipeline_run
          -
            id: gateway
            stage: verify
            skill: shell-skill
            command_template: "python3 -c 'from pathlib import Path; p=Path(r\"{project_root}/.beacon/gateway.txt\"); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(\"ok\")'"
            produces_evidence:
              - gateway_smoke
            produces_cases:
              - upload_mp4_success
  default_profile: demo
""".strip()
        + "\n",
        encoding="utf-8",
    )


def _seed_release_state(root: Path) -> None:
    (root / ".beacon").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "state" / "evo" / "scorecards").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "state" / "evo" / "experiments").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": VERSION, "run_id": "run-release-001", "issues": []}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (root / ".beacon" / "state" / "evo" / "scorecards" / "latest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "generated_at": "2026-03-28T00:00:00+00:00",
                "main_kpi": "false_complete_rate",
                "counts": {"keep": 2, "review": 1, "discard": 0},
                "candidates": [{"candidate_id": "c1"}],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / ".beacon" / "state" / "evo" / "experiments" / "latest.json").write_text(
        json.dumps({"run_id": "run-exp-001", "main_kpi_score": 88}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_v110_qa_run_should_emit_precision_artifacts(tmp_path: Path):
    _seed_common_docs(tmp_path)
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
    assert qa_status["scenario_results_v2"]
    assert qa_status["feature_scorecard"]["release_ready"] is True
    assert (tmp_path / qa_status["ac_closure_path"]).exists()
    assert (tmp_path / qa_status["feature_scorecard_path"]).exists()

    first = qa_status["scenario_results_v2"][0]
    assert first["closure_outcome"] == "accepted"
    assert first["confidence_calibrated"] >= 0.6


def test_v110_qa_run_should_consume_project_profile_gate(tmp_path: Path):
    _seed_common_docs(tmp_path)
    _mark_implemented(tmp_path)
    _write_demo_profile(tmp_path)
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
    assert qa_status["project_profile_gate"]["status"] == "pass"
    assert (tmp_path / ".beacon" / "pipeline.txt").exists()
    assert (tmp_path / ".beacon" / "gateway.txt").exists()


def test_v110_release_scorecard_should_consume_feature_scorecard_and_project_gate(tmp_path: Path):
    _seed_common_docs(tmp_path)
    _mark_implemented(tmp_path)
    _write_demo_profile(tmp_path)
    _seed_release_state(tmp_path)
    script = _write_passing_layer_script(tmp_path)

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

    result = _invoke(["release", "scorecard", VERSION, "--project", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["feature_qa_scorecard"]["release_ready"] is True
    assert payload["qa"]["project_profile_gate_status"] == "pass"
    assert payload["release_ready"] is True
    assert payload["feature_qa_scorecard"]["release_confidence_min"] >= 0.6


def test_v110_material_audit_should_require_source_architecture_and_project_skill_blueprint(tmp_path: Path):
    docs = tmp_path / "docs" / "beacon" / VERSION
    (docs / "user-story").mkdir(parents=True, exist_ok=True)
    (docs / "prd").mkdir(parents=True, exist_ok=True)
    (docs / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs / "execution").mkdir(parents=True, exist_ok=True)
    (docs / "release").mkdir(parents=True, exist_ok=True)
    docs.joinpath("SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    docs.joinpath("execution", "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    docs.joinpath("user-story", "demo.md").write_text("# User Story\n", encoding="utf-8")
    docs.joinpath("prd", "demo.md").write_text("# PRD\n", encoding="utf-8")
    docs.joinpath("qa", "test-cases", "demo.md").write_text("# QA\n", encoding="utf-8")
    docs.joinpath("release", f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (docs / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (docs / ".machine" / "qa" / "demo.ac-test-matrix.json").write_text(json.dumps({"entries": [{}]}), encoding="utf-8")

    payload = build_material_audit(tmp_path, version=VERSION, strict=True)
    assert payload["status"] == "fail"
    failed = {item["name"] for item in payload["checks"] if item["status"] == "fail"}
    assert "formal_project_skill_blueprint_present" in failed
    assert "formal_source_architecture_present" in failed


def test_v110_test_case_create_should_preserve_existing_human_qa_doc(tmp_path: Path):
    _seed_common_docs(tmp_path)
    original = (tmp_path / "docs" / "beacon" / VERSION / "qa" / "test-cases" / f"{SLUG}.md")
    original.write_text("# Human QA Plan\nDo not overwrite.\n", encoding="utf-8")

    result = _invoke(["test-case", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    assert result.exit_code == 0, result.stdout
    assert "preserved" in result.stdout
    assert original.read_text(encoding="utf-8") == "# Human QA Plan\nDo not overwrite.\n"
    assert (tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").exists()


def test_v110_qa_audit_label_should_refresh_calibration_and_feed_experiment(tmp_path: Path):
    _seed_common_docs(tmp_path)
    _mark_implemented(tmp_path)
    _seed_release_state(tmp_path)
    script = _write_passing_layer_script(tmp_path)

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
    qa_payload = json.loads((tmp_path / ".beacon" / "qa" / "status.json").read_text(encoding="utf-8"))
    scenario = qa_payload["scenario_results_v2"][0]

    label = _invoke(
        [
            "qa",
            "audit",
            "label",
            str(qa_payload["run_id"]),
            str(scenario["scenario_id"]),
            "--label",
            "false_pass",
            "--feature",
            SLUG,
            "--project",
            str(tmp_path),
            "--json",
        ]
    )
    assert label.exit_code == 0, label.stdout
    label_payload = json.loads(label.stdout)
    assert label_payload["training_sample_count"] == 1

    calibration = json.loads((tmp_path / ".beacon" / "state" / "qa-calibration" / "latest.json").read_text(encoding="utf-8"))
    assert calibration["training_sample_count"] == 1
    assert calibration["model_type"] == "histogram-binning"

    experiment = _invoke(["version", "experiment", "v110 qa precision", "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert experiment.exit_code == 0, experiment.stdout
    experiment_payload = json.loads(experiment.stdout)
    assert "false_block_rate" in experiment_payload["metrics"]
    assert "human_audit_agreement" in experiment_payload["metrics"]
