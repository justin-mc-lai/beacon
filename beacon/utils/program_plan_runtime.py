"""Program plan start runtime — plan_mode classification and artifact bootstrap."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from beacon.utils.program_plan_state import PROGRAM_PLAN_STATES, transition
from beacon.utils.runtime import now_iso


FULL_PARITY_SIGNALS = ("全功能", "完整复刻", "full_parity", "parity", "full parity")
INTERACTIVE_SIGNALS = ("brainstorm", "探讨", "对齐", "交互", "interactive")
AUTO_SOURCE_SIGNALS = ("github.com", "gitlab.com", "http://", "https://")


def slugify_program(utterance: str, explicit: str = "") -> str:
    if explicit.strip():
        return explicit.strip()
    tokens = re.findall(r"[a-z0-9]+", utterance.lower())
    base = "-".join(tokens[:6]) or "program"
    return base[:48]


def classify_plan_mode(
    utterance: str,
    *,
    mode_flag: str = "",
    source: str = "",
) -> dict[str, Any]:
    normalized = (mode_flag or "").strip().lower()
    if normalized in {"auto", "interactive", "auto-detect"}:
        if normalized != "auto-detect":
            return {"plan_mode": normalized, "confidence": 100, "reason": "cli_flag"}
    text = f"{utterance} {source}".lower()
    if any(sig in text for sig in INTERACTIVE_SIGNALS):
        return {"plan_mode": "interactive", "confidence": 85, "reason": "interactive_signals"}
    if source.strip() or any(sig in utterance for sig in FULL_PARITY_SIGNALS):
        return {"plan_mode": "auto", "confidence": 80, "reason": "source_or_full_parity"}
    if any(sig in text for sig in AUTO_SOURCE_SIGNALS):
        return {"plan_mode": "auto", "confidence": 75, "reason": "source_url"}
    return {"plan_mode": "auto-detect", "confidence": 40, "reason": "low_confidence_needs_one_question"}


def program_artifacts_root(project_root: Path, version: str, program_slug: str) -> Path:
    return project_root / "docs" / "beacon" / version / "programs" / program_slug


def program_run_state_path(project_root: Path, version: str, program_slug: str) -> Path:
    return program_artifacts_root(project_root, version, program_slug) / "program-run-state.json"


def write_program_run_state(
    project_root: Path,
    *,
    version: str,
    program_slug: str,
    plan_mode: str,
    lake_or_ocean: str = "海",
    program_phase: str = "P0",
    fsm_state: str = "program_intent_captured",
    p4_ack: bool = False,
    next_action: str = "",
) -> Path:
    path = program_run_state_path(project_root, version, program_slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "program_slug": program_slug,
        "version": version,
        "plan_mode": plan_mode,
        "program_phase": program_phase,
        "fsm_state": fsm_state,
        "lake_or_ocean": lake_or_ocean,
        "p4_ack": p4_ack,
        "next_action": next_action or f"program_phase:{program_phase}",
        "updated_at": now_iso(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_program_run_state(project_root: Path, version: str, program_slug: str) -> dict[str, Any] | None:
    path = program_run_state_path(project_root, version, program_slug)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def build_plan_start_payload(
    project_root: Path,
    *,
    version: str,
    utterance: str,
    program_slug: str = "",
    mode_flag: str = "",
    source: str = "",
) -> dict[str, Any]:
    slug = slugify_program(utterance, program_slug)
    classification = classify_plan_mode(utterance, mode_flag=mode_flag, source=source)
    plan_mode = classification["plan_mode"]
    delegate_skill = {
        "auto": "beacon-pln-program-auto",
        "interactive": "beacon-pln-program-interactive",
        "auto-detect": "beacon-pln-program",
    }.get(plan_mode, "beacon-pln-program")
    state_from = "program_intent_captured"
    state_to = "plan_mode_selected" if plan_mode != "auto-detect" else state_from
    transition_result = transition(state_from, "plan_mode_selected") if state_to == "plan_mode_selected" else None
    artifact_root = program_artifacts_root(project_root, version, slug)
    artifact_root.mkdir(parents=True, exist_ok=True)
    manifest_path = artifact_root / "program-manifest.md"
    if not manifest_path.exists():
        manifest_path.write_text(
            "\n".join(
                [
                    "---",
                    f"program_slug: {slug}",
                    f"version: {version}",
                    f"plan_mode: {plan_mode}",
                    f"plan_mode_reason: {classification['reason']}",
                    "scope_mode: full_parity",
                    "lake_or_ocean: 海",
                    "---",
                    "",
                    "# Program Manifest",
                    "",
                    f"User utterance: {utterance.strip()}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    existing_state = read_program_run_state(project_root, version, slug)
    program_phase = "P0"
    fsm_state = state_to
    if existing_state:
        program_phase = str(existing_state.get("program_phase") or "P0")
        fsm_state = str(existing_state.get("fsm_state") or state_to)
    state_path = write_program_run_state(
        project_root,
        version=version,
        program_slug=slug,
        plan_mode=plan_mode,
        lake_or_ocean=str(existing_state.get("lake_or_ocean") if existing_state else "海"),
        program_phase=program_phase,
        fsm_state=fsm_state,
        p4_ack=bool(existing_state.get("p4_ack")) if existing_state else False,
        next_action=str(existing_state.get("next_action") if existing_state else f"program_phase:{program_phase}"),
    )
    return {
        "schema_version": "1.0",
        "version": version,
        "program_slug": slug,
        "utterance": utterance,
        "plan_mode": plan_mode,
        "plan_mode_classification": classification,
        "delegate_skill": delegate_skill,
        "state": state_to,
        "program_phase": program_phase,
        "program_run_state_path": str(state_path.relative_to(project_root)),
        "fsm_states": list(PROGRAM_PLAN_STATES),
        "transition": transition_result.__dict__ if transition_result else None,
        "artifact_root": str(artifact_root.relative_to(project_root)),
        "generated_at": now_iso(),
    }


def emit_plan_start_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
