"""v1.6.10 gold-aligned truth template + postwrite + release materials gates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from beacon.utils.feature_package import (
    materialize_feature_package,
    render_tests_package,
    render_truth_package,
)
from beacon.utils.truth_gen_postwrite import run_truth_gen_postwrite_gates
from beacon.utils.truth_review_gate import (
    evaluate_release_truth_materials_gate,
    mark_package_materials_stale,
    run_truth_review_gate,
)


def _write_humanizer_stub(root: Path, *, lang: str = "zh") -> Path:
    rel = "core-skills/Humanizer-zh/SKILL.md" if lang == "zh" else "core-skills/humanizer/SKILL.md"
    path = root / "oss-sync" / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# humanizer-{lang}\n\nRemove AI tone. Fulltext stub for tests.\n",
        encoding="utf-8",
    )
    return path


def _goldish_package(root: Path, *, version: str = "v1.6.10", slug: str = "demo-pay") -> Path:
    d = root / "docs" / "beacon" / version / "features" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "truth.md").write_text(
        f"""---
slug: {slug}
version: {version}
status: draft
language: zh
domain_required: true
package_maturity: filled
parser_contract: beacon-feature-package-v2
materials_status: current
---

# Requirement Truth: {slug}

## 人话

用户下单并支付；超时关单；重复回调幂等。

- 能做：支付与超时关单
- 不能做：跳态支付
- 怎样算完：paid / closed / refunded

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-01 | prompt | must | AC-001 | covered |
| INT-02 | prompt | must | AC-002 | covered |

## 用户旅程

1. 创建订单 2. 支付 3. 成功或超时 4. 可选退款

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | pay succeeds |
| AC-002 | timeout closes order |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| created | pay | amount_ok | paid | capture |
| created | timeout | unpaid | closed | cancel |
| paid | refund | within_window | refunded | reverse |

### invalid / illegal

- paid → created
- closed → paid

## Non-goals

- 线下现金对账
""",
        encoding="utf-8",
    )
    (d / "tests.md").write_text(
        f"""---
slug: {slug}
version: {version}
materials_status: current
---

# Tests

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `rg -n 'AC-001' docs/beacon/{version}/features/{slug}/truth.md` | present |
| TC-002 | AC-002 | `rg -n 'AC-002' docs/beacon/{version}/features/{slug}/truth.md` | present |
| TC-E | AC-001 | `python3 -c 'print(0)'` | exit_code==0 |
""",
        encoding="utf-8",
    )
    (d / "tasks.md").write_text(
        "---\nmaterials_status: current\n---\n# Tasks\n- [ ] TASK-001 implement pay\n",
        encoding="utf-8",
    )
    (d / "evidence.md").write_text(
        "| Surface | Authority | Canonical Artifact | Status | Route |\n"
        "|---------|-----------|--------------------|--------|-------|\n"
        "| qa | qa_verdict | .beacon/evidence/x.json | linked | qa |\n",
        encoding="utf-8",
    )
    return d


def test_render_truth_v1610_gold_sections(tmp_path: Path):
    text = render_truth_package(tmp_path, version="v1.6.10", feature="order-pay")
    for needle in (
        "## 人话",
        "## Intent Coverage Matrix",
        "## FSM 五元组",
        "invalid / illegal",
        "## Acceptance Criteria",
        "## Non-goals",
    ):
        assert needle in text, needle
    tests = render_tests_package(tmp_path, version="v1.6.10", feature="order-pay")
    assert "TC ID | AC ID | Command | Assertion" in tests


def test_render_truth_legacy_plain_language(tmp_path: Path):
    text = render_truth_package(tmp_path, version="v1.5.0", feature="legacy-feat")
    assert "## 大白话说明" in text
    assert "## 人话" not in text


def test_postwrite_recommend_freeze_on_pass(tmp_path: Path):
    _write_humanizer_stub(tmp_path)
    _goldish_package(tmp_path)
    post = run_truth_gen_postwrite_gates(
        tmp_path,
        version="v1.6.10",
        feature="demo-pay",
        written=["truth.md"],
        language="zh",
    )
    assert post.get("humanizer", {}).get("fulltext_loaded") is True
    assert int(post.get("humanizer", {}).get("skill_chars") or 0) > 0
    assert post.get("truth_review_gate", {}).get("pass") is True
    assert post.get("recommend_freeze") is True
    assert post.get("blocked") is False


def test_postwrite_no_freeze_on_review_fail(tmp_path: Path):
    _write_humanizer_stub(tmp_path)
    d = tmp_path / "docs" / "beacon" / "v1.6.10" / "features" / "broken"
    d.mkdir(parents=True)
    (d / "truth.md").write_text(
        """---
slug: broken
version: v1.6.10
status: draft
language: zh
domain_required: true
parser_contract: beacon-feature-package-v2
---
# Truth
## Acceptance Criteria
| AC ID | Description |
|-------|-------------|
| AC-001 | only one
## FSM 五元组
| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| a | e | g | b | x |
""",
        encoding="utf-8",
    )
    (d / "tests.md").write_text(
        "| TC ID | AC ID | Command | Assertion |\n|-------|-------|---------|-----------|\n| TC-001 | AC-001 | x | y |\n",
        encoding="utf-8",
    )
    post = run_truth_gen_postwrite_gates(
        tmp_path,
        version="v1.6.10",
        feature="broken",
        language="zh",
    )
    assert post.get("recommend_freeze") is False
    assert post.get("blocked") is True
    assert "truth_review_gate_failed" in (post.get("reason_codes") or []) or not post.get(
        "truth_review_gate", {}
    ).get("pass")


def test_materialize_v1610_runs_postwrite(tmp_path: Path):
    _write_humanizer_stub(tmp_path)
    (tmp_path / "docs" / "beacon" / "v1.6.10").mkdir(parents=True)
    out = materialize_feature_package(
        tmp_path,
        version="v1.6.10",
        feature="mat-lake",
        force=True,
    )
    assert "truth_gen_postwrite" in out
    truth = (tmp_path / "docs/beacon/v1.6.10/features/mat-lake/truth.md").read_text(encoding="utf-8")
    assert "## 人话" in truth
    assert "## Intent Coverage Matrix" in truth
    # scaffold domain_required=false may still pass or fail TRG; freeze only if both ok
    assert "recommend_freeze" in out
    if out["truth_gen_postwrite"].get("blocked"):
        assert out["recommend_freeze"] is False


def test_release_materials_gate_stale_fail_closed(tmp_path: Path):
    _write_humanizer_stub(tmp_path)
    _goldish_package(tmp_path)
    # ensure TRG report exists and passes
    review = run_truth_review_gate(tmp_path, version="v1.6.10", feature="demo-pay", write_report=True)
    assert review.get("pass") or review.get("review_gate_pass")
    mark_package_materials_stale(tmp_path, version="v1.6.10", feature="demo-pay")
    gate = evaluate_release_truth_materials_gate(tmp_path, version="v1.6.10", feature="demo-pay")
    assert gate.get("required") is True
    assert gate.get("blocked") is True
    assert "materials_status_stale" in (gate.get("reason_codes") or [])


def test_release_materials_gate_missing_report_recheck(tmp_path: Path):
    _write_humanizer_stub(tmp_path)
    _goldish_package(tmp_path)
    gate = evaluate_release_truth_materials_gate(tmp_path, version="v1.6.10", feature="demo-pay")
    # live re-check should produce report; goldish package should pass
    assert gate.get("required") is True
    if gate.get("blocked"):
        # if blocked, must not be silent — reason codes present
        assert gate.get("reason_codes")
    else:
        assert gate.get("pass") is True
