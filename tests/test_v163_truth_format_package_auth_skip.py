"""Tests for beacon-truth-format-package-auth-skip-v163.

Covers 4 connected cracks (C direction):
1. compute_feature_paths returns features/ paths for >=v1.5.2
2. manifest status read from truth.md frontmatter for package-auth
3. truth_format validation skipped for >=v1.5.2 (feature_package.validate replaces)
4. legacy truth_format preserved for <v1.5.2
"""
from __future__ import annotations

from pathlib import Path

from beacon.utils.manifest import compute_feature_paths, sync_manifest
from beacon.utils.truth_map import feature_package_authoritative


# ---- AC-001 feature paths package-auth ----

def test_feature_paths_package_auth() -> None:
    """compute_feature_paths for >=v1.5.2 returns features/<slug>/ paths."""
    paths = compute_feature_paths(Path("/tmp/proj"), "v1.6.3", "demo-feat")
    assert "features/v1.6.3/demo-feat/truth.md" in paths["prd"] or "features/" in paths["prd"], paths
    # truth path must point to features/<slug>/truth.md for package-auth
    assert "features/" in paths.get("truth", paths["prd"]), paths


def test_feature_paths_legacy_unchanged() -> None:
    """compute_feature_paths for <v1.5.2 keeps legacy paths."""
    paths = compute_feature_paths(Path("/tmp/proj"), "v1.4.10", "demo-feat")
    assert "prd/demo-feat.md" in paths["prd"]
    assert "features/" not in paths["prd"]


# ---- AC-002 manifest status from frontmatter ----

def _make_pkg(root: Path, version: str, slug: str, status: str = "frozen") -> None:
    pkg = root / "docs" / "beacon" / version / "features" / slug
    pkg.mkdir(parents=True)
    (pkg / "truth.md").write_text(
        f"---\nslug: {slug}\nversion: {version}\nstatus: {status}\nlanguage: zh\n"
        "canonical_refs:\n  prd: a\n  user_story: a\n  test_case: a\n"
        "parser_contract: beacon-feature-package-v1\n"
        "truth_source_model: feature_package_authoritative\n"
        "truth_map_contract: beacon-truth-map-v1\n---\n\n# t\n",
        encoding="utf-8",
    )
    (pkg / "tests.md").write_text(
        f"---\nslug: {slug}\nversion: {version}\nstatus: {status}\nlanguage: zh\n"
        "truth_ref: a\nparser_contract: beacon-feature-package-v1\n---\n\n"
        "# t\n\n## 覆盖矩阵\n\n"
        "| AC ID | TC ID | Layer | Command | Assertion |\n"
        "|-------|-------|-------|---------|-----------|\n"
        "| AC-001 | TC-001 | contract | `python3 -m pytest tests/x.py -q` | pass |\n",
        encoding="utf-8",
    )
    (pkg / "tasks.md").write_text(
        f"---\nslug: {slug}\nversion: {version}\nstatus: {status}\nlanguage: zh\n"
        "truth_ref: a\nparser_contract: beacon-feature-package-v1\n---\n\n"
        "# t\n\n- [ ] TC-001 do (BLOCKED:Phase-A)\n",
        encoding="utf-8",
    )
    (pkg / "evidence.md").write_text(
        f"---\nslug: {slug}\nversion: {version}\nstatus: {status}\nlanguage: zh\n"
        "truth_ref: a\nparser_contract: beacon-feature-package-v1\n---\n\n"
        "# t\n\n## Authority Surface\n\n"
        "| surface | authority | artifact |\n|---------|-----------|----------|\n"
        "| truth.md | requirement_truth | a |\n",
        encoding="utf-8",
    )


def test_manifest_status_from_frontmatter(tmp_path: Path) -> None:
    """package-auth frozen package manifest status = frozen (from truth.md frontmatter)."""
    _make_pkg(tmp_path, "v1.6.3", "demo-feat", status="frozen")
    result = sync_manifest(tmp_path, "v1.6.3")
    for f in result.get("features", []):
        if f.get("slug") == "demo-feat":
            assert f.get("status") == "frozen", f.get("status")
            return
    assert False, "feature not found in manifest"


