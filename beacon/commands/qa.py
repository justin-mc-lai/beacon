"""Beacon QA command - primary surface for v1.1.10 precision-aware verification."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

import typer

from beacon.commands.auto_test import _update_evidence_manifest
from beacon.commands.team import TeamState, TerminalStatus, get_team_state_file, save_team_state
from beacon.utils.delivery_kernel import build_delivery_contract
from beacon.utils.coverage import write_coverage_summary
from beacon.utils.implement_adapters import format_template
from beacon.utils.material_audit import build_requirement_package_gate
from beacon.utils.project_metadata import metadata_machine_path, verify_project_metadata
from beacon.utils.exhaustiveness import build_exhaustiveness_report, write_exhaustiveness_report
from beacon.utils.exhaustiveness import feature_exhaustiveness_report_path
from beacon.utils.project_skills import (
    evaluate_project_profile_gate,
    resolve_profile_for_feature,
    run_profile_orchestration,
)
from beacon.utils.learning_loop import refresh_learning_loop
from beacon.utils.qa_precision import refresh_qa_calibration_model, write_qa_audit_label
from beacon.utils.qa_feature import (
    build_feature_qa_precision_artifacts,
    build_feature_qa_plan,
    collect_verification_writeback,
    feature_qa_plan_path,
    feature_qa_matrix_path,
    feature_qa_status_path,
    load_feature_qa_status,
    materialize_feature_qa_matrix,
    writeback_feature_matrix_evidence,
    write_feature_qa_status,
)
from beacon.utils.qa_runtime import (
    list_qa_sessions,
    load_current_qa_session,
    load_qa_session,
    load_qa_status,
    qa_current_session_path,
    qa_status_path,
    set_current_qa_session,
    write_qa_session,
    write_qa_status,
)
from beacon.utils.story_state import feature_slug
from beacon.utils.subagent_readiness import (
    delegation_readiness_precheck,
    detect_host_runtime,
    runtime_context_not_required_precheck,
    runtime_context_precheck_required,
    runtime_readiness_precheck,
)
from beacon.utils.subagent_runtime import (
    resolve_team_runtime,
    spawn_tmux_workers,
    wait_for_worker_results,
    worker_result_path,
    write_team_hud,
    write_worker_spec,
)
from beacon.utils.team_surface import (
    build_context_isolation,
    load_implement_to_qa_handoff,
    qa_team_contract,
)
from beacon.utils.v110_baseline import generate_spec_fingerprint
from beacon.utils.v115_delivery import refresh_evidence_manifest
from beacon.utils.writeback import record_acceptance_writeback, record_verification_writeback

app = typer.Typer(name="qa", help="QA primary surface (v1.1.10)")
session_app = typer.Typer(name="session", help="QA login/session state helpers")
audit_app = typer.Typer(name="audit", help="QA audit truth helpers")
app.add_typer(session_app, name="session")
app.add_typer(audit_app, name="audit")

KNOWN_SCOPES = {
    "all",
    "full",
    "ui",
    "api-curl",
    "unit",
    "smoke",
    "visual",
    "functional",
    "interface",
    "contract",
    "integration",
    "regression",
    "exception",
    "compatibility",
    "qa9",
}
OPTION_NAMES_WITH_VALUE = {
    "--project",
    "--project-root",
    "-p",
    "--version",
    "-v",
    "--qa-matrix-path",
    "--matrix-path",
    "--qa-types",
    "--qa-profile",
    "--layer-command",
    "--ui-command",
    "--api-curl-command",
    "--unit-command",
    "--smoke-command",
    "--visual-command",
    "--interface-command",
    "--contract-command",
    "--integration-command",
    "--functional-command",
    "--regression-command",
    "--exception-command",
    "--compatibility-command",
    "--origin-url",
    "--target-url",
    "--snapshot-file",
    "--snapshot-text",
    "--required-ui-action",
    "--ui-action-evidence",
    "--compat-browsers",
    "--compat-devices",
    "--rerun-flaky",
    "--max-flaky-rate",
    "--mode",
    "--host-runtime",
}
FLAG_NAMES = {
    "--strict-ui-assertion",
    "--require-fresh-evidence",
    "--require-junit",
    "--require-assertion-count",
    "--require-ui-actions",
    "--verbose",
    "-v",
    "--json",
}
LAYER_SPECIFIC_OPTION_MAP: dict[str, tuple[str, ...]] = {
    "ui": ("--ui-command",),
    "api-curl": ("--api-curl-command",),
    "unit": ("--unit-command",),
    "smoke": ("--smoke-command",),
    "visual": ("--visual-command",),
    "functional": ("--functional-command",),
    "interface": ("--interface-command", "--api-curl-command"),
    "contract": ("--contract-command",),
    "integration": ("--integration-command",),
    "regression": ("--regression-command",),
    "exception": ("--exception-command",),
    "compatibility": ("--compatibility-command",),
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _beacon_exec(args: list[str], *, cwd: Path | None = None) -> int:
    cmd = [sys.executable, "-m", "beacon.main", *args]
    result = subprocess.run(cmd, cwd=cwd or _repo_root())
    return int(result.returncode)


def _beacon_exec_silent(args: list[str], *, cwd: Path | None = None) -> int:
    cmd = [sys.executable, "-m", "beacon.main", *args]
    result = subprocess.run(cmd, cwd=cwd or _repo_root(), capture_output=True, text=True)
    return int(result.returncode)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _render_qa_team_role_markdown(role: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# QA Team Role Report: {role}",
        "",
        f"- role: `{role}`",
        f"- status: `{payload.get('status', '')}`",
        f"- feature: `{payload.get('feature', '')}`",
    ]
    summary = str(payload.get("summary", "")).strip()
    if summary:
        lines.append(f"- summary: {summary}")
    for key in ("targeted_scenario_ids", "stop_reasons", "evidence_refs", "recommendations"):
        values = payload.get(key)
        if isinstance(values, list):
            lines.extend(["", f"## {key}"])
            if values:
                lines.extend(f"- {item}" for item in values)
            else:
                lines.append("- none")
    return "\n".join(lines) + "\n"


def _materialize_qa_team_surface(
    project_root: Path,
    *,
    version: str,
    feature: str,
    run_id: str,
    payload: dict[str, Any],
    runtime: str = "file",
) -> dict[str, Any]:
    feature_key = feature_slug(feature)
    team_name = f"qa-team-{run_id}"
    resolved_runtime = resolve_team_runtime(runtime)
    state = {
        "active": True,
        "team_name": team_name,
        "task": f"QA verify {feature}",
        "runtime": resolved_runtime,
        "feature": feature,
        "version": version,
        "run_id": run_id,
        "surface_dir": "qa-team",
        "state": TeamState.TERMINAL.value,
        "terminal_status": TerminalStatus.PASS.value if str(payload.get("status", "")).lower() == "passed" else TerminalStatus.BLOCKED.value,
        "started_at": str(payload.get("generated_at") or ""),
        "ended_at": str(payload.get("generated_at") or ""),
        "workers": [
            {"id": "worker-001", "role": "verifier", "status": "completed"},
            {"id": "worker-002", "role": "repair-handoff-writer", "status": "completed"},
        ],
        "tasks": [
            {"id": 1, "description": "Verify QA evidence and blockers", "status": "completed", "worker": "worker-001"},
            {"id": 2, "description": "Write repair handoff when blocked", "status": "completed", "worker": "worker-002"},
        ],
        "review_gates": {
            "spec": {"status": "pass", "reviewer": "verifier"},
            "quality": {"status": "pass" if str(payload.get("status", "")).lower() == "passed" else "blocked", "reviewer": "repair-handoff-writer"},
        },
        "fix_loops": 0,
        "context_isolation": build_context_isolation(
            role_plane="qa",
            isolated_from=["implement-team"],
            shared_inputs=["docs/beacon/<version>/qa/test-cases", "implementation_summary", "technical_archive", "evidence_refs"],
            shared_outputs=["feature_scorecard", "repair_handoff", "qa_status"],
            rule="qa_must_not_inherit_implement_private_context",
        ),
    }
    save_team_state(project_root, team_name, state)

    artifact_dir = project_root / "docs" / "beacon" / version / "execution" / "qa-team" / feature_key / run_id
    role_reports: dict[str, dict[str, str]] = {}
    feature_scorecard = payload.get("feature_scorecard") if isinstance(payload.get("feature_scorecard"), dict) else {}
    stop_reasons = [str(item) for item in feature_scorecard.get("stop_reasons", []) if str(item).strip()]
    repair_handoff = feature_scorecard.get("repair_handoff") if isinstance(feature_scorecard.get("repair_handoff"), dict) else {}
    evidence_refs = [
        str(payload.get("feature_matrix_path") or ""),
        str(payload.get("ac_closure_path") or ""),
        str(payload.get("feature_scorecard_path") or ""),
    ]
    targeted_scenarios = [str(item) for item in payload.get("targeted_scenario_ids", []) if str(item).strip()]
    role_payloads = {
        "verifier": {
            "feature": feature,
            "status": payload.get("status", "unknown"),
            "summary": "qa-team verifier summarized coverage, blockers, and release readiness",
            "targeted_scenario_ids": targeted_scenarios,
            "stop_reasons": stop_reasons,
            "evidence_refs": [item for item in evidence_refs if item],
            "recommendations": ["Proceed to release review."] if str(payload.get("status", "")).lower() == "passed" else ["Use repair handoff and rerun QA after implementation fix."],
        },
        "repair-handoff-writer": {
            "feature": feature,
            "status": "completed",
            "summary": "qa-team repair handoff writer materialized blocker handoff from canonical feature scorecard",
            "targeted_scenario_ids": targeted_scenarios,
            "stop_reasons": stop_reasons,
            "evidence_refs": [str(repair_handoff.get("command") or "")] if repair_handoff else [],
            "recommendations": [str(repair_handoff.get("command") or "").strip()] if repair_handoff else ["No repair handoff required."],
        },
    }
    tmux_session = ""
    if resolved_runtime == "tmux":
        worker_specs = []
        for role, role_payload in role_payloads.items():
            json_path = artifact_dir / f"{role}.json"
            md_path = artifact_dir / f"{role}.md"
            spec_payload = {
                "role": role,
                "payload": role_payload,
                "output_json": str(json_path),
                "output_md": str(md_path),
                "result_path": str(worker_result_path(project_root, team_name=team_name, role=role)),
            }
            spec_path = write_worker_spec(project_root, team_name=team_name, role=role, payload=spec_payload)
            worker_specs.append({"role": role, "spec_path": spec_path})
        spawn_payload = spawn_tmux_workers(project_root, team_name=team_name, worker_specs=worker_specs)
        tmux_session = str(spawn_payload.get("tmux_session", "") or "")
        results = wait_for_worker_results(project_root, team_name=team_name, roles=list(role_payloads.keys()))
        worker_map = {item["role"]: item for item in spawn_payload.get("workers", []) if isinstance(item, dict)}
        for role in role_payloads:
            result = results.get(role, {})
            role_reports[role] = {
                "json": str(Path(str(result.get("json", ""))).relative_to(project_root)),
                "markdown": str(Path(str(result.get("markdown", ""))).relative_to(project_root)),
                "status": str(result.get("status", "") or role_payloads[role].get("status", "")),
                "pane_id": str(worker_map.get(role, {}).get("pane_id", "") or ""),
            }
    else:
        for role, role_payload in role_payloads.items():
            json_path = artifact_dir / f"{role}.json"
            md_path = artifact_dir / f"{role}.md"
            _write_json(json_path, role_payload)
            md_path.parent.mkdir(parents=True, exist_ok=True)
            md_path.write_text(_render_qa_team_role_markdown(role, role_payload), encoding="utf-8")
            role_reports[role] = {
                "json": str(json_path.relative_to(project_root)),
                "markdown": str(md_path.relative_to(project_root)),
                "status": str(role_payload.get("status", "")),
                "pane_id": "",
            }

    hud = write_team_hud(
        project_root,
        team_name=team_name,
        version=version,
        feature=feature_key,
        run_id=run_id,
        surface_dir="qa-team",
        runtime=resolved_runtime,
        tmux_session=tmux_session,
        roles=[
            {
                "worker_id": f"worker-{index+1:03d}",
                "role": role,
                "status": str(role_reports.get(role, {}).get("status", "") or ""),
                "pane_id": str(role_reports.get(role, {}).get("pane_id", "") or ""),
                "json": str(role_reports.get(role, {}).get("json", "") or ""),
                "markdown": str(role_reports.get(role, {}).get("markdown", "") or ""),
            }
            for index, role in enumerate(["verifier", "repair-handoff-writer"])
        ],
    )

    return {
        "team_name": team_name,
        "team_surface": "qa-team",
        "state_path": str(get_team_state_file(project_root, team_name).relative_to(project_root)),
        "artifact_dir": str(artifact_dir.relative_to(project_root)),
        "terminal_status": state["terminal_status"],
        "runtime": resolved_runtime,
        "tmux_session": tmux_session,
        "roles": ["verifier", "repair-handoff-writer"],
        "role_reports": role_reports,
        "context_isolation": state["context_isolation"],
        "hud": hud,
    }


def _extract_option(args: list[str], *names: str) -> str:
    index = 0
    while index < len(args):
        item = str(args[index])
        for name in names:
            if item == name and index + 1 < len(args):
                return str(args[index + 1])
            if item.startswith(f"{name}="):
                return item.split("=", 1)[1]
        index += 1
    return ""


def _strip_flag(args: list[str], flag: str) -> tuple[list[str], bool]:
    out: list[str] = []
    found = False
    for item in args:
        if item == flag:
            found = True
            continue
        out.append(item)
    return out, found


def _strip_option_with_value(args: list[str], option: str) -> list[str]:
    out: list[str] = []
    skip_next = False
    for item in args:
        if skip_next:
            skip_next = False
            continue
        if item == option:
            skip_next = True
            continue
        if str(item).startswith(f"{option}="):
            continue
        out.append(item)
    return out


def _first_positional(args: list[str]) -> str:
    skip_next = False
    for index, item in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if item in OPTION_NAMES_WITH_VALUE:
            skip_next = True
            continue
        if any(item.startswith(f"{name}=") for name in OPTION_NAMES_WITH_VALUE):
            continue
        if item in FLAG_NAMES or item.startswith("-"):
            continue
        return str(item)
    return ""


def _remove_first_positional(args: list[str]) -> list[str]:
    out: list[str] = []
    removed = False
    skip_next = False
    for item in args:
        if skip_next:
            out.append(item)
            skip_next = False
            continue
        if item in OPTION_NAMES_WITH_VALUE:
            out.append(item)
            skip_next = True
            continue
        if any(str(item).startswith(f"{name}=") for name in OPTION_NAMES_WITH_VALUE):
            out.append(item)
            continue
        if not removed and not str(item).startswith("-"):
            removed = True
            continue
        out.append(item)
    return out


def _sanitize_auto_test_passthrough_args(args: list[str]) -> list[str]:
    out = _remove_first_positional(args)
    for option in (
        "--project",
        "--project-root",
        "-p",
        "--version",
        "-v",
        "--mode",
        "--runtime",
        "--host-runtime",
        "--qa-matrix-path",
        "--matrix-path",
    ):
        out = _strip_option_with_value(out, option)
    for flag in ("--team-mode",):
        out, _ = _strip_flag(out, flag)
    return out


def _qa_matrix_matches_expected(qa_status: dict[str, Any], expected_matrix_path: Path) -> bool:
    qa9 = qa_status.get("qa9") if isinstance(qa_status.get("qa9"), dict) else {}
    candidates = [
        str(qa9.get("qa_matrix_path") or "").strip(),
    ]
    execution = qa_status.get("execution") if isinstance(qa_status.get("execution"), dict) else {}
    matrix_report = execution.get("matrix_report") if isinstance(execution.get("matrix_report"), dict) else {}
    candidates.append(str(matrix_report.get("matrix_path") or "").strip())
    expected = str(expected_matrix_path.resolve())
    for candidate in candidates:
        if not candidate:
            continue
        try:
            resolved = str(Path(candidate).resolve())
        except Exception:  # noqa: BLE001
            resolved = candidate
        if resolved == expected:
            return True
    return False


def _qa_status_run_id(qa_status: dict[str, Any]) -> str:
    if not isinstance(qa_status, dict):
        return ""
    execution = qa_status.get("execution") if isinstance(qa_status.get("execution"), dict) else {}
    return str(qa_status.get("run_id") or execution.get("run_id") or "").strip()


def _matching_qa_run_ids(project_root: Path, expected_matrix_path: Path) -> set[str]:
    run_ids: set[str] = set()
    current_status = load_qa_status(project_root)
    if _qa_matrix_matches_expected(current_status, expected_matrix_path):
        run_id = _qa_status_run_id(current_status)
        if run_id:
            run_ids.add(run_id)
    evidence_root = project_root / ".beacon" / "evidence" / "auto-test"
    if not evidence_root.exists():
        return run_ids
    for summary_path in evidence_root.glob("run-*/summary.json"):
        try:
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(payload, dict) or not _qa_matrix_matches_expected(payload, expected_matrix_path):
            continue
        run_id = _qa_status_run_id(payload)
        if run_id:
            run_ids.add(run_id)
    return run_ids


def _resolve_feature_qa_status(
    project_root: Path,
    *,
    expected_matrix_path: Path,
    exclude_run_ids: set[str] | None = None,
) -> dict[str, Any]:
    excluded = {str(item).strip() for item in (exclude_run_ids or set()) if str(item).strip()}
    current_status = load_qa_status(project_root)
    current_run_id = _qa_status_run_id(current_status)
    if (
        current_run_id
        and current_run_id not in excluded
        and _qa_matrix_matches_expected(current_status, expected_matrix_path)
    ):
        return current_status

    evidence_root = project_root / ".beacon" / "evidence" / "auto-test"
    if not evidence_root.exists():
        return current_status

    candidates: list[tuple[str, dict[str, Any]]] = []
    for summary_path in evidence_root.glob("run-*/summary.json"):
        try:
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(payload, dict) or not _qa_matrix_matches_expected(payload, expected_matrix_path):
            continue
        run_id = _qa_status_run_id(payload) or summary_path.parent.name
        if run_id in excluded:
            continue
        candidates.append((run_id, payload))
    if not candidates:
        return current_status
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def _looks_like_feature_request(args: list[str]) -> bool:
    positional = _first_positional(args)
    if not positional:
        return False
    return positional.strip().lower() not in KNOWN_SCOPES


def _explicit_layer_overrides(args: list[str]) -> set[str]:
    explicit: set[str] = set()
    index = 0
    while index < len(args):
        item = str(args[index])
        if item == "--layer-command" and index + 1 < len(args):
            raw = str(args[index + 1])
            if "=" in raw:
                layer = raw.split("=", 1)[0].strip().lower().replace("_", "-")
                if layer:
                    explicit.add(layer)
            index += 2
            continue
        if item.startswith("--layer-command="):
            raw = item.split("=", 1)[1]
            if "=" in raw:
                layer = raw.split("=", 1)[0].strip().lower().replace("_", "-")
                if layer:
                    explicit.add(layer)
            index += 1
            continue
        for layer, option_names in LAYER_SPECIFIC_OPTION_MAP.items():
            matched = False
            for option_name in option_names:
                if item == option_name:
                    explicit.add(layer)
                    index += 2
                    matched = True
                    break
                if item.startswith(f"{option_name}="):
                    explicit.add(layer)
                    index += 1
                    matched = True
                    break
            if matched:
                break
        else:
            index += 1
    return explicit


def _profile_layer_command_args(
    *,
    project_profile: dict[str, Any] | None,
    project_root: Path,
    feature: str,
    version: str,
    targeted_layers: list[str],
    raw_args: list[str],
) -> list[str]:
    if not isinstance(project_profile, dict) or not project_profile:
        return []
    profile_commands = project_profile.get("qa_layer_commands")
    if not isinstance(profile_commands, dict):
        return []

    explicit_layers = _explicit_layer_overrides(raw_args)
    context = {
        "project_root": str(project_root),
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": version,
        "profile_id": str(project_profile.get("profile_id") or ""),
    }
    auto_args: list[str] = []
    for raw_layer in targeted_layers:
        layer = str(raw_layer or "").strip().lower().replace("_", "-")
        if not layer or layer in explicit_layers:
            continue
        command_template = str(
            profile_commands.get(layer)
            or profile_commands.get(layer.replace("-", "_"))
            or profile_commands.get("default")
            or ""
        ).strip()
        if not command_template:
            continue
        auto_args.extend(["--layer-command", f"{layer}={format_template(command_template, context)}"])
    return auto_args


def _collect_evidence_refs(payload: dict[str, Any], *, project_root: Path, feature_matrix_rel: str) -> list[str]:
    refs: list[str] = [feature_matrix_rel, str(qa_status_path(project_root).relative_to(project_root)), str(qa_current_session_path(project_root).relative_to(project_root))]
    execution = payload.get("execution") if isinstance(payload.get("execution"), dict) else {}
    layers = execution.get("layers") if isinstance(execution.get("layers"), list) else []
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        layer_refs = layer.get("evidence_ref") if isinstance(layer.get("evidence_ref"), list) else []
        refs.extend(str(item) for item in layer_refs if str(item).strip())
    artifacts = execution.get("artifacts") if isinstance(execution.get("artifacts"), list) else []
    refs.extend(str(item) for item in artifacts if str(item).strip())
    refs.extend(
        str(item.get("evidence_ref") or "")
        for item in payload.get("per_item_results", [])
        if isinstance(item, dict) and item.get("evidence_ref")
    )
    ordered: list[str] = []
    seen: set[str] = set()
    for item in refs:
        if isinstance(item, list):
            for nested in item:
                text = str(nested).strip()
                if text and text not in seen:
                    seen.add(text)
                    ordered.append(text)
            continue
        text = str(item).strip()
        if text and text not in seen:
            seen.add(text)
            ordered.append(text)
    return ordered


def _run_feature_aware_qa(raw_args: list[str]) -> tuple[int, dict[str, Any]]:
    args, json_output = _strip_flag(raw_args, "--json")
    args, team_mode = _strip_flag(args, "--team-mode")
    feature = _first_positional(args)
    project_value = _extract_option(args, "--project", "--project-root", "-p")
    version = _extract_option(args, "--version", "-v") or "auto"
    mode = _extract_option(args, "--mode") or "feature-aware"
    runtime = _extract_option(args, "--runtime") or "file"
    host_runtime = _extract_option(args, "--host-runtime")
    project_root = Path(project_value).resolve() if project_value else Path.cwd()
    args = _strip_option_with_value(args, "--mode")
    args = _strip_option_with_value(args, "--runtime")
    current_session = load_current_qa_session(project_root)

    if metadata_machine_path(project_root).exists():
        metadata_verdict = verify_project_metadata(project_root, version=version if version != "auto" else "")
        if str(metadata_verdict.get("status") or "").lower() == "fail":
            blocked_payload = {
                "schema_version": "1.0",
                "feature": feature,
                "version": version,
                "status": "blocked",
                "reason_codes": ["project_metadata_contract_blocked"],
                "project_metadata_verification": metadata_verdict,
                "recommended_command": f"beacon doctor metadata verify --project-root {project_root} --version {version}",
            }
            if json_output:
                typer.echo(json.dumps(blocked_payload, ensure_ascii=False, indent=2))
            else:
                typer.echo("Beacon QA blocked: project metadata contract blocked", err=True)
            return 2, blocked_payload

    requirement_package_gate = build_requirement_package_gate(
        project_root,
        version=version if version != "auto" else None,
        feature=feature or "",
        strict=True,
    )
    if str(requirement_package_gate.get("status") or "").lower() == "blocked":
        blocked_payload = {
            "schema_version": "1.0",
            "feature": feature,
            "version": version,
            "status": "blocked",
            "reason_codes": ["requirement_package_contract_blocked"],
            "requirement_package_gate": requirement_package_gate,
            "recommended_command": str(requirement_package_gate.get("recommended_command") or "beacon-change"),
        }
        if json_output:
            typer.echo(json.dumps(blocked_payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon QA blocked: requirement package contract blocked", err=True)
        return 2, blocked_payload

    def _with_delivery_contract(
        payload: dict[str, Any],
        *,
        requirement_binding: dict[str, Any] | None = None,
        traceability_refs: list[str] | None = None,
        execution_surface: str | None = None,
    ) -> dict[str, Any]:
        contract = build_delivery_contract(
            feature=feature,
            version=version,
            requested_mode=str(payload.get("execution_mode") or mode),
            effective_mode=str(payload.get("execution_mode") or mode),
            execution_mode=str(payload.get("execution_mode") or mode),
            runner_mode=str(payload.get("execution_surface") or execution_surface or ("qa-team" if team_mode else "qa")),
            host_runtime=str(payload.get("host_runtime") or detect_host_runtime(host_runtime or None)),
            capability_snapshot=payload.get("capability_snapshot") if isinstance(payload.get("capability_snapshot"), dict) else {},
            subagent_prechecks=payload.get("subagent_prechecks") if isinstance(payload.get("subagent_prechecks"), dict) else {},
            requirement_binding=requirement_binding or {},
            traceability_refs=traceability_refs or [],
            runner=str(current_session.get("runner_type") or ""),
            execution_surface=str(payload.get("execution_surface") or execution_surface or ("qa-team" if team_mode else "qa")),
            team_mode=bool(payload.get("team_mode", team_mode)),
            qa_status=str(payload.get("status") or ""),
            release_ready=bool(payload.get("release_ready", False)),
            risk_flags=payload.get("reason_codes") if isinstance(payload.get("reason_codes"), list) else [],
        )
        payload["delivery_contract"] = contract
        payload["host_native_delivery"] = contract
        return payload

    project_profile = resolve_profile_for_feature(project_root, version=version, feature=feature)
    project_profile_gate = evaluate_project_profile_gate(project_root, version=version, feature=feature)
    project_orchestration: dict[str, Any] = project_profile_gate.get("orchestration", {}) if isinstance(project_profile_gate, dict) else {}
    if project_profile and str(project_profile_gate.get("status") or "") != "pass":
        orchestration_params: dict[str, str] = {}
        for key in ("origin", "profile_ref", "cookies_ref", "storage_state_ref"):
            value = str(current_session.get(key) or "").strip()
            if value:
                orchestration_params[key] = value
        orchestration_exit, project_orchestration = run_profile_orchestration(
            project_root,
            version=version,
            feature=feature,
            profile_id=str(project_profile.get("profile_id") or ""),
            stage="verify",
            params=orchestration_params,
        )
        project_profile_gate = evaluate_project_profile_gate(
            project_root,
            version=version,
            feature=feature,
            profile_id=str(project_profile.get("profile_id") or ""),
        )
        if orchestration_exit != 0 or str(project_profile_gate.get("status") or "") == "blocked":
            blocked_payload = {
                "schema_version": "1.0",
                "feature": feature,
                "version": version,
                "status": "blocked",
                "reason_codes": ["project_profile_gate_blocked"],
                "project_profile": project_profile,
                "project_profile_gate": project_profile_gate,
                "project_orchestration": project_orchestration,
                "session_id": str(current_session.get("session_id") or ""),
            }
            _with_delivery_contract(blocked_payload)
            write_feature_qa_status(project_root, feature=feature, payload=blocked_payload)
            if json_output:
                typer.echo(json.dumps(blocked_payload, ensure_ascii=False, indent=2))
            else:
                typer.echo(f"Beacon QA blocked: project profile gate blocked for {feature}", err=True)
            return 2, blocked_payload

    resolved_host_runtime = detect_host_runtime(host_runtime or None)
    subagent_prechecks: dict[str, Any] = {
        "required": False,
        "host_runtime": resolved_host_runtime,
        "runtime_readiness": {},
        "delegation_readiness": {},
    }
    if team_mode:
        if runtime_context_precheck_required(
            version=version,
            adapter_id="qa-team",
            adapter_type="native",
            runtime_family="beacon-native",
            mode="team",
            runtime=runtime,
        ):
            runtime_precheck = runtime_readiness_precheck(project_root, host_runtime=resolved_host_runtime)
        else:
            runtime_precheck = runtime_context_not_required_precheck(
                host_runtime=resolved_host_runtime,
                detail=(
                    "Local QA team runtime is executed through Beacon-native orchestration; "
                    "project AGENTS/CLAUDE context files are not required for this surface."
                ),
            )
        delegation_precheck = delegation_readiness_precheck(project_root, feature=feature, version=version)
        subagent_prechecks = {
            "required": True,
            "host_runtime": resolved_host_runtime,
            "runtime_readiness": runtime_precheck,
            "delegation_readiness": delegation_precheck,
        }
        if str(runtime_precheck.get("status", "")).strip().lower() != "pass":
            blocked_payload = {
                "schema_version": "1.0",
                "feature": feature,
                "version": version,
                "status": "blocked",
                "reason_codes": [str(runtime_precheck.get("reason_code", "runtime_not_ready") or "runtime_not_ready")],
                "host_runtime": resolved_host_runtime,
                "subagent_prechecks": subagent_prechecks,
                "recommended_command": str(runtime_precheck.get("recommended_command", "") or ""),
            }
            _with_delivery_contract(blocked_payload)
            write_feature_qa_status(project_root, feature=feature, payload=blocked_payload)
            if json_output:
                typer.echo(json.dumps(blocked_payload, ensure_ascii=False, indent=2))
            else:
                typer.echo(f"Beacon QA blocked: {blocked_payload['reason_codes'][0]}", err=True)
            return 2, blocked_payload
        if str(delegation_precheck.get("status", "")).strip().lower() != "pass":
            blocked_payload = {
                "schema_version": "1.0",
                "feature": feature,
                "version": version,
                "status": "blocked",
                "reason_codes": [str(delegation_precheck.get("reason_code", "delegation_not_ready") or "delegation_not_ready")],
                "host_runtime": resolved_host_runtime,
                "subagent_prechecks": subagent_prechecks,
                "recommended_command": str(delegation_precheck.get("recommended_command", "") or ""),
            }
            _with_delivery_contract(blocked_payload)
            write_feature_qa_status(project_root, feature=feature, payload=blocked_payload)
            if json_output:
                typer.echo(json.dumps(blocked_payload, ensure_ascii=False, indent=2))
            else:
                typer.echo(f"Beacon QA blocked: {blocked_payload['reason_codes'][0]}", err=True)
            return 2, blocked_payload

    plan = build_feature_qa_plan(project_root, version=version, feature=feature, execution_mode=mode)
    team_contract = qa_team_contract(project_root, version=version, feature=feature)
    handoff = load_implement_to_qa_handoff(
        project_root,
        feature=feature,
        run_id=str(plan.get("implementation_run_id") or ""),
    ) if str(plan.get("implementation_run_id") or "").strip() else {}
    if not bool(plan.get("implementation_done", False)):
        if json_output:
            typer.echo(json.dumps(plan, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon QA blocked: implementation not recorded for {feature}", err=True)
        return 2, plan

    if not list(plan.get("targeted_entries") or []):
        current_status = load_qa_status(project_root)
        if str(current_status.get("status") or "").strip().lower() == "passed":
            current_run_id = str(current_status.get("run_id") or plan.get("implementation_run_id") or "").strip()
            coverage_summary_path = write_coverage_summary(
                project_root,
                version=version,
                run_id=current_run_id,
            )
            payload = {
                **current_status,
                **plan,
                "run_id": current_run_id,
                "status": "passed",
                "implementation_done": True,
                "evidence_done": True,
                "feature_matrix_path": str(feature_qa_matrix_path(project_root, feature=feature).relative_to(project_root)),
                "message": "feature has no executable QA matrix entries; reused existing passed QA status",
                "team_mode": bool(team_mode),
                "host_runtime": resolved_host_runtime,
                "subagent_prechecks": subagent_prechecks,
                "team_contract": team_contract,
                "implement_to_qa_handoff": handoff,
            }
            _with_delivery_contract(
                payload,
                requirement_binding={
                    "source_of_truth_root": f"docs/beacon/{version}",
                    "feature_matrix_path": str(feature_qa_matrix_path(project_root, feature=feature).relative_to(project_root)),
                },
                traceability_refs=[
                    str(feature_qa_matrix_path(project_root, feature=feature).relative_to(project_root)),
                    str(handoff.get("summary_ref") or ""),
                    str(handoff.get("technical_archive_ref") or ""),
                ],
                execution_surface="qa-team" if team_mode else "qa",
            )
            if team_mode:
                payload["team_execution"] = _materialize_qa_team_surface(
                    project_root,
                    version=version,
                    feature=feature,
                    run_id=current_run_id or plan.get("implementation_run_id") or "feature-qa",
                    payload=payload,
                    runtime=runtime,
                )
                payload["execution_surface"] = "qa-team"
                payload["context_isolation"] = payload["team_execution"].get("context_isolation", {})
            feature_status_file = write_feature_qa_status(project_root, feature=feature, payload=payload)
            manifest_refs = [str(feature_status_file.relative_to(project_root))]
            for candidate in (
                project_root / ".beacon" / "auto-test-status.json",
                coverage_summary_path,
                project_root / ".beacon" / "qa" / "status.json",
            ):
                if candidate.exists():
                    manifest_refs.append(str(candidate.relative_to(project_root)))
            _update_evidence_manifest(
                project_root,
                manifest_refs,
                run_id=current_run_id,
                version=version,
            )
            if json_output:
                typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                typer.echo(f"✓ Feature QA reused existing pass: {feature}")
                typer.echo(f"  Reason: {payload['message']}")
            return 0, payload

    if str(plan.get("status") or "") == "up_to_date":
        existing_status = load_feature_qa_status(project_root, feature=feature)
        current_status = load_qa_status(project_root)
        current_run_id = str(current_status.get("run_id") or existing_status.get("run_id") or plan.get("implementation_run_id") or "").strip()
        coverage_summary_path = write_coverage_summary(
            project_root,
            version=version,
            run_id=current_run_id,
        )
        payload = {
            **existing_status,
            **plan,
            "feature_matrix_path": str(feature_qa_matrix_path(project_root, feature=feature).relative_to(project_root)),
            "message": "feature QA already up to date; no rerun required",
            "team_mode": bool(team_mode),
            "host_runtime": resolved_host_runtime,
            "subagent_prechecks": subagent_prechecks,
            "team_contract": team_contract,
            "implement_to_qa_handoff": handoff,
        }
        _with_delivery_contract(
            payload,
            requirement_binding={
                "source_of_truth_root": f"docs/beacon/{version}",
                "feature_matrix_path": str(feature_qa_matrix_path(project_root, feature=feature).relative_to(project_root)),
            },
            traceability_refs=[
                str(feature_qa_matrix_path(project_root, feature=feature).relative_to(project_root)),
                str(handoff.get("summary_ref") or ""),
                str(handoff.get("technical_archive_ref") or ""),
            ],
            execution_surface="qa-team" if team_mode else "qa",
        )
        if team_mode:
            payload["team_execution"] = _materialize_qa_team_surface(
                project_root,
                version=version,
                feature=feature,
                run_id=str(payload.get("run_id") or plan.get("implementation_run_id") or "feature-qa"),
                payload=payload,
                runtime=runtime,
            )
            payload["execution_surface"] = "qa-team"
            payload["context_isolation"] = payload["team_execution"].get("context_isolation", {})
        feature_status_path = write_feature_qa_status(project_root, feature=feature, payload=payload)
        manifest_refs = [str(feature_status_path.relative_to(project_root))]
        for candidate in (
            project_root / ".beacon" / "auto-test-status.json",
            coverage_summary_path,
            project_root / ".beacon" / "qa" / "status.json",
        ):
            if candidate.exists():
                manifest_refs.append(str(candidate.relative_to(project_root)))
        for key in ("canonical_matrix_path", "ac_closure_path", "feature_scorecard_path"):
            value = str(payload.get(key) or "").strip()
            if value:
                manifest_refs.append(value)
        _update_evidence_manifest(
            project_root,
            manifest_refs,
            run_id=current_run_id,
            version=version,
        )
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"✓ Feature QA up to date: {feature}")
            typer.echo(f"  Reason: {payload['message']}")
        return 0, payload

    matrix_path = materialize_feature_qa_matrix(project_root, plan=plan)
    passthrough_args = _sanitize_auto_test_passthrough_args(args)
    auto_args = [
        "auto-test",
        "create",
        "qa9",
        *passthrough_args,
        "--project",
        str(project_root),
        "--version",
        version,
        "--qa-matrix-path",
        str(matrix_path),
        "--qa-types",
        ",".join(plan.get("targeted_layers") or ["contract"]),
        "--ui-runner",
        "browser-use",
        "--require-fresh-evidence",
    ]
    auto_args.extend(
        _profile_layer_command_args(
            project_profile=project_profile,
            project_root=project_root,
            feature=feature,
            version=version,
            targeted_layers=list(plan.get("targeted_layers") or []),
            raw_args=args,
        )
    )
    known_matching_run_ids = _matching_qa_run_ids(project_root, matrix_path)
    command_exit = _beacon_exec_silent(auto_args, cwd=_repo_root()) if json_output else _beacon_exec(auto_args, cwd=_repo_root())
    if command_exit != 0:
        blocked_payload = {
            **plan,
            "status": "blocked",
            "reason_codes": sorted({*list(plan.get("reason_codes") or []), "auto_test_invocation_failed"}),
            "message": "auto-test qa9 invocation failed; stale QA status was not accepted",
            "command_exit": int(command_exit),
            "auto_test_args": auto_args,
            "team_mode": bool(team_mode),
            "host_runtime": resolved_host_runtime,
            "subagent_prechecks": subagent_prechecks,
            "team_contract": team_contract,
            "implement_to_qa_handoff": handoff,
        }
        _with_delivery_contract(
            blocked_payload,
            requirement_binding={"source_of_truth_root": f"docs/beacon/{version}"},
            traceability_refs=[str(matrix_path.relative_to(project_root))],
            execution_surface="qa-team" if team_mode else "qa",
        )
        if team_mode:
            blocked_payload["team_execution"] = _materialize_qa_team_surface(
                project_root,
                version=version,
                feature=feature,
                run_id=str(plan.get("implementation_run_id") or "feature-qa"),
                payload=blocked_payload,
                runtime=runtime,
            )
            blocked_payload["execution_surface"] = "qa-team"
            blocked_payload["context_isolation"] = blocked_payload["team_execution"].get("context_isolation", {})
        feature_status_file = write_feature_qa_status(project_root, feature=feature, payload=blocked_payload)
        _update_evidence_manifest(
            project_root,
            [str(feature_status_file.relative_to(project_root))],
            run_id=str(plan.get("implementation_run_id") or ""),
            version=version,
        )
        if json_output:
            typer.echo(json.dumps(blocked_payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon QA blocked: auto-test qa9 invocation failed", err=True)
        return 2, blocked_payload
    qa_status = _resolve_feature_qa_status(
        project_root,
        expected_matrix_path=matrix_path,
        exclude_run_ids=known_matching_run_ids,
    )
    if not _qa_matrix_matches_expected(qa_status, matrix_path):
        blocked_payload = {
            **plan,
            "status": "blocked",
            "reason_codes": sorted({*list(plan.get("reason_codes") or []), "qa_matrix_mismatch"}),
            "message": "auto-test returned QA status for a different matrix; current feature evidence was rejected",
            "command_exit": int(command_exit),
            "expected_qa_matrix_path": str(matrix_path),
            "observed_qa_matrix_path": str(((qa_status.get("qa9") or {}).get("qa_matrix_path")) or ""),
            "team_mode": bool(team_mode),
            "host_runtime": resolved_host_runtime,
            "subagent_prechecks": subagent_prechecks,
            "team_contract": team_contract,
            "implement_to_qa_handoff": handoff,
        }
        _with_delivery_contract(
            blocked_payload,
            requirement_binding={"source_of_truth_root": f"docs/beacon/{version}"},
            traceability_refs=[
                str(matrix_path.relative_to(project_root)),
                str(((qa_status.get("qa9") or {}).get("qa_matrix_path")) or ""),
            ],
            execution_surface="qa-team" if team_mode else "qa",
        )
        if team_mode:
            blocked_payload["team_execution"] = _materialize_qa_team_surface(
                project_root,
                version=version,
                feature=feature,
                run_id=str(qa_status.get("run_id") or plan.get("implementation_run_id") or "feature-qa"),
                payload=blocked_payload,
                runtime=runtime,
            )
            blocked_payload["execution_surface"] = "qa-team"
            blocked_payload["context_isolation"] = blocked_payload["team_execution"].get("context_isolation", {})
        feature_status_file = write_feature_qa_status(project_root, feature=feature, payload=blocked_payload)
        _update_evidence_manifest(
            project_root,
            [str(feature_status_file.relative_to(project_root))],
            run_id=str(qa_status.get("run_id") or plan.get("implementation_run_id") or ""),
            version=version,
        )
        if json_output:
            typer.echo(json.dumps(blocked_payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon QA blocked: QA matrix mismatch", err=True)
        return 2, blocked_payload
    verified_ids, failed_ids, per_item_results = collect_verification_writeback(plan=plan, qa_status=qa_status)
    feature_matrix_rel = str(matrix_path.relative_to(project_root))

    record_verification_writeback(
        project_root,
        version=version,
        feature=feature,
        run_id=str(qa_status.get("run_id") or plan.get("implementation_run_id") or "feature-qa"),
        verified_item_ids=verified_ids,
        failed_item_ids=failed_ids,
        evidence_ref=_collect_evidence_refs(qa_status, project_root=project_root, feature_matrix_rel=feature_matrix_rel),
    )

    blocking_updates = plan.get("blocking_artifact_updates") if isinstance(plan.get("blocking_artifact_updates"), list) else []
    qa_status = dict(qa_status)
    qa_status["feature"] = feature
    qa_status["feature_slug"] = str(plan.get("feature_slug") or "")
    qa_status["implementation_done"] = True
    qa_status["evidence_done"] = str(qa_status.get("status") or "").strip().lower() == "passed"
    qa_status["story_sequence"] = plan.get("story_sequence", [])
    qa_status["targeted_rerun"] = {
        "required": True,
        "reason_codes": plan.get("reason_codes", []),
        "targeted_layers": plan.get("targeted_layers", []),
        "targeted_ac_ids": plan.get("targeted_ac_ids", []),
        "targeted_tc_ids": plan.get("targeted_tc_ids", []),
        "targeted_scenario_ids": plan.get("targeted_scenario_ids", []),
        "targeted_scenario_families": plan.get("targeted_scenario_families", []),
    }
    qa_status["boundary_evidence"] = {
        "boundary_principles": plan.get("boundary_principles", []),
        "assumption_capture_required": True,
        "goal_driven_verification_required": True,
        "targeted_scope_only": bool(plan.get("targeted_tc_ids") or plan.get("targeted_ac_ids")),
        "verification_item_count": len(per_item_results),
    }
    qa_status["feature_matrix_path"] = feature_matrix_rel
    qa_status["blocking_artifact_updates"] = blocking_updates
    qa_status["per_item_results"] = per_item_results
    qa_status["execution_mode"] = str(plan.get("execution_mode") or mode)
    qa_status["project_profile"] = project_profile or {}
    qa_status["project_profile_gate"] = project_profile_gate if isinstance(project_profile_gate, dict) else {}
    qa_status["project_orchestration"] = project_orchestration if isinstance(project_orchestration, dict) else {}
    qa_status["current_session_id"] = str(current_session.get("session_id") or "")
    canonical_matrix = writeback_feature_matrix_evidence(
        project_root,
        plan=plan,
        per_item_results=per_item_results,
        run_id=str(qa_status.get("run_id") or ""),
    )
    if canonical_matrix is not None:
        qa_status["canonical_matrix_path"] = str(canonical_matrix.relative_to(project_root))
    exhaustiveness = build_exhaustiveness_report(
        project_root,
        feature=feature,
        run_id=str(qa_status.get("run_id") or plan.get("implementation_run_id") or "feature-qa"),
        plan=plan,
        qa_status=qa_status,
    )
    write_exhaustiveness_report(project_root, feature=feature, payload=exhaustiveness)
    qa_status["exhaustiveness"] = exhaustiveness
    scenario_results_v2, ac_closure, feature_scorecard, ac_closure_path, feature_scorecard_path = build_feature_qa_precision_artifacts(
        project_root,
        feature=feature,
        run_id=str(qa_status.get("run_id") or plan.get("implementation_run_id") or "feature-qa"),
        plan=plan,
        per_item_results=per_item_results,
        project_profile_gate=project_profile_gate,
        qa_status=qa_status,
        exhaustiveness=exhaustiveness,
    )
    qa_status["scenario_results_v2"] = scenario_results_v2
    qa_status["ac_closure_path"] = str(ac_closure_path.relative_to(project_root))
    qa_status["feature_scorecard_path"] = str(feature_scorecard_path.relative_to(project_root))
    qa_status["feature_scorecard"] = feature_scorecard
    qa_status["release_ready"] = bool(feature_scorecard.get("release_ready", False))
    if qa_status["release_ready"]:
        qa_status["status"] = "passed"
        qa_status["evidence_done"] = True
    if str(exhaustiveness.get("status") or "").strip().lower() != "passed" and not qa_status["release_ready"]:
        qa_status["status"] = "blocked"
        qa_status["evidence_done"] = False
        qa_status["release_ready"] = False
    _with_delivery_contract(
        qa_status,
        requirement_binding={
            "source_of_truth_root": f"docs/beacon/{version}",
            "feature_matrix_path": feature_matrix_rel,
            "canonical_matrix_path": str(qa_status.get("canonical_matrix_path") or ""),
        },
        traceability_refs=[
            feature_matrix_rel,
            str(qa_status.get("canonical_matrix_path") or ""),
            str(ac_closure_path.relative_to(project_root)),
            str(feature_scorecard_path.relative_to(project_root)),
            str(handoff.get("summary_ref") or ""),
            str(handoff.get("technical_archive_ref") or ""),
        ],
        execution_surface="qa-team" if team_mode else "qa",
    )
    refreshed_fingerprint = generate_spec_fingerprint(
        project_root,
        run_id=str(qa_status.get("run_id") or plan.get("implementation_run_id") or "feature-qa"),
        version=version,
    )
    refreshed_hash = str(refreshed_fingerprint.get("fingerprint_hash", "") or "").strip()
    if refreshed_hash:
        qa_status["current_spec_fingerprint_hash"] = refreshed_hash
        qa_status["spec_fingerprint_hash"] = refreshed_hash
        execution_payload = qa_status.get("execution")
        if isinstance(execution_payload, dict):
            execution_payload["spec_fingerprint"] = {
                "fingerprint_hash": refreshed_hash,
                "version": str(qa_status.get("version") or version),
                "generated_at": str(refreshed_fingerprint.get("generated_at", "") or ""),
            }
        auto_test_status_path = project_root / ".beacon" / "auto-test-status.json"
        if auto_test_status_path.exists():
            try:
                auto_test_status = json.loads(auto_test_status_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                auto_test_status = {}
            if isinstance(auto_test_status, dict):
                auto_test_status["spec_fingerprint_hash"] = refreshed_hash
                execution_payload = auto_test_status.get("execution")
                if isinstance(execution_payload, dict):
                    execution_payload["spec_fingerprint"] = {
                        "fingerprint_hash": refreshed_hash,
                        "version": str(qa_status.get("version") or version),
                        "generated_at": str(refreshed_fingerprint.get("generated_at", "") or ""),
                    }
                auto_test_status_path.write_text(
                    json.dumps(auto_test_status, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
    status_paths = write_qa_status(project_root, qa_status)
    coverage_summary_path = write_coverage_summary(
        project_root,
        version=version,
        run_id=str(qa_status.get("run_id") or ""),
    )
    manifest_refs = [status_paths["legacy"], status_paths["canonical"]]
    if canonical_matrix is not None:
        manifest_refs.append(str(canonical_matrix.relative_to(project_root)))
    manifest_refs.extend(
        [
            str(coverage_summary_path.relative_to(project_root)),
            str(ac_closure_path.relative_to(project_root)),
            str(feature_scorecard_path.relative_to(project_root)),
        ]
    )
    acceptance_writeback: dict[str, Any] | None = None
    if bool(qa_status.get("evidence_done")) and str(qa_status.get("status") or "").strip().lower() == "passed":
        accepted_ac_ids = [
            str(item.get("ac_id") or "").strip()
            for item in (ac_closure.get("reports") if isinstance(ac_closure.get("reports"), list) else [])
            if isinstance(item, dict) and str(item.get("closure_status") or "").strip() == "accepted" and str(item.get("ac_id") or "").strip()
        ]
        accepted_test_ids = sorted(
            {
                str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
                for item in scenario_results_v2
                if str(item.get("closure_outcome") or "").strip() == "accepted"
                and str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
            }
        )
        record_verification_writeback(
            project_root,
            version=version,
            feature=feature,
            run_id=str(qa_status.get("run_id") or plan.get("implementation_run_id") or "feature-qa"),
            verified_item_ids=[*accepted_ac_ids, *accepted_test_ids],
            failed_item_ids=[],
            evidence_ref=manifest_refs,
        )
        acceptance_result = record_acceptance_writeback(
            project_root,
            version=version,
            feature=feature,
            accepted_by="qa",
            verdict="passed",
            run_id=str(qa_status.get("run_id") or plan.get("implementation_run_id") or "feature-qa"),
            evidence_ref=manifest_refs,
            source_command=f'beacon qa run "{feature}" --project-root {project_root} --version {version}',
            accepted_ac_ids=accepted_ac_ids,
            accepted_test_ids=accepted_test_ids,
        )
        acceptance_writeback = {
            "status": "completed",
            "machine_path": str(acceptance_result.get("machine_path") or ""),
            "markdown_path": str(acceptance_result.get("markdown_path") or ""),
            "runtime_path": str(acceptance_result.get("runtime_path") or ""),
            "transaction_id": str(acceptance_result.get("acceptance_envelope", {}).get("transaction_id", "") or ""),
            "source_hash": str(acceptance_result.get("acceptance_envelope", {}).get("source_hash", "") or ""),
            "projection_seq": acceptance_result.get("acceptance_envelope", {}).get("projection_seq"),
            "transaction_status": str(acceptance_result.get("acceptance_envelope", {}).get("transaction_status", "") or ""),
        }
        manifest_refs.extend(
            [
                str(acceptance_result.get("machine_path") or ""),
                str(acceptance_result.get("markdown_path") or ""),
                str(acceptance_result.get("runtime_path") or ""),
            ]
        )
    payload = {
        **plan,
        "run_id": str(qa_status.get("run_id") or ""),
        "status": str(qa_status.get("status") or "unknown"),
        "implementation_done": True,
        "evidence_done": bool(qa_status.get("evidence_done", False)),
        "feature_matrix_path": feature_matrix_rel,
        "blocking_artifact_updates": blocking_updates,
        "per_item_results": per_item_results,
        "verified_item_ids": verified_ids,
        "failed_item_ids": failed_ids,
        "targeted_scenario_ids": list(plan.get("targeted_scenario_ids") or []),
        "targeted_scenario_families": list(plan.get("targeted_scenario_families") or []),
        "story_scenario_map_path": str(plan.get("story_scenario_map_path") or ""),
        "exhaustiveness": exhaustiveness,
        "project_profile": project_profile or {},
        "project_profile_gate": project_profile_gate if isinstance(project_profile_gate, dict) else {},
        "current_session_id": str(current_session.get("session_id") or ""),
        "scenario_results_v2": scenario_results_v2,
        "ac_closure": ac_closure,
        "feature_scorecard": feature_scorecard,
        "ac_closure_path": str(ac_closure_path.relative_to(project_root)),
        "feature_scorecard_path": str(feature_scorecard_path.relative_to(project_root)),
        "team_mode": bool(team_mode),
        "host_runtime": resolved_host_runtime,
        "subagent_prechecks": subagent_prechecks,
        "team_contract": team_contract,
        "implement_to_qa_handoff": handoff,
        "acceptance_writeback": acceptance_writeback or {"status": "skipped"},
    }
    _with_delivery_contract(
        payload,
        requirement_binding={
            "source_of_truth_root": f"docs/beacon/{version}",
            "feature_matrix_path": feature_matrix_rel,
            "canonical_matrix_path": str(qa_status.get("canonical_matrix_path") or ""),
        },
        traceability_refs=[
            feature_matrix_rel,
            str(qa_status.get("canonical_matrix_path") or ""),
            str(ac_closure_path.relative_to(project_root)),
            str(feature_scorecard_path.relative_to(project_root)),
            str(handoff.get("summary_ref") or ""),
            str(handoff.get("technical_archive_ref") or ""),
        ],
        execution_surface="qa-team" if team_mode else "qa",
    )
    if team_mode:
        payload["team_execution"] = _materialize_qa_team_surface(
            project_root,
            version=version,
            feature=feature,
            run_id=str(qa_status.get("run_id") or plan.get("implementation_run_id") or "feature-qa"),
            payload=payload,
            runtime=runtime,
        )
        payload["execution_surface"] = "qa-team"
        payload["context_isolation"] = payload["team_execution"].get("context_isolation", {})
    feature_status_file = write_feature_qa_status(project_root, feature=feature, payload=payload)
    manifest_refs.extend(
        [
            str(feature_status_file.relative_to(project_root)),
            str(feature_qa_plan_path(project_root, feature=feature).relative_to(project_root)),
            str(feature_qa_matrix_path(project_root, feature=feature).relative_to(project_root)),
            str(feature_exhaustiveness_report_path(project_root, feature=feature).relative_to(project_root)),
            str(feature_qa_status_path(project_root, feature=feature).relative_to(project_root)),
        ]
    )
    _update_evidence_manifest(
        project_root,
        manifest_refs,
        run_id=str(qa_status.get("run_id") or ""),
        version=version,
    )
    refresh_evidence_manifest(
        project_root,
        refs=list(dict.fromkeys(manifest_refs)),
        version=str(qa_status.get("version") or version),
    )

    final_status = str(qa_status.get("status") or "").strip().lower()
    exit_code = 0 if final_status == "passed" else command_exit
    if exit_code == 0 and final_status != "passed":
        exit_code = 2

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Feature QA status: {payload['status']}")
        typer.echo(f"  feature: {feature}")
        typer.echo(f"  matrix: {feature_matrix_rel}")
        typer.echo(f"  evidence_done: {payload['evidence_done']}")
        typer.echo(f"  continue_decision: {feature_scorecard.get('continue_decision', 'continue')}")
        coverage_current = feature_scorecard.get("coverage_current") if isinstance(feature_scorecard.get("coverage_current"), dict) else {}
        if coverage_current:
            typer.echo(
                f"  coverage: {coverage_current.get('executed_scenarios', 0)}/{coverage_current.get('required_scenarios', 0)} ({coverage_current.get('coverage_rate', 0)})"
            )
        if str(feature_scorecard.get("continue_decision") or "") == "stop_for_repair":
            typer.echo(f"  stop_reasons: {', '.join(feature_scorecard.get('stop_reasons', [])) or '-'}")
            typer.echo(f"  resume_command: {feature_scorecard.get('resume_command', '')}")
        if blocking_updates:
            typer.echo(f"  blocking_artifact_updates: {len(blocking_updates)}")
    return exit_code, payload


@app.command(
    "run",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def run(
    ctx: typer.Context,
    feature: Optional[str] = typer.Argument(None, help="Feature name or legacy QA scope"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    mode: str = typer.Option("feature-aware", "--mode", help="QA execution mode"),
    runtime: str = typer.Option("file", "--runtime", help="Runtime mode: file/tmux/auto"),
    host_runtime: str = typer.Option("", "--host-runtime", help="Host runtime for native subagent checks: codex|claude"),
    layer_command: Optional[list[str]] = typer.Option(None, "--layer-command", help="Override a QA layer command using layer=command (repeatable)"),
    team_mode: bool = typer.Option(False, "--team-mode", help="Run through the explicit qa-team surface"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Run QA in scope mode or feature-aware mode (`beacon qa run <feature>`)."""
    raw_args: list[str] = []
    if feature:
        raw_args.append(feature)
    if project:
        raw_args.extend(["--project", project])
    if version:
        raw_args.extend(["--version", version])
    if mode:
        raw_args.extend(["--mode", mode])
    if runtime:
        raw_args.extend(["--runtime", runtime])
    if host_runtime:
        raw_args.extend(["--host-runtime", host_runtime])
    for item in layer_command or []:
        raw_args.extend(["--layer-command", item])
    if team_mode:
        raw_args.append("--team-mode")
    if json_output:
        raw_args.append("--json")
    raw_args.extend(str(item) for item in ctx.args)

    if _looks_like_feature_request(raw_args):
        code, _ = _run_feature_aware_qa(raw_args)
        raise typer.Exit(code=code)
    code = _beacon_exec(["auto-test", "create", *raw_args], cwd=_repo_root())
    raise typer.Exit(code=code)


