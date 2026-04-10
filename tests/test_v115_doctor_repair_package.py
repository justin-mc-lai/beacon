from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_v115_layout(root: Path) -> None:
    base = root / "docs" / "beacon" / "v1.1.5"
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "release" / "v1.1.5.md").write_text("# Release\n", encoding="utf-8")
    for filename in (
        "config.json",
        "source.json",
        "git-alignment.json",
        "change-impact.json",
        "delivery-manifest.json",
        "terminal.json",
        "implementation-summary-machine-feature.json",
    ):
        (base / "execution" / filename).write_text(json.dumps({"name": filename}), encoding="utf-8")
    (base / "qa" / "test-cases" / "machine-feature.md").write_text("# Test\n", encoding="utf-8")
    (base / "qa" / "test-cases" / "machine-feature.ac-test-matrix.json").write_text(
        json.dumps({"entries": []}),
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / "machine-feature.qa9-matrix.json").write_text(
        json.dumps({"entries": []}),
        encoding="utf-8",
    )


def test_doctor_repair_package_should_move_machine_artifacts_and_create_indexes(tmp_path: Path):
    _seed_v115_layout(tmp_path)
    result = _invoke(["doctor", "repair-package", "--project-root", str(tmp_path), "--version", "v1.1.5", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"

    machine_exec = tmp_path / "docs" / "beacon" / "v1.1.5" / ".machine" / "execution"
    assert (machine_exec / "config.json").exists()
    assert (machine_exec / "terminal.json").exists()
    assert (machine_exec / "implementation-summary-machine-feature.json").exists()
    assert not (tmp_path / "docs" / "beacon" / "v1.1.5" / "execution" / "config.json").exists()
    assert not (tmp_path / "docs" / "beacon" / "v1.1.5" / "execution" / "implementation-summary-machine-feature.json").exists()
    assert not (tmp_path / "docs" / "beacon" / "v1.1.5" / "qa" / "test-cases" / "machine-feature.ac-test-matrix.json").exists()
    assert (tmp_path / "docs" / "beacon" / "v1.1.5" / ".machine" / "qa" / "machine-feature.ac-test-matrix.json").exists()
    assert (tmp_path / "docs" / "beacon" / "v1.1.5" / "execution" / "index.md").exists()
    assert (tmp_path / "docs" / "beacon" / "v1.1.5" / "qa" / "test-cases" / "index.md").exists()


def test_doctor_repair_package_should_create_eval_lab_skeleton(tmp_path: Path):
    _seed_v115_layout(tmp_path)
    result = _invoke(["doctor", "repair-package", "--project-root", str(tmp_path), "--version", "v1.1.5", "--json"])
    assert result.exit_code == 0, result.stdout
    eval_root = tmp_path / ".beacon" / "state" / "eval-lab"
    assert (eval_root / "experiments").is_dir()
    assert (eval_root / "scores").is_dir()
    assert (eval_root / "drift-audit").is_dir()
    assert (eval_root / "keep-discard-log.jsonl").exists()
    benchmark = json.loads((eval_root / "benchmark-surface.json").read_text(encoding="utf-8"))
    assert "delivery_closure" in benchmark["benchmarks"]


def test_doctor_fix_should_apply_v115_package_repair_for_latest_docs(tmp_path: Path):
    _seed_v115_layout(tmp_path)
    (tmp_path / "docs" / "beacon" / "v1.1.4" / "release").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "v1.1.4" / "release" / "v1.1.4.md").write_text("# Release\n", encoding="utf-8")
    result = _invoke(["doctor", "--fix", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "docs" / "beacon" / "v1.1.5" / ".machine" / "execution" / "config.json").exists()
