"""Curated host subagent pack install/verify for Codex and Claude (v1.6.8+ plan-review)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.host_subagent_gate import (
    MINIMAL_SIX_ROLES,
    PLAN_REVIEW_TEN_ROLES,
)
from beacon.utils.runtime import now_iso

PACK_MINIMAL = "minimal"
PACK_PLAN_REVIEW = "plan-review"
SUPPORTED_PACKS = (PACK_MINIMAL, PACK_PLAN_REVIEW)

BEACON_HARD = (
    "HARD: cannot_complete_goal=true; cannot_auto_release=true; cannot_write_truth=true; "
    "parent integrates; emit findings with severity/confidence when reviewing; "
    "do not claim QA or release pass; do not freeze package truth."
)

# Role metadata used to generate host agent stubs (curated, VoltAgent-inspired)
ROLE_META: dict[str, dict[str, str]] = {
    "search-specialist": {
        "stage": "research",
        "sandbox": "read-only",
        "description": "Fast high-signal search of codebase or external sources before deeper work.",
        "instructions": (
            "Own search execution. Return ranked hits with relevance, next file to inspect, and gaps. "
            "Do not spawn further agents. Do not claim QA or release pass."
        ),
        "oss_relpath": "categories/10-research-analysis/search-specialist.toml",
    },
    "docs-researcher": {
        "stage": "research",
        "sandbox": "read-only",
        "description": "Research official docs and specs with citations.",
        "instructions": (
            "Produce a concise research brief with sources. Read-only. "
            "Do not rewrite requirement truth or mark complete."
        ),
        "oss_relpath": "categories/10-research-analysis/docs-researcher.toml",
    },
    "multi-agent-coordinator": {
        "stage": "review",
        "sandbox": "read-only",
        "description": "Plan multi-agent work with ownership and non-overlapping write scopes.",
        "instructions": (
            "Map critical path vs sidecar tasks. Return ownership plan only. "
            "Parent integrates. Cannot complete GoalRun."
        ),
        "oss_relpath": "categories/09-meta-orchestration/multi-agent-coordinator.toml",
    },
    "code-reviewer": {
        "stage": "qa",
        "sandbox": "read-only",
        "description": "Review correctness, tests, and simplicity for a change.",
        "instructions": (
            "Review only. List findings with severity. Do not self-certify release. "
            "Evidence for parent evaluator."
        ),
        "oss_relpath": "categories/04-quality-security/code-reviewer.toml",
    },
    "backend-developer": {
        "stage": "implement",
        "sandbox": "workspace-write",
        "description": "Implement bounded backend tasks under parent ownership.",
        "instructions": (
            "Implement only within assigned ownership. Do not write main package truth. "
            "Do not claim product complete or release."
        ),
        "oss_relpath": "categories/01-core-development/backend-developer.toml",
    },
    "qa-expert": {
        "stage": "qa",
        "sandbox": "read-only",
        "description": "Acceptance and test evidence review against frozen truth.",
        "instructions": (
            "Map scenarios to evidence. Flag fake greens. Do not issue formal release verdict; "
            "route to parent beacon-eval-qa / release human gate."
        ),
        "oss_relpath": "categories/04-quality-security/qa-expert.toml",
    },
    "architect-reviewer": {
        "stage": "review",
        "sandbox": "read-only",
        "description": "Architectural review for boundaries, coupling, and design coherence.",
        "instructions": (
            "Own architecture review as evidence-driven risk reduction. "
            "Map boundaries, dependency direction, failure isolation, migration feasibility. "
            "Return findings for parent synthesis only."
        ),
        "oss_relpath": "categories/04-quality-security/architect-reviewer.toml",
    },
    "knowledge-synthesizer": {
        "stage": "review",
        "sandbox": "read-only",
        "description": "Merge multi-lane findings into one synthesis without rewriting truth.",
        "instructions": (
            "Merge duplicate findings, preserve conflicts, pick highest severity, "
            "emit one recommended_route for the parent. Do not freeze truth."
        ),
        "oss_relpath": "categories/09-meta-orchestration/knowledge-synthesizer.toml",
    },
    "security-auditor": {
        "stage": "review",
        "sandbox": "read-only",
        "description": "Security and trust-boundary review for auth, secrets, and exposure.",
        "instructions": (
            "Review permission, trust, data exposure, and fail-closed behavior. "
            "Findings only; no release verdict."
        ),
        "oss_relpath": "categories/04-quality-security/security-auditor.toml",
    },
    "performance-engineer": {
        "stage": "review",
        "sandbox": "read-only",
        "description": "Performance and concurrency budget review.",
        "instructions": (
            "Review runtime bounds, backpressure, observability, and budget risks. "
            "Findings only; parent integrates."
        ),
        "oss_relpath": "categories/04-quality-security/performance-engineer.toml",
    },
    "api-designer": {
        "stage": "review",
        "sandbox": "read-only",
        "description": "API/CLI/schema contract coherence review.",
        "instructions": (
            "Review API and command contracts for stability and caller impact. "
            "Read-only findings; do not implement."
        ),
        "oss_relpath": "categories/01-core-development/api-designer.toml",
    },
}

OSS_CODEX_ROOTS = (
    Path.home() / "Developer/Personal/oss-sync/agents/agent-skills/awesome-codex-subagents",
    Path("/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/awesome-codex-subagents"),
)
OSS_CLAUDE_ROOTS = (
    Path.home() / "Developer/Personal/oss-sync/agents/agent-skills/awesome-claude-code-subagents",
    Path("/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/awesome-claude-code-subagents"),
)


def agents_dir(project_root: Path, host_runtime: str) -> Path:
    host = str(host_runtime or "").strip().lower()
    root = Path(project_root)
    if host == "claude":
        return root / ".claude" / "agents"
    return root / ".codex" / "agents"


def role_filename(role: str, host_runtime: str) -> str:
    host = str(host_runtime or "").strip().lower()
    if host == "claude":
        return f"{role}.md"
    return f"{role}.toml"


def _first_existing(roots: tuple[Path, ...]) -> Path | None:
    for root in roots:
        if root.is_dir():
            return root
    return None


def _load_oss_body(role: str, host_runtime: str) -> str | None:
    meta = ROLE_META.get(role) or {}
    rel = str(meta.get("oss_relpath") or "")
    if not rel:
        return None
    host = str(host_runtime or "codex").strip().lower()
    if host == "claude":
        root = _first_existing(OSS_CLAUDE_ROOTS)
        if root is None:
            return None
        path = root / rel.replace(".toml", ".md")
    else:
        root = _first_existing(OSS_CODEX_ROOTS)
        if root is None:
            return None
        path = root / rel
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def render_codex_toml(role: str, meta: dict[str, str], *, body_override: str | None = None) -> str:
    if body_override and body_override.strip().startswith("name"):
        # Project VoltAgent toml: force read-only sandbox for plan roles + HARD block
        text = body_override
        text = re.sub(
            r'(?m)^sandbox_mode\s*=\s*".*"\s*$',
            'sandbox_mode = "read-only"',
            text,
            count=1,
        )
        if "cannot_complete_goal" not in text:
            if 'developer_instructions = """' in text:
                text = text.replace(
                    'developer_instructions = """',
                    f'developer_instructions = """\n{BEACON_HARD}\n',
                    1,
                )
            elif "[instructions]" in text:
                text = text.rstrip() + f"\n\n# Beacon\n# {BEACON_HARD}\n"
            else:
                text = text.rstrip() + f'\n\ndeveloper_instructions = """\n{BEACON_HARD}\n"""\n'
        return text if text.endswith("\n") else text + "\n"

    sandbox = "read-only" if role != "backend-developer" else (meta.get("sandbox") or "workspace-write")
    if role != "backend-developer":
        sandbox = "read-only"
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
        f"{BEACON_HARD}\n"
        f"\"\"\"\n"
    )


