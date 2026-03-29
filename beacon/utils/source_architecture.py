"""Generate human-friendly source architecture docs from the current Beacon code tree."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, write_json
from beacon.utils.versioning import resolve_target_version

DOC_FILES = (
    "index.md",
    "overall-system-map.md",
    "command-surface-and-module-map.md",
    "lifecycle-memory-and-state.md",
    "skills-prompts-and-project-workflows.md",
    "workflow-and-artifact-flow.md",
    "qa-implement-release-feedback-loop.md",
    "sync-contract.md",
)


def source_architecture_dir(project_root: Path, *, version: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved_version / "source-architecture"


def source_architecture_generation_path(project_root: Path, *, version: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved_version / ".machine" / "execution" / "source-architecture-generation.json"


def _relative(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _beacon_source_paths(project_root: Path) -> list[Path]:
    source_root = project_root / "beacon"
    if not source_root.exists():
        return []
    return sorted(
        [
            path
            for path in source_root.rglob("*.py")
            if "__pycache__" not in path.parts
        ]
    )


def _collect_inputs(project_root: Path) -> dict[str, Any]:
    source_paths = _beacon_source_paths(project_root)
    command_paths = sorted([path for path in source_paths if "commands" in path.parts and path.name != "__init__.py"])
    util_paths = sorted([path for path in source_paths if "utils" in path.parts])
    adapter_paths = sorted([path for path in source_paths if "adapters" in path.parts])
    fingerprints = {_relative(path, project_root): _sha256_file(path) for path in source_paths}
    aggregate_hash = hashlib.sha256(json.dumps(fingerprints, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return {
        "source_paths": source_paths,
        "command_paths": command_paths,
        "util_paths": util_paths,
        "adapter_paths": adapter_paths,
        "fingerprints": fingerprints,
        "aggregate_hash": aggregate_hash,
    }


def _command_name(path: Path) -> str:
    name = path.stem
    aliases = {
        "user_story": "user-story",
        "auto_test": "auto-test",
        "data_dictionary": "data-dictionary",
        "evolution_summary": "evolution-summary",
        "ralph_bridge": "ralph-bridge",
        "test_case": "test-case",
        "test_progress": "test-progress",
        "ui_spec": "ui-spec",
    }
    return aliases.get(name, name.replace("_", "-"))


def _top_dirs(paths: list[Path], project_root: Path) -> list[str]:
    return sorted({_relative(path.parent, project_root) for path in paths})


def _render_index(version: str) -> str:
    return "\n".join(
        [
            f"# Beacon {version} Source Architecture Index",
            "",
            "## Purpose",
            "",
            "This directory is the generated, human-friendly projection of the current Beacon source tree.",
            "",
            "## Recommended Reading Order",
            "",
            "1. `./overall-system-map.md`",
            "2. `./command-surface-and-module-map.md`",
            "3. `./lifecycle-memory-and-state.md`",
            "4. `./skills-prompts-and-project-workflows.md`",
            "5. `./workflow-and-artifact-flow.md`",
            "6. `./qa-implement-release-feedback-loop.md`",
            "7. `./sync-contract.md`",
            "",
            "## Source Of Truth",
            "",
            "- generated from the current `beacon/` source tree",
            "- human requirement docs explain why the line exists",
            "- this directory explains how the code is currently organized",
            "",
        ]
    ) + "\n"


def _render_overall_system_map(version: str, data: dict[str, Any], project_root: Path) -> str:
    command_paths = data["command_paths"]
    util_paths = data["util_paths"]
    adapter_paths = data["adapter_paths"]
    return "\n".join(
        [
            f"# Beacon {version} Overall System Map",
            "",
            "## One-line Positioning",
            "",
            "Beacon is a CLI kernel that keeps requirement materials, machine artifacts, runtime state, QA evidence, and release governance in one versioned system.",
            "",
            "## Core Layering",
            "",
            "```text",
            "beacon/main.py",
            "→ beacon/cli_factory.py",
            "→ beacon/commands/*",
            "→ beacon/utils/*",
            "→ beacon/adapters/*",
            "→ docs/beacon/<version> + .machine + .beacon runtime state",
            "```",
            "",
            "## Current Source Counts",
            "",
            f"- command modules: `{len(command_paths)}`",
            f"- utility modules: `{len(util_paths)}`",
            f"- adapter modules: `{len(adapter_paths)}`",
            "",
            "## Major Code Roots",
            "",
            *[f"- `{item}`" for item in _top_dirs(command_paths + util_paths + adapter_paths, project_root)],
            "",
        ]
    ) + "\n"


def _render_command_surface_map(version: str, data: dict[str, Any], project_root: Path) -> str:
    commands = sorted([(_command_name(path), _relative(path, project_root)) for path in data["command_paths"]], key=lambda item: item[0])
    lines = [
        f"# Beacon {version} Command Surface And Module Map",
        "",
        "## Entry Path",
        "",
        "The command surface is registered through:",
        "",
        "- `beacon/main.py`",
        "- `beacon/cli_factory.py`",
        "- `beacon/command_catalog.py`",
        "",
        "## Command Modules",
        "",
        "| Command | Module |",
        "| --- | --- |",
    ]
    for command, module_path in commands:
        lines.append(f"| `{command}` | `{module_path}` |")
    lines.extend(
        [
            "",
            "## Key Point",
            "",
            "Most complexity lives below the command functions, in state helpers, artifact helpers, project workflow helpers, and QA/release scoring helpers.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_lifecycle_memory_and_state(version: str, project_root: Path) -> str:
    lines = [
        f"# Beacon {version} Lifecycle, Memory, And State",
        "",
        "## Main State Surfaces",
        "",
        "- `beacon/utils/story_state.py`",
        "- `beacon/utils/revision_state.py`",
        "- `beacon/utils/workflow_memory.py`",
        "- `beacon/utils/qa_runtime.py`",
        "- `beacon/utils/control_plane.py`",
        "- `beacon/utils/learning_loop.py`",
        "",
        "## Runtime Roots",
        "",
        "- `.beacon/qa/`",
        "- `.beacon/qa/sessions/`",
        "- `.beacon/implement/<run_id>/`",
        "- `.beacon/state/`",
        "- `.beacon/debug/`",
        "",
        "## Closure Sequence",
        "",
        "```text",
        "draft → frozen → implemented → verified → accepted/released",
        "```",
        "",
    ]
    return "\n".join(lines)


def _render_skills_prompts_and_project_workflows(version: str) -> str:
    return "\n".join(
        [
            f"# Beacon {version} Skills, Prompts, And Project Workflows",
            "",
            "## Main Sources",
            "",
            "- `beacon/utils/implement_adapters.py`",
            "- `beacon/utils/skill_config.py`",
            "- `beacon/utils/project_skills.py`",
            "- `beacon/utils/context_files.py`",
            "- `beacon/commands/implement.py`",
            "- `beacon/commands/skill.py`",
            "- `beacon/commands/profile.py`",
            "- `beacon/commands/verify.py`",
            "",
            "## Key Distinction",
            "",
            "- implement adapters decide how code work runs",
            "- project profiles decide how a target project verifies/releases",
            "- prompt/skill docs decide how humans and agents enter the lifecycle",
            "",
        ]
    ) + "\n"


def _render_workflow_and_artifact_flow(version: str) -> str:
    return "\n".join(
        [
            f"# Beacon {version} Workflow And Artifact Flow",
            "",
            "```text",
            "user-story / prd / test-cases",
            "→ .machine/user-story / .machine/qa / .machine/execution",
            "→ implement runtime raw",
            "→ QA status / evidence / sessions",
            "→ gate / release scorecard",
            "→ feedback / rewrite / learning",
            "```",
            "",
            "## Truth Surfaces",
            "",
            "- `docs/beacon/<version>/` for human primary docs",
            "- `docs/beacon/<version>/.machine/` for machine projection",
            "- `.beacon/` for runtime state and evidence",
            "",
        ]
    ) + "\n"


def _render_qa_implement_release_feedback_loop(version: str) -> str:
    return "\n".join(
        [
            f"# Beacon {version} QA, Implement, Release, And Feedback Loop",
            "",
            "## Main Modules",
            "",
            "- QA: `beacon/commands/qa.py`, `beacon/utils/qa_feature.py`, `beacon/utils/qa_precision.py`",
            "- Implement: `beacon/commands/implement.py`, `beacon/utils/implement_native.py`",
            "- Release/Gate: `beacon/commands/gate.py`, `beacon/commands/release.py`, `beacon/commands/report.py`, `beacon/commands/status.py`",
            "- Learning: `beacon/utils/learning_loop.py`, `beacon/utils/debug_feedback.py`",
            "",
            "## Main Loop",
            "",
            "```text",
            "qa finding",
            "→ release/gate judgement",
            "→ implement follow-up",
            "→ technical archive",
            "→ requirement rewrite",
            "→ next QA / next version",
            "```",
            "",
        ]
    ) + "\n"


def _render_sync_contract(version: str) -> str:
    return "\n".join(
        [
            f"# Beacon {version} Source Architecture Sync Contract",
            "",
            "Structural code changes must update source architecture docs.",
            "",
            "At minimum, update these docs when changing:",
            "",
            "- command registration or command layering",
            "- story/revision/workflow state structures",
            "- `.machine` artifact shapes or paths",
            "- `.beacon` runtime directories",
            "- skill/profile/orchestration structures",
            "- QA → implement → feedback loop shape",
            "",
        ]
    ) + "\n"


def build_source_architecture_docs(project_root: Path, *, version: str) -> dict[str, str]:
    resolved_version = resolve_target_version(project_root, version)
    data = _collect_inputs(project_root)
    docs = {
        "index.md": _render_index(resolved_version),
        "overall-system-map.md": _render_overall_system_map(resolved_version, data, project_root),
        "command-surface-and-module-map.md": _render_command_surface_map(resolved_version, data, project_root),
        "lifecycle-memory-and-state.md": _render_lifecycle_memory_and_state(resolved_version, project_root),
        "skills-prompts-and-project-workflows.md": _render_skills_prompts_and_project_workflows(resolved_version),
        "workflow-and-artifact-flow.md": _render_workflow_and_artifact_flow(resolved_version),
        "qa-implement-release-feedback-loop.md": _render_qa_implement_release_feedback_loop(resolved_version),
        "sync-contract.md": _render_sync_contract(resolved_version),
    }
    return docs


def generate_source_architecture(project_root: Path, *, version: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    output_dir = source_architecture_dir(project_root, version=resolved_version)
    docs = build_source_architecture_docs(project_root, version=resolved_version)
    output_dir.mkdir(parents=True, exist_ok=True)
    written_files: list[str] = []
    for name, content in docs.items():
        path = output_dir / name
        path.write_text(content, encoding="utf-8")
        written_files.append(_relative(path, project_root))

    inputs = _collect_inputs(project_root)
    metadata = {
        "schema_version": "1.0",
        "version": resolved_version,
        "generated_at": now_iso(),
        "source_file_count": len(inputs["source_paths"]),
        "command_module_count": len(inputs["command_paths"]),
        "util_module_count": len(inputs["util_paths"]),
        "adapter_module_count": len(inputs["adapter_paths"]),
        "source_fingerprints": inputs["fingerprints"],
        "aggregate_hash": inputs["aggregate_hash"],
        "generated_docs": written_files,
    }
    metadata_path = source_architecture_generation_path(project_root, version=resolved_version)
    write_json(metadata_path, metadata)
    return {
        "status": "generated",
        "version": resolved_version,
        "output_dir": _relative(output_dir, project_root),
        "metadata_path": _relative(metadata_path, project_root),
        "generated_docs": written_files,
        "aggregate_hash": inputs["aggregate_hash"],
    }


def current_source_architecture_status(project_root: Path, *, version: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    metadata_path = source_architecture_generation_path(project_root, version=resolved_version)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    if not isinstance(metadata, dict):
        metadata = {}
    current_inputs = _collect_inputs(project_root)
    stored_hash = str(metadata.get("aggregate_hash") or "").strip()
    current_hash = str(current_inputs.get("aggregate_hash") or "").strip()
    return {
        "version": resolved_version,
        "metadata_exists": metadata_path.exists(),
        "metadata_path": _relative(metadata_path, project_root),
        "stored_hash": stored_hash,
        "current_hash": current_hash,
        "up_to_date": bool(metadata_path.exists() and stored_hash and stored_hash == current_hash),
        "generated_docs": metadata.get("generated_docs", []),
    }

