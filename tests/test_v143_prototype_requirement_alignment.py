from __future__ import annotations

from pathlib import Path

from beacon.commands.gate import GateMode, check_prototype_contract
from beacon.utils.prototype_support import feature_requires_prototype, version_requires_prototype


VERSION = "v1.4.3"
UMBRELLA = "beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation"
DESIGN = "beacon-v1.4.3-design-review-surface-and-prototype-governance"


def _write_feature_docs(root: Path, feature: str, body: str) -> None:
    slug = feature.lower().replace(" ", "-")
    for rel in ("user-story", "prd", "qa/test-cases"):
        path = root / "docs" / "beacon" / VERSION / rel / f"{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")


def test_v143_conceptual_prototype_language_does_not_trigger_prototype_gate(tmp_path: Path) -> None:
    umbrella_body = (
        "# PRD\n"
        "design-review owns direction challenge while prototype remains conditional handoff freeze when triggered.\n"
        "prototype must not become final approval or UI deliverable authority.\n"
    )
    design_body = (
        "# PRD\n"
        "design-review happens before prototype when UX/UI handoff is real.\n"
        "prototype is a governed packaging layer, not the design decision owner.\n"
    )
    _write_feature_docs(tmp_path, UMBRELLA, umbrella_body)
    _write_feature_docs(tmp_path, DESIGN, design_body)

    assert feature_requires_prototype(tmp_path, VERSION, UMBRELLA) is False
    assert feature_requires_prototype(tmp_path, VERSION, DESIGN) is False
    assert version_requires_prototype(tmp_path, VERSION) is False
    assert check_prototype_contract(tmp_path, GateMode.STRICT, "release", version=VERSION) == []


def test_v143_explicit_ui_trigger_still_requires_prototype(tmp_path: Path) -> None:
    _write_feature_docs(
        tmp_path,
        DESIGN,
        (
            "# PRD\n"
            "ui_visualization_required: true\n"
            "prototype_freeze_required: true\n"
            "页面：项目详情、审批面板、状态面板。\n"
        ),
    )

    assert feature_requires_prototype(tmp_path, VERSION, DESIGN) is True
    assert version_requires_prototype(tmp_path, VERSION) is True
    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version=VERSION)
    reason_codes = {item.get("reason_code") for item in issues}
    assert "prototype_missing" in reason_codes