def render_claude_md(role: str, meta: dict[str, str], *, body_override: str | None = None) -> str:
    if body_override and body_override.lstrip().startswith("---"):
        text = body_override
        # Strip write tools if listed
        text = re.sub(r"(?mi)^tools:\s*.*$", "tools: Read, Glob, Grep", text, count=1)
        if "cannot_complete_goal" not in text:
            text = text.rstrip() + f"\n\n**{BEACON_HARD}**\n"
        return text if text.endswith("\n") else text + "\n"

    return (
        f"---\n"
        f"name: {role}\n"
        f"description: {meta.get('description') or role}\n"
        f"---\n\n"
        f"# {role}\n\n"
        f"Stage: `{meta.get('stage')}`  \n"
        f"Sandbox: `read-only`\n\n"
        f"{meta.get('instructions') or ''}\n\n"
        f"**{BEACON_HARD}**\n"
    )


def _roles_for_pack(pack_name: str, roles: list[str] | None) -> list[str] | dict[str, Any]:
    if roles:
        selected = list(roles)
    elif pack_name == PACK_PLAN_REVIEW:
        selected = list(PLAN_REVIEW_TEN_ROLES)
    else:
        selected = list(MINIMAL_SIX_ROLES)
    for role in selected:
        if role not in ROLE_META:
            return {"status": "blocked", "reason_code": "unknown_role", "role": role}
    return selected


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
    if pack_name not in SUPPORTED_PACKS:
        return {
            "status": "blocked",
            "reason_code": "unsupported_pack",
            "pack": pack_name,
            "allowed": list(SUPPORTED_PACKS),
        }

    selected = _roles_for_pack(pack_name, roles)
    if isinstance(selected, dict):
        return selected

    target = agents_dir(root, host)
    target.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    projected: list[str] = []
    for role in selected:
        meta = ROLE_META[role]
        name = role_filename(role, host)
        path = target / name
        oss_body = _load_oss_body(role, host)
        if oss_body:
            projected.append(role)
            content = (
                render_claude_md(role, meta, body_override=oss_body)
                if host == "claude"
                else render_codex_toml(role, meta, body_override=oss_body)
            )
        else:
            content = render_claude_md(role, meta) if host == "claude" else render_codex_toml(role, meta)
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(root)))

    manifest = {
        "schema": "beacon-host-subagent-pack.v1",
        "pack": pack_name,
        "host_runtime": host,
        "roles": selected,
        "written": written,
        "projected_from_oss": projected,
        "cannot_complete_goal": True,
        "cannot_write_truth": True,
        "installed_at": now_iso(),
        "source": (
            "curated-plan-review (VoltAgent projection + Beacon HARD)"
            if pack_name == PACK_PLAN_REVIEW
            else "curated-minimal (oss-inspired; not full VoltAgent dump)"
        ),
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
        "projected_from_oss": projected,
        "manifest": str(man_path.relative_to(root)),
        "role_count": len(selected),
    }


