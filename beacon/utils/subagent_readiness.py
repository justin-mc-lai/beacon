"""Readiness checks for host-native subagent/team delegation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from beacon.utils.global_boundaries import path_mentions_global_boundaries, project_global_boundaries_path
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version

_SUPPORTED_HOSTS = {"codex", "claude"}


def detect_host_runtime(host_runtime: str | None = None) -> str:
    value = str(host_runtime or "").strip().lower()
    if value in _SUPPORTED_HOSTS:
        return value
    env_value = str(os.environ.get("BEACON_HOST_RUNTIME", "")).strip().lower()
    if env_value in _SUPPORTED_HOSTS:
        return env_value
    codex_present = _codex_skill_root().exists()
    claude_present = _claude_skill_root().exists()
    if codex_present and not claude_present:
        return "codex"
    if claude_present and not codex_present:
        return "claude"
    if codex_present and claude_present:
        return "codex"
    return "unknown"


def _codex_skill_root() -> Path:
    return Path.home() / ".agents" / "skills" / "beacon"


def _claude_skill_root() -> Path:
    return Path.home() / ".claude" / "skills" / "beacon"


def runtime_readiness_precheck(
    project_root: Path | str,
    *,
    host_runtime: str | None = None,
) -> dict[str, Any]:
    root = Path(project_root)
    resolved_host = detect_host_runtime(host_runtime)
    global_boundaries = project_global_boundaries_path(root)
    checks: list[dict[str, Any]] = []

    if resolved_host == "unknown":
        return {
            "schema_version": "1.0",
            "check": "runtime-readiness",
            "status": "blocked",
            "reason_code": "host_runtime_unknown",
            "host_runtime": resolved_host,
            "checks": [],
            "recommended_command": "set --host-runtime codex|claude when running subagent readiness checks",
        }

    if resolved_host == "codex":
        skill_root = _codex_skill_root()
        context_file = root / "AGENTS.md"
    else:
        skill_root = _claude_skill_root()
        context_file = root / "CLAUDE.md"

    checks.append({"name": "skill_root_present", "ok": skill_root.exists(), "detail": str(skill_root)})
    checks.append({"name": "context_file_present", "ok": context_file.exists(), "detail": str(context_file)})
    checks.append({"name": "global_boundaries_present", "ok": global_boundaries.exists(), "detail": str(global_boundaries)})
    checks.append(
        {
            "name": "context_inherits_global_boundaries",
            "ok": context_file.exists() and path_mentions_global_boundaries(context_file, project_root=root),
            "detail": str(context_file),
        }
    )

    blocked = [item["name"] for item in checks if not bool(item.get("ok"))]
    return {
        "schema_version": "1.0",
        "check": "runtime-readiness",
        "status": "blocked" if blocked else "pass",
        "reason_code": "runtime_not_ready" if blocked else "",
        "host_runtime": resolved_host,
        "checks": checks,
        "blocked_checks": blocked,
        "recommended_command": (
            "beacon doctor setup-context --project-root ."
            if any(name in {"context_file_present", "context_inherits_global_boundaries", "global_boundaries_present"} for name in blocked)
            else ""
        ),
    }


def delegation_readiness_precheck(
    project_root: Path | str,
    *,
    feature: str,
    version: str = "auto",
) -> dict[str, Any]:
    root = Path(project_root)
    resolved_version = resolve_target_version(root, version)
    slug = feature_slug(feature)
    docs_root = root / "docs" / "beacon" / resolved_version
    checks = [
        {
            "name": "prd_present",
            "ok": (docs_root / "prd" / f"{slug}.md").exists(),
            "detail": str((docs_root / "prd" / f"{slug}.md").relative_to(root)),
        },
        {
            "name": "user_story_present",
            "ok": (docs_root / "user-story" / f"{slug}.md").exists(),
            "detail": str((docs_root / "user-story" / f"{slug}.md").relative_to(root)),
        },
        {
            "name": "test_case_present",
            "ok": (docs_root / "qa" / "test-cases" / f"{slug}.md").exists(),
            "detail": str((docs_root / "qa" / "test-cases" / f"{slug}.md").relative_to(root)),
        },
        {
            "name": "implementation_plan_present",
            "ok": (docs_root / ".machine" / "execution" / f"implementation-plan-{slug}.json").exists(),
            "detail": str((docs_root / ".machine" / "execution" / f"implementation-plan-{slug}.json").relative_to(root)),
        },
        {
            "name": "git_workflow_present",
            "ok": (docs_root / ".machine" / "execution" / f"git-workflow-{slug}.json").exists(),
            "detail": str((docs_root / ".machine" / "execution" / f"git-workflow-{slug}.json").relative_to(root)),
        },
        {
            "name": "qa_baseline_bundle_present",
            "ok": all(
                path.exists()
                for path in [
                    docs_root / ".machine" / "qa" / f"{slug}.ac-test-matrix.json",
                    docs_root / ".machine" / "qa" / f"{slug}.qa9-matrix.json",
                    docs_root / ".machine" / "qa" / f"{slug}.story-scenario-map.json",
                ]
            ),
            "detail": str((docs_root / ".machine" / "qa").relative_to(root)),
        },
    ]
    blocked = [item["name"] for item in checks if not bool(item.get("ok"))]
    return {
        "schema_version": "1.0",
        "check": "delegation-readiness",
        "status": "blocked" if blocked else "pass",
        "reason_code": "delegation_not_ready" if blocked else "",
        "feature": feature,
        "version": resolved_version,
        "checks": checks,
        "blocked_checks": blocked,
        "recommended_command": (
            f'beacon implement plan "{feature}" --project-root {root} --version {resolved_version}'
            if any(name in {"implementation_plan_present", "git_workflow_present"} for name in blocked)
            else ""
        ),
    }
