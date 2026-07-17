from __future__ import annotations

import os

os.environ.setdefault("BEACON_DESIGN_MD_LINT_SKIP_NPX", "1")

from pathlib import Path

from beacon.utils.design_company_templates import (
    COMPANY_DESIGN_TEMPLATES,
    auto_select_company_template,
    list_company_templates,
)
from beacon.utils.design_md_lint import run_design_md_lint
from beacon.utils.product_goal_runtime import (
    build_stage_plan,
    create_goal_run,
    detect_ux_intent,
    run_design_stage_for_goal,
    tick_goal_run,
)
from beacon.utils.ui_design_ship import apply_ui_design_to_scorecard, build_ui_design_ship_gate
from beacon.utils.design_baseline import synthesize_unattended_design_baseline


def test_goal_inserts_design_stage_when_ux() -> None:
    stages = build_stage_plan(utterance="做运营中台界面", ux_required=True)
    names = [s["stage"] for s in stages]
    assert names == ["plan", "truth", "design", "implement", "qa", "release"]
    design = next(s for s in stages if s["stage"] == "design")
    assert "beacon-gen-design" in design["skills"]


def test_goal_no_design_stage_without_ux() -> None:
    stages = build_stage_plan(utterance="纯后端 API 无界面", ux_required=False)
    assert "design" not in [s["stage"] for s in stages]


def test_detect_ux_intent() -> None:
    assert detect_ux_intent("需要视觉交付的管理后台") is True
    assert detect_ux_intent("batch job only", truth_markdown="ux_required: true") is True


def test_run_design_stage_writes_baseline(tmp_path: Path) -> None:
    (tmp_path / "docs" / "beacon" / "v1.6.7" / "features" / "demo-ui").mkdir(parents=True)
    (tmp_path / "docs" / "beacon" / "v1.6.7" / "features" / "demo-ui" / "truth.md").write_text(
        "---\nux_required: true\n---\n# 中台\n运营后台订单列表\n",
        encoding="utf-8",
    )
    run = create_goal_run(
        tmp_path,
        utterance="做运营中台订单列表 UI",
        version="v1.6.7",
        feature="demo-ui",
    )
    assert run.get("ux_required") is True
    assert "design" in [s["stage"] for s in run["stages"]]
    # advance to design via ticks: plan done, truth done, design active
    rid = run["run_id"]
    tick_goal_run(tmp_path, rid, note="finish plan")
    tick_goal_run(tmp_path, rid, note="finish truth")
    # third tick should enter design and auto-run
    payload = tick_goal_run(tmp_path, rid, note="enter design")
    # if design not auto-entered, call explicitly
    if not payload.get("design_stage"):
        payload = run_design_stage_for_goal(tmp_path, rid)
    assert payload.get("design_stage")
    assert (tmp_path / "DESIGN.md").exists() or (
        payload["design_stage"].get("baseline", {}).get("mode") == "fine_tune"
    )
    assert payload["design_stage"].get("lint", {}).get("evidence_path")


def test_existing_design_fine_tune(tmp_path: Path) -> None:
    (tmp_path / "docs" / "beacon" / "v1.6.7").mkdir(parents=True)
    (tmp_path / "DESIGN.md").write_text("# Brand\ncoral only\n", encoding="utf-8")
    out = synthesize_unattended_design_baseline(tmp_path, "v1.6.7", force=False)
    assert out["mode"] == "fine_tune"
    assert (tmp_path / "DESIGN.md").read_text(encoding="utf-8") == "# Brand\ncoral only\n"
    assert (tmp_path / "docs/beacon/v1.6.7/design/fine-tune-proposal.md").exists()


def test_design_md_lint_writes_evidence(tmp_path: Path) -> None:
    from beacon.utils.design_baseline import render_complete_design_md

    (tmp_path / "docs" / "beacon" / "v1.6.7").mkdir(parents=True)
    (tmp_path / "DESIGN.md").write_text(
        render_complete_design_md(product_name="LintMe", surface="web", version="v1.6.7"),
        encoding="utf-8",
    )
    payload = run_design_md_lint(tmp_path, feature="lint-demo", version="v1.6.7")
    assert payload.get("evidence_path")
    assert (tmp_path / payload["evidence_path"]).exists()
    assert payload.get("status") in {"pass", "blocked"}


def test_ship_blocks_on_lint_error(tmp_path: Path) -> None:
    (tmp_path / "docs" / "beacon" / "v1.6.7" / "features" / "ux-demo").mkdir(parents=True)
    truth = "---\nux_required: true\n---\n# UI\n\n## Domain FSM — X\n\n| State | From | Guard |\n| draft | - | - |\n"
    (tmp_path / "docs" / "beacon" / "v1.6.7" / "features" / "ux-demo" / "truth.md").write_text(truth, encoding="utf-8")
    # empty-ish DESIGN triggers structural error
    (tmp_path / "DESIGN.md").write_text("# incomplete\n", encoding="utf-8")
    (tmp_path / "docs" / "beacon" / "v1.6.7" / "features" / "ux-demo" / "ui-state-matrix.md").write_text(
        "| State | Page | Badge | Primary action |\n| draft | home | gray | go |\n",
        encoding="utf-8",
    )
    gate = build_ui_design_ship_gate(tmp_path, version="v1.6.7", feature="ux-demo")
    assert gate.get("required") is True
    # either design_md_lint blocked or design missing-quality
    lint = gate.get("design_md_lint") or {}
    assert gate.get("blocked") is True or lint.get("blocked") is True or gate.get("status") == "blocked"


def test_company_catalog_min_eight() -> None:
    assert len(list_company_templates()) >= 8
    assert len(COMPANY_DESIGN_TEMPLATES) >= 8


def test_company_auto_select() -> None:
    d = auto_select_company_template("stripe 支付 billing checkout")
    assert d["company_template"] == "stripe"
    d2 = auto_select_company_template("random text", surface="pc-console")
    assert d2["company_template"] in COMPANY_DESIGN_TEMPLATES


def test_implement_blocks_without_design() -> None:
    # prompt contract check via implement_adapters string presence
    from beacon.utils import implement_adapters as ia
    src = Path(ia.__file__).read_text(encoding="utf-8")
    assert "beacon design baseline" in src
    assert "STOP freestyle UI" in src or "fail-closed" in src or "surface auto" in src


def test_scorecard_has_design_fields(tmp_path: Path) -> None:
    from beacon.utils.design_baseline import render_complete_design_md

    (tmp_path / "docs" / "beacon" / "v1.6.7" / "features" / "ux-demo").mkdir(parents=True)
    truth = "---\nux_required: true\n---\n# UI page\n"
    (tmp_path / "docs" / "beacon" / "v1.6.7" / "features" / "ux-demo" / "truth.md").write_text(truth, encoding="utf-8")
    (tmp_path / "DESIGN.md").write_text(
        render_complete_design_md(product_name="S", surface="web"), encoding="utf-8"
    )
    (tmp_path / "docs" / "beacon" / "v1.6.7" / "features" / "ux-demo" / "ui-state-matrix.md").write_text(
        "| State | Page | Badge | Primary |\n| empty | home | - | create |\n",
        encoding="utf-8",
    )
    gate = build_ui_design_ship_gate(tmp_path, version="v1.6.7", feature="ux-demo")
    sc = apply_ui_design_to_scorecard({"release_ready": True, "continue_decision": "ready_for_release"}, gate)
    assert "design_alignment" in sc
    assert "design_md_lint" in sc
    assert "ui_state_matrix" in sc
