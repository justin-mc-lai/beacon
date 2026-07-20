"""Curated host subagent pack install/verify for Codex and Claude (v1.6.8)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.host_subagent_gate import MINIMAL_SIX_ROLES
from beacon.utils.runtime import now_iso

PACK_MINIMAL = "minimal"

# Role metadata used to generate host agent stubs (curated, not full VoltAgent dump)
ROLE_META: dict[str, dict[str, str]] = {
    "search-specialist": {
        "stage": "research",
        "sandbox": "read-only",
        "description": "Fast high-signal search of codebase or external sources before deeper work.",
        "instructions": (
            "Own search execution. Return ranked hits with relevance, next file to inspect, and gaps. "
            "Do not spawn further agents. Do not claim QA or release pass."
        ),
    },
    "docs-researcher": {
        "stage": "research",
        "sandbox": "read-only",
        "description": "Research official docs and specs with citations.",
        "instructions": (
            "Produce a concise research brief with sources. Read-only. "
            "Do not rewrite requirement truth or mark complete."
        ),
    },
    "multi-agent-coordinator": {
        "stage": "review",
        "sandbox": "read-only",
        "description": "Plan multi-agent work with ownership and non-overlapping write scopes.",
        "instructions": (
            "Map critical path vs sidecar tasks. Return ownership plan only. "
            "Parent integrates. Cannot complete GoalRun."
        ),
    },
    "code-reviewer": {
        "stage": "qa",
        "sandbox": "read-only",
        "description": "Review correctness, tests, and simplicity for a change.",
        "instructions": (
            "Review only. List findings with severity. Do not self-certify release. "
            "Evidence for parent evaluator."
        ),
    },
    "backend-developer": {
        "stage": "implement",
        "sandbox": "workspace-write",
        "description": "Implement bounded backend tasks under parent ownership.",
        "instructions": (
            "Implement only within assigned ownership. Do not write main package truth. "
            "Do not claim product complete or release."
        ),
    },
    "qa-expert": {
        "stage": "qa",
        "sandbox": "read-only",
        "description": "Acceptance and test evidence review against frozen truth.",
        "instructions": (
            "Map scenarios to evidence. Flag fake greens. Do not issue formal release verdict; "
            "route to parent beacon-eval-qa / release human gate."
        ),
    },
}


def agents_dir(project_root: Path, host_runtime: str) -> Path:
    host = str(host_runtime or "").strip().lower()
    root = Path(project_root)
    if host == "claude":
        return root / ".claude" / "agents"
    # default codex
    return root / ".codex" / "agents"


def role_filename(role: str, host_runtime: str) -> str:
    host = str(host_runtime or "").strip().lower()
    if host == "claude":
        return f"{role}.md"
    return f"{role}.toml"


def render_codex_toml(role: str, meta: dict[str, str]) -> str:
    sandbox = meta.get("sandbox") or "read-only"
    desc = meta.get("description") or role
    body = meta.get("instructions") or ""
    return (
        f'name = "{role}"\n'
        f'description = "{desc}"\n'
        f'model = "gpt-5.3-codex-spark"\n'
        f'model_reasoning_effort = "medium"\n'
        f'sandbox_mode = "{sandbox}"\n'
        f"developer_instructions = \"\"\"\n"
        f"You are Beacon curated host subagent `{role}` (stage={meta.get('stage')}).\n"
        f"{body}\n"
        f"HARD: cannot_complete_goal=true; cannot_auto_release=true; parent integrates.\n"
        f"\"\"\"\n"
    )


def render_claude_md(role: str, meta: dict[str, str]) -> str:
    return (
        f"---\n"
        f"name: {role}\n"
        f"description: {meta.get('description') or role}\n"
        f"---\n\n"
        f"# {role}\n\n"
        f"Stage: `{meta.get('stage')}`  \n"
        f"Sandbox: `{meta.get('sandbox')}`\n\n"
        f"{meta.get('instructions') or ''}\n\n"
        f"**HARD:** cannot_complete_goal; cannot_auto_release; parent integrates.\n"
    )


def install_subagent_pack(
    project_root: Path | str,
    *,
    host_runtime: str = "codex",
    pack: str = PACK_MINIMAL,
    roles: list[str] | None = None,
) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    host = str(host_runtime or "codex").strip().lower()
    if host not in {"codex", "claude"}:
        return {
            "status": "blocked",
            "reason_code": "unsupported_host_runtime",
            "host_runtime": host,
        }
    pack_name = str(pack or PACK_MINIMAL).strip().lower()
    if pack_name != PACK_MINIMAL:
        return {
            "status": "blocked",
            "reason_code": "unsupported_pack",
            "pack": pack_name,
            "allowed": [PACK_MINIMAL],
        }

    selected = list(roles) if roles else list(MINIMAL_SIX_ROLES)
    for role in selected:
        if role not in ROLE_META:
            return {"status": "blocked", "reason_code": "unknown_role", "role": role}

    target = agents_dir(root, host)
    target.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for role in selected:
        meta = ROLE_META[role]
        name = role_filename(role, host)
        path = target / name
        content = render_claude_md(role, meta) if host == "claude" else render_codex_toml(role, meta)
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(root)))

    manifest = {
        "schema": "beacon-host-subagent-pack.v1",
        "pack": pack_name,
        "host_runtime": host,
        "roles": selected,
        "written": written,
        "cannot_complete_goal": True,
        "installed_at": now_iso(),
        "source": "curated-minimal (oss-inspired; not full VoltAgent dump)",
    }
    man_path = target / "beacon-pack-manifest.json"
    man_path.write_text(
        __import__("json").dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "status": "ok",
        "host_runtime": host,
        "pack": pack_name,
        "agents_dir": str(target.relative_to(root)),
        "roles": selected,
        "written": written,
        "manifest": str(man_path.relative_to(root)),
        "role_count": len(selected),
    }


def verify_subagent_agents(
    project_root: Path | str,
    *,
    host_runtime: str = "codex",
    require_pack: bool = True,
) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    host = str(host_runtime or "codex").strip().lower()
    target = agents_dir(root, host)
    checks: list[dict[str, Any]] = []
    missing: list[str] = []

    checks.append(
        {
            "name": "agents_dir_present",
            "ok": target.is_dir(),
            "detail": str(target),
        }
    )
    if not target.is_dir():
        return {
            "schema_version": "1.0",
            "check": "host-subagent-agents",
            "status": "fail",
            "host_runtime": host,
            "checks": checks,
            "missing_roles": list(MINIMAL_SIX_ROLES),
            "reason_code": "agents_dir_missing",
            "recommended_command": (
                f"beacon doctor install-subagent-pack --project-root . --host-runtime {host} --pack minimal"
            ),
        }

    for role in MINIMAL_SIX_ROLES:
        name = role_filename(role, host)
        path = target / name
        ok = path.is_file() and path.stat().st_size > 0
        checks.append({"name": f"role:{role}", "ok": ok, "detail": str(path)})
        if not ok:
            missing.append(role)

    man = target / "beacon-pack-manifest.json"
    checks.append({"name": "pack_manifest", "ok": man.is_file(), "detail": str(man)})

    ok_all = not missing and (man.is_file() if require_pack else not missing)
    return {
        "schema_version": "1.0",
        "check": "host-subagent-agents",
        "status": "pass" if ok_all else "fail",
        "host_runtime": host,
        "checks": checks,
        "missing_roles": missing,
        "reason_code": "" if ok_all else "pack_roles_missing",
        "recommended_command": (
            ""
            if ok_all
            else f"beacon doctor install-subagent-pack --project-root . --host-runtime {host} --pack minimal"
        ),
    }
