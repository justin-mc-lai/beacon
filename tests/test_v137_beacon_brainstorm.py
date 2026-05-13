from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.command_catalog import DEFAULT_USER_SURFACE, LABS_COMMANDS, SUPPORTED_SUBCOMMANDS
from beacon.main import app
from beacon.utils.delivery_baseline import implementation_delivery_baseline_path
from beacon.utils.implementation_plan import build_implementation_plan_gate_payload, implementation_plan_json_path
from beacon.utils.runtime import write_json


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_v137_docs(root: Path) -> None:
    version_root = root / "docs" / "beacon" / "v1.3.7"
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n- frozen truth is canonical\n", encoding="utf-8")
    (version_root / "execution").mkdir(parents=True, exist_ok=True)
    (version_root / "prd").mkdir(parents=True, exist_ok=True)
    (version_root / "user-story").mkdir(parents=True, exist_ok=True)
    (version_root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (version_root / "SUMMARY.md").write_text("# v1.3.7\n", encoding="utf-8")
    (version_root / "execution" / "index.md").write_text("# Index\n", encoding="utf-8")
    (version_root / "execution" / "architecture-blueprint.md").write_text("# Architecture\nbaseline envelope\n", encoding="utf-8")
    slug = "beacon-v1.3.7-beacon-brainstorm-built-in-convergence-and-evolution-thinking"
    (version_root / "prd" / f"{slug}.md").write_text("# PRD\nFR-001 brainstorm convergence\n", encoding="utf-8")
    (version_root / "user-story" / f"{slug}.md").write_text("# User Story\nAC-001 converge requirements\n", encoding="utf-8")
    (version_root / "qa" / "test-cases" / f"{slug}.md").write_text("# Test Case\nTC-001 run brainstorm\n", encoding="utf-8")


def _seed_project_metadata(root: Path, *, version: str, service: str, branch: str) -> None:
    write_json(
        root / ".beacon" / "metadata" / "project-version-metadata.json",
        {
            "schema_version": "1.0",
            "project_root": str(root.resolve()),
            "global_project_metadata": {
                "project_root": str(root.resolve()),
                "topology_kind": "monorepo",
                "default_execution_service": service,
                "service_bindings": [
                    {
                        "service_key": service,
                        "repo_root": str((root / "services" / service).resolve()),
                        "repo_root_relative": f"services/{service}",
                        "role": "service",
                        "writable": True,
                        "worktree_path_policy": "follow-repo-root",
                    }
                ],
            },
            "version_scoped_metadata": {
                version: {
                    "participating_services": [service],
                    "per_service_canonical_branch": {service: branch},
                    "branch_guard_mode": "strict",
                    "validation_state": "verified",
                }
            },
            "transaction": {},
        },
    )


def test_v137_beacon_brainstorm_should_remain_labs_sidecar() -> None:
    assert "brainstorm" in LABS_COMMANDS
    assert "brainstorm" in SUPPORTED_SUBCOMMANDS
    assert "brainstorm" not in DEFAULT_USER_SURFACE
    skill = Path(__file__).resolve().parents[1] / "skills" / "beacon" / "beacon-brainstorm" / "SKILL.md"
    assert skill.exists()
    text = skill.read_text(encoding="utf-8")
    assert "name: beacon-brainstorm" in text
    assert "not a new main lifecycle stage" in text


def test_v137_architecture_blueprint_should_define_layered_delivery_model() -> None:
    text = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "beacon"
        / "v1.3.7"
        / "execution"
        / "architecture-blueprint.md"
    ).read_text(encoding="utf-8")

    for snippet in (
        "## Blueprint Goal",
        "## Runtime Position",
        "## System Boundary",
        "## Layered Architecture",
        "### 1. Frozen Truth Layer",
        "### 2. Canonical Baseline Layer",
        "### 6. Brainstorm Sidecar Layer",
        "## Anti-Drift Contract",
        "runtime line: `v1.3.7`",
        "delivery docs line: `v1.3.7`",
        "canonical implementation delivery baseline envelope is the only implementation projection truth",
    ):
        assert snippet in text


