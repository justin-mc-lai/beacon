from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.test_case import _build_entries_from_qa_case_rows
from beacon.cli_factory import build_app
from beacon.utils import project_hooks
from beacon.utils.project_hooks import ALLOWED_HOOK_CODES, plan_hook, run_hook, validate_hook_contract
from beacon.utils.requirement_parsing import extract_qa_case_rows


VERSION = "v1.4.10"
FEATURE = "project-lifecycle-hook-skill-toolkit-contract"


def _write_hook(root: Path, hook_id: str = "rolo-post-implement-uat", *, hook_code: str = "post_implement_pre_qa", trigger_policy: str = "manual_confirmed", enabled: bool = True, body_extra: str = "") -> Path:
    path = root / "docs" / "beacon" / "hooks" / f"{hook_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
hook_id: {hook_id}
hook_code: {hook_code}
project: rolo
enabled: {str(enabled).lower()}
trigger_policy: {trigger_policy}
skill: rolo-dev-git-to-pipeline-uat
command_template: "rolo_dev.sh rolo-dev-git-to-pipeline-uat --service {{service_name}} --pipeline uat_app_service"
produces_evidence:
  - uat_pipeline_run
  - pipeline_status
failure_route: implement
---

# Rolo Post Implement UAT Hook

## Purpose

Deliver a completed implementation to UAT before formal QA.

## Admission

- Implementation evidence is available.
- Operator confirms the side-effect action.

## Evidence

- UAT pipeline run id.
- Pipeline status.

## Failure Route

Return to implement repair when delivery fails.

