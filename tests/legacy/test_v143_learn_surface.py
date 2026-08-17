from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.learn_surface import run_governed_recall
from beacon.utils.support_surface_transactions import load_support_surface_summary


VERSION = "v1.4.3"
FEATURE = "beacon-v1.4.3-governed-learning-recall-and-route-explainability"


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


def test_v143_learn_surface_exists_and_is_visible(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    payload = run_governed_recall(tmp_path, version=VERSION, feature=FEATURE, mode="recall", limit=5)

    assert payload["surface"] == "beacon-learn"
    assert payload["status"] == "advisory"
    summary = load_support_surface_summary(tmp_path, surface="beacon-learn")
    assert summary["status"] == "advisory"
    assert "beacon help" in summary["latest_next_route"]


def test_v143_stale_and_conflicting_learning_downgraded(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)
    memory_root = tmp_path / ".beacon" / "memory"
    memory_root.mkdir(parents=True, exist_ok=True)
    (memory_root / "decisions.json").write_text(
        json.dumps(
            {
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
                    {
                        "memory_id": "m-3",
                        "decision": "This is stale and should be downgraded.",
                        "content": "This is stale and should be downgraded.",
                        "source": "remember",
                        "source_session_id": "manual",
                        "evidence_ref": ["docs/c.md"],
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = run_governed_recall(tmp_path, version=VERSION, feature=FEATURE, mode="audit", memory_type="decision", limit=10)

    assert payload["reason_codes"] == ["learning_conflict_requires_operator_resolution"]
    assert len(payload["conflicting_learning"]) == 1
    assert len(payload["stale_learning"]) == 1
    assert payload["status"] == "advisory"
