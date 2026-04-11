"""Small wrapper around team HUD paths."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.subagent_runtime import team_hud_html_path, team_hud_json_path


def resolve_team_hud_paths(project_root: Path, *, team_name: str, version: str, feature: str, run_id: str, surface_dir: str) -> dict[str, Path]:
    return {
        "json": team_hud_json_path(project_root, team_name=team_name),
        "html": team_hud_html_path(project_root, version=version, feature=feature, run_id=run_id, surface_dir=surface_dir),
    }
