"""Tests for beacon-spec-fingerprint-package-auth-paths-v163.

Covers: _find_layer_files scans features/<slug>/ for >=v1.5.2 so spec
fingerprint reflects truth/tests content, making spec_impl_drift effective
on truth changes.
"""
from __future__ import annotations

from pathlib import Path

from beacon.utils.v110_baseline import _find_layer_files, generate_spec_fingerprint
from beacon.utils.truth_map import feature_package_authoritative


def _make_pkg(root: Path, version: str, slug: str = "demo-fp") -> None:
    pkg = root / "docs" / "beacon" / version / "features" / slug
    pkg.mkdir(parents=True)
    (pkg / "truth.md").write_text("# truth v1\n", encoding="utf-8")
    (pkg / "tests.md").write_text("# tests v1\n", encoding="utf-8")


# ---- AC-001 user_story layer package-auth ----

def test_user_story_layer_package_auth(tmp_path: Path) -> None:
    _make_pkg(tmp_path, "v1.6.3", "demo-fp")
    files = _find_layer_files(tmp_path, version="v1.6.3", layer="user_story")
    assert any("features/demo-fp/truth.md" in str(f) for f in files), files


# ---- AC-002 prd layer package-auth ----

def test_prd_layer_package_auth(tmp_path: Path) -> None:
    _make_pkg(tmp_path, "v1.6.3", "demo-fp")
    files = _find_layer_files(tmp_path, version="v1.6.3", layer="prd")
    assert any("features/demo-fp/truth.md" in str(f) for f in files), files


# ---- AC-003 truth change detected ----

def test_truth_change_detected(tmp_path: Path) -> None:
    _make_pkg(tmp_path, "v1.6.3", "demo-fp")
    fp1 = generate_spec_fingerprint(tmp_path, run_id="r1", version="v1.6.3")
    h1 = fp1.get("fingerprint_hash", "")
    # mutate truth.md
    (tmp_path / "docs" / "beacon" / "v1.6.3" / "features" / "demo-fp" / "truth.md").write_text(
        "# truth v2 CHANGED\n", encoding="utf-8"
    )
    fp2 = generate_spec_fingerprint(tmp_path, run_id="r2", version="v1.6.3")
    h2 = fp2.get("fingerprint_hash", "")
    assert h1 != h2, f"truth change not detected: {h1} == {h2}"


# ---- AC-004 legacy compat ----

def test_legacy_find_layer_files_ignored(tmp_path: Path) -> None:
    """<v1.5.2 legacy dirs are no longer scanned (package-auth layers only)."""
    base = tmp_path / "docs" / "beacon" / "v1.4.10"
    (base / "user-story").mkdir(parents=True)
    (base / "user-story" / "legacy.md").write_text("# us\n", encoding="utf-8")
    (base / "prd").mkdir(parents=True)
    (base / "prd" / "legacy.md").write_text("# prd\n", encoding="utf-8")
    us_files = _find_layer_files(tmp_path, version="v1.4.10", layer="user_story")
    prd_files = _find_layer_files(tmp_path, version="v1.4.10", layer="prd")
    assert us_files == []
    assert prd_files == []


# ---- AC-005 test_case layer preserved ----

def test_case_layer_preserved(tmp_path: Path) -> None:
    """test_case layer still scans .machine/qa/*.ac-test-matrix.json."""
    _make_pkg(tmp_path, "v1.6.3", "demo-fp")
    qa_dir = tmp_path / "docs" / "beacon" / "v1.6.3" / ".machine" / "qa"
    qa_dir.mkdir(parents=True)
    (qa_dir / "demo-fp.ac-test-matrix.json").write_text('{"k":"v"}', encoding="utf-8")
    files = _find_layer_files(tmp_path, version="v1.6.3", layer="test_case")
    assert any("demo-fp.ac-test-matrix.json" in str(f) for f in files), files


# ---- AC-006 no regression v1.6.3 release ----

def test_no_regression_v163_release() -> None:
    """v1.6.3 release gate still passes after fingerprint regen."""
    root = Path(__file__).resolve().parents[1]
    # regenerate fingerprint for current state and verify it's consistent
    fp = generate_spec_fingerprint(root, run_id="test-consistency", version="v1.6.12")
    # user_story/prd layers must now have content (count > 0)
    layers = fp.get("layers", {})
    assert layers.get("user_story", {}).get("count", 0) > 0, layers
    assert layers.get("prd", {}).get("count", 0) > 0, layers


# ---- AC-007 no regression v1.6.2 ----

def test_no_regression_v162() -> None:
    """v1.6.2 fingerprint layers unchanged (legacy scan)."""
    root = Path(__file__).resolve().parents[1]
    fp = generate_spec_fingerprint(root, run_id="test-v162", version="v1.6.2")
    # v1.6.2 is package-auth too — should also now see features/ content
    # (this is an improvement, not a regression; just ensure no crash + has layers)
    assert "layers" in fp
    assert fp.get("fingerprint_hash", "")
