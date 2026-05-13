"""Support helpers for host-scheduled automation capability reporting."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def build_automation_capabilities_payload(project_root: Path) -> dict[str, Any]:
    automation_root = project_root / "automation"
    codex_root = automation_root / "codex"
    jobs_root = automation_root / "jobs"
    launchd_root = automation_root / "launchd"
    docs_path = project_root / "docs" / "analysis" / "codex-automations-and-beacon-capability-guide.md"

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
        "assets": {
            "docs": str(docs_path.relative_to(project_root)) if docs_path.exists() else "",
            "automation_root": str(automation_root.relative_to(project_root)) if automation_root.exists() else "",
            "codex_specs": _sorted_relative_files(codex_root),
            "job_wrappers": _sorted_relative_files(jobs_root),
            "launchd_examples": _sorted_relative_files(launchd_root),
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

    lines = [
        "# Beacon Automation Capabilities",
        "",
        f"- project_root: `{payload.get('project_root', '')}`",
        f"- docs: `{assets.get('docs', '')}`",
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
    lines.extend(["", "## Recommendations"])
    for item in recommendations:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"
