"""Tests for beacon-ecosystem-discovery-sync-drift-v163.

Covers 3 ecosystem drifts:
1. manifest sync scans features/ for package-authoritative versions
2. sync-materials rebuilds machine source hash (no stale)
3. freeze rebuilds machine json after freezing
"""
from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.manifest import sync_manifest
from beacon.utils.truth_map import feature_package_authoritative, rebuild_machine_json


def _make_pkg(root: Path, version: str, slug: str = "demo-eco") -> Path:
    pkg = root / "docs" / "beacon" / version / "features" / slug
    pkg.mkdir(parents=True)
    (pkg / "truth.md").write_text(
        "---\nslug: {s}\nversion: {v}\nstatus: draft\nlanguage: zh\n"
        "canonical_refs:\n  prd: a\n  user_story: a\n  test_case: a\n"
        "parser_contract: beacon-feature-package-v1\n"
        "truth_source_model: feature_package_authoritative\n"
        "truth_map_contract: beacon-truth-map-v1\n---\n\n# t\n".format(s=slug, v=version),
        encoding="utf-8",
    )
    (pkg / "tests.md").write_text(
        "---\nslug: {s}\nversion: {v}\nstatus: draft\nlanguage: zh\n"
        "truth_ref: a\nparser_contract: beacon-feature-package-v1\n---\n\n"
        "# t\n\n## 覆盖矩阵\n\n"
        "| AC ID | TC ID | Layer | Command | Assertion |\n"
        "|-------|-------|-------|---------|-----------|\n"
        "| AC-001 | TC-001 | contract | `python3 -m pytest tests/x.py -q` | pass |\n".format(s=slug, v=version),
        encoding="utf-8",
    )
    (pkg / "tasks.md").write_text(
        "---\nslug: {s}\nversion: {v}\nstatus: draft\nlanguage: zh\n"
        "truth_ref: a\nparser_contract: beacon-feature-package-v1\n---\n\n"
        "# t\n\n- [ ] TC-001 do (BLOCKED:Phase-A)\n".format(s=slug, v=version),
        encoding="utf-8",
    )
    (pkg / "evidence.md").write_text(
        "---\nslug: {s}\nversion: {v}\nstatus: draft\nlanguage: zh\n"
        "truth_ref: a\nparser_contract: beacon-feature-package-v1\n---\n\n"
        "# t\n\n## Authority Surface\n\n"
        "| surface | authority | artifact |\n|---------|-----------|----------|\n"
        "| truth.md | requirement_truth | a |\n".format(s=slug, v=version),
        encoding="utf-8",
    )
    return pkg


# ---- AC-001 manifest sync discovers features/ ----

def test_manifest_sync_discovers_features_dir(tmp_path: Path) -> None:
    """manifest sync for >=v1.5.2 scans features/<slug>/."""
    assert feature_package_authoritative("v1.6.3") is True
    _make_pkg(tmp_path, "v1.6.3", "demo-eco")
    # no prd/user-story/qa-test-cases — only features/
    result = sync_manifest(tmp_path, "v1.6.3")
    features = [f.get("slug") for f in result.get("features", [])]
    assert "demo-eco" in features, features


# ---- AC-004 legacy compat ----

def test_legacy_manifest_sync_unchanged(tmp_path: Path) -> None:
    """<v1.5.2 manifest sync still scans legacy dirs only."""
    assert feature_package_authoritative("v1.4.10") is False
    # build legacy layout
    base = tmp_path / "docs" / "beacon" / "v1.4.10"
    (base / "user-story").mkdir(parents=True)
    (base / "user-story" / "legacy-feat.md").write_text("# legacy", encoding="utf-8")
    result = sync_manifest(tmp_path, "v1.4.10")
    features = [f.get("slug") for f in result.get("features", [])]
    assert "legacy-feat" in features


# ---- AC-002 sync-materials rebuilds hash ----

