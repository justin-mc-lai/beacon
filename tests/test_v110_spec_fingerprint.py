"""v1.1.0 spec fingerprint and baseline snapshot contracts."""

from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.v110_baseline import generate_spec_fingerprint, record_baseline_snapshot


def _seed_v110_docs(root: Path, *, version: str = "v1.1.0") -> None:
    (root / "docs" / "beacon" / version / "user-story").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / version / "prd").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / version / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)

    (root / "docs" / "beacon" / version / "user-story" / "feature.md").write_text(
        "# User Story\n\n- AC-001\n",
        encoding="utf-8",
    )
    (root / "docs" / "beacon" / version / "prd" / "feature.md").write_text(
        "# PRD\n\n- FR-001\n",
        encoding="utf-8",
    )
    matrix = {
        "schema_version": "1.0",
        "entries": [
            {
                "ac_id": "AC-001",
                "tc_id": "TC-001",
                "layer": "unit",
                "evidence_path": ".beacon/evidence/auto-test/{run_id}/unit/result.json",
            }
        ],
    }
    (root / "docs" / "beacon" / version / "qa" / "test-cases" / "feature.ac-test-matrix.json").write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_fingerprint_should_cover_user_story_prd_test_case(tmp_path: Path):
    _seed_v110_docs(tmp_path)

    payload = generate_spec_fingerprint(
        tmp_path,
        run_id="run-v110-fp-001",
        version="v1.1.0",
    )
    assert payload.get("fingerprint_hash")

    layers = payload.get("layers", {})
    assert layers.get("user_story", {}).get("count") == 1
    assert layers.get("prd", {}).get("count") == 1
    assert layers.get("test_case", {}).get("count") == 1

    latest_path = tmp_path / ".beacon" / "state" / "spec-fingerprints" / "v1.1.0" / "latest.json"
    assert latest_path.exists()


def test_baseline_snapshot_should_include_required_fields_and_revision(tmp_path: Path):
    _seed_v110_docs(tmp_path)

    first = record_baseline_snapshot(
        tmp_path,
        run_id="run-v110-baseline-001",
        version="v1.1.0",
        feature="Debug Loop",
        workflow_status="completed",
    )
    baseline_1 = first.get("baseline", {})

    prd_path = tmp_path / "docs" / "beacon" / "v1.1.0" / "prd" / "feature.md"
    prd_path.write_text("# PRD\n\n- FR-001 updated\n", encoding="utf-8")

    second = record_baseline_snapshot(
        tmp_path,
        run_id="run-v110-baseline-002",
        version="v1.1.0",
        feature="Debug Loop",
        workflow_status="running",
    )
    baseline_2 = second.get("baseline", {})

    assert baseline_1.get("baseline_id")
    assert baseline_2.get("baseline_id")
    assert baseline_2.get("revision_of") == baseline_1.get("baseline_id")

    spec_fp = baseline_2.get("spec_fingerprint", {})
    assert spec_fp.get("user_story")
    assert spec_fp.get("prd")
    assert spec_fp.get("test_case")
    assert spec_fp.get("fingerprint_hash")

    assert isinstance(baseline_2.get("open_questions"), list)
    assert isinstance(baseline_2.get("delta_summary"), dict)
    assert isinstance(baseline_2.get("risk_flags"), list)
    assert "prd" in baseline_2.get("delta_summary", {}).get("changed_layers", [])

    change_impact = second.get("change_impact", {})
    assert change_impact.get("doc_chain_update_required") is True
    task_names = [str(item.get("task", "")) for item in change_impact.get("tasks", []) if isinstance(item, dict)]
    assert any(task == "regenerate-prd" for task in task_names)
