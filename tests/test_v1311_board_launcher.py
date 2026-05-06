from __future__ import annotations

import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import request

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_sources(tmp_path: Path, feature_slug: str, version: str) -> None:
    content = """# Feature

target_audience: Beacon operator and implementation owner
primary_use_cases: launch board, inspect frozen workbench, align operator next actions
operator_mental_state: needs dense but stable execution visibility
usage_environment: desktop-first operator workbench
brand_tone: quiet, precise, operational
density_preference: workbench-medium
design_preset: apple-inspired-design-md
prototype_freeze_required: true

AC-001 board launcher exists
AC-002 launcher resolves frozen prototype contract
AC-003 board stays read-only on requirement truth
TC-001 verify launcher contract
TC-002 verify fail-closed readiness

## Pages
- Portfolio Board
- Execution Board
- Feature Detail
- Run Detail
- Review Surface
- Recovery Diagnostics

## Route Map
- Portfolio Board -> Execution Board
- Execution Board -> Run Detail
- Run Detail -> Review Surface
- Review Surface -> Recovery Diagnostics
"""
    for sub in ("user-story", "prd", "qa/test-cases"):
        target = tmp_path / "docs" / "beacon" / version / sub / f"{feature_slug}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def _freeze_bundle(tmp_path: Path, version: str, feature: str) -> None:
    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--mode", "rule"])
    assert create.exit_code == 0, create.stdout
    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version])
    assert review.exit_code == 0, review.stdout
    freeze = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version])
    assert freeze.exit_code == 0, freeze.stdout


def test_v1311_board_command_should_be_registered() -> None:
    result = _invoke(["board", "--help"])
    assert result.exit_code == 0, result.stdout
    assert "--feature" in result.stdout
    assert "--dry-run" in result.stdout
    assert "dispatch" in result.stdout


