from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.help import _render_human
from beacon.main import app
from beacon.utils.help_support import build_help_payload
from beacon.utils.implement_mode_playbooks import (
    FORBIDDEN_PUBLIC_IMPLEMENT_MODE_SKILLS,
    IMPLEMENT_MODE_PLAYBOOKS,
    PUBLIC_IMPLEMENT_SKILL,
    recommend_implement_mode,
    validate_public_implement_route,
)
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime import write_json
from beacon.utils.skill_eval_kit import default_route_stability_cases, validate_cases


VERSION = "v1.4.10"
FEATURE = "implement-mode-human-playbooks-and-routing-contract"
SLUG = "implement-mode-human-playbooks-and-routing-contract"

runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_frozen_feature(root: Path) -> None:
    docs = root / "docs" / "beacon" / VERSION
    for rel in (
        "SUMMARY.md",
        "execution/index.md",
        f"prd/{SLUG}.md",
        f"user-story/{SLUG}.md",
        f"qa/test-cases/{SLUG}.md",
        f"research/{SLUG}.md",
        f"source-architecture/{SLUG}.md",
    ):
        path = docs / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {rel}\n", encoding="utf-8")
    freeze_revision_state(root, version=VERSION, feature=FEATURE)


def test_single_public_implement_entrypoint() -> None:
    for skill_path in (
        Path("skills/beacon/beacon-implement/SKILL.md"),
        Path(".agents/skills/beacon-implement/SKILL.md"),
    ):
        skill_text = skill_path.read_text(encoding="utf-8")

        assert "name: beacon-implement" in skill_text
        assert "only public implementation entrypoint" in skill_text
        assert "references/implement-single.md" in skill_text
        assert "references/implement-team.md" in skill_text
        assert "references/implement-ralph.md" in skill_text
        for forbidden in FORBIDDEN_PUBLIC_IMPLEMENT_MODE_SKILLS:
            assert f"name: {forbidden}" not in skill_text


def test_mode_playbooks_have_required_sections() -> None:
    for mode in ("single", "team", "ralph"):
        playbook = IMPLEMENT_MODE_PLAYBOOKS[mode]
        source_path = Path(f"skills/beacon/beacon-implement/references/implement-{mode}.md")
        packaged_path = Path(f".agents/skills/beacon-implement/references/implement-{mode}.md")
        text = source_path.read_text(encoding="utf-8")
        assert packaged_path.read_text(encoding="utf-8") == text
        for field in ("purpose", "admission_conditions", "expected_evidence", "boundary"):
            assert playbook.get(field)
        for heading in ("## Purpose", "## Admission", "## Command", "## Evidence", "## Boundary"):
            assert heading in text
        assert f"--mode {mode}" in text


def test_mode_recommendation_rules(tmp_path: Path) -> None:
    single = recommend_implement_mode(feature=FEATURE, project_root=tmp_path, version=VERSION)
    team = recommend_implement_mode(feature=FEATURE, project_root=tmp_path, version=VERSION, prompt="use team subagent lanes")
    ralph = recommend_implement_mode(feature=FEATURE, project_root=tmp_path, version=VERSION, prompt="continue Ralph multi-round closure")

    assert single["recommended_mode"] == "single"
    assert team["recommended_mode"] == "team"
    assert ralph["recommended_mode"] == "ralph"
    assert single["canonical_command"].endswith(f'--version {VERSION} --mode single')
    assert team["canonical_command"].endswith(f'--version {VERSION} --mode team')
    assert ralph["canonical_command"].endswith(f'--version {VERSION} --mode ralph')


def test_ralph_boundary_is_not_verdict() -> None:
    playbook = IMPLEMENT_MODE_PLAYBOOKS["ralph"]
    boundary = str(playbook["boundary"]).lower()

    assert "never replaces qa" in boundary
    assert "release" in boundary
    assert "gate" in boundary
    assert "frozen truth" in boundary


