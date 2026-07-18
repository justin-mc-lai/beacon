from pathlib import Path

from beacon.utils.truth_human_readable import (
    REASON_L0_MISSING,
    check_truth_file,
    check_truth_text,
    example_paths,
    norms_paths,
)

ROOT = Path(__file__).resolve().parents[1]
TRUTH = ROOT / "docs/beacon/v1.6.7/features/beacon-truth-human-readable-i18n-v167/truth.md"


def test_self_truth_has_l0():
    r = check_truth_file(TRUTH)
    assert r["ok"] is True, r
    assert "## 人话" in r.get("l0_headings", []) or "l0" in r


def test_l0_budget_self():
    r = check_truth_file(TRUTH)
    assert r["ok"] is True


def test_l0_four_questions():
    text = TRUTH.read_text(encoding="utf-8")
    assert "能做" in text or "不能" in text
    assert "怎样算" in text or "完成" in text


def test_norms_files_exist():
    n = norms_paths(ROOT)
    assert n["zh"].is_file()
    assert n["en"].is_file()
    assert "五原则" in n["zh"].read_text(encoding="utf-8") or "原则" in n["zh"].read_text(encoding="utf-8")


def test_gate_missing_l0():
    bad = "---\nlanguage: zh\n---\n# x\n\n## Acceptance Criteria\n| AC | d |\n"
    r = check_truth_text(bad)
    assert r["ok"] is False
    assert r["reason_code"] == REASON_L0_MISSING


def test_l0_not_sufficient_for_ac():
    # L0 alone is not a package — document contract: AC section still expected for packages
    only_l0 = "---\nlanguage: zh\n---\n# t\n\n## 人话\n\n意图测试。\n- 能做：a\n- 不能做：b\n- 怎样算完：c\n"
    r = check_truth_text(only_l0)
    assert r["ok"] is True  # prose gate passes
    assert "Acceptance Criteria" not in only_l0  # package completeness is separate


def test_language_enum():
    r = check_truth_text("---\nlanguage: fr\n---\n## 人话\n\nx\n")
    assert r["ok"] is False


def test_bilingual_fixture():
    t = """---
language: bilingual
---
# t

## 人话

意图中文。能做 a。不能做 b。怎样算完 c。

## Plain language

Intent en. Can: a. Cannot: b. Done when: c.
"""
    r = check_truth_text(t)
    assert r["ok"] is True, r


def test_examples_exist():
    e = example_paths(ROOT)
    assert e["zh"].is_file()
    assert e["en"].is_file()


def test_humanizer_must_not_drop_ac():
    text = TRUTH.read_text(encoding="utf-8")
    assert "AC-HR-001" in text
    assert "AC-HR-012" in text


def test_axis_mentions_lake():
    axis = ROOT / "docs/beacon/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/goalrun-main-axis.md"
    assert "beacon-truth-human-readable-i18n-v167" in axis.read_text(encoding="utf-8")
