from __future__ import annotations

import json
from pathlib import Path

from beacon.main import app
from beacon.utils.agent_surface import SkillProjection, resolve_global_agent_surface
from beacon.utils.program_orchestrator import build_program_orchestrator_state
from beacon.utils.version_defaults import _project_release_baseline
from typer.testing import CliRunner


runner = CliRunner()


def test_project_release_baseline_ignores_runtime_collapsed_onboarding(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("beacon.utils.version_defaults._toolkit_runtime", lambda _root: "v1.6.12")
    baseline = _project_release_baseline(tmp_path, docs_versions=["v0.0.5"], onboarding_docs="v1.6.12")
    assert baseline == "v0.0.5"


def test_resolve_global_agent_surface_uses_flat_beacon_brand_only(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "beacon.utils.agent_surface._expected_skill_projections",
        lambda *_args, **_kwargs: [
            SkillProjection(id="beacon-goal", source_path="skills/beacon/beacon-goal", source_hash="h1", source_kind="packaged_skill_directory"),
            SkillProjection(id="beacon-plan", source_path="skills/beacon/beacon-plan", source_hash="h2", source_kind="packaged_skill_directory"),
        ],
    )
    monkeypatch.setattr(
        "beacon.utils.agent_surface.verify_global_agents_beacon_skills",
        lambda **_kwargs: {
            "status": "pass",
            "ok": True,
            "skills_root": str(tmp_path / ".agents" / "skills"),
            "missing": [],
            "wrong_target": [],
            "leak_package_roots": [],
        },
    )
    payload = resolve_global_agent_surface(agent="codex", runtime_version="v1.6.12", docs_version="v1.6.12", home=tmp_path / "home")
    assert payload["ok"] is True
    assert payload["resolution_mode"] == "global-first"
    assert payload["missing"] == []
    assert payload["expected_ids"] == ["beacon-goal", "beacon-plan"]


def test_program_orchestrate_surfaces_current_lake_and_next_action(tmp_path: Path) -> None:
    version = "v1.6.12"
    program = "demo-program"
    program_root = tmp_path / "docs" / "beacon" / version / "programs" / program
    program_root.mkdir(parents=True)
    (program_root / "feature-graph.json").write_text(
        json.dumps(
            {
                "program_slug": program,
                "version": version,
                "scope_mode": "full_parity",
                "lakes": [
                    {"slug": "lake-a", "feature_slug": "lake-a", "depends_on": [], "parity_subset": ["a"], "status": "frozen", "truth_status": "frozen"},
                    {"slug": "lake-b", "feature_slug": "lake-b", "depends_on": ["lake-a"], "parity_subset": ["b"], "status": "frozen", "truth_status": "frozen"},
                ],
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    payload = build_program_orchestrator_state(tmp_path, version=version, program_slug=program)
    assert payload["current_lake"] == "lake-a"
    assert payload["current_stage"] == "implement"
    assert payload["next_action"] == "beacon-gen-implement:lake-a"


def test_program_orchestrate_cli_writes_program_run_state(tmp_path: Path) -> None:
    version = "v1.6.12"
    program = "demo-program"
    program_root = tmp_path / "docs" / "beacon" / version / "programs" / program
    program_root.mkdir(parents=True)
    (program_root / "feature-graph.json").write_text(
        json.dumps(
            {
                "program_slug": program,
                "version": version,
                "scope_mode": "full_parity",
                "lakes": [
                    {"slug": "lake-a", "feature_slug": "lake-a", "depends_on": [], "parity_subset": ["a"], "status": "frozen", "truth_status": "frozen"},
                ],
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (program_root / "program-manifest.md").write_text(
        "---\nprogram_slug: demo-program\nversion: v1.6.12\nprogram_plan_frozen: true\nlake_package_truth_frozen: true\n---\n",
        encoding="utf-8",
    )
    (program_root / "program-truth-freeze.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "program_slug": program,
                "version": version,
                "status": "frozen",
                "blocked": False,
                "lakes": [{"slug": "lake-a", "feature_slug": "lake-a", "status": "frozen", "truth_promotion_complete": True}],
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["program", "orchestrate", program, "--project", str(tmp_path), "--version", version, "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["current_lake"] == "lake-a"
    assert payload["program_run_state_path"].endswith("program-run-state.json")


def test_goal_continue_routes_through_program_orchestrator(tmp_path: Path) -> None:
    version = "v1.6.12"
    program = "demo-program"
    run_id = "run-program-continue"
    program_root = tmp_path / "docs" / "beacon" / version / "programs" / program
    program_root.mkdir(parents=True)
    (program_root / "feature-graph.json").write_text(
        json.dumps(
            {
                "program_slug": program,
                "version": version,
                "scope_mode": "full_parity",
                "lakes": [
                    {"slug": "lake-a", "feature_slug": "lake-a", "depends_on": [], "parity_subset": ["a"], "status": "frozen", "truth_status": "frozen"},
                ],
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (program_root / "program-manifest.md").write_text(
        "---\nprogram_slug: demo-program\nversion: v1.6.12\nprogram_plan_frozen: true\nlake_package_truth_frozen: true\n---\n",
        encoding="utf-8",
    )
    (program_root / "program-truth-freeze.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "program_slug": program,
                "version": version,
                "status": "frozen",
                "blocked": False,
                "lakes": [{"slug": "lake-a", "feature_slug": "lake-a", "status": "frozen", "truth_promotion_complete": True}],
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    goal_state = {
        "schema_version": "1.0",
        "run_id": run_id,
        "status": "running",
        "blocked": False,
        "reason_code": "",
        "version": version,
        "feature": "lake-a",
        "lakes": ["lake-a"],
        "current_stage": "implement",
        "stages": [
            {"stage": "plan", "status": "done", "loaded": True, "skills": []},
            {"stage": "truth", "status": "done", "loaded": True, "skills": []},
            {"stage": "implement", "status": "active", "loaded": True, "skills": []},
            {"stage": "qa", "status": "planned", "loaded": False, "skills": []},
            {"stage": "release", "status": "planned", "loaded": False, "skills": []},
        ],
        "history": [{"event": "created"}],
    }
    state_path = tmp_path / ".beacon" / "state" / "product-goal" / f"{run_id}.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(goal_state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result = runner.invoke(app, ["goal", "continue", "--run-id", run_id, "--project", str(tmp_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("program_orchestrator", {}).get("current_lake") == "lake-a"
    assert payload.get("program_orchestrator", {}).get("next_action") == "beacon-gen-implement:lake-a"
