"""Project-level lifecycle hook contracts and runtime evidence."""

from __future__ import annotations

import re
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any

from beacon import __toolkit_version__
from beacon.utils.runtime import generate_run_id, now_iso, write_json
from beacon.utils.skill_config import SkillConfigError, _Parser
from beacon.utils.v115_delivery import refresh_evidence_manifest
from beacon.utils.versioning import resolve_target_version
from beacon.utils.agent_eval_kit import is_live_runner_admitted

ALLOWED_HOOK_CODES = {
    "post_implement_pre_qa",
    "qa_diagnostics",
    "post_qa_pre_release",
    "post_release",
}

ALLOWED_TRIGGER_POLICIES = {
    "dry_run_only",
    "manual_confirmed",
    "auto_allowed",
}

ALLOWED_FAILURE_ROUTES = {
    "implement",
    "qa",
    "release",
    "change",
    "blocked",
}

AUTHORITY_BOUNDARY_KEYWORDS = {
    "prd truth",
    "user-story truth",
    "test-case truth",
    "qa verdict",
    "release verdict",
    "gate verdict",
    "freeze state",
    "requirement truth",
}

BEACON_POST_RELEASE_LOCAL_INSTALL_HOOK_ID = "beacon-post-release-local-install"


def hooks_root(project_root: Path) -> Path:
    return project_root / "docs" / "beacon" / "hooks"


def hook_path(project_root: Path, hook_id: str) -> Path:
    return hooks_root(project_root) / f"{hook_id}.md"


def hook_state_dir(project_root: Path, hook_id: str) -> Path:
    return project_root / ".beacon" / "state" / "hooks" / hook_id


def hook_latest_read_model_path(project_root: Path, hook_id: str) -> Path:
    return project_root / "docs" / "beacon" / ".machine" / "hooks" / f"{hook_id}.latest.json"


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str, list[str]]:
    if not text.startswith("---\n"):
        return {}, text, ["frontmatter_missing"]
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text, ["frontmatter_unclosed"]
    raw = text[4:end].strip("\n")
    body = text[text.find("\n", end + 1) + 1 :]
    try:
        data = _Parser(raw.splitlines()).parse()
    except SkillConfigError:
        return {}, body, ["frontmatter_parse_failed"]
    return data, body, []


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def load_hook_contract(project_root: Path, hook_id: str) -> dict[str, Any]:
    path = hook_path(project_root, hook_id)
    if not path.exists():
        return {
            "hook_id": hook_id,
            "path": str(path.relative_to(project_root)),
            "exists": False,
            "frontmatter": {},
            "body": "",
            "parse_errors": ["hook_file_missing"],
        }
    text = path.read_text(encoding="utf-8")
    frontmatter, body, parse_errors = _parse_frontmatter(text)
    return {
        "hook_id": str(frontmatter.get("hook_id") or hook_id),
        "path": str(path.relative_to(project_root)),
        "exists": True,
        "frontmatter": frontmatter,
        "body": body,
        "parse_errors": parse_errors,
    }


def list_hook_contracts(project_root: Path) -> list[dict[str, Any]]:
    root = hooks_root(project_root)
    if not root.exists():
        return []
    hooks: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.md")):
        hooks.append(load_hook_contract(project_root, path.stem))
    return hooks


def _command_project_arg(project_root: Path) -> str:
    try:
        if project_root.resolve() == Path.cwd().resolve():
            return "."
    except Exception:  # noqa: BLE001
        pass
    return str(project_root)


def _hook_command(
    project_root: Path,
    hook_id: str,
    *,
    version: str = "",
    feature: str = "",
    hook_code: str = "",
    confirm: bool = False,
    dry_run: bool = False,
) -> str:
    parts = [
        "beacon",
        "hooks",
        "run",
        hook_id,
        "--project",
        _command_project_arg(project_root),
    ]
    if version:
        parts.extend(["--version", version])
    if feature:
        parts.extend(["--feature", feature])
    if hook_code:
        parts.extend(["--hook-code", hook_code])
    if dry_run:
        parts.append("--dry-run")
    if confirm:
        parts.append("--confirm")
    return " ".join(shlex.quote(part) for part in parts)


