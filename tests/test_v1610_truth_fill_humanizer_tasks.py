"""v1.6.10: scaffold draft-only, humanizer apply, AC tasks, domain exec TC."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.feature_package import (
    materialize_feature_package,
    render_tasks_package,
    render_tests_package,
    render_truth_package,
)
from beacon.utils.humanizer_config import apply_humanizer_l0
from beacon.utils.truth_gen_postwrite import run_truth_gen_postwrite_gates
from beacon.utils.truth_review_gate import evaluate_truth_review_gate


def _hum_stub(root: Path) -> None:
    p = root / "oss-sync/core-skills/Humanizer-zh/SKILL.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# humanizer-zh\n去掉 AI 味。标志着→说明\n", encoding="utf-8")


def test_scaffold_template_has_maturity_and_journey(tmp_path: Path):
    t = render_truth_package(tmp_path, version="v1.6.10", feature="lake-x")
    assert "package_maturity: scaffold" in t
    assert "## 用户旅程" in t
    assert "## 人话" in t
    # scaffold must not pass fill-depth
    tests = render_tests_package(tmp_path, version="v1.6.10", feature="lake-x")
    r = evaluate_truth_review_gate(truth_md=t, tests_md=tests, version="v1.6.10", feature="lake-x")
    assert r["pass"] is False
    assert r.get("reason_code") == "truth_scaffold_not_filled" or any(
        f.get("kind") == "scaffold_maturity" for f in r.get("findings") or []
    )


def test_humanizer_apply_preserves_machine_fields():
    md = """---
status: draft
language: zh
---

## 人话

这标志着 赋能 支付体验。

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-01 | prompt | must | AC-001 | covered |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | pay |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| a | e | g | b | x |
"""
    out = apply_humanizer_l0(md, profile={"language": "zh", "preserve_machine_fields": True, "skill_text": "x"})
    assert out["applied"] is True
    assert "Acceptance Criteria" in out["truth_md"]
    assert "Intent Coverage Matrix" in out["truth_md"]
    assert "标志着" not in out["truth_md"].split("## Intent")[0]
    assert "说明" in out["truth_md"] or "支持" in out["truth_md"]


def test_business_domain_requires_exec_and_journey():
    truth = """---
domain_required: true
package_maturity: filled
language: zh
---
# T
## 人话
支付。
- 能做：付
- 不能做：跳态
- 怎样算完：paid
## Intent Coverage Matrix
| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-01 | prompt | must | AC-001 | covered |
## Acceptance Criteria
| AC ID | Description |
|-------|-------------|
| AC-001 | pay
## FSM 五元组
| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| created | pay | ok | paid | cap |
### invalid / illegal
- paid→created
## Non-goals
- x
"""
    tests_docs = """| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `rg -n pay truth.md` | y |
"""
    r = evaluate_truth_review_gate(truth_md=truth, tests_md=tests_docs, version="v1.6.10", feature="pay")
    assert r["pass"] is False
    kinds = {f.get("kind") for f in r.get("findings") or []}
    assert "journey_missing" in kinds or "domain_exec_tc_missing" in kinds

    truth2 = truth.replace("## Acceptance Criteria", "## 用户旅程\n1. 下单 2. 支付\n\n## Acceptance Criteria")
    tests2 = tests_docs + "\n| TC-E | AC-001 | `python3 -c 'print(0)'` | exit_code==0 |\n"
    r2 = evaluate_truth_review_gate(truth_md=truth2, tests_md=tests2, version="v1.6.10", feature="pay")
    assert r2["pass"] is True


def test_tasks_derived_from_ac(tmp_path: Path):
    d = tmp_path / "docs/beacon/v1.6.10/features/t1"
    d.mkdir(parents=True)
    (d / "truth.md").write_text(
        """---
slug: t1
version: v1.6.10
---
## Acceptance Criteria
| AC ID | Description |
|-------|-------------|
| AC-001 | first
| AC-002 | second
""",
        encoding="utf-8",
    )
    tasks = render_tasks_package(tmp_path, version="v1.6.10", feature="t1")
    assert "TASK-001 Implement AC-001" in tasks
    assert "TASK-002 Implement AC-002" in tasks
    assert "task_source: acceptance_criteria" in tasks


def test_materialize_scaffold_not_recommend_freeze(tmp_path: Path):
    _hum_stub(tmp_path)
    (tmp_path / "docs/beacon/v1.6.10").mkdir(parents=True)
    out = materialize_feature_package(tmp_path, version="v1.6.10", feature="mat", force=True)
    assert out.get("recommend_freeze") is False
    pw = out.get("truth_gen_postwrite") or {}
    assert pw.get("recommend_freeze") is False
    assert "truth-review" in str(pw.get("workflow") or {}).lower() or any(
        "fill" in s.lower() or "review" in s.lower() for s in (pw.get("next_steps") or [])
    )
