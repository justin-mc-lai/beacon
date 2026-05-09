"""Project-local agent surface materialization for Beacon host-visible skills."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, write_json

_RULE_BLOCK_START = "<!-- BEACON:AGENT_SURFACE:START -->"
_RULE_BLOCK_END = "<!-- BEACON:AGENT_SURFACE:END -->"
_STATE_PATH = Path(".beacon") / "state" / "agent-surfaces.json"


@dataclass(frozen=True)
class AgentSurfaceTarget:
    """Resolved project-local surface target for one agent host."""

    agent: str
    skills_root: Path
    rules_path: Path | None = None
    rules_kind: str = ""


def packaged_beacon_skill_root() -> Path:
    """Return the packaged Beacon skill-pack root shipped with the repo/runtime."""
    return (Path(__file__).resolve().parents[2] / "skills" / "beacon").resolve()


def resolve_agent_surface_target(project_root: Path | str, agent: str) -> AgentSurfaceTarget:
    """Resolve project-local installation target for one supported agent."""
    root = Path(project_root).resolve()
    normalized = str(agent or "").strip().lower()
    if normalized == "winsurf":
        normalized = "windsurf"
    if normalized == "trae":
        return AgentSurfaceTarget(
            agent=normalized,
            skills_root=root / ".trae" / "skills",
            rules_path=root / ".trae" / "rules" / "project_rules.md",
            rules_kind="markdown",
        )
    if normalized == "claude":
        return AgentSurfaceTarget(
            agent=normalized,
            skills_root=root / ".claude" / "skills",
        )
    if normalized == "codex":
        return AgentSurfaceTarget(
            agent=normalized,
            skills_root=root / ".agents" / "skills",
        )
    if normalized == "cursor":
        return AgentSurfaceTarget(
            agent=normalized,
            skills_root=root / ".cursor" / "skills",
            rules_path=root / ".cursor" / "rules" / "beacon-agent-surface.mdc",
            rules_kind="cursor-mdc",
        )
    if normalized == "windsurf":
        return AgentSurfaceTarget(
            agent=normalized,
            skills_root=root / ".windsurf" / "skills",
            rules_path=root / ".windsurf" / "workflows" / "beacon-agent-surface.md",
            rules_kind="windsurf-workflow",
        )
    raise ValueError("agent must be one of: trae, claude, codex, cursor, windsurf")


def list_host_visible_skills(skill_root: Path | None = None) -> list[Path]:
    """List packaged Beacon host-visible skill directories."""
    base = (skill_root or packaged_beacon_skill_root()).resolve()
    skills = [
        child
        for child in base.iterdir()
        if child.is_dir() and (child / "SKILL.md").exists()
    ]
    return sorted(skills, key=lambda item: item.name)


def _hash_directory(path: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(node for node in path.rglob("*") if node.is_file())
    for file_path in files:
        relative = file_path.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _load_state(project_root: Path) -> dict[str, Any]:
    state_path = project_root / _STATE_PATH
    if not state_path.exists():
        return {"schema_version": "1.0", "agents": {}}
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema_version": "1.0", "agents": {}}
    if not isinstance(payload, dict):
        return {"schema_version": "1.0", "agents": {}}
    agents = payload.get("agents")
    if not isinstance(agents, dict):
        payload["agents"] = {}
    return payload


def _write_state(project_root: Path, payload: dict[str, Any], *, dry_run: bool) -> dict[str, Any]:
    state_path = project_root / _STATE_PATH
    existed = state_path.exists()
    current = state_path.read_text(encoding="utf-8") if state_path.exists() else ""
    next_content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    changed = current != next_content
    if not dry_run:
        write_json(state_path, payload)
    return {
        "path": str(state_path),
        "action": "planned" if dry_run else "updated" if existed else "created",
        "changed": changed or not existed,
    }


def _managed_skill_ids(agent_state: dict[str, Any]) -> set[str]:
    skills = agent_state.get("installed_skills")
    if not isinstance(skills, list):
        return set()
    return {
        str(item.get("id", "")).strip()
        for item in skills
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }


def _merge_managed_block(existing_content: str, managed_block: str) -> tuple[str, str]:
    current = existing_content or ""
    if not current.strip():
        return managed_block, "created"

    start_count = current.count(_RULE_BLOCK_START)
    end_count = current.count(_RULE_BLOCK_END)
    if start_count == 1 and end_count == 1:
        start_idx = current.find(_RULE_BLOCK_START)
        end_idx = current.find(_RULE_BLOCK_END) + len(_RULE_BLOCK_END)
        if current.lstrip().startswith("---") and managed_block.lstrip().startswith("---"):
            prefix = current[:start_idx].lstrip()
            if prefix.startswith("---") and prefix.count("---") >= 2:
                start_idx = 0
        return f"{current[:start_idx]}{managed_block}{current[end_idx:]}", "replaced"

    preserved = current.strip("\n")
    return f"{managed_block}\n\n{preserved}\n", "prepended"


def _skill_lines(skill_ids: list[str]) -> str:
    return "\n".join(f"- `{skill_id}`" for skill_id in skill_ids)


def _build_trae_rules_block(runtime_version: str, docs_version: str, skill_ids: list[str]) -> str:
    body = (
        f"{_RULE_BLOCK_START}\n"
        f"<!-- BEACON:VERSION:{runtime_version} -->\n"
        f"<!-- BEACON:DOCS_VERSION:{docs_version} -->\n"
        "# Beacon Trae Project Rules\n\n"
        "- Prefer project-local Beacon skills under `.trae/skills/`.\n"
        "- Prefer `beacon <subcommand>` as the stable execution entry.\n"
        "- Treat `docs/beacon/global-boundaries.md` and `docs/beacon/<version>/` as canonical truth.\n"
        "- If skill materialization drifts, run `beacon doctor setup-agent-surface --project-root . --agent trae`.\n"
        "- Verify Trae skill availability with `beacon doctor verify-agent-surface --project-root . --agent trae --strict`.\n"
        "\n## Installed Beacon Skills\n\n"
        f"{_skill_lines(skill_ids)}\n"
        f"{_RULE_BLOCK_END}\n"
    )
    return body


def _build_cursor_rules_block(runtime_version: str, docs_version: str, skill_ids: list[str]) -> str:
    return (
        "---\n"
        f"description: Beacon {runtime_version} agent skill surface and routing\n"
        "alwaysApply: true\n"
        "---\n"
        f"{_RULE_BLOCK_START}\n"
        f"<!-- BEACON:VERSION:{runtime_version} -->\n"
        f"<!-- BEACON:DOCS_VERSION:{docs_version} -->\n"
        "# Beacon Cursor Agent Surface\n\n"
        "- Beacon skills are materialized under `.cursor/skills/`.\n"
        "- Use `beacon <subcommand>` as the stable local execution surface.\n"
        "- Treat `docs/beacon/global-boundaries.md` and `docs/beacon/<version>/` as canonical truth.\n"
        "- Refresh with `beacon doctor setup-agent-surface --project-root . --agent cursor`.\n"
        "- Verify with `beacon doctor verify-agent-surface --project-root . --agent cursor --strict`.\n"
        "\n## Installed Beacon Skills\n\n"
        f"{_skill_lines(skill_ids)}\n"
        f"{_RULE_BLOCK_END}\n"
    )


def _build_windsurf_workflow_block(runtime_version: str, docs_version: str, skill_ids: list[str]) -> str:
    return (
        "---\n"
        f"description: Beacon {runtime_version} agent skill surface and routing\n"
        "---\n"
        f"{_RULE_BLOCK_START}\n"
        f"<!-- BEACON:VERSION:{runtime_version} -->\n"
        f"<!-- BEACON:DOCS_VERSION:{docs_version} -->\n"
        "# Beacon Windsurf Agent Surface\n\n"
        "Use this workflow to discover and route to project-local Beacon skills.\n\n"
        "1. Prefer project-local Beacon skills under `.windsurf/skills/`.\n"
        "2. Use `beacon <subcommand>` as the stable local execution surface.\n"
        "3. Treat `docs/beacon/global-boundaries.md` and `docs/beacon/<version>/` as canonical truth.\n"
        "4. Refresh with `beacon doctor setup-agent-surface --project-root . --agent windsurf`.\n"
        "5. Verify with `beacon doctor verify-agent-surface --project-root . --agent windsurf --strict`.\n"
        "\n## Installed Beacon Skills\n\n"
        f"{_skill_lines(skill_ids)}\n"
        f"{_RULE_BLOCK_END}\n"
    )


def _build_rules_block(target: AgentSurfaceTarget, runtime_version: str, docs_version: str, skill_ids: list[str]) -> str:
    if target.rules_kind == "cursor-mdc":
        return _build_cursor_rules_block(runtime_version, docs_version, skill_ids)
    if target.rules_kind == "windsurf-workflow":
        return _build_windsurf_workflow_block(runtime_version, docs_version, skill_ids)
    return _build_trae_rules_block(runtime_version, docs_version, skill_ids)


def _sync_rules_file(target: AgentSurfaceTarget, runtime_version: str, docs_version: str, skill_ids: list[str], *, dry_run: bool) -> dict[str, Any] | None:
    if target.rules_path is None:
        return None
    existed = target.rules_path.exists()
    current = target.rules_path.read_text(encoding="utf-8") if target.rules_path.exists() else ""
    managed = _build_rules_block(target, runtime_version, docs_version, skill_ids)
    merged, merge_mode = _merge_managed_block(current, managed)
    changed = current != merged
    if not dry_run:
        target.rules_path.parent.mkdir(parents=True, exist_ok=True)
        target.rules_path.write_text(merged, encoding="utf-8")
    return {
        "path": str(target.rules_path),
        "action": "planned" if dry_run else "updated" if existed else "created",
        "merge_mode": merge_mode,
        "changed": changed or not existed,
    }


def setup_agent_surface(
    project_root: Path | str,
    *,
    agent: str,
    runtime_version: str,
    docs_version: str,
    dry_run: bool,
    force: bool = False,
) -> dict[str, Any]:
    """Materialize Beacon host-visible skills into a project-local agent surface."""
    root = Path(project_root).resolve()
    target = resolve_agent_surface_target(root, agent)
    source_root = packaged_beacon_skill_root()
    source_skills = list_host_visible_skills(source_root)
    state = _load_state(root)
    agents_state = state.setdefault("agents", {})
    agent_state = agents_state.get(target.agent) if isinstance(agents_state.get(target.agent), dict) else {}
    previously_managed = _managed_skill_ids(agent_state)

    installed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    removed: list[str] = []
    warnings: list[str] = []

    if not dry_run:
        target.skills_root.mkdir(parents=True, exist_ok=True)

    source_names = {item.name for item in source_skills}
    stale_ids = sorted(previously_managed - source_names)
    for skill_id in stale_ids:
        stale_path = target.skills_root / skill_id
        if not stale_path.exists():
            continue
        removed.append(str(stale_path))
        if not dry_run:
            shutil.rmtree(stale_path)

    installed_state: list[dict[str, Any]] = []
    for source_skill in source_skills:
        skill_id = source_skill.name
        destination = target.skills_root / skill_id
        source_hash = _hash_directory(source_skill)
        destination_exists = destination.exists()
        destination_hash = _hash_directory(destination) if destination_exists else ""
        managed_existing = skill_id in previously_managed

        if destination_exists and not managed_existing and not force and destination_hash and destination_hash != source_hash:
            skipped.append(
                {
                    "id": skill_id,
                    "path": str(destination),
                    "reason": "unmanaged_existing_directory",
                }
            )
            warnings.append(f"{skill_id} skipped because destination already exists and is unmanaged")
            continue

        action = "unchanged"
        if not destination_exists:
            action = "planned" if dry_run else "created"
        elif destination_hash != source_hash:
            action = "planned" if dry_run else "updated"

        if action != "unchanged":
            if not dry_run:
                if destination.exists():
                    shutil.rmtree(destination)
                shutil.copytree(source_skill, destination)
        installed.append(
            {
                "id": skill_id,
                "path": str(destination),
                "action": action,
                "source_hash": source_hash,
            }
        )
        installed_state.append(
            {
                "id": skill_id,
                "path": str(destination.relative_to(root)),
                "source_path": str(source_skill.relative_to(source_root)),
                "source_hash": source_hash,
            }
        )

    skill_ids = [item.name for item in source_skills]
    rules_result = _sync_rules_file(target, runtime_version, docs_version, skill_ids, dry_run=dry_run)
    state_payload = {
        **state,
        "updated_at": now_iso(),
        "runtime_version": runtime_version,
        "docs_version": docs_version,
        "agents": {
            **agents_state,
            target.agent: {
                "agent": target.agent,
                "surface_root": str(target.skills_root.relative_to(root)),
                "rules_path": str(target.rules_path.relative_to(root)) if target.rules_path else "",
                "source_root": str(source_root.relative_to(root)) if source_root.is_relative_to(root) else str(source_root),
                "installed_skills": installed_state,
            },
        },
    }
    state_result = _write_state(root, state_payload, dry_run=dry_run)

    return {
        "project_root": str(root),
        "agent": target.agent,
        "surface_root": str(target.skills_root),
        "rules_path": str(target.rules_path) if target.rules_path else "",
        "installed": installed,
        "skipped": skipped,
        "removed": removed,
        "warnings": warnings,
        "state": state_result,
        "rules": rules_result,
    }


def verify_agent_surface(
    project_root: Path | str,
    *,
    agent: str,
    runtime_version: str,
    strict: bool,
) -> dict[str, Any]:
    """Verify project-local agent surface materialization against packaged Beacon skills."""
    root = Path(project_root).resolve()
    target = resolve_agent_surface_target(root, agent)
    source_root = packaged_beacon_skill_root()
    source_skills = list_host_visible_skills(source_root)
    expected_ids = [item.name for item in source_skills]
    missing: list[str] = []
    drifted: list[str] = []

    for source_skill in source_skills:
        destination = target.skills_root / source_skill.name
        if not destination.exists():
            missing.append(source_skill.name)
            continue
        if _hash_directory(source_skill) != _hash_directory(destination):
            drifted.append(source_skill.name)

    checks: list[dict[str, Any]] = [
        {
            "name": "agent_supported",
            "status": "pass",
            "details": {"agent": target.agent},
        },
        {
            "name": "surface_root_present",
            "status": "pass" if target.skills_root.exists() else "fail",
            "details": {"path": str(target.skills_root), "exists": target.skills_root.exists()},
        },
        {
            "name": "host_visible_skills_present",
            "status": "pass" if not missing else "fail",
            "details": {"expected": expected_ids, "missing": missing},
        },
        {
            "name": "host_visible_skills_drift",
            "status": "pass" if not drifted else ("fail" if strict else "warn"),
            "details": {"drifted": drifted},
        },
    ]

    if target.rules_path is not None:
        rules_exists = target.rules_path.exists()
        rules_text = target.rules_path.read_text(encoding="utf-8") if rules_exists else ""
        checks.append(
            {
                "name": "agent_rules_managed_block",
                "status": "pass" if rules_exists and _RULE_BLOCK_START in rules_text and _RULE_BLOCK_END in rules_text else "fail",
                "details": {"path": str(target.rules_path), "exists": rules_exists},
            }
        )

    state_path = root / _STATE_PATH
    state_exists = state_path.exists()
    checks.append(
        {
            "name": "agent_surface_state_projection",
            "status": "pass" if state_exists else ("fail" if strict else "warn"),
            "details": {"path": str(state_path), "exists": state_exists},
        }
    )

    status = "pass"
    if any(str(item.get("status")) == "fail" for item in checks):
        status = "fail"
    elif any(str(item.get("status")) == "warn" for item in checks):
        status = "warn"

    return {
        "project_root": str(root),
        "agent": target.agent,
        "surface_root": str(target.skills_root),
        "runtime_version": runtime_version,
        "strict": strict,
        "status": status,
        "ok": status != "fail",
        "checks": checks,
    }
