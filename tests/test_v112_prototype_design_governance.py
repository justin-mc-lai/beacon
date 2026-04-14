from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_design_governed_sources(
    tmp_path: Path,
    feature: str,
    version: str = "v1.1.12",
    extra_lines: list[str] | None = None,
) -> None:
    slug = feature.lower().replace(" ", "-")
    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            f"# User Story: {feature}",
            "",
            "**As a** product design owner，",
            "**I want** a governed reference pack，",
            "**So that** design and implementation stay aligned.",
            "",
            "prototype_mode: reference-pack-v2",
            "design_governance_required: true",
            "design_generation_mode: description-as-design",
            "interactive_prototype_required: true",
            "design_reference_sources: GemDesign-style requirement-to-design generation；Figma-style interactive fidelity and freeze discipline",
            "ui_visualization_required: true",
            "coverage_mode: all-existing-routes",
            "prototype_archetype: admin-workbench",
            "target_user: 设计协作者",
            "theme_mood: disciplined",
            "theme_primary: #2563eb",
            "theme_secondary: #0f172a",
            "brand_keywords: editorial, precise, layered",
            "surface_style: elevated-clean",
            "sections: Overview；Page Inventory；Delivery Readiness",
            "navigation: Overview；Page Inventory；Delivery Readiness",
            "primary_entry: Overview",
            "primary_exit: Delivery Readiness",
            "primary_cta: Generate Reference Pack",
            "secondary_cta: Review Design",
            "jump_map: Overview->Page Inventory：review inventory；Page Inventory->Delivery Readiness：final check",
            "states: empty；loading；error；completed",
            "required_states:",
            "  - empty",
            "  - loading",
            "  - error",
            "  - completed",
            *(extra_lines or []),
        ]
    )
    (us_dir / f"{slug}.md").write_text(body, encoding="utf-8")
    (prd_dir / f"{slug}.md").write_text(body, encoding="utf-8")


