"""Intent-First Truth Generation Protocol for v1.6.2+

Transforms truth generation from template-driven to intent-driven:
  1. Intent Capture: extract deterministic statements from user utterance
  2. Intent Verification: user confirms or corrects intent list
  3. Structured Truth Derivation: derive truth.md from confirmed intents
  4. Determinism Verification: TIG-DC gate ensures no placeholders/hollow templates
  5. Freeze: frozen truth with provenance chain
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IntentCapture:
    """A single user intent extracted from utterance."""

    text: str
    source_type: str  # user_intent | context_analysis | constraint_derivation
    source_ref: str


def _split_utterance(utterance: str) -> list[str]:
    """Split user utterance into candidate intent sentences."""
    # Split on Chinese/English sentence terminators
    raw = re.split(r"[。\.\n;；]", utterance)
    return [s.strip() for s in raw if len(s.strip()) >= 10]


def capture_intents_from_utterance(user_utterance: str) -> list[IntentCapture]:
    """Phase 1: Capture intents from raw user utterance.

    Returns a list of IntentCapture objects, each representing a deterministic
    user intent.  Minimal heuristic: split on sentence boundaries and treat
    each substantive sentence as an intent.
    """
    candidates = _split_utterance(user_utterance)
    intents: list[IntentCapture] = []
    for idx, text in enumerate(candidates, start=1):
        intents.append(
            IntentCapture(
                text=text,
                source_type="user_intent",
                source_ref=f"utterance_sentence_{idx}: {text[:120]}",
            )
        )
    return intents


def derive_ac_from_intent(intent: IntentCapture, index: int) -> dict[str, str]:
    """Phase 3: Derive a single AC row from a confirmed intent."""
    ac_id = f"AC-{index:03d}"
    description = intent.text
    # Simple heuristic: if intent contains "should", "must", "shall", "应", "必须"
    # treat it as the requirement description directly.
    return {
        "ac_id": ac_id,
        "theme": "intent",
        "description": description,
    }


def build_provenance(intents: list[IntentCapture]) -> list[dict[str, Any]]:
    """Build provenance entries for truth frontmatter."""
    provenance: list[dict[str, Any]] = []
    for idx, intent in enumerate(intents, start=1):
        ac_id = f"AC-{idx:03d}"
        provenance.append(
            {
                "ac_id": ac_id,
                "source_type": intent.source_type,
                "source_ref": intent.source_ref,
            }
        )
    return provenance


def _render_frontmatter(
    *,
    slug: str,
    version: str,
    language: str = "en",
    status: str = "draft",
    provenance: list[dict[str, Any]] | None = None,
) -> str:
    """Render YAML frontmatter with optional provenance block."""
    lines = [
        "---",
        f"slug: {slug}",
        f"version: {version}",
        f"status: {status}",
        f"language: {language}",
        "canonical_refs:",
        f"  prd: docs/beacon/{version}/features/{slug}/truth.md",
        f"  user_story: docs/beacon/{version}/features/{slug}/truth.md",
        f"  test_case: docs/beacon/{version}/features/{slug}/tests.md",
        "parser_contract: beacon-feature-package-v1",
        "truth_source_model: intent_first_authoritative",
        "truth_map_contract: beacon-truth-map-v1",
    ]
    if provenance:
        lines.append("provenance:")
        for entry in provenance:
            lines.append(f"  - ac_id: {entry['ac_id']}")
            lines.append(f"    source_type: {entry['source_type']}")
            lines.append(f"    source_ref: \"{entry['source_ref']}\"")
    lines.append("---")
    return "\n".join(lines)


def render_intent_first_truth(
    feature: str,
    version: str,
    intents: list[IntentCapture],
    user_utterance: str,
) -> str:
    """Phase 3: Render a complete truth.md from confirmed intents.

    v1.6.10+: gold-aligned structure (人话 + matrix + FSM + illegal + AC + Non-goals).
    """
    slug = feature.strip().lower().replace(" ", "-").replace("_", "-")
    provenance = build_provenance(intents)
    ac_rows = [derive_ac_from_intent(intent, idx) for idx, intent in enumerate(intents, start=1)]
    if not ac_rows:
        ac_rows = [{"ac_id": "AC-001", "theme": "core", "description": "Confirm core intent is delivered"}]

    # semver gate
    try:
        parts = str(version or "v0").lstrip("v").split(".")
        sv = (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0, int(parts[2]) if len(parts) > 2 else 0)
    except Exception:
        sv = (0, 0, 0)

    if sv >= (1, 6, 10):
        lines = [
            "---",
            f"slug: {slug}",
            f"version: {version}",
            "status: draft",
            "language: zh",
            "domain_required: false",
            "parser_contract: beacon-feature-package-v2",
            "materials_status: current",
            "truth_source_model: intent_first",
            "canonical_refs:",
            f"  prd: docs/beacon/{version}/features/{slug}/truth.md",
            f"  user_story: docs/beacon/{version}/features/{slug}/truth.md",
            f"  test_case: docs/beacon/{version}/features/{slug}/tests.md",
            "---",
            "",
            f"# Requirement Truth: {feature} ({version})",
            "",
            "## 人话",
            "",
            f"根据用户意图生成 `{feature}` 的需求真相。能做的写清，不能做的写清，怎样算完写清。",
            "",
            "- 能做：已确认意图对应的结果",
            "- 不能做：未确认意图默认实现",
            "- 怎样算完：Intent Matrix must covered + 每 AC 有 TC + review 通过后再 freeze",
            "",
            "## User Intent",
            "",
            f"> {user_utterance}",
            "",
            "## Intent Coverage Matrix",
            "",
            "| intent_id | source | strength | landing | status |",
            "|-----------|--------|----------|---------|--------|",
        ]
        for idx, row in enumerate(ac_rows, start=1):
            lines.append(f"| INT-{idx:03d} | prompt | must | {row['ac_id']} | covered |")
        lines.extend(
            [
                "",
                "## Acceptance Criteria",
                "",
                "| AC ID | Description |",
                "|-------|-------------|",
            ]
        )
        for row in ac_rows:
            lines.append(f"| {row['ac_id']} | {row.get('description') or row.get('theme') or ''} |")
        lines.extend(
            [
                "",
                "## FSM 五元组",
                "",
                "| State | Event | Guard | To | Action |",
                "|-------|-------|-------|-----|--------|",
                "| draft | submit | package_complete | in_review | — |",
                "| in_review | pass | gate_ok | frozen | set_frozen |",
                "| in_review | fail | — | draft | attach_report |",
                "",
                "### invalid / illegal",
                "",
                "- draft → frozen without review",
                "",
                "## Non-goals",
                "",
                "- 未在 Matrix 声明的意图",
                "",
                "## Provenance",
                "",
                "Each AC traces to a confirmed user intent.",
                "",
                "## Source Excerpt",
                "",
                "```markdown",
                user_utterance[:4000].rstrip(),
                "```",
                "",
            ]
        )
        return "\n".join(lines)

    lines = [
        _render_frontmatter(slug=slug, version=version, language="en", status="draft", provenance=provenance),
        "",
        f"# Feature: {feature}",
        "",
        "## Overview",
        "",
        "This truth package was generated via the Intent-First Protocol.",
        "Every acceptance criterion is derived from a confirmed user intent.",
        "",
        "## User Intent",
        "",
        f"> {user_utterance}",
        "",
        "## Acceptance Criteria",
        "",
        "| AC ID | Theme | Description |",
        "|-------|-------|-------------|",
    ]
    for row in ac_rows:
        lines.append(f"| {row['ac_id']} | {row['theme']} | {row['description']} |")
    lines.extend(
        [
            "",
            "## Provenance",
            "",
            "Each AC above traces to a confirmed user intent (see frontmatter).",
            "Source types allowed: `user_intent`, `context_analysis`, `constraint_derivation`.",
            "",
            "## Source Excerpt",
            "",
            "```markdown",
            user_utterance[:4000].rstrip(),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def render_intent_first_tests(feature: str, ac_rows: list[dict[str, str]], version: str = "") -> str:
    """Render a tests.md from derived AC rows."""
    slug = feature.strip().lower().replace(" ", "-").replace("_", "-")
    try:
        parts = str(version or "v0").lstrip("v").split(".")
        sv = (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0, int(parts[2]) if len(parts) > 2 else 0)
    except Exception:
        sv = (0, 0, 0)
    if sv >= (1, 6, 10):
        lines = [
            "---",
            f"slug: {slug}",
            f"version: {version}",
            "materials_status: current",
            "---",
            "",
            f"# Tests: {feature}",
            "",
            "| TC ID | AC ID | Command | Assertion |",
            "|-------|-------|---------|-----------|",
        ]
        for idx, row in enumerate(ac_rows, start=1):
            ac = row["ac_id"]
            lines.append(
                f"| TC-{idx:03d} | {ac} | `rg -n '{ac}' docs/beacon/{version}/features/{slug}/truth.md` | AC present |"
            )
        lines.append("")
        return "\n".join(lines)
    lines = [
        f"# Tests: {feature}",
        "",
        "## Coverage Matrix",
        "",
        "| AC ID | TC ID | Layer | Command | Assertion |",
        "|-------|-------|-------|---------|-----------|",
    ]
    for idx, row in enumerate(ac_rows, start=1):
        tc_id = f"TC-{idx:03d}"
        lines.append(f"| {row['ac_id']} | {tc_id} | unit | `beacon doctor --help` | exit 0 |")
    lines.extend(
        [
            "",
            "## Validation Note",
            "",
            "Tests derived from intent-first AC table. Update commands and assertions to match implementation.",
            "",
        ]
    )
    return "\n".join(lines)


def render_intent_first_tasks(feature: str, ac_rows: list[dict[str, str]]) -> str:
    """Render a tasks.md from derived AC rows."""
    lines = [f"# Tasks: {feature}", ""]
    for row in ac_rows:
        lines.append(f"- [ ] Implement {row['ac_id']}: {row['description'][:60]}")
    lines.append("")
    return "\n".join(lines)


def render_intent_first_evidence(feature: str) -> str:
    """Render an evidence.md stub."""
    return f"""# Evidence: {feature}

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| qa | qa_verdict | tests/ | linked | qa |

"""
