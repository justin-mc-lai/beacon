from __future__ import annotations

import json
import shutil
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_prototype_contract
from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _copy_real_v136_sources(tmp_path: Path) -> str:
    version = "v1.3.6"
    feature = "beacon-v1.3.6-visual-management-console-and-material-viewer"
    targets = {
        ROOT / "docs" / "beacon" / version / "user-story" / "beacon-v1.3.6-visual-management-console-and-material-viewer.md":
            tmp_path / "docs" / "beacon" / version / "user-story" / "beacon-v1.3.6-visual-management-console-and-material-viewer.md",
        ROOT / "docs" / "beacon" / version / "prd" / "beacon-v1-3-6-visual-management-console-and-material-viewer.md":
            tmp_path / "docs" / "beacon" / version / "prd" / "beacon-v1-3-6-visual-management-console-and-material-viewer.md",
        ROOT / "docs" / "beacon" / version / "qa" / "test-cases" / "beacon-v1.3.6-visual-management-console-and-material-viewer.md":
            tmp_path / "docs" / "beacon" / version / "qa" / "test-cases" / "beacon-v1.3.6-visual-management-console-and-material-viewer.md",
    }
    for source, target in targets.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return feature


def test_v135_prototype_should_freeze_real_v136_management_console_wireframe(tmp_path: Path):
    feature = _copy_real_v136_sources(tmp_path)
    version = "v1.3.6"

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    create_payload = json.loads(create.stdout)
    assert create_payload["prototype_mode"] == "wireframe"

    bind = _invoke(["prototype", "bind", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert bind.exit_code == 0, bind.stdout

    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    review_payload = json.loads(review.stdout)
    assert review_payload["overall_status"] == "pass"

    freeze = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert freeze.exit_code == 0, freeze.stdout
    assert json.loads(freeze.stdout)["status"] == "frozen"

    status = _invoke(["prototype", "status", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert status.exit_code == 0, status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["gate_ready"] is True

    root = tmp_path / "docs" / "beacon" / version / "prototype" / "beacon-v1-3-6-visual-management-console-and-material-viewer"
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    expected_pages = {
        "home",
        "management-overview",
        "project-detail",
        "runtime-center",
        "recovery-diagnostics",
        "material-viewer",
        "material-document-detail",
    }
    assert expected_pages.issubset(set(plan["required_pages"]))
    for page_id in expected_pages:
        assert (root / "pages" / f"{page_id}.md").exists(), page_id

    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version=version)
    assert issues == []