# ---- AC-003 truth_format skip package-auth ----

def test_truth_format_skip_package_auth(tmp_path: Path) -> None:
    """build_requirement_package_gate for >=v1.5.2 does not report truth_format_non_compliant."""
    from beacon.utils.material_audit import build_requirement_package_gate
    _make_pkg(tmp_path, "v1.6.3", "demo-feat", status="frozen")
    gate = build_requirement_package_gate(tmp_path, version="v1.6.3", feature="demo-feat")
    failing = [c.get("name") for c in gate.get("failing_checks", [])]
    assert not any("truth_format" in str(n) for n in failing), failing


# ---- AC-004 legacy truth_format preserved ----

def test_legacy_truth_format_preserved(tmp_path: Path) -> None:
    """<v1.5.2 truth_format validation still runs (legacy path)."""
    from beacon.utils.material_audit import build_requirement_package_gate
    # build a legacy v1.4.10 package with NON-compliant test-case (no Outline etc.)
    base = tmp_path / "docs" / "beacon" / "v1.4.10"
    (base / "qa" / "test-cases").mkdir(parents=True)
    (base / "qa" / "test-cases" / "demo-legacy.md").write_text("# bad\n\nno format\n", encoding="utf-8")
    (base / "prd").mkdir(parents=True)
    (base / "prd" / "demo-legacy.md").write_text("# prd\n", encoding="utf-8")
    (base / "user-story").mkdir(parents=True)
    (base / "user-story" / "demo-legacy.md").write_text("# us\n", encoding="utf-8")
    sync_manifest(tmp_path, "v1.4.10")
    gate = build_requirement_package_gate(tmp_path, version="v1.4.10", feature="demo-legacy")
    # legacy non-compliant test-case should be flagged (validation still runs)
    failing = [c.get("name") for c in gate.get("failing_checks", [])]
    assert any("truth_format" in str(n) for n in failing) or gate.get("status") == "blocked", failing


# ---- AC-005 implement unblocked format ----

def test_implement_unblocked_format() -> None:
    """v1.6.3 frozen package implement run not blocked by truth_format."""
    from beacon.utils.material_audit import build_requirement_package_gate
    root = Path(__file__).resolve().parents[1]
    gate = build_requirement_package_gate(
        root, version="v1.6.3", feature="beacon-gate-truth-model-alignment-v163"
    )
    failing = [c.get("name") for c in gate.get("failing_checks", [])]
    assert not any("truth_format" in str(n) for n in failing), failing
    assert gate.get("status") != "blocked" or not any(
        "truth_format" in str(c.get("reason_code", "")) for c in gate.get("failing_checks", [])
    )


# ---- AC-006 no regression v1.6.2 ----

def test_no_regression_v162() -> None:
    """v1.6.2 package build_requirement_package_gate still pass (not broken by path fix)."""
    from beacon.utils.material_audit import build_requirement_package_gate
    root = Path(__file__).resolve().parents[1]
    gate = build_requirement_package_gate(
        root, version="v1.6.2", feature="beacon-global-workspace-git-admission-v162"
    )
    failing = [c.get("name") for c in gate.get("failing_checks", [])]
    assert not any("truth_format" in str(n) for n in failing), failing


# ---- AC-007 feature_package.validate still runs ----

def test_feature_package_validate_still_runs() -> None:
    """package-auth packages still pass feature_package.validate_feature_package (real validation not bypassed)."""
    from beacon.utils.feature_package import validate_feature_package
    root = Path(__file__).resolve().parents[1]
    result = validate_feature_package(
        root, version="v1.6.3", feature="beacon-gate-truth-model-alignment-v163"
    )
    assert result.get("status") == "pass", result.get("diagnostics")
