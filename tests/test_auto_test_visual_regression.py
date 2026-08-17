from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.auto_test import _resolve_layers
from beacon.main import app


runner = CliRunner()


def _write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


def test_scope_all_should_not_include_visual_but_full_should():
    assert _resolve_layers("all") == ["ui", "api-curl", "unit", "smoke"]
    assert _resolve_layers("full") == ["ui", "api-curl", "unit", "smoke", "visual"]


def test_auto_test_visual_compare_only_pass_and_fail(tmp_path: Path):
    baseline = tmp_path / "snapshots" / "baseline"
    current = tmp_path / "snapshots" / "current"

    _write_bytes(baseline / "home.png", b"same-image")
    _write_bytes(current / "home.png", b"same-image")

    first = runner.invoke(
        app,
        [
            "auto-test",
            "create",
            "visual",
            "--project",
            str(tmp_path),
            "--visual-baseline-dir",
            str(baseline),
            "--visual-current-dir",
            str(current),
            "--visual-threshold",
            "0",
        ],
    )
    assert first.exit_code == 0
    first_payload = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    assert first_payload["status"] == "passed"
    assert first_payload["selected_layers"] == ["visual"]
    assert first_payload["execution"]["layers"][0]["status"] == "passed"

    _write_bytes(current / "home.png", b"changed-image")
    second = runner.invoke(
        app,
        [
            "auto-test",
            "create",
            "visual",
            "--project",
            str(tmp_path),
            "--visual-baseline-dir",
            str(baseline),
            "--visual-current-dir",
            str(current),
            "--visual-threshold",
            "0",
        ],
    )
    assert second.exit_code == 0
    second_payload = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    assert second_payload["status"] == "failed"
    layer = second_payload["execution"]["layers"][0]
    assert layer["layer"] == "visual"
    assert layer["status"] == "failed"
    assert layer["visual_compare"]["mismatch_count"] >= 1
