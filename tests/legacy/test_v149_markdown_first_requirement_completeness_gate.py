from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.help_support import build_help_payload
from beacon.utils.requirement_deepening import build_requirement_completeness_gate
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime import write_json
from beacon.utils.story_state import freeze_story_state, sync_story_state_from_docs


VERSION = "v1.4.9"
FEATURE = "Markdown First Requirement Completeness Gate"
SLUG = "markdown-first-requirement-completeness-gate"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_docs(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# Global Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# Summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# Execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/boundaries.md", "# Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/execution/project-skill-qa-evolution-blueprint.md", "# Skill Blueprint\n")
    _write(root, f"docs/beacon/{VERSION}/source-architecture/index.md", "# Source Architecture\n")
    _write(root, f"docs/beacon/{VERSION}/source-architecture/{SLUG}.md", "# Source Architecture\n")
    _write(root, f"docs/beacon/{VERSION}/research/{SLUG}.md", "# Research\n\n## Business Flow\n- Markdown first.\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        "\n".join(
            [
                "# PRD: Markdown First Requirement Completeness Gate",
                "",
                "## 1. Problem",
                "- Requirement truth lives in human Markdown.",
                "",
                "## 2. Goals",
                "- Machine completeness is a projection, not a truth gate.",
                "",
                "## 8. Acceptance Criteria",
                "- AC-001 Frozen Markdown truth admits downstream stages without completeness projection JSON.",
                "- AC-002 Missing completeness projection recommends material sync only.",
                "- AC-003 Broken Markdown truth still blocks downstream admission.",
            ]
        )
        + "\n",
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        "\n".join(
            [
                "# User Story",
                "",
                "## Acceptance Criteria",
                "- AC-001 Frozen Markdown truth admits downstream stages without completeness projection JSON.",
                "- AC-002 Missing completeness projection recommends material sync only.",
                "- AC-003 Broken Markdown truth still blocks downstream admission.",
            ]
        )
        + "\n",
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
        "\n".join(
            [
                "# Test Cases",
                "",
                "| AC ID | TC ID | Layer | Command | Assertion |",
                "| --- | --- | --- | --- | --- |",
                "| AC-001 | TC-001 | gate | pytest | downstream admission is nonblocking |",
                "| AC-002 | TC-002 | gate | pytest | sync-materials is advisory |",
                "| AC-003 | TC-003 | gate | pytest | broken Markdown truth blocks |",
            ]
        )
        + "\n",
    )


def _freeze(root: Path) -> None:
    sync_story_state_from_docs(root, VERSION, FEATURE)
    freeze_story_state(root, VERSION, FEATURE)
    freeze_revision_state(root, version=VERSION, feature=FEATURE)
    write_json(
        root / "docs" / "beacon" / VERSION / ".machine" / "change" / f"{SLUG}.refreeze-transaction.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "version": VERSION,
            "refreeze_status": "complete",
            "truth_revision_after": {"revision_id": "R1", "doc_status": "frozen"},
        },
    )


def test_missing_completeness_projection_is_nonblocking_when_markdown_truth_is_frozen(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)

    gate = build_requirement_completeness_gate(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        target_stage="qa",
    )

    assert gate["status"] == "pass"
    assert gate["blocked"] is False
    assert gate["reason_code"] == "requirement_completeness_projection_missing"
    assert "doctor sync-materials" in gate["recommended_command"]
    assert "test-case create" not in gate["recommended_command"]
    assert gate["stage_gates"]["stage_admission"]["status"] == "pass"
    assert gate["markdown_first_truth"]["status"] == "pass"


def test_broken_markdown_truth_still_blocks_when_completeness_projection_is_missing(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    qa_path = tmp_path / "docs" / "beacon" / VERSION / "qa" / "test-cases" / f"{SLUG}.md"
    payload = qa_path.read_text(encoding="utf-8").replace("AC-003", "AC-999")
    qa_path.write_text(payload, encoding="utf-8")

    gate = build_requirement_completeness_gate(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        target_stage="qa",
    )

    assert gate["status"] == "blocked"
    assert gate["blocked"] is True
    assert gate["reason_code"] == "requirement_completeness_missing"
    assert "test-case create" in gate["recommended_command"]


def test_existing_completeness_projection_still_controls_blocking_verdict(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    requirement_dir = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "requirement"
    write_json(
        requirement_dir / f"{SLUG}.completeness.json",
        {
            "schema_version": "1.0",
            "completeness_verdict": "blocked",
            "readiness": {"implement_ready": False},
            "unresolved_gap_count": 1,
            "high_risk_unresolved_categories": ["critical-role-state-gap"],
            "role_state_risk_coverage": {},
        },
    )
    write_json(requirement_dir / f"{SLUG}.candidate-ledger.json", {"entries": [{"gap_id": "gap-1"}]})
    write_json(requirement_dir / f"{SLUG}.supplement-decision-log.json", {"entries": []})

    gate = build_requirement_completeness_gate(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        target_stage="qa",
    )

    assert gate["status"] == "blocked"
    assert gate["reason_code"] == "requirement_completeness_blocked"
    assert json.loads((requirement_dir / f"{SLUG}.completeness.json").read_text(encoding="utf-8"))[
        "completeness_verdict"
    ] == "blocked"


def test_help_brainstorm_hint_uses_feature_research_for_v149_markdown_first(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["requirement_completeness"]["status"] == "pass"
    assert payload["requirement_completeness"]["blocked"] is False
    assert payload["brainstorm_hint"]["recommended_output"] == f"docs/beacon/{VERSION}/research/{SLUG}.md"
