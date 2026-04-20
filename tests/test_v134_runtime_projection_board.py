from __future__ import annotations

import json
import importlib
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils import runtime_projection as runtime_projection_module
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
    (base / "prd" / "beacon-runtime-ledger.md").write_text("# Runtime Ledger PRD\n\n- scope\n", encoding="utf-8")
    (base / "user-story" / "beacon-runtime-ledger.md").write_text("# Runtime Ledger User Story\n\n1. actor\n", encoding="utf-8")
    (base / "qa" / "test-cases" / "beacon-runtime-ledger.md").write_text("# Runtime Ledger Test Case\n\n> verify\n", encoding="utf-8")


def _make_projection_envelope(root: Path, *, project_key: str, display_name: str) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "project_key": project_key,
        "display_name": display_name,
        "workspace_root": str(root),
        "project_root": str(root),
        "docs_version": "v1.3.4",
        "docs_root": str(root / "docs" / "beacon" / "v1.3.4"),
        "state_root": str(root / ".beacon"),
        "beacon_runtime_version": "v1.3.3",
        "feature": "",
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
            "next_step": {"action": "user-story"},
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
        },
        "debug": {
            "state": "no_debug_feed",
            "issue_count": 0,
            "index_exists": False,
            "paths": [],
        },
        "git_scopes": [],
        "sessions": {"qa_session_id": "", "qa_runner_type": ""},
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
        },
    }


def test_v134_detect_debug_state_should_model_tri_state(tmp_path: Path) -> None:
    no_debug = runtime_projection_module.detect_debug_state(tmp_path)
    assert no_debug["state"] == "no_debug_feed"

    debug_root = tmp_path / ".beacon" / "debug"
    debug_root.mkdir(parents=True, exist_ok=True)
    (debug_root / "index.json").write_text(json.dumps({"latest_run_id": "run-001"}), encoding="utf-8")

    runtime_feed_only = runtime_projection_module.detect_debug_state(tmp_path)
    assert runtime_feed_only["state"] == "runtime_feed_only"
    assert runtime_feed_only["latest_run_id"] == "run-001"

    issues_root = debug_root / "issues"
    issues_root.mkdir(parents=True, exist_ok=True)
    (issues_root / "issue-1.json").write_text("{}", encoding="utf-8")

    materialized_issue = runtime_projection_module.detect_debug_state(tmp_path)
    assert materialized_issue["state"] == "materialized_issue"
    assert materialized_issue["issue_count"] == 1


def test_v134_build_runtime_projection_should_be_deterministic_and_multi_repo_aware(
    monkeypatch, tmp_path: Path
) -> None:
    _seed_docs(tmp_path)
    (tmp_path / ".beacon" / "debug").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "debug" / "index.json").write_text(
        json.dumps({"latest_run_id": "run-runtime-feed"}),
        encoding="utf-8",
    )

    monkeypatch.setattr(runtime_projection_module, "resolve_target_version", lambda *_args, **_kwargs: "v1.3.4")
    monkeypatch.setattr(
        runtime_projection_module,
        "discover_git_scopes",
        lambda _root: [
            {
                "scope_key": "root",
                "repo_root": "/workspace/root",
                "repo_name": "root",
                "branch": "main",
                "commit": "abc123",
                "dirty": False,
                "role": "primary",
                "worktree_path": "/workspace/root",
                "source_priority": "git_worktree",
            },
            {
                "scope_key": "svc",
                "repo_root": "/workspace/service-a",
                "repo_name": "service-a",
                "branch": "feat/runtime",
                "commit": "def456",
                "dirty": True,
                "role": "service",
                "worktree_path": "/workspace/service-a",
                "source_priority": "git_worktree",
            },
        ],
    )
    monkeypatch.setattr(
        runtime_projection_module,
        "build_help_payload",
        lambda *_args, **_kwargs: {
            "current_stage": "implemented",
            "blocked": False,
            "blocked_reason": "",
            "next_step": {"action": "qa"},
            "execution_surface": {
                "implement_mode": "team",
                "qa_execution_mode": "story-exhaustive",
            },
            "hud": {},
        },
    )
    monkeypatch.setattr(
        runtime_projection_module,
        "load_current_qa_session",
        lambda _root: {"session_id": "session-001", "runner_type": "browser-use"},
    )

    envelope1 = runtime_projection_module.build_runtime_projection(
        tmp_path,
        docs_version="v1.3.4",
        feature="beacon-runtime-ledger",
    )
    envelope2 = runtime_projection_module.build_runtime_projection(
        tmp_path,
        docs_version="v1.3.4",
        feature="beacon-runtime-ledger",
    )

    assert envelope1["project_kind"] == "multi_repo_workspace"
    assert envelope1["board"]["debug_state"] == "runtime_feed_only"
    assert envelope1["runtime"]["mode"] == "team"
    assert envelope1["projection"]["preflight_status"] == "pass"
    assert envelope1["projection"]["source_hash"] == envelope2["projection"]["source_hash"]
    assert envelope1["projection"]["projection_seq"] == envelope2["projection"]["projection_seq"]
    assert envelope1["project_key"] == envelope2["project_key"]
    assert str(envelope1["project_key"]).startswith(f"{tmp_path.name}--")


