"""Fixed English truth templates for v1.4.12+.

Section titles and table column names are pure English strings, immutable by LLM.
Content language is controlled by --lang parameter (en|zh), written to **Language** front matter.
Outline sections contain mandatory mermaid FILL annotations.
"""

from __future__ import annotations

from datetime import datetime


# PRD mandatory sections in order
PRD_MANDATORY = [
    "Overview",
    "Outline",
    "Problem",
    "Goals",
    "Scope",
    "Functional Requirements",
    "Acceptance Criteria",
    "Non-Goals",
    "Success Metrics",
]

# PRD optional sections with insertion points
PRD_OPTIONAL: dict[str, str] = {
    "Context": "after_outline",
    "Design Principles": "after_goals",
    "Source Contract": "after_functional_requirements",
    "State Axes": "after_functional_requirements",
    "Runtime Behavior Contract": "after_functional_requirements",
    "Evidence Contract": "before_acceptance_criteria",
    "Diagram Truth Layer": "after_success_metrics",
}

# User Story mandatory sections in order
USER_STORY_MANDATORY = [
    "Story",
    "Outline",
    "Acceptance Criteria",
    "Test Story Map",
    "References",
]

# User Story optional sections
USER_STORY_OPTIONAL: dict[str, str] = {
    "State Axis Coverage": "after_acceptance_criteria",
}

# Test Case mandatory sections in order
TEST_CASE_MANDATORY = [
    "Outline",
    "Coverage Matrix",
    "Explicit Non Coverage",
]

# Test Case optional sections
TEST_CASE_OPTIONAL: dict[str, str] = {
    "Branch Coverage Mapping": "after_coverage_matrix",
}


def _now_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def render_prd_template(*, feature_slug: str, version: str, lang: str = "en") -> str:
    """Return PRD fixed template with English section titles, no numbering, and Outline mermaid."""
    lines = [
        f"# PRD: <Human-Readable Name>",
        "",
        f"**Feature**: `{feature_slug}`",
        f"**Version**: `{version}`",
        f"**Status**: `template`",
        f"**Date**: `{_now_date()}`",
        f"**Language**: `{lang}`",
        "",
        "## Overview",
        "<!-- FILL: One paragraph describing the problem and expected outcome. -->",
        "",
        "## Outline",
        "<!-- FILL: Mermaid diagram showing the feature's core flow or state transitions.",
        "     Use flowchart TD/LR for procedural features, stateDiagram-v2 for stateful features.",
        "     This is the reader's first visual map — keep it high-level and readable. -->",
        "",
        "```mermaid",
        "flowchart TD",
        "    A[Start] --> B{Decision}",
        "    B -->|Path 1| C[Outcome 1]",
        "    B -->|Path 2| D[Outcome 2]",
        "```",
        "",
        "## Context",
        "<!-- FILL: References to research docs, architecture docs, and global constraints. -->",
        "",
        "## Problem",
        "<!-- FILL: Specific problem in the current system, backed by source-anchored evidence. -->",
        "",
        "## Goals",
        "<!-- FILL: List of acceptance criteria. -->",
        "",
        "## Design Principles",
        "<!-- FILL: Design constraints and principles this feature must follow. -->",
        "",
        "## Scope",
        "",
        "### In Scope",
        "<!-- FILL -->",
        "",
        "### Out of Scope",
        "<!-- FILL -->",
        "",
        "## Functional Requirements",
        "",
        "| FR ID | Related AC | Requirement |",
        "|-------|-----------|-------------|",
        "<!-- FILL: FR-001 | AC-001 | Description -->",
        "",
        "## Source Contract",
        "<!-- FILL: Affected source files with line numbers. -->",
        "",
        "## State Axes",
        "",
        "| Axis | States | Meaning |",
        "|------|--------|---------|",
        "<!-- FILL -->",
        "",
        "## Acceptance Criteria",
        "<!-- FILL: List all ACs with details. -->",
        "",
        "## Non-Goals",
        "<!-- FILL: Explicitly excluded items. -->",
        "",
        "## Success Metrics",
        "<!-- FILL: How to determine successful delivery. -->",
        "",
        "## Diagram Truth Layer",
        "<!-- Optional: only for features with complex state machines, branch flows, or decision priorities.",
        "     Use mermaid stateDiagram-v2 for detailed state transitions.",
        "     Use mermaid flowchart for detailed branch flows.",
        "     Diagram Truth Layer extends the Outline, not replaces it. -->",
        "",
        "### Diagram Types",
        "<!-- FILL: branch-flow, state-machine, decision-priority -->",
        "",
        "### State Axes",
        "",
        "| Axis | States | Meaning |",
        "|------|--------|---------|",
        "<!-- FILL -->",
        "",
        "### Branch Flow",
        "<!-- FILL: mermaid flowchart or stateDiagram-v2 for detailed branches -->",
        "",
        "### Propagation Contract",
        "- Diagram truth must stay explicit through freeze readiness, implementation planning, and QA coverage.",
        "- State axes must not be silently compressed into one implicit status field.",
        "- User-story AC must declare which state axis transitions they cover.",
        "- Test-case coverage must declare which diagram branches they cover.",
    ]
    return "\n".join(lines)


