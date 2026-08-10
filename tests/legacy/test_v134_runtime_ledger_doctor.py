from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils import runtime_projection_store as store_module


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path, version: str = "v1.3.4") -> None:
    base = root / "docs" / "beacon" / version
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text(f"# {version}\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution Index\n\n- A\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n\nBeacon runtime.\n", encoding="utf-8")
    (base / "prd" / "demo-feature.md").write_text("# Demo PRD\n\n- scope\n- flow\n", encoding="utf-8")
    (base / "user-story" / "demo-feature.md").write_text("# Demo User Story\n\n1. actor\n2. action\n", encoding="utf-8")
    (base / "qa" / "test-cases" / "demo-feature.md").write_text("# Demo Test Case\n\n> verify\n", encoding="utf-8")


def _make_projection_envelope(root: Path, *, project_key: str, display_name: str) -> dict[str, object]:
    return {
        "schema_version": "1.1",
        "project_key": project_key,
        "display_name": display_name,
        "workspace_root": str(root),
        "project_root": str(root),
        "docs_version": "v1.3.4",
        "docs_root": str(root / "docs" / "beacon" / "v1.3.4"),
        "state_root": str(root / ".beacon"),
        "beacon_runtime_version": "v1.3.4",
        "feature": "demo-feature",
        "package_key": f"{project_key}:v1.3.4:demo-feature",
        "project_kind": "single_repo",
        "truth": {
            "docs_root": str(root / "docs" / "beacon" / "v1.3.4"),
            "state_root": str(root / ".beacon"),
            "source_of_truth": "docs/beacon + .beacon",
        },
        "lifecycle": {
            "stage": "requirements",
            "current_stage": "draft",
            "progress_label": "materials:1/3",
            "blocked": False,
            "blocked_reason": "",
            "next_step": {
                "action": "user-story",
                "command": f"beacon user-story --project-root {root} --version v1.3.4",
            },
        },
        "materials": {"prd": "ready", "user_story": "missing", "test_case": "missing"},
        "runtime": {
            "mode": "idle",
            "execution_surface": {},
            "runtime_corroboration": {
                "status": "missing",
                "source": "truth-only",
                "reason": "runtime cache absent",
            },
            "qa_session": {},
            "hud": {},
            "run_count": 0,
            "worker_count": 0,
            "host_session_count": 1,
        },
        "debug": {
            "state": "no_debug_feed",
            "issue_count": 0,
            "index_exists": False,
            "paths": [],
        },
        "git_scopes": [],
        "sessions": {"qa_session_id": "", "qa_runner_type": ""},
        "feature_packages": [
            {
                "project_key": project_key,
                "package_key": f"{project_key}:v1.3.4:demo-feature",
                "feature": "demo-feature",
                "feature_slug": "demo-feature",
                "docs_version": "v1.3.4",
                "prd_path": "docs/beacon/v1.3.4/prd/demo-feature.md",
                "user_story_path": "docs/beacon/v1.3.4/user-story/demo-feature.md",
                "test_case_path": "docs/beacon/v1.3.4/qa/test-cases/demo-feature.md",
                "materials": {"prd": "ready", "user_story": "missing", "test_case": "missing"},
            }
        ],
        "feature_lifecycle": [
            {
                "project_key": project_key,
                "package_key": f"{project_key}:v1.3.4:demo-feature",
                "feature": "demo-feature",
                "current_stage": "requirements",
                "progress_label": "materials:1/3",
                "blocked": False,
                "blocked_reason": "",
                "next_action": "user-story",
                "runtime_mode": "idle",
                "debug_state": "no_debug_feed",
                "truth_refs": {
                    "docs_root": str(root / "docs" / "beacon" / "v1.3.4"),
                    "state_root": str(root / ".beacon"),
                },
            }
        ],
        "stage_material_status": [
            {
                "project_key": project_key,
                "package_key": f"{project_key}:v1.3.4:demo-feature",
                "material_type": "prd",
                "status": "ready",
                "truth_path": "docs/beacon/v1.3.4/prd/demo-feature.md",
            }
        ],
        "runs": [],
        "run_workers": [],
        "run_targets": [],
        "run_events": [],
        "artifact_refs": [],
        "git_workspace_bindings": [],
        "host_sessions": [
            {
                "project_key": project_key,
                "feature": "demo-feature",
                "run_id": f"run-{project_key}",
                "host_runtime": "codex",
                "session_id": f"host:{project_key}",
                "thread_id": "thread-1",
                "turn_id": "turn-2",
                "transcript_path": ".beacon/transcripts/demo-session.md",
                "status": "observed",
                "started_at": "2026-04-19T00:00:00+00:00",
                "ended_at": "",
            }
        ],
        "health_snapshots": [
            {
                "project_key": project_key,
                "snapshot_at": "2026-04-19T00:00:00+00:00",
                "overall_status": "degraded",
                "stale_runs": 0,
                "blocked_runs": 0,
                "failing_scopes": 0,
                "sync_status": "pass",
                "notes": ["runtime_corroboration_missing"],
            }
        ],
        "debug_issues": [],
        "projection": {
            "source_hash": f"hash-{project_key}",
            "projection_seq": f"ps-{project_key}",
            "projection_version": "v1.3.4-runtime-ledger",
            "truth_refs": {
                "docs_root": str(root / "docs" / "beacon" / "v1.3.4"),
                "state_root": str(root / ".beacon"),
            },
            "preflight_status": "pass",
            "confidence": 1.0,
            "uncertainty_reason": "",
            "preflight": {
                "status": "pass",
                "conflicts": [],
                "warnings": [],
                "source_priority": [
                    "user_explicit",
                    "git_worktree",
                    "project_config",
                    "truth_binding",
                    "heuristic",
                ],
            },
        },
        "board": {
            "version": "v1.3.4",
            "project_kind": "single_repo",
            "current_stage": "requirements",
            "progress_label": "materials:1/3",
            "blocker": "none",
            "next_action": "user-story",
            "debug_state": "no_debug_feed",
            "runtime_corroboration": "missing",
            "health_status": "degraded",
            "active_runs": 0,
            "active_agents": 0,
        },
    }


