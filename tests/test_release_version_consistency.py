"""Release/version consistency guards for Beacon packaging."""

from __future__ import annotations

import re
from pathlib import Path

from beacon import __version__
from beacon.prefixed import SUPPORTED_SUBCOMMANDS


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def _read_pyproject() -> tuple[str, set[str]]:
    text = PYPROJECT.read_text(encoding="utf-8")

    version_match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    assert version_match, "pyproject.toml missing [project].version"
    version = version_match.group(1)

    script_keys = set(
        re.findall(
            r'^(beacon-[a-z0-9\-]+)\s*=\s*"beacon\.prefixed:main"',
            text,
            flags=re.MULTILINE,
        )
    )
    return version, script_keys


def test_pyproject_version_should_match_runtime_version():
    pyproject_version, _ = _read_pyproject()
    assert pyproject_version == __version__


def test_prefixed_scripts_should_cover_all_supported_subcommands():
    _, script_keys = _read_pyproject()
    expected = {f"beacon-{name}" for name in SUPPORTED_SUBCOMMANDS}

    missing = sorted(expected - script_keys)
    extra = sorted(script_keys - expected)

    assert not missing, f"missing prefixed script entries: {missing}"
    assert not extra, f"unexpected prefixed script entries: {extra}"

