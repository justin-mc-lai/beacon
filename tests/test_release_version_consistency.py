"""Release/version consistency guards for Beacon packaging."""

from __future__ import annotations

from pathlib import Path

from beacon import __version__

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def _read_pyproject() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    needle = 'version = "'
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(needle):
            return stripped[len(needle) : -1]
    raise AssertionError("pyproject.toml missing [project].version")


def test_pyproject_version_should_match_runtime_version():
    pyproject_version = _read_pyproject()
    assert pyproject_version == __version__


def test_pyproject_should_not_expose_prefixed_console_scripts():
    text = PYPROJECT.read_text(encoding="utf-8")
    assert "beacon.prefixed:main" not in text
    assert "\nbeacon-think = " not in text


def test_pyproject_should_not_ship_pytest_as_runtime_dependency():
    text = PYPROJECT.read_text(encoding="utf-8")
    project_section = text.split("[project.optional-dependencies]", 1)[0]
    assert '"pytest>=' not in project_section
    assert "[project.optional-dependencies]" in text
    assert "dev = [" in text
