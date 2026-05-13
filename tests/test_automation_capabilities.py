from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.automation_capabilities import (
    build_automation_capabilities_payload,
    render_automation_capabilities_markdown,
)


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def test_automation_capabilities_payload_should_report_boundary_and_assets():
    payload = build_automation_capabilities_payload(ROOT)

    assert payload["boundary"]["scheduler_owner"] == "codex_automations_or_host_scheduler"
    assert payload["boundary"]["truth_owner"] == "beacon"
    assert "nightly-qa" in payload["supported_job_patterns"]
    assert payload["assets"]["docs"] == "docs/analysis/codex-automations-and-beacon-capability-guide.md"
    assert "automation/codex/nightly-qa.md" in payload["assets"]["codex_specs"]
    assert "automation/jobs/beacon-qa-job.sh" in payload["assets"]["job_wrappers"]


def test_automation_capabilities_markdown_should_render_human_sections():
    payload = build_automation_capabilities_payload(ROOT)
    text = render_automation_capabilities_markdown(payload)

    assert "# Beacon Automation Capabilities" in text
    assert "## Boundary" in text
    assert "## Supported Job Patterns" in text
    assert "## Codex Prompt Specs" in text
    assert "## Host Scheduler Assets" in text


def test_automation_capabilities_cli_should_support_json_and_human_output():
    human = runner.invoke(app, ["automation", "capabilities", "--project-root", str(ROOT)])
    assert human.exit_code == 0, human.stdout
    assert "Beacon Automation Capabilities" in human.stdout
    assert "nightly-qa" in human.stdout

    machine = runner.invoke(app, ["automation", "capabilities", "--project-root", str(ROOT), "--json"])
    assert machine.exit_code == 0, machine.stdout
    payload = json.loads(machine.stdout)
    assert payload["assets"]["automation_root"] == "automation"
    assert "gated-implement" in payload["supported_job_patterns"]


def test_v145_docs_should_link_codex_automations_capability_surfaces():
    summary = (ROOT / "docs" / "beacon" / "v1.4.5" / "SUMMARY.md").read_text(encoding="utf-8")
    index_doc = (ROOT / "docs" / "beacon" / "v1.4.5" / "execution" / "index.md").read_text(encoding="utf-8")

    assert "docs/analysis/codex-automations-and-beacon-capability-guide.md" in summary
    assert "automation/README.md" in summary
    assert "beacon automation capabilities --project-root ." in summary

    assert "Codex Automations is supported as a host-scheduled capability plane" in index_doc
    assert "docs/analysis/codex-automations-and-beacon-capability-guide.md" in index_doc
    assert "beacon automation capabilities --project-root ." in index_doc