{body_extra}
""",
        encoding="utf-8",
    )
    return path


def test_project_level_hook_truth(tmp_path: Path) -> None:
    _write_hook(tmp_path)
    version_hook = tmp_path / "docs" / "beacon" / VERSION / "hooks" / "rolo-post-implement-uat.md"

    payload = plan_hook(tmp_path, "rolo-post-implement-uat", version=VERSION, feature=FEATURE)

    assert payload["status"] == "planned"
    assert payload["admission"]["path"] == "docs/beacon/hooks/rolo-post-implement-uat.md"
    assert not version_hook.exists()


def test_single_file_hook_contract() -> None:
    root = Path("unused")

    assert "post_implement_pre_qa" in ALLOWED_HOOK_CODES
    assert "qa_diagnostics" in ALLOWED_HOOK_CODES
    assert "post_qa_pre_release" in ALLOWED_HOOK_CODES
    assert "post_release" in ALLOWED_HOOK_CODES
    assert not (root / "docs" / "beacon" / VERSION / "hooks").exists()


def test_finite_hook_code_taxonomy(tmp_path: Path) -> None:
    _write_hook(tmp_path, hook_code="unknown_hook")

    payload = validate_hook_contract(tmp_path, "rolo-post-implement-uat")

    assert payload["blocked"] is True
    assert "unknown_hook_code" in payload["reason_codes"]


def test_hook_admission_requires_manual_confirmation(tmp_path: Path) -> None:
    _write_hook(tmp_path, trigger_policy="manual_confirmed")

    blocked = run_hook(tmp_path, "rolo-post-implement-uat", version=VERSION, feature=FEATURE)
    confirmed = run_hook(tmp_path, "rolo-post-implement-uat", version=VERSION, feature=FEATURE, confirm=True)

    assert blocked["blocked"] is True
    assert blocked["reason_code"] == "manual_confirmation_required"
    assert confirmed["status"] == "passed"
    assert confirmed["side_effect_executed"] is True


def test_hook_evidence_topology(tmp_path: Path) -> None:
    _write_hook(tmp_path)

    payload = run_hook(tmp_path, "rolo-post-implement-uat", version=VERSION, feature=FEATURE, dry_run=True)

    runtime_path = tmp_path / payload["evidence_paths"]["runtime"]
    latest_path = tmp_path / payload["evidence_paths"]["latest_read_model"]
    assert runtime_path.exists()
    assert latest_path == tmp_path / "docs" / "beacon" / ".machine" / "hooks" / "rolo-post-implement-uat.latest.json"
    assert json.loads(latest_path.read_text(encoding="utf-8"))["runtime_evidence_only"] is True


def test_human_toolkit_commands(tmp_path: Path) -> None:
    _write_hook(tmp_path)
    app = build_app(package_version="0-test")
    runner = CliRunner()

    listed = runner.invoke(app, ["hooks", "list", "--project-root", str(tmp_path), "--json"])
    planned = runner.invoke(app, ["hooks", "plan", "rolo-post-implement-uat", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--json"])
    dry_run = runner.invoke(app, ["hooks", "run", "rolo-post-implement-uat", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--dry-run", "--json"])
    confirmed = runner.invoke(app, ["hooks", "run", "rolo-post-implement-uat", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--confirm", "--json"])
    status = runner.invoke(app, ["hooks", "status", "rolo-post-implement-uat", "--project-root", str(tmp_path), "--feature", FEATURE, "--json"])
    disabled = runner.invoke(app, ["hooks", "disable", "rolo-post-implement-uat", "--project-root", str(tmp_path), "--json"])

    for result in (listed, planned, dry_run, confirmed, status, disabled):
        assert result.exit_code == 0, result.output
    assert json.loads(listed.output)["hook_count"] == 1
    assert json.loads(planned.output)["status"] == "planned"
    assert json.loads(dry_run.output)["status"] == "planned"
    assert json.loads(confirmed.output)["status"] == "passed"
    assert json.loads(status.output)["truth_authority"] is False
    assert json.loads(disabled.output)["status"] == "disabled"


def test_project_hooks_human_facing_skill_packaged() -> None:
    # 1+6 merge: governor hooks surface lives in SUPPORT.md under beacon-gov-hooks.
    skill_text = Path("skills/beacon/beacon-gov-hooks/SUPPORT.md").read_text(encoding="utf-8")

    assert "name: beacon-gov-hooks" in skill_text
    assert "migrated from `beacon-project-hooks`" in skill_text
    assert "beacon hooks list --project ." in skill_text
    assert 'beacon hooks plan "<hook-id>" --project . --version <version> --feature "<feature>"' in skill_text
    assert 'beacon hooks run "<hook-id>" --project . --version <version> --feature "<feature>" --dry-run' in skill_text
    assert 'beacon hooks run "<hook-id>" --project . --version <version> --feature "<feature>" --confirm' in skill_text
    assert "docs/beacon/hooks/<hook-id>.md" in skill_text
    assert "docs/beacon/<version>/hooks/" in skill_text
    assert "Side-effect hooks require explicit operator confirmation" in skill_text


def test_fixture_hooks_are_not_global_defaults(tmp_path: Path) -> None:
    _write_hook(tmp_path, "beacon-post-release-local-install", hook_code="post_release")
    _write_hook(tmp_path, "rolo-post-implement-uat", hook_code="post_implement_pre_qa")
    _write_hook(tmp_path, "rolo-qa-debuglab", hook_code="qa_diagnostics")

    app = build_app(package_version="0-test")
    result = CliRunner().invoke(app, ["hooks", "list", "--project-root", str(tmp_path), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert {item["hook_id"] for item in payload["hooks"]} == {
        "beacon-post-release-local-install",
        "rolo-post-implement-uat",
        "rolo-qa-debuglab",
    }
    assert payload["truth_root"] == "docs/beacon/hooks"


def test_hook_authority_boundary(tmp_path: Path) -> None:
    _write_hook(tmp_path, body_extra="This hook will set release verdict when it passes.")

    payload = validate_hook_contract(tmp_path, "rolo-post-implement-uat")

    assert payload["blocked"] is True
    assert "hook_authority_bypass" in payload["reason_codes"]


def test_unsafe_hook_requests_fail_closed(tmp_path: Path) -> None:
    _write_hook(tmp_path)

    hidden = run_hook(tmp_path, "rolo-post-implement-uat", version=VERSION, feature=FEATURE)
    missing = validate_hook_contract(tmp_path, "missing-hook")

    assert hidden["blocked"] is True
    assert hidden["reason_code"] == "manual_confirmation_required"
    assert missing["blocked"] is True
    assert "hook_file_missing" in missing["reason_codes"]


def test_explicit_gate_pytest_with_manual_confirmation_name_stays_automated() -> None:
    qa_path = Path("docs/beacon/archive/v1.4.10/qa/test-cases/project-lifecycle-hook-skill-toolkit-contract.md")
    rows = extract_qa_case_rows(qa_path.read_text(encoding="utf-8"), f"qa:test-cases:{qa_path}")
    entries = _build_entries_from_qa_case_rows(
        feature=FEATURE,
        feature_slug=FEATURE,
        qa_rows=rows,
        ac_items=[{"ac_id": "AC-001"}],
        ui_runner="playwright",
    )
    row = next(item for item in entries if item["tc_id"] == "TC-HOOK-004")

    assert row["layer"] == "gate"
    assert row["qa_type"] == "gate"
    assert row["automation"] == "auto"


def test_beacon_source_release_hook_contract_exists() -> None:
    path = Path("docs/beacon/hooks/beacon-post-release-local-install.md")

    assert path.exists()
    payload = validate_hook_contract(Path("."), "beacon-post-release-local-install", hook_code="post_release")

    assert payload["blocked"] is False
    assert payload["contract"]["trigger_policy"] == "manual_confirmed"
    assert "legacy_beacon_skill_cleanup" in payload["contract"]["produces_evidence"]
    assert "claude_global_beacon_subskills_install" in payload["contract"]["produces_evidence"]
    assert "claude_global_beacon_subskills_verify" in payload["contract"]["produces_evidence"]
    assert "codex_agent_surface_verify" in payload["contract"]["produces_evidence"]
    assert "global_beacon_cli_version" in payload["contract"]["produces_evidence"]


def _copy_beacon_source_hook(tmp_path: Path) -> None:
    source = Path("docs/beacon/hooks/beacon-post-release-local-install.md")
    target = tmp_path / "docs" / "beacon" / "hooks" / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def test_beacon_source_release_hook_requires_confirmation(tmp_path: Path) -> None:
    _copy_beacon_source_hook(tmp_path)

    payload = run_hook(
        tmp_path,
        "beacon-post-release-local-install",
        version=VERSION,
        feature="implement-mode-human-playbooks-and-routing-contract",
        hook_code="post_release",
    )

    assert payload["blocked"] is True
    assert payload["reason_code"] == "manual_confirmation_required"
    assert payload["side_effect_executed"] is False


def test_beacon_source_release_hook_confirmed_followup(tmp_path: Path, monkeypatch) -> None:
    _copy_beacon_source_hook(tmp_path)

    def fake_followup(project_root: Path, *, version: str, feature: str) -> dict:
        return {
            "schema_version": "1.0",
            "hook_id": "beacon-post-release-local-install",
            "version": version,
            "feature": feature,
            "status": "pass",
            "blocked": False,
            "reason_codes": [],
            "agent_surfaces": {
                "codex": {"setup_status": "PASS", "verify_status": "PASS"},
                "claude": {"setup_status": "PASS", "verify_status": "PASS"},
            },
            "launcher_setup": {"status": "PASS"},
            "cli_versions": {
                "beacon": {"stdout": f"Beacon CLI {version}", "status": "pass"},
                "beacon-cli": {"stdout": f"Beacon CLI {version}", "status": "pass"},
            },
        }

    monkeypatch.setattr("beacon.utils.project_hooks._run_beacon_post_release_local_install", fake_followup)

    payload = run_hook(
        tmp_path,
        "beacon-post-release-local-install",
        version=VERSION,
        feature="implement-mode-human-playbooks-and-routing-contract",
        hook_code="post_release",
        confirm=True,
    )

    assert payload["blocked"] is False
    assert payload["side_effect_executed"] is True
    followup = payload["post_release_followup"]
    assert followup["status"] == "pass"
    assert followup["agent_surfaces"]["codex"]["setup_status"] == "PASS"
    assert followup["agent_surfaces"]["codex"]["verify_status"] == "PASS"
    assert followup["agent_surfaces"]["claude"]["setup_status"] == "PASS"
    assert followup["agent_surfaces"]["claude"]["verify_status"] == "PASS"
    assert followup["launcher_setup"]["status"] == "PASS"
    assert VERSION in followup["cli_versions"]["beacon"]["stdout"]
    assert VERSION in followup["cli_versions"]["beacon-cli"]["stdout"]


def test_beacon_source_release_hook_checks_runtime_cli_version_not_docs_version(tmp_path: Path, monkeypatch) -> None:
    _copy_beacon_source_hook(tmp_path)

    class Result:
        exit_code = 0

        def __init__(self, payload: dict) -> None:
            self.payload = payload

    monkeypatch.setattr(project_hooks, "__toolkit_version__", "v1.5.2")
    monkeypatch.setattr(
        "beacon.utils.doctor_orchestrator.run_agent_surface_setup",
        lambda **_: Result({"status": "PASS", "result": {}}),
    )
    monkeypatch.setattr(
        "beacon.utils.doctor_orchestrator.run_agent_surface_verify",
        lambda **_: Result({"status": "PASS", "result": {}}),
    )
    monkeypatch.setattr(
        "beacon.utils.doctor_orchestrator.run_launcher_setup",
        lambda **_: Result({"status": "PASS"}),
    )
    monkeypatch.setattr(
        "beacon.utils.doctor_orchestrator.run_legacy_beacon_skills_cleanup",
        lambda **_: Result({"status": "PASS", "result": {"removed_count": 0, "removed": []}}),
    )
    monkeypatch.setattr(
        project_hooks,
        "_command_output",
        lambda args: {"stdout": "Beacon CLI v1.5.2", "status": "pass", "returncode": 0, "command": args},
    )

    payload = run_hook(
        tmp_path,
        "beacon-post-release-local-install",
        version="v1.6.0",
        feature="beacon-skill-harness-taxonomy-v160",
        hook_code="post_release",
        confirm=True,
    )

    assert payload["blocked"] is False
    followup = payload["post_release_followup"]
    assert followup["status"] == "pass"
    assert followup["version"] == "v1.6.0"
    assert followup["expected_runtime_version"] == "v1.5.2"
    assert not any("version_mismatch" in reason for reason in followup["reason_codes"])


def test_beacon_source_release_hook_collects_installation_evidence(tmp_path: Path, monkeypatch) -> None:
    test_beacon_source_release_hook_confirmed_followup(tmp_path, monkeypatch)


def test_beacon_source_release_hook_runs_legacy_skill_cleanup(tmp_path: Path, monkeypatch) -> None:
    _copy_beacon_source_hook(tmp_path)
    calls: list[dict[str, object]] = []

    class Result:
        exit_code = 0

        def __init__(self, payload: dict) -> None:
            self.payload = payload

    def fake_cleanup(**kwargs):
        calls.append(kwargs)
        return Result({"status": "PASS", "result": {"removed_count": 2, "removed": []}})

    monkeypatch.setattr(
        "beacon.utils.doctor_orchestrator.run_legacy_beacon_skills_cleanup",
        fake_cleanup,
    )
    monkeypatch.setattr(
        "beacon.utils.doctor_orchestrator.run_agent_surface_setup",
        lambda **_: Result({"status": "PASS", "result": {}}),
    )
    monkeypatch.setattr(
        "beacon.utils.doctor_orchestrator.run_agent_surface_verify",
        lambda **_: Result({"status": "PASS", "result": {}}),
    )
    monkeypatch.setattr(
        "beacon.utils.doctor_orchestrator.run_launcher_setup",
        lambda **_: Result({"status": "PASS"}),
    )
    monkeypatch.setattr(
        project_hooks,
        "_command_output",
        lambda args: {"stdout": "Beacon CLI v1.6.0", "status": "pass", "returncode": 0, "command": args},
    )
    monkeypatch.setattr(project_hooks, "__toolkit_version__", "v1.6.0")

    payload = run_hook(
        tmp_path,
        "beacon-post-release-local-install",
        version=VERSION,
        feature="beacon-skill-harness-taxonomy-v160",
        hook_code="post_release",
        confirm=True,
    )

    assert payload["blocked"] is False
    assert calls
    assert calls[0]["scope"] == "all"
    assert calls[0]["force"] is True
    followup = payload["post_release_followup"]
    assert followup["legacy_skill_cleanup"]["removed_count"] == 2
