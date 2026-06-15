"""Beacon skill command - adapter registry and preference management."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from beacon.utils.implement_adapters import (
    adapter_defined_in_config,
    detect_adapter,
    discover_skill_adapters,
    global_config_path,
    project_config_path,
    resolve_default_runner,
)
from beacon.utils.agent_surface import (
    build_v160_rough_prompt_route,
    default_v160_skill_package_root,
    materialize_v160_skill_package,
    verify_v160_no_fake_delivery,
    verify_v160_research_promotion,
    verify_v160_skill_package,
    validate_v160_research_artifact,
    v160_rename_matrix,
)
from beacon.utils.truth_integrity import verify_closure_via_tig
from beacon.utils.project_skills import bind_feature_profile, list_skill_registry
from beacon.utils.runtime import now_iso
from beacon.utils.skill_config import load_yaml_like, write_yaml_like
from beacon.utils.skill_discovery import (
    apply_skill_discovery,
    build_skill_discovery_payload,
    load_skill_discovery,
    validate_skill_discovery_payload,
    write_skill_discovery_state,
)
from beacon.utils.skill_drift import build_skill_drift_report
from beacon.utils.skill_eval_kit import (
    generate_skill_eval_review,
    materialize_skill_eval_kit,
    run_skill_eval,
    run_skill_eval_benchmark,
)

app = typer.Typer(name="skill", help="Manage Beacon implementation skill adapters")
registry_app = typer.Typer(name="registry", help="Inspect Beacon multi-skill registry")
eval_kit_app = typer.Typer(name="eval-kit", help="Manage Beacon Skill Eval Kit")
package_app = typer.Typer(name="package", help="Manage generated Beacon host-visible skill packages")


def _resolve_scope_path(project_root: Path, scope: str) -> Path:
    return global_config_path() if scope == "global" else project_config_path(project_root)


def _adapter_defined_in_project_config(project_root: Path, adapter_id: str) -> bool:
    path = project_config_path(project_root)
    config = load_yaml_like(path) if path.exists() else {}
    skill_section = config.get("skill") if isinstance(config.get("skill"), dict) else {}
    adapters = skill_section.get("adapters") if isinstance(skill_section.get("adapters"), dict) else {}
    implementation_section = config.get("implementation") if isinstance(config.get("implementation"), dict) else {}
    runners = implementation_section.get("runners") if isinstance(implementation_section.get("runners"), dict) else {}
    preferred = str(skill_section.get("preferred", "")).strip()
    return adapter_id in adapters or adapter_id in runners or preferred == adapter_id


def _require_v160(version: str) -> None:
    if str(version).strip() != "v1.6.0":
        typer.echo("skill package taxonomy commands currently target v1.6.0 only", err=True)
        raise typer.Exit(2)


def _split_refs(value: str) -> list[str]:
    return [item.strip() for item in str(value or "").split(",") if item.strip()]


def _emit_payload(payload: dict[str, Any], *, json_output: bool, fail_on_status: bool = True) -> None:
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"status: {payload.get('status')}")
        for key in ("package_root", "research_path", "recommended_route", "reason_code"):
            if payload.get(key):
                typer.echo(f"{key}: {payload.get(key)}")
    if fail_on_status and str(payload.get("status") or "").lower() in {"fail", "blocked"}:
        raise typer.Exit(2)


def _upsert_adapter(
    *,
    config_path: Path,
    adapter_id: str,
    adapter_type: str,
    command: str | None,
    runtime_family: str | None,
) -> dict[str, Any]:
    config = load_yaml_like(config_path) if config_path.exists() else {}
    skill_section = config.setdefault("skill", {})
    if not isinstance(skill_section, dict):
        skill_section = {}
        config["skill"] = skill_section
    adapters = skill_section.setdefault("adapters", {})
    if not isinstance(adapters, dict):
        adapters = {}
        skill_section["adapters"] = adapters

    payload = adapters.get(adapter_id) if isinstance(adapters.get(adapter_id), dict) else {}
    payload = dict(payload)
    payload["adapter_type"] = adapter_type
    payload["runtime_family"] = runtime_family or adapter_id
    if command:
        payload["command"] = command
    if adapter_type == "command-skill":
        if adapter_id == "omx":
            payload.setdefault("args", ["exec", "--full-auto", "--cd", "{project_root}", "--skip-git-repo-check", "{task_prompt}"])
            payload.setdefault("skill_prefix", "$workflows-work")
        else:
            payload.setdefault("args", ["run", "--project-root", "{project_root}", "--task", "{task_prompt}"])
        payload.setdefault("result_file", ".beacon/implement/{run_id}/result.json")
    elif adapter_type == "command":
        payload.setdefault("args", [])
        payload.setdefault("result_file", ".beacon/implement/{run_id}/result.json")
    elif adapter_type in {"handoff", "claude-skill"}:
        payload.setdefault("request_file", ".beacon/implement/{run_id}/request.md")
        payload.setdefault("result_file", ".beacon/implement/{run_id}/result.json")

    adapters[adapter_id] = payload
    write_yaml_like(config_path, config)
    return payload


def _set_preferred(*, config_path: Path, adapter_id: str) -> dict[str, Any]:
    config = load_yaml_like(config_path) if config_path.exists() else {}
    skill_section = config.setdefault("skill", {})
    if not isinstance(skill_section, dict):
        skill_section = {}
        config["skill"] = skill_section
    skill_section["preferred"] = adapter_id
    write_yaml_like(config_path, config)
    return config


@package_app.command("materialize")
def package_materialize(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("v1.6.0", "--version", "-v", help="Target skill package taxonomy version"),
    output_root: str = typer.Option("", "--output-root", "--output", help="Generated package root"),
    force: bool = typer.Option(False, "--force", help="Overwrite generated package drift"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Materialize the v1.6.0 generated harness-first host-visible skill package."""
    _require_v160(version)
    root = Path(project_root) if project_root else Path.cwd()
    package_root = Path(output_root) if output_root else default_v160_skill_package_root(root, version)
    payload = materialize_v160_skill_package(root, output_root=package_root, dry_run=dry_run, force=force)
    _emit_payload(payload, json_output=json_output, fail_on_status=True)


