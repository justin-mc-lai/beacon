from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any


_SKILL_DIR_MAP = {
    "prd": "beacon-gen-truth",
    "implement": "beacon-gen-implement",
    "qa": "beacon-eval-qa",
    "release": "beacon-eval-release",
}

_SECTION_MAP = {
    "## Inputs Contract": "inputs_contract",
    "## Decision Protocol": "decision_protocol",
    "## Anti-Inertia Notes": "anti_inertia_notes",
    "## Learning Notes": "learning_notes",
    "## Backstop CLI": "backstop_cli",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _skill_path(stage: str) -> Path:
    skill_dir = _SKILL_DIR_MAP.get(stage, "")
    if not skill_dir:
        raise KeyError(f"unsupported decision surface stage: {stage}")
    return _repo_root() / "skills" / "beacon" / skill_dir / "SKILL.md"


@lru_cache(maxsize=None)
def _read_skill_sections(stage: str) -> dict[str, Any]:
    path = _skill_path(stage)
    text = path.read_text(encoding="utf-8")
    sections: dict[str, list[str]] = {value: [] for value in _SECTION_MAP.values()}
    current_key = ""
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        mapped = _SECTION_MAP.get(line.strip())
        if mapped:
            current_key = mapped
            continue
        if current_key and line.strip().startswith("## "):
            current_key = ""
            continue
        if not current_key:
            continue
        cleaned = line.strip()
        if cleaned.startswith("- "):
            cleaned = cleaned[2:].strip()
        elif cleaned.startswith("* "):
            cleaned = cleaned[2:].strip()
        if cleaned:
            sections[current_key].append(cleaned)
    return {
        "path": str(path.relative_to(_repo_root())),
        "sections": sections,
    }


def build_skill_decision_surface(
    stage: str,
    *,
    reason_code: str = "",
    recommended_command: str = "",
    blocked: bool = False,
    dual_read_required: bool = True,
) -> dict[str, Any]:
    payload = _read_skill_sections(stage)
    sections = payload.get("sections", {}) if isinstance(payload.get("sections"), dict) else {}
    decision_protocol = list(sections.get("decision_protocol", []) or [])
    anti_inertia_notes = list(sections.get("anti_inertia_notes", []) or [])
    learning_notes = list(sections.get("learning_notes", []) or [])
    backstop_cli = list(sections.get("backstop_cli", []) or [])
    primary_reason = decision_protocol[0] if decision_protocol else ""
    if blocked and anti_inertia_notes:
        primary_reason = anti_inertia_notes[0]
    return {
        "stage": stage,
        "skill_ref": str(payload.get("path") or ""),
        "inputs_contract": list(sections.get("inputs_contract", []) or []),
        "decision_protocol": decision_protocol,
        "anti_inertia_notes": anti_inertia_notes,
        "learning_notes": learning_notes,
        "backstop_cli": backstop_cli,
        "primary_reason": primary_reason,
        "recommended_command": recommended_command or (backstop_cli[0] if backstop_cli else ""),
        "reason_code": reason_code,
    }


def build_python_guardrail_contract(
    stage: str,
    *,
    reason_code: str = "",
    blocked: bool = False,
    dual_read_required: bool = True,
) -> dict[str, Any]:
    return {
        "stage": stage,
        "decision_owner": "skill_surface",
        "enforcement_owner": "python_guardrail",
        "blocked": blocked,
        "reason_code": reason_code,
        "dual_read_required_before_cutover": dual_read_required,
        "fail_closed": True,
    }


def attach_skill_decision_surface(
    payload: dict[str, Any],
    *,
    stage: str,
    reason_code: str = "",
    recommended_command: str = "",
    blocked: bool = False,
    dual_read_required: bool = True,
) -> dict[str, Any]:
    payload["decision_surface"] = build_skill_decision_surface(
        stage,
        reason_code=reason_code,
        recommended_command=recommended_command,
        blocked=blocked,
        dual_read_required=dual_read_required,
    )
    payload["guardrail_contract"] = build_python_guardrail_contract(
        stage,
        reason_code=reason_code,
        blocked=blocked,
        dual_read_required=dual_read_required,
    )
    return payload
