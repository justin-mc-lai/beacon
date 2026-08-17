"""Intent-First Truth Generation Protocol tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from beacon.utils.intent_first import (
    IntentCapture,
    capture_intents_from_utterance,
    derive_ac_from_intent,
    build_provenance,
    render_intent_first_truth,
    render_intent_first_tests,
    render_intent_first_tasks,
    render_intent_first_evidence,
)
from beacon.utils.truth_integrity import build_truth_integrity_gate

VERSION = "v1.6.10"


def test_capture_intents_from_utterance_splits_sentences() -> None:
    utterance = (
        "The system should validate all user inputs before processing. "
        "It must reject malformed data with clear error messages. "
        "管理员应能查看所有审计日志。"
    )
    intents = capture_intents_from_utterance(utterance)
    assert len(intents) == 3
    assert intents[0].source_type == "user_intent"
    assert "validate all user inputs" in intents[0].text


def test_capture_intents_skips_short_fragments() -> None:
    utterance = "A. B. Short. This is a real intent sentence that should be captured."
    intents = capture_intents_from_utterance(utterance)
    assert len(intents) == 1
    assert "real intent sentence" in intents[0].text


def test_derive_ac_from_intent() -> None:
    intent = IntentCapture(
        text="The system should return HTTP 404 for missing resources.",
        source_type="user_intent",
        source_ref="utterance_1",
    )
    ac = derive_ac_from_intent(intent, 1)
    assert ac["ac_id"] == "AC-001"
    assert ac["theme"] == "intent"
    assert "HTTP 404" in ac["description"]


def test_build_provenance() -> None:
    intents = [
        IntentCapture(text="foo", source_type="user_intent", source_ref="ref1"),
        IntentCapture(text="bar", source_type="context_analysis", source_ref="ref2"),
    ]
    prov = build_provenance(intents)
    assert len(prov) == 2
    assert prov[0]["ac_id"] == "AC-001"
    assert prov[0]["source_type"] == "user_intent"
    assert prov[1]["ac_id"] == "AC-002"
    assert prov[1]["source_type"] == "context_analysis"


def test_render_intent_first_truth_contains_provenance() -> None:
    intents = [
        IntentCapture(
            text="The system must block freeze when placeholders are present.",
            source_type="user_intent",
            source_ref="utterance_1",
        )
    ]
    content = render_intent_first_truth("tig-dc-v160", VERSION, intents, "Block freeze on placeholders")
    assert "---" in content
    assert "truth_source_model: intent_first" in content
    assert "provenance:" in content
    assert "AC-001" in content
    assert "## User Intent" in content
    assert "Block freeze on placeholders" in content


def test_render_intent_first_truth_tig_dc_passes(tmp_path: Path) -> None:
    """Intent-first generated truth with clean intents should pass TIG-DC without blocking."""
    intents = [
        IntentCapture(
            text="The gate must reject any truth containing indeterminate words.",
            source_type="user_intent",
            source_ref="utterance_1",
        ),
        IntentCapture(
            text="Vague template sentences must be detected and reported as warnings.",
            source_type="context_analysis",
            source_ref="analysis_1",
        ),
    ]
    content = render_intent_first_truth("intent-first-smoke", VERSION, intents, "Clean intent")

    # Write to temp feature package
    slug = "intent-first-smoke"
    feature_dir = tmp_path / "docs/beacon" / VERSION / "features" / slug
    feature_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/beacon/VERSION").write_text(f"{VERSION}\n", encoding="utf-8")
    (feature_dir / "truth.md").write_text(content, encoding="utf-8")

    ac_rows = [derive_ac_from_intent(intent, idx) for idx, intent in enumerate(intents, start=1)]
    (feature_dir / "tests.md").write_text(render_intent_first_tests("intent-first-smoke", ac_rows, version=VERSION), encoding="utf-8")
    (feature_dir / "tasks.md").write_text(render_intent_first_tasks("intent-first-smoke", ac_rows), encoding="utf-8")
    (feature_dir / "evidence.md").write_text(render_intent_first_evidence("intent-first-smoke"), encoding="utf-8")

    gate = build_truth_integrity_gate(tmp_path, version=VERSION, feature=slug, mode="block")
    dc = gate.get("determinism_check", {})
    # Clean intents should produce no placeholders and no hollow templates
    assert gate["status"] == "pass", f"Unexpectedly blocked: {gate.get('reason_code')} findings={gate.get('findings')}"
    assert not gate["blocked"]
    assert dc.get("placeholder_count", 0) == 0
    assert dc.get("hollow_template_count", 0) == 0


def test_render_intent_first_tests_has_coverage_matrix() -> None:
    ac_rows = [
        {"ac_id": "AC-001", "theme": "intent", "description": "foo"},
        {"ac_id": "AC-002", "theme": "intent", "description": "bar"},
    ]
    content = render_intent_first_tests("feat", ac_rows, version=VERSION)
    assert "| TC-001 | AC-001 |" in content
    assert "| TC-002 | AC-002 |" in content


def test_render_intent_first_tasks_has_checklist() -> None:
    ac_rows = [
        {"ac_id": "AC-001", "theme": "intent", "description": "Validate user input thoroughly"},
    ]
    content = render_intent_first_tasks("feat", ac_rows)
    assert "Implement AC-001:" in content
    assert "ac=AC-001" in content
    assert "evidence=" in content


def test_render_intent_first_evidence_stub() -> None:
    content = render_intent_first_evidence("feat")
    assert "Evidence: feat" in content
    assert "linked" in content
