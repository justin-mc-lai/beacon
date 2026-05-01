"""Regression tests for workflow/gate/release fixes."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_test_execution_integrity
from beacon.commands.release import _build_version_change_payload, _render_version_change_markdown
from beacon.main import app
from beacon.utils.artifact_paths import change_docs_file, change_file_output, machine_execution_dir, release_checklist_file
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime import load_run_state, save_run_state
from beacon.utils.technical_review_contract import technical_review_contract_json_path
from beacon.utils.writeback import record_implementation_writeback, record_verification_writeback
from beacon.utils.workflow_memory import append_lifecycle_event, compute_workflow_progress


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_release_artifacts(project_root: Path, *, version: str, run_id: str) -> None:
    beacon_dir = project_root / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    (beacon_dir / "auto-test-status.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "version": version,
                "run_id": run_id,
                "execution": {"run_id": run_id, "version": version},
            }
        ),
        encoding="utf-8",
    )
    (beacon_dir / "gate-report.json").write_text(
        json.dumps(
            {
                "stage": "release",
                "mode": "strict",
                "status": "Pass",
                "issues": [],
                "version": version,
                "run_id": run_id,
                "coverage": {"full_coverage": True},
            }
        ),
        encoding="utf-8",
    )
    (beacon_dir / "evidence-manifest.json").write_text(
        json.dumps(
            {
                "version": version,
                "run_id": run_id,
                "entries": [{"path": ".beacon/auto-test-status.json", "sha256": "x"}],
            }
        ),
        encoding="utf-8",
    )


def _seed_review_acceptance_feature(project_root: Path, *, version: str, feature: str) -> str:
    slug = feature.lower().replace(" ", "-")
    docs_root = project_root / "docs" / "beacon" / version
    (docs_root / "user-story").mkdir(parents=True, exist_ok=True)
    (docs_root / "prd").mkdir(parents=True, exist_ok=True)
    (docs_root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs_root / "execution").mkdir(parents=True, exist_ok=True)
    prototype_root = docs_root / "prototype" / slug
    prototype_root.mkdir(parents=True, exist_ok=True)

    summary = docs_root / "SUMMARY.md"
    summary.write_text("# Summary\n", encoding="utf-8")
    (docs_root / "execution" / "index.md").write_text("# Execution Index\n", encoding="utf-8")
    (docs_root / "execution" / "architecture-blueprint.md").write_text("# Blueprint\n", encoding="utf-8")
    (docs_root / "user-story" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# User Story: {feature}",
                "",
                "| ID | Theme | Acceptance Criteria |",
                "| --- | --- | --- |",
                "| AC-001 | prototype | Reference pack is generated |",
            ]
        ),
        encoding="utf-8",
    )
    (docs_root / "prd" / f"{slug}.md").write_text(f"# PRD: {feature}\n", encoding="utf-8")
    (docs_root / "qa" / "test-cases" / f"{slug}.md").write_text(f"# Test Cases: {feature}\n", encoding="utf-8")

    machine_user_story = docs_root / ".machine" / "user-story"
    machine_qa = docs_root / ".machine" / "qa"
    machine_exec = machine_execution_dir(project_root, version)
    machine_user_story.mkdir(parents=True, exist_ok=True)
    machine_qa.mkdir(parents=True, exist_ok=True)
    machine_exec.mkdir(parents=True, exist_ok=True)
    for suffix in ("ac-test-matrix", "qa9-matrix", "story-scenario-map"):
        (machine_qa / f"{slug}.{suffix}.json").write_text(json.dumps({"feature": feature}, ensure_ascii=False), encoding="utf-8")
    (machine_exec / f"{slug}.revision.json").write_text(
        json.dumps({"feature": feature, "version": version, "revision_id": "R1"}, ensure_ascii=False),
        encoding="utf-8",
    )

    for rel in (
        "prototype-plan.json",
        "manifest.json",
        "prototype-review.json",
        "freeze.json",
    ):
        (prototype_root / rel).write_text(json.dumps({"feature": feature}, ensure_ascii=False), encoding="utf-8")

    (docs_root / ".machine" / "trace" / "implementation" / slug).mkdir(parents=True, exist_ok=True)
    ((docs_root / ".machine" / "trace" / "implementation" / slug) / f"technical-implementation-{slug}.md").write_text(
        f"# technical-implementation-{slug}.md\n",
        encoding="utf-8",
    )
    for rel in (
        f"implementation-brief-{slug}.md",
        f"review-quality-{slug}.md",
        f"review-spec-{slug}.md",
    ):
        path = docs_root / "execution" / rel
        path.write_text(f"# {rel}\n", encoding="utf-8")
    for rel in (
        f"technical-implementation-{slug}.json",
        f"implementation-summary-{slug}.json",
        f"review-quality-{slug}.json",
        f"review-spec-{slug}.json",
        "terminal.json",
    ):
        (machine_exec / rel).write_text(
            json.dumps({"feature": feature, "version": version, "status": "Pass"}, ensure_ascii=False),
            encoding="utf-8",
        )

    state_dir = project_root / ".beacon" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / f"implementation-{slug}.json").write_text(
        json.dumps({"feature": feature, "version": version}, ensure_ascii=False),
        encoding="utf-8",
    )
    qa_feature_dir = project_root / ".beacon" / "qa" / "features" / slug
    qa_feature_dir.mkdir(parents=True, exist_ok=True)
    (qa_feature_dir / "scorecard.json").write_text(
        json.dumps({"feature": feature, "version": version, "continue_decision": "ready_for_release"}, ensure_ascii=False),
        encoding="utf-8",
    )

    return slug


def test_run_workflow_strict_flag_should_enable_effective_strict_mode(tmp_path: Path):
    result = _invoke(
        [
            "run",
            "workflow",
            "--strict",
            "--feature",
            "demo",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["reason"] == "missing_user_story_for_strict_mode"


def test_workflow_run_should_auto_route_think_start_and_parse_options(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "run",
            "think",
            "Demo Feature",
            "--project",
            str(tmp_path),
            "--options",
            '{"qa_profile":"web-core"}',
        ]
    )
    assert result.exit_code == 0
    think_progress_dir = tmp_path / ".beacon" / "state" / "think-progress"
    files = sorted(think_progress_dir.glob("*.json"))
    assert files
    payload = json.loads(files[-1].read_text(encoding="utf-8"))
    assert payload.get("topic") == "Demo Feature"
    assert payload.get("qa_profile") == "web-core"


def test_gate_should_fallback_when_gate_config_json_is_malformed(tmp_path: Path):
    config_path = tmp_path / ".beacon" / "gate-config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("{invalid json", encoding="utf-8")

    result = _invoke(
        [
            "gate",
            "check",
            "think",
            "--mode",
            "normal",
            "--json",
            "--project-root",
            str(tmp_path),
        ]
    )
    assert result.exit_code == 0
    assert "Traceback" not in result.stdout


def test_gate_should_resolve_relative_matrix_path_from_project_root(tmp_path: Path):
    version = "v1.0.0"
    run_id = "run-relative-matrix-001"
    matrix_path = tmp_path / "docs" / "beacon" / version / ".machine" / "qa" / "feature.ac-test-matrix.json"
    evidence_path = tmp_path / ".beacon" / "evidence" / "test-results" / "feature" / "TC-001.json"
    auto_test_status = tmp_path / ".beacon" / "auto-test-status.json"
    signature_chain = tmp_path / ".beacon" / "evidence-signature-chain.json"

    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    auto_test_status.parent.mkdir(parents=True, exist_ok=True)

    matrix_path.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "ac_id": "AC-001",
                        "tc_id": "TC-001",
                        "layer": "unit",
                        "evidence_path": str(evidence_path.relative_to(tmp_path)),
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    evidence_path.write_text(json.dumps({"status": "passed"}, ensure_ascii=False), encoding="utf-8")

    auto_test_status.write_text(
        json.dumps(
            {
                "status": "passed",
                "run_id": run_id,
                "execution": {
                    "run_id": run_id,
                    "version": version,
                    "layers": [
                        {"layer": "unit", "status": "passed"}
                    ],
                    "matrix_report": {
                        "matrix_path": f"docs/beacon/{version}/.machine/qa/feature.ac-test-matrix.json",
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    summary_sha = hashlib.sha256(auto_test_status.read_bytes()).hexdigest()
    signature_chain.write_text(
        json.dumps(
            [
                {
                    "run_id": run_id,
                    "summary_path": ".beacon/auto-test-status.json",
                    "summary_sha256": summary_sha,
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    issues = check_test_execution_integrity(tmp_path, GateMode.STRICT, "release")
    assert issues == []


def test_version_change_payload_should_analyze_multi_feature_implementation_order(tmp_path: Path):
    version = "v1.3.12"
    docs_root = tmp_path / "docs" / "beacon" / version
    (docs_root / "execution").mkdir(parents=True, exist_ok=True)
    (docs_root / "execution" / "architecture-blueprint.md").write_text("# Blueprint\n", encoding="utf-8")
    (docs_root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (tmp_path / "docs" / "beacon" / "global-boundaries.md").write_text("# Global\n", encoding="utf-8")

    alpha = "Feature Alpha"
    beta = "Feature Beta"
    gamma = "Feature Gamma"
    alpha_slug = _seed_review_acceptance_feature(tmp_path, version=version, feature=alpha)
    beta_slug = _seed_review_acceptance_feature(tmp_path, version=version, feature=beta)
    gamma_slug = _seed_review_acceptance_feature(tmp_path, version=version, feature=gamma)

    freeze_revision_state(tmp_path, version=version, feature=alpha)
    freeze_revision_state(tmp_path, version=version, feature=beta)
    freeze_revision_state(tmp_path, version=version, feature=gamma)

    for feature, services in (
        (alpha, ["api"]),
        (beta, ["api"]),
        (gamma, ["web"]),
    ):
        path = technical_review_contract_json_path(tmp_path, version, feature)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "feature": feature,
                    "feature_slug": feature.lower().replace(" ", "-"),
                    "version": version,
                    "revision_id": "R1",
                    "base_branch": "main",
                    "target_branch": f"beacon/{version}",
                    "branch_prefix": "beacon/",
                    "worktree_root": ".",
                    "workspace_root": ".",
                    "environment_mode": "local-dev",
                    "isolation_strategy": "repo-local isolation",
                    "review_status": "approved",
                    "approved_by": "test",
                    "reviewed_at": "2026-05-01T12:00:00+08:00",
                    "use_git_worktree": False,
                    "service_directories": services,
                    "direct_delivery_services": services,
                    "writable_services": services,
                    "reference_only_services": ["docs"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    machine_change = docs_root / ".machine" / "change"
    machine_change.mkdir(parents=True, exist_ok=True)
    for feature, slug in ((alpha, alpha_slug), (beta, beta_slug), (gamma, gamma_slug)):
        (machine_change / f"{slug}.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "version": version,
                    "feature": feature,
                    "feature_slug": slug,
                    "status": "completed",
                    "summary": f"{feature} summary",
                    "added": [f"{feature} added"],
                    "removed": [],
                    "fixed": [],
                    "traceability_refs": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    payload = _build_version_change_payload(tmp_path, version=version)
    order = payload["implementation_order"]

    assert order["status"] == "analyzed"
    assert order["feature_count"] == 3
    assert order["ordered_feature_slugs"][0] == alpha_slug
    assert len(order["waves"]) == 2
    assert [item["feature_slug"] for item in order["waves"][0]["features"]] == [alpha_slug, gamma_slug]
    assert order["waves"][0]["parallelizable"] is True
    assert [item["feature_slug"] for item in order["waves"][1]["features"]] == [beta_slug]
    assert order["waves"][1]["features"][0]["depends_on_features"] == [alpha_slug]
    assert order["waves"][1]["features"][0]["reason_code"] == "shared_delivery_service_conflict"

    markdown = _render_version_change_markdown(payload)
    assert "## Implementation Order" in markdown
    assert f"`{alpha_slug}`" in markdown
    assert f"`{beta_slug}`" in markdown
    assert "depends_on=feature-alpha" in markdown


def test_release_create_should_use_resolved_version_in_file_content(tmp_path: Path):
    (tmp_path / "docs" / "beacon" / "v2.0.0").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "v1.0.0").mkdir(parents=True, exist_ok=True)

    result = _invoke(["release", "create", "latest", "--project", str(tmp_path)])
    assert result.exit_code == 0

    out = release_checklist_file(tmp_path, "v2.0.0")
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "# Release Checklist: v2.0.0" in text
    assert "**Version**: v2.0.0" in text
    assert "latest" not in text


def test_release_create_should_aggregate_version_change_document(tmp_path: Path):
    version = "v2.1.0"
    for slug, summary, field, item in (
        ("feature-a", "First feature landed", "added", "Added contract A"),
        ("feature-b", "Second feature landed", "fixed", "Fixed edge case B"),
    ):
        change_json = change_file_output(tmp_path, version, f"{slug}.json")
        change_md = change_docs_file(tmp_path, version, f"{slug}.md")
        change_json.parent.mkdir(parents=True, exist_ok=True)
        change_md.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "1.0",
            "version": version,
            "feature": slug.replace("-", " ").title(),
            "feature_slug": slug,
            "status": "completed",
            "summary": summary,
            "added": [item] if field == "added" else [],
            "removed": [],
            "fixed": [item] if field == "fixed" else [],
            "traceability_refs": [f"docs/beacon/{version}/.machine/execution/implementation-summary-{slug}.json"],
        }
        change_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        change_md.write_text(f"# {slug}\n", encoding="utf-8")

    result = _invoke(["release", "create", version, "--project", str(tmp_path)])
    assert result.exit_code == 0

    version_change_md = change_docs_file(tmp_path, version, f"{version}.md")
    version_change_json = change_file_output(tmp_path, version, f"{version}.json")
    assert version_change_md.exists()
    assert version_change_json.exists()

    change_text = version_change_md.read_text(encoding="utf-8")
    assert "feature packages included: 2" in change_text
    assert "`feature-a`" in change_text
    assert "`feature-b`" in change_text
    assert "[feature-a] Added contract A" in change_text
    assert "[feature-b] Fixed edge case B" in change_text

    release_text = release_checklist_file(tmp_path, version).read_text(encoding="utf-8")
    assert f"docs/beacon/{version}/change/{version}.md" in release_text
    assert f"docs/beacon/{version}/.machine/change/{version}.json" in release_text


def test_release_create_should_not_overwrite_canonical_release_note(tmp_path: Path):
    version = "v2.1.0"
    release_dir = tmp_path / "docs" / "beacon" / version / "release"
    release_dir.mkdir(parents=True, exist_ok=True)
    canonical_release_note = release_dir / f"{version}.md"
    canonical_release_note.write_text("# Canonical release note\n", encoding="utf-8")

    result = _invoke(["release", "create", version, "--project", str(tmp_path)])
    assert result.exit_code == 0

    assert canonical_release_note.read_text(encoding="utf-8") == "# Canonical release note\n"
    checklist = release_checklist_file(tmp_path, version)
    assert checklist.exists()
    assert "# Release Checklist: v2.1.0" in checklist.read_text(encoding="utf-8")


def test_release_create_should_preserve_version_change_timestamp_when_scope_is_unchanged(tmp_path: Path):
    version = "v2.1.1"
    slug = "feature-a"
    change_json = change_file_output(tmp_path, version, f"{slug}.json")
    change_md = change_docs_file(tmp_path, version, f"{slug}.md")
    change_json.parent.mkdir(parents=True, exist_ok=True)
    change_md.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "version": version,
        "feature": "Feature A",
        "feature_slug": slug,
        "status": "completed",
        "summary": "Feature A landed",
        "added": ["Added contract A"],
        "removed": [],
        "fixed": [],
        "traceability_refs": [f"docs/beacon/{version}/.machine/execution/implementation-summary-{slug}.json"],
    }
    change_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    change_md.write_text("# feature-a\n", encoding="utf-8")

    prior_version_payload = _build_version_change_payload(tmp_path, version=version)
    prior_version_payload["generated_at"] = "2026-04-24 19:15"
    version_change_json = change_file_output(tmp_path, version, f"{version}.json")
    version_change_md = change_docs_file(tmp_path, version, f"{version}.md")
    version_change_json.write_text(json.dumps(prior_version_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    version_change_md.write_text(_render_version_change_markdown(prior_version_payload), encoding="utf-8")

    result = _invoke(["release", "create", version, "--project", str(tmp_path)])
    assert result.exit_code == 0

    current_payload = json.loads(version_change_json.read_text(encoding="utf-8"))
    assert current_payload["generated_at"] == "2026-04-24 19:15"
    current_markdown = version_change_md.read_text(encoding="utf-8")
    assert "**Generated**: 2026-04-24 19:15" in current_markdown


def test_release_create_should_synthesize_feature_changes_from_technical_archive_when_missing(tmp_path: Path):
    version = "v1.3.1"
    slug = "feature-from-archive"
    machine_exec = tmp_path / "docs" / "beacon" / version / ".machine" / "execution"
    exec_dir = tmp_path / "docs" / "beacon" / version / "execution"
    machine_exec.mkdir(parents=True, exist_ok=True)
    exec_dir.mkdir(parents=True, exist_ok=True)

    (machine_exec / f"technical-implementation-{slug}.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "version": version,
                "feature": "Feature From Archive",
                "feature_slug": slug,
                "implementation_scope_summary": "Archive-backed feature landed",
                "changed_files": ["beacon/commands/release.py"],
                "additions": [],
                "deletions": [],
                "modifications": [],
                "refactors": [],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (machine_exec / f"implementation-summary-{slug}.json").write_text("{}", encoding="utf-8")
    (exec_dir / f"implementation-brief-{slug}.md").write_text("# summary\n", encoding="utf-8")

    result = _invoke(["release", "create", version, "--project", str(tmp_path)])
    assert result.exit_code == 0

    version_change_json = change_file_output(tmp_path, version, f"{version}.json")
    payload = json.loads(version_change_json.read_text(encoding="utf-8"))
    assert payload["feature_count"] == 1
    assert payload["features"][0]["feature_slug"] == slug
    assert any("[feature-from-archive] Updated `beacon/commands/release.py`" == item for item in payload["fixed"])
    assert change_file_output(tmp_path, version, f"{slug}.json").exists()
    assert change_docs_file(tmp_path, version, f"{slug}.md").exists()


def test_release_check_should_fail_when_artifacts_version_mismatch(tmp_path: Path):
    _seed_release_artifacts(tmp_path, version="v1.2.3", run_id="run-20260306T000000000000")

    mismatch = _invoke(["release", "check", "v9.9.9", "--project", str(tmp_path)])
    assert mismatch.exit_code == 1
    assert "expected=v9.9.9" in mismatch.stdout

    matched = _invoke(["release", "check", "v1.2.3", "--project", str(tmp_path)])
    assert matched.exit_code == 0


def test_v131_release_check_should_require_version_change_documents(tmp_path: Path):
    version = "v1.3.1"
    (tmp_path / "docs" / "beacon" / version).mkdir(parents=True, exist_ok=True)
    _seed_release_artifacts(tmp_path, version=version, run_id="run-20260306T000000000001")

    blocked = _invoke(["release", "check", version, "--project", str(tmp_path)])
    assert blocked.exit_code == 1
    assert "version change markdown exists" in blocked.stdout

    _invoke(["release", "create", version, "--project", str(tmp_path)])
    passed = _invoke(["release", "check", version, "--project", str(tmp_path)])
    assert passed.exit_code == 0


def test_compute_workflow_progress_should_not_read_gate_pass_from_other_run(tmp_path: Path):
    run_a = "run-aaa"
    run_b = "run-bbb"
    save_run_state(tmp_path, run_a, {"run_id": run_a, "workflow": "workflow.start", "feature": "A", "version": "v1.0.0"})
    save_run_state(tmp_path, run_b, {"run_id": run_b, "workflow": "workflow.start", "feature": "B", "version": "v1.0.0"})

    for event in ("stage_started", "stage_context_injected", "stage_finished", "memory_writeback"):
        append_lifecycle_event(tmp_path, run_id=run_a, stage="gate", event=event, source="test")

    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "run_id": run_a, "version": "v1.0.0"}),
        encoding="utf-8",
    )

    progress_b = compute_workflow_progress(tmp_path, run_id=run_b)
    assert progress_b.get("gate_pass") is False
    assert progress_b.get("gate_status") == "unknown"


def test_review_accept_should_backfill_workflow_closure_from_accepted_artifacts(tmp_path: Path):
    version = "v1.1.11"
    feature = "Prototype Reference Pack V2"
    slug = _seed_review_acceptance_feature(tmp_path, version=version, feature=feature)
    run_id = "run-20260331T023659Z-291e"

    save_run_state(
        tmp_path,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "mode": "manual",
            "feature": feature,
            "version": version,
            "prototype_enabled": True,
            "status": "planned",
            "started_at": "2026-03-31T02:36:59+00:00",
            "events": [{"event": "workflow_started", "ts": "2026-03-31T02:36:59+00:00"}],
        },
    )
    freeze_revision_state(tmp_path, version=version, feature=feature)
    record_implementation_writeback(tmp_path, version=version, feature=feature, run_id="impl-run")
    record_verification_writeback(
        tmp_path,
        version=version,
        feature=feature,
        run_id="verify-run",
        verified_item_ids=["AC-001", "TASK-001", "TEST-001"],
        failed_item_ids=[],
        evidence_ref=[".beacon/auto-test-status.json"],
    )

    beacon_dir = tmp_path / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    (beacon_dir / "auto-test-status.json").write_text(
        json.dumps({"status": "passed", "run_id": run_id, "version": version}, ensure_ascii=False),
        encoding="utf-8",
    )
    (beacon_dir / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "run_id": run_id, "version": version}, ensure_ascii=False),
        encoding="utf-8",
    )
    (beacon_dir / "evidence-manifest.json").write_text(
        json.dumps({"run_id": run_id, "version": version, "entries": [{"path": ".beacon/auto-test-status.json", "sha256": "x"}]}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = _invoke(["review", "accept", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "accepted"
    assert payload["workflow_closure_complete"] is True
    assert payload["workflow_gate_pass"] is True

    progress = compute_workflow_progress(tmp_path, version=version, feature=feature)
    assert progress["run_id"] == run_id
    assert progress["closure_complete"] is True
    assert progress["missing_closure_stages"] == []

    run_state = load_run_state(tmp_path, run_id)
    assert run_state is not None
    assert run_state["status"] == "completed"
    assert any(item.get("event") == "workflow_completed" for item in run_state.get("events", []))
    gate_report = json.loads((beacon_dir / "gate-report.json").read_text(encoding="utf-8"))
    evidence_manifest = json.loads((beacon_dir / "evidence-manifest.json").read_text(encoding="utf-8"))
    assert gate_report["run_id"] == run_id
    assert evidence_manifest["run_id"] == run_id

    help_result = _invoke(["help", "--project-root", str(tmp_path), "--version", version, "--feature", feature, "--json"])
    assert help_result.exit_code == 0, help_result.stdout
    help_payload = json.loads(help_result.stdout)
    assert help_payload["current_stage"] == "accepted"
    assert help_payload["next_step"]["action"] == "release-check"
    assert "prototype" in payload["workflow_synced_stages"]
    assert slug == "prototype-reference-pack-v2"
