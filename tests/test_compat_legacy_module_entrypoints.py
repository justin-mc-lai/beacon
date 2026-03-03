"""Compatibility tests for legacy `python -m beacon.<subcommand>` entrypoints."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_legacy_python_module_think_should_still_work(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "beacon.think",
            "start",
            "回归兼容测试",
            "--project",
            str(tmp_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Starting think session" in result.stdout
