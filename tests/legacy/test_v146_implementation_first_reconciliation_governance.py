from __future__ import annotations

import json
import subprocess
from pathlib import Path

from beacon.utils.help_support import build_help_payload
from beacon.utils.reconciliation import detect_implementation_first_reconciliation_needed, reconciliation_artifact_path
from beacon.utils.runtime import write_json
from beacon.utils.revision_state import freeze_revision_state, reopen_revision_state
from beacon.utils.writeback import record_implementation_writeback


VERSION = "v1.4.6"
FEATURE = "Implementation First Reconciliation Feature"
SLUG = "implementation-first-reconciliation-feature"


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Beacon Tests"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "beacon-tests@example.com"], cwd=root, check=True, capture_output=True, text=True)
    (root / ".gitkeep").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)


def _seed_docs(root: Path) -> None:
    _init_git_repo(root)
    version_root = root / "docs" / "beacon" / VERSION
    (version_root / "prd").mkdir(parents=True, exist_ok=True)
    (version_root / "user-story").mkdir(parents=True, exist_ok=True)
    (version_root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (version_root / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (version_root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (version_root / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (version_root / "user-story" / f"{SLUG}.md").write_text(
        "# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Recovery | Preserve reconciliation provenance |\n",
        encoding="utf-8",
    )
    (version_root / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (version_root / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").write_text(
        json.dumps({"entries": [{"ac_id": "AC-001", "tc_id": "TC-001"}]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _seed_reconciliation_scenario(root: Path) -> dict[str, object]:
    _seed_docs(root)
    freeze_revision_state(root, version=VERSION, feature=FEATURE)
    record_implementation_writeback(
        root,
        version=VERSION,
        feature=FEATURE,
        run_id="run-impl-r1",
        implemented_item_ids=["AC-001"],
        changed_files=["beacon/utils/writeback.py"],
    )
    reopen_revision_state(root, version=VERSION, feature=FEATURE, reason="change-request")
    revision = freeze_revision_state(root, version=VERSION, feature=FEATURE)
    detection = detect_implementation_first_reconciliation_needed(
        root,
        version=VERSION,
        feature=FEATURE,
        revision_state=revision,
    )
    return {"revision": revision, "detection": detection}


def test_reconciliation_is_defined_as_recovery_not_normal_delivery(tmp_path: Path) -> None:
    result = _seed_reconciliation_scenario(tmp_path)
    artifact = result["detection"]["artifact"]
    assert result["detection"]["required"] is True
    assert artifact["recovery_kind"] == "implementation_first_reconciliation"
    assert artifact["delivery_mode"] == "recovery_not_normal_delivery"


def test_reconciliation_routes_through_change_not_new_stage(tmp_path: Path) -> None:
    _seed_reconciliation_scenario(tmp_path)
    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert "implementation_first_reconciliation_required" in payload["blocking_reasons_raw"]
    assert payload["next_step"]["action"] == "beacon-change"
    assert payload["next_step"]["command"].startswith("beacon change ")


def test_reconciliation_artifact_contract_is_frozen(tmp_path: Path) -> None:
    result = _seed_reconciliation_scenario(tmp_path)
    artifact = result["detection"]["artifact"]
    assert reconciliation_artifact_path(tmp_path, version=VERSION, feature=FEATURE).exists()
    assert artifact["feature"] == FEATURE
    assert artifact["version"] == VERSION
    assert artifact["drift_detected_at"]
    assert artifact["implementation_artifacts"]
    assert artifact["missing_truth_surfaces"] == ["prd", "user-story", "qa/test-cases"]
    assert artifact["recovery_reason"]
    assert artifact["truth_surfaces_backfilled"]
    assert artifact["re_freeze_status"] == "completed"
    assert artifact["reprojection_targets"]


def test_reconciliation_requires_reprojection_of_affected_proof(tmp_path: Path) -> None:
    result = _seed_reconciliation_scenario(tmp_path)
    artifact = result["detection"]["artifact"]
    assert f"docs/beacon/{VERSION}/user-story/{SLUG}.md" in artifact["reprojection_targets"]
    assert f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md" in artifact["reprojection_targets"]
    assert "qa_proof" in artifact["reprojection_targets"]
    assert "release_facing_proof" in artifact["reprojection_targets"]


def test_reconciliation_preserves_drift_provenance(tmp_path: Path) -> None:
    result = _seed_reconciliation_scenario(tmp_path)
    artifact = result["detection"]["artifact"]
    implementation_artifact = artifact["implementation_artifacts"][0]
    assert implementation_artifact["revision_id"] == "R1"
    assert implementation_artifact["run_id"] == "run-impl-r1"
    assert artifact["provenance"]["post_hoc_writeback_occurred"] is True
    assert artifact["provenance"]["preserve_drift_history"] is True


def test_reconciliation_closes_when_current_revision_has_implementation_writeback(tmp_path: Path) -> None:
    result = _seed_reconciliation_scenario(tmp_path)
    revision = result["revision"]

    record_implementation_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-impl-r2",
        implemented_item_ids=["AC-001"],
        changed_files=["beacon/utils/writeback.py"],
    )

    detection = detect_implementation_first_reconciliation_needed(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        revision_state=revision,
    )

    assert detection["required"] is False


def test_reconciliation_closes_when_implementation_first_refreeze_completed(tmp_path: Path) -> None:
    result = _seed_reconciliation_scenario(tmp_path)
    revision = result["revision"]

    write_json(
        tmp_path
        / "docs"
        / "beacon"
        / VERSION
        / ".machine"
        / "change"
        / f"{SLUG}.refreeze-transaction.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "change_reason": "implementation-first-reconciliation",
            "refreeze_status": "complete",
            "truth_revision_before": {
                "revision_id": str(revision.get("source_revision_id") or ""),
                "doc_status": "frozen",
            },
            "truth_revision_after": {
                "revision_id": str(revision.get("revision_id") or ""),
                "doc_status": "frozen",
            },
        },
    )

    detection = detect_implementation_first_reconciliation_needed(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        revision_state=revision,
    )
    artifact = detection["artifact"]

    assert detection["required"] is False
    assert artifact["status"] == "completed"
    assert artifact["completion_reason_code"] == "implementation_first_reconciliation_completed"
    assert artifact["resolution"]["resolved_by"] == "change_refreeze_transaction"
    assert artifact["implementation_artifacts"][0]["revision_id"] == "R1"
