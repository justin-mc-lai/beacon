from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_release_repo(root: Path) -> None:
    (root / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "beacon" / "__init__.py").write_text(
        '__version__ = "1.1.4"\n__toolkit_version__ = "v1.1.4"\n',
        encoding="utf-8",
    )
    for version in ("v1.1.4", "v1.1.5"):
        base = root / "docs" / "beacon" / version
        (base / "release").mkdir(parents=True, exist_ok=True)
        (base / "release" / f"{version}.md").write_text(f"# Release {version}\n", encoding="utf-8")


def test_init_should_create_v115_machine_dirs_indexes_and_eval_lab(tmp_path: Path):
    _seed_release_repo(tmp_path)
    result = _invoke(["init", "--project-root", str(tmp_path), "--version", "v1.1.5", "--apply"])
    assert result.exit_code == 0, result.stdout
    docs_root = tmp_path / "docs" / "beacon" / "v1.1.5"
    assert (docs_root / ".machine" / "execution").is_dir()
    assert (docs_root / ".machine" / "qa").is_dir()
    assert (docs_root / "execution" / "index.md").exists()
    assert (docs_root / "qa" / "test-cases" / "index.md").exists()
    assert (tmp_path / ".beacon" / "state" / "eval-lab" / "keep-discard-log.jsonl").exists()


def test_status_should_report_v115_machine_root(tmp_path: Path):
    _seed_release_repo(tmp_path)
    result = _invoke(["status", "--project-root", str(tmp_path), "--version", "v1.1.5"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    source = payload["source_of_truth"]
    version_context = payload["version_context"]
    assert source["root"] == "docs/beacon/v1.1.5"
    assert source["machine_root"] == "docs/beacon/v1.1.5/.machine"
    assert version_context["docs_version"] == "v1.1.5"
    assert version_context["runtime_version"] == "v1.1.10"
