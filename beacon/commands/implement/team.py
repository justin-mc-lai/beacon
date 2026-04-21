"""Team surface integration for implement command."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.team_surface import write_implement_to_qa_handoff


def write_team_handoff(
    project_root: Path,
    *,
    feature: str,
    version: str,
    team_id: str,
    results: dict[str, Any],
) -> None:
    """Write implement-to-QA handoff for team mode."""
    handoff_data = {
        "feature": feature,
        "version": version,
        "team_id": team_id,
        "mode": "team",
        "results": results,
    }

    write_implement_to_qa_handoff(project_root, handoff_data)


def validate_team_mode(mode: str, adapter_id: str, runtime_family: str) -> bool:
    """Validate if team mode is applicable."""
    if mode == "team":
        return True

    if adapter_id == "codex-subagents":
        return True

    if runtime_family == "claude-code":
        return True

    return False