@package_app.command("verify")
def package_verify(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("v1.6.0", "--version", "-v", help="Target skill package taxonomy version"),
    package_root: str = typer.Option("", "--package-root", help="Generated package root"),
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Fail on generated drift"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Verify a v1.6.0 generated harness-first host-visible skill package."""
    _require_v160(version)
    root = Path(project_root) if project_root else Path.cwd()
    resolved_package_root = Path(package_root) if package_root else default_v160_skill_package_root(root, version)
    payload = verify_v160_skill_package(root, package_root=resolved_package_root, strict=strict)
    _emit_payload(payload, json_output=json_output, fail_on_status=True)


@package_app.command("rename-matrix")
def package_rename_matrix(
    version: str = typer.Option("v1.6.0", "--version", "-v", help="Target skill package taxonomy version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Print the v1.6.0 old-to-new host-visible skill rename matrix."""
    _require_v160(version)
    payload = {"schema_version": "1.0", "status": "pass", "version": version, "rename_matrix": v160_rename_matrix()}
    _emit_payload(payload, json_output=json_output, fail_on_status=False)


@package_app.command("route-prompt")
def package_route_prompt(
    prompt: str = typer.Argument(..., help="Rough user prompt to classify and route"),
    truth_refs: str = typer.Option("", "--truth-refs", help="Comma-separated truth refs"),
    source_refs: str = typer.Option("", "--source-refs", help="Comma-separated source refs"),
    evidence_refs: str = typer.Option("", "--evidence-refs", help="Comma-separated evidence refs"),
    version: str = typer.Option("v1.6.0", "--version", "-v", help="Target skill package taxonomy version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Build the v1.6.0 rough-prompt planner routing envelope."""
    _require_v160(version)
    payload = build_v160_rough_prompt_route(
        prompt,
        truth_refs=_split_refs(truth_refs),
        source_refs=_split_refs(source_refs),
        evidence_refs=_split_refs(evidence_refs),
    )
    _emit_payload(payload, json_output=json_output, fail_on_status=False)


@package_app.command("verify-research")
def package_verify_research(
    feature: str = typer.Argument(..., help="Feature slug"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("v1.6.0", "--version", "-v", help="Target docs version"),
    research_path: str = typer.Option("", "--research-path", help="Research artifact path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Verify the v1.6.0 planner research support_advisory artifact contract."""
    _require_v160(version)
    root = Path(project_root) if project_root else Path.cwd()
    payload = validate_v160_research_artifact(
        root,
        version=version,
        feature=feature,
        research_path=Path(research_path) if research_path else None,
    )
    _emit_payload(payload, json_output=json_output, fail_on_status=True)


@package_app.command("verify-promotion")
def package_verify_promotion(
    feature: str = typer.Argument(..., help="Feature slug"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("v1.6.0", "--version", "-v", help="Target docs version"),
    research_path: str = typer.Option("", "--research-path", help="Research artifact path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Verify whether v1.6.0 planner research may promote into truth/generate/evaluate mainline."""
    _require_v160(version)
    root = Path(project_root) if project_root else Path.cwd()
    payload = verify_v160_research_promotion(
        root,
        version=version,
        feature=feature,
        research_path=Path(research_path) if research_path else None,
    )
    _emit_payload(payload, json_output=json_output, fail_on_status=True)


@package_app.command("verify-closure")
def package_verify_closure(
    payload_json: str = typer.Option("", "--payload-json", help="Closure payload JSON string"),
    payload_path: str = typer.Option("", "--payload-path", help="Closure payload JSON file"),
    feature: str = typer.Option("", "--feature", help="Feature slug to verify from package files"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root when using --feature"),
    version: str = typer.Option("v1.6.0", "--version", "-v", help="Target skill package taxonomy version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Reject fake-delivery payloads as implementation, QA, or release closure."""
    _require_v160(version)
    root = Path(project_root or ".").expanduser().resolve()
    if feature.strip() and not payload_path and not payload_json:
        result = verify_closure_via_tig(root, version=version, feature=feature.strip())
        _emit_payload(result, json_output=json_output, fail_on_status=True)
        return
    payload: dict[str, Any] = {}
    if payload_path:
        loaded = json.loads(Path(payload_path).read_text(encoding="utf-8"))
        payload = loaded if isinstance(loaded, dict) else {"payload": loaded}
    elif payload_json:
        loaded = json.loads(payload_json)
        payload = loaded if isinstance(loaded, dict) else {"payload": loaded}
    if feature.strip():
        result = verify_closure_via_tig(root, version=version, feature=feature.strip(), payload=payload)
    else:
        from beacon.utils.agent_surface import verify_v160_no_fake_delivery

        result = verify_v160_no_fake_delivery(payload)
    _emit_payload(result, json_output=json_output, fail_on_status=True)


def _doctor_adapter(adapter_id: str, payload: dict[str, Any], project_root: Path) -> dict[str, Any]:
    detected, evidence = detect_adapter(adapter_id, project_root)
    issues: list[str] = []
    if not payload.get("adapter_type"):
        issues.append("adapter_type missing")
    if payload.get("adapter_type") in {"command", "command-skill"} and not payload.get("command"):
        issues.append("command missing")
    if payload.get("adapter_type") == "command-skill" and not payload.get("result_file"):
        issues.append("result_file missing")
    if payload.get("adapter_type") in {"handoff", "claude-skill"} and not payload.get("request_file"):
        issues.append("request_file missing")
    if payload.get("adapter_type") == "command-skill" and not payload.get("args"):
        issues.append("args missing")
    return {
        "adapter_id": adapter_id,
        "detected": detected,
        "evidence": evidence,
        "issues": issues,
        "status": "pass" if detected and not issues else ("warn" if detected else "fail"),
    }


@registry_app.command("list")
def registry_list(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """List builtin + external project skills known to Beacon."""
    root = Path(project_root) if project_root else Path.cwd()
    rows = list_skill_registry(root)
    payload = {"schema_version": "1.0", "skills": rows}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon Skill Registry")
    typer.echo("=" * 22)
    for row in rows:
        typer.echo(f"- {row['id']} ({row['kind']}) detected={row['detected']}")


@app.command("detect")
def detect(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Detect locally available skill runtimes/adapters."""
    root = Path(project_root) if project_root else Path.cwd()
    adapters = discover_skill_adapters(root)
    preferred = resolve_default_runner(root)
    payload = {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "project_root": str(root),
        "preferred": preferred or "",
        "adapters": [],
    }
    for adapter_id, adapter in sorted(adapters.items()):
        detected, evidence = detect_adapter(adapter_id, root)
        payload["adapters"].append(
            {
                "id": adapter_id,
                "adapter_type": str(adapter.get("adapter_type", "")),
                "runtime_family": str(adapter.get("runtime_family", "")),
                "detected": detected,
                "evidence": evidence,
                "preferred": adapter_id == preferred,
            }
        )

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    typer.echo("Beacon Skill Detect")
    typer.echo("=" * 22)
    for item in payload["adapters"]:
        marker = "*" if item["preferred"] else "-"
        typer.echo(f"{marker} {item['id']}: detected={item['detected']} ({', '.join(item['evidence']) or 'no evidence'})")


@app.command("list")
def list_adapters(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """List known skill adapters."""
    root = Path(project_root) if project_root else Path.cwd()
    adapters = discover_skill_adapters(root)
    preferred = resolve_default_runner(root)
    items = []
    for adapter_id, payload in sorted(adapters.items()):
        items.append(
            {
                "id": adapter_id,
                "adapter_type": str(payload.get("adapter_type", "")),
                "runtime_family": str(payload.get("runtime_family", "")),
                "source": "configured" if adapter_defined_in_config(root, adapter_id) else "builtin",
                "preferred": adapter_id == preferred,
            }
        )
    if json_output:
        typer.echo(json.dumps({"adapters": items, "preferred": preferred or ""}, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon Skill Adapters")
    typer.echo("=" * 24)
    for item in items:
        marker = "*" if item["preferred"] else "-"
        typer.echo(f"{marker} {item['id']} ({item['adapter_type']}, {item['source']})")


@app.command("show")
def show(
    adapter_id: str = typer.Argument(..., help="Adapter id"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Show a specific adapter configuration."""
    root = Path(project_root) if project_root else Path.cwd()
    adapters = discover_skill_adapters(root)
    payload = adapters.get(adapter_id)
    if not isinstance(payload, dict):
        typer.echo(f"Unknown adapter: {adapter_id}", err=True)
        raise typer.Exit(2)
    detected, evidence = detect_adapter(adapter_id, root)
    output = {
        "id": adapter_id,
        "source": "configured" if adapter_defined_in_config(root, adapter_id) else "builtin",
        "preferred": adapter_id == resolve_default_runner(root),
        "detected": detected,
        "evidence": evidence,
        "adapter": payload,
    }
    if json_output:
        typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
        return
    typer.echo(json.dumps(output, ensure_ascii=False, indent=2))


@app.command("register")
def register(
    adapter_id: str = typer.Argument(..., help="Adapter id"),
    adapter_type: str = typer.Option(..., "--type", help="Adapter type: command|command-skill|handoff|claude-skill"),
    command: str = typer.Option("", "--command", help="Executable command"),
    runtime_family: str = typer.Option("", "--runtime-family", help="Runtime family"),
    scope: str = typer.Option("project", "--scope", help="Config scope: project|global"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Register or scaffold a skill adapter in Beacon config."""
    if adapter_type not in {"command", "command-skill", "handoff", "claude-skill"}:
        typer.echo(f"Unsupported adapter type: {adapter_type}", err=True)
        raise typer.Exit(2)
    root = Path(project_root) if project_root else Path.cwd()
    path = _resolve_scope_path(root, scope)
    payload = _upsert_adapter(
        config_path=path,
        adapter_id=adapter_id,
        adapter_type=adapter_type,
        command=command or None,
        runtime_family=runtime_family or None,
    )
    output = {"config_path": str(path), "adapter_id": adapter_id, "adapter": payload, "scope": scope}
    if json_output:
        typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Registered adapter `{adapter_id}` in {path}")


@app.command("bind")
def bind(
    feature: str = typer.Argument(..., help="Feature name"),
    profile: str = typer.Option(..., "--profile", help="Project profile id"),
    version: str = typer.Option("auto", "--version", "-v", help="Target version"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Bind a feature to a project profile for skill-aware verification/orchestration."""
    root = Path(project_root) if project_root else Path.cwd()
    path = bind_feature_profile(root, version=version, feature=feature, profile_id=profile)
    payload = {
        "schema_version": "1.0",
        "status": "bound",
        "feature": feature,
        "profile_id": profile,
        "binding_path": str(path.relative_to(root)),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ bound `{feature}` to profile `{profile}`")


@app.command("prefer")
def prefer(
    adapter_id: str = typer.Argument(..., help="Adapter id to prefer"),
    scope: str = typer.Option("project", "--scope", help="Config scope: project|global"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Set preferred skill adapter."""
    root = Path(project_root) if project_root else Path.cwd()
    adapters = discover_skill_adapters(root)
    if adapter_id not in adapters:
        typer.echo(f"Unknown adapter: {adapter_id}", err=True)
        raise typer.Exit(2)
    path = _resolve_scope_path(root, scope)
    payload = _set_preferred(config_path=path, adapter_id=adapter_id)
    output = {"config_path": str(path), "preferred": adapter_id, "scope": scope, "config": payload}
    if json_output:
        typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Preferred adapter set to `{adapter_id}` in {path}")


@app.command("doctor")
def doctor(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Validate configured adapters and environment availability."""
    root = Path(project_root) if project_root else Path.cwd()
    adapters = discover_skill_adapters(root)
    preferred = resolve_default_runner(root)
    checks = [_doctor_adapter(adapter_id, payload, root) for adapter_id, payload in sorted(adapters.items())]
    for item in checks:
        adapter_id = str(item.get("adapter_id", "") or "")
        if str(item.get("status", "") or "") != "fail":
            continue
        if _adapter_defined_in_project_config(root, adapter_id):
            continue
        item["status"] = "warn"
    discovery_payload = load_skill_discovery(root)
    if discovery_payload:
        discovery_issues = validate_skill_discovery_payload(root, discovery_payload)
        checks.append(
            {
                "adapter_id": "skill-discovery",
                "detected": True,
                "evidence": [str((root / ".beacon" / "state" / "skill-discovery").relative_to(root))],
                "issues": discovery_issues,
                "status": "pass" if not discovery_issues else "fail",
            }
        )
    status = "pass"
    if any(item["status"] == "fail" for item in checks):
        status = "fail"
    elif any(item["status"] == "warn" for item in checks):
        status = "warn"
    if preferred and preferred not in adapters:
        preferred_status = "fail" if _adapter_defined_in_project_config(root, preferred) else "warn"
        checks.append(
            {
                "adapter_id": preferred,
                "detected": False,
                "evidence": [],
                "issues": ["preferred adapter not found"],
                "status": preferred_status,
            }
        )
        if preferred_status == "fail":
            status = "fail"
    status = "pass"
    if any(item["status"] == "fail" for item in checks):
        status = "fail"
    elif any(item["status"] == "warn" for item in checks):
        status = "warn"
    payload = {"schema_version": "1.0", "status": status, "preferred": preferred or "", "checks": checks}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        if status == "fail":
            raise typer.Exit(2)
        return
    typer.echo("Beacon Skill Doctor")
    typer.echo("=" * 20)
    for item in checks:
        typer.echo(f"- {item['status'].upper()}: {item['adapter_id']} :: {', '.join(item['issues']) or 'ok'}")
    if status == "fail":
        raise typer.Exit(2)


@app.command("discover")
def discover(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    template: str = typer.Option("", "--template", help="Template id override"),
    profile_id: str = typer.Option("", "--profile", help="Recommended profile id override"),
    from_memory: bool = typer.Option(False, "--from-memory", help="Use prior discovery artifacts as memory signals"),
    apply_recommended: bool = typer.Option(False, "--apply-recommended", help="Apply the recommended profile/config"),
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run", help="Preview by default; disable for explicit apply"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Discover bounded project skill/profile recommendations for the current project."""
    root = (Path(project_root) if project_root else Path.cwd()).resolve()
    payload = build_skill_discovery_payload(
        root,
        template_id=template or None,
        from_memory=from_memory,
        profile_id=profile_id or None,
    )
    if apply_recommended and not dry_run:
        payload = apply_skill_discovery(root, payload)
    state_path = write_skill_discovery_state(root, payload)
    payload["state_path"] = str(state_path.relative_to(root))
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon Skill Discover")
    typer.echo("=" * 22)
    typer.echo(f"status: {payload.get('status')}")
    typer.echo(f"selected_template: {payload.get('selected_template', '') or '-'}")
    typer.echo(f"recommended_profile_id: {payload.get('recommended_profile_id', '') or '-'}")
    typer.echo(f"state_path: {payload.get('state_path', '')}")


@app.command("sync-check")
def sync_check(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Check Beacon skill drift across repo, local Claude installs, and legacy Codex duplicates."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = build_skill_drift_report(root)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Skill Sync Check")
        typer.echo("=" * 24)
        typer.echo(f"status: {payload['status']}")
        typer.echo(f"drift_count: {payload['drift_count']}")
        typer.echo(f"missing_count: {payload['missing_count']}")
        for item in payload.get("checks", []):
            if not isinstance(item, dict):
                continue
            typer.echo(f"- {item.get('name')}: {item.get('status')}")
            if item.get("kind") == "directory" and str(item.get("status")) == "drift":
                typer.echo(
                    f"  missing={len(item.get('missing_files', []))} unexpected={len(item.get('unexpected_files', []))} drift={len(item.get('drift_files', []))}"
                )
    if str(payload.get("status")) != "pass":
        raise typer.Exit(2)


app.add_typer(registry_app, name="registry")
app.add_typer(package_app, name="package")


@eval_kit_app.command("init")
def eval_kit_init(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("v1.4.10", "--version", "-v", help="Eval case set version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Materialize default Skill Eval Kit cases, tags, splits, and regression core."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = materialize_skill_eval_kit(root, version=version)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        if payload.get("status") == "blocked":
            raise typer.Exit(2)
        return
    typer.echo(f"✓ Skill Eval Kit ready: {payload.get('root')}")


@eval_kit_app.command("run")
def eval_kit_run(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    split: str = typer.Option("regression-core", "--split", help="Split to run: regression-core|optimization|holdout|all"),
    version: str = typer.Option("v1.4.10", "--version", "-v", help="Eval case set version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Run Skill Eval Kit cases and write runtime evidence."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = run_skill_eval(root, split=split, version=version)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        if payload.get("status") != "pass":
            raise typer.Exit(2)
        return
    typer.echo(f"✓ Skill Eval Kit run: {payload.get('metrics_path')}")


@eval_kit_app.command("review")
def eval_kit_review(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    feedback_path: str = typer.Option("", "--feedback-path", help="Optional feedback.json path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Generate a self-contained Skill Eval Kit review artifact."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = generate_skill_eval_review(root, feedback_path=Path(feedback_path) if feedback_path else None)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        if payload.get("status") in {"fail", "blocked"}:
            raise typer.Exit(2)
        return
    typer.echo(f"✓ Skill Eval Kit review: {payload.get('review_html_path')}")


@eval_kit_app.command("benchmark")
def eval_kit_benchmark(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("v1.6.0", "--version", "-v", help="Benchmark case set version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Run Skill Eval Kit benchmark and write behavior evidence artifacts."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = run_skill_eval_benchmark(root, version=version)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        if payload.get("status") != "pass":
            raise typer.Exit(2)
        return
    typer.echo(f"✓ Skill Eval Kit benchmark: {payload.get('root')}")


app.add_typer(eval_kit_app, name="eval-kit")