def _advisory_command(project_root: Path, hook_id: str, *, version: str, feature: str, hook_code: str, trigger_policy: str) -> str:
    if trigger_policy == "dry_run_only":
        return _hook_command(
            project_root,
            hook_id,
            version=version,
            feature=feature,
            hook_code=hook_code,
            dry_run=True,
        )
    return _hook_command(
        project_root,
        hook_id,
        version=version,
        feature=feature,
        hook_code=hook_code,
        confirm=True,
    )


def discover_hooks_for_boundary(project_root: Path, hook_code: str, *, feature: str = "") -> dict[str, Any]:
    """Discover project-local hooks for a finite lifecycle boundary."""
    hooks: list[dict[str, Any]] = []
    for item in list_hook_contracts(project_root):
        frontmatter = item.get("frontmatter") if isinstance(item.get("frontmatter"), dict) else {}
        declared_code = str(frontmatter.get("hook_code") or "").strip()
        if hook_code and declared_code != hook_code:
            continue
        if frontmatter.get("enabled") is not True:
            continue
        hook_id = str(item.get("hook_id") or Path(str(item.get("path") or "")).stem)
        admission = validate_hook_contract(project_root, hook_id, feature=feature, hook_code=hook_code)
        hooks.append(
            {
                "hook_id": hook_id,
                "hook_code": declared_code,
                "path": str(item.get("path") or ""),
                "status": "ready" if not admission.get("blocked") else "blocked",
                "blocked": bool(admission.get("blocked")),
                "reason_codes": list(admission.get("reason_codes") or []),
                "trigger_policy": str((admission.get("contract") or {}).get("trigger_policy") or ""),
                "failure_route": str((admission.get("contract") or {}).get("failure_route") or ""),
                "admission": admission,
            }
        )
    return {
        "schema_version": "1.0",
        "project_root": str(project_root),
        "hook_code": hook_code,
        "feature": feature,
        "status": "ready" if hooks else "none",
        "hook_count": len(hooks),
        "hooks": hooks,
        "truth_root": "docs/beacon/hooks",
        "truth_authority": False,
        "runtime_evidence_only": True,
    }


def build_lifecycle_hook_advisory(
    project_root: Path,
    *,
    version: str = "",
    feature: str = "",
    hook_code: str,
    boundary_stage: str = "",
    record_dry_run_evidence: bool = True,
) -> dict[str, Any]:
    """Build lifecycle-boundary hook advice without executing side effects."""
    discovery = discover_hooks_for_boundary(project_root, hook_code, feature=feature)
    hook_items: list[dict[str, Any]] = []
    for item in discovery.get("hooks", []) if isinstance(discovery.get("hooks"), list) else []:
        if not isinstance(item, dict):
            continue
        hook_id = str(item.get("hook_id") or "")
        if not hook_id:
            continue
        plan = plan_hook(project_root, hook_id, version=version, feature=feature, hook_code=hook_code)
        dry_run_payload = (
            run_hook(
                project_root,
                hook_id,
                version=version,
                feature=feature,
                hook_code=hook_code,
                dry_run=True,
                confirm=False,
            )
            if record_dry_run_evidence and not bool(plan.get("blocked"))
            else {}
        )
        trigger_policy = str(((plan.get("admission") or {}).get("contract") or {}).get("trigger_policy") or "")
        recommended_command = "" if bool(plan.get("blocked")) else _advisory_command(
            project_root,
            hook_id,
            version=version,
            feature=feature,
            hook_code=hook_code,
            trigger_policy=trigger_policy,
        )
        dry_run_command = "" if bool(plan.get("blocked")) else _hook_command(
            project_root,
            hook_id,
            version=version,
            feature=feature,
            hook_code=hook_code,
            dry_run=True,
        )
        dry_run_evidence_paths = (
            dry_run_payload.get("evidence_paths")
            if isinstance(dry_run_payload.get("evidence_paths"), dict)
            else {}
        )
        hook_items.append(
            {
                "hook_id": hook_id,
                "hook_code": hook_code,
                "boundary_stage": boundary_stage,
                "trigger_policy": trigger_policy,
                "plan_status": str(plan.get("status") or ""),
                "blocked": bool(plan.get("blocked")),
                "reason_codes": list(((plan.get("admission") or {}).get("reason_codes") or [])),
                "evidence_paths": plan.get("evidence_paths", {}),
                "dry_run": {
                    "attempted": bool(dry_run_payload),
                    "status": str(dry_run_payload.get("status") or ""),
                    "blocked": bool(dry_run_payload.get("blocked", False)),
                    "reason_code": str(dry_run_payload.get("reason_code") or ""),
                    "evidence_paths": dry_run_evidence_paths,
                    "side_effect_executed": bool(dry_run_payload.get("side_effect_executed", False)),
                },
                "dry_run_command": dry_run_command,
                "recommended_command": recommended_command,
                "manual_confirmation_required": trigger_policy == "manual_confirmed",
                "side_effect_executed": False,
                "truth_authority": False,
                "runtime_evidence_only": True,
                "admission": plan.get("admission", {}),
            }
        )
    blocked_hooks = [item for item in hook_items if bool(item.get("blocked"))]
    status = "none" if not hook_items else "blocked" if blocked_hooks else "ready"
    return {
        "schema_version": "1.0",
        "status": status,
        "blocked": bool(blocked_hooks),
        "hook_code": hook_code,
        "boundary_stage": boundary_stage,
        "version": version,
        "feature": feature,
        "project_root": str(project_root),
        "hook_count": len(hook_items),
        "hooks": hook_items,
        "discovery": discovery,
        "recommended_command": next(
            (str(item.get("recommended_command") or "") for item in hook_items if str(item.get("recommended_command") or "")),
            "",
        ),
        "side_effect_executed": False,
        "truth_authority": False,
        "runtime_evidence_only": True,
        "verdict_authority": "none",
        "support_evidence_only": True,
    }


