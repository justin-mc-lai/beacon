from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.4.4"
FEATURE = "Beacon V144 Design Baseline Demo"
SLUG = "beacon-v144-design-baseline-demo"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_feature_docs(root: Path, *, prd_extra: str = "") -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/architecture-blueprint.md", "# blueprint\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        (
            "# PRD\n"
            "ui_visualization_required: true\n"
            "prototype_freeze_required: true\n"
            "design_preset: operator-console\n"
            "layout: dashboard workbench with clear hierarchy\n"
            "states: loading / empty / success / error\n"
            "interaction: click detail, submit approval, return to overview\n"
            f"{prd_extra}"
        ),
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        (
            "# User Story\n"
            "page hierarchy is explicit\n"
            "state coverage includes loading, empty, success, error\n"
            "users click toolbar actions and return to overview\n"
        ),
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
        "# Test Cases\nverify hierarchy, state changes, and interaction flow\n",
    )


def test_v144_review_design_should_emit_template_catalog_and_selected_preset(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    result = _invoke(["review", "design", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    baseline = payload["design_baseline_review"]
    assert baseline["template_catalog_count"] == 3
    assert baseline["canonical_design_preset"] == "operator-console"
    assert baseline["recommended_design_preset"] == "operator-console"
    assert baseline["anti_ai_ui_contract"]["minimum_touch_target"] == "44x44"


def test_v144_review_design_should_flag_discouraged_anti_ai_patterns(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path, prd_extra="visual direction uses gradient text and purple gradient hero\n")

    result = _invoke(["review", "design", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    reason_codes = {item["reason_code"] for item in payload["design_baseline_review"]["findings"]}
    assert "anti_ai_gradient_text_requested" in reason_codes
    assert "anti_ai_purple_gradient_requested" in reason_codes