def test_v137_brainstorm_run_should_read_beacon_version_materials(tmp_path: Path) -> None:
    _seed_v137_docs(tmp_path)
    feature = "Beacon v1.3.7 beacon-brainstorm built-in convergence and evolution thinking"
    result = _invoke(
        [
            "brainstorm",
            "run",
            "补齐头暴子 skill 的边界",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--feature",
            feature,
            "--mode",
            "requirement-convergence",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["mode"] == "requirement-convergence"
    assert payload["missing_refs"] == []
    assert payload["human_closure_scaffold"]["enabled"] is True
    refs = [item["path"] for item in payload["version_material_refs"]]
    assert "docs/beacon/v1.3.7/execution/architecture-blueprint.md" in refs
    assert any(path.endswith("/prd/beacon-v1.3.7-beacon-brainstorm-built-in-convergence-and-evolution-thinking.md") for path in refs)
    output = tmp_path / payload["output_path"]
    assert output.exists()
    assert payload["output_path"].startswith("docs/brainstorms/")
    assert payload["output_path"].endswith(
        "beacon-v1.3.7-beacon-brainstorm-built-in-convergence-and-evolution-thinking-brainstorm.md"
    )
    text = output.read_text(encoding="utf-8")
    for section in (
        "## prompt_summary",
        "## version_material_refs",
        "## first_principles_breakdown",
        "## socratic_questions",
        "## redundancy_cuts",
        "## convergence_contract",
        "## converged_recommendation",
        "## next_route",
        "## human_closure_scaffold",
    ):
        assert section in text
    research_path = tmp_path / payload["human_closure_scaffold"]["research_path"]
    source_arch_path = tmp_path / payload["human_closure_scaffold"]["source_architecture_path"]
    assert research_path.exists()
    assert source_arch_path.exists()
    research_text = research_path.read_text(encoding="utf-8")
    assert "## Architecture" in research_text
    assert "## Business Flow" in research_text
    assert "## State Machine" in research_text
    assert "## Decision Priority" in research_text
    assert "## Open Questions" in research_text


def test_v137_brainstorm_should_reuse_existing_human_closure_scaffold(tmp_path: Path) -> None:
    _seed_v137_docs(tmp_path)
    feature = "Beacon v1.3.7 beacon-brainstorm built-in convergence and evolution thinking"
    first = _invoke(
        [
            "brainstorm",
            "run",
            "补齐头暴子 skill 的边界",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--feature",
            feature,
            "--mode",
            "requirement-convergence",
            "--json",
        ]
    )
    assert first.exit_code == 0, first.stdout
    second = _invoke(
        [
            "brainstorm",
            "run",
            "再次检查 requirement closure",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--feature",
            feature,
            "--mode",
            "requirement-convergence",
            "--json",
        ]
    )
    assert second.exit_code == 0, second.stdout
    payload = json.loads(second.stdout)
    assert payload["human_closure_scaffold"]["created"] == []
    assert payload["human_closure_scaffold"]["existing"]


def test_v137_brainstorm_modes_should_run(tmp_path: Path) -> None:
    _seed_v137_docs(tmp_path)
    for mode in ("requirement-convergence", "project-evolution", "implementation-readiness", "scope-simplification"):
        result = _invoke(
            [
                "brainstorm",
                "run",
                f"mode {mode}",
                "--project-root",
                str(tmp_path),
                "--version",
                "v1.3.7",
                "--mode",
                mode,
                "--json",
            ]
        )
        assert result.exit_code == 0, result.stdout
        assert json.loads(result.stdout)["mode"] == mode


def test_v137_brainstorm_old_mode_aliases_should_map_to_canonical_modes(tmp_path: Path) -> None:
    _seed_v137_docs(tmp_path)
    aliases = {
        "frozen-truth-delta": "implementation-readiness",
        "evolution-exploration": "project-evolution",
        "redundancy-pruning": "scope-simplification",
    }
    for alias, canonical in aliases.items():
        result = _invoke(
            [
                "brainstorm",
                "run",
                f"mode {alias}",
                "--project-root",
                str(tmp_path),
                "--version",
                "v1.3.7",
                "--mode",
                alias,
                "--json",
            ]
        )
        assert result.exit_code == 0, result.stdout
        payload = json.loads(result.stdout)
        assert payload["mode"] == alias
        assert payload["canonical_mode"] == canonical
        assert payload["converged_recommendation"]


def test_v137_brainstorm_should_emit_resolved_project_metadata_view(tmp_path: Path) -> None:
    _seed_v137_docs(tmp_path)
    _seed_project_metadata(tmp_path, version="v1.3.7", service="api", branch="beacon/v1.3.7")
    result = _invoke(
        [
            "brainstorm",
            "run",
            "核实 monorepo branch contract",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["resolved_metadata_view"]["topology_kind"] == "monorepo"
    assert payload["resolved_metadata_view"]["selected_service"] == "api"
    assert payload["resolved_metadata_view"]["selected_branch"] == "beacon/v1.3.7"
    assert payload["metadata_ref"] == ".beacon/metadata/project-version-metadata.json"
    text = (tmp_path / payload["output_path"]).read_text(encoding="utf-8")
    assert "## project_metadata" in text
    assert "- selected_branch: `beacon/v1.3.7`" in text


def test_v137_brainstorm_auto_version_should_prefer_feature_version_semantics(tmp_path: Path) -> None:
    _seed_v137_docs(tmp_path)
    result = _invoke(
        [
            "brainstorm",
            "run",
            "复盘 Beacon v1.3.7 的头暴语义",
            "--project-root",
            str(tmp_path),
            "--version",
            "auto",
            "--feature",
            "Beacon v1.3.7 beacon-brainstorm built-in convergence and evolution thinking",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["version"] == "v1.3.7"
    assert payload["missing_refs"] == []
    assert payload["next_route"] == "brainstorm closed"


def test_v137_brainstorm_should_quarantine_external_project_outputs(tmp_path: Path) -> None:
    _seed_v137_docs(tmp_path)
    result = _invoke(
        [
            "brainstorm",
            "run",
            "针对 shopxo_canada 的第三方能力治理做收敛分析，不改 Beacon frozen truth",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["output_path"].startswith("docs/brainstorms/external/")
    output = tmp_path / payload["output_path"]
    assert output.exists()


def test_v137_brainstorm_should_flatten_prompt_paths_in_output_slug(tmp_path: Path) -> None:
    _seed_v137_docs(tmp_path)
    result = _invoke(
        [
            "brainstorm",
            "run",
            "分析生产出现的直推、间推数据错误问题。输入材料：docs/debug/01_relation_type_mismatch_fix.sql。目标：给出最小闭环排查路径。",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["output_path"].startswith("docs/brainstorms/")
    assert "/docs/" not in payload["output_path"]
    assert "docs-debug-01_relation_type_mismatch_fix.sql" in payload["output_path"]
    output = tmp_path / payload["output_path"]
    assert output.exists()


def test_v137_brainstorm_should_refuse_requirement_truth_output(tmp_path: Path) -> None:
    _seed_v137_docs(tmp_path)
    result = _invoke(
        [
            "brainstorm",
            "run",
            "try writing truth",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--output",
            "docs/beacon/v1.3.7/prd/blocked.md",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "brainstorm_invalid_request"
    assert not (tmp_path / "docs" / "beacon" / "v1.3.7" / "prd" / "blocked.md").exists()


def test_v137_implementation_delivery_baseline_should_be_canonical_projection_source(tmp_path: Path) -> None:
    _seed_v137_docs(tmp_path)
    feature = "Beacon v1.3.7 beacon-brainstorm built-in convergence and evolution thinking"
    freeze = _invoke(["freeze", feature, "--project", str(tmp_path), "--version", "v1.3.7", "--json"])
    assert freeze.exit_code == 0, freeze.stdout
    contract = _invoke(
        [
            "doctor",
            "sync-technical-review-contract",
            feature,
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--revision-id",
            "R1",
            "--review-status",
            "approved",
            "--approved-by",
            "codex",
            "--reviewed-at",
            "2026-04-23T09:00:00+08:00",
            "--json",
        ]
    )
    assert contract.exit_code == 0, contract.stdout
    plan_result = _invoke(["implement", "plan", feature, "--project-root", str(tmp_path), "--version", "v1.3.7", "--json"])
    assert plan_result.exit_code == 0, plan_result.stdout

    baseline = json.loads(implementation_delivery_baseline_path(tmp_path, "v1.3.7", feature).read_text(encoding="utf-8"))
    plan = json.loads(implementation_plan_json_path(tmp_path, "v1.3.7", feature).read_text(encoding="utf-8"))
    assert baseline["feature_overlays"][plan["feature_slug"]]["revision_id"] == "R1"
    git_workflow = plan["git_workflow"]
    for field in ("baseline_id", "transaction_id", "source_hash", "projection_seq"):
        assert plan[field] == baseline[field]
        assert git_workflow[field] == baseline[field]
    assert plan["canonical_envelope_ref"].endswith("implementation-delivery-baseline-beacon-v1.3.7-beacon-brainstorm-built-in-convergence-and-evolution-thinking.json")

    plan["source_hash"] = "sha256:tampered"
    implementation_plan_json_path(tmp_path, "v1.3.7", feature).write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    gate = build_implementation_plan_gate_payload(tmp_path, version="v1.3.7", feature=feature)
    assert gate["blocked"] is True
    assert gate["reason_code"] == "delivery_baseline_projection_drift"
