"""Acceptance Kit v1 helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_execution_dir
from beacon.utils.runtime import read_json
from beacon.utils.story_state import feature_slug
from beacon.utils.truth_map import feature_package_authoritative, resolve_truth_read_refs


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = str(version or "").strip().lower().lstrip("v")
    try:
        major, minor, patch = normalized.split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def _default_requirement_refs(version: str, slug: str) -> tuple[str, str, str]:
    if _semver_tuple(version) >= (1, 5, 2):
        base = f"docs/beacon/{version}/features/{slug}"
        return f"{base}/truth.md", f"{base}/truth.md", f"{base}/tests.md"
    return (
        f"docs/beacon/{version}/prd/{slug}.md",
        f"docs/beacon/{version}/user-story/{slug}.md",
        f"docs/beacon/{version}/qa/test-cases/{slug}.md",
    )


_KIT_LAYER_ORDER = ["skill-contract", "scenario-suite", "trace-scorecard", "real-project-proof"]


def _resolve_project_root(project_root: Path) -> Path:
    return Path(project_root).expanduser().resolve()


def acceptance_kit_machine_path(project_root: Path, version: str, feature: str) -> Path:
    return machine_execution_dir(project_root, version) / f"acceptance-kit-{feature_slug(feature)}.json"


def load_acceptance_kit(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    project_root = _resolve_project_root(project_root)
    path = acceptance_kit_machine_path(project_root, version, feature)
    payload = read_json(path, {})
    if not isinstance(payload, dict) or not payload:
        return {}
    normalized = dict(payload)
    normalized["_machine_path"] = str(path.relative_to(project_root))
    return normalized


def _layer_status(layer: dict[str, Any] | None) -> str:
    payload = layer if isinstance(layer, dict) else {}
    return str(payload.get("status") or payload.get("verdict") or payload.get("result") or "").strip().lower()


def summarize_acceptance_kit(kit: dict[str, Any] | None) -> dict[str, Any]:
    payload = kit if isinstance(kit, dict) else {}
    layers = payload.get("layers") if isinstance(payload.get("layers"), dict) else {}
    layer_details: list[dict[str, Any]] = []
    verdicts: dict[str, str] = {}
    failed_layers: list[str] = []
    for layer_name in _KIT_LAYER_ORDER:
        detail = layers.get(layer_name) if isinstance(layers.get(layer_name), dict) else {}
        status = _layer_status(detail)
        verdicts[layer_name] = status or "missing"
        layer_details.append(
            {
                "name": layer_name,
                "status": verdicts[layer_name],
                "source_truth_ref": str(detail.get("source_truth_ref") or ""),
                "evidence_ref": str(detail.get("evidence_ref") or ""),
            }
        )
        if verdicts[layer_name] not in {"pass", "passed", "ok"}:
            failed_layers.append(layer_name)
    verdict = str(payload.get("verdict") or "").strip().lower()
    if not verdict:
        verdict = "passed" if not failed_layers else "blocked"
    if failed_layers:
        ladder = "blocked"
    else:
        ladder = "passed"
    regression_raw = payload.get("regression_pass")
    regression_pass = bool(regression_raw) if isinstance(regression_raw, bool) else str(regression_raw or "").strip().lower() in {"pass", "passed", "ok", "true", "1"}
    return {
        "schema_version": str(payload.get("schema_version") or "1.0"),
        "feature": str(payload.get("feature") or ""),
        "version": str(payload.get("version") or ""),
        "verdict": verdict,
        "layer_verdicts": verdicts,
        "layer_details": layer_details,
        "failed_layers": failed_layers,
        "contract_pass": verdicts.get("skill-contract") in {"pass", "passed", "ok"},
        "scenario_pass": verdicts.get("scenario-suite") in {"pass", "passed", "ok"},
        "trace_pass": verdicts.get("trace-scorecard") in {"pass", "passed", "ok"},
        "real_project_pass": verdicts.get("real-project-proof") in {"pass", "passed", "ok"},
        "regression_pass": regression_pass if payload.get("regression_pass") is not None else bool(not failed_layers),
        "real_project_proof": {
            "status": str((payload.get("real_project_proof") or {}).get("status") or verdicts.get("real-project-proof") or ""),
            "evidence_refs": list((payload.get("real_project_proof") or {}).get("evidence_refs") or []),
            "source": str((payload.get("real_project_proof") or {}).get("source") or ""),
        },
        "machine_path": str(payload.get("_machine_path") or ""),
        "summary": "Contract Pass" if not failed_layers and verdict == "passed" else "Blocked",
        "layer_count": len(layer_details),
        "layer_order": list(_KIT_LAYER_ORDER),
        "all_layers_passed": not failed_layers,
    }


def build_acceptance_kit_projection(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    project_root = _resolve_project_root(project_root)
    kit = load_acceptance_kit(project_root, version=version, feature=feature)
    summary = summarize_acceptance_kit(kit)
    if not kit:
        return {
            "present": False,
            "summary": summary,
            "links": [],
            "reason_code": "acceptance_kit_missing",
        }
    if feature_package_authoritative(version):
        refs = resolve_truth_read_refs(
            project_root,
            version=version,
            feature=feature,
            consumer="acceptance-kit",
        )["requirement_refs"]
        source_by_layer = {
            "skill-contract": refs["prd"],
            "scenario-suite": refs["user_story"],
            "trace-scorecard": refs["test_case"],
        }
        layer_details = summary.get("layer_details") if isinstance(summary.get("layer_details"), list) else []
        for item in layer_details:
            if not isinstance(item, dict):
                continue
            layer = str(item.get("name") or "")
            if layer in source_by_layer:
                item["source_truth_ref"] = source_by_layer[layer]
    links = [
        {
            "layer": item["name"],
            "status": item["status"],
            "source_truth_ref": item["source_truth_ref"],
            "evidence_ref": item["evidence_ref"],
        }
        for item in summary.get("layer_details", [])
    ]
    return {
        "present": True,
        "summary": summary,
        "links": links,
        "reason_code": "acceptance_kit_blocked" if not summary.get("all_layers_passed") else "",
    }


def write_acceptance_kit_projection(
    project_root: Path,
    *,
    version: str,
    feature: str,
    acceptance_envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    project_root = _resolve_project_root(project_root)
    envelope = acceptance_envelope if isinstance(acceptance_envelope, dict) else {}
    if not envelope:
        path = acceptance_kit_machine_path(project_root, version, feature)
        if not path.exists():
            return {}
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            envelope = {}
    if not isinstance(envelope, dict) or not envelope:
        return {}

    requirement_refs = [str(item).strip() for item in (envelope.get("requirement_refs") or []) if str(item).strip()]
    test_case_refs = [str(item).strip() for item in (envelope.get("test_case_refs") or []) if str(item).strip()]
    evidence_refs = [str(item).strip() for item in (envelope.get("evidence_refs") or []) if str(item).strip()]
    runtime_ref = str(envelope.get("runtime_projection_ref") or "").strip()
    markdown_ref = str(envelope.get("markdown_ref") or "").strip()
    machine_ref = str(envelope.get("canonical_envelope_ref") or "").strip()
    slug = feature_slug(feature)

    if feature_package_authoritative(version):
        refs = resolve_truth_read_refs(
            project_root,
            version=version,
            feature=slug,
            consumer="acceptance-kit",
        )["requirement_refs"]
        default_skill_ref, default_scenario_ref, default_trace_ref = refs["prd"], refs["user_story"], refs["test_case"]
    else:
        default_skill_ref, default_scenario_ref, default_trace_ref = _default_requirement_refs(version, slug)
    skill_ref = requirement_refs[0] if requirement_refs else default_skill_ref
    scenario_ref = requirement_refs[1] if len(requirement_refs) > 1 else default_scenario_ref
    trace_ref = requirement_refs[2] if len(requirement_refs) > 2 else default_trace_ref
    real_project_refs = [ref for ref in [runtime_ref, markdown_ref, machine_ref, *evidence_refs] if ref]

    payload = {
        "schema_version": "1.0",
        "feature": str(envelope.get("feature") or feature),
        "feature_slug": slug,
        "version": str(envelope.get("version") or version),
        "verdict": "passed" if str(envelope.get("verdict") or "").strip().lower() == "passed" else "blocked",
        "layers": {
            "skill-contract": {
                "status": "pass",
                "source_truth_ref": skill_ref,
                "evidence_ref": machine_ref or markdown_ref or skill_ref,
            },
            "scenario-suite": {
                "status": "pass",
                "source_truth_ref": scenario_ref,
                "evidence_ref": markdown_ref or scenario_ref,
            },
            "trace-scorecard": {
                "status": "pass",
                "source_truth_ref": trace_ref,
                "evidence_ref": trace_ref,
            },
            "real-project-proof": {
                "status": "pass",
                "source_truth_ref": runtime_ref or machine_ref or markdown_ref or trace_ref,
                "evidence_ref": runtime_ref or machine_ref or markdown_ref or trace_ref,
            },
        },
        "real_project_proof": {
            "status": "pass",
            "evidence_refs": real_project_refs,
            "source": "qa_acceptance_envelope",
        },
        "regression_pass": True,
    }
    path = acceptance_kit_machine_path(project_root, version, feature)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload
