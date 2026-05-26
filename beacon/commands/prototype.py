"""Beacon prototype command - design-result adapter with legacy wireframe compatibility."""

from __future__ import annotations

import json
import sys
from pathlib import Path
import shutil
from typing import Optional

import typer

from beacon.utils.change_surface import build_change_command
from beacon.utils.prototype_support import (
    build_ui_ux_dev_route,
    design_result_adapter_status,
    prototype_adapter_only_supported,
    prototype_generation_deprecated,
    write_design_result_adapter_binding,
)
from beacon.utils.prototype_utils import (
    _real_prototype_llm_inference,
    bind_prototype_bundle,
    compile_prototype_plan,
    evaluate_prototype_status,
    legacy_prototype_source_path,
    freeze_prototype,
    prototype_dir,
    reconcile_prototype_bundle,
    review_prototype_bundle,
    write_prototype_plan,
    write_prototype_bundle,
)
from beacon.utils.requirement_deepening import build_requirement_completeness_gate
from beacon.utils.versioning import resolve_operational_docs_version, resolve_target_version

app = typer.Typer(name="prototype", help="Adapt accepted UI/UX results into Beacon truth bindings; read legacy wireframe freezes")


def _json_safe(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    return value


def _load_bridge_payload(payload_json: str = "") -> dict:
    raw = str(payload_json or "").strip()
    if not raw:
        raw = sys.stdin.read().strip()
    if not raw:
        raise typer.BadParameter("bridge payload missing")
    try:
        payload = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        raise typer.BadParameter(f"invalid bridge payload: {exc}") from exc
    if not isinstance(payload, dict):
        raise typer.BadParameter("bridge payload must be a JSON object")
    return payload


def _resolved_operational_version(project_root: Path, version: str, command_name: str) -> str:
    try:
        return resolve_operational_docs_version(project_root, version, command_name=command_name)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc


def _externalized_generation_payload(
    *,
    project_root: Path,
    version: str,
    feature: str,
    command_name: str,
) -> dict:
    route = build_ui_ux_dev_route(feature=feature, version=version, project_root=project_root, intent="review")
    return {
        "schema_version": "1.0",
        "feature": feature,
        "version": version,
        "status": "blocked",
        "reason_code": "prototype_generation_externalized",
        "command": command_name,
        "message": (
            "Beacon v1.4.9+ no longer generates native UI/UX wireframe bundles. "
            "Route UI/UX execution to ui-ux-dev, then bind accepted output through prototype adapt."
        ),
        "prototype_role": "design-result-adapter",
        "ui_ux_execution_owner": "ui-ux-dev",
        "recommended_route": route,
        "recommended_command": (
            route["command"]
            + " && "
            + f'beacon prototype adapt "{feature}" --project {project_root} --version {version} --design-result-ref <ui-ux-dev-output>'
        ),
        "bootstrap_command": route["bootstrap_command"],
    }


def _emit_generation_externalized(payload: dict, *, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"Beacon prototype generation blocked: {payload.get('reason_code')}", err=True)
    typer.echo(str(payload.get("message", "")), err=True)
    typer.echo(f"recommended: {payload.get('recommended_command', '')}", err=True)


@app.command("host-bridge", hidden=True)
def host_bridge(
    payload_json: str = typer.Argument("", help="Optional bridge request JSON; default reads stdin"),
):
    """Hidden host-native bridge endpoint for prototype semantic compile."""
    try:
        payload = _load_bridge_payload(payload_json)
    except typer.BadParameter as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc

    request_kind = str(payload.get("request_kind") or "").strip()
    if request_kind != "prototype-wireframe-compile":
        typer.echo("unsupported prototype bridge request_kind", err=True)
        raise typer.Exit(2)
    feature = str(payload.get("feature") or "").strip()
    version = str(payload.get("version") or "").strip()
    if prototype_generation_deprecated(version):
        typer.echo(
            json.dumps(
                _externalized_generation_payload(
                    project_root=Path.cwd(),
                    version=version,
                    feature=feature,
                    command_name="prototype host-bridge",
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        raise typer.Exit(2)

    documents = payload.get("documents")
    docs = documents if isinstance(documents, list) else []
    normalized_docs = [item for item in docs if isinstance(item, dict)]
    semantic_layer = payload.get("semantic_layer") if isinstance(payload.get("semantic_layer"), dict) else {}
    try:
        inference = _real_prototype_llm_inference(
            feature=str(payload.get("feature") or "").strip(),
            version=str(payload.get("version") or "").strip(),
            docs=normalized_docs,
            model=str(payload.get("requested_model") or "beacon-prototype-compiler").strip(),
            semantic_layer=semantic_layer,
        )
    except Exception as exc:  # noqa: BLE001
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc

    typer.echo(json.dumps(inference, ensure_ascii=False))


@app.command()
def plan(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    mode: str = typer.Option("auto", "--mode", help="Compile mode: auto/llm/rule"),
    model: str = typer.Option("beacon-prototype-compiler", "--model", help="Compiler model label for evidence"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Compile structured wireframe freeze plan from requirement contracts."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype plan")
    if prototype_generation_deprecated(resolved_version):
        payload = _externalized_generation_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            command_name="prototype plan",
        )
        _emit_generation_externalized(payload, json_output=json_output)
        raise typer.Exit(2)
    requirement_gate = build_requirement_completeness_gate(
        project_root,
        version=resolved_version,
        feature=feature,
        target_stage="prototype",
    )
    if bool(requirement_gate.get("blocked")):
        typer.echo(json.dumps({
            "feature": feature,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": str(requirement_gate.get("reason_code") or "requirement_completeness_blocked"),
            "requirement_completeness_gate": requirement_gate,
            "recommended_command": str(
                requirement_gate.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="requirement-completeness-blocked",
                )
            ),
        }, ensure_ascii=False, indent=2))
        raise typer.Exit(2)
    try:
        result = write_prototype_plan(project_root, resolved_version, feature, mode=mode, model=model)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)
    payload = {
        "feature": feature,
        "version": resolved_version,
        "prototype_mode": result["plan"].get("prototype_mode"),
        "requested_mode": (result["plan"].get("compiler") or {}).get("requested_mode"),
        "effective_mode": (result["plan"].get("compiler") or {}).get("effective_mode"),
        "generator_mode": (result["plan"].get("compiler") or {}).get("generator_mode"),
        "fallback_reason": (result["plan"].get("compiler") or {}).get("fallback_reason"),
        "capability_snapshot": (result["plan"].get("compiler") or {}).get("capability_snapshot", {}),
        "required_pages": result["plan"].get("required_pages", []),
        "required_states": result["plan"].get("required_states", []),
        "path": str(result["path"].relative_to(project_root)),
        "requirement_completeness_gate": requirement_gate,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Prototype plan compiled: {result['path']}")


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Optional output directory override"),
    mode: str = typer.Option("auto", "--mode", help="Compile mode: auto/llm/rule"),
    model: str = typer.Option("beacon-prototype-compiler", "--model", help="Compiler model label for evidence"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Create a requirement-driven wireframe freeze bundle from requirement contracts."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype create")
    if prototype_generation_deprecated(resolved_version):
        payload = _externalized_generation_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            command_name="prototype create",
        )
        _emit_generation_externalized(payload, json_output=json_output)
        raise typer.Exit(2)
    requirement_gate = build_requirement_completeness_gate(
        project_root,
        version=resolved_version,
        feature=feature,
        target_stage="prototype",
    )
    if bool(requirement_gate.get("blocked")):
        typer.echo(json.dumps({
            "feature": feature,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": str(requirement_gate.get("reason_code") or "requirement_completeness_blocked"),
            "requirement_completeness_gate": requirement_gate,
            "recommended_command": str(
                requirement_gate.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="requirement-completeness-blocked",
                )
            ),
        }, ensure_ascii=False, indent=2))
        raise typer.Exit(2)
    try:
        result = write_prototype_bundle(project_root, resolved_version, feature, mode=mode, model=model)
    except FileNotFoundError as exc:
        typer.echo(f"Missing source docs: {exc}")
        raise typer.Exit(2)
    except ValueError as exc:
        typer.echo(f"Prototype Contract invalid: {exc}")
        raise typer.Exit(2)

    if output:
        out_root = Path(output)
        out_root.mkdir(parents=True, exist_ok=True)
        for name, path in result["files"].items():
            if name == "root":
                continue
            target = out_root / path.name
            if path.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(path, target)
                continue
            shutil.copy2(path, target)

    payload = {
        "feature": feature,
        "version": resolved_version,
        "ui_kit": result["plan"].get("ui_kit"),
        "prototype_type": result["contract"]["prototype_archetype"],
        "prototype_mode": result.get("prototype_mode", "wireframe"),
        "requested_mode": (result["plan"].get("compiler") or {}).get("requested_mode"),
        "effective_mode": (result["plan"].get("compiler") or {}).get("effective_mode"),
        "generator_mode": (result["plan"].get("compiler") or {}).get("generator_mode"),
        "fallback_reason": (result["plan"].get("compiler") or {}).get("fallback_reason"),
        "capability_snapshot": (result["plan"].get("compiler") or {}).get("capability_snapshot", {}),
        "paths": {k: str(v.relative_to(project_root)) for k, v in result["files"].items() if k != "root"},
        "semantic_layer": result.get("semantic_layer", {}),
        "requirement_completeness_gate": requirement_gate,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    typer.echo(f"✓ Wireframe bundle created: {result['files']['wireframe_summary']}")
    typer.echo(f"✓ Archetype: {result['contract']['prototype_archetype']}")
    typer.echo(f"✓ Generator mode: {(result['plan'].get('compiler') or {}).get('generator_mode', 'unknown')}")
    if output:
        typer.echo(f"✓ Copied artifacts to: {Path(output)}")


@app.command()
def adapt(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    design_result_ref: str = typer.Option("", "--design-result-ref", help="Accepted ui-ux-dev output reference"),
    design_result_source: str = typer.Option("ui-ux-dev", "--design-result-source", help="Design result source label"),
    accepted_by: str = typer.Option("", "--accepted-by", help="Human or agent that accepted the design result"),
    summary: str = typer.Option("", "--summary", help="Short accepted design result summary"),
    screen_intent: Optional[list[str]] = typer.Option(None, "--screen-intent", help="Screen intent captured by the adapter"),
    state_visibility: Optional[list[str]] = typer.Option(None, "--state-visibility", help="State visibility captured by the adapter"),
    interaction_handoff: Optional[list[str]] = typer.Option(None, "--interaction-handoff", help="Interaction handoff captured by the adapter"),
    coverage_notes: str = typer.Option("", "--coverage-notes", help="Truth coverage notes"),
    out_of_scope_notes: str = typer.Option("", "--out-of-scope-notes", help="Out-of-scope notes"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Bind an accepted external UI/UX result to PRD, user-story, and test-case truth."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype adapt")
    if not prototype_adapter_only_supported(resolved_version):
        payload = {
            "schema_version": "1.0",
            "feature": feature,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": "prototype_adapter_not_supported_for_version",
            "message": "prototype adapt is the v1.4.9+ design-result adapter surface; use legacy prototype create for older versions.",
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(payload["message"], err=True)
        raise typer.Exit(2)
    payload = write_design_result_adapter_binding(
        project_root,
        resolved_version,
        feature,
        design_result_ref=design_result_ref,
        design_result_source=design_result_source,
        accepted_by=accepted_by,
        summary=summary,
        screen_intent=screen_intent or [],
        state_visibility=state_visibility or [],
        interaction_handoff=interaction_handoff or [],
        coverage_notes=coverage_notes,
        out_of_scope_notes=out_of_scope_notes,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Prototype adapter binding written: {payload.get('paths', {}).get('binding_md', '')}")


@app.command()
def preview(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Print local entry points for a generated wireframe freeze bundle."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype preview")
    status = evaluate_prototype_status(project_root, resolved_version, feature)
    summary_path = status["files"]["wireframe_summary"]
    navigation_map_path = status["files"]["navigation_map_md"]
    if not summary_path.exists():
        typer.echo(f"Prototype bundle not found: {summary_path}", err=True)
        raise typer.Exit(1)

    root = status["root"]
    typer.echo(f"Wireframe bundle ready: {root}")
    typer.echo(f"Summary: {summary_path}")
    typer.echo(f"Navigation map: {navigation_map_path}")


@app.command("directory")
def directory(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Show the prototype directory summary and coverage contract."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype directory")
    status = evaluate_prototype_status(project_root, resolved_version, feature)
    summary_path = status["files"]["wireframe_summary"]
    if not summary_path.exists():
        typer.echo(f"Prototype directory not found: {summary_path}", err=True)
        raise typer.Exit(1)

    coverage_path = status["files"]["coverage_report"]
    coverage = {}
    if coverage_path.exists():
        try:
            loaded = json.loads(coverage_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                coverage = loaded
        except Exception:  # noqa: BLE001
            coverage = {}

    payload = {
        "feature": feature,
        "version": resolved_version,
        "directory_path": str(status["root"].relative_to(project_root)),
        "wireframe_summary_path": str(summary_path.relative_to(project_root)),
        "navigation_map_path": str(status["files"]["navigation_map_md"].relative_to(project_root)),
        "requested_mode": (status.get("compiler") or {}).get("requested_mode"),
        "effective_mode": (status.get("compiler") or {}).get("effective_mode"),
        "generator_mode": (status.get("compiler") or {}).get("generator_mode"),
        "fallback_reason": (status.get("compiler") or {}).get("fallback_reason"),
        "capability_snapshot": (status.get("compiler") or {}).get("capability_snapshot", {}),
        "required_pages": coverage.get("required_pages", []),
        "required_states": coverage.get("required_states", []),
        "generated_pages": coverage.get("generated_pages", []),
        "generated_state_variants": coverage.get("required_states", []),
        "review_status": status.get("review_status"),
        "design_review_outcome": status.get("design_review_outcome"),
        "human_view_status": status.get("human_view_status"),
        "machine_contract_status": status.get("machine_contract_status"),
        "sqlite_projection_status": status.get("sqlite_projection_status"),
        "drift_status": status.get("drift_status"),
        "gate_ready": bool(status.get("gate_ready")),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    typer.echo("Beacon Prototype Directory")
    typer.echo("=" * 28)
    typer.echo(f"feature       : {feature}")
    typer.echo(f"version       : {resolved_version}")
    typer.echo(f"directory     : {status['root']}")
    typer.echo(f"summary       : {summary_path}")
    typer.echo(f"navigation    : {status['files']['navigation_map_md']}")
    typer.echo(f"pages         : {len(payload.get('generated_pages', []))}")
    typer.echo(f"state_variants: {len(payload.get('generated_state_variants', []))}")
    typer.echo(f"review        : {payload.get('review_status')}")
    typer.echo(f"human_view    : {payload.get('human_view_status')}")
    typer.echo(f"machine_view  : {payload.get('machine_contract_status')}")
    typer.echo(f"sqlite_view   : {payload.get('sqlite_projection_status')}")
    typer.echo(f"drift         : {payload.get('drift_status')}")
    typer.echo(f"gate_ready    : {payload.get('gate_ready')}")


@app.command()
def review(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Review a generated wireframe freeze bundle against requirement and delivery contracts."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype review")
    try:
        payload = review_prototype_bundle(project_root, resolved_version, feature)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)
    payload["requirement_completeness_gate"] = build_requirement_completeness_gate(
        project_root,
        version=resolved_version,
        feature=feature,
        target_stage="prototype",
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Prototype review complete: {payload.get('overall_status')}")
    typer.echo(f"✓ Review report: {prototype_dir(project_root, resolved_version, feature) / 'prototype-review.md'}")


@app.command()
def bind(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Bind prototype route-closure cases to implementation-map runtime targets."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype bind")
    try:
        payload = bind_prototype_bundle(project_root, resolved_version, feature)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)
    if json_output:
        serializable = {
            "feature": feature,
            "version": resolved_version,
            "bound_cases": payload.get("bound_cases", 0),
            "path": str(Path(payload.get("path", "")).relative_to(project_root)),
        }
        typer.echo(json.dumps(serializable, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Prototype bound: {payload.get('bound_cases', 0)} cases")
    typer.echo(f"✓ Implementation map: {payload.get('path')}")


@app.command()
def freeze(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Freeze a prototype by persisting source and artifact fingerprints."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype freeze")
    requirement_gate = build_requirement_completeness_gate(
        project_root,
        version=resolved_version,
        feature=feature,
        target_stage="prototype",
    )
    if bool(requirement_gate.get("blocked")):
        typer.echo(json.dumps({
            "feature": feature,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": str(requirement_gate.get("reason_code") or "requirement_completeness_blocked"),
            "requirement_completeness_gate": requirement_gate,
            "recommended_command": str(
                requirement_gate.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="requirement-completeness-blocked",
                )
            ),
        }, ensure_ascii=False, indent=2))
        raise typer.Exit(2)
    try:
        payload = freeze_prototype(project_root, resolved_version, feature)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)
    payload["requirement_completeness_gate"] = requirement_gate
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(
        f"✓ Prototype frozen: {prototype_dir(project_root, resolved_version, feature) / 'freeze.json'} "
        f"({payload.get('status')})"
    )


@app.command("reconcile")
def reconcile(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Repair prototype bundle metadata and structured sinks without overwriting human-visible pages."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype reconcile")
    try:
        payload = reconcile_prototype_bundle(project_root, resolved_version, feature)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)
    if json_output:
        serializable = dict(payload)
        serializable["root"] = str(payload["root"])
        typer.echo(json.dumps(serializable, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Prototype reconciled: {payload.get('root')}")
    typer.echo(f"✓ Canonical truth: {payload.get('canonical_truth_source')}")


@app.command()
def status(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    include_legacy: bool = typer.Option(False, "--include-legacy", help="Include legacy wireframe migration details"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON status payload"),
):
    """Show prototype status including stale detection and review readiness."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype status")
    if prototype_adapter_only_supported(resolved_version):
        payload = design_result_adapter_status(project_root, resolved_version, feature)
        if include_legacy:
            legacy = evaluate_prototype_status(project_root, resolved_version, feature)
            legacy_status = str(legacy.get("status") or "")
            payload["legacy_prototype"] = {
                **_json_safe(legacy),
                "migration_input_present": legacy_status == "legacy_source_only"
                or str(legacy.get("legacy_source_status") or "") == "present",
                "current_closure": False,
            }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
            return
        typer.echo("Beacon Prototype Adapter Status")
        typer.echo("=" * 32)
        typer.echo(f"feature      : {feature}")
        typer.echo(f"version      : {resolved_version}")
        typer.echo(f"status       : {payload.get('status')}")
        typer.echo(f"role         : {payload.get('adapter_role')}")
        typer.echo(f"reason_code  : {payload.get('reason_code', '')}")
        typer.echo(f"binding_json : {(payload.get('paths') or {}).get('binding_json', '')}")
        typer.echo(f"binding_ready: {bool(payload.get('binding_ready'))}")
        if include_legacy:
            legacy = payload.get("legacy_prototype") if isinstance(payload.get("legacy_prototype"), dict) else {}
            typer.echo(f"legacy_migration_input_present: {bool(legacy.get('migration_input_present'))}")
        if payload.get("recommended_command"):
            typer.echo(f"next_action  : {payload.get('recommended_command')}")
        return
    payload = evaluate_prototype_status(project_root, resolved_version, feature)
    payload["requirement_completeness_gate"] = build_requirement_completeness_gate(
        project_root,
        version=resolved_version,
        feature=feature,
        target_stage="prototype",
    )
    if json_output:
        serializable = dict(payload)
        serializable["root"] = str(payload["root"])
        serializable["files"] = {k: str(v) for k, v in payload["files"].items()}
        if "legacy_source_path" in serializable:
            serializable["legacy_source_path"] = str(serializable["legacy_source_path"])
        typer.echo(json.dumps(serializable, ensure_ascii=False, indent=2))
        return

    typer.echo("Beacon Prototype Status")
    typer.echo("=" * 32)
    typer.echo(f"feature      : {feature}")
    typer.echo(f"version      : {resolved_version}")
    typer.echo(f"status       : {payload.get('status')}")
    typer.echo(f"mode         : {payload.get('prototype_mode', 'wireframe')}")
    typer.echo(f"ui_kit       : {payload.get('ui_kit')}")
    typer.echo(f"generator    : {(payload.get('compiler') or {}).get('generator_mode', 'unknown')}")
    typer.echo(f"review       : {payload.get('review_status')}")
    typer.echo(f"human_view   : {payload.get('human_view_status')}")
    typer.echo(f"machine_view : {payload.get('machine_contract_status')}")
    typer.echo(f"sqlite_view  : {payload.get('sqlite_projection_status')}")
    typer.echo(f"drift        : {payload.get('drift_status')}")
    typer.echo(f"req_complete : {(payload.get('requirement_completeness_gate') or {}).get('status', 'n/a')}")
    if payload.get("drift_type"):
        typer.echo(f"drift_type   : {payload.get('drift_type')}")
    if payload.get("reason_code"):
        typer.echo(f"reason_code  : {payload.get('reason_code')}")
    if payload.get("next_action"):
        typer.echo(f"next_action  : {payload.get('next_action')}")
    if payload.get("repair_path"):
        typer.echo(f"repair_path  : {payload.get('repair_path')}")
    typer.echo(f"gate_ready   : {bool(payload.get('gate_ready'))}")
    typer.echo(f"path         : {payload['files']['wireframe_summary']}")
    if payload.get("legacy_source_status") == "present":
        typer.echo(f"legacy_source: {payload.get('legacy_source_path')}")
    typer.echo(f"stale        : {bool(payload.get('stale'))}")


@app.command("list")
def _list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """List generated prototypes and legacy single-file prototype sources."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    root = project_root / "docs" / "beacon" / resolved_version / "prototype"
    if not root.exists():
        typer.echo("No prototypes found")
        return
    candidates: list[str] = []
    for path in sorted(root.iterdir()):
        if path.is_dir():
            candidates.append(path.name)
            continue
        if path.is_file() and path.suffix == ".md":
            feature = path.stem
            if feature not in candidates:
                candidates.append(feature)
    if not candidates:
        typer.echo("No prototypes found")
        return
    typer.echo(f"Prototypes ({len(candidates)} found):")
    for feature in candidates:
        state = evaluate_prototype_status(project_root, resolved_version, feature)
        suffix = ""
        if state.get("legacy_source_status") == "present":
            suffix = f" / legacy_source={legacy_prototype_source_path(project_root, resolved_version, feature)}"
        typer.echo(f"  - {feature}: {state.get('status')} / review={state.get('review_status')} / gate_ready={state.get('gate_ready')}{suffix}")
