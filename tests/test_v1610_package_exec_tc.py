"""package exec-layer TC runner (lake D)."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.feature_package import materialize_feature_package
from beacon.utils.package_exec_tc import list_exec_tc_rows, run_package_exec_tcs


def test_list_exec_skips_rg_and_print0():
    md = """
| TC ID | AC ID | Command | Assertion |
| TC-1 | AC-001 | `rg -n x truth.md` | y |
| TC-2 | AC-001 | `python3 -c 'print(0)'` | exit_code==0 |
| TC-3 | AC-001 | `python3 -c 'import beacon'` | exit_code==0 |
"""
    rows = list_exec_tc_rows(md)
    cmds = " ".join((r.get("command") or "") for r in rows)
    assert "rg -n" not in cmds
    assert "print(0)" not in cmds
    assert "import beacon" in cmds


def test_materialize_any_docs_version_writes_gold_shape(tmp_path: Path):
    """Product docs lines (e.g. v0.0.x / v1.5.x) still get gold shape — dual-axis safe."""
    (tmp_path / "docs/beacon/v1.5.2").mkdir(parents=True)
    out = materialize_feature_package(tmp_path, version="v1.5.2", feature="old")
    assert out.get("blocked") is not True
    truth = (tmp_path / "docs/beacon/v1.5.2/features/old/truth.md").read_text(encoding="utf-8")
    assert "## 人话" in truth or "## Plain language" in truth
    assert "## Intent Coverage Matrix" in truth
    assert "package_maturity: scaffold" in truth


def test_run_exec_writes_evidence(tmp_path: Path):
    version = "v1.6.10"
    slug = "exec-demo"
    d = tmp_path / "docs/beacon" / version / "features" / slug
    d.mkdir(parents=True)
    (d / "truth.md").write_text(
        """---
slug: exec-demo
version: v1.6.10
domain_required: false
package_maturity: filled
---
# T
## 人话
x
## Intent Coverage Matrix
| intent_id | source | strength | landing | status |
| INT-01 | p | must | AC-001 | covered |
## Acceptance Criteria
| AC ID | Description |
| AC-001 | a |
## FSM 五元组
| State | Event | Guard | To | Action |
| a | e | g | b | x |
### invalid / illegal
- a→z
## Non-goals
- n
""",
        encoding="utf-8",
    )
    (d / "tests.md").write_text(
        """| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-E | AC-001 | `python3 -c 'print(1)'` | exit_code==0 |
""",
        encoding="utf-8",
    )
    out = run_package_exec_tcs(tmp_path, version=version, feature=slug, write_evidence=True)
    assert out["pass"] is True
    assert (tmp_path / ".beacon/evidence/test-results/exec-demo/TC-E.json").is_file()