def test_v1311_board_dry_run_should_emit_ready_launcher_contract(tmp_path: Path) -> None:
    version = "v1.3.11"
    feature = "Beacon Operator Workbench And Board Launcher"
    feature_slug = "beacon-operator-workbench-and-board-launcher"
    _prepare_sources(tmp_path, feature_slug, version)
    _freeze_bundle(tmp_path, version, feature)

    result = _invoke(
        [
            "board",
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--dry-run",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["readiness_status"] == "ready"
    assert payload["mode"] == "local-web"
    assert payload["feature_slug"] == feature_slug
    assert payload["entry_html"] == "index.html"
    assert payload["board_url"].endswith("/index.html")
    assert Path(payload["bundle_root"]).exists()
    assert Path(payload["entry_html_path"]).exists()
    assert payload["runtime_source"]["prototype_status"]["gate_ready"] is True
    assert payload["runtime_source"]["surface"] == "operator-workbench-bundle"
    assert payload["view_contract"]["views"] == [
        "portfolio-board",
        "execution-board",
        "feature-detail",
        "run-detail",
        "review-surface",
        "recovery-diagnostics",
    ]
    assert payload["operator_workbench"]["portfolio_board"]["project_name"] == tmp_path.name
    actions = payload["operator_workbench"]["operator_action_contract"]["actions"]
    assert [item["action_id"] for item in actions] == ["continue", "stop", "retry", "repair"]
    assert all(item["governance"] for item in actions)


def test_v1311_board_should_surface_supplement_jump_links(tmp_path: Path) -> None:
    version = "v1.3.11"
    feature = "Beacon Operator Workbench And Board Launcher"
    feature_slug = "beacon-operator-workbench-and-board-launcher"
    _prepare_sources(tmp_path, feature_slug, version)
    _freeze_bundle(tmp_path, version, feature)

    contract = _invoke(
        [
            "board",
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--dry-run",
            "--json",
        ]
    )
    assert contract.exit_code == 0, contract.stdout
    payload = json.loads(contract.stdout)
    workbench = payload["operator_workbench"]
    assert "supplement_task" in workbench["feature_detail"]
    assert "re_freeze_transaction" in workbench["feature_detail"]
    bundle_root = Path(payload["bundle_root"])
    html = (bundle_root / "index.html").read_text(encoding="utf-8")
    assert "补料跳转" in html
    assert "jump-link" in html


def test_v1311_board_dry_run_should_reuse_persistent_bundle_and_serve_index(tmp_path: Path) -> None:
    version = "v1.3.11"
    feature = "Reusable Board Bundle"
    feature_slug = "reusable-board-bundle"
    _prepare_sources(tmp_path, feature_slug, version)
    _freeze_bundle(tmp_path, version, feature)

    first = _invoke(
        [
            "board",
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--dry-run",
            "--json",
        ]
    )
    assert first.exit_code == 0, first.stdout
    first_payload = json.loads(first.stdout)
    bundle_root = Path(first_payload["bundle_root"])
    index_path = Path(first_payload["entry_html_path"])
    assert bundle_root.exists()
    assert index_path.exists()
    first_mtime = index_path.stat().st_mtime_ns

    second = _invoke(
        [
            "board",
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--dry-run",
            "--json",
        ]
    )
    assert second.exit_code == 0, second.stdout
    second_payload = json.loads(second.stdout)
    assert Path(second_payload["bundle_root"]) == bundle_root
    assert Path(second_payload["entry_html_path"]) == index_path
    assert index_path.stat().st_mtime_ns == first_mtime

    handler = partial(SimpleHTTPRequestHandler, directory=str(bundle_root))
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        port = int(server.server_address[1])
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with request.urlopen(f"http://127.0.0.1:{port}/index.html", timeout=5) as response:
                assert response.status == 200
                html = response.read().decode("utf-8")
            assert "Beacon 执行工作台" in html
            assert "恢复判断" in html
            assert "toolkit exists as hidden/labs command" not in html
        finally:
            server.shutdown()
            thread.join(timeout=5)


def test_v1311_board_should_fail_closed_when_prototype_not_frozen(tmp_path: Path) -> None:
    version = "v1.3.11"
    feature = "Board Launcher Draft Only"
    feature_slug = "board-launcher-draft-only"
    _prepare_sources(tmp_path, feature_slug, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--mode", "rule"])
    assert create.exit_code == 0, create.stdout

    result = _invoke(
        [
            "board",
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--dry-run",
            "--json",
        ]
    )

    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["readiness_status"] == "not_ready"
    assert "not gate ready" in payload["failure_reason"]
    assert payload["runtime_source"]["prototype_status"]["gate_ready"] is False


def test_v1311_board_should_auto_detect_single_gate_ready_prototype(tmp_path: Path) -> None:
    version = "v1.3.11"
    feature = "Single Candidate Board"
    feature_slug = "single-candidate-board"
    _prepare_sources(tmp_path, feature_slug, version)
    _freeze_bundle(tmp_path, version, feature)

    result = _invoke(
        [
            "board",
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--dry-run",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["feature"] == feature_slug
    assert payload["selection_mode"] == "auto-single-gate-ready"
    assert payload["operator_workbench"]["views"][1] == "execution-board"


def test_v1311_board_desktop_contract_should_be_planned_not_implemented(tmp_path: Path) -> None:
    version = "v1.3.11"
    feature = "Desktop Planned Board"
    feature_slug = "desktop-planned-board"
    _prepare_sources(tmp_path, feature_slug, version)
    _freeze_bundle(tmp_path, version, feature)

    result = _invoke(
        [
            "board",
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--desktop",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["mode"] == "desktop-planned"
    assert payload["readiness_status"] == "planned"
    assert "not implemented yet" in payload["failure_reason"]


def test_v1311_board_dry_run_should_emit_execution_groups_and_diagnostics(tmp_path: Path) -> None:
    version = "v1.3.11"
    feature = "Board Runtime Payload"
    feature_slug = "board-runtime-payload"
    _prepare_sources(tmp_path, feature_slug, version)
    _freeze_bundle(tmp_path, version, feature)

    run_root = tmp_path / ".beacon" / "runs" / "run-001"
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "state.json").write_text(
        json.dumps(
            {
                "run_id": "run-001",
                "feature": feature,
                "version": version,
                "mode": "team",
                "status": "blocked",
                "started_at": "2026-05-01T12:00:00Z",
                "recommended_command": "beacon help --project-root .",
                "reason_code": "blocked_dependency",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_root / "events.jsonl").write_text(
        json.dumps({"event": "blocked", "stage": "implement", "reason_code": "blocked_dependency", "ts": "2026-05-01T12:01:00Z"}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    result = _invoke(
        [
            "board",
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--dry-run",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    groups = payload["operator_workbench"]["execution_board"]["groups"]
    assert groups["blocked"]["count"] >= 1
    assert payload["operator_workbench"]["run_detail"]["selected_run_id"] == "run-001"
    assert payload["operator_workbench"]["recovery_diagnostics"][0]["reason_code"]
    actions = payload["operator_workbench"]["run_detail"]["operator_actions"]
    retry = next(item for item in actions if item["action_id"] == "retry")
    repair = next(item for item in actions if item["action_id"] == "repair")
    stop = next(item for item in actions if item["action_id"] == "stop")
    assert retry["availability"] == "enabled"
    assert "resume continue" in retry["command"] or "beacon help" in retry["command"]
    assert repair["availability"] == "enabled"
    assert stop["availability"] in {"guarded", "unavailable"}


def test_v1311_board_dispatch_dry_run_should_resolve_action_contract(tmp_path: Path) -> None:
    version = "v1.3.11"
    feature = "Board Dispatch Dry Run"
    feature_slug = "board-dispatch-dry-run"
    _prepare_sources(tmp_path, feature_slug, version)
    _freeze_bundle(tmp_path, version, feature)

    result = _invoke(
        [
            "board",
            "dispatch",
            "repair",
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--dry-run",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "planned"
    assert payload["action"]["action_id"] == "repair"
    assert payload["action"]["availability"] in {"enabled", "guarded"}
    assert payload["action"]["command"]


def test_v1311_board_dispatch_should_execute_retry_action(tmp_path: Path) -> None:
    version = "v1.3.11"
    feature = "Board Dispatch Execute"
    feature_slug = "board-dispatch-execute"
    _prepare_sources(tmp_path, feature_slug, version)
    _freeze_bundle(tmp_path, version, feature)

    run_root = tmp_path / ".beacon" / "runs" / "run-002"
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "state.json").write_text(
        json.dumps(
            {
                "run_id": "run-002",
                "feature": feature,
                "version": version,
                "mode": "team",
                "status": "blocked",
                "started_at": "2026-05-01T12:00:00Z",
                "recommended_command": f'beacon help --project-root "{tmp_path}" --version {version} --feature "{feature}" --json',
                "reason_code": "blocked_dependency",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "board",
            "dispatch",
            "retry",
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert payload["action"]["action_id"] == "retry"
    assert payload["execution"]["exit_code"] == 0
