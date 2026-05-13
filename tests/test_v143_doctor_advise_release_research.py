from __future__ import annotations

import json
import importlib
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime import write_json


runner = CliRunner()
VERSION = "v1.4.3"
FEATURE = "Doctor Advise Release Research Projection"
SLUG = "doctor-advise-release-research-projection"
help_support_module = importlib.import_module("beacon.utils.help_support")


def _seed_docs(root: Path) -> None:
    docs = root / "docs" / "beacon" / VERSION
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (docs / "prd").mkdir(parents=True, exist_ok=True)
    (docs / "user-story").mkdir(parents=True, exist_ok=True)
    (docs / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (docs / "execution").mkdir(parents=True, exist_ok=True)
    (docs / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (docs / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (docs / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (docs / "user-story" / f"{SLUG}.md").write_text("# User Story\n", encoding="utf-8")
    (docs / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    write_json(docs / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json", {"entries": []})


def test_v143_doctor_advise_should_expose_release_research_in_json_and_text(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    monkeypatch.setattr(
        help_support_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": True,
            "gate": {"status": "Pass", "blocked_count": 0, "reason_codes": []},
            "qa": {"status": "passed", "execution_mode": "feature-aware", "evidence_done": True},
            "acceptance": {"status": "pass", "continue_decision": "ready_for_release"},
            "research_projection": {
                "present": True,
                "section_count": 2,
                "sections": {
                    "business_flow": ["explicit release path"],
                    "state_machine": ["freeze -> qa -> release"],
                },
                "source": f"research:docs/beacon/{VERSION}/research/{SLUG}.md",
                "source_artifact": f"docs/beacon/{VERSION}/.machine/user-story/{SLUG}.json",
            },
        },
    )
    write_json(
        tmp_path / ".beacon" / "qa" / "status.json",
        {
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "passed",
            "execution_mode": "feature-aware",
            "evidence_done": True,
            "run_id": "run-qa-001",
        },
    )

    json_result = runner.invoke(
        app,
        ["doctor", "advise", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--json"],
    )
    assert json_result.exit_code == 0, json_result.stdout
    payload = json.loads(json_result.stdout)
    assert payload["release_research"]["present"] is True
    assert payload["release_research"]["sections"] == ["business_flow", "state_machine"]
    assert payload["surface_explanation"]["release_research"] == payload["release_research"]

    text_result = runner.invoke(
        app,
        ["doctor", "advise", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE],
    )
    assert text_result.exit_code == 0, text_result.stdout
    assert "release_research: present=True sections=business_flow,state_machine count=2" in text_result.stdout
