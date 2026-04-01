"""Doctor/help navigation bridge helpers.

This module intentionally wraps the canonical help payload builder used by the
`beacon help` command so that `doctor advise` and `help` stay aligned.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.doctor_diagnostics import build_doctor_payload
from beacon.utils.help_support import build_help_payload as _build_help_payload


def build_help_payload(project_root: Path, *, version: str | None = None, feature: str | None = None, run_id: str | None = None) -> dict[str, Any]:
    return _build_help_payload(project_root, version=version or "auto", feature=feature or "", run_id=run_id)



def build_doctor_advise_payload(project_root: Path, *, version: str | None = None, feature: str | None = None, run_id: str | None = None, strict: bool = False) -> dict[str, Any]:
    help_payload = build_help_payload(project_root, version=version, feature=feature, run_id=run_id)
    doctor_payload = build_doctor_payload(project_root, strict=strict, version=version or "auto")
    incompatibilities = doctor_payload.get("incompatibilities", []) if isinstance(doctor_payload.get("incompatibilities"), list) else []
    repair_plan = doctor_payload.get("repair_plan", []) if isinstance(doctor_payload.get("repair_plan"), list) else []
    diagnosis = []
    for item in incompatibilities[:5]:
        if not isinstance(item, dict):
            continue
        diagnosis.append(
            {
                "code": str(item.get("code", "")),
                "severity": str(item.get("severity", "medium")),
                "summary": str(item.get("summary", "")),
                "repair": list(item.get("repair", [])),
            }
        )

    next_step = dict(help_payload.get("next_step", {}))
    if diagnosis:
        top = diagnosis[0]
        code = str(top.get("code", ""))
        if code in {"COMP-207", "COMP-208", "COMP-209"}:
            next_step = {
                "action": "repair-context",
                "reason": str(top.get("summary", "context files need repair")),
                "command": f'beacon doctor setup-context --project-root "{project_root}"',
            }
        else:
            next_step = {
                "action": "repair-package",
                "reason": str(top.get("summary", "delivery package needs repair")),
                "command": f'beacon doctor repair-package --project-root "{project_root}" --version "{help_payload.get("version", version or "auto")}"',
            }

    status = str(doctor_payload.get("overall", "WARN")).upper()
    if help_payload.get("blocked") and status == "PASS":
        status = "WARN"

    return {
        "schema_version": "1.0",
        "action": "advise",
        "status": status,
        "feature": help_payload.get("feature", ""),
        "docs_version": help_payload.get("docs_version", help_payload.get("version", "")),
        "runtime_version": help_payload.get("runtime_version", ""),
        "context_managed_version": (
            help_payload.get("version_context", {}).get("context_managed_version", "")
            if isinstance(help_payload.get("version_context"), dict)
            else ""
        ),
        "version": help_payload.get("version", ""),
        "run_id": help_payload.get("run_id", ""),
        "revision_id": help_payload.get("revision_id", ""),
        "current_stage": help_payload.get("current_stage", ""),
        "doc_status": help_payload.get("doc_status", ""),
        "delivery_status": help_payload.get("delivery_status", ""),
        "blocked": bool(help_payload.get("blocked")) or bool(diagnosis),
        "blocking_reasons": list(help_payload.get("blocking_reasons", [])),
        "scores": dict(help_payload.get("scores", {})),
        "next_step": next_step,
        "doctor_overall": doctor_payload.get("overall", "WARN"),
        "doctor_checks": doctor_payload.get("checks", []),
        "diagnosis": diagnosis,
        "repair_plan": repair_plan,
    }
