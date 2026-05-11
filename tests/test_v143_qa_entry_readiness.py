from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.artifact_paths import execution_file_output, human_execution_file
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.story_state import feature_slug, load_story_state
from beacon.utils.writeback import record_implementation_writeback


VERSION = "v1.4.3"
FEATURES = [
    "beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface",
    "beacon-v1.4.3-design-review-surface-and-prototype-governance",
    "beacon-v1.4.3-governed-learning-recall-and-route-explainability",
    "beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation",
]


def _render_summary_markdown(payload: dict[str, object]) -> str:
    return (
        "# Beacon Implementation Summary\n\n"
        f"- feature: `{payload.get('feature', '')}`\n"
        f"- version: `{payload.get('version', '')}`\n"
        f"- run_id: `{payload.get('run_id', '')}`\n"
        f"- status: `{payload.get('status', '')}`\n"
        f"- runner: `{payload.get('runner', '')}`\n"
        "\n## Changed Files\n"
        + "\n".join(f"- `{item}`" for item in payload.get("changed_files", []))
        + "\n"
    )


def _rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_impl_evidence(root: Path, feature: str) -> None:
    slug = feature_slug(feature)
    base = root / "docs" / "beacon" / VERSION
    machine_exec = base / ".machine" / "execution"
    human_exec = base / "execution"
    marker = root / ".beacon" / "state" / f"implementation-{slug}.json"
    machine_exec.mkdir(parents=True, exist_ok=True)
    human_exec.mkdir(parents=True, exist_ok=True)

    story = load_story_state(root, version=VERSION, feature=feature, create_if_missing=True) or {}
    item_ids = [str(item.get("id") or "").strip() for item in story.get("items", []) if str(item.get("id") or "").strip()]
    run_id = f"run-{slug}-impl"
    record_implementation_writeback(
        root,
        version=VERSION,
        feature=feature,
        run_id=run_id,
        implemented_item_ids=item_ids,
        task_ids=[],
        changed_files=[
            "beacon/commands/review.py",
            "beacon/utils/ceo_review_surface.py",
            "beacon/utils/design_review_surface.py",
            "beacon/utils/learn_surface.py",
            "beacon/utils/support_surface_transactions.py",
        ],
    )
    write_json(
        marker,
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "feature": feature,
            "feature_slug": slug,
            "version": VERSION,
            "runner": "codex-subagents",
            "skill": "beacon:beacon-implement",
            "status": "completed",
            "generated_at": now_iso(),
        },
    )

    requirement_traceability = {
        "source_of_truth_root": f"docs/beacon/{VERSION}",
        "prd": f"docs/beacon/{VERSION}/prd/{slug}.md",
        "user_story": f"docs/beacon/{VERSION}/user-story/{slug}.md",
        "test_case": f"docs/beacon/{VERSION}/qa/test-cases/{slug}.md",
        "ac_matrix": f"docs/beacon/{VERSION}/.machine/qa/{slug}.ac-test-matrix.json",
        "requirement_completeness_ref": f"docs/beacon/{VERSION}/.machine/requirement/{slug}.completeness.json",
        "requirement_completeness_verdict": "freeze_ready",
        "revision_id": "R1",
        "implemented_item_ids": item_ids,
        "implemented_task_ids": [],
        "verified_task_ids": [],
    }
    delivery_surfaces = {
        "runtime_mode": "single",
        "shipped_surfaces": [
            "beacon-ceo-review",
            "beacon-design-review",
            "beacon-learn",
            "help/status route explainability",
        ],
        "partial_surfaces": [],
        "deferred_surfaces": [],
        "downgrade_rationale": "",
    }
    summary_payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "feature": feature,
        "feature_slug": slug,
        "version": VERSION,
        "runner": "codex-subagents",
        "adapter_type": "native",
        "skill": "beacon:beacon-implement",
        "status": "completed",
        "summary": "v1.4.3 support-surface implementation completed.",
        "changed_files": [
            "beacon/commands/review.py",
            "beacon/commands/help.py",
            "beacon/commands/status.py",
            "beacon/utils/ceo_review_surface.py",
            "beacon/utils/design_review_surface.py",
            "beacon/utils/learn_surface.py",
            "beacon/utils/support_surface_transactions.py",
        ],
        "verification": [{"command": "pytest -q tests/test_v143_*", "status": "passed"}],
        "implemented_task_ids": [],
        "verified_task_ids": [],
        "blocked_task_ids": [],
        "failed_task_ids": [],
        "artifact_updates": {"prd": {"required": False}},
        "request_path": "",
        "result_path": "",
        "stdout_path": "",
        "stderr_path": "",
        "branch_preflight_path": "",
        "branch_preflight": {},
        "plan_preflight_path": "",
        "plan_preflight": {},
        "implementation_plan": "",
        "implementation_plan_progress": {},
        "requirement_traceability": requirement_traceability,
        "delivery_surfaces": delivery_surfaces,
        "revision_cleanup": {},
        "skill_admission": {},
        "traceability_refs": [
            requirement_traceability["prd"],
            requirement_traceability["user_story"],
            requirement_traceability["test_case"],
            requirement_traceability["ac_matrix"],
        ],
        "implementation_marker": _rel(root, marker),
        "technical_archive": {
            "json": f"docs/beacon/{VERSION}/.machine/execution/technical-implementation-{slug}.json",
            "md": f"docs/beacon/{VERSION}/execution/technical-implementation-{slug}.md",
        },
        "change_document": {
            "json": f"docs/beacon/{VERSION}/.machine/change/{slug}.json",
            "md": f"docs/beacon/{VERSION}/change/{slug}.md",
        },
        "review_spec": {},
        "review_quality": {},
        "generated_at": now_iso(),
        "writeback": {},
    }
    summary_json = execution_file_output(root, VERSION, f"implementation-summary-{slug}.json")
    summary_md = human_execution_file(root, VERSION, f"implementation-brief-{slug}.md")
    write_json(summary_json, summary_payload)
    summary_md.write_text(_render_summary_markdown(summary_payload), encoding="utf-8")

    technical_json = execution_file_output(root, VERSION, f"technical-implementation-{slug}.json")
    technical_md = human_execution_file(root, VERSION, f"technical-implementation-{slug}.md")
    technical_payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": VERSION,
        "run_id": run_id,
        "runner": "codex-subagents",
        "skill": "beacon:beacon-implement",
        "summary": "v1.4.3 support surface runtime and route explainability implemented.",
        "changed_files": summary_payload["changed_files"],
        "services": [{"name": "beacon", "role": "runtime", "changed_files": summary_payload["changed_files"]}],
        "db_changes": {"none": True},
        "api_changes": {"none": True},
        "config_changes": [],
        "env_changes": [],
        "assumptions": [],
        "simplicity_notes": ["Reused support-surface transaction and review surfaces instead of adding new lifecycle commands."],
        "scope_guard": {"in_scope": True, "summary": "support-surface runtime closure only", "allowed_paths": ["beacon/commands", "beacon/utils", "docs/beacon/v1.4.3", "tests"]},
        "verification_signals": {"has_assumptions": False},
    }
    write_json(technical_json, technical_payload)
    technical_md.write_text("# Technical Implementation\n\n- status: completed\n", encoding="utf-8")


def materialize_v143_implementation_evidence(project_root: Path) -> None:
    for feature in FEATURES:
        _seed_impl_evidence(project_root, feature)
