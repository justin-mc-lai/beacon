from __future__ import annotations

import json
from pathlib import Path

from beacon.commands.implement import commands as implement_commands
from beacon.utils.implementation_evidence import classify_behavior_evidence
from beacon.utils.program_admission import evaluate_program_next_action_admission


VERSION = "v0.0.12"
PROGRAM = "sidepilot-pi-host"
CURRENT_LAKE = "content-hub-foundation"
DOWNSTREAM_LAKE = "pi-host-ui-ux"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed_program(
    root: Path,
    *,
    next_action: str,
    downstream_depends_on: list[str] | None = None,
) -> Path:
    program_root = root / "docs" / "beacon" / VERSION / "programs" / PROGRAM
    program_root.mkdir(parents=True, exist_ok=True)
    (program_root / "program-manifest.md").write_text(
        "\n".join(
            [
                "---",
                f"program_slug: {PROGRAM}",
                f"version: {VERSION}",
                "program_plan_frozen: true",
                "lake_package_truth_frozen: true",
                "---",
                "",
                f"# {PROGRAM}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _write_json(
        program_root / "feature-graph.json",
        {
            "schema_version": "1.0",
            "program_slug": PROGRAM,
            "version": VERSION,
            "scope_mode": "full_parity",
            "program_plan_frozen": True,
            "lakes": [
                {
                    "slug": CURRENT_LAKE,
                    "feature_slug": CURRENT_LAKE,
                    "depends_on": [],
                    "parity_subset": ["content_hub"],
                    "status": "frozen",
                    "truth_status": "frozen",
                },
                {
                    "slug": DOWNSTREAM_LAKE,
                    "feature_slug": DOWNSTREAM_LAKE,
                    "depends_on": downstream_depends_on or [CURRENT_LAKE],
                    "parity_subset": ["pi_host_ui"],
                    "status": "frozen",
                    "truth_status": "frozen",
                },
            ],
        },
    )
    _write_json(
        program_root / "program-truth-freeze.json",
        {
            "schema_version": "1.0",
            "program_slug": PROGRAM,
            "version": VERSION,
            "status": "frozen",
            "blocked": False,
            "lakes": [
                {"slug": CURRENT_LAKE, "status": "frozen", "truth_promotion_complete": True},
                {"slug": DOWNSTREAM_LAKE, "status": "frozen", "truth_promotion_complete": True},
            ],
        },
    )
    _write_json(
        program_root / "program-run-state.json",
        {
            "schema_version": "1.0",
            "program_slug": PROGRAM,
            "version": VERSION,
            "next_action": next_action,
        },
    )
    return program_root


def test_program_next_action_blocks_wrong_lake(tmp_path: Path) -> None:
    _seed_program(tmp_path, next_action=f"beacon-gen-implement:{CURRENT_LAKE}")

    payload = evaluate_program_next_action_admission(tmp_path, version=VERSION, feature=DOWNSTREAM_LAKE)

    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "program_next_action_mismatch"
    assert payload["expected_lake_slug"] == CURRENT_LAKE
    assert payload["target_lake_slug"] == DOWNSTREAM_LAKE
    assert "implementation_marker" not in payload
    assert "implement_to_qa_handoff" not in payload


def test_program_next_action_allows_current_lake(tmp_path: Path) -> None:
    _seed_program(tmp_path, next_action=f"beacon-gen-implement:{CURRENT_LAKE}")

    payload = evaluate_program_next_action_admission(tmp_path, version=VERSION, feature=CURRENT_LAKE)

    assert payload["status"] == "pass"
    assert payload["program_slug"] == PROGRAM
    assert payload["lake_slug"] == CURRENT_LAKE
    assert payload["material_path"].endswith("program-truth-freeze.json")
    assert payload["next_action_source"].endswith("program-run-state.json")
    assert payload["next_action_target"] == CURRENT_LAKE


def test_program_dependency_closure_blocks_downstream_lake(tmp_path: Path) -> None:
    _seed_program(tmp_path, next_action=f"beacon-gen-implement:{DOWNSTREAM_LAKE}")

    payload = evaluate_program_next_action_admission(tmp_path, version=VERSION, feature=DOWNSTREAM_LAKE)

    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "program_dependency_unclosed"
    assert payload["unclosed_dependencies"][0]["feature_slug"] == CURRENT_LAKE
    assert payload["unclosed_dependencies"][0]["implementation_closed"] is False
    assert payload["unclosed_dependencies"][0]["qa_closed"] is False


def test_per_feature_implement_admission_unchanged_without_program_topology(tmp_path: Path) -> None:
    payload = evaluate_program_next_action_admission(tmp_path, version=VERSION, feature="standalone-feature")

    assert payload["status"] == "pass"
    assert payload["program_admission_required"] is False
    assert payload["reason_codes"] == []


def test_static_shell_ui_evidence_is_non_acceptance() -> None:
    payload = classify_behavior_evidence(
        {
            "surface": "pi-host-ui-ux",
            "required_surface_state": "coming_soon",
            "recovery_control": "no-op",
        }
    )

    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "static_shell_implementation_evidence"


def test_source_grep_only_tests_do_not_satisfy_behavior_ac() -> None:
    payload = classify_behavior_evidence(
        {
            "test_kind": "source_grep_only",
            "assertion": "readFileSync(route).toContain('Restore')",
        }
    )

    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "static_source_assertion_only"


def test_blocked_generator_writes_diagnostic_only(tmp_path: Path, monkeypatch) -> None:
    _seed_program(tmp_path, next_action=f"beacon-gen-implement:{CURRENT_LAKE}")
    monkeypatch.setattr(implement_commands, "build_legacy_cutover_preflight", lambda *args, **kwargs: {"blocked": False})
    monkeypatch.setattr(implement_commands, "build_requirement_package_gate", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(implement_commands, "_requirement_closure_preflight", lambda *args, **kwargs: {"blocked": False})
    monkeypatch.setattr(implement_commands, "_automation_runtime_preflight", lambda *args, **kwargs: {"blocked": False})
    monkeypatch.setattr(implement_commands, "gate_workspace_admission_or_block", lambda *args, **kwargs: None)

    exit_code, payload = implement_commands.run_implement_stage(
        feature=DOWNSTREAM_LAKE,
        project_root=tmp_path,
        version=VERSION,
        dry_run=True,
    )

    assert exit_code == 2
    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "program_next_action_mismatch"
    assert payload["diagnostic_only"] is True
    assert (tmp_path / ".beacon" / "implement" / payload["run_id"] / "state.json").exists()
    assert not (tmp_path / ".beacon" / "state" / f"implementation-{DOWNSTREAM_LAKE}.json").exists()
    assert not (
        tmp_path
        / "docs"
        / "beacon"
        / VERSION
        / ".machine"
        / "execution"
        / f"implementation-summary-{DOWNSTREAM_LAKE}.json"
    ).exists()
    assert not (tmp_path / ".beacon" / "handoffs" / "implement-to-qa" / DOWNSTREAM_LAKE).exists()