def render_user_story_template(*, feature_slug: str, version: str, lang: str = "en") -> str:
    """Return User Story fixed template with English section titles and Outline mermaid."""
    lines = [
        f"# User Story: <Human-Readable Name>",
        "",
        f"**Feature**: `{feature_slug}`",
        f"**Version**: `{version}`",
        f"**Status**: `template`",
        f"**Date**: `{_now_date()}`",
        f"**Language**: `{lang}`",
        "",
        "## Story",
        "<!-- FILL: As a <role>, I want <goal>, so that <benefit>. -->",
        "",
        "## Outline",
        "<!-- FILL: Mermaid diagram showing the user journey through key paths.",
        "     Use flowchart LR for user journey. Each node maps to an AC.",
        "     This is the reader's first visual map of the user story. -->",
        "",
        "```mermaid",
        "flowchart LR",
        "    A[User starts] --> B[Action 1]",
        "    B --> C{Decision}",
        "    C -->|AC-001| D[Outcome 1]",
        "    C -->|AC-002| E[Outcome 2]",
        "```",
        "",
        "## Acceptance Criteria",
        "",
        "| AC ID | Theme | Description |",
        "|-------|-------|-------------|",
        "<!-- FILL: AC-001 | <theme> | <description> -->",
        "",
        "## State Axis Coverage",
        "<!-- Optional: only when PRD declares state axes. -->",
        "",
        "| AC ID | State Axis | Transition | Covered |",
        "|-------|-----------|------------|---------|",
        "<!-- FILL -->",
        "",
        "## Test Story Map",
        "",
        "| Test ID | Covers | Scenario |",
        "|---------|--------|----------|",
        "<!-- FILL: TC-001 | AC-001 | <scenario> -->",
        "",
        "## References",
        f"- Research: `docs/beacon/{version}/research/{feature_slug}.md`",
        f"- PRD: `docs/beacon/{version}/prd/{feature_slug}.md`",
        f"- Test cases: `docs/beacon/{version}/qa/test-cases/{feature_slug}.md`",
    ]
    return "\n".join(lines)


def render_test_case_template(*, feature_slug: str, version: str, lang: str = "en") -> str:
    """Return Test Case fixed template with English section titles and Outline mermaid."""
    lines = [
        f"# Test Cases: <Human-Readable Name>",
        "",
        f"**Feature**: `{feature_slug}`",
        f"**Version**: `{version}`",
        f"**Status**: `template`",
        f"**Date**: `{_now_date()}`",
        f"**Language**: `{lang}`",
        "",
        "## Outline",
        "<!-- FILL: Mermaid diagram showing test coverage layer paths.",
        "     Use flowchart TD for test layers (unit → integration → e2e).",
        "     Each path maps to a Coverage Matrix row. -->",
        "",
        "```mermaid",
        "flowchart TD",
        "    A[Unit Layer] --> B[Integration Layer]",
        "    B --> C[End-to-End Layer]",
        "```",
        "",
        "## Coverage Matrix",
        "",
        "| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |",
        "|-------|-------|-------|-----------------|----------|---------------|",
        "<!-- FILL: AC-001 | TC-001 | unit | <command> | <assertion> | <path> -->",
        "",
        "## Branch Coverage Mapping",
        "<!-- Optional: only when PRD declares branch-flow or state-machine. -->",
        "",
        "| TC ID | Diagram Branch | Transition | Covered |",
        "|-------|----------------|------------|---------|",
        "<!-- FILL -->",
        "",
        "## Explicit Non Coverage",
        "<!-- FILL: Scenarios intentionally not covered and why. -->",
    ]
    return "\n".join(lines)
