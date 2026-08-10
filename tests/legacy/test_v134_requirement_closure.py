from __future__ import annotations

import hashlib
import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_spec_consistency
from beacon.main import app
from beacon.utils.artifact_paths import execution_file_output, qa_matrix_output


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(tmp_path: Path, *, version: str, feature: str, with_acceptance: bool) -> str:
    slug = feature.lower().replace(" ", "-")
    root = tmp_path / "docs" / "beacon" / version
    (root / "user-story").mkdir(parents=True, exist_ok=True)
    (root / "prd").mkdir(parents=True, exist_ok=True)
    (root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (root / "execution").mkdir(parents=True, exist_ok=True)
    if with_acceptance:
        (root / "user-story" / f"{slug}.md").write_text(
            "\n".join(
                [
                    "# User Story",
                    "",
                    "| ID | Theme | Acceptance Criteria |",
                    "| --- | --- | --- |",
                    "| AC-001 | lifecycle | Runtime state is projected without replacing docs truth |",
                ]
            ),
            encoding="utf-8",
        )
        (root / "qa" / "test-cases" / f"{slug}.md").write_text(
            "\n".join(
                [
                    "# Test Cases",
                    "",
                    "| ID | Theme | Acceptance Criteria |",
                    "| --- | --- | --- |",
                    "| AC-001 | lifecycle | Runtime state is projected without replacing docs truth |",
                ]
            ),
            encoding="utf-8",
        )
    else:
        (root / "user-story" / f"{slug}.md").write_text("# User Story\n", encoding="utf-8")
        (root / "qa" / "test-cases" / f"{slug}.md").write_text("# Test Cases\n", encoding="utf-8")
    (root / "prd" / f"{slug}.md").write_text("# PRD\n", encoding="utf-8")
    matrix_path = qa_matrix_output(tmp_path, version, slug, "ac-test-matrix")
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text(json.dumps({"entries": [{"ac_id": "AC-001", "tc_id": "TC-001"}]}, ensure_ascii=False), encoding="utf-8")
    state_dir = tmp_path / ".beacon" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / f"implementation-{slug}.json").write_text("{}", encoding="utf-8")
    return slug


def test_v134_review_spec_should_fail_when_requirement_closure_is_broken(tmp_path: Path):
    version = "v1.3.4"
    slug = _seed_docs(tmp_path, version=version, feature="Closure Feature", with_acceptance=False)
    execution_file_output(tmp_path, version, f"implementation-summary-{slug}.json").parent.mkdir(parents=True, exist_ok=True)
    execution_file_output(tmp_path, version, f"implementation-summary-{slug}.json").write_text(
        json.dumps({"mode": "team", "traceability_refs": []}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = _invoke(["review", "spec", "Closure Feature", "--project", str(tmp_path), "--version", version, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert payload["status"] == "fail"
    assert payload["requirement_closure"]["status"] == "fail"
    assert "user_story_acceptance_missing" in reason_codes
    assert "implementation_requirement_traceability_missing" in reason_codes
    assert "implementation_delivery_summary_missing" in reason_codes


def test_v134_review_spec_should_pass_when_requirement_closure_is_complete(tmp_path: Path):
    version = "v1.3.4"
    feature = "Closure Feature"
    slug = _seed_docs(tmp_path, version=version, feature=feature, with_acceptance=True)
    execution_file_output(tmp_path, version, f"implementation-summary-{slug}.json").parent.mkdir(parents=True, exist_ok=True)
    execution_file_output(tmp_path, version, f"implementation-summary-{slug}.json").write_text(
        json.dumps(
            {
                "mode": "team",
                "traceability_refs": [
                    f"docs/beacon/{version}/prd/{slug}.md",
                    f"docs/beacon/{version}/user-story/{slug}.md",
                ],
                "requirement_traceability": {
                    "source_of_truth_root": f"docs/beacon/{version}",
                    "prd": f"docs/beacon/{version}/prd/{slug}.md",
                    "user_story": f"docs/beacon/{version}/user-story/{slug}.md",
                    "test_case": f"docs/beacon/{version}/qa/test-cases/{slug}.md",
                    "ac_matrix": f"docs/beacon/{version}/.machine/qa/{slug}.ac-test-matrix.json",
                    "revision_id": "R1",
                    "implemented_item_ids": ["AC-001"],
                    "implemented_task_ids": ["TASK-001"],
                    "verified_task_ids": ["TEST-001"],
                },
                "delivery_surfaces": {
                    "runtime_mode": "team",
                    "shipped_surfaces": ["runtime-board", "project-runtime-view"],
                    "partial_surfaces": [],
                    "deferred_surfaces": [],
                    "downgrade_rationale": "",
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = _invoke(["review", "spec", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["requirement_closure"]["status"] == "pass"


def test_v134_gate_spec_consistency_should_block_on_requirement_closure_review(tmp_path: Path):
    version = "v1.3.4"
    fingerprint_hash = "sha256:" + hashlib.sha256(b"closure").hexdigest()

    baseline_dir = tmp_path / ".beacon" / "state" / "baselines" / version
    baseline_dir.mkdir(parents=True, exist_ok=True)
    (baseline_dir / "latest.json").write_text(
        json.dumps(
            {
                "baseline_id": "bl-001",
                "run_id": "run-001",
                "revision_of": "bl-000",
                "spec_fingerprint": {"fingerprint_hash": fingerprint_hash},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    spec_dir = tmp_path / ".beacon" / "state" / "spec-fingerprints" / version
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "latest.json").write_text(
        json.dumps({"fingerprint_hash": fingerprint_hash}, ensure_ascii=False),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "execution": {"spec_fingerprint": {"fingerprint_hash": fingerprint_hash}},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    review_spec_path = execution_file_output(tmp_path, version, "review-spec-closure-feature.json")
    review_spec_path.parent.mkdir(parents=True, exist_ok=True)
    review_spec_path.write_text(
        json.dumps(
            {
                "feature": "Closure Feature",
                "review_type": "spec",
                "requirement_closure": {
                    "enabled": True,
                    "status": "fail",
                    "issues": [
                        {
                            "reason_code": "prd_user_story_test_case_traceability_broken",
                            "severity": "critical",
                            "message": "acceptance criteria missing from test-case coverage: ['AC-001']",
                        }
                    ],
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    issues, verdict = check_spec_consistency(tmp_path, GateMode.STRICT, "release", version=version)
    reason_codes = {item["reason_code"] for item in issues}
    assert verdict["status"] == "blocked"
    assert "prd_user_story_test_case_traceability_broken" in reason_codes
