from __future__ import annotations

import importlib
from pathlib import Path

report_module = importlib.import_module("beacon.commands.report")
status_module = importlib.import_module("beacon.commands.status")
board_launcher_module = importlib.import_module("beacon.utils.board_launcher")


def test_v143_report_human_summary_should_surface_research_projection_sections() -> None:
    text = report_module._human_summary(
        {
            "run_id": "latest",
            "release_scorecard": {
                "release_ready": True,
                "gate": {"status": "Pass", "blocked_count": 0},
                "qa": {"status": "passed", "execution_mode": "feature-aware", "evidence_done": True},
                "research_projection": {
                    "present": True,
                    "section_count": 2,
                    "sections": {
                        "business_flow": ["frozen flow remains explicit"],
                        "state_machine": ["planned -> verified"],
                    },
                },
            },
        }
    )

    assert "- research_projection_present: `True`" in text
    assert "- research_projection_section_count: `2`" in text
    assert "- research_projection_sections: `business_flow, state_machine`" in text


def test_v143_status_impl_should_print_release_research_summary(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(status_module, "newest_run_id", lambda *_args, **_kwargs: "")
    monkeypatch.setattr(status_module, "resolve_target_version", lambda *_args, **_kwargs: "v1.4.3")
    monkeypatch.setattr(status_module, "read_json", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "compute_memory_metrics", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "compute_workflow_progress", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "workflow_memory_transaction_contract", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "compute_coverage_metrics", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "build_material_audit", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(status_module, "build_requirement_package_gate", lambda *_args, **_kwargs: {"status": "pass", "failure_categories": []})
    monkeypatch.setattr(status_module, "describe_project_version_context", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        status_module,
        "build_help_payload",
        lambda *_args, **_kwargs: {
            "lifecycle": {},
            "workflow_progress_display": {},
            "revision_id": "R1",
        },
    )
    monkeypatch.setattr(status_module, "load_implementation_plan_progress", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "build_requirement_clarity_gate_payload", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "load_requirement_clarity_state", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "build_technical_review_gate_payload", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "load_technical_review_state", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "load_qa_status", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "build_resume_contract", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "load_keep_discard_engine", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "build_release_scorecard", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        status_module,
        "summarize_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": True,
            "gate_status": "Pass",
            "qa_status": "passed",
            "qa_execution_mode": "feature-aware",
            "qa_evidence_done": True,
            "main_kpi": "false_complete_rate",
            "main_kpi_score": 88,
            "decision_keep": 2,
            "decision_review": 1,
            "decision_discard": 0,
            "research_projection_present": True,
            "research_projection_section_count": 2,
            "research_projection_sections": ["business_flow", "state_machine"],
        },
    )
    monkeypatch.setattr(status_module, "acceptance_projection_transaction_contract", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        status_module,
        "evaluate_semantic_contract",
        lambda *_args, **_kwargs: {"status": "not_applicable", "reason_code": "", "message": "", "artifacts": {}, "details": {}},
    )
    monkeypatch.setattr(status_module, "build_runtime_projection", lambda *_args, **_kwargs: {"projects": [], "runs": [], "board": {}, "lifecycle": {}})
    monkeypatch.setattr(status_module, "list_projects", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(status_module, "load_project_detail", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "sync_projection", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(status_module, "load_support_surface_summary", lambda *_args, **_kwargs: {})

    exit_code = status_module._status_impl(
        board=True,
        verbose=False,
        project_root=str(tmp_path),
        version="v1.4.3",
        feature="Research Projection Feature",
        run_id="",
        change_intent="",
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "- release.research: present sections=business_flow,state_machine count=2" in output


def test_v143_board_workbench_should_surface_research_projection_summary(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        board_launcher_module,
        "build_runtime_projection",
        lambda *_args, **_kwargs: {
            "display_name": "Beacon",
            "project_key": "beacon",
            "runs": [],
            "run_events": [],
            "artifact_refs": [],
            "board": {"current_stage": "release", "progress_label": "ready", "health_status": "healthy", "next_action": "release"},
            "lifecycle": {"current_stage": "release", "progress_label": "ready", "blocked": False, "blocked_reason": ""},
            "materials": {"prd": "ready", "user_story": "ready", "test_case": "ready"},
            "requirement_completeness": {},
            "supplement_task": {},
            "re_freeze_transaction": {},
            "git_scopes": [],
            "runtime_corroboration": "pass",
        },
    )
    monkeypatch.setattr(board_launcher_module, "load_implementation_plan_progress", lambda *_args, **_kwargs: {"status": "completed", "next_task_id": "", "blocked_task_ids": [], "counts": {}})
    monkeypatch.setattr(
        board_launcher_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "delivery": {"type": "initial"},
            "acceptance": {"status": "pass"},
            "revision_binding": {"revision_id": "R1"},
            "research_projection": {
                "present": True,
                "sections": {
                    "business_flow": ["frozen path"],
                    "state_machine": ["planned -> verified"],
                },
            },
        },
    )
    monkeypatch.setattr(board_launcher_module, "build_acceptance_kit_projection", lambda *_args, **_kwargs: {"summary": {}})
    monkeypatch.setattr(board_launcher_module, "_build_operator_actions", lambda *_args, **_kwargs: [])

    payload = board_launcher_module.build_operator_workbench_payload(
        tmp_path,
        version="v1.4.3",
        feature="Research Projection Feature",
        prototype_status={"status": "frozen", "review_status": "approved", "gate_ready": True, "drift_status": "pass"},
    )

    assert payload["execution_board"]["wave_grouping"]["research_projection_present"] is True
    assert payload["execution_board"]["wave_grouping"]["research_projection_sections"] == ["business_flow", "state_machine"]
    assert payload["review_surface"]["release_scorecard_summary"]["research_projection_present"] is True

    html = board_launcher_module.render_operator_workbench_html(payload)
    assert "Research Projection" in html
    assert "business_flow, state_machine" in html
