from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.acceptance_kit import build_acceptance_kit_projection, load_acceptance_kit, summarize_acceptance_kit
from beacon.utils.runtime_projection import build_runtime_projection


VERSION = "v1.3.12"
FEATURE = "Beacon Acceptance Kit v1"
SLUG = "beacon-acceptance-kit-v1"


def _seed_docs(root: Path) -> None:
    docs = root / "docs" / "beacon" / VERSION
    (docs / "prd").mkdir(parents=True, exist_ok=True)
    (docs / "user-story").mkdir(parents=True, exist_ok=True)
    (docs / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs / "execution").mkdir(parents=True, exist_ok=True)
    (docs / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (docs / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (docs / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (docs / "user-story" / f"{SLUG}.md").write_text("# Story\n", encoding="utf-8")
    (docs / "qa" / "test-cases" / f"{SLUG}.md").write_text("# TC\n", encoding="utf-8")


def _seed_acceptance_kit(root: Path) -> None:
    path = root / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"acceptance-kit-{SLUG}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "version": VERSION,
                "verdict": "passed",
                "layers": {
                    "skill-contract": {"status": "pass", "source_truth_ref": "docs/beacon/v1.3.12/prd/beacon-acceptance-kit-v1.md"},
                    "scenario-suite": {"status": "pass", "source_truth_ref": "docs/beacon/v1.3.12/user-story/beacon-acceptance-kit-v1.md"},
                    "trace-scorecard": {"status": "pass", "source_truth_ref": "docs/beacon/v1.3.12/.machine/qa/beacon-acceptance-kit-v1.qa9-matrix.json"},
                    "real-project-proof": {"status": "pass", "source_truth_ref": ".beacon/transactions/acceptance-kit.json"},
                },
                "real_project_proof": {"status": "pass", "evidence_refs": [".beacon/transactions/acceptance-kit.json"], "source": "real-project-validation"},
                "regression_pass": True,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_v1312_acceptance_kit_should_emit_layered_verdicts(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_acceptance_kit(tmp_path)

    kit = load_acceptance_kit(tmp_path, version=VERSION, feature=FEATURE)
    summary = summarize_acceptance_kit(kit)
    projection = build_acceptance_kit_projection(tmp_path, version=VERSION, feature=FEATURE)

    assert summary["verdict"] == "passed"
    assert summary["contract_pass"] is True
    assert summary["scenario_pass"] is True
    assert summary["trace_pass"] is True
    assert summary["real_project_pass"] is True
    assert summary["regression_pass"] is True
    assert projection["present"] is True
    assert projection["reason_code"] == ""


def test_v1312_runtime_projection_should_embed_acceptance_kit(tmp_path: Path, monkeypatch) -> None:
    _seed_docs(tmp_path)
    _seed_acceptance_kit(tmp_path)

    monkeypatch.setattr("beacon.utils.runtime_projection.resolve_target_version", lambda *_args, **_kwargs: VERSION)
    monkeypatch.setattr(
        "beacon.utils.runtime_projection.build_help_payload",
        lambda *_args, **_kwargs: {
            "current_stage": "implemented",
            "blocked": False,
            "blocked_reason": "",
            "next_step": {"action": "qa"},
            "execution_surface": {"implement_mode": "ralph", "ralph_phase": "execute"},
            "requirement_completeness": {
                "status": "blocked",
                "target_stage": "qa",
                "blocked_subgates": ["skill-contract"],
                "downgraded_subgates": [],
                "focus_areas": ["story gap"],
                "trace_loop_status": "supplement_required",
                "human_loop_handoff": {"recommended_command": "beacon user-story create", "focus_areas": ["story gap"]},
            },
        },
    )
    monkeypatch.setattr("beacon.utils.runtime_projection.load_qa_status", lambda *_args, **_kwargs: {"feature": FEATURE, "status": "passed"})
    monkeypatch.setattr("beacon.utils.runtime_projection.load_current_qa_session", lambda *_args, **_kwargs: {"session_id": "qa-1", "runner_type": "browser-use"})

    payload = build_runtime_projection(tmp_path, docs_version=VERSION, feature=FEATURE)

    assert payload["board"]["acceptance_kit_status"] == "Contract Pass"
    assert payload["board"]["acceptance_kit_verdict"] == "passed"
    assert payload["acceptance_kit"]["summary"]["all_layers_passed"] is True
