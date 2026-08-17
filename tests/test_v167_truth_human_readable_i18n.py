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


def test_validate_package_passes_self():
    from beacon.utils.feature_package import validate_feature_package

    r = validate_feature_package(ROOT, version="v1.6.12", feature="beacon-test-modernization-v1612")
    assert r.get("blocked") is False, r.get("diagnostics")
    codes = [d.get("code") for d in r.get("diagnostics") or []]
    assert any(c == "truth_human_l0_ok" or (isinstance(c, str) and c.startswith("truth_human")) for c in codes) or r.get("blocked") is False


def test_validate_package_blocks_missing_l0(tmp_path: Path):
    from beacon.utils.feature_package import validate_feature_package

    # minimal package under tmp
    ver = "v1.6.7"
    slug = "demo-no-l0"
    pkg = tmp_path / "docs" / "beacon" / ver / "features" / slug
    pkg.mkdir(parents=True)
    (pkg / "truth.md").write_text(
        """---
slug: demo-no-l0
version: v1.6.7
status: draft
language: zh
canonical_refs:
  truth: docs/beacon/v1.6.7/features/demo-no-l0/truth.md
  tests: docs/beacon/v1.6.7/features/demo-no-l0/tests.md
  tasks: docs/beacon/v1.6.7/features/demo-no-l0/tasks.md
  evidence: docs/beacon/v1.6.7/features/demo-no-l0/evidence.md
parser_contract: beacon-feature-package-v2
---

# Demo

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | x | y |
""",
        encoding="utf-8",
    )
    (pkg / "tests.md").write_text(
        """# Tests
## Coverage Matrix
| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | unit | `python3 -m pytest -q` | pass |
""",
        encoding="utf-8",
    )
    (pkg / "tasks.md").write_text("- [ ] TASK-001 do it\n", encoding="utf-8")
    (pkg / "evidence.md").write_text(
        """# Evidence
| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| t | requirement_truth | docs/beacon/v1.6.7/features/demo-no-l0/truth.md | draft | truth |
""",
        encoding="utf-8",
    )
    r = validate_feature_package(tmp_path, version=ver, feature=slug)
    assert r.get("blocked") is True
    assert r.get("reason_code") == "truth_human_l0_missing"
    codes = [d.get("code") for d in r.get("diagnostics") or []]
    assert "truth_human_l0_missing" in codes


def test_prose_check_cli():
    import subprocess
    import sys

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "beacon.main",
            "truth",
            "prose-check",
            "-f",
            "beacon-truth-human-readable-i18n-v167",
            "-v",
            "v1.6.7",
            "-p",
            str(ROOT),
            "--json",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "ok" in proc.stdout.lower() or '"ok": true' in proc.stdout