def test_v134_runtime_projection_store_should_sync_and_list_portfolio(monkeypatch, tmp_path: Path) -> None:
    ledger_root = tmp_path / "ledger"
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(ledger_root))

    alpha_root = tmp_path / "alpha"
    beta_root = tmp_path / "beta"
    _seed_docs(alpha_root)
    _seed_docs(beta_root)

    alpha = _make_projection_envelope(alpha_root, project_key="alpha", display_name="Alpha")
    beta = _make_projection_envelope(beta_root, project_key="beta", display_name="Beta")
    beta["projection"]["source_hash"] = "hash-beta"
    beta["projection"]["projection_seq"] = "ps-beta"

    alpha_result = store_module.sync_projection(alpha)
    beta_result = store_module.sync_projection(beta)

    assert alpha_result["status"] == "applied"
    assert beta_result["status"] == "applied"
    assert (ledger_root / "runtime-ledger.sqlite3").exists()
    assert Path(alpha_result["mirror_paths"]["project"]).exists()
    assert Path(beta_result["mirror_paths"]["projection_writes"]).exists()

    portfolio = store_module.list_projects(limit=12)
    assert len(portfolio) == 2
    assert {row["display_name"] for row in portfolio} == {"Alpha", "Beta"}

    detail = store_module.load_project_detail("alpha")
    assert detail["display_name"] == "Alpha"
    assert detail["projection"]["projection_seq"] == "ps-alpha"


def test_v134_public_board_should_include_document_projection(monkeypatch, tmp_path: Path) -> None:
    ledger_root = tmp_path / "ledger"
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(ledger_root))

    project_root = tmp_path / "alpha"
    _seed_docs(project_root)
    envelope = _make_projection_envelope(project_root, project_key="alpha", display_name="Alpha")
    store_module.sync_projection(envelope)

    detail_path = ledger_root / "pocketbase" / "pb_public" / "data" / "projects" / "alpha.json"
    detail = json.loads(detail_path.read_text(encoding="utf-8"))
    assert any(item["section"] == "版本摘要" for item in detail["documents"])
    assert any(item["section"] == "执行蓝图" for item in detail["documents"])

    summary_doc_key = next(item["doc_key"] for item in detail["documents"] if item["relative_path"] == "SUMMARY.md")
    summary_doc_path = ledger_root / "pocketbase" / "pb_public" / "data" / "documents" / "alpha" / f"{summary_doc_key}.json"
    summary_doc = json.loads(summary_doc_path.read_text(encoding="utf-8"))
    assert summary_doc["title"] == "v1.3.4"
    assert "# v1.3.4" in summary_doc["content"]


def test_v134_status_board_should_sync_projection_and_render_portfolio(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    ledger_root = tmp_path / "ledger"
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(ledger_root))

    status_module = importlib.import_module("beacon.commands.status")

    envelope = _make_projection_envelope(tmp_path, project_key="demo", display_name="Demo Project")
    monkeypatch.setattr(status_module, "build_runtime_projection", lambda *_args, **_kwargs: envelope)
    monkeypatch.setattr(status_module, "build_release_scorecard", lambda *_args, **_kwargs: {"release_ready": False})
    monkeypatch.setattr(
        status_module,
        "summarize_release_scorecard",
        lambda _payload: {
            "release_ready": False,
            "gate_status": "open",
            "qa_status": "not_started",
            "qa_execution_mode": "none",
            "qa_evidence_done": False,
        },
    )

    result = _invoke(
        [
            "status",
            "show-status",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.4",
            "--board",
        ]
    )
    assert result.exit_code == 0, result.stdout
    assert "Beacon Status Board" in result.stdout
    assert "- board.project: Demo Project" in result.stdout
    assert "- board.ledger_sync: applied" in result.stdout
    assert "- board.portfolio_projects: 1" in result.stdout
    assert "- portfolio.1: Demo Project | kind=single_repo" in result.stdout
    assert (ledger_root / "runtime-ledger.sqlite3").exists()