def verify_subagent_agents(
    project_root: Path | str,
    *,
    host_runtime: str = "codex",
    require_pack: bool = True,
    pack: str | None = None,
) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    host = str(host_runtime or "").strip().lower()
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

    expected = list(PLAN_REVIEW_TEN_ROLES if str(pack or "").strip().lower() == PACK_PLAN_REVIEW else MINIMAL_SIX_ROLES)
    # Prefer manifest pack when present
    man = target / "beacon-pack-manifest.json"
    if man.is_file():
        try:
            import json

            payload = json.loads(man.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and str(payload.get("pack") or "") == PACK_PLAN_REVIEW:
                expected = list(payload.get("roles") or PLAN_REVIEW_TEN_ROLES)
            elif isinstance(payload, dict) and payload.get("roles"):
                # verify listed roles exist
                expected = [str(x) for x in payload.get("roles") if str(x).strip()]
        except Exception:  # noqa: BLE001
            pass

    for role in expected:
        name = role_filename(role, host)
        path = target / name
        ok = path.is_file() and path.stat().st_size > 0
        checks.append({"name": f"role:{role}", "ok": ok, "detail": str(path)})
        if not ok:
            missing.append(role)

    checks.append({"name": "pack_manifest", "ok": man.is_file(), "detail": str(man)})

    ok_all = not missing and (man.is_file() if require_pack else not missing)
    return {
        "schema_version": "1.0",
        "check": "host-subagent-agents",
        "status": "pass" if ok_all else "fail",
        "host_runtime": host,
        "checks": checks,
        "missing_roles": missing,
        "expected_roles": expected,
        "reason_code": "" if ok_all else "pack_roles_missing",
        "recommended_command": (
            ""
            if ok_all
            else f"beacon doctor install-subagent-pack --project-root . --host-runtime {host} --pack plan-review"
        ),
    }