def test_v134_runtime_ledger_should_write_anchor_control_plane_and_fallback_to_mirror(monkeypatch, tmp_path: Path) -> None:
    ledger_root = tmp_path / "ledger"
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(ledger_root))

    project_root = tmp_path / "alpha"
    _seed_docs(project_root)
    envelope = _make_projection_envelope(project_root, project_key="alpha", display_name="Alpha")

    result = store_module.sync_projection(envelope)

    assert result["status"] == "applied"
    assert result["sqlite_status"] == "applied"
    assert Path(result["envelope_path"]).exists()
    assert Path(result["control_plane"]["schema_path"]).exists()
    assert Path(result["control_plane"]["serve_script"]).exists()
    assert Path(result["mirror_paths"]["project"]).exists()
    assert Path(result["mirror_paths"]["board_index"]).exists()
    assert Path(result["mirror_paths"]["board_portfolio_page"]).exists()
    assert Path(result["mirror_paths"]["board_portfolio"]).exists()
    assert "--publicDir \"$ROOT/pb_public\"" in Path(result["control_plane"]["serve_script"]).read_text(encoding="utf-8")

    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_DISABLE_SQLITE", "1")
    portfolio = store_module.list_projects(limit=5)
    assert len(portfolio) == 1
    assert portfolio[0]["display_name"] == "Alpha"
    detail = store_module.load_project_detail("alpha")
    assert detail["project_key"] == "alpha"


def test_v134_doctor_runtime_ledger_commands_should_rebuild_verify_and_export(monkeypatch, tmp_path: Path) -> None:
    ledger_root = tmp_path / "ledger"
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(ledger_root))
    project_root = tmp_path / "demo"
    _seed_docs(project_root)

    rebuild = _invoke(
        [
            "doctor",
            "rebuild-runtime-ledger",
            "--project-root",
            str(project_root),
            "--version",
            "v1.3.4",
            "--json",
        ]
    )
    assert rebuild.exit_code == 0, rebuild.stdout
    rebuild_payload = json.loads(rebuild.stdout)
    assert rebuild_payload["result"]["status"] == "applied"
    assert Path(rebuild_payload["result"]["envelope_path"]).exists()

    verify = _invoke(
        [
            "doctor",
            "verify-runtime-ledger",
            "--project-root",
            str(project_root),
            "--version",
            "v1.3.4",
            "--json",
        ]
    )
    assert verify.exit_code == 0, verify.stdout
    verify_payload = json.loads(verify.stdout)
    assert verify_payload["action"] == "verify-runtime-ledger"
    assert verify_payload["status"] in {"PASS", "WARN"}
    checks = verify_payload["result"]["checks"]
    assert any(item["name"] == "projection_determinism" for item in checks)
    assert any(item["name"] == "pocketbase_control_plane" for item in checks)
    assert any(item["name"] == "pocketbase_board_surface" for item in checks)

    export = _invoke(
        [
            "doctor",
            "export-runtime-ledger",
            "--project-root",
            str(project_root),
            "--label",
            "smoke-export",
            "--json",
        ]
    )
    assert export.exit_code == 0, export.stdout
    export_payload = json.loads(export.stdout)
    copied = export_payload["result"]["copied"]
    assert Path(export_payload["result"]["export_root"]).exists()
    assert "projections" in copied
    assert "pocketbase" in copied


