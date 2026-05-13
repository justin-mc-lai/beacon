from __future__ import annotations

from beacon.utils.prototype_utils import (
    build_anti_ai_ui_contract,
    build_design_template_catalog,
    normalize_design_preset_choice,
)


def test_v144_design_template_catalog_should_freeze_three_templates() -> None:
    catalog = build_design_template_catalog("v1.4.4")

    assert catalog["catalog_mode"] == "fixed-three-templates"
    assert catalog["template_count"] == 3
    assert set(catalog["templates"]) == {"restrained-product", "operator-console", "editorial-calm"}
    assert catalog["templates"]["restrained-product"]["source"] == "apple"
    assert catalog["templates"]["operator-console"]["source"] == "vercel"
    assert catalog["templates"]["editorial-calm"]["source"] == "apple+vercel hybrid"


def test_v144_design_preset_normalization_should_default_to_restrained_product() -> None:
    normalized = normalize_design_preset_choice("v1.4.4", "", "")

    assert normalized["design_preset"] == "restrained-product"
    assert normalized["canonical_design_preset"] == "restrained-product"
    assert normalized["preset_source"] == "apple"
    assert normalized["template_catalog_count"] == 3


def test_v144_anti_ai_ui_contract_should_expose_required_baseline() -> None:
    contract = build_anti_ai_ui_contract("v1.4.4")

    assert contract["contract_mode"] == "baseline"
    assert "gradient text" in contract["forbidden_visual_patterns"]
    assert contract["minimum_touch_target"] == "44x44"
    assert contract["focus_visibility_policy"] == "required"
    assert contract["external_reference_runtime_dependency"] is False
