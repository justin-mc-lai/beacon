from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path, version: str = "v1.3.4") -> None:
    base = root / "docs" / "beacon" / version / "execution"
    base.mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / version / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "index.md").write_text("# Execution Index\n", encoding="utf-8")


def test_v134_implement_status_json_should_return_structured_missing_payload(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    result = _invoke(
        [
            "implement",
            "status",
            "demo-feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.4",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "missing"
    assert payload["reason_code"] == "implementation_run_not_found"
    assert payload["feature"] == "demo-feature"
    assert payload["feature_slug"] == "demo-feature"
    assert payload["version"] == "v1.3.4"
