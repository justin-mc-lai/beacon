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
    return {
        "schema_version": "1.0",
        "version": version,
        "program_slug": slug,
        "utterance": utterance,
        "plan_mode": plan_mode,
        "plan_mode_classification": classification,
        "delegate_skill": delegate_skill,
        "state": state_to,
        "fsm_states": list(PROGRAM_PLAN_STATES),
        "transition": transition_result.__dict__ if transition_result else None,
        "artifact_root": str(artifact_root.relative_to(project_root)),
        "generated_at": now_iso(),
    }


def emit_plan_start_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
