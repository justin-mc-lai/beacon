from __future__ import annotations

import json
import subprocess
from pathlib import Path

from beacon import __toolkit_version__
from typer.testing import CliRunner

from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
VERSION = __toolkit_version__
FEATURE = "Beacon Iteration Governance"
SCRIPT = ROOT / "skills" / "beacon-iteration-governance" / "scripts" / "run_iteration_governance.sh"
runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _write_profile_config(root: Path) -> None:
    root.joinpath("beacon.config.yaml").write_text(
        f"""
project_skills:
  registry:
    beacon-iteration-governance:
      id: beacon-iteration-governance
      kind: external
      entry: {SCRIPT}
      capabilities:
        - verify
        - delivery
        - docs-governance
        - release-readiness
      supported_stages:
        - verify
        - delivery
      evidence_contract:
        - docs_current_contract
        - docs_material_audit
        - delivery_audit
        - release_readiness
  profiles:
    beacon-iter-dev:
      project: beacon
      profile_id: beacon-iter-dev
      description: Beacon source iteration governance profile.
      skills:
        verify: beacon-iteration-governance
        delivery: beacon-iteration-governance
      required_evidence:
        - docs_current_contract
        - docs_material_audit
      required_cases: []
      orchestration:
        nodes:
          -
            id: docs-contract
            stage: verify
            skill: beacon-iteration-governance
            command_template: "{{skill_entry}} quick --project-root {{repo_root}} --version {VERSION}"
            produces_evidence:
              - docs_current_contract
              - docs_material_audit
          -
            id: delivery-audit
            stage: delivery
            skill: beacon-iteration-governance
            command_template: "{{skill_entry}} delivery --project-root {{repo_root}} --version {VERSION}"
            produces_evidence:
              - delivery_audit
              - release_readiness
  default_profile: beacon-iter-dev
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_iteration_governance_skill_package_should_exist():
    base = ROOT / "skills" / "beacon-iteration-governance"
    assert (base / "SKILL.md").exists()
    assert (base / "metadata.json").exists()
    assert (base / "references" / "workflow.md").exists()
    assert (base / "examples" / "profile-integration.md").exists()
    assert SCRIPT.exists()


def test_iteration_governance_script_should_support_help():
    result = subprocess.run(["bash", str(SCRIPT), "--help"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "quick|delivery|full" in result.stdout


def test_iteration_governance_skill_should_be_usable_via_beacon_skill_registry_and_verify(tmp_path: Path):
    _write_profile_config(tmp_path)

    registry = _invoke(["skill", "registry", "list", "--project-root", str(tmp_path), "--json"])
    assert registry.exit_code == 0, registry.stdout
    registry_payload = json.loads(registry.stdout)
    ids = {item["id"] for item in registry_payload["skills"]}
    assert "beacon-iteration-governance" in ids

    bind = _invoke(["skill", "bind", FEATURE, "--profile", "beacon-iter-dev", "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert bind.exit_code == 0, bind.stdout

    verify = _invoke(
        [
            "verify",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--param",
            f"repo_root={ROOT}",
            "--json",
        ]
    )
    assert verify.exit_code == 0, verify.stdout
    payload = json.loads(verify.stdout)
    assert payload["orchestration"]["status"] == "completed"
    assert payload["gate"]["status"] == "pass"

    delivery = _invoke(
        [
            "orchestrate",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--stage",
            "delivery",
            "--param",
            f"repo_root={ROOT}",
            "--dry-run",
            "--json",
        ]
    )
    assert delivery.exit_code == 0, delivery.stdout
    delivery_payload = json.loads(delivery.stdout)
    assert delivery_payload["status"] == "dry_run"
    assert delivery_payload["nodes"][0]["skill_id"] == "beacon-iteration-governance"
    assert "delivery" in delivery_payload["nodes"][0]["command"]