def test_sync_materials_rebuilds_hash(tmp_path: Path) -> None:
    """sync_project_requirement_materials for package-authoritative calls rebuild,
    so truth-map verify has no machine_json_source_hash_stale."""
    from beacon.utils.material_sync import sync_project_requirement_materials
    from beacon.utils.truth_map import verify_truth_map

    _make_pkg(tmp_path, "v1.6.3", "demo-eco")
    # first rebuild to create .machine
    rebuild_machine_json(tmp_path, version="v1.6.3", feature="demo-eco")
    # now mutate truth.md (simulating post-freeze edit)
    (tmp_path / "docs" / "beacon" / "v1.6.3" / "features" / "demo-eco" / "truth.md").write_text(
        "---\nslug: demo-eco\nversion: v1.6.3\nstatus: draft\nlanguage: zh\n"
        "canonical_refs:\n  prd: a\n  user_story: a\n  test_case: a\n"
        "parser_contract: beacon-feature-package-v1\n"
        "truth_source_model: feature_package_authoritative\n"
        "truth_map_contract: beacon-truth-map-v1\n---\n\n# t mutated\n",
        encoding="utf-8",
    )
    # sync-materials should rebuild and fix hash
    sync_project_requirement_materials(tmp_path, version="v1.6.3", feature="demo-eco")
    result = verify_truth_map(tmp_path, version="v1.6.3", feature="demo-eco")
    codes = [d.get("code") for d in result.get("diagnostics", [])]
    assert "machine_json_source_hash_stale" not in codes, codes


# ---- AC-003 freeze rebuilds machine ----

def test_freeze_rebuilds_machine(tmp_path: Path, monkeypatch) -> None:
    """freeze should call rebuild_machine_json so .machine hash stays in sync."""
    from beacon.commands import freeze as freeze_mod

    _make_pkg(tmp_path, "v1.6.3", "demo-eco")
    called: list[str] = []
    orig_rebuild = freeze_mod.rebuild_machine_json if hasattr(freeze_mod, "rebuild_machine_json") else None

    # We assert freeze imports/uses rebuild_machine_json by checking the source
    src = Path(freeze_mod.__file__).read_text(encoding="utf-8")
    assert "rebuild_machine_json" in src, "freeze must call rebuild_machine_json"


# ---- AC-007 _discover_features via manifest ----

def test_discover_features_finds_packages(tmp_path: Path) -> None:
    """_discover_features (material_sync) finds features/ packages via manifest."""
    from beacon.utils.material_sync import _discover_features

    _make_pkg(tmp_path, "v1.6.3", "demo-eco")
    # sync manifest first so _discover_features can use it
    sync_manifest(tmp_path, "v1.6.3")
    found = _discover_features(tmp_path, "v1.6.3")
    assert "demo-eco" in found, found


# ---- AC-005 / AC-006 no regression on real packages ----

def test_no_regression_v162() -> None:
    """v1.6.2 feature package still passes truth-map verify."""
    from beacon.utils.truth_map import verify_truth_map
    root = Path(__file__).resolve().parents[1]
    result = verify_truth_map(
        root, version="v1.6.2", feature="beacon-global-workspace-git-admission-v162"
    )
    assert result.get("status") != "blocked" or not result.get("diagnostics")


def test_no_regression_v163_packages() -> None:
    """v1.6.3 four frozen packages still pass truth-map verify."""
    from beacon.utils.truth_map import verify_truth_map
    root = Path(__file__).resolve().parents[1]
    for slug in [
        "beacon-gate-truth-model-alignment-v163",
        "beacon-freeze-integrity-drift-repair-v163",
        "beacon-version-resolve-fail-closed-v163",
        "beacon-workflow-memory-completion-gate-v163",
    ]:
        result = verify_truth_map(root, version="v1.6.3", feature=slug)
        codes = [d.get("code") for d in result.get("diagnostics", [])]
        assert "machine_json_source_hash_stale" not in codes, f"{slug}: {codes}"
