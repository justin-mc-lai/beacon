from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.ceo_review_surface import run_ceo_review
from beacon.utils.help_support import build_help_payload
from beacon.utils.learn_surface import run_governed_recall


VERSION = "v1.4.3"
FEATURE = "beacon-v1.4.3-governed-learning-recall-and-route-explainability"
SLUG = "beacon-v1.4.3-governed-learning-recall-and-route-explainability"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_feature_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / VERSION
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "execution" / "project-skill-qa-evolution-blueprint.md").write_text("# Blueprint\n", encoding="utf-8")
    (base / "source-architecture").mkdir(parents=True, exist_ok=True)
    (base / "source-architecture" / "index.md").write_text("# Source Architecture\n", encoding="utf-8")
    (base / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "user-story" / f"{SLUG}.md").write_text("# User Story\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (base / ".machine" / "qa" / f"{SLUG}.story-scenario-map.json").write_text('{"scenarios":[]}\n', encoding="utf-8")
    (base / ".machine" / "user-story" / f"{SLUG}.json").parent.mkdir(parents=True, exist_ok=True)
    (base / ".machine" / "user-story" / f"{SLUG}.json").write_text('{"items":[]}\n', encoding="utf-8")
    req_dir = base / ".machine" / "requirement"
    req_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ("freeze-contract", "completeness", "envelope", "candidate-ledger", "supplement-decision-log"):
        (req_dir / f"{SLUG}.{suffix}.json").write_text('{"status":"ok"}\n', encoding="utf-8")


def test_v143_support_surfaces_explain_route_and_learning(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)
    run_ceo_review(tmp_path, version=VERSION, feature=FEATURE, decision="reframe")
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
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    run_governed_recall(tmp_path, version=VERSION, feature=FEATURE, mode="audit", memory_type="decision", limit=5)

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["support_surface_projection"]["primary_operator_doc_ref"].endswith("execution/index.md")
    assert payload["learning_surface"]["subject_surface"]
    assert any(step["step"] == "learning_surface" for step in payload["decision_trace"])
