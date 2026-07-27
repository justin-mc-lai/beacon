"""Program freeze gate — aggregate lake readiness and emit program-truth-freeze.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.program_graph import (
    capture_feature_graph_structure_baseline,
    feature_graph_path,
    load_feature_graph,
)
from beacon.utils.runtime import now_iso
from beacon.utils.plan_goal_task_closure import validate_authenticated_program_freeze


def _parity_matrix_has_pending_defer(project_root: Path, version: str, program_slug: str) -> bool:
    matrix_path = project_root / "docs" / "beacon" / version / "programs" / program_slug / "program-parity-matrix.md"
    if not matrix_path.exists():
        return False
    text = matrix_path.read_text(encoding="utf-8").lower()
    return "pending" in text and "user_decision" in text


def _lake_truth_promotion_complete(project_root: Path, version: str, program_slug: str, lake_slug: str) -> bool:
    promo = (
        project_root
        / "docs"
        / "beacon"
        / version
        / "programs"
        / program_slug
        / "lakes"
        / lake_slug
        / "truth-promotion.json"
    )
    if not promo.exists():
        return False
    try:
        payload = json.loads(promo.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return payload.get("status") == "complete"


def build_program_freeze_gate(
    project_root: Path,
    *,
    version: str,
    program_slug: str,
    lake_or_ocean: str = "海",
    feature_graph_ack: bool = True,
) -> dict[str, Any]:
    graph_path = feature_graph_path(project_root, version, program_slug)
    payload, errors = load_feature_graph(graph_path)
    findings: list[dict[str, str]] = []
    if errors:
        for err in errors:
            findings.append({"kind": "graph_validation", "code": err})
    if lake_or_ocean == "海" and not feature_graph_ack:
        findings.append({"kind": "sea_guard", "code": "feature_graph_ack_required"})
    if payload and _parity_matrix_has_pending_defer(project_root, version, program_slug):
        findings.append({"kind": "deferral", "code": "pending_deferral_in_parity_matrix"})
    lake_rows: list[dict[str, Any]] = []
    if payload:
        for lake in payload.get("lakes") or []:
            if not isinstance(lake, dict):
                continue
            slug = str(lake.get("slug") or "")
            lake_rows.append(
                {
                    "slug": slug,
                    "status": lake.get("status"),
                    "truth_promotion_complete": _lake_truth_promotion_complete(project_root, version, program_slug, slug),
                }
            )
            if lake.get("status") != "frozen":
                findings.append({"kind": "lake", "code": f"lake_not_frozen:{slug}"})
            if not _lake_truth_promotion_complete(project_root, version, program_slug, slug):
                findings.append({"kind": "lake", "code": f"truth_promotion_missing:{slug}"})
    blocked = bool(findings)
    return {
        "schema_version": "1.0",
        "program_slug": program_slug,
        "version": version,
        "status": "blocked" if blocked else "frozen",
        "blocked": blocked,
        "findings": findings,
        "lakes": lake_rows,
        "generated_at": now_iso(),
        "artifact_name": "program-truth-freeze.json",
    }


def write_program_freeze_gate(project_root: Path, gate: dict[str, Any]) -> Path:
    program_slug = str(gate.get("program_slug") or "")
    version = str(gate.get("version") or "")
    out_dir = project_root / "docs" / "beacon" / version / "programs" / program_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "program-truth-freeze.json"
    out_path.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not gate.get("blocked"):
        graph_payload, graph_errors = load_feature_graph(
            feature_graph_path(project_root, version, program_slug)
        )
        if graph_payload and not graph_errors:
            capture_feature_graph_structure_baseline(
                project_root,
                version=version,
                program_slug=program_slug,
                graph_payload=graph_payload,
            )
    return out_path


def validate_program_freeze_authenticated(
    project_root: Path,
    *,
    version: str,
    program_slug: str,
    lake_receipts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Strong Program freeze gate: status-only promotion is insufficient."""
    base = build_program_freeze_gate(project_root, version=version, program_slug=program_slug)
    receipts = list(lake_receipts or [])
    if not receipts:
        # load lake promotion files when present
        lakes_dir = project_root / "docs" / "beacon" / version / "programs" / program_slug / "lakes"
        if lakes_dir.exists():
            for lake_dir in sorted(p for p in lakes_dir.iterdir() if p.is_dir()):
                promo = lake_dir / "truth-promotion.json"
                if promo.exists():
                    try:
                        receipts.append(json.loads(promo.read_text(encoding="utf-8")))
                    except json.JSONDecodeError:
                        receipts.append({"status": "complete", "feature": lake_dir.name})
    auth = validate_authenticated_program_freeze(
        project_root,
        version=version,
        program_slug=program_slug,
        lake_receipts=receipts,
    )
    findings = list(base.get("findings") or [])
    if auth.get("blocked"):
        findings.append({"kind": "authenticated_freeze", "code": str(auth.get("reason_code") or "authenticated_program_freeze_failed")})
        for item in auth.get("findings") or []:
            findings.append({"kind": "authenticated_freeze", "code": str(item.get("code") or item)})
    blocked = bool(findings) or bool(auth.get("blocked"))
    return {
        **base,
        "status": "blocked" if blocked else "frozen",
        "blocked": blocked,
        "findings": findings,
        "authenticated": auth,
        "gate_mode": "authenticated_pac_receipts",
    }
