from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_spec_consistency
from beacon.main import app
from beacon.utils.artifact_paths import execution_file_output
from beacon.utils.implementation_plan import load_implementation_plan
from beacon.utils.revision_delta import load_revision_delta, revision_delta_json_path


runner = CliRunner()
VERSION = "v1.3.8"
FEATURE = "V138 Change Cleanup Closure Feature"
SLUG = "v138-change-cleanup-closure-feature"


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


def _version_root(root: Path) -> Path:
    return root / "docs" / "beacon" / VERSION


def _seed_docs(root: Path) -> None:
    _init_git_repo(root)
    version_root = _version_root(root)
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (version_root / "prd").mkdir(parents=True, exist_ok=True)
    (version_root / "user-story").mkdir(parents=True, exist_ok=True)
    (version_root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (version_root / "execution").mkdir(parents=True, exist_ok=True)
    (version_root / "release").mkdir(parents=True, exist_ok=True)
    (version_root / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (version_root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (version_root / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (version_root / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (version_root / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    _write_r1_docs(root)


def _write_r1_docs(root: Path) -> None:
    version_root = _version_root(root)
    (version_root / "prd" / f"{SLUG}.md").write_text(
        (
            "# PRD\n\n"
            "## Functional Requirements\n\n"
            "### FR-001 Preserve primary route\n"
            "- keep the primary frozen route stable\n\n"
            "### FR-002 Support legacy inline mode\n"
            "- keep the legacy inline mode available for existing users\n"
        ),
        encoding="utf-8",
    )
    (version_root / "user-story" / f"{SLUG}.md").write_text(
        (
            "# User Story\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | Route | Preserve the primary frozen route |\n"
            "| AC-002 | Legacy | Support legacy inline mode for existing users |\n"
        ),
        encoding="utf-8",
    )
    (version_root / "qa" / "test-cases" / f"{SLUG}.md").write_text(
        (
            "# Test Cases\n\n"
            "## TC-001 Preserve primary route\n"
            "- verify the primary route remains stable\n\n"
            "## TC-002 Legacy inline mode\n"
            "- verify legacy inline mode still works\n"
        ),
        encoding="utf-8",
    )
    (version_root / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").write_text(
        json.dumps(
            {
                "entries": [
                    {"ac_id": "AC-001", "tc_id": "TC-001"},
                    {"ac_id": "AC-002", "tc_id": "TC-002"},
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_r2_docs(root: Path) -> None:
    version_root = _version_root(root)
    (version_root / "prd" / f"{SLUG}.md").write_text(
        (
            "# PRD\n\n"
            "## Functional Requirements\n\n"
            "### FR-001 Preserve primary route\n"
            "- keep the primary frozen route stable\n"
        ),
        encoding="utf-8",
    )
    (version_root / "user-story" / f"{SLUG}.md").write_text(
        (
            "# User Story\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | Route | Preserve the primary frozen route |\n"
        ),
        encoding="utf-8",
    )
    (version_root / "qa" / "test-cases" / f"{SLUG}.md").write_text(
        (
            "# Test Cases\n\n"
            "## TC-001 Preserve primary route\n"
            "- verify the primary route remains stable\n"
        ),
        encoding="utf-8",
    )
    (version_root / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").write_text(
        json.dumps({"entries": [{"ac_id": "AC-001", "tc_id": "TC-001"}]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _sync_contract(root: Path, *, revision_id: str) -> None:
    result = _invoke(
        [
            "doctor",
            "sync-technical-review-contract",
            FEATURE,
            "--project-root",
            str(root),
            "--version",
            VERSION,
            "--revision-id",
            revision_id,
            "--review-status",
            "approved",
            "--approved-by",
            "tech-lead",
            "--reviewed-at",
            "2026-04-26T12:00:00+08:00",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout


def _seed_spec_consistency_baseline(root: Path) -> None:
    fingerprint_hash = "sha256:" + hashlib.sha256(b"cleanup").hexdigest()
    baseline_dir = root / ".beacon" / "state" / "baselines" / VERSION
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
    spec_dir = root / ".beacon" / "state" / "spec-fingerprints" / VERSION
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "latest.json").write_text(
        json.dumps({"fingerprint_hash": fingerprint_hash}, ensure_ascii=False),
        encoding="utf-8",
    )
    (root / ".beacon" / "auto-test-status.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "execution": {"spec_fingerprint": {"fingerprint_hash": fingerprint_hash}},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _freeze_changed_revision(root: Path) -> None:
    freeze_r1 = _invoke(["freeze", FEATURE, "--project", str(root), "--version", VERSION, "--json"])
    assert freeze_r1.exit_code == 0, freeze_r1.stdout
    _sync_contract(root, revision_id="R1")
    reopened = _invoke(["reopen", FEATURE, "--project-root", str(root), "--version", VERSION, "--reason", "change-request", "--json"])
    assert reopened.exit_code == 0, reopened.stdout
    _write_r2_docs(root)
    freeze_r2 = _invoke(["freeze", FEATURE, "--project", str(root), "--version", VERSION, "--json"])
    assert freeze_r2.exit_code == 0, freeze_r2.stdout
    _sync_contract(root, revision_id="R2")


def _summary_payload(root: Path, *, cleanup: dict | None) -> dict:
    revision_delta_ref = str(revision_delta_json_path(root, VERSION, FEATURE).relative_to(root))
    traceability_refs = [
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
        f"docs/beacon/{VERSION}/.machine/qa/{SLUG}.ac-test-matrix.json",
        revision_delta_ref,
    ]
    payload = {
        "schema_version": "1.0",
        "run_id": "run-impl-001",
        "feature": FEATURE,
        "feature_slug": SLUG,
        "version": VERSION,
        "status": "completed",
        "traceability_refs": traceability_refs,
        "requirement_traceability": {
            "source_of_truth_root": f"docs/beacon/{VERSION}",
            "prd": f"docs/beacon/{VERSION}/prd/{SLUG}.md",
            "user_story": f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
            "test_case": f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
            "ac_matrix": f"docs/beacon/{VERSION}/.machine/qa/{SLUG}.ac-test-matrix.json",
            "revision_id": "R2",
            "implemented_item_ids": ["AC-001"],
            "implemented_task_ids": ["ITASK-001"],
            "verified_task_ids": ["TEST-001"],
        },
        "delivery_surfaces": {
            "runtime_mode": "team",
            "shipped_surfaces": ["primary-route"],
            "partial_surfaces": [],
            "deferred_surfaces": [],
            "downgrade_rationale": "",
        },
    }
    if cleanup is not None:
        payload["revision_cleanup"] = cleanup
    return payload


def _write_implementation_marker(root: Path) -> None:
    marker_path = root / ".beacon" / "state" / f"implementation-{SLUG}.json"
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "run-impl-001",
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "runner": "native-single",
                "status": "completed",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_v138_change_cleanup_delta_should_drive_cleanup_task_and_preflight(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze_changed_revision(tmp_path)

    revision_delta = load_revision_delta(tmp_path, version=VERSION, feature=FEATURE)
    assert revision_delta["status"] == "ready"
    assert revision_delta["cleanup_required"] is True
    assert revision_delta["removed_requirement_count"] == 1
    assert revision_delta["removed_requirement_surfaces"][0]["text"] == "Support legacy inline mode for existing users"

    plan_result = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert plan_result.exit_code == 0, plan_result.stdout
    plan = load_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)
    assert plan["source_refs"]["revision_delta"] == f"docs/beacon/{VERSION}/.machine/execution/revision-delta-{SLUG}.json"
    cleanup_task = next(task for task in plan["tasks"] if task.get("required_cleanup"))
    assert cleanup_task["source_revision_id"] == "R1"
    assert cleanup_task["cleanup_surface_labels"] == ["AC-002: Support legacy inline mode for existing users"]

    plan["tasks"] = [task for task in plan["tasks"] if not task.get("required_cleanup")]
    plan_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"implementation-plan-{SLUG}.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run_result = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--mode",
            "single",
            "--runner",
            "native-single",
            "--dry-run",
            "--host-prompt",
            "Implement the latest frozen revision exactly",
            "--json",
        ]
    )
    assert run_result.exit_code == 2, run_result.stdout
    payload = json.loads(run_result.stdout)
    assert payload["reason_code"] == "implementation_plan_cleanup_missing"


def test_v138_changed_feature_should_backfill_revision_delta_for_legacy_preflight(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze_changed_revision(tmp_path)

    plan_result = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert plan_result.exit_code == 0, plan_result.stdout

    delta_json = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"revision-delta-{SLUG}.json"
    delta_md = tmp_path / "docs" / "beacon" / VERSION / "execution" / f"revision-delta-{SLUG}.md"
    delta_json.unlink()
    delta_md.unlink()

    dry_run = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--mode",
            "single",
            "--runner",
            "native-single",
            "--dry-run",
            "--host-prompt",
            "Implement the latest frozen revision exactly",
            "--json",
        ]
    )
    assert dry_run.exit_code == 0, dry_run.stdout
    payload = json.loads(dry_run.stdout)
    assert payload["status"] == "dry_run"
    assert payload["plan_preflight"]["status"] == "pass"
    assert not delta_json.exists()
    assert not delta_md.exists()
    assert load_revision_delta(tmp_path, version=VERSION, feature=FEATURE)["cleanup_required"] is True


def test_v138_legacy_completed_plan_should_overlay_cleanup_in_memory_only(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze_changed_revision(tmp_path)

    plan_result = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert plan_result.exit_code == 0, plan_result.stdout

    plan_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"implementation-plan-{SLUG}.json"
    legacy_plan = json.loads(plan_path.read_text(encoding="utf-8"))
    legacy_plan["source_refs"].pop("revision_delta", None)
    legacy_plan.pop("revision_delta", None)
    legacy_plan["revision_delta_ref"] = ""
    legacy_plan["revision_delta_markdown_ref"] = ""
    legacy_plan["revision_cleanup_required"] = False
    legacy_plan["source_revision_id"] = ""
    legacy_plan["tasks"] = [task for task in legacy_plan["tasks"] if not task.get("required_cleanup")]
    for task in legacy_plan["tasks"]:
        task["status"] = "completed"
    legacy_plan["status"] = "completed"
    legacy_plan_text = json.dumps(legacy_plan, ensure_ascii=False, indent=2) + "\n"
    plan_path.write_text(legacy_plan_text, encoding="utf-8")

    dry_run = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--mode",
            "single",
            "--runner",
            "native-single",
            "--dry-run",
            "--host-prompt",
            "Implement the latest frozen revision exactly",
            "--json",
        ]
    )
    assert dry_run.exit_code == 0, dry_run.stdout
    payload = json.loads(dry_run.stdout)
    assert payload["status"] == "dry_run"
    assert payload["plan_preflight"]["status"] == "pass"
    assert plan_path.read_text(encoding="utf-8") == legacy_plan_text


def test_v138_review_and_gate_should_block_without_revision_cleanup_evidence(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze_changed_revision(tmp_path)
    _seed_spec_consistency_baseline(tmp_path)
    _write_implementation_marker(tmp_path)

    summary_path = execution_file_output(tmp_path, VERSION, f"implementation-summary-{SLUG}.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(_summary_payload(tmp_path, cleanup=None), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    review_result = _invoke(["review", "spec", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert review_result.exit_code == 0, review_result.stdout
    review_payload = json.loads(review_result.stdout)
    reason_codes = {item["reason_code"] for item in review_payload["issues"]}
    assert review_payload["status"] == "fail"
    assert review_payload["requirement_closure"]["status"] == "fail"
    assert "superseded_surface_cleanup_missing" in reason_codes

    issues, verdict = check_spec_consistency(tmp_path, GateMode.STRICT, "release", version=VERSION)
    assert verdict["status"] == "blocked"
    assert "superseded_surface_cleanup_missing" in {item["reason_code"] for item in issues}

    summary_path.write_text(
        json.dumps(
            _summary_payload(
                tmp_path,
                cleanup={
                    "revision_id": "R2",
                    "source_revision_id": "R1",
                    "revision_delta_ref": f"docs/beacon/{VERSION}/.machine/execution/revision-delta-{SLUG}.json",
                    "cleanup_required": True,
                    "cleanup_review_completed": True,
                    "removed_surfaces": ["Removed legacy inline mode code path"],
                    "retained_legacy_surfaces": [],
                    "cleanup_rationale": "",
                },
            ),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    review_pass = _invoke(["review", "spec", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert review_pass.exit_code == 0, review_pass.stdout
    review_pass_payload = json.loads(review_pass.stdout)
    assert review_pass_payload["status"] == "pass"
    assert review_pass_payload["requirement_closure"]["status"] == "pass"
