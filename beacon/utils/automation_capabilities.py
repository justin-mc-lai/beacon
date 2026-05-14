"""Support helpers for host-scheduled automation capability reporting."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.automation_executors import build_executor_capability_matrix
from beacon.utils.automation_queue import build_automation_queue_validation_payload, default_queue_path


def build_automation_capabilities_payload(project_root: Path) -> dict[str, Any]:
    automation_root = project_root / "automation"
    codex_root = automation_root / "codex"
    jobs_root = automation_root / "jobs"
    launchd_root = automation_root / "launchd"
    docs_path = project_root / "docs" / "analysis" / "codex-automations-and-beacon-capability-guide.md"
    queue_path = default_queue_path(project_root)
    queue_validation = build_automation_queue_validation_payload(project_root, queue_path) if queue_path.exists() else {}

    def _sorted_relative_files(root: Path) -> list[str]:
        if not root.exists():
            return []
        return sorted(
            str(path.relative_to(project_root))
            for path in root.rglob("*")
            if path.is_file()
        )

    return {
        "schema_version": "1.0",
        "project_root": str(project_root),
        "boundary": {
            "scheduler_owner": "codex_automations_or_host_scheduler",
            "truth_owner": "beacon",
            "queue_execution_owner": "host_wrapper",
            "gate_owner": "beacon",
            "notification_owner": "host_wrapper",
        },
        "supported_job_patterns": [
            "morning-status",
            "nightly-qa",
            "gated-implement",
        ],
        "feedback_loop": {
            "qa_feedback_ledger": ".beacon/automation/qa-feedback-ledger.json",
            "queue_update_entrypoint": "beacon automation update-queue --project-root .",
            "qa_summary_entrypoint": "beacon automation summarize-qa --project-root .",
            "shared_summary_entrypoint": "beacon automation build-summary --project-root . --job <job> --layer <layer>",
            "summary_schema": {
                "schema_version": "1.0",
                "required_fields": [
                    "summary_kind",
                    "project_root",
                    "job",
                    "layer",
                    "status",
                    "analysis.headline",
                    "analysis.summary_line",
                    "metrics",
                    "features",
                    "artifacts",
                    "notification",
                ],
            },
        },
        "bootstrap": {
            "init_entrypoint": "beacon automation init --project-root .",
            "ownership": "project_local_scaffold_generation",
            "toolkit_skill": "beacon-toolkit-automation",
        },
        "executor_matrix": build_executor_capability_matrix(),
        "assets": {
            "docs": str(docs_path.relative_to(project_root)) if docs_path.exists() else "",
            "automation_root": str(automation_root.relative_to(project_root)) if automation_root.exists() else "",
            "queue_path": str(queue_path.relative_to(project_root)) if queue_path.exists() else "",
            "codex_specs": _sorted_relative_files(codex_root),
            "job_wrappers": _sorted_relative_files(jobs_root),
            "launchd_examples": _sorted_relative_files(launchd_root),
        },
        "queue_contract": {
            "status": str(queue_validation.get("status", "missing") or "missing"),
            "error_count": int(queue_validation.get("error_count", 0) or 0),
        },
        "recommendations": [
            "keep scheduling outside Beacon core commands",
            "use explicit queue governance for candidate selection",
            "call Beacon public CLI only from host wrappers",
            "treat notification transport as host concern, not release truth",
        ],
    }


def render_automation_capabilities_markdown(payload: dict[str, Any]) -> str:
    assets = payload.get("assets", {}) if isinstance(payload.get("assets"), dict) else {}
    codex_specs = assets.get("codex_specs", []) if isinstance(assets.get("codex_specs"), list) else []
    job_wrappers = assets.get("job_wrappers", []) if isinstance(assets.get("job_wrappers"), list) else []
    launchd_examples = assets.get("launchd_examples", []) if isinstance(assets.get("launchd_examples"), list) else []
    boundary = payload.get("boundary", {}) if isinstance(payload.get("boundary"), dict) else {}
    recommendations = payload.get("recommendations", []) if isinstance(payload.get("recommendations"), list) else []
    patterns = payload.get("supported_job_patterns", []) if isinstance(payload.get("supported_job_patterns"), list) else []
    queue_contract = payload.get("queue_contract", {}) if isinstance(payload.get("queue_contract"), dict) else {}
    feedback_loop = payload.get("feedback_loop", {}) if isinstance(payload.get("feedback_loop"), dict) else {}
    bootstrap = payload.get("bootstrap", {}) if isinstance(payload.get("bootstrap"), dict) else {}
    executor_matrix = payload.get("executor_matrix", []) if isinstance(payload.get("executor_matrix"), list) else []

    lines = [
        "# Beacon Automation Capabilities",
        "",
        f"- project_root: `{payload.get('project_root', '')}`",
        f"- docs: `{assets.get('docs', '')}`",
        f"- queue_path: `{assets.get('queue_path', '')}`",
        f"- queue_status: `{queue_contract.get('status', '')}`",
        f"- queue_error_count: `{queue_contract.get('error_count', '')}`",
        "",
        "## Boundary",
        f"- scheduler_owner: `{boundary.get('scheduler_owner', '')}`",
        f"- truth_owner: `{boundary.get('truth_owner', '')}`",
        f"- queue_execution_owner: `{boundary.get('queue_execution_owner', '')}`",
        f"- gate_owner: `{boundary.get('gate_owner', '')}`",
        f"- notification_owner: `{boundary.get('notification_owner', '')}`",
        "",
        "## Supported Job Patterns",
    ]
    for item in patterns:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Codex Prompt Specs"])
    for item in codex_specs or ["(none)"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Job Wrappers"])
    for item in job_wrappers or ["(none)"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Host Scheduler Assets"])
    for item in launchd_examples or ["(none)"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Feedback Loop",
            f"- qa_feedback_ledger: `{feedback_loop.get('qa_feedback_ledger', '')}`",
            f"- qa_summary_entrypoint: `{feedback_loop.get('qa_summary_entrypoint', '')}`",
            f"- queue_update_entrypoint: `{feedback_loop.get('queue_update_entrypoint', '')}`",
            f"- shared_summary_entrypoint: `{feedback_loop.get('shared_summary_entrypoint', '')}`",
            "",
            "## Bootstrap",
            f"- init_entrypoint: `{bootstrap.get('init_entrypoint', '')}`",
            f"- ownership: `{bootstrap.get('ownership', '')}`",
            f"- toolkit_skill: `{bootstrap.get('toolkit_skill', '')}`",
            "",
            "## Executor Matrix",
        ]
    )
    for item in executor_matrix:
        if not isinstance(item, dict):
            continue
        lines.append(
            f"- `{item.get('executor', '')}`: tier=`{item.get('tier', '')}` status=`{item.get('status', '')}` "
            f"beacon_runtime_execution=`{item.get('beacon_runtime_execution', False)}`"
        )
    lines.extend(["", "## Recommendations"])
    for item in recommendations:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"
