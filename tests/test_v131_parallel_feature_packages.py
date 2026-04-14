from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
ROOT = Path(__file__).resolve().parents[1]
VERSION = "v1.3.1"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_v131_should_allow_multiple_parallel_feature_packages_in_same_version(tmp_path: Path):
    features = ["Feature Alpha", "Feature Beta"]

    for feature in features:
        us = _invoke(["user-story", "create", feature, "--project", str(tmp_path), "--version", VERSION])
        assert us.exit_code == 0
        prd = _invoke(["prd", "create", feature, "--project", str(tmp_path), "--version", VERSION])
        assert prd.exit_code == 0
        tc = _invoke(["test-case", "create", feature, "--project", str(tmp_path), "--version", VERSION])
        assert tc.exit_code == 0

    for slug in ("feature-alpha", "feature-beta"):
        assert (tmp_path / "docs" / "beacon" / VERSION / "user-story" / f"{slug}.md").exists()
        assert (tmp_path / "docs" / "beacon" / VERSION / "prd" / f"{slug}.md").exists()
        assert (tmp_path / "docs" / "beacon" / VERSION / "qa" / "test-cases" / f"{slug}.md").exists()
        assert (tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{slug}.ac-test-matrix.json").exists()


def test_v131_docs_should_lock_parallel_feature_package_and_change_contract():
    required_files = [
        ROOT / "docs" / "beacon" / VERSION / "execution" / "parallel-feature-package-contract.md",
        ROOT / "docs" / "beacon" / VERSION / "execution" / "change-document-contract.md",
        ROOT / "docs" / "beacon" / VERSION / "execution" / "version-evolution-blueprint.md",
        ROOT / "docs" / "beacon" / VERSION / "change" / "v1.3.1.md",
    ]
    for path in required_files:
        assert path.exists(), f"missing v1.3.1 contract artifact: {path}"

    summary = (ROOT / "docs" / "beacon" / VERSION / "SUMMARY.md").read_text(encoding="utf-8")
    index_doc = (ROOT / "docs" / "beacon" / VERSION / "execution" / "index.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs" / "beacon" / VERSION / "execution" / "architecture-blueprint.md").read_text(encoding="utf-8")
    boundaries = (ROOT / "docs" / "beacon" / VERSION / "execution" / "boundaries.md").read_text(encoding="utf-8")
    release_doc = (ROOT / "docs" / "beacon" / VERSION / "release" / "v1.3.1.md").read_text(encoding="utf-8")

    assert "./execution/parallel-feature-package-contract.md" in summary
    assert "./execution/change-document-contract.md" in summary
    assert "./execution/version-evolution-blueprint.md" in summary
    assert "./parallel-feature-package-contract.md" in index_doc
    assert "./change-document-contract.md" in index_doc
    assert "./version-evolution-blueprint.md" in index_doc
    assert "feature package" in architecture.lower()
    assert "feature-package boundary" in boundaries.lower()
    assert "change/v1.3.1.md" in release_doc
