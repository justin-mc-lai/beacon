from __future__ import annotations

import json
from pathlib import Path

from beacon.commands.gate import GateMode, check_prototype_contract
from beacon.utils.prototype_support import source_fingerprints


def _write_design_governed_requirements(root: Path, version: str, feature: str) -> None:
    slug = feature.lower().replace(" ", "-")
    us = root / "docs" / "beacon" / version / "user-story"
    prd = root / "docs" / "beacon" / version / "prd"
    us.mkdir(parents=True, exist_ok=True)
    prd.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            "ui_visualization_required: true",
            "prototype_mode: reference-pack-v2",
            "design_governance_required: true",
        ]
    )
    (us / f"{slug}.md").write_text(body, encoding="utf-8")
    (prd / f"{slug}.md").write_text(body, encoding="utf-8")


def test_gate_should_require_design_governance_artifacts_when_enabled(tmp_path: Path):
    feature = "Feature Proto"
    version = "v1.1.12"
    _write_design_governed_requirements(tmp_path, version, feature)
    proto = tmp_path / "docs" / "beacon" / version / "prototype" / feature.lower().replace(" ", "-")
    proto.mkdir(parents=True, exist_ok=True)
    (proto / "theme.json").write_text('{"primary":"#2563eb"}', encoding="utf-8")
    (proto / "navigation-map.json").write_text('{"navigation_nodes":[],"jump_map":[]}', encoding="utf-8")
    (proto / "interaction-map.json").write_text('{"ctas":[],"states":[]}', encoding="utf-8")
    (proto / "prototype-plan.json").write_text(
        json.dumps({"prototype_mode": "reference-pack-v2", "contract": {"design_governance_required": True}}, ensure_ascii=False),
        encoding="utf-8",
    )
    (proto / "coverage-report.json").write_text(json.dumps({"required_pages": [], "required_states": []}), encoding="utf-8")
    (proto / "prototype-review.json").write_text('{"overall_status":"pass","checks":[]}', encoding="utf-8")
    (proto / "prototype-review.md").write_text("# Review\n", encoding="utf-8")
    (proto / "index.html").write_text("<html aria-label='x'></html>", encoding="utf-8")
    (proto / "manifest.json").write_text(
        json.dumps(
            {
                "ui_kit": "bootstrap-5.3.x",
                "review_status": "pass",
                "prototype_mode": "reference-pack-v2",
                "design_governance_required": True,
            }
        ),
        encoding="utf-8",
    )
    (proto / "source-map.json").write_text("{}", encoding="utf-8")
    fps = source_fingerprints(tmp_path, version, feature)
    (proto / "freeze.json").write_text(
        json.dumps({"status": "frozen", "source_fingerprints": fps, "review_status": "pass"}),
        encoding="utf-8",
    )

    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "prototype", version=version)
    reason_codes = {item.get("reason_code") for item in issues}
    assert "prototype_design_brief_missing" in reason_codes
    assert "prototype_design_system_contract_missing" in reason_codes
    assert "prototype_design_prompt_missing" in reason_codes
    assert "prototype_web_guideline_review_missing" in reason_codes


def test_gate_should_block_when_design_review_outcome_is_blocked(tmp_path: Path):
    feature = "Feature Proto"
    version = "v1.1.12"
    _write_design_governed_requirements(tmp_path, version, feature)
    proto = tmp_path / "docs" / "beacon" / version / "prototype" / feature.lower().replace(" ", "-")
    proto.mkdir(parents=True, exist_ok=True)
    for name, content in {
        "theme.json": '{"primary":"#2563eb"}',
        "navigation-map.json": '{"navigation_nodes":[],"jump_map":[]}',
        "interaction-map.json": '{"ctas":[],"states":[]}',
        "prototype-review.json": '{"overall_status":"pass","checks":[]}',
        "prototype-review.md": "# Review\n",
        "index.html": "<html aria-label='x'></html>",
        "source-map.json": "{}",
        "design-brief.json": '{"tone":"disciplined"}',
        "design-system-contract.json": '{"design_governance_required":true}',
        "design-prompt.json": '{"design_generation_mode":"description-as-design"}',
        "design-prompt.md": "# Design Prompt\n",
        "web-guideline-review.json": '{"design_review_outcome":"blocked","severity_counts":{"critical":1}}',
        "web-guideline-review.md": "# Web Guideline Review\n",
    }.items():
        (proto / name).write_text(content, encoding="utf-8")
    (proto / "prototype-plan.json").write_text(
        json.dumps(
            {
                "prototype_mode": "reference-pack-v2",
                "required_pages": [],
                "required_states": [],
                "contract": {"design_governance_required": True},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (proto / "coverage-report.json").write_text(json.dumps({"required_pages": [], "required_states": []}), encoding="utf-8")
    (proto / "manifest.json").write_text(
        json.dumps(
            {
                "ui_kit": "bootstrap-5.3.x",
                "review_status": "pass",
                "prototype_mode": "reference-pack-v2",
                "design_governance_required": True,
                "design_review_outcome": "blocked",
                "artifacts": {
                    "design_brief": f"docs/beacon/{version}/prototype/feature-proto/design-brief.json",
                        "design_system_contract": f"docs/beacon/{version}/prototype/feature-proto/design-system-contract.json",
                        "design_prompt_json": f"docs/beacon/{version}/prototype/feature-proto/design-prompt.json",
                        "design_prompt_md": f"docs/beacon/{version}/prototype/feature-proto/design-prompt.md",
                        "web_guideline_review_json": f"docs/beacon/{version}/prototype/feature-proto/web-guideline-review.json",
                    "web_guideline_review_md": f"docs/beacon/{version}/prototype/feature-proto/web-guideline-review.md",
                },
            }
        ),
        encoding="utf-8",
    )
    fps = source_fingerprints(tmp_path, version, feature)
    (proto / "freeze.json").write_text(
        json.dumps({"status": "frozen", "source_fingerprints": fps, "review_status": "pass"}),
        encoding="utf-8",
    )

    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "prototype", version=version)
    reason_codes = {item.get("reason_code") for item in issues}
    assert "prototype_design_review_failed" in reason_codes
