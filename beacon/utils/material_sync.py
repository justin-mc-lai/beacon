"""Project requirement material sync helpers."""

from __future__ import annotations

import io
import os
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

import typer

from beacon.commands.test_case import create as create_test_case
from beacon.utils.story_state import sync_story_state_from_docs
from beacon.utils.versioning import resolve_target_version


def _discover_features(project_root: Path, version: str) -> list[str]:
    root = project_root / "docs" / "beacon" / version / "user-story"
    if not root.exists():
        return []
    return sorted(path.stem for path in root.glob("*.md") if path.is_file() and path.stem != "index")


def sync_feature_requirement_materials(
    project_root: Path,
    *,
    version: str,
    feature: str,
    dry_run: bool = False,
    overwrite_test_doc: bool = False,
    ui_runner: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    if dry_run:
        slug = str(feature or "").strip().lower().replace(" ", "-")
        return {
            "feature": feature,
            "version": resolved_version,
            "status": "planned",
            "story_path": f"docs/beacon/{resolved_version}/.machine/user-story/{slug}.json",
            "qa_matrix_path": f"docs/beacon/{resolved_version}/.machine/qa/{slug}.ac-test-matrix.json",
            "story_scenario_map_path": f"docs/beacon/{resolved_version}/.machine/qa/{slug}.story-scenario-map.json",
        }

    story_sync = sync_story_state_from_docs(project_root, resolved_version, feature)
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    previous_override = os.environ.get("BEACON_ALLOW_CONTEXT_VERSION_DRIFT")
    os.environ["BEACON_ALLOW_CONTEXT_VERSION_DRIFT"] = "1"
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            try:
                create_test_case(
                    feature=feature,
                    test_type="all",
                    version=resolved_version,
                    project=str(project_root),
                    output=None,
                    overwrite_doc=overwrite_test_doc,
                    qa_profile="web-full",
                    qa_types=None,
                    llm_auto=True,
                    llm_mode="auto",
                    automation_target_rate=0.85,
                    matrix_output=None,
                    expansion_profile="pua-web",
                    scenario_depth="standard",
                    mode="auto",
                    model="beacon-test-case-compiler",
                    json_output=False,
                    ui_runner=ui_runner,
                )
            except typer.Exit as exc:  # pragma: no cover - defensive, command exits via Typer only on parameter errors
                raise RuntimeError(f"test_case_sync_failed:{exc.exit_code}") from exc
    finally:
        if previous_override is None:
            os.environ.pop("BEACON_ALLOW_CONTEXT_VERSION_DRIFT", None)
        else:
            os.environ["BEACON_ALLOW_CONTEXT_VERSION_DRIFT"] = previous_override

    slug = str(story_sync.get("feature") or feature).strip().lower().replace(" ", "-")
    return {
        "feature": feature,
        "version": resolved_version,
        "status": "synced",
        "story_sync": story_sync,
        "qa_matrix_path": f"docs/beacon/{resolved_version}/.machine/qa/{slug}.ac-test-matrix.json",
        "qa9_matrix_path": f"docs/beacon/{resolved_version}/.machine/qa/{slug}.qa9-matrix.json",
        "story_scenario_map_path": f"docs/beacon/{resolved_version}/.machine/qa/{slug}.story-scenario-map.json",
        "command_stdout": stdout_capture.getvalue().strip(),
        "command_stderr": stderr_capture.getvalue().strip(),
    }


def sync_project_requirement_materials(
    project_root: Path,
    *,
    version: str,
    feature: str = "",
    all_features: bool = False,
    dry_run: bool = False,
    overwrite_test_doc: bool = False,
    ui_runner: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    features = [feature] if str(feature or "").strip() and not all_features else _discover_features(project_root, resolved_version)
    results: list[dict[str, Any]] = []
    for name in features:
        results.append(
            sync_feature_requirement_materials(
                project_root,
                version=resolved_version,
                feature=name,
                dry_run=dry_run,
                overwrite_test_doc=overwrite_test_doc,
                ui_runner=ui_runner,
            )
        )
    return {
        "schema_version": "1.0",
        "project_root": str(project_root),
        "version": resolved_version,
        "dry_run": dry_run,
        "feature_count": len(results),
        "results": results,
    }


def sync_change_loop_requirement_package(
    project_root: Path,
    *,
    version: str,
    feature: str,
    overwrite_test_doc: bool = False,
    ui_runner: str = "",
) -> dict[str, Any]:
    """Refresh the active machine requirement package during reopen/freeze change loops."""
    resolved_version = resolve_target_version(project_root, version)
    result = sync_feature_requirement_materials(
        project_root,
        version=resolved_version,
        feature=feature,
        dry_run=False,
        overwrite_test_doc=overwrite_test_doc,
        ui_runner=ui_runner,
    )
    return {
        "schema_version": "1.0",
        "project_root": str(project_root),
        "version": resolved_version,
        "feature": feature,
        "status": str(result.get("status") or "synced"),
        "story_path": str(result.get("story_sync", {}).get("path") or ""),
        "qa_matrix_path": str(result.get("qa_matrix_path") or ""),
        "qa9_matrix_path": str(result.get("qa9_matrix_path") or ""),
        "story_scenario_map_path": str(result.get("story_scenario_map_path") or ""),
        "story_sync": result.get("story_sync", {}),
    }
