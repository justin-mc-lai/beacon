from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.1.7"
FEATURE = "Project Skill Feature"
SLUG = "project-skill-feature"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / VERSION
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "user-story" / f"{SLUG}.md").write_text(
        """# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Verify | Profile-backed verification |\n""",
        encoding="utf-8",
    )
    (base / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text(f"# Release {VERSION}\n", encoding="utf-8")
    (base / "SUMMARY.md").write_text(f"# Summary {VERSION}\n", encoding="utf-8")


def _write_demo_profile(root: Path) -> None:
    (root / "beacon.config.yaml").write_text(
        """
project_skills:
  registry:
    shell-skill:
      id: shell-skill
      kind: external
      entry: /bin/sh
      capabilities:
        - verify
      supported_stages:
        - verify
      evidence_contract:
        - uat_pipeline_run
        - gateway_smoke
  profiles:
    demo:
      project: demo
      profile_id: demo
      description: Demo profile
      skills:
        verify: shell-skill
      required_evidence:
        - uat_pipeline_run
        - gateway_smoke
      required_cases:
        - upload_mp4_success
      orchestration:
        nodes:
          -
            id: pipeline
            stage: verify
            skill: shell-skill
            command_template: "python3 -c 'from pathlib import Path; p=Path(r\"{project_root}/.beacon/pipeline.txt\"); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(\"ok\")'"
            produces_evidence:
              - uat_pipeline_run
          -
            id: gateway
            stage: verify
            skill: shell-skill
            command_template: "python3 -c 'from pathlib import Path; p=Path(r\"{project_root}/.beacon/gateway.txt\"); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(\"ok\")'"
            produces_evidence:
              - gateway_smoke
            produces_cases:
              - upload_mp4_success
  default_profile: demo
""".strip()
        + "\n",
        encoding="utf-8",
    )


def _write_contract_profile(root: Path) -> None:
    (root / "beacon.config.yaml").write_text(
        """
project_skills:
  profiles:
    rolo-check:
      project: rolo
      profile_id: rolo-check
      description: Contract drift demo
      skills:
        verify: rolo-dev
      required_evidence: []
      required_cases: []
      contracts:
        -
          id: upload-types
          description: upload types stay aligned
          sources:
            -
              path: docs/beacon/v1.3.0/user-story/splash-marketing-content.md
              required_tokens:
                - GIF
                - 视频
            -
              path: report-svr/app/services/sts_upload_service.go
              required_tokens:
                - .gif
                - .mp4
  default_profile: rolo-check
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_profile_create_rolo_example_should_write_profile_and_registry(tmp_path: Path):
    result = _invoke(["profile", "create", "rolo", "rolo-uat", "--example", "rolo-uat", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "created"

    show = _invoke(["profile", "show", "rolo-uat", "--project-root", str(tmp_path), "--json"])
    assert show.exit_code == 0, show.stdout
    profile_payload = json.loads(show.stdout)
    profile = profile_payload["profile"]
    assert profile["project"] == "rolo"
    assert profile["skills"]["verify"] == "rolo-dev"
    assert "upload_mp4_success" in profile["required_cases"]


def test_skill_registry_list_should_include_builtin_and_external_skills(tmp_path: Path):
    _invoke(["profile", "create", "rolo", "rolo-uat", "--example", "rolo-uat", "--project-root", str(tmp_path)])
    result = _invoke(["skill", "registry", "list", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    ids = {item["id"] for item in payload["skills"]}
    assert {"native-single", "native-team", "qa9-default", "rolo-dev"} <= ids


def test_verify_run_should_execute_profile_orchestration_and_satisfy_gate(tmp_path: Path):
    _seed_docs(tmp_path)
    _write_demo_profile(tmp_path)
    bind = _invoke(["skill", "bind", FEATURE, "--profile", "demo", "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert bind.exit_code == 0, bind.stdout

    result = _invoke(["verify", "run", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["orchestration"]["status"] == "completed"
    assert payload["gate"]["status"] == "pass"
    assert (tmp_path / ".beacon" / "pipeline.txt").exists()
    assert (tmp_path / ".beacon" / "gateway.txt").exists()


def test_help_should_be_profile_aware_and_recommend_verify_run(tmp_path: Path):
    _seed_docs(tmp_path)
    _write_demo_profile(tmp_path)
    _invoke(["skill", "bind", FEATURE, "--profile", "demo", "--project-root", str(tmp_path), "--version", VERSION])
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--runner", "native-single"])

    result = _invoke(["help", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["project_profile"]["profile_id"] == "demo"
    assert payload["next_step"]["action"] == "verify-run"
    assert "beacon verify run" in payload["next_step"]["command"]


def test_review_accept_should_block_when_project_required_cases_missing(tmp_path: Path):
    _seed_docs(tmp_path)
    _write_demo_profile(tmp_path)
    _invoke(["skill", "bind", FEATURE, "--profile", "demo", "--project-root", str(tmp_path), "--version", VERSION])
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--runner", "native-single"])
    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(json.dumps({"status": "passed", "summary": {"blocked": 0}}), encoding="utf-8")

    result = _invoke(["review", "accept", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason"] == "project_profile_gate_blocked"
    assert any(item.get("reason_code") == "required_case_missing" for item in payload.get("issues", []))


def test_doctor_advise_should_surface_contract_drift_from_profile(tmp_path: Path):
    _write_contract_profile(tmp_path)
    _invoke(["skill", "bind", FEATURE, "--profile", "rolo-check", "--project-root", str(tmp_path), "--version", VERSION])
    drift_docs = tmp_path / "docs" / "beacon" / "v1.3.0" / "user-story"
    drift_docs.mkdir(parents=True, exist_ok=True)
    (drift_docs / "splash-marketing-content.md").write_text("支持 GIF 和 视频\n", encoding="utf-8")
    drift_code = tmp_path / "report-svr" / "app" / "services"
    drift_code.mkdir(parents=True, exist_ok=True)
    (drift_code / "sts_upload_service.go").write_text('var AllowedExtensions = map[string]bool{".jpg": true, ".png": true, ".pdf": true}', encoding="utf-8")

    result = _invoke(["doctor", "advise", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert "contract_drift" in payload["blocking_reasons"]
