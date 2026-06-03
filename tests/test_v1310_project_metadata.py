from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.implement.commands import _branch_guard_inputs, _run_branch_preflight
from beacon.main import app
from beacon.utils.project_metadata import resolve_project_metadata_view


runner = CliRunner()


def _git(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _seed_v1310_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / "v1.3.10" / "execution"
    base.mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "v1.3.10" / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")


def _seed_release_artifacts(root: Path, *, version: str, coverage_version: str) -> None:
    beacon_dir = root / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    docs_root = root / "docs" / "beacon" / version
    machine_change = docs_root / ".machine" / "change"
    release_dir = docs_root / "change"
    machine_change.mkdir(parents=True, exist_ok=True)
    release_dir.mkdir(parents=True, exist_ok=True)
    (beacon_dir / "auto-test-status.json").write_text(
        json.dumps({"status": "passed", "version": version, "run_id": "run-123"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (beacon_dir / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": version, "run_id": "run-123"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (beacon_dir / "evidence-manifest.json").write_text(
        json.dumps({"version": version, "run_id": "run-123", "entries": [{"path": ".beacon/auto-test-status.json"}]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (beacon_dir / "coverage-summary.json").write_text(
        json.dumps({"schema_version": "1.0", "run_id": "run-123", "version": coverage_version, "coverage_rate": 1.0, "full_coverage": True}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (machine_change / f"{version}.json").write_text(
        json.dumps({"version": version, "current_feature": "feature-a", "features": [{"feature": "feature-a"}]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (release_dir / f"{version}.md").write_text("# release\n", encoding="utf-8")


def test_v1310_friction_intake_should_emit_absolute_project_and_artifact_paths(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(tmp_path / ".runtime-ledger"))
    _seed_v1310_docs(tmp_path)

    result = runner.invoke(
        app,
        [
            "friction-intake",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.10",
            "--mode",
            "capture",
            "--note",
            "monorepo repo binding bug: project root has no .git and canonical branch contract drifts.",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["project_root"] == str(tmp_path.resolve())
    assert Path(payload["paths"]["json_abs"]).exists()
    assert Path(payload["paths"]["markdown_abs"]).exists()
    assert Path(payload["paths"]["evidence_abs"][0]).exists()
    latest = json.loads((tmp_path / ".beacon" / "state" / "friction-intake" / "latest.json").read_text(encoding="utf-8"))
    assert latest["project_root"] == str(tmp_path.resolve())
    assert Path(latest["payload_abs_path"]).exists()
    assert Path(latest["markdown_abs_path"]).exists()


def test_v1310_friction_intake_should_classify_metadata_domains(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(tmp_path / ".runtime-ledger"))
    _seed_v1310_docs(tmp_path)
    notes = {
        "monorepo": "monorepo root has no .git and topology detection keeps drifting",
        "branch-governance": "canonical branch governance is wrong and implement continues on the wrong branch",
        "repo-binding": "project root to service repo root binding is missing for the target service repo",
    }
    for expected_domain, note in notes.items():
        result = runner.invoke(
            app,
            [
                "friction-intake",
                "run",
                "--project-root",
                str(tmp_path),
                "--version",
                "v1.3.10",
                "--mode",
                "capture",
                "--note",
                note,
                "--json",
            ],
        )
        assert result.exit_code == 0, result.stdout
        payload = json.loads(result.stdout)
        assert payload["items"][0]["domain"] == expected_domain


def test_v1310_doctor_metadata_should_support_crud_and_verify(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(tmp_path / ".runtime-ledger"))
    service_root = tmp_path / "services" / "api"
    service_root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", "beacon/v1.3.10"], cwd=service_root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=service_root)
    _git(["git", "config", "user.name", "Test User"], cwd=service_root)
    (service_root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=service_root)
    _git(["git", "commit", "-m", "init"], cwd=service_root)

    create = runner.invoke(
        app,
        [
            "doctor",
            "metadata",
            "create",
            "--project-root",
            str(tmp_path),
            "--topology-kind",
            "monorepo",
            "--default-execution-service",
            "api",
            "--service-key",
            "api",
            "--repo-root",
            str(service_root),
            "--version",
            "v1.3.10",
            "--branch",
            "beacon/v1.3.10",
            "--json",
        ],
    )
    assert create.exit_code == 0, create.stdout
    create_payload = json.loads(create.stdout)
    assert create_payload["result"]["summary"]["transaction_id"]

    show = runner.invoke(
        app,
        ["doctor", "metadata", "show", "--project-root", str(tmp_path), "--version", "v1.3.10", "--json"],
    )
    assert show.exit_code == 0, show.stdout
    show_payload = json.loads(show.stdout)
    assert show_payload["result"]["resolved_metadata_view"]["selected_branch"] == "beacon/v1.3.10"

    verify = runner.invoke(
        app,
        ["doctor", "metadata", "verify", "--project-root", str(tmp_path), "--version", "v1.3.10", "--json"],
    )
    assert verify.exit_code == 0, verify.stdout
    verify_payload = json.loads(verify.stdout)
    assert verify_payload["result"]["status"] == "pass"

    delete = runner.invoke(
        app,
        ["doctor", "metadata", "delete", "--project-root", str(tmp_path), "--service-key", "api", "--json"],
    )
    assert delete.exit_code == 0, delete.stdout
    delete_payload = json.loads(delete.stdout)
    assert delete_payload["result"]["payload"]["global_project_metadata"]["service_bindings"] == []


def test_v1310_implement_branch_guard_inputs_should_consume_project_metadata(tmp_path: Path) -> None:
    service_root = tmp_path / "services" / "worker"
    service_root.mkdir(parents=True, exist_ok=True)
    result = runner.invoke(
        app,
        [
            "doctor",
            "metadata",
            "create",
            "--project-root",
            str(tmp_path),
            "--topology-kind",
            "monorepo",
            "--default-execution-service",
            "worker",
            "--service-key",
            "worker",
            "--repo-root",
            str(service_root),
            "--version",
            "v1.3.10",
            "--branch",
            "beacon/v1.3.10",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    inputs = _branch_guard_inputs(tmp_path, version="v1.3.10", feature="demo")
    assert inputs["expected_branch"] == "beacon/v1.3.10"
    assert str(service_root) in inputs["git_roots"]
    assert "worker" in inputs["direct_delivery_services"]
    view = resolve_project_metadata_view(tmp_path, version="v1.3.10")
    assert view["selected_service"] == "worker"


def test_v1310_single_repo_branch_preflight_should_accept_service_key_alias(tmp_path: Path) -> None:
    _git(["git", "init", "-b", "main"], cwd=tmp_path)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=tmp_path)
    _git(["git", "config", "user.email", "beacon@example.com"], cwd=tmp_path)
    (tmp_path / "README.md").write_text("test\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=tmp_path)
    _git(["git", "commit", "-m", "init"], cwd=tmp_path)

    result = runner.invoke(
        app,
        [
            "doctor",
            "metadata",
            "create",
            "--project-root",
            str(tmp_path),
            "--topology-kind",
            "single_repo",
            "--default-execution-service",
            "beacon",
            "--service-key",
            "beacon",
            "--repo-root",
            str(tmp_path),
            "--version",
            "v1.3.10",
            "--branch",
            "main",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout

    inputs = _branch_guard_inputs(tmp_path, version="v1.3.10", feature="demo")
    payload = _run_branch_preflight(
        project_root=tmp_path,
        version="v1.3.10",
        run_id="run-test",
        feature="demo",
        auto_switch_branch=False,
        require_clean_worktree_for_switch=True,
        expected_branch=str(inputs["expected_branch"]),
        branch_prefix=str(inputs["branch_prefix"]),
        base_branch=str(inputs["base_branch"]),
        git_roots=list(inputs["git_roots"]),
        direct_delivery_services=list(inputs["direct_delivery_services"]),
    )
    assert payload["service_scope"]["unresolved_services"] == []
    assert "implement_direct_delivery_service_scope_unresolved" not in payload.get("reason_codes", [])


def test_v1310_prd_should_embed_project_metadata_context(tmp_path: Path) -> None:
    _seed_v1310_docs(tmp_path)
    service_root = tmp_path / "services" / "api"
    service_root.mkdir(parents=True, exist_ok=True)
    create = runner.invoke(
        app,
        [
            "doctor",
            "metadata",
            "create",
            "--project-root",
            str(tmp_path),
            "--topology-kind",
            "monorepo",
            "--default-execution-service",
            "api",
            "--service-key",
            "api",
            "--repo-root",
            str(service_root),
            "--version",
            "v1.3.10",
            "--branch",
            "beacon/v1.3.10",
            "--json",
        ],
    )
    assert create.exit_code == 0, create.stdout

    result = runner.invoke(
        app,
        [
            "prd",
            "create",
            "Beacon Metadata Contract",
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.10",
            "--mode",
            "rule",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    canonical = json.loads(Path(payload["canonical_path"]).read_text(encoding="utf-8"))
    compile_payload = json.loads(Path(payload["compile_path"]).read_text(encoding="utf-8"))
    assert canonical["project_metadata_context"]["metadata_ref"] == ".beacon/metadata/project-version-metadata.json"
    assert canonical["project_metadata_context"]["resolved_metadata_view"]["selected_service"] == "api"
    assert compile_payload["project_metadata_context"]["resolved_metadata_view"]["selected_branch"] == "beacon/v1.3.10"
    assert ".beacon/metadata/project-version-metadata.json" in canonical["source_refs"]


def test_v1310_qa_should_block_when_project_metadata_branch_contract_fails(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(tmp_path / ".runtime-ledger"))
    _seed_v1310_docs(tmp_path)
    service_root = tmp_path / "services" / "api"
    service_root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", "main"], cwd=service_root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=service_root)
    _git(["git", "config", "user.name", "Test User"], cwd=service_root)
    (service_root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=service_root)
    _git(["git", "commit", "-m", "init"], cwd=service_root)
    create = runner.invoke(
        app,
        [
            "doctor",
            "metadata",
            "create",
            "--project-root",
            str(tmp_path),
            "--topology-kind",
            "monorepo",
            "--default-execution-service",
            "api",
            "--service-key",
            "api",
            "--repo-root",
            str(service_root),
            "--version",
            "v1.3.10",
            "--branch",
            "beacon/v1.3.10",
            "--json",
        ],
    )
    assert create.exit_code == 0, create.stdout
    result = runner.invoke(
        app,
        ["qa", "run", "demo-feature", "--project-root", str(tmp_path), "--version", "v1.3.10", "--json"],
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_codes"] == ["project_metadata_contract_blocked"]
    assert payload["project_metadata_verification"]["status"] == "fail"


def test_v1310_release_should_block_when_project_metadata_branch_contract_fails(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(tmp_path / ".runtime-ledger"))
    version = "v1.3.10"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)
    service_root = tmp_path / "services" / "api"
    service_root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", "main"], cwd=service_root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=service_root)
    _git(["git", "config", "user.name", "Test User"], cwd=service_root)
    (service_root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=service_root)
    _git(["git", "commit", "-m", "init"], cwd=service_root)
    create = runner.invoke(
        app,
        [
            "doctor",
            "metadata",
            "create",
            "--project-root",
            str(tmp_path),
            "--topology-kind",
            "monorepo",
            "--default-execution-service",
            "api",
            "--service-key",
            "api",
            "--repo-root",
            str(service_root),
            "--version",
            version,
            "--branch",
            "beacon/v1.3.10",
            "--json",
        ],
    )
    assert create.exit_code == 0, create.stdout
    result = runner.invoke(app, ["release", "check", version, "--project-root", str(tmp_path)])
    assert result.exit_code == 1, result.stdout
    assert "project metadata contract" in result.stdout
    assert "expected_branch" in result.stdout