def test_design_governance_plan_and_review_emit_artifacts(tmp_path: Path):
    feature = "Design Governed Prototype"
    version = "v1.1.12"
    _prepare_design_governed_sources(tmp_path, feature, version)

    plan = _invoke(["prototype", "plan", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert plan.exit_code == 0, plan.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / "design-governed-prototype"
    design_brief = json.loads((root / "design-brief.json").read_text(encoding="utf-8"))
    design_system = json.loads((root / "design-system-contract.json").read_text(encoding="utf-8"))
    design_prompt = json.loads((root / "design-prompt.json").read_text(encoding="utf-8"))
    assert design_brief["tone"] == "disciplined"
    assert design_brief["design_generation_mode"] == "description-as-design"
    assert design_brief["interactive_prototype_required"] is True
    assert "frontend-design" in design_brief["guidance_anchors"]
    assert "web-design-guidelines" in design_brief["guidance_anchors"]
    assert any("GemDesign-style" in item for item in design_brief["design_mode_references"])
    assert design_system["design_governance_required"] is True
    assert design_system["design_generation_mode"] == "description-as-design"
    assert design_system["interactive_prototype_required"] is True
    assert design_system["typography"]["body"] != "Inter"
    assert design_prompt["design_generation_mode"] == "description-as-design"
    assert design_prompt["interactive_prototype_required"] is True
    assert "frontend-design" in design_prompt["guidance_anchors"]
    assert "web-design-guidelines" in design_prompt["guidance_anchors"]
    assert any("Figma-style" in item for item in design_prompt["design_mode_references"])
    assert "Design a high-fidelity interactive prototype" in design_prompt["llm_design_prompt"]
    assert (root / "design-prompt.md").exists()

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    payload = json.loads(review.stdout)
    assert payload["overall_status"] == "pass"
    assert payload["design_review_outcome"] in {"pass", "revise"}
    assert payload["iteration_writeback_path"]

    guideline_review = json.loads((root / "web-guideline-review.json").read_text(encoding="utf-8"))
    assert guideline_review["design_governance_required"] is True
    assert (root / "web-guideline-review.md").exists()
    rewrite_input = tmp_path / payload["iteration_writeback_path"]
    assert rewrite_input.exists()
    rewrite_payload = json.loads(rewrite_input.read_text(encoding="utf-8"))
    assert rewrite_payload["source_type"] == "prototype_design_review"
    assert "design_brief" in rewrite_payload["rewrite_targets"]
    assert "guideline_fix" in rewrite_payload["rewrite_targets"]
    engine = json.loads((tmp_path / ".beacon" / "state" / "evo" / "decision-engine.json").read_text(encoding="utf-8"))
    assert engine["decision_summary"]
    check_names = {item["name"] for item in payload["checks"] if item["status"] == "pass"}
    assert "design_brief_present" in check_names
    assert "design_system_contract_present" in check_names
    assert "design_prompt_present" in check_names
    assert "web_guideline_review_generated" in check_names


def test_design_governance_directory_command_and_style_analysis_artifacts(tmp_path: Path):
    feature = "Design Governed Prototype"
    version = "v1.1.12"
    _prepare_design_governed_sources(tmp_path, feature, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / "design-governed-prototype"
    style_analysis = json.loads((root / "ui-style-analysis.json").read_text(encoding="utf-8"))
    assert style_analysis["directory_contract"]["directory_page"] == "index.html"
    assert "ui-style-analysis.json" in style_analysis["secondary_build_contract"]["required_artifacts"]
    assert (root / "ui-style-analysis.md").exists()

    directory = _invoke(["prototype", "directory", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert directory.exit_code == 0, directory.stdout
    payload = json.loads(directory.stdout)
    assert payload["directory_page"].endswith("docs/beacon/v1.1.12/prototype/design-governed-prototype/index.html")
    assert payload["style_analysis_path"].endswith("ui-style-analysis.json")
    assert "overview" in payload["generated_pages"]


def test_review_design_should_emit_cso_inspired_security_findings(tmp_path: Path):
    feature = "Secure Upload Prototype"
    version = "v1.1.12"
    _prepare_design_governed_sources(
        tmp_path,
        feature,
        version,
        extra_lines=[
            "primary_cta: Upload asset",
            "secondary_cta: Review upload",
            "sections: Upload Queue；Delivery Readiness",
        ],
    )

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version])
    assert create.exit_code == 0, create.stdout

    review = _invoke(["review", "design", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    payload = json.loads(review.stdout)
    assert payload["review_type"] == "design"
    assert payload["security_design_review"]["mode"] == "cso-inspired-design-review"
    reason_codes = {item["reason_code"] for item in payload["security_design_review"]["findings"]}
    assert "upload_constraints_missing" in reason_codes
    assert payload["artifacts"]["json"].endswith("review-design-secure-upload-prototype.json")
    assert payload["status"] == "fail"


def test_design_governance_review_should_fail_on_critical_guideline_gap(tmp_path: Path):
    feature = "Design Governed Prototype"
    version = "v1.1.12"
    _prepare_design_governed_sources(tmp_path, feature, version)

    assert _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    root = tmp_path / "docs" / "beacon" / version / "prototype" / "design-governed-prototype"
    html_path = root / "index.html"
    html = html_path.read_text(encoding="utf-8").replace("Skip to main content", "Missing skip link")
    html_path.write_text(html, encoding="utf-8")

    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    payload = json.loads(review.stdout)
    assert payload["overall_status"] == "fail"
    failed = {item["name"] for item in payload["checks"] if item["status"] == "fail"}
    assert "web_guideline_critical_findings_clear" in failed
    rewrite_input = tmp_path / payload["iteration_writeback_path"]
    rewrite_payload = json.loads(rewrite_input.read_text(encoding="utf-8"))
    assert rewrite_payload["design_review_outcome"] == "blocked"
    assert rewrite_payload["rewrite_targets"]["guideline_fix"]