def _body_has_required_sections(body: str) -> list[str]:
    lower = body.lower()
    missing: list[str] = []
    for section in ("purpose", "admission", "evidence", "failure"):
        if f"## {section}" not in lower and f"### {section}" not in lower:
            missing.append(section)
    return missing


def _authority_boundary_issues(body: str, frontmatter: dict[str, Any]) -> list[str]:
    text = f"{body}\n{frontmatter.get('authority', '')}\n{frontmatter.get('authority_boundary', '')}".lower()
    issues: list[str] = []
    for keyword in AUTHORITY_BOUNDARY_KEYWORDS:
        if re.search(rf"\b(can|may|will|writes?|rewrites?|sets?|passes?)\b[^.\n]*{re.escape(keyword)}", text):
            issues.append("hook_authority_bypass")
            break
    return issues


def validate_hook_contract(project_root: Path, hook_id: str, *, feature: str = "", hook_code: str = "") -> dict[str, Any]:
    contract = load_hook_contract(project_root, hook_id)
    frontmatter = contract["frontmatter"]
    diagnostics: list[dict[str, str]] = []

    for reason in contract["parse_errors"]:
        diagnostics.append({"reason_code": reason, "message": reason})

    path_hook_id = Path(contract["path"]).stem
    declared_hook_id = str(frontmatter.get("hook_id") or "").strip()
    if declared_hook_id != path_hook_id:
        diagnostics.append({"reason_code": "hook_id_mismatch", "message": "hook_id must match file name"})

    declared_code = str(frontmatter.get("hook_code") or "").strip()
    if declared_code not in ALLOWED_HOOK_CODES:
        diagnostics.append({"reason_code": "unknown_hook_code", "message": "hook_code is not allowed"})
    if hook_code and declared_code != hook_code:
        diagnostics.append({"reason_code": "hook_code_mismatch", "message": "hook_code does not match requested boundary"})

    if frontmatter.get("enabled") is not True:
        diagnostics.append({"reason_code": "hook_disabled", "message": "hook is disabled or missing enabled: true"})

    trigger_policy = str(frontmatter.get("trigger_policy") or "").strip()
    if trigger_policy not in ALLOWED_TRIGGER_POLICIES:
        diagnostics.append({"reason_code": "invalid_trigger_policy", "message": "trigger_policy is not allowed"})

    failure_route = str(frontmatter.get("failure_route") or "").strip()
    if failure_route not in ALLOWED_FAILURE_ROUTES:
        diagnostics.append({"reason_code": "invalid_failure_route", "message": "failure_route is not allowed"})

    skill = str(frontmatter.get("skill") or "").strip()
    command_template = str(frontmatter.get("command_template") or "").strip()
    if not skill and not command_template:
        diagnostics.append({"reason_code": "hook_invocation_missing", "message": "skill or command_template is required"})

    produces_evidence = _string_list(frontmatter.get("produces_evidence"))
    if not produces_evidence:
        diagnostics.append({"reason_code": "required_evidence_missing", "message": "produces_evidence is required"})

    feature_pattern = str(frontmatter.get("feature_pattern") or "").strip()
    if feature and feature_pattern and feature_pattern not in {"*", feature} and feature_pattern not in feature:
        diagnostics.append({"reason_code": "feature_selector_mismatch", "message": "hook does not apply to this feature"})

    for section in _body_has_required_sections(str(contract.get("body") or "")):
        diagnostics.append({"reason_code": f"section_missing_{section}", "message": f"missing body section: {section}"})

    for reason in _authority_boundary_issues(str(contract.get("body") or ""), frontmatter):
        diagnostics.append({"reason_code": reason, "message": "hook cannot claim lifecycle truth authority"})

    status = "pass" if not diagnostics else "blocked"
    return {
        "schema_version": "1.0",
        "hook_id": hook_id,
        "hook_code": declared_code,
        "feature": feature,
        "path": contract["path"],
        "status": status,
        "blocked": bool(diagnostics),
        "reason_codes": [item["reason_code"] for item in diagnostics],
        "diagnostics": diagnostics,
        "contract": {
            "hook_id": declared_hook_id,
            "hook_code": declared_code,
            "enabled": bool(frontmatter.get("enabled")),
            "trigger_policy": trigger_policy,
            "skill": skill,
            "command_template": command_template,
            "produces_evidence": produces_evidence,
            "failure_route": failure_route,
        },
    }


