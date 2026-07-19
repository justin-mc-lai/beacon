"""Program/lake implementation admission checks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_frontmatter(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return {}
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    out: dict[str, str] = {}
    for raw in parts[1].splitlines():
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        normalized_key = key.strip().lower().replace("-", "_").replace(" ", "_")
        out[normalized_key] = value.strip().strip("`").strip('"').strip("'")
    return out


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _lake_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("lakes") if isinstance(payload.get("lakes"), list) else []
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = feature_slug(str(row.get("slug") or row.get("feature_slug") or ""))
        feature = feature_slug(str(row.get("feature_slug") or row.get("slug") or ""))
        if not slug and not feature:
            continue
        out.append(
            {
                **row,
                "slug": slug or feature,
                "feature_slug": feature or slug,
                "depends_on": [
                    feature_slug(str(item))
                    for item in row.get("depends_on", [])
                    if str(item).strip()
                ]
                if isinstance(row.get("depends_on"), list)
                else [],
            }
        )
    return out


def _is_program_frozen(
    *,
    manifest: dict[str, str],
    graph: dict[str, Any],
    freeze: dict[str, Any],
) -> bool:
    return (
        str(freeze.get("status") or "").strip().lower() == "frozen"
        or str(manifest.get("program_plan_frozen") or "").strip().lower() == "true"
        or str(manifest.get("lake_package_truth_frozen") or "").strip().lower() == "true"
        or str(graph.get("program_plan_frozen") or "").strip().lower() == "true"
    )


def _next_action_target(next_action: str) -> str:
    text = str(next_action or "").strip()
    if not text:
        return ""
    if ":" in text:
        text = text.rsplit(":", 1)[-1].strip()
    if " " in text:
        text = text.split()[-1].strip().strip('"').strip("'")
    return feature_slug(text)


def resolve_program_lake_topology(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    """Resolve the frozen program/lake topology that owns a feature, if any."""
    root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(root, version)
    slug = feature_slug(feature)
    programs_root = root / "docs" / "beacon" / resolved_version / "programs"
    if not programs_root.is_dir():
        return {
            "status": "not_applicable",
            "blocked": False,
            "reason_code": "",
            "feature_slug": slug,
            "version": resolved_version,
        }

    for program_dir in sorted(path for path in programs_root.iterdir() if path.is_dir()):
        manifest_path = program_dir / "program-manifest.md"
        graph_path = program_dir / "feature-graph.json"
        freeze_path = program_dir / "program-truth-freeze.json"
        run_state_path = program_dir / "program-run-state.json"

        manifest = _read_frontmatter(manifest_path)
        graph = _read_json(graph_path)
        freeze = _read_json(freeze_path)
        run_state = _read_json(run_state_path)
        graph_lakes = _lake_rows(graph)
        freeze_lakes = _lake_rows(freeze)
        lake_by_slug: dict[str, dict[str, Any]] = {}
        for row in [*graph_lakes, *freeze_lakes]:
            row_slug = feature_slug(str(row.get("slug") or row.get("feature_slug") or ""))
            row_feature = feature_slug(str(row.get("feature_slug") or row.get("slug") or ""))
            existing = lake_by_slug.get(row_slug or row_feature, {})
            merged = {**existing, **row}
            if existing.get("depends_on") and not row.get("depends_on"):
                merged["depends_on"] = existing.get("depends_on")
            if row_slug:
                lake_by_slug[row_slug] = merged
            if row_feature:
                lake_by_slug[row_feature] = merged

        lake = lake_by_slug.get(slug)
        if not isinstance(lake, dict):
            continue
        if not _is_program_frozen(manifest=manifest, graph=graph, freeze=freeze):
            continue
        material_path = freeze_path if freeze_path.exists() else graph_path
        next_action = str(run_state.get("next_action") or "").strip()
        return {
            "status": "resolved",
            "blocked": False,
            "reason_code": "",
            "feature_slug": slug,
            "version": resolved_version,
            "program_slug": str(
                run_state.get("program_slug")
                or graph.get("program_slug")
                or freeze.get("program_slug")
                or program_dir.name
            ).strip(),
            "lake_slug": str(lake.get("slug") or slug),
            "lake_feature_slug": str(lake.get("feature_slug") or slug),
            "depends_on": [
                feature_slug(str(item))
                for item in lake.get("depends_on", [])
                if str(item).strip()
            ],
            "material_path": _rel(material_path, root) if material_path.exists() else "",
            "program_run_state_path": _rel(run_state_path, root) if run_state_path.exists() else "",
            "program_manifest_path": _rel(manifest_path, root) if manifest_path.exists() else "",
            "feature_graph_path": _rel(graph_path, root) if graph_path.exists() else "",
            "program_truth_freeze_path": _rel(freeze_path, root) if freeze_path.exists() else "",
            "next_action": next_action,
            "next_action_target": _next_action_target(next_action),
            "next_action_source": _rel(run_state_path, root) if run_state_path.exists() else "",
        }
    return {
        "status": "not_applicable",
        "blocked": False,
        "reason_code": "",
        "feature_slug": slug,
        "version": resolved_version,
    }


def _status_passed(payload: dict[str, Any]) -> bool:
    status = str(payload.get("status") or payload.get("verdict") or "").strip().lower()
    return status in {"pass", "passed", "ok", "completed", "accepted"}


def _implementation_closed(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    slug = feature_slug(feature)
    candidates = [
        root / ".beacon" / "state" / f"implementation-{slug}.json",
        root / "docs" / "beacon" / version / ".machine" / "execution" / f"implementation-summary-{slug}.json",
    ]
    for path in candidates:
        payload = _read_json(path)
        if payload and _status_passed(payload):
            return {"closed": True, "path": _rel(path, root), "status": str(payload.get("status") or "")}
    return {"closed": False, "path": "", "status": "missing"}


def _qa_closed(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    slug = feature_slug(feature)
    candidates = [
        root / ".beacon" / "qa" / "features" / slug / "status.json",
        root / "docs" / "beacon" / version / ".machine" / "execution" / f"qa-acceptance-{slug}.json",
        root / ".beacon" / "transactions" / f"qa-acceptance-{slug}.json",
    ]
    for path in candidates:
        payload = _read_json(path)
        if not payload:
            continue
        status_passed = _status_passed(payload)
        evidence_done = payload.get("evidence_done")
        release_ready = payload.get("release_ready")
        if status_passed and (
            evidence_done is True
            or release_ready is True
            or str(payload.get("verdict") or "").strip().lower() == "passed"
        ):
            return {"closed": True, "path": _rel(path, root), "status": str(payload.get("status") or payload.get("verdict") or "")}
    return {"closed": False, "path": "", "status": "missing"}


def evaluate_program_next_action_admission(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    """Evaluate program/lake next_action and dependency closure before implementation writes."""
    root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(root, version)
    topology = resolve_program_lake_topology(root, version=resolved_version, feature=feature)
    if topology.get("status") != "resolved":
        return {
            **topology,
            "schema_version": "1.0",
            "status": "pass",
            "blocked": False,
            "program_admission_required": False,
            "reason_code": "",
            "reason_codes": [],
        }

    lake_slug = feature_slug(str(topology.get("lake_slug") or feature))
    next_action_target = feature_slug(str(topology.get("next_action_target") or ""))
    if next_action_target and next_action_target != lake_slug:
        return {
            **topology,
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "program_admission_required": True,
            "reason_code": "program_next_action_mismatch",
            "reason_codes": ["program_next_action_mismatch"],
            "expected_lake_slug": next_action_target,
            "target_lake_slug": lake_slug,
            "recommended_command": f'beacon implement run "{next_action_target}" --project {root} --version {resolved_version}',
        }

    dependency_results: list[dict[str, Any]] = []
    for dependency in topology.get("depends_on", []):
        dep_slug = feature_slug(str(dependency))
        if not dep_slug:
            continue
        implementation = _implementation_closed(root, version=resolved_version, feature=dep_slug)
        qa = _qa_closed(root, version=resolved_version, feature=dep_slug)
        dependency_results.append(
            {
                "feature_slug": dep_slug,
                "implementation_closed": bool(implementation.get("closed")),
                "implementation_ref": str(implementation.get("path") or ""),
                "qa_closed": bool(qa.get("closed")),
                "qa_ref": str(qa.get("path") or ""),
            }
        )
    unclosed = [
        row
        for row in dependency_results
        if not bool(row.get("implementation_closed")) or not bool(row.get("qa_closed"))
    ]
    if unclosed:
        first = str(unclosed[0].get("feature_slug") or "")
        return {
            **topology,
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "program_admission_required": True,
            "reason_code": "program_dependency_unclosed",
            "reason_codes": ["program_dependency_unclosed"],
            "target_lake_slug": lake_slug,
            "dependencies": dependency_results,
            "unclosed_dependencies": unclosed,
            "recommended_command": f'beacon implement run "{first}" --project {root} --version {resolved_version}' if first else "",
        }

    # v1.6.8 fsm-implement-order: entity precedence hard gate when domain_required
    try:
        from beacon.utils.fsm_implement_order import evaluate_fsm_implement_order

        fsm_order = evaluate_fsm_implement_order(root, version=resolved_version, feature=lake_slug)
    except Exception as exc:  # noqa: BLE001
        fsm_order = {
            "status": "pass",
            "blocked": False,
            "reason_code": "",
            "error": str(exc),
        }
    if bool(fsm_order.get("blocked")):
        return {
            **topology,
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "program_admission_required": True,
            "reason_code": str(fsm_order.get("reason_code") or "fsm_implement_order_violation"),
            "reason_codes": list(fsm_order.get("reason_codes") or [fsm_order.get("reason_code")]),
            "target_lake_slug": lake_slug,
            "dependencies": dependency_results,
            "fsm_implement_order": fsm_order,
            "recommended_command": str(fsm_order.get("recommended_command") or ""),
        }

    return {
        **topology,
        "schema_version": "1.0",
        "status": "pass",
        "blocked": False,
        "program_admission_required": True,
        "reason_code": "",
        "reason_codes": [],
        "target_lake_slug": lake_slug,
        "dependencies": dependency_results,
        "fsm_implement_order": fsm_order,
    }
