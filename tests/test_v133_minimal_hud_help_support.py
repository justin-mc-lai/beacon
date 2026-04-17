from __future__ import annotations

from pathlib import Path

from beacon.utils.help_support import build_help_payload
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime import write_json


FEATURE = "beacon-v1.3.3-minimal-hud-scenarios-and-implementation"
SLUG = "beacon-v1.3.3-minimal-hud-scenarios-and-implementation"
VERSION = "v1.3.3"


def _seed_docs(root: Path) -> None:
    docs = root / "docs" / "beacon" / VERSION
    (docs / "user-story").mkdir(parents=True, exist_ok=True)
    (docs / "prd").mkdir(parents=True, exist_ok=True)
    (docs / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (docs / "user-story" / f"{SLUG}.md").write_text("# User Story\n", encoding="utf-8")
    (docs / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (docs / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    write_json(
        docs / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json",
        {"entries": [{"ac_id": "AC-001", "tc_id": "TC-001", "evidence_path": ".beacon/evidence/TC-001.json"}]},
    )
    evidence = root / ".beacon" / "evidence" / "TC-001.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text("{}", encoding="utf-8")


def test_v133_help_payload_should_include_minimal_hud_and_hud_refs(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    write_json(
        tmp_path / ".beacon" / "implement" / "run-impl-001" / "state.json",
        {
            "schema_version": "1.0",
            "run_id": "run-impl-001",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "completed",
            "mode": "team",
            "runner": "codex-subagents",
            "host_runtime": "codex",
            "team_execution": {
                "hud": {
                    "json": ".beacon/state/team-hud/impl-team.json",
                    "html": f"docs/beacon/{VERSION}/execution/codex-subagents/{SLUG}/run-impl-001/index.html",
                }
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
            "evidence_done": True,
            "execution_mode": "feature-aware",
            "run_id": "run-qa-001",
        },
    )

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    minimal_hud = payload.get("minimal_hud", {})
    assert minimal_hud.get("scenario") in {"S2", "S3", "S4", "S6"}
    lines = minimal_hud.get("lines", [])
    assert isinstance(lines, list) and lines
    assert len(lines) <= 3

    hud = payload.get("hud", {})
    assert hud.get("team_hud_json") == ".beacon/state/team-hud/impl-team.json"
    assert hud.get("team_hud_html")
    assert hud.get("ralph_state_json", "") in {"", f".beacon/ralph/{SLUG}.json"}
