from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.help_support import build_help_payload
from beacon.utils.runtime import write_json
from beacon.utils.release_scorecard import build_release_scorecard, summarize_release_scorecard
from beacon.utils.revision_state import reopen_revision_state


runner = CliRunner()
VERSION = "v1.3.5"
FEATURE = "Beacon Change Loop Surface"
SLUG = "beacon-change-loop-surface"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / VERSION
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "prd" / f"{SLUG}.md").write_text(
        (
            "# PRD\n\n"
            "## 功能需求\n\n"
            "### FR-001 Change loop surface\n"
            "- expose stable post-freeze routing\n"
        ),
        encoding="utf-8",
    )
    (base / "user-story" / f"{SLUG}.md").write_text(
        (
            "# User Story\n\n"
            "## US-001：Change loop surface\n\n"
            "### 验收标准\n\n"
            "- [ ] expose stable route\n"
        ),
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")


def _freeze_feature(root: Path) -> None:
    result = _invoke(["freeze", FEATURE, "--project", str(root), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout


def _sync_approved_contract(root: Path, *, revision_id: str) -> None:
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
            "2026-04-20T23:30:00+08:00",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout


def _write_change_docs(root: Path, *, added: list[str], removed: list[str], fixed: list[str]) -> None:
    feature_json = root / "docs" / "beacon" / VERSION / ".machine" / "change" / f"{SLUG}.json"
    feature_md = root / "docs" / "beacon" / VERSION / "change" / f"{SLUG}.md"
    version_json = root / "docs" / "beacon" / VERSION / ".machine" / "change" / f"{VERSION}.json"
    version_md = root / "docs" / "beacon" / VERSION / "change" / f"{VERSION}.md"
    for path in (feature_json, feature_md, version_json, version_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    feature_payload = {
        "schema_version": "1.0",
        "version": VERSION,
        "feature": FEATURE,
        "feature_slug": SLUG,
        "status": "completed",
        "summary": "Change-loop surface updated",
        "added": added,
        "removed": removed,
        "fixed": fixed,
        "traceability_refs": [f"docs/beacon/{VERSION}/.machine/execution/implementation-summary-{SLUG}.json"],
    }
    version_payload = {
        "schema_version": "1.0",
        "version": VERSION,
        "status": "generated",
        "feature_count": 1,
        "features": [
            {
                "feature": FEATURE,
                "feature_slug": SLUG,
                "summary": "Change-loop surface updated",
                "status": "completed",
            }
        ],
        "added": [f"[{SLUG}] {item}" for item in added],
        "removed": [f"[{SLUG}] {item}" for item in removed],
        "fixed": [f"[{SLUG}] {item}" for item in fixed],
        "traceability_refs": [
            f"docs/beacon/{VERSION}/.machine/change/{SLUG}.json",
            f"docs/beacon/{VERSION}/change/{SLUG}.md",
        ],
    }
    feature_json.write_text(json.dumps(feature_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    feature_md.write_text(f"# {SLUG}\n", encoding="utf-8")
    version_json.write_text(json.dumps(version_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    version_md.write_text(f"# {VERSION} change\n", encoding="utf-8")


def _write_release_ready_runtime(root: Path) -> None:
    qa_root = root / ".beacon" / "qa"
    feature_root = qa_root / "features" / SLUG
    feature_root.mkdir(parents=True, exist_ok=True)
    (qa_root / "status.json").write_text(
        json.dumps(
            {
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "status": "passed",
                "evidence_done": True,
                "execution_mode": "feature-aware",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (feature_root / "scorecard.json").write_text(
        json.dumps(
            {
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "unresolved_closure_outcomes": [],
                "project_profile_gate_status": "pass",
                "release_confidence_min": 1.0,
                "release_confidence_avg": 1.0,
                "review_required_count": 0,
                "needs_replay_count": 0,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (root / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "pass", "issues": [], "version": VERSION}, ensure_ascii=False),
        encoding="utf-8",
    )


def _seed_project_metadata(root: Path) -> None:
    write_json(
        root / ".beacon" / "metadata" / "project-version-metadata.json",
        {
            "schema_version": "1.0",
            "project_root": str(root.resolve()),
            "global_project_metadata": {
                "project_root": str(root.resolve()),
                "topology_kind": "monorepo",
                "default_execution_service": "api",
                "service_bindings": [
                    {
                        "service_key": "api",
                        "repo_root": str((root / "services" / "api").resolve()),
                        "repo_root_relative": "services/api",
                        "role": "service",
                        "writable": True,
                        "worktree_path_policy": "follow-repo-root",
                    }
                ],
            },
            "version_scoped_metadata": {
                VERSION: {
                    "participating_services": ["api"],
                    "per_service_canonical_branch": {"api": "beacon/v1.3.5"},
                    "branch_guard_mode": "strict",
                    "validation_state": "verified",
                }
            },
            "transaction": {},
        },
    )


def test_v135_help_and_status_should_route_change_intent_to_beacon_change(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_project_metadata(tmp_path)
    _freeze_feature(tmp_path)

    help_payload = build_help_payload(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        change_intent="这个功能冻结后还要改需求范围并重新冻结",
    )
    assert help_payload["change_loop"]["recommended"] is True
    assert help_payload["next_step"]["action"] == "beacon-change"
    assert help_payload["next_step"]["command"] == "beacon-change"
    assert help_payload["project_metadata_context"]["metadata_ref"] == ".beacon/metadata/project-version-metadata.json"
    assert help_payload["project_metadata_context"]["resolved_metadata_view"]["selected_branch"] == "beacon/v1.3.5"
    assert help_payload["change_loop"]["project_metadata_context"]["resolved_metadata_view"]["selected_service"] == "api"
    assert "doctor metadata verify" in help_payload["change_loop"]["ladder"]
    assert "doctor metadata update" in help_payload["change_loop"]["ladder"]
    assert "qa delta-run" in help_payload["change_loop"]["ladder"]

    result = _invoke(
        [
            "status",
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
            "--change-intent",
            "这个功能冻结后还要改需求范围并重新冻结",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["change_loop"]["recommended"] is True
    assert payload["next_step"]["action"] == "beacon-change"
    assert payload["change_loop"]["route"] == "beacon-change"
    assert payload["project_metadata_context"]["resolved_metadata_view"]["topology_kind"] == "monorepo"
    assert payload["change_loop"]["metadata_verify_command"].startswith("beacon doctor metadata verify ")


def test_v135_release_scorecard_should_block_stale_release_when_revision_reopened(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze_feature(tmp_path)
    _sync_approved_contract(tmp_path, revision_id="R1")
    _write_change_docs(tmp_path, added=["Added stable routing"], removed=[], fixed=[])
    _write_release_ready_runtime(tmp_path)

    initial = build_release_scorecard(tmp_path, version=VERSION)
    assert initial["release_ready"] is True
    assert initial["revision_binding"]["gate_bound_to_latest_revision"] is True

    reopen_revision_state(tmp_path, version=VERSION, feature=FEATURE, reason="change-request")
    reopened = build_release_scorecard(tmp_path, version=VERSION)
    summary = summarize_release_scorecard(reopened)
    assert reopened["release_ready"] is False
    assert reopened["revision_binding"]["status"] == "reopened"
    assert reopened["revision_binding"]["reason_code"] == "revision_not_frozen"
    assert reopened["revision_binding"]["gate_bound_to_latest_revision"] is False
    assert summary["release_revision_current"] is False


def test_v135_release_scorecard_should_classify_initial_and_revised_delivery(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze_feature(tmp_path)
    _sync_approved_contract(tmp_path, revision_id="R1")
    _write_change_docs(tmp_path, added=["Added stable routing"], removed=[], fixed=[])
    _write_release_ready_runtime(tmp_path)

    initial = build_release_scorecard(tmp_path, version=VERSION)
    assert initial["delivery"]["type"] == "initial"

    reopen_revision_state(tmp_path, version=VERSION, feature=FEATURE, reason="change-request")
    _freeze_feature(tmp_path)
    _sync_approved_contract(tmp_path, revision_id="R2")
    _write_change_docs(tmp_path, added=["Added delta verification routing"], removed=[], fixed=[])

    revised = build_release_scorecard(tmp_path, version=VERSION)
    summary = summarize_release_scorecard(revised)
    assert revised["delivery"]["type"] == "revised"
    assert revised["revision_binding"]["gate_bound_to_latest_revision"] is True
    assert summary["delivery_type"] == "revised"
    assert summary["release_revision_current"] is True


def test_v135_release_scorecard_should_classify_hotfix_delivery(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze_feature(tmp_path)
    reopen_revision_state(tmp_path, version=VERSION, feature=FEATURE, reason="hotfix")
    _freeze_feature(tmp_path)
    _sync_approved_contract(tmp_path, revision_id="R2")
    _write_change_docs(tmp_path, added=[], removed=[], fixed=["Fixed stale release reuse"])
    _write_release_ready_runtime(tmp_path)

    scorecard = build_release_scorecard(tmp_path, version=VERSION)
    summary = summarize_release_scorecard(scorecard)
    assert scorecard["delivery"]["type"] == "hotfix"
    assert summary["delivery_type"] == "hotfix"