def plan_hook(project_root: Path, hook_id: str, *, version: str = "", feature: str = "", hook_code: str = "") -> dict[str, Any]:
    admission = validate_hook_contract(project_root, hook_id, feature=feature, hook_code=hook_code)
    return {
        "schema_version": "1.0",
        "action": "plan",
        "hook_id": hook_id,
        "version": version,
        "feature": feature,
        "status": "planned" if not admission["blocked"] else "blocked",
        "blocked": bool(admission["blocked"]),
        "admission": admission,
        "evidence_policy": "runtime_evidence_only",
        "truth_authority": False,
        "evidence_paths": {
            "runtime_root": str(hook_state_dir(project_root, hook_id).relative_to(project_root)),
            "latest_read_model": str(hook_latest_read_model_path(project_root, hook_id).relative_to(project_root)),
        },
    }


def _command_output(args: list[str]) -> dict[str, Any]:
    resolved = shutil.which(args[0])
    payload: dict[str, Any] = {
        "command": args,
        "path": resolved or "",
        "status": "blocked",
        "stdout": "",
        "stderr": "",
        "returncode": None,
    }
    if not resolved:
        payload["reason_code"] = "launcher_not_found"
        return payload
    completed = subprocess.run(args, text=True, capture_output=True, check=False)
    payload.update(
        {
            "status": "pass" if completed.returncode == 0 else "blocked",
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "returncode": completed.returncode,
            "reason_code": "" if completed.returncode == 0 else "launcher_command_failed",
        }
    )
    return payload


def _resolve_eval_version(project_root: Path, version: str) -> tuple[str, str | None]:
    """Resolve the hook's working version via the centralized resolver.

    Returns (resolved_version, error_reason). error_reason is None on success,
    or "version_resolve_failed" when resolution raises — callers must fail
    closed on a non-None error_reason. Replaces the old hardcoded v1.6.1
    fallback that bypassed resolve_target_version.
    """
    try:
        resolved = resolve_target_version(project_root, version)
    except Exception:
        return ("", "version_resolve_failed")
    return (resolved, None)


