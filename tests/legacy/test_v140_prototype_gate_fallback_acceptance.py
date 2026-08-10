from __future__ import annotations

import importlib
import json
from pathlib import Path

from beacon.commands.gate import GateMode, check_prototype_contract


VERSION = "v1.4.0"
FEATURE_DIR = "beacon-v1-4-0-demo-prototype"
gate_module = importlib.import_module("beacon.commands.gate")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_v140_release_gate_allows_accepted_prototype_auto_fallback(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "docs" / "beacon" / VERSION / "prototype" / FEATURE_DIR
    pages_dir = root / "pages"
    page_specs_dir = root / "page-specs"
    pages_dir.mkdir(parents=True, exist_ok=True)
    page_specs_dir.mkdir(parents=True, exist_ok=True)
    (pages_dir / "intent-router.md").write_text("# intent-router\n", encoding="utf-8")
    _write_json(page_specs_dir / "intent-router.json", {"page_id": "intent-router", "states": ["ready"]})

    plan_path = root / "prototype-plan.json"
    coverage_path = root / "coverage-report.json"
    review_json_path = root / "prototype-review.json"
    manifest_path = root / "manifest.json"

    _write_json(
        plan_path,
        {
            "prototype_mode": "wireframe",
            "required_pages": ["intent-router"],
            "required_states": ["ready"],
            "page_specs": [{"page_id": "intent-router", "states": ["ready"]}],
            "compiler": {
                "requested_mode": "auto",
                "fallback_reason": "host_compile_failed",
                "generator_mode": "rule",
            },
        },
    )
    _write_json(coverage_path, {"compact_mode_detected": False})
    _write_json(review_json_path, {"overall_status": "pass", "checks": []})
    _write_json(manifest_path, {"prototype_mode": "wireframe"})

    required_text_files = {
        "wireframe_summary": root / "wireframe-summary.md",
        "navigation_map_md": root / "navigation-map.md",
        "state_flow_map_md": root / "state-flow-map.md",
        "component_catalog_md": root / "component-catalog.md",
        "review_md": root / "prototype-review.md",
        "ux_prd": root / "ux-prd.md",
        "design_md": root / "DESIGN.md",
        "preview_html": root / "preview.html",
        "preview_dark_html": root / "preview-dark.html",
    }
    for path in required_text_files.values():
        path.write_text("ok\n", encoding="utf-8")

    required_json_files = {
        "wireframe_manifest": root / "wireframe-manifest.json",
        "theme": root / "theme.json",
        "navigation_map": root / "navigation-map.json",
        "state_flow_map": root / "state-flow-map.json",
        "component_catalog": root / "component-catalog.json",
        "canonical_envelope": root / "canonical-envelope.json",
        "interaction_map": root / "interaction-map.json",
    }
    for path in required_json_files.values():
        _write_json(path, {})

    files = {
        "prototype_plan": str(plan_path),
        "coverage_report": str(coverage_path),
        "manifest": str(manifest_path),
        "review_json": str(review_json_path),
        "review_md": str(required_text_files["review_md"]),
        "pages_dir": str(pages_dir),
        "page_specs_dir": str(page_specs_dir),
        "wireframe_summary": str(required_text_files["wireframe_summary"]),
        "wireframe_manifest": str(required_json_files["wireframe_manifest"]),
        "theme": str(required_json_files["theme"]),
        "navigation_map": str(required_json_files["navigation_map"]),
        "navigation_map_md": str(required_text_files["navigation_map_md"]),
        "state_flow_map": str(required_json_files["state_flow_map"]),
        "state_flow_map_md": str(required_text_files["state_flow_map_md"]),
        "component_catalog": str(required_json_files["component_catalog"]),
        "component_catalog_md": str(required_text_files["component_catalog_md"]),
        "canonical_envelope": str(required_json_files["canonical_envelope"]),
        "interaction_map": str(required_json_files["interaction_map"]),
        "ux_prd": str(required_text_files["ux_prd"]),
        "design_md": str(required_text_files["design_md"]),
        "preview_html": str(required_text_files["preview_html"]),
        "preview_dark_html": str(required_text_files["preview_dark_html"]),
    }

    payload = {
        "status": "frozen",
        "review_status": "pass",
        "recorded_source_fingerprints": {"prd": "sha256:demo"},
        "drift_status": "consistent",
        "sqlite_projection_status": "pass",
        "compiler_fallback_accepted": True,
        "files": files,
    }

    monkeypatch.setattr(gate_module, "prototype_status", lambda *_args, **_kwargs: payload)
    monkeypatch.setattr(gate_module, "feature_requires_route_closure", lambda *_args, **_kwargs: False)

    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version=VERSION)
    reason_codes = {item["reason_code"] for item in issues}
    assert "prototype_auto_template_downgrade_blocked" not in reason_codes
