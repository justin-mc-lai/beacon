"""Import path conflict guards for mixed beacon roots."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import beacon
from beacon import main as beacon_main
from beacon import __toolkit_version__


ROOT = Path(__file__).resolve().parents[1]


def test_pin_beacon_import_path_should_force_current_package_path():
    package_dir = Path(beacon_main.__file__).resolve().parent
    original_path = list(getattr(beacon, "__path__", []))
    try:
        beacon.__path__ = ["/tmp/fake-skill-beacon", *original_path]  # type: ignore[attr-defined]
        beacon_main._pin_beacon_import_path()
        assert list(beacon.__path__) == [str(package_dir)]  # type: ignore[attr-defined]
    finally:
        beacon.__path__ = original_path  # type: ignore[attr-defined]


def test_import_beacon_main_should_ignore_polluted_package_path(tmp_path: Path):
    fake_pkg_root = tmp_path / "fake-beacon-path"
    fake_commands = fake_pkg_root / "commands"
    fake_commands.mkdir(parents=True, exist_ok=True)
    (fake_commands / "__init__.py").write_text("", encoding="utf-8")
    (fake_commands / "version.py").write_text(
        "raise RuntimeError('polluted beacon.commands.version imported')\n",
        encoding="utf-8",
    )

    code = f"""
import beacon
beacon.__path__ = [r\"{fake_pkg_root}\", *list(beacon.__path__)]
import beacon.main
print("import-ok")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "import-ok" in result.stdout


def test_beacon_cli_should_work_when_pythonpath_has_conflicting_skill_root(tmp_path: Path):
    conflict_root = tmp_path / ".claude" / "skills" / "beacon"
    fake_pkg = conflict_root / "beacon"
    fake_pkg.mkdir(parents=True, exist_ok=True)
    (fake_pkg / "__init__.py").write_text("__version__='0.0.0-bad'\n", encoding="utf-8")
    (fake_pkg / "main.py").write_text("raise RuntimeError('wrong beacon imported')\n", encoding="utf-8")

    script = ROOT / "beacon-cli"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(conflict_root)
    result = subprocess.run(
        [str(script), "--version"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert f"Beacon CLI {__toolkit_version__}" in result.stdout