def _run_beacon_post_release_local_install(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    from beacon.utils.agent_eval_kit import run_agent_eval
    from beacon.utils.doctor_orchestrator import (
        run_agent_surface_setup,
        run_agent_surface_verify,
        run_context_setup,
        run_context_verify,
        run_launcher_setup,
        run_legacy_beacon_skills_cleanup,
    )

    runtime_version = str(__toolkit_version__).strip()
    eval_version, resolve_error = _resolve_eval_version(project_root, version)
    docs_version = eval_version or ""
    drift = bool(runtime_version and docs_version and runtime_version != docs_version)
    blocked_reasons: list[str] = []
    if resolve_error:
        blocked_reasons.append(resolve_error)

    legacy_cleanup = run_legacy_beacon_skills_cleanup(
        project_root=str(project_root),
        version=version,
        agent="all",
        scope="all",
        dry_run=False,
        force=True,
    )

    from beacon.utils.agent_surface import (
        SUPPORTED_HOST_AGENTS,
        install_global_agents_beacon_skills,
        install_global_claude_beacon_skills,
        verify_global_agents_beacon_skills,
        verify_global_claude_beacon_skills,
    )

    # Codex/agents: flat Scheme A 1+6 (never package-root leak)
    agents_global_install = install_global_agents_beacon_skills(
        beacon_root=project_root,
        dry_run=False,
    )
    agents_global_verify = verify_global_agents_beacon_skills()

    claude_global_install = install_global_claude_beacon_skills(
        beacon_root=project_root,
        dry_run=False,
    )
    claude_global_verify = verify_global_claude_beacon_skills()

    agent_results: dict[str, Any] = {}
    for agent in SUPPORTED_HOST_AGENTS:
        setup = run_agent_surface_setup(
            project_root=str(project_root),
            version=version,
            agent=agent,
            dry_run=False,
            force=True,
        )
        verify = run_agent_surface_verify(
            project_root=str(project_root),
            version=version,
            agent=agent,
            strict=True,
        )
        agent_results[agent] = {
            "setup_status": setup.payload.get("status"),
            "verify_status": verify.payload.get("status"),
            "setup_result": setup.payload.get("result", {}),
            "verify_result": verify.payload.get("result", {}),
        }
        if setup.exit_code != 0 or setup.payload.get("status") != "PASS":
            blocked_reasons.append(f"{agent}_agent_surface_setup_failed")
        if verify.exit_code != 0 or verify.payload.get("status") != "PASS":
            blocked_reasons.append(f"{agent}_agent_surface_verify_failed")

    if agents_global_verify.get("status") != "pass":
        blocked_reasons.append("agents_global_beacon_subskills_verify_failed")
    if claude_global_verify.get("status") != "pass":
        blocked_reasons.append("claude_global_beacon_subskills_verify_failed")

    # Keep managed agent context (AGENTS.md / CLAUDE.md / .gitignore) on the
    # released docs line. Skill surfaces alone can leave context at an older
    # managed version and trip help/context guards after ship.
    context_setup = run_context_setup(
        project_root=str(project_root),
        version=version,
        dry_run=False,
        force=True,
        sync_materials=False,
        feature=feature or "",
        all_features=False,
        overwrite_test_doc=False,
        with_claude=True,
        with_agents=True,
        with_gitignore=True,
    )
    context_verify = run_context_verify(
        project_root=str(project_root),
        strict=True,
        with_gitignore=True,
    )
    if context_setup.exit_code != 0 or context_setup.payload.get("status") != "PASS":
        blocked_reasons.append("managed_context_setup_failed")
    if context_verify.exit_code != 0 or context_verify.payload.get("status") != "PASS":
        blocked_reasons.append("managed_context_verify_failed")

    launcher_setup = run_launcher_setup(bin_dir="", launcher_source="", force=True, dry_run=False)
    if launcher_setup.exit_code != 0 or launcher_setup.payload.get("status") != "PASS":
        blocked_reasons.append("global_cli_launcher_setup_failed")

    cli_versions = {
        "beacon": _command_output(["beacon", "--version"]),
        "beacon-cli": _command_output(["beacon-cli", "--version"]),
    }
    expected_runtime_version = str(__toolkit_version__).strip()
    expected = expected_runtime_version
    if expected:
        for name, row in cli_versions.items():
            output = str(row.get("stdout") or "")
            if row.get("status") != "pass":
                blocked_reasons.append(f"{name}_version_command_failed")
            elif expected not in output:
                blocked_reasons.append(f"{name}_runtime_version_mismatch")

    agent_eval_release_hook: dict[str, Any] | None = None
    if not resolve_error and is_live_runner_admitted(project_root, version=eval_version):
        agent_eval_release_hook = run_agent_eval(
            project_root,
            split="regression-core",
            runner="live",
            version=eval_version,
            live_tier="release_hook",
        )
        if agent_eval_release_hook.get("status") != "pass":
            blocked_reasons.append("agent_eval_release_hook_failed")

    # Runtime alignment: detect runtime!=docs and route to sync-version-surfaces.
    # Hook does NOT auto pip install — it advises the operator. This closes the
    # skills/runtime split where hook publishes v1.6.3 skills but beacon --version
    # still reports the old runtime.
    runtime_aligned = bool(runtime_version and docs_version and runtime_version == docs_version)
    runtime_recommended = "" if runtime_aligned else (
        f"beacon doctor sync-version-surfaces --project-root {project_root}"
    )

    return {
        "schema_version": "1.0",
        "hook_id": BEACON_POST_RELEASE_LOCAL_INSTALL_HOOK_ID,
        "version": version,
        "feature": feature,
        "status": "blocked" if blocked_reasons else "pass",
        "blocked": bool(blocked_reasons),
        "reason_codes": blocked_reasons,
        "expected_runtime_version": expected_runtime_version,
        "runtime_version": runtime_version,
        "docs_version": docs_version,
        "drift": drift,
        "runtime_alignment": {
            "runtime_version": runtime_version,
            "docs_version": docs_version,
            "aligned": runtime_aligned,
            "recommended_command": runtime_recommended,
        },
        "legacy_skill_cleanup": legacy_cleanup.payload.get("result", {}),
        "agents_global_skill_install": agents_global_install,
        "agents_global_skill_verify": agents_global_verify,
        "claude_global_skill_install": claude_global_install,
        "claude_global_skill_verify": claude_global_verify,
        "agent_surfaces": agent_results,
        "managed_context_setup": context_setup.payload,
        "managed_context_verify": context_verify.payload,
        "launcher_setup": launcher_setup.payload,
        "cli_versions": cli_versions,
        "agent_eval_release_hook": agent_eval_release_hook,
        "commands_confirmed": [
            f"python3 -m beacon.main doctor cleanup-legacy-beacon-skills --project-root . --version {version} --scope all --force --json",
            f"python3 -c \"from beacon.utils.agent_surface import install_global_agents_beacon_skills, verify_global_agents_beacon_skills, install_global_claude_beacon_skills, verify_global_claude_beacon_skills; install_global_agents_beacon_skills(beacon_root='{project_root}'); verify_global_agents_beacon_skills(); install_global_claude_beacon_skills(beacon_root='{project_root}'); verify_global_claude_beacon_skills()\"",
            f"python3 -m beacon.main doctor setup-agent-surface --project-root . --version {version} --agent codex --force --json",
            f"python3 -m beacon.main doctor verify-agent-surface --project-root . --version {version} --agent codex --strict --json",
            f"python3 -m beacon.main doctor setup-agent-surface --project-root . --version {version} --agent claude --force --json",
            f"python3 -m beacon.main doctor verify-agent-surface --project-root . --version {version} --agent claude --strict --json",
            f"python3 -m beacon.main doctor setup-context --project-root . --version {version} --force --json",
            "python3 -m beacon.main doctor verify-context --project-root . --strict --json",
            "python3 -m beacon.main doctor setup --force --json",
            "beacon --version",
            "beacon-cli --version",
            f"beacon eval run --runner live --live-tier release_hook --split regression-core --version {eval_version} --json",
        ],
    }


def run_hook(
    project_root: Path,
    hook_id: str,
    *,
    version: str = "",
    feature: str = "",
    hook_code: str = "",
    dry_run: bool = False,
    confirm: bool = False,
) -> dict[str, Any]:
    plan = plan_hook(project_root, hook_id, version=version, feature=feature, hook_code=hook_code)
    run_id = generate_run_id(project_root)
    payload = {
        "schema_version": "1.0",
        "action": "run",
        "run_id": run_id,
        "hook_id": hook_id,
        "version": version,
        "feature": feature,
        "dry_run": dry_run,
        "confirmed": confirm,
        "status": "planned" if dry_run else "passed",
        "blocked": False,
        "reason_code": "",
        "plan": plan,
        "side_effect_executed": False,
        "runtime_evidence_only": True,
        "truth_authority": False,
        "written_at": now_iso(),
    }
    if plan["blocked"]:
        payload.update({"status": "blocked", "blocked": True, "reason_code": "hook_admission_blocked"})
    else:
        trigger_policy = str(plan["admission"]["contract"]["trigger_policy"])
        if dry_run:
            payload["status"] = "planned"
        elif trigger_policy == "dry_run_only":
            payload.update({"status": "blocked", "blocked": True, "reason_code": "hook_dry_run_only"})
        elif trigger_policy == "manual_confirmed" and not confirm:
            payload.update({"status": "blocked", "blocked": True, "reason_code": "manual_confirmation_required"})
        elif not confirm:
            payload.update({"status": "blocked", "blocked": True, "reason_code": "hidden_auto_run_not_allowed"})
        else:
            payload["side_effect_executed"] = True
            if hook_id == BEACON_POST_RELEASE_LOCAL_INSTALL_HOOK_ID:
                followup = _run_beacon_post_release_local_install(project_root, version=version, feature=feature)
                payload["post_release_followup"] = followup
                if followup["blocked"]:
                    payload.update({"status": "blocked", "blocked": True, "reason_code": "post_release_followup_failed"})

    runtime_path = hook_state_dir(project_root, hook_id) / f"{run_id}.json"
    latest_path = hook_latest_read_model_path(project_root, hook_id)
    payload["evidence_paths"] = {
        "runtime": str(runtime_path.relative_to(project_root)),
        "latest_read_model": str(latest_path.relative_to(project_root)),
    }
    write_json(runtime_path, payload)
    write_json(latest_path, payload)
    refresh_evidence_manifest(
        project_root,
        refs=[
            str(runtime_path.relative_to(project_root)),
            str(latest_path.relative_to(project_root)),
        ],
        version=version,
    )
    return payload


def disable_hook(project_root: Path, hook_id: str) -> dict[str, Any]:
    path = hook_path(project_root, hook_id)
    if not path.exists():
        return {"schema_version": "1.0", "hook_id": hook_id, "status": "blocked", "reason_code": "hook_file_missing"}
    text = path.read_text(encoding="utf-8")
    if re.search(r"(?m)^enabled:\s*(true|false)\s*$", text):
        updated = re.sub(r"(?m)^enabled:\s*(true|false)\s*$", "enabled: false", text, count=1)
    elif text.startswith("---\n"):
        updated = text.replace("---\n", "---\nenabled: false\n", 1)
    else:
        updated = f"---\nhook_id: {hook_id}\nenabled: false\n---\n\n{text}"
    path.write_text(updated, encoding="utf-8")
    return {"schema_version": "1.0", "hook_id": hook_id, "status": "disabled", "path": str(path.relative_to(project_root))}


def hook_status(project_root: Path, hook_id: str, *, feature: str = "") -> dict[str, Any]:
    admission = validate_hook_contract(project_root, hook_id, feature=feature)
    latest_path = hook_latest_read_model_path(project_root, hook_id)
    latest = {}
    if latest_path.exists():
        from beacon.utils.runtime import read_json

        latest = read_json(latest_path, {})
    return {
        "schema_version": "1.0",
        "hook_id": hook_id,
        "feature": feature,
        "status": "ready" if not admission["blocked"] else "blocked",
        "blocked": bool(admission["blocked"]),
        "admission": admission,
        "latest_run": latest if isinstance(latest, dict) else {},
        "truth_authority": False,
    }
