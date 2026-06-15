"""Read-only oss-sync capability inventory for planner source parity."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DEFAULT_OSS_SYNC_ROOT = Path.home() / "Developer" / "Personal" / "oss-sync"

PARITY_SOURCE_PROFILES: dict[str, dict[str, Any]] = {
    "fission-ai-openspec": {
        "display_name": "OpenSpec",
        "aliases": ("openspec", "open-spec", "fission-ai/openspec"),
        "default_capabilities": (
            "directory_state_machine", "delta_spec_merge", "slash_command_dispatch",
            "cli_validate_archive", "multi_ide_schema", "workspace_planning",
        ),
    },
    "github-spec-kit": {
        "display_name": "Spec Kit",
        "aliases": ("spec-kit", "spec kit", "github/spec-kit"),
        "default_capabilities": (
            "constitution_spec_plan", "phase_gated_workflow",
            "lightweight_onboarding", "specs_directory_truth",
        ),
    },
    "garrytan-gstack": {
        "display_name": "gstack",
        "aliases": ("gstack", "garrytan/gstack"),
        "default_capabilities": (
            "browser_session_ops", "dev_ops_closure", "deploy_canary_ship",
            "host_runner_integration", "context_save_restore",
        ),
    },
    "everyinc-compound-engineering-plugin": {
        "display_name": "compound-engineering-plugin",
        "aliases": (
            "compound-engineering-plugin", "compound engineering",
            "compound-engineering", "everyinc/compound-engineering-plugin",
        ),
        "default_capabilities": (
            "persona_reviewer_catalog", "finding_synthesis", "autofix_routing",
            "diff_pr_scope_review", "plugin_marketplace", "iterative_optimization_loop",
        ),
    },
}

_SOURCE_REF_PATTERNS = (
    re.compile(r"oss-sync[/\\](?P<rel>[^:\s]+)", re.IGNORECASE),
    re.compile(r"github\.com[:/][^/\s]+/(?P<repo>[^/\s#?.]+)", re.IGNORECASE),
)


def default_oss_sync_root() -> Path:
    return DEFAULT_OSS_SYNC_ROOT


def _load_repos_index(root: Path) -> list[dict[str, Any]]:
    index_path = root / "index" / "repos.json"
    if not index_path.is_file():
        return []
    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    repos = payload.get("repositories")
    return repos if isinstance(repos, list) else []


def _load_cached_analysis(root: Path, slug: str) -> dict[str, Any] | None:
    analysis_path = root / "index" / "analysis" / f"{slug}.json"
    if not analysis_path.is_file():
        return None
    try:
        payload = json.loads(analysis_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _repo_slug(owner: str, repo: str) -> str:
    owner_text, repo_text = str(owner or "").strip(), str(repo or "").strip()
    return f"{owner_text}-{repo_text}" if owner_text and repo_text else (repo_text or owner_text)


def _match_profile(source_ref: str) -> str | None:
    blob = str(source_ref or "").strip().lower()
    if not blob:
        return None
    for slug, profile in PARITY_SOURCE_PROFILES.items():
        for alias in [slug.replace("-", " "), slug, *profile.get("aliases", ())]:
            if str(alias).strip().lower() in blob:
                return slug
    for pattern in _SOURCE_REF_PATTERNS:
        match = pattern.search(source_ref)
        if not match:
            continue
        rel = str(match.groupdict().get("rel") or match.groupdict().get("repo") or "").strip().lower()
        if not rel:
            continue
        for row_slug, profile in PARITY_SOURCE_PROFILES.items():
            if rel in row_slug or rel in str(profile.get("display_name", "")).lower():
                return row_slug
            for alias in profile.get("aliases", ()):
                if str(alias).lower() in rel or rel in str(alias).lower():
                    return row_slug
    return None


def _capabilities_from_analysis(analysis: dict[str, Any] | None, defaults: tuple[str, ...]) -> list[str]:
    capabilities = list(defaults)
    if not analysis:
        return capabilities
    if analysis.get("entrypoints"):
        capabilities.append("cli_or_runtime_entrypoint")
    skills_paths = analysis.get("skills_paths") or []
    if skills_paths:
        capabilities.append("host_skill_surfaces")
        if len(skills_paths) >= 5:
            capabilities.append("multi_skill_catalog")
    if analysis.get("docs_paths"):
        capabilities.append("documentation_surface")
    top = [str(x).lower() for x in (analysis.get("top_level_dirs") or [])]
    if "schemas" in top:
        capabilities.append("workflow_schema_registry")
    if "plugins" in top:
        capabilities.append("plugin_packaging")
    if any(n in top for n in ("canary", "browse", "bin")):
        capabilities.append("operational_tooling")
    return list(dict.fromkeys(capabilities))


def resolve_oss_sync_source_inventory(source_refs: list[str], *, oss_sync_root: Path | None = None) -> list[dict[str, Any]]:
    root = (oss_sync_root or default_oss_sync_root()).expanduser().resolve()
    repos = _load_repos_index(root)
    repo_by_slug = {_repo_slug(str(r.get("owner") or ""), str(r.get("repo") or "")): r for r in repos if isinstance(r, dict)}
    repo_by_slug.update({str(r.get("name") or "").strip().lower(): r for r in repos if isinstance(r, dict)})
    inventory, seen = [], set()
    for source_ref in source_refs:
        slug = _match_profile(source_ref)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        profile = PARITY_SOURCE_PROFILES[slug]
        analysis = _load_cached_analysis(root, slug)
        repo_row = repo_by_slug.get(slug) or repo_by_slug.get(profile["display_name"].lower())
        capabilities = _capabilities_from_analysis(analysis, tuple(profile.get("default_capabilities", ())))
        inventory.append({
            "source_ref": source_ref,
            "oss_sync_slug": slug,
            "display_name": profile["display_name"],
            "relative_path": (repo_row or {}).get("relative_path") or (analysis or {}).get("relative_path") or "",
            "upstream_url": (repo_row or {}).get("remote_fetch") or "",
            "analysis_status": (repo_row or {}).get("analysis_status") or ("complete" if analysis else "missing"),
            "learning_doc_path": (repo_row or {}).get("learning_doc_path") or "",
            "capabilities": capabilities,
            "inventory_required": True,
            "inventory_source": "oss_sync_index" if analysis or repo_row else "profile_defaults",
        })
    return inventory


def build_source_capability_inventory(
    prompt: str, source_refs: list[str], scope_mode: str, *, oss_sync_root: Path | None = None,
) -> list[dict[str, Any]]:
    if scope_mode != "full_parity" and not source_refs:
        return []
    oss_entries = resolve_oss_sync_source_inventory(source_refs, oss_sync_root=oss_sync_root)
    if oss_entries:
        return oss_entries
    refs = source_refs or ["user_prompt_source_reference"]
    return [{
        "source_ref": ref,
        "capabilities": ["reviewer_catalog", "finding_schema", "synthesis_pipeline", "autofix_routing", "scope_detection"],
        "inventory_required": True,
        "inventory_source": "fallback_defaults",
    } for ref in refs]
