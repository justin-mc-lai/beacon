from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.material_audit import build_requirement_package_gate
from beacon.utils.version_package_upgrade import registered_upgrade_steps, upgrade_version_package


runner = CliRunner()
VERSION = "v9.9.9"


def _seed_min_version_line(root: Path) -> None:
    base = root / "docs" / "beacon" / VERSION
    base.mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text(f"# Summary {VERSION}\n", encoding="utf-8")
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "VERSION").write_text(f"{VERSION}\n", encoding="utf-8")


def test_upgrade_package_writes_release_stub(tmp_path: Path):
    _seed_min_version_line(tmp_path)
    release_path = tmp_path / "docs" / "beacon" / VERSION / "release" / f"{VERSION}.md"
    assert not release_path.exists()

    result = upgrade_version_package(tmp_path, version=VERSION, apply=True)
    assert result["applied"] is True
    assert release_path.exists()
    assert f"# Release: {VERSION}" in release_path.read_text(encoding="utf-8")


def test_registered_upgrade_steps_include_release_stub():
    steps = [item["step"] for item in registered_upgrade_steps()]
    assert "v1.1.13-release-stub" in steps


def test_package_gate_routes_upgrade_package(tmp_path: Path):
    _seed_min_version_line(tmp_path)
    gate = build_requirement_package_gate(tmp_path, version=VERSION, feature="", strict=True)
    assert gate["status"] == "blocked"
    assert gate["remediation_mode"] == "upgrade-package"
    assert gate["recommended_action"] == "doctor-upgrade-package"
    assert "upgrade-package" in gate["recommended_command"]


def test_package_gate_repair_commands(tmp_path: Path):
    _seed_min_version_line(tmp_path)
    gate = build_requirement_package_gate(tmp_path, version=VERSION, feature="", strict=True)
    repair = gate.get("repair_commands")
    assert isinstance(repair, list)
    assert len(repair) >= 2
    assert repair[0] == gate["recommended_command"]
    assert "verify-materials" in repair[1]


def test_doctor_upgrade_package_cli_writes_release_stub(tmp_path: Path):
    _seed_min_version_line(tmp_path)
    result = runner.invoke(
        app,
        ["doctor", "upgrade-package", "--project-root", str(tmp_path), "--version", VERSION, "--json"],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    release_path = tmp_path / "docs" / "beacon" / VERSION / "release" / f"{VERSION}.md"
    assert release_path.exists()
