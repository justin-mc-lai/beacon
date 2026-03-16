"""Prototype command contracts for v1.1.2."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app

runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_sources(tmp_path: Path, feature: str, version: str = "v1.1.2") -> None:
    result = _invoke(["user-story", "create", feature, "--project", str(tmp_path), "--version", version])
    assert result.exit_code == 0
    result = _invoke(["prd", "create", feature, "--project", str(tmp_path), "--version", version])
    assert result.exit_code == 0


def test_prototype_help():
    result = _invoke(["prototype", "--help"])
    assert result.exit_code == 0
    assert "Generate and manage static UI prototypes" in result.stdout


def test_prototype_create_generates_static_html(tmp_path: Path):
    feature = "Login Feature"
    _prepare_sources(tmp_path, feature)
    result = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    assert result.exit_code == 0
    html_path = tmp_path / "docs" / "beacon" / "v1.1.2" / "prototype" / "login-feature" / "index.html"
    assert html_path.exists()
    content = html_path.read_text(encoding="utf-8")
    assert "Bootstrap" in content
    assert "Reference Prototype" in content
    assert "prototypeModal" in content
    assert "prototypeDrawer" in content


def test_prototype_outputs_only_under_docs_beacon(tmp_path: Path):
    feature = "Orders Dashboard"
    _prepare_sources(tmp_path, feature)
    result = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["paths"]["index_html"].startswith("docs/beacon/v1.1.2/prototype/")
    assert "docs/product" not in result.stdout


def test_prototype_manifest_and_source_map_contract(tmp_path: Path):
    feature = "Profile Center"
    _prepare_sources(tmp_path, feature)
    result = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    assert result.exit_code == 0
    root = tmp_path / "docs" / "beacon" / "v1.1.2" / "prototype" / "profile-center"
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    source_map = json.loads((root / "source-map.json").read_text(encoding="utf-8"))
    freeze = json.loads((root / "freeze.json").read_text(encoding="utf-8"))
    assert manifest["ui_kit"] == "bootstrap-5.3.x"
    assert manifest["status"] == "draft"
    assert source_map["derived_from"] == ["user-story", "prd"]
    assert "user-story" in source_map["source_fingerprints"]
    assert freeze["status"] == "draft"


def test_prototype_preview_prints_local_entry(tmp_path: Path):
    feature = "Billing Portal"
    _prepare_sources(tmp_path, feature)
    _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    result = _invoke(["prototype", "preview", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    assert result.exit_code == 0
    assert "file://" in result.stdout
    assert "python3 -m http.server 4173" in result.stdout


def test_prototype_freeze_and_status_stale_detection(tmp_path: Path):
    feature = "Settings Screen"
    _prepare_sources(tmp_path, feature)
    _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    result = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", "v1.1.2", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "frozen"

    story = tmp_path / "docs" / "beacon" / "v1.1.2" / "user-story" / "settings-screen.md"
    story.write_text(story.read_text(encoding="utf-8") + "\n- [ ] AC-extra\n", encoding="utf-8")

    result = _invoke(["prototype", "status", feature, "--project", str(tmp_path), "--version", "v1.1.2", "--json"])
    assert result.exit_code == 0
    status_payload = json.loads(result.stdout)
    assert status_payload["status"] == "stale"
    assert status_payload["stale"] is True


def test_prototype_list_lists_existing_prototypes(tmp_path: Path):
    feature = "Risk Console"
    _prepare_sources(tmp_path, feature)
    _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    result = _invoke(["prototype", "list", "--project", str(tmp_path), "--version", "v1.1.2"])
    assert result.exit_code == 0
    assert "risk-console" in result.stdout


def test_prototype_create_requires_source_docs(tmp_path: Path):
    result = _invoke(["prototype", "create", "Missing Feature", "--project", str(tmp_path), "--version", "v1.1.2"])
    assert result.exit_code == 2
    assert "Missing source docs" in result.stdout or "Missing source docs" in result.stderr