def test_v134_runtime_ledger_should_publish_public_board_data_for_multiple_projects(monkeypatch, tmp_path: Path) -> None:
    ledger_root = tmp_path / "ledger"
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(ledger_root))

    alpha_root = tmp_path / "alpha"
    beta_root = tmp_path / "beta"
    _seed_docs(alpha_root)
    _seed_docs(beta_root)

    store_module.sync_projection(_make_projection_envelope(alpha_root, project_key="alpha", display_name="Alpha"))
    store_module.sync_projection(_make_projection_envelope(beta_root, project_key="beta", display_name="Beta"))

    portfolio_path = ledger_root / "pocketbase" / "pb_public" / "data" / "portfolio-summary.json"
    alpha_detail_path = ledger_root / "pocketbase" / "pb_public" / "data" / "projects" / "alpha.json"
    manifest_path = ledger_root / "pocketbase" / "pb_public" / "board-manifest.json"
    root_index_path = ledger_root / "pocketbase" / "pb_public" / "index.html"
    board_js_path = ledger_root / "pocketbase" / "pb_public" / "assets" / "board.js"

    portfolio = json.loads(portfolio_path.read_text(encoding="utf-8"))
    assert portfolio["summary"]["project_count"] == 2
    assert {item["display_name"] for item in portfolio["projects"]} == {"Alpha", "Beta"}
    assert {item["recommended_skill"] for item in portfolio["projects"]} == {"beacon-user-story"}
    assert {item["current_stage"] for item in portfolio["projects"]} == {"requirements"}

    alpha_detail = json.loads(alpha_detail_path.read_text(encoding="utf-8"))
    assert alpha_detail["project"]["display_name"] == "Alpha"
    assert alpha_detail["truth"]["source_of_truth"] == "docs/beacon + .beacon"
    assert alpha_detail["project"]["recommended_skill"] == "beacon-user-story"
    assert alpha_detail["host_sessions"][0]["run_id"] == "run-alpha"
    assert alpha_detail["host_sessions"][0]["transcript_ref"] == ".beacon/transcripts/demo-session.md"
    assert any(item["relative_path"] == "SUMMARY.md" for item in alpha_detail["documents"])
    summary_doc_key = next(item["doc_key"] for item in alpha_detail["documents"] if item["relative_path"] == "SUMMARY.md")
    summary_doc_path = ledger_root / "pocketbase" / "pb_public" / "data" / "documents" / "alpha" / f"{summary_doc_key}.json"
    assert summary_doc_path.exists()
    summary_doc = json.loads(summary_doc_path.read_text(encoding="utf-8"))
    assert summary_doc["title"] == "v1.3.4"
    assert "# v1.3.4" in summary_doc["content"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "portfolio-overview" in manifest["pages"]
    assert manifest["project_count"] == 2

    root_index = root_index_path.read_text(encoding="utf-8")
    assert 'data-page="board-home"' in root_index
    assert "Beacon 管理看板" in root_index
    assert "四页职责" not in root_index  # root shell stays thin; content comes from board.js
    assert "http-equiv=\"refresh\"" not in root_index

    board_js = board_js_path.read_text(encoding="utf-8")
    assert '"board-home": { nav: "首页" }' in board_js
    assert "async function renderBoardHome()" in board_js
    assert "按角色看" in board_js
    assert "版本文档列表与网页查看" in board_js
