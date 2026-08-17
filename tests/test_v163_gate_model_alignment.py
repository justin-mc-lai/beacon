"""Tests for beacon-gate-truth-model-alignment-v163 (P0-3).

Covers check_formal_version_package_closure semver fork:
- <v1.5.2 keeps legacy top-dir contract (prd/user-story/qa/test-cases)
- >=v1.5.2 checks package-authoritative feature package closure instead
- version-line materials still checked for all versions
- empty dirs cannot bypass; missing feature package still blocks
"""
from __future__ import annotations

from pathlib import Path

from beacon.commands.gate import GateMode, check_formal_version_package_closure


def _write(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("<!-- stub -->\n", encoding="utf-8")


def _version_line(root: Path, version: str) -> None:
    """Write the shared version-line materials required for all versions."""
    base = root / "docs" / "beacon" / version
    _write(base / "SUMMARY.md")
    _write(base / "execution" / "boundaries.md")
    _write(base / "release" / f"{version}.md")


def _v1110_extras(root: Path, version: str) -> None:
    base = root / "docs" / "beacon" / version
    _write(base / "execution" / "project-skill-qa-evolution-blueprint.md")
    _write(base / "source-architecture" / "index.md")


def _feature_package(root: Path, version: str, slug: str = "demo-feature") -> None:
    pkg = root / "docs" / "beacon" / version / "features" / slug
    _write(pkg / "truth.md")
    _write(pkg / "tests.md")


def _reason_codes(issues: list[dict]) -> list[str]:
    return [str(i.get("reason_code", "")) for i in issues]


def test_semver_fork_v162_no_legacy_top_dirs_required(tmp_path: Path) -> None:
    """AC-001: >=v1.5.2 does not require prd/user-story/qa/test-cases top dirs."""
    _version_line(tmp_path, "v1.6.2")
    _v1110_extras(tmp_path, "v1.6.2")
    _feature_package(tmp_path, "v1.6.2")
    # intentionally no prd/ user-story/ qa/test-cases/
    issues = check_formal_version_package_closure(
        tmp_path, GateMode.STRICT, "release", "v1.6.2"
    )
    codes = _reason_codes(issues)
    assert "formal_package_closure_missing" not in codes
    assert "feature_package_closure_missing" not in codes


def test_feature_package_closure_satisfied(tmp_path: Path) -> None:
    """AC-002: >=v1.5.2 with features/<slug>/{truth,tests}.md passes."""
    _version_line(tmp_path, "v1.6.2")
    _v1110_extras(tmp_path, "v1.6.2")
    _feature_package(tmp_path, "v1.6.2")
    issues = check_formal_version_package_closure(
        tmp_path, GateMode.STRICT, "release", "v1.6.2"
    )
    assert issues == []


def test_legacy_v1410_keeps_top_dir_contract(tmp_path: Path) -> None:
    """AC-003: <v1.5.2 still requires prd/user-story/qa/test-cases top dirs."""
    _version_line(tmp_path, "v1.4.10")
    _v1110_extras(tmp_path, "v1.4.10")
    # no prd/ user-story/ qa/test-cases/
    issues = check_formal_version_package_closure(
        tmp_path, GateMode.STRICT, "release", "v1.4.10"
    )
    codes = _reason_codes(issues)
    assert "formal_package_closure_missing" in codes
    missing_detail = str(issues[0].get("details", {}).get("missing", []))
    assert "prd/" in missing_detail
    assert "user-story/" in missing_detail
    assert "qa/test-cases/" in missing_detail


def test_version_line_materials_still_checked(tmp_path: Path) -> None:
    """AC-004: >=v1.5.2 missing SUMMARY still critical blocks."""
    _v1110_extras(tmp_path, "v1.6.2")
    _write(tmp_path / "docs" / "beacon" / "v1.6.2" / "execution" / "boundaries.md")
    _write(tmp_path / "docs" / "beacon" / "v1.6.2" / "release" / "v1.6.2.md")
    _feature_package(tmp_path, "v1.6.2")
    # no SUMMARY.md
    issues = check_formal_version_package_closure(
        tmp_path, GateMode.STRICT, "release", "v1.6.2"
    )
    codes = _reason_codes(issues)
    assert "formal_package_closure_missing" in codes
    assert any(i.get("severity") == "critical" and i.get("blocked") for i in issues)


def test_missing_feature_package_blocks(tmp_path: Path) -> None:
    """AC-005: >=v1.5.2 with no feature package -> feature_package_closure_missing."""
    _version_line(tmp_path, "v1.6.2")
    _v1110_extras(tmp_path, "v1.6.2")
    # no features/ dir
    issues = check_formal_version_package_closure(
        tmp_path, GateMode.STRICT, "release", "v1.6.2"
    )
    codes = _reason_codes(issues)
    assert "feature_package_closure_missing" in codes
    msg = str(issues[0].get("message", ""))
    assert "prd/" not in msg
    assert "user-story/" not in msg
    assert "qa/test-cases/" not in msg


def test_regression_v162_no_top_dir_block() -> None:
    """AC-006: real project v1.6.2 no longer blocks on missing top dirs."""
    project_root = Path(__file__).resolve().parents[1]
    issues = check_formal_version_package_closure(
        project_root, GateMode.STRICT, "release", "v1.6.2"
    )
    for issue in issues:
        msg = str(issue.get("message", "")) + str(issue.get("details", ""))
        # must not complain about legacy top dirs for v1.6.2
        assert "prd/" not in msg, f"legacy top-dir drift: {msg}"
        assert "user-story/" not in msg, f"legacy top-dir drift: {msg}"
        assert "qa/test-cases/" not in msg, f"legacy top-dir drift: {msg}"


def test_empty_dir_no_bypass(tmp_path: Path) -> None:
    """AC-007: empty prd/ dir does not bypass; needs real feature package."""
    _version_line(tmp_path, "v1.6.2")
    _v1110_extras(tmp_path, "v1.6.2")
    # empty prd/ dir, no .md files, no features/
    (tmp_path / "docs" / "beacon" / "v1.6.2" / "prd").mkdir(parents=True)
    issues = check_formal_version_package_closure(
        tmp_path, GateMode.STRICT, "release", "v1.6.2"
    )
    codes = _reason_codes(issues)
    assert "feature_package_closure_missing" in codes
    assert any(i.get("blocked") for i in issues)
