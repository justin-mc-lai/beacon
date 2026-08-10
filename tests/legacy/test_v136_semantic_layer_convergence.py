from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_semantic_contract
from beacon.main import app
from beacon.utils.llm_loop import _sanitize_stage
from beacon.utils.project_skills import load_skill_registry


runner = CliRunner()
ROOT = Path(__file__).resolve().parents[1]
VERSION = "v1.3.6"
FEATURE = "beacon-v1.3.6-visual-management-console-and-material-viewer"
FEATURE_SLUG = "beacon-v1-3-6-visual-management-console-and-material-viewer"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Beacon Tests"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "beacon-tests@example.com"], cwd=root, check=True, capture_output=True, text=True)
    (root / ".gitkeep").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "switch", "-c", f"beacon/{VERSION}"], cwd=root, check=True, capture_output=True, text=True)


def _seed_base(root: Path) -> None:
    if not (root / ".git").exists():
        _init_git_repo(root)
    (root / "AGENTS.md").write_text(
        "# AGENTS.md\n\n- Use docs/beacon/global-boundaries.md as the canonical Beacon-wide global constraint source.\n",
        encoding="utf-8",
    )
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    base = root / "docs" / "beacon" / VERSION
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text(f"# {VERSION}\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution Index\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture Blueprint\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text(f"# Release {VERSION}\n", encoding="utf-8")


def _copy_real_v136_sources(tmp_path: Path) -> None:
    _seed_base(tmp_path)
    targets = {
        ROOT / "docs" / "beacon" / VERSION / "user-story" / f"{FEATURE}.md":
            tmp_path / "docs" / "beacon" / VERSION / "user-story" / f"{FEATURE}.md",
        ROOT / "docs" / "beacon" / VERSION / "prd" / f"{FEATURE_SLUG}.md":
            tmp_path / "docs" / "beacon" / VERSION / "prd" / f"{FEATURE_SLUG}.md",
        ROOT / "docs" / "beacon" / VERSION / "qa" / "test-cases" / f"{FEATURE}.md":
            tmp_path / "docs" / "beacon" / VERSION / "qa" / "test-cases" / f"{FEATURE}.md",
    }
    for source, target in targets.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    shutil.copy2(
        tmp_path / "docs" / "beacon" / VERSION / "prd" / f"{FEATURE_SLUG}.md",
        tmp_path / "docs" / "beacon" / VERSION / "prd" / f"{FEATURE}.md",
    )
    (
        tmp_path / "docs" / "beacon" / VERSION / "qa" / "test-cases" / f"{FEATURE}.ac-test-matrix.json"
    ).write_text('{"entries":[]}\n', encoding="utf-8")


def test_v136_project_skill_registry_should_include_default_taste_bridge(tmp_path: Path) -> None:
    registry = load_skill_registry(tmp_path)
    payload = registry["taste-skill"]
    assert payload["repo"] == "https://github.com/Leonxlnx/taste-skill"
    assert payload["supported_stages"] == ["prototype", "implement"]
    assert "taste-design" in payload["capabilities"]


def test_v136_prototype_should_materialize_semantic_layer_before_freeze(tmp_path: Path) -> None:
    _copy_real_v136_sources(tmp_path)

    result = _invoke(
        [
            "prototype",
            "create",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    semantic_layer = payload["semantic_layer"]
    contract_path = tmp_path / semantic_layer["artifacts"]["semantic_contract"]
    dictionary_path = tmp_path / semantic_layer["artifacts"]["semantic_dictionary"]
    usage_path = tmp_path / semantic_layer["artifacts"]["semantic_usage_guidelines"]
    review_path = tmp_path / semantic_layer["artifacts"]["semantic_review"]

    assert contract_path.exists()
    assert dictionary_path.exists()
    assert usage_path.exists()
    assert review_path.exists()

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    labels = [item["label"] for item in contract["official_language"]["page_names"]]
    assert any(label in {"管理端看板", "物料查看器", "文档查看器"} for label in labels)
    assert contract["default_design_bridge"]["skill_id"] == "taste-skill"

    plan_path = tmp_path / payload["paths"]["prototype_plan"]
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan["semantic_layer"]["artifacts"]["semantic_contract"] == semantic_layer["artifacts"]["semantic_contract"]
    assert plan["contract"]["semantic_governance_required"] is True


def test_v136_implement_dry_run_should_reuse_semantic_layer_and_default_taste_bridge(tmp_path: Path) -> None:
    _copy_real_v136_sources(tmp_path)
    (tmp_path / "beacon.config.yaml").write_text(
        (
            "implementation:\n"
            "  default_runner: fake-handoff\n"
            "  runners:\n"
            "    fake-handoff:\n"
            "      adapter_type: handoff\n"
            "      runtime_family: external-handoff\n"
            "      request_file: .beacon/implement/{run_id}/request.md\n"
            "      result_file: .beacon/implement/{run_id}/result.json\n"
        ),
        encoding="utf-8",
    )

    freeze = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    assert freeze.exit_code == 0, freeze.stdout
    sync = _invoke(
        [
            "doctor",
            "sync-technical-review-contract",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--revision-id",
            "R1",
            "--review-status",
            "approved",
            "--approved-by",
            "test",
            "--reviewed-at",
            "2026-04-22",
            "--json",
        ]
    )
    assert sync.exit_code == 0, sync.stdout
    plan = _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert plan.exit_code == 0, plan.stdout

    result = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--mode",
            "team",
            "--runner",
            "fake-handoff",
            "--dry-run",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "dry_run"

    request_path = tmp_path / payload["request_path"]
    request_payload = json.loads(request_path.read_text(encoding="utf-8"))
    semantic_layer = request_payload["semantic_layer"]
    assert semantic_layer["default_design_bridge"]["skill_id"] == "taste-skill"
    assert "semantic-contract.json" in request_payload["task_prompt"]
    assert "taste-skill" in request_payload["task_prompt"]
    assert not (tmp_path / semantic_layer["artifacts"]["semantic_contract"]).exists()


def test_v136_llm_loop_should_normalize_canonical_and_legacy_stage_vocabulary() -> None:
    assert _sanitize_stage("prototype", "none") == "prototype"
    assert _sanitize_stage("implementation", "none") == "implement"
    assert _sanitize_stage("review", "none") == "qa"
    assert _sanitize_stage("delivery", "none") == "release"


def test_v136_gate_release_should_block_when_semantic_contract_missing(tmp_path: Path) -> None:
    _copy_real_v136_sources(tmp_path)
    create = _invoke(["prototype", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert create.exit_code == 0, create.stdout
    payload = json.loads(create.stdout)
    semantic_contract = tmp_path / payload["semantic_layer"]["artifacts"]["semantic_contract"]
    semantic_contract.unlink()

    issues = check_semantic_contract(tmp_path, GateMode.STRICT, "release", version=VERSION)
    reason_codes = {item["reason_code"] for item in issues}
    assert "semantic_contract_missing" in reason_codes


def test_v136_gate_release_should_block_when_default_taste_bridge_drifts(tmp_path: Path) -> None:
    _copy_real_v136_sources(tmp_path)
    create = _invoke(["prototype", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert create.exit_code == 0, create.stdout
    payload = json.loads(create.stdout)
    semantic_contract = tmp_path / payload["semantic_layer"]["artifacts"]["semantic_contract"]
    contract_payload = json.loads(semantic_contract.read_text(encoding="utf-8"))
    contract_payload["default_design_bridge"]["repo"] = "https://example.com/not-official"
    semantic_contract.write_text(json.dumps(contract_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    issues = check_semantic_contract(tmp_path, GateMode.STRICT, "release", version=VERSION)
    reason_codes = {item["reason_code"] for item in issues}
    assert "semantic_default_taste_bridge_drift" in reason_codes


def test_v136_status_should_emit_semantic_summary(tmp_path: Path) -> None:
    _copy_real_v136_sources(tmp_path)
    create = _invoke(["prototype", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert create.exit_code == 0, create.stdout

    status = _invoke(["status", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE])
    assert status.exit_code == 0, status.stdout
    payload = json.loads(status.stdout)
    assert payload["semantic"]["status"] == "pass"
    assert payload["semantic"]["details"]["default_design_bridge"]["skill_id"] == "taste-skill"
