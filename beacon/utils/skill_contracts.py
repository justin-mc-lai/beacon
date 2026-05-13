"""Machine-checkable skill contract helpers for Beacon v1.4.6."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


SKILL_ANATOMY_V2_SECTIONS = (
    "## Overview",
    "## When to Use",
    "## Boundary",
    "## Workflow / Decision Loop",
    "## Common Rationalizations",
    "## Red Flags",
    "## Verification",
    "## Evidence Produced",
    "## State Updated",
    "## Gate Impact",
)

ANTI_RATIONALIZATION_SKILLS = (
    "using-beacon",
    "beacon-prd",
    "beacon-change",
    "beacon-brainstorm",
    "beacon-implement",
    "beacon-qa",
    "beacon-release",
)

HOST_VISIBLE_SKILLS = (
    "using-beacon",
    "beacon-prd",
    "beacon-change",
    "beacon-brainstorm",
    "beacon-implement",
    "beacon-qa",
    "beacon-release",
    "beacon-ceo-review",
    "beacon-design-review",
    "beacon-deep",
    "beacon-help",
    "beacon-status",
    "beacon-doctor",
)

SUPPORT_SURFACE_MEMBERS = (
    "brainstorm",
    "deep",
    "ceo-review",
    "design-review",
    "help",
    "status",
    "doctor",
)

PUBLIC_SURFACE_FAMILIES = {
    "truth": ["prd", "user-story", "test-case", "change"],
    "execution": ["prototype", "implement"],
    "support": list(SUPPORT_SURFACE_MEMBERS),
    "gate": ["qa", "release"],
}

_SECTION_RE = re.compile(r"^(## [^\n]+)$", re.MULTILINE)
_SUPPORT_BOUNDARY_MARKERS = (
    "not a new lifecycle stage",
    "not truth source",
    "not gate source",
    "does not rewrite frozen truth",
    "does not freeze truth directly",
    "does not replace `beacon-change`",
)
_STEP_SCRIPT_RE = re.compile(r"^(?:\d+\.\s|step\s+\d+[:\s])", re.IGNORECASE | re.MULTILINE)


def parse_skill_sections(text: str) -> dict[str, str]:
    matches = list(_SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[heading] = text[start:end].strip()
    return sections


def detect_operation_script_smell(text: str) -> bool:
    numbered_steps = len(_STEP_SCRIPT_RE.findall(text))
    return numbered_steps >= 4


def support_surface_constitution() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "family": "support-surface-constitution",
        "members": list(SUPPORT_SURFACE_MEMBERS),
        "boundaries": {
            "not_truth_source": True,
            "not_gate_source": True,
            "not_new_lifecycle_stage": True,
        },
        "allowed_roles": ["challenge", "explain", "route", "diagnose"],
        "forbidden_roles": ["freeze_truth", "ship_gate", "silent_truth_writeback"],
    }


def public_surface_family_contract() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "families": dict(PUBLIC_SURFACE_FAMILIES),
        "handoff_rules": {
            "support_to_truth": ["beacon-change", "beacon-prd", "beacon-user-story", "beacon-test-case"],
            "support_to_execution": ["beacon-implement", "beacon-prototype"],
            "support_to_gate": ["beacon-qa", "beacon-release"],
        },
    }


def build_skill_contract_report(project_root: Path, *, skill_dirs: tuple[str, ...] = HOST_VISIBLE_SKILLS) -> dict[str, Any]:
    skill_root = project_root / "skills" / "beacon"
    reports: list[dict[str, Any]] = []
    for skill_dir in skill_dirs:
        path = skill_root / skill_dir / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        sections = parse_skill_sections(text)
        missing_sections = [section for section in SKILL_ANATOMY_V2_SECTIONS if section not in sections]
        rationalization_body = sections.get("## Common Rationalizations", "")
        anti_rationalization_present = bool(rationalization_body.strip())
        step_script_smell = detect_operation_script_smell(sections.get("## Workflow / Decision Loop", ""))

        boundary_body = " ".join(
            [
                sections.get("## Boundary", ""),
                sections.get("## Gate Impact", ""),
                text,
            ]
        ).lower()
        support_overreach_risk = skill_dir in {
            "beacon-brainstorm",
            "beacon-deep",
            "beacon-ceo-review",
            "beacon-design-review",
            "beacon-help",
            "beacon-status",
            "beacon-doctor",
        } and not any(marker in boundary_body for marker in _SUPPORT_BOUNDARY_MARKERS)

        reports.append(
            {
                "skill_dir": skill_dir,
                "path": str(path.relative_to(project_root)),
                "missing_sections": missing_sections,
                "anti_rationalization_present": anti_rationalization_present,
                "support_overreach_risk": support_overreach_risk,
                "operation_script_smell": step_script_smell,
            }
        )

    failures = [
        item
        for item in reports
        if item["missing_sections"]
        or item["support_overreach_risk"]
        or item["operation_script_smell"]
        or (item["skill_dir"] in ANTI_RATIONALIZATION_SKILLS and not item["anti_rationalization_present"])
    ]
    return {
        "schema_version": "1.0",
        "status": "pass" if not failures else "fail",
        "reports": reports,
        "failure_count": len(failures),
    }