def test_recommendation_includes_reason_and_command(tmp_path: Path) -> None:
    recommendation = recommend_implement_mode(feature=FEATURE, project_root=tmp_path, version=VERSION)

    assert recommendation["public_skill"] == PUBLIC_IMPLEMENT_SKILL
    assert recommendation["recommended_mode"] == "single"
    assert recommendation["reason"]
    assert recommendation["canonical_command"] == f'beacon implement run "{FEATURE}" --project {tmp_path} --version {VERSION} --mode single'
    assert recommendation["playbook_ref"].endswith("implement-single.md")

    rendered = _render_human(
        {
            "feature": FEATURE,
            "docs_version": VERSION,
            "runtime_version": VERSION,
            "implement_mode_recommendation": recommendation,
            "next_step": {"action": "implement", "reason": "test", "command": recommendation["canonical_command"]},
        }
    )

    assert "implement mode" in rendered
    assert "public skill : beacon-implement" in rendered
    assert "--mode single" in rendered


def test_skill_eval_route_stability_cases() -> None:
    cases = default_route_stability_cases()
    validation = validate_cases(cases)
    implement_cases = {case["expected_mode"]: case for case in cases if case.get("expected_public_skill") == PUBLIC_IMPLEMENT_SKILL}

    assert validation["status"] == "pass"
    assert set(implement_cases) == {"single", "team", "ralph"}
    for mode, case in implement_cases.items():
        assert case["expected_route"] == f"beacon-implement --mode {mode}"
        assert case["forbidden_public_skills"] == list(FORBIDDEN_PUBLIC_IMPLEMENT_MODE_SKILLS)


def test_nonexistent_mode_public_skills_fail_closed() -> None:
    for forbidden in FORBIDDEN_PUBLIC_IMPLEMENT_MODE_SKILLS:
        payload = validate_public_implement_route(forbidden)
        assert payload["status"] == "blocked"
        assert payload["reason_code"] == "forbidden_public_implement_mode_skill"
        assert payload["redirect_skill"] == PUBLIC_IMPLEMENT_SKILL


def test_mode_playbooks_preserve_truth_boundaries(tmp_path: Path) -> None:
    recommendation = recommend_implement_mode(
        feature=FEATURE,
        project_root=tmp_path,
        version=VERSION,
        next_step={
            "action": "implement",
            "reason": "implementation_repair_required",
            "command": f'beacon implement run "{FEATURE}" --project {tmp_path} --version {VERSION} --mode ralph',
        },
    )
    serialized = json.dumps(recommendation, ensure_ascii=False).lower()

    assert recommendation["recommended_mode"] == "ralph"
    assert "rewrite" not in serialized
    assert "verdict" not in recommendation["canonical_command"].lower()
    assert "never replaces qa" in recommendation["authority_boundary"].lower()


def test_help_does_not_show_stale_mode_when_final_gate_blocks(tmp_path: Path) -> None:
    _seed_frozen_feature(tmp_path)
    write_json(
        tmp_path / ".beacon" / "ralph" / f"{SLUG}.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "version": VERSION,
            "phase": "running",
            "current_blocker": "implementation_repair_required",
            "next_action": "implement",
            "recommended_command": f'beacon implement run "{FEATURE}" --project {tmp_path} --version {VERSION} --mode ralph',
        },
    )

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["next_step"]["action"] == "human_review"
    assert payload["implement_mode_recommendation"] == {}


def test_single_mode_completion_does_not_force_ralph(tmp_path: Path) -> None:
    _seed_frozen_feature(tmp_path)
    write_json(
        tmp_path / ".beacon" / "implement" / "run-single-mode" / "state.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "run_id": "run-single-mode",
            "mode": "single",
            "status": "completed",
            "runner": "native-single",
            "generated_at": "2026-05-24T00:00:00+00:00",
        },
    )

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["execution_surface"]["implement_mode"] == "single"
    assert payload["execution_surface"]["ralph_status"] == ""
    assert payload["next_step"]["action"] != "ralph"
