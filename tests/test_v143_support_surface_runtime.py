from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.ceo_review_surface import run_ceo_review
from beacon.utils.learn_surface import run_governed_recall
from beacon.utils.support_surface_transactions import load_support_surface_summary


VERSION = "v1.4.3"
FEATURE = "beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_feature_docs(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/architecture-blueprint.md", "# blueprint\n")
    _write(root, f"docs/beacon/{VERSION}/prd/{FEATURE}.md", "# prd\n")
    _write(root, f"docs/beacon/{VERSION}/user-story/{FEATURE}.md", "# story\n")
    _write(root, f"docs/beacon/{VERSION}/qa/test-cases/{FEATURE}.md", "# test\n")


def test_v143_ceo_review_should_write_support_surface_receipt(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    payload = run_ceo_review(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        focus="scope",
        decision="reframe",
    )

    assert payload["surface"] == "beacon-ceo-review"
    assert payload["decision"] == "reframe"
    machine_path = tmp_path / payload["artifacts"]["machine_path"]
    state_path = tmp_path / payload["artifacts"]["state_path"]
    assert machine_path.exists()
    assert state_path.exists()
    summary = load_support_surface_summary(tmp_path, surface="beacon-ceo-review")
    assert summary["status"] == "accepted_for_writeback"
    assert "beacon change" in summary["latest_next_route"]


def test_v143_governed_recall_should_write_learning_receipt(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)
    memory_root = tmp_path / ".beacon" / "memory"
    memory_root.mkdir(parents=True, exist_ok=True)
    legacy_payload = {
        "schema_version": "3.0",
        "decisions": [
            {
                "memory_id": "m-1",
                "decision": "Prefer explicit route explainability.",
                "content": "Prefer explicit route explainability.",
                "source": "remember",
                "source_session_id": "manual",
                "evidence_ref": ["docs/a.md"],
            },
            {
                "memory_id": "m-2",
                "decision": "Conflict: previous route may now be stale.",
                "content": "Conflict: previous route may now be stale.",
                "source": "remember",
                "source_session_id": "manual",
                "evidence_ref": ["docs/b.md"],
            },
        ],
    }
    (memory_root / "decisions.json").write_text(json.dumps(legacy_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    payload = run_governed_recall(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        mode="audit",
        memory_type="decision",
        limit=10,
    )

    assert payload["surface"] == "beacon-learn"
    assert payload["decision"] == "audit"
    summary = load_support_surface_summary(tmp_path, surface="beacon-learn")
    assert summary["status"] == "advisory"
    assert "beacon help" in summary["latest_next_route"]