@app.command("team-run")
def team_run(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    mode: str = typer.Option("feature-aware", "--mode", help="QA execution mode"),
    runtime: str = typer.Option("file", "--runtime", help="Runtime mode: file/tmux/auto"),
    host_runtime: str = typer.Option("", "--host-runtime", help="Host runtime for native subagent checks: codex|claude"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Run QA through the explicit qa-team surface with isolated context."""
    raw_args = [
        feature,
        "--project",
        str(Path(project).resolve() if project else Path.cwd()),
        "--version",
        version,
        "--mode",
        mode,
        "--runtime",
        runtime,
        "--host-runtime",
        host_runtime,
        "--team-mode",
    ]
    if json_output:
        raw_args.append("--json")
    code, payload = _run_feature_aware_qa(raw_args)
    if not json_output:
        typer.echo(f"Beacon QA team-run status: {payload.get('status')}")
        typer.echo(f"  feature: {feature}")
        if payload.get("team_execution"):
            typer.echo(f"  team_surface: {payload.get('team_execution', {}).get('team_surface', '')}")
            typer.echo(f"  state_path: {payload.get('team_execution', {}).get('state_path', '')}")
    raise typer.Exit(code=code)


@app.command("evolve")
def evolve(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    mode: str = typer.Option("feature-aware", "--mode", help="QA execution mode: feature-aware/story-exhaustive"),
    write_matrix: bool = typer.Option(True, "--write-matrix/--no-write-matrix", help="Write targeted matrix for rerun"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Compute the delta-aware rerun plan for a feature without executing QA."""
    project_root = Path(project).resolve() if project else Path.cwd()
    plan = build_feature_qa_plan(
        project_root,
        version=version,
        feature=feature,
        execution_mode=mode,
        persist=write_matrix,
    )
    if write_matrix and plan.get("targeted_entries"):
        matrix_path = materialize_feature_qa_matrix(project_root, plan=plan)
        plan["feature_matrix_path"] = str(matrix_path.relative_to(project_root))
    if write_matrix:
        write_feature_qa_status(project_root, feature=feature, payload=plan)
    if json_output:
        typer.echo(json.dumps(plan, ensure_ascii=False, indent=2))
        return
    typer.echo(f"Beacon QA evolve: {feature}")
    typer.echo(f"- status: {plan.get('status')}")
    typer.echo(f"- mode: {plan.get('execution_mode')}")
    typer.echo(f"- targeted_layers: {', '.join(plan.get('targeted_layers', [])) or '-'}")
    typer.echo(f"- targeted_tc_ids: {', '.join(plan.get('targeted_tc_ids', [])) or '-'}")
    typer.echo(f"- targeted_scenario_ids: {', '.join(plan.get('targeted_scenario_ids', [])) or '-'}")
    typer.echo(f"- reason_codes: {', '.join(plan.get('reason_codes', [])) or '-'}")


@app.command("team-plan")
def team_plan(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    mode: str = typer.Option("feature-aware", "--mode", help="QA execution mode"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Build a QA plan with explicit qa-team execution guidance."""
    project_root = Path(project).resolve() if project else Path.cwd()
    plan = build_feature_qa_plan(project_root, version=version, feature=feature, execution_mode=mode)
    plan["team_surface"] = "qa-team"
    plan["team_mode"] = True
    plan["team_contract"] = qa_team_contract(project_root, version=version, feature=feature)
    if json_output:
        typer.echo(json.dumps(plan, ensure_ascii=False, indent=2))
        return
    typer.echo(f"Beacon QA team-plan: {feature}")
    typer.echo(f"- team_surface: qa-team")
    typer.echo(f"- run_command: {plan['team_contract'].get('run_command', '')}")


@app.command("status")
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Read canonical QA status, falling back to legacy auto-test status."""
    project_root = Path(project) if project else Path.cwd()
    payload = load_qa_status(project_root)
    if not payload:
        typer.echo("No QA status found. Run `beacon qa run ...` first.")
        raise typer.Exit(1)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon QA Status")
    typer.echo("=" * 40)
    typer.echo(f"Status: {payload.get('status', 'N/A')}")
    typer.echo(f"Version: {payload.get('version', 'N/A')}")
    typer.echo(f"Run ID: {payload.get('run_id', 'N/A')}")
    typer.echo(f"Scope: {payload.get('scope', 'N/A')}")
    feature = str(payload.get("feature") or "").strip()
    if feature:
        typer.echo(f"Feature: {feature}")
        typer.echo(f"Evidence done: {payload.get('evidence_done')}")
        typer.echo(f"Execution mode: {payload.get('execution_mode', 'feature-aware')}")
        typer.echo(f"Host runtime: {payload.get('host_runtime', 'N/A') or 'N/A'}")
        prechecks = payload.get("subagent_prechecks") if isinstance(payload.get("subagent_prechecks"), dict) else {}
        if prechecks:
            runtime_precheck = prechecks.get("runtime_readiness") if isinstance(prechecks.get("runtime_readiness"), dict) else {}
            delegation_precheck = prechecks.get("delegation_readiness") if isinstance(prechecks.get("delegation_readiness"), dict) else {}
            typer.echo(f"Subagent runtime: {runtime_precheck.get('status', 'N/A') or 'N/A'}")
            typer.echo(f"Subagent delegation: {delegation_precheck.get('status', 'N/A') or 'N/A'}")
    layers = payload.get("selected_layers")
    if isinstance(layers, list):
        typer.echo(f"Layers: {', '.join(str(x) for x in layers)}")
    exhaustiveness = payload.get("exhaustiveness")
    if isinstance(exhaustiveness, dict):
        typer.echo(
            f"Exhaustiveness: score={exhaustiveness.get('score', 0)} threshold={exhaustiveness.get('threshold', 0)} status={exhaustiveness.get('status', 'N/A')}"
        )
    feature_scorecard = payload.get("feature_scorecard")
    if isinstance(feature_scorecard, dict) and feature_scorecard:
        typer.echo(f"Continue decision: {feature_scorecard.get('continue_decision', 'continue')}")
        coverage_current = feature_scorecard.get("coverage_current")
        if isinstance(coverage_current, dict):
            typer.echo(
                f"Coverage: {coverage_current.get('executed_scenarios', 0)}/{coverage_current.get('required_scenarios', 0)} ({coverage_current.get('coverage_rate', 0)})"
            )
        if str(feature_scorecard.get("continue_decision") or "") == "stop_for_repair":
            typer.echo(f"Stop reasons: {', '.join(feature_scorecard.get('stop_reasons', [])) or '-'}")
            typer.echo(f"Resume command: {feature_scorecard.get('resume_command', '')}")


@app.command(
    "import",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def import_results(ctx: typer.Context):
    """Primary alias of `beacon auto-test import-qa-use ...`."""
    code = _beacon_exec(["auto-test", "import-qa-use", *ctx.args], cwd=_repo_root())
    raise typer.Exit(code=code)


@session_app.command("save")
def session_save(
    session_id: str = typer.Argument(..., help="Session id"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    origin: str = typer.Option("", "--origin", help="Origin or base URL"),
    runner_type: str = typer.Option("agent-browser", "--runner-type", help="Runner type"),
    profile_ref: str = typer.Option("", "--profile-ref", help="Browser profile ref"),
    cookies_ref: str = typer.Option("", "--cookies-ref", help="Cookies artifact path"),
    storage_state_ref: str = typer.Option("", "--storage-state-ref", help="Storage state artifact path"),
    expires_at: str = typer.Option("", "--expires-at", help="Expiry timestamp"),
    sensitivity: str = typer.Option("internal", "--sensitivity", help="Sensitivity label"),
    scope: Optional[list[str]] = typer.Option(None, "--scope", help="Allowed scopes/origins"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Save a canonical QA session manifest."""
    project_root = Path(project) if project else Path.cwd()
    payload = {
        "origin": origin,
        "runner_type": runner_type,
        "profile_ref": profile_ref,
        "cookies_ref": cookies_ref,
        "storage_state_ref": storage_state_ref,
        "expires_at": expires_at,
        "sensitivity": sensitivity,
        "scopes": list(scope or []),
    }
    refs = write_qa_session(project_root, session_id, payload)
    current_ref = set_current_qa_session(project_root, session_id)
    result = {"session_id": session_id, **refs, **current_ref}
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ QA session saved: {session_id}")
    typer.echo(f"  Manifest: {project_root / refs['manifest']}")


@session_app.command("list")
def session_list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """List QA sessions."""
    project_root = Path(project) if project else Path.cwd()
    rows = list_qa_sessions(project_root)
    current = load_current_qa_session(project_root)
    current_id = str(current.get("session_id", "") or "")
    payload = {"current_session_id": current_id, "sessions": rows}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"QA Sessions ({len(rows)} found):")
    for row in rows:
        marker = "*" if str(row.get("session_id", "")) == current_id else "-"
        typer.echo(f"{marker} {row.get('session_id')} ({row.get('runner_type', 'unknown')} @ {row.get('origin', '-')})")


@session_app.command("use")
def session_use(
    session_id: str = typer.Argument(..., help="Session id"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Set the current QA session."""
    project_root = Path(project) if project else Path.cwd()
    payload = load_qa_session(project_root, session_id)
    if not payload:
        typer.echo(f"Session not found: {session_id}", err=True)
        raise typer.Exit(2)
    refs = set_current_qa_session(project_root, session_id)
    result = {"session_id": session_id, **refs}
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Current QA session: {session_id}")


@session_app.command("show")
def session_show(
    session_id: str = typer.Argument("", help="Session id (default current)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Show current or named QA session."""
    project_root = Path(project) if project else Path.cwd()
    target = session_id.strip() or str(load_current_qa_session(project_root).get("session_id", "") or "")
    if not target:
        typer.echo("No current QA session selected", err=True)
        raise typer.Exit(2)
    payload = load_qa_session(project_root, target)
    if not payload:
        typer.echo(f"Session not found: {target}", err=True)
        raise typer.Exit(2)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@audit_app.command("label")
def audit_label(
    run_id: str = typer.Argument(..., help="QA run id"),
    scenario_id: str = typer.Argument(..., help="Scenario id"),
    label: str = typer.Option(..., "--label", help="Audit label"),
    feature: str = typer.Option("", "--feature", help="Feature slug/name"),
    reason: str = typer.Option("", "--reason", help="Audit reason"),
    auditor: str = typer.Option("human-review", "--auditor", help="Auditor id"),
    evidence_ref: list[str] = typer.Option([], "--evidence-ref", help="Evidence ref (repeatable)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Record a machine-readable QA audit label."""
    project_root = Path(project) if project else Path.cwd()
    payload = {
        "schema_version": "1.0",
        "scenario_id": scenario_id,
        "feature_slug": feature_slug(feature) if feature else "",
        "label": label,
        "auditor": auditor,
        "reason": reason,
        "evidence_refs": [str(item) for item in evidence_ref if str(item).strip()],
    }
    path = write_qa_audit_label(project_root, run_id=run_id, scenario_id=scenario_id, payload=payload)
    calibration = refresh_qa_calibration_model(project_root)
    learning = refresh_learning_loop(project_root)
    result = {
        "status": "recorded",
        "run_id": run_id,
        "scenario_id": scenario_id,
        "audit_path": str(path.relative_to(project_root)),
        "calibration_model_path": str((project_root / ".beacon" / "state" / "qa-calibration" / "latest.json").relative_to(project_root)),
        "training_sample_count": calibration.get("training_sample_count"),
        "learning_counts": learning.get("counts", {}),
    }
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ QA audit recorded: {path}")


@audit_app.command("calibrate")
def audit_calibrate(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Recompute the QA calibration model from recorded audit labels."""
    project_root = Path(project) if project else Path.cwd()
    payload = refresh_qa_calibration_model(project_root)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("✓ QA calibration model refreshed")
    typer.echo(f"  samples: {payload.get('training_sample_count', 0)}")
