"""Beacon workflow command - Full product workflow"""
import hashlib
import json
import typer
from typing import Any, Optional
from pathlib import Path
import subprocess
import sys
import os

from beacon.utils.llm_loop import build_next_stage_trace, merge_token_usage
from beacon.utils.memory import append_memory_entry
from beacon.utils.runtime import (
    append_jsonl,
    generate_run_id,
    load_run_state,
    now_iso,
    save_run_state,
    write_json,
)
from beacon.utils.versioning import resolve_target_version
from beacon.utils.workflow_memory import (
    append_lifecycle_event,
    compute_workflow_progress,
    record_stage_writeback,
    resolve_workflow_run_id,
    write_stage_context,
)

app = typer.Typer(name="workflow", help="Full product workflow")

WORKFLOW_STAGES = [
    ("think", "Product thinking (vNext)", "beacon think start"),
    ("user-story", "Generate user stories", "beacon user-story create"),
    ("prd", "Generate PRD", "beacon prd create"),
    ("test-case", "Generate executable test matrix", "beacon test-case create"),
    ("implementation", "Align code implementation with docs", "beacon run workflow"),
    ("verify", "Run multi-layer tests and gate closure", "beacon auto-test create"),
]


def _print_next_step_selector(project_root: Path, version: str, run_id: str, feature: str) -> None:
    """Show selectable next-step prompts after workflow terminal states."""
    typer.echo("\n" + "=" * 50)
    typer.echo("NEXT STEP SELECTOR (choose one)")
    typer.echo("=" * 50)
    typer.echo("1) OMC 路径（编排/评审）")
    typer.echo(
        f'   omc run --project-root "{project_root}" '
        f'--task "继续推进 {feature}（version={version}, run_id={run_id}）"'
    )
    typer.echo("2) OMX 路径（长任务执行）")
    typer.echo(
        f'   omx run --project-root "{project_root}" '
        f'--task "执行 {feature} 的下一轮迭代（version={version}, run_id={run_id}）"'
    )
    typer.echo("3) Beacon Team 协作模式")
    typer.echo(
        f'   beacon team start "{feature} 交付协作" --project "{project_root}"'
    )
    typer.echo("（如需继续当前主流程）")
    typer.echo(
        f'   beacon workflow continue --project "{project_root}" --version "{version}" --run-id "{run_id}" --auto'
    )


def _append_llm_trace(state: dict[str, Any], trace: dict[str, Any]) -> None:
    prompts = state.get("llm_prompts")
    if not isinstance(prompts, list):
        prompts = []
    prompts.append(trace)
    state["llm_prompts"] = prompts
    state["token_usage"] = merge_token_usage(state.get("token_usage"), trace)


def _raw_command_log_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "raw-command-log.jsonl"


def _log_raw_command(
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    command: str,
    exit_code: int,
) -> None:
    append_jsonl(
        _raw_command_log_path(project_root),
        {
            "ts": now_iso(),
            "run_id": run_id,
            "stage": stage,
            "command": command,
            "exit_code": exit_code,
        },
    )


def _update_evidence_manifest(project_root: Path, evidence_refs: list[str]) -> None:
    manifest_path = project_root / ".beacon" / "evidence-manifest.json"
    payload = {}
    if manifest_path.exists():
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            payload = {}
    if not isinstance(payload, dict):
        payload = {}
    entries = payload.get("entries")
    if not isinstance(entries, list):
        entries = []
    by_path: dict[str, dict[str, Any]] = {
        str(item.get("path")): item
        for item in entries
        if isinstance(item, dict) and str(item.get("path", "")).strip()
    }
    for ref in evidence_refs:
        ref_path = str(ref or "").strip()
        if not ref_path:
            continue
        full = project_root / ref_path
        if not full.exists() or not full.is_file():
            continue
        by_path[ref_path] = {
            "path": ref_path,
            "sha256": hashlib.sha256(full.read_bytes()).hexdigest(),
            "updated_at": now_iso(),
        }
    write_json(manifest_path, {"entries": list(by_path.values()), "updated_at": now_iso()})


def _write_workflow_terminal_artifacts(
    *,
    project_root: Path,
    version: str,
    run_id: str,
    feature: str,
    workflow_status: str,
    reason: str,
) -> None:
    exec_roots = [
        project_root / "docs" / "beacon" / version / "execution",
        project_root / "docs" / "product" / version / "execution",
    ]
    status_value = "Pass" if workflow_status == "completed" else "Blocked"
    evidence_refs = [
        f".beacon/runs/{run_id}/state.json",
        ".beacon/raw-command-log.jsonl",
        ".beacon/auto-test-status.json",
    ]

    written_refs: list[str] = []
    for root in exec_roots:
        root.mkdir(parents=True, exist_ok=True)
        boundaries = root / "boundaries.md"
        terminal = root / "terminal.json"
        boundaries.write_text(
            "\n".join(
                [
                    f"# Workflow Boundaries ({version})",
                    "",
                    f"- run_id: {run_id}",
                    f"- feature: {feature}",
                    f"- workflow_status: {workflow_status}",
                    f"- reason: {reason}",
                    "- guardrail: implementation stage requires explicit command execution",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        terminal_payload = {
            "schema_version": "1.0",
            "version": version,
            "run_id": run_id,
            "feature": feature,
            "status": status_value,
            "reason": reason,
            "traceability": {
                "evidence_refs": evidence_refs,
            },
            "generated_at": now_iso(),
        }
        write_json(terminal, terminal_payload)
        written_refs.extend(
            [
                str(boundaries.relative_to(project_root)),
                str(terminal.relative_to(project_root)),
            ]
        )

    gate_status = "Pass" if status_value == "Pass" else "Blocked"
    gate_issues: list[dict[str, Any]] = []
    if gate_status == "Blocked":
        gate_issues.append(
            {
                "reason_code": reason or "workflow_blocked",
                "message": f"Workflow blocked: {reason or 'unknown'}",
                "blocked": True,
            }
        )
    write_json(
        project_root / ".beacon" / "gate-report.json",
        {
            "stage": "release",
            "mode": "strict",
            "status": gate_status,
            "issues": gate_issues,
            "updated_at": now_iso(),
        },
    )
    _update_evidence_manifest(project_root, written_refs + [".beacon/gate-report.json"])

    release_evidence_refs = sorted(
        set(
            written_refs
            + [
                ".beacon/gate-report.json",
                f".beacon/runs/{run_id}/state.json",
                ".beacon/raw-command-log.jsonl",
                ".beacon/auto-test-status.json",
            ]
        )
    )
    append_memory_entry(
        project_root=project_root,
        mem_type="decision",
        text=f"[workflow.release-profile] run={run_id} status={workflow_status} reason={reason}",
        source_session_id=run_id,
        source="workflow.release-profile",
        evidence_ref=release_evidence_refs,
        confidence=0.82,
        tags=["release", "workflow-loop", workflow_status],
    )
    append_lifecycle_event(
        project_root,
        run_id=f"release:{version}",
        stage="release",
        event="release_decision_recorded",
        source="workflow.release-profile",
        evidence_ref=release_evidence_refs,
        details={
            "workflow_run_id": run_id,
            "feature": feature,
            "version": version,
            "status": workflow_status,
            "reason": reason,
        },
    )


def _sync_terminal_manifest(project_root: Path, *, version: str, run_id: str) -> None:
    refs = [
        f".beacon/runs/{run_id}/state.json",
        ".beacon/raw-command-log.jsonl",
        ".beacon/auto-test-status.json",
        ".beacon/gate-report.json",
    ]
    for root in (
        project_root / "docs" / "beacon" / version / "execution",
        project_root / "docs" / "product" / version / "execution",
    ):
        for name in ("boundaries.md", "terminal.json", "summary.json", "summary.md"):
            path = root / name
            if path.exists():
                refs.append(str(path.relative_to(project_root)))
    _update_evidence_manifest(project_root, refs)


def run_beacon_command(
    args: list,
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    extra_env: Optional[dict[str, str]] = None,
) -> subprocess.CompletedProcess[str]:
    """Run a beacon subcommand"""
    cmd = [sys.executable, "-m", "beacon.main"] + args
    env = os.environ.copy()
    env.update(extra_env or {})
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True,
        env=env,
    )
    _log_raw_command(
        project_root,
        run_id=run_id,
        stage=stage,
        command=" ".join(cmd),
        exit_code=int(result.returncode),
    )
    return result


def ensure_output_dirs(project_root: Path, version: str = "v1.0.0"):
    """Ensure output directories exist - supports both docs/beacon and docs/product"""
    dirs = [
        # Beacon primary directories
        project_root / "docs" / "beacon" / version / "user-story",
        project_root / "docs" / "beacon" / version / "prd",
        project_root / "docs" / "beacon" / version / "qa" / "test-cases",
        # PTK compatibility directories
        project_root / "docs" / "product" / version / "user-story",
        project_root / "docs" / "product" / version / "prd",
        project_root / "docs" / "product" / version / "qa" / "test-cases",
        # State directory
        project_root / ".beacon" / "state",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def _slug(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "-")


def _stage_output_candidates(project_root: Path, stage: str, feature: str, version: str) -> list[Path]:
    slug = _slug(feature)
    common = [project_root / ".beacon" / "raw-command-log.jsonl"]
    if stage == "think":
        return [
            project_root / ".beacon" / "state" / "think-progress" / f"{version}.json",
            project_root / ".beacon" / "state" / "think-progress.json",
        ] + common
    if stage == "user-story":
        return [
            project_root / "docs" / "product" / version / "user-story" / f"{slug}.md",
            project_root / "docs" / "beacon" / version / "user-story" / f"{slug}.md",
        ] + common
    if stage == "prd":
        return [
            project_root / "docs" / "product" / version / "prd" / f"{slug}.md",
            project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md",
        ] + common
    if stage == "test-case":
        return [
            project_root / "docs" / "product" / version / "qa" / "test-cases" / f"{slug}.md",
            project_root / "docs" / "beacon" / version / "qa" / "test-cases" / f"{slug}.md",
            project_root / "docs" / "product" / version / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json",
            project_root / "docs" / "beacon" / version / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json",
            project_root / "docs" / "product" / version / "qa" / "test-cases" / f"{slug}.qa9-matrix.json",
            project_root / "docs" / "beacon" / version / "qa" / "test-cases" / f"{slug}.qa9-matrix.json",
        ] + common
    if stage == "implementation":
        return [
            project_root / ".beacon" / "state" / f"implementation-{slug}.json",
        ] + common
    if stage == "verify":
        return [
            project_root / ".beacon" / "auto-test-status.json",
        ] + common
    return common


def _matrix_path_candidates(project_root: Path, feature: str, version: str) -> list[Path]:
    slug = _slug(feature)
    return [
        project_root / "docs" / "product" / version / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json",
        project_root / "docs" / "beacon" / version / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json",
    ]


def _qa9_matrix_path_candidates(project_root: Path, feature: str, version: str) -> list[Path]:
    slug = _slug(feature)
    return [
        project_root / "docs" / "product" / version / "qa" / "test-cases" / f"{slug}.qa9-matrix.json",
        project_root / "docs" / "beacon" / version / "qa" / "test-cases" / f"{slug}.qa9-matrix.json",
    ]


def _append_run_event(state: dict[str, Any], event: str, **details: Any) -> None:
    events = state.get("events")
    if not isinstance(events, list):
        events = []
    payload = {"event": event, "ts": now_iso()}
    payload.update(details)
    events.append(payload)
    state["events"] = events


def _execute_stage(
    *,
    project_root: Path,
    run_id: str,
    stage: str,
    feature: str,
    version: str,
    implementation_command: Optional[str],
    verify_scope: str,
    verify_config: Optional[str],
    verify_ui_command: Optional[str],
    verify_api_curl_command: Optional[str],
    verify_unit_command: Optional[str],
    verify_smoke_command: Optional[str],
    verify_require_ui_actions: bool,
    verify_qa_profile: str,
    verify_qa_types: Optional[list[str]],
    verify_qa_matrix_path: Optional[str],
    verify_ui_runner: str,
    verify_compat_browsers: Optional[str],
    verify_compat_devices: Optional[str],
    verify_require_fresh_evidence: bool,
) -> int:
    """Execute one workflow stage and write lifecycle events."""
    failure_details: dict[str, Any] = {}
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage=stage,
        event="stage_started",
        source="workflow.start",
        details={"feature": feature, "version": version},
    )
    context_path = write_stage_context(
        project_root,
        run_id=run_id,
        stage=stage,
        feature=feature,
    )
    stage_env = {
        "BEACON_WORKFLOW_RUN_ID": run_id,
        "BEACON_WORKFLOW_STAGE": stage,
        "BEACON_STAGE_CONTEXT_PATH": str(context_path),
    }

    if stage == "think":
        result = run_beacon_command(
            ["think", "start", feature, "--project", str(project_root), "--version", version],
            project_root,
            run_id=run_id,
            stage=stage,
            extra_env=stage_env,
        )
        rc = int(result.returncode)
    elif stage == "user-story":
        result = run_beacon_command(
            ["user-story", "create", feature, "--project", str(project_root), "--version", version],
            project_root,
            run_id=run_id,
            stage=stage,
            extra_env=stage_env,
        )
        rc = int(result.returncode)
    elif stage == "prd":
        result = run_beacon_command(
            ["prd", "create", feature, "--project", str(project_root), "--version", version],
            project_root,
            run_id=run_id,
            stage=stage,
            extra_env=stage_env,
        )
        rc = int(result.returncode)
    elif stage == "test-case":
        result = run_beacon_command(
            ["test-case", "create", feature, "--project", str(project_root), "--version", version],
            project_root,
            run_id=run_id,
            stage=stage,
            extra_env=stage_env,
        )
        rc = int(result.returncode)
    elif stage == "implementation":
        resolved_implementation_command = str(implementation_command or "").strip()
        command_source = "cli"
        if not resolved_implementation_command:
            env_command = str(os.environ.get("BEACON_IMPLEMENTATION_COMMAND", "")).strip()
            if env_command:
                resolved_implementation_command = env_command
                command_source = "env"
        if not resolved_implementation_command:
            # Keep workflow one-command runnable for runbook/newcomers.
            resolved_implementation_command = (
                "python3 -c \"print('BEACON_IMPLEMENTATION_NOOP=1')\""
            )
            command_source = "builtin-noop"

        env = os.environ.copy()
        env.update(stage_env)
        shell_result = subprocess.run(
            resolved_implementation_command,
            cwd=project_root,
            shell=True,
            text=True,
            env=env,
        )
        rc = shell_result.returncode
        _log_raw_command(
            project_root,
            run_id=run_id,
            stage=stage,
            command=resolved_implementation_command,
            exit_code=rc,
        )
        if rc == 0:
            marker = project_root / ".beacon" / "state" / f"implementation-{_slug(feature)}.json"
            write_json(
                marker,
                {
                    "schema_version": "1.0",
                    "run_id": run_id,
                    "stage": "implementation",
                    "feature": feature,
                    "version": version,
                    "command": resolved_implementation_command,
                    "command_source": command_source,
                    "status": "completed",
                    "generated_at": now_iso(),
                },
            )
    elif stage == "verify":
        verify_scope_norm = (verify_scope or "all").strip().lower()
        require_ui_actions_effective = verify_require_ui_actions and verify_scope_norm in {
            "ui",
            "all",
            "functional",
            "qa9",
        }
        verify_args = [
            "auto-test",
            "create",
            verify_scope,
            "--project",
            str(project_root),
        ]
        if verify_config:
            verify_args.extend(["--config", verify_config])
        if verify_ui_command:
            verify_args.extend(["--ui-command", verify_ui_command])
        if verify_api_curl_command:
            verify_args.extend(["--api-curl-command", verify_api_curl_command])
        if verify_unit_command:
            verify_args.extend(["--unit-command", verify_unit_command])
        if verify_smoke_command:
            verify_args.extend(["--smoke-command", verify_smoke_command])
        if verify_scope_norm == "qa9":
            verify_args.extend(["--qa-profile", verify_qa_profile])
            if verify_qa_types:
                for item in verify_qa_types:
                    verify_args.extend(["--qa-types", item])
            if verify_ui_runner:
                verify_args.extend(["--ui-runner", verify_ui_runner])
            if verify_compat_browsers:
                verify_args.extend(["--compat-browsers", verify_compat_browsers])
            if verify_compat_devices:
                verify_args.extend(["--compat-devices", verify_compat_devices])
            if verify_require_fresh_evidence:
                verify_args.append("--require-fresh-evidence")
        if require_ui_actions_effective:
            verify_args.append("--require-ui-actions")
        if verify_qa_matrix_path and verify_scope_norm == "qa9":
            verify_args.extend(["--qa-matrix-path", verify_qa_matrix_path])
        else:
            if verify_scope_norm == "qa9":
                for matrix_path in _qa9_matrix_path_candidates(project_root, feature, version):
                    if matrix_path.exists():
                        verify_args.extend(["--qa-matrix-path", str(matrix_path)])
                        break
            for matrix_path in _matrix_path_candidates(project_root, feature, version):
                if matrix_path.exists():
                    verify_args.extend(["--matrix-path", str(matrix_path)])
                    break
        result = run_beacon_command(
            verify_args,
            project_root,
            run_id=run_id,
            stage=stage,
            extra_env=stage_env,
        )
        rc = int(result.returncode)
        # Verify stage hard condition: auto-test artifact must be passed.
        if rc == 0:
            verify_artifact = project_root / ".beacon" / "auto-test-status.json"
            if not verify_artifact.exists():
                rc = 1
                failure_details = {
                    "exit_code": 1,
                    "verify_status": "missing_artifact",
                    "reason": "verify_status_artifact_missing",
                }
            else:
                try:
                    verify_payload = json.loads(verify_artifact.read_text(encoding="utf-8"))
                except Exception:  # noqa: BLE001
                    verify_payload = {}
                verify_status = str(verify_payload.get("status", "")).lower()
                if verify_status != "passed":
                    rc = 1
                    failure_details = {
                        "exit_code": 1,
                        "verify_status": verify_status or "unknown",
                        "reason": "verify_not_passed",
                    }
    else:
        rc = 1

    if rc == 0:
        evidence = [
            str(path.relative_to(project_root))
            for path in _stage_output_candidates(project_root, stage, feature, version)
            if path.exists()
        ]
        _update_evidence_manifest(project_root, evidence)
        append_lifecycle_event(
            project_root,
            run_id=run_id,
            stage=stage,
            event="stage_finished",
            source="workflow.start",
            evidence_ref=evidence,
            details={"exit_code": rc},
        )
        record_stage_writeback(
            project_root,
            run_id=run_id,
            stage=stage,
            feature=feature,
            evidence_ref=evidence,
            status="completed",
        )
    else:
        append_lifecycle_event(
            project_root,
            run_id=run_id,
            stage=stage,
            event="stage_failed",
            source="workflow.start",
            details=failure_details or {"exit_code": rc},
        )
    return rc


@app.command()
def start(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    auto: bool = typer.Option(False, "--auto", "-a", help="Auto-run all stages"),
    skip: Optional[str] = typer.Option(None, "--skip", "-s", help="Skip stages (e.g., think,user-story)"),
    implementation_command: Optional[str] = typer.Option(
        None,
        "--implementation-command",
        help="Implementation stage command override",
    ),
    verify_scope: str = typer.Option("all", "--verify-scope", help="Verify scope: ui/api-curl/unit/smoke/all/qa9"),
    verify_config: Optional[str] = typer.Option(None, "--verify-config", help="Verify config path"),
    verify_ui_command: Optional[str] = typer.Option(None, "--verify-ui-command", help="Verify UI command"),
    verify_api_curl_command: Optional[str] = typer.Option(None, "--verify-api-curl-command", help="Verify API curl command"),
    verify_unit_command: Optional[str] = typer.Option(None, "--verify-unit-command", help="Verify unit command"),
    verify_smoke_command: Optional[str] = typer.Option(None, "--verify-smoke-command", help="Verify smoke command"),
    verify_require_ui_actions: bool = typer.Option(
        False,
        "--verify-require-ui-actions/--no-verify-require-ui-actions",
        help="Require key UI action evidence in verify stage.",
    ),
    verify_qa_profile: str = typer.Option(
        "web-full",
        "--verify-qa-profile",
        help="Verify QA profile for qa9 scope: web-core/web-full/custom",
    ),
    verify_qa_types: Optional[list[str]] = typer.Option(
        None,
        "--verify-qa-types",
        help="Verify QA types for qa9 scope (comma-separated or repeatable).",
    ),
    verify_qa_matrix_path: Optional[str] = typer.Option(
        None,
        "--verify-qa-matrix-path",
        help="Verify QA9 matrix path (*.qa9-matrix.json).",
    ),
    verify_ui_runner: str = typer.Option(
        "playwright",
        "--verify-ui-runner",
        help="Verify UI runner for qa9: playwright/cypress/browser-use/agent-browser/midscene",
    ),
    verify_compat_browsers: Optional[str] = typer.Option(
        None,
        "--verify-compat-browsers",
        help="Verify compatibility browsers list (comma-separated).",
    ),
    verify_compat_devices: Optional[str] = typer.Option(
        None,
        "--verify-compat-devices",
        help="Verify compatibility devices list (comma-separated).",
    ),
    verify_require_fresh_evidence: bool = typer.Option(
        False,
        "--verify-require-fresh-evidence/--no-verify-require-fresh-evidence",
        help="Verify stage requires current run fresh evidence for matrix artifacts.",
    ),
):
    """Start full product workflow"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)

    # Ensure directories exist
    ensure_output_dirs(project_root, resolved_version)
    run_id = generate_run_id(project_root)
    started_at = now_iso()
    skip_stages = {x.strip() for x in (skip.split(",") if skip else []) if x.strip()}
    predicted = build_next_stage_trace(
        feature=feature,
        version=resolved_version,
        run_id=run_id,
        next_stage="think",
        context="workflow.start",
    )
    base_state: dict[str, Any] = {
        "run_id": run_id,
        "workflow": "workflow.start",
        "mode": "auto" if auto else "manual",
        "feature": feature,
        "version": resolved_version,
        "status": "running" if auto else "planned",
        "started_at": started_at,
        "events": [{"event": "workflow_started", "ts": started_at}],
        "llm_prompts": [predicted],
        "token_usage": merge_token_usage({}, predicted),
        "tool_calls": [{"name": "workflow.next_stage.predict", "args": {"next_stage": "think"}}],
    }
    save_run_state(
        project_root,
        run_id,
        base_state,
    )

    typer.echo(f"Starting Beacon Workflow: {feature}")
    typer.echo(f"Project: {project_root}")
    typer.echo(f"Version: {resolved_version}")
    typer.echo(f"Run ID: {run_id}")
    typer.echo("\n" + "=" * 50)
    typer.echo("WORKFLOW STAGES")
    typer.echo("=" * 50)

    for i, (stage, desc, cmd) in enumerate(WORKFLOW_STAGES, 1):
        if stage in skip_stages:
            typer.echo(f"{i}. {stage:12} - {desc} [SKIPPED]")
            continue

        if auto:
            typer.echo(f"{i}. {stage:12} - {desc}")
            typer.echo(f"    → Running: {cmd} {feature}")
            rc = _execute_stage(
                project_root=project_root,
                run_id=run_id,
                stage=stage,
                feature=feature,
                version=resolved_version,
                implementation_command=implementation_command,
                verify_scope=verify_scope,
                verify_config=verify_config,
                verify_ui_command=verify_ui_command,
                verify_api_curl_command=verify_api_curl_command,
                verify_unit_command=verify_unit_command,
                verify_smoke_command=verify_smoke_command,
                verify_require_ui_actions=verify_require_ui_actions,
                verify_qa_profile=verify_qa_profile,
                verify_qa_types=verify_qa_types,
                verify_qa_matrix_path=verify_qa_matrix_path,
                verify_ui_runner=verify_ui_runner,
                verify_compat_browsers=verify_compat_browsers,
                verify_compat_devices=verify_compat_devices,
                verify_require_fresh_evidence=verify_require_fresh_evidence,
            )
            if rc == 0:
                typer.echo(f"    ✓ {stage} completed")
            else:
                typer.echo(f"    ✗ {stage} failed (exit={rc})")
                blocked = dict(base_state)
                blocked["status"] = "blocked"
                blocked["reason"] = f"{stage}_failed"
                blocked["ended_at"] = now_iso()
                _append_run_event(blocked, "workflow_blocked", stage=stage, exit_code=rc)
                _write_workflow_terminal_artifacts(
                    project_root=project_root,
                    version=resolved_version,
                    run_id=run_id,
                    feature=feature,
                    workflow_status="blocked",
                    reason=f"{stage}_failed",
                )
                save_run_state(project_root, run_id, blocked)
                _sync_terminal_manifest(project_root, version=resolved_version, run_id=run_id)
                _print_next_step_selector(project_root=project_root, version=resolved_version, run_id=run_id, feature=feature)
                raise typer.Exit(rc)
        else:
            typer.echo(f"{i}. {stage:12} - {desc} [PENDING]")

    if auto:
        typer.echo("\n" + "=" * 50)
        typer.echo("WORKFLOW COMPLETE")
        typer.echo("=" * 50)
        completed = dict(base_state)
        completed["status"] = "completed"
        completed["reason"] = "ok"
        completed["ended_at"] = now_iso()
        _append_run_event(completed, "workflow_completed")
        _write_workflow_terminal_artifacts(
            project_root=project_root,
            version=resolved_version,
            run_id=run_id,
            feature=feature,
            workflow_status="completed",
            reason="ok",
        )
        save_run_state(project_root, run_id, completed)
        _sync_terminal_manifest(project_root, version=resolved_version, run_id=run_id)
        _print_next_step_selector(project_root=project_root, version=resolved_version, run_id=run_id, feature=feature)
    else:
        append_lifecycle_event(
            project_root,
            run_id=run_id,
            stage="workflow",
            event="workflow_planned",
            source="workflow.start",
            details={"feature": feature, "version": resolved_version, "skip_stages": sorted(skip_stages)},
        )
        planned = dict(base_state)
        planned["status"] = "planned"
        planned["reason"] = "awaiting_continue"
        _append_run_event(planned, "workflow_planned")
        save_run_state(project_root, run_id, planned)
        typer.echo("\nWorkflow planned (manual mode).")
        typer.echo("Run next step:")
        typer.echo(
            f"  beacon workflow continue --project {project_root} --version {resolved_version} --run-id {run_id}"
        )
        _print_next_step_selector(project_root=project_root, version=resolved_version, run_id=run_id, feature=feature)


@app.command("continue")
def continue_workflow(  # noqa: A003
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    feature: Optional[str] = typer.Option(None, "--feature", "-f", help="Feature filter"),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Explicit run id"),
    auto: bool = typer.Option(False, "--auto", "-a", help="Continue until verify"),
    implementation_command: Optional[str] = typer.Option(
        None,
        "--implementation-command",
        help="Implementation stage command override",
    ),
    verify_scope: str = typer.Option("all", "--verify-scope", help="Verify scope: ui/api-curl/unit/smoke/all/qa9"),
    verify_config: Optional[str] = typer.Option(None, "--verify-config", help="Verify config path"),
    verify_ui_command: Optional[str] = typer.Option(None, "--verify-ui-command", help="Verify UI command"),
    verify_api_curl_command: Optional[str] = typer.Option(None, "--verify-api-curl-command", help="Verify API curl command"),
    verify_unit_command: Optional[str] = typer.Option(None, "--verify-unit-command", help="Verify unit command"),
    verify_smoke_command: Optional[str] = typer.Option(None, "--verify-smoke-command", help="Verify smoke command"),
    verify_require_ui_actions: bool = typer.Option(
        False,
        "--verify-require-ui-actions/--no-verify-require-ui-actions",
        help="Require key UI action evidence in verify stage.",
    ),
    verify_qa_profile: str = typer.Option(
        "web-full",
        "--verify-qa-profile",
        help="Verify QA profile for qa9 scope: web-core/web-full/custom",
    ),
    verify_qa_types: Optional[list[str]] = typer.Option(
        None,
        "--verify-qa-types",
        help="Verify QA types for qa9 scope (comma-separated or repeatable).",
    ),
    verify_qa_matrix_path: Optional[str] = typer.Option(
        None,
        "--verify-qa-matrix-path",
        help="Verify QA9 matrix path (*.qa9-matrix.json).",
    ),
    verify_ui_runner: str = typer.Option(
        "playwright",
        "--verify-ui-runner",
        help="Verify UI runner for qa9: playwright/cypress/browser-use/agent-browser/midscene",
    ),
    verify_compat_browsers: Optional[str] = typer.Option(
        None,
        "--verify-compat-browsers",
        help="Verify compatibility browsers list (comma-separated).",
    ),
    verify_compat_devices: Optional[str] = typer.Option(
        None,
        "--verify-compat-devices",
        help="Verify compatibility devices list (comma-separated).",
    ),
    verify_require_fresh_evidence: bool = typer.Option(
        False,
        "--verify-require-fresh-evidence/--no-verify-require-fresh-evidence",
        help="Verify stage requires current run fresh evidence for matrix artifacts.",
    ),
):
    """Continue workflow from memory lifecycle progress and execute next stage(s)."""
    project_root = Path(project) if project else Path.cwd()
    version_raw = (version or "").strip().lower()
    version_filter = None if version_raw in {"", "auto", "latest"} else resolve_target_version(project_root, version)
    resolved_run_id = resolve_workflow_run_id(
        project_root,
        run_id=run_id,
        version=version_filter,
        feature=feature,
    )
    if not resolved_run_id:
        typer.echo("✗ No workflow run found for the given filters")
        raise typer.Exit(2)

    state = load_run_state(project_root, resolved_run_id) or {}
    run_feature = str(state.get("feature", "") or feature or "").strip()
    run_version = str(state.get("version", "") or resolve_target_version(project_root, version)).strip()
    if not run_feature:
        typer.echo("✗ Workflow run is missing feature metadata")
        raise typer.Exit(2)

    progress = compute_workflow_progress(project_root, run_id=resolved_run_id)
    if progress.get("closure_complete"):
        typer.echo(f"✓ Workflow already complete: {resolved_run_id}")
        return

    next_stage = str(progress.get("next_stage") or "")
    if not next_stage:
        typer.echo("✗ Cannot resolve next stage from memory progress")
        raise typer.Exit(2)
    trace = build_next_stage_trace(
        feature=run_feature,
        version=run_version,
        run_id=resolved_run_id,
        next_stage=next_stage,
        context="workflow.continue",
    )

    stage_order = [name for name, _, _ in WORKFLOW_STAGES]
    start_idx = stage_order.index(next_stage) if next_stage in stage_order else 0
    if auto:
        stage_sequence = stage_order[start_idx:]
    else:
        stage_sequence = [next_stage]

    typer.echo(f"Continuing workflow run: {resolved_run_id}")
    typer.echo(f"Feature: {run_feature}")
    typer.echo(f"Version: {run_version}")
    typer.echo(f"Next stage: {next_stage}")
    typer.echo(f"Mode: {'auto' if auto else 'single-step'}")

    working_state = dict(state)
    working_state["status"] = "running"
    working_state.setdefault("started_at", now_iso())
    _append_llm_trace(working_state, trace)
    _append_run_event(working_state, "workflow_continue_started", next_stage=next_stage, auto=auto)
    save_run_state(project_root, resolved_run_id, working_state)

    for stage in stage_sequence:
        stage_progress = compute_workflow_progress(project_root, run_id=resolved_run_id)
        stage_data = stage_progress.get("stages", {}).get(stage, {})
        if str(stage_data.get("status", "")) == "completed":
            typer.echo(f"    · {stage} already completed, skip")
            continue
        typer.echo(f"    → Running stage: {stage}")
        rc = _execute_stage(
            project_root=project_root,
            run_id=resolved_run_id,
            stage=stage,
            feature=run_feature,
            version=run_version,
            implementation_command=implementation_command,
            verify_scope=verify_scope,
            verify_config=verify_config,
            verify_ui_command=verify_ui_command,
            verify_api_curl_command=verify_api_curl_command,
            verify_unit_command=verify_unit_command,
            verify_smoke_command=verify_smoke_command,
            verify_require_ui_actions=verify_require_ui_actions,
            verify_qa_profile=verify_qa_profile,
            verify_qa_types=verify_qa_types,
            verify_qa_matrix_path=verify_qa_matrix_path,
            verify_ui_runner=verify_ui_runner,
            verify_compat_browsers=verify_compat_browsers,
            verify_compat_devices=verify_compat_devices,
            verify_require_fresh_evidence=verify_require_fresh_evidence,
        )
        if rc != 0:
            blocked = load_run_state(project_root, resolved_run_id) or working_state
            blocked["status"] = "blocked"
            blocked["reason"] = f"{stage}_failed"
            blocked["ended_at"] = now_iso()
            _append_run_event(blocked, "workflow_continue_blocked", stage=stage, exit_code=rc)
            _write_workflow_terminal_artifacts(
                project_root=project_root,
                version=run_version,
                run_id=resolved_run_id,
                feature=run_feature,
                workflow_status="blocked",
                reason=f"{stage}_failed",
            )
            save_run_state(project_root, resolved_run_id, blocked)
            _sync_terminal_manifest(project_root, version=run_version, run_id=resolved_run_id)
            typer.echo(f"    ✗ {stage} failed (exit={rc})")
            _print_next_step_selector(
                project_root=project_root,
                version=run_version,
                run_id=resolved_run_id,
                feature=run_feature,
            )
            raise typer.Exit(rc)
        typer.echo(f"    ✓ {stage} completed")

        refreshed = compute_workflow_progress(project_root, run_id=resolved_run_id)
        if not auto:
            missing = refreshed.get("missing_closure_stages", [])
            current = load_run_state(project_root, resolved_run_id) or working_state
            current["status"] = "running" if missing else "completed"
            current["reason"] = "partial_progress" if missing else "ok"
            if not missing:
                current["ended_at"] = now_iso()
            _append_run_event(current, "workflow_continue_step_done", stage=stage, missing_stages=missing)
            save_run_state(project_root, resolved_run_id, current)
            return

    final_progress = compute_workflow_progress(project_root, run_id=resolved_run_id)
    final_state = load_run_state(project_root, resolved_run_id) or working_state
    if final_progress.get("closure_complete"):
        final_state["status"] = "completed"
        final_state["reason"] = "ok"
        final_state["ended_at"] = now_iso()
        _append_run_event(final_state, "workflow_continue_completed")
        _write_workflow_terminal_artifacts(
            project_root=project_root,
            version=run_version,
            run_id=resolved_run_id,
            feature=run_feature,
            workflow_status="completed",
            reason="ok",
        )
        _sync_terminal_manifest(project_root, version=run_version, run_id=resolved_run_id)
        typer.echo("✓ Workflow closure complete")
        _print_next_step_selector(
            project_root=project_root,
            version=run_version,
            run_id=resolved_run_id,
            feature=run_feature,
        )
    else:
        final_state["status"] = "running"
        final_state["reason"] = "partial_progress"
        _append_run_event(
            final_state,
            "workflow_continue_partial",
            missing_stages=final_progress.get("missing_closure_stages", []),
        )
        typer.echo(
            "○ Workflow partially continued; missing stages: "
            f"{final_progress.get('missing_closure_stages', [])}"
        )
    save_run_state(project_root, resolved_run_id, final_state)


@app.command()
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    feature: Optional[str] = typer.Option(None, "--feature", "-f", help="Feature filter"),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Explicit run id"),
):
    """Show workflow status"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)

    typer.echo("Beacon Workflow Status")
    typer.echo("=" * 40)

    # Check docs/beacon first, fallback to docs/product
    beacon_dir = project_root / "docs" / "beacon" / resolved_version
    product_dir = project_root / "docs" / "product" / resolved_version

    # Determine which docs dir to use
    beacon_has_docs = beacon_dir.exists() and any(beacon_dir.rglob("*.md"))
    product_has_docs = product_dir.exists() and any(product_dir.rglob("*.md"))
    if beacon_has_docs:
        docs_dir = beacon_dir
        docs_type = "beacon"
    elif product_has_docs:
        docs_dir = product_dir
        docs_type = "product"
    elif beacon_dir.exists():
        docs_dir = beacon_dir
        docs_type = "beacon"
    else:
        docs_dir = beacon_dir  # Use beacon as default
        docs_type = "beacon"

    typer.echo(f"Using: docs/{docs_type}/{resolved_version}")

    # Check each stage
    stages = [
        ("think", ".beacon/state/think-progress.json"),
        ("user-story", "user-story"),
        ("prd", "prd"),
        ("test-case", "qa/test-cases"),
        ("implementation", ".beacon/state"),
        ("verify", ".beacon/auto-test-status.json"),
    ]

    for stage, path in stages:
        if stage == "think":
            candidates = [
                project_root / ".beacon" / "state" / "think-progress" / f"{resolved_version}.json",
                project_root / ".beacon" / "state" / "think-progress.json",
            ]
            stage_path = next((p for p in candidates if p.exists()), candidates[-1])
        else:
            stage_path = docs_dir / path
        if stage in {"implementation", "verify"}:
            stage_path = project_root / path
        if stage_path.exists():
            if stage_path.is_file():
                typer.echo(f"✓ {stage}: Completed")
            elif stage_path.is_dir():
                files = list(stage_path.glob("*.md")) + list(stage_path.glob("*/state.json"))
                if stage == "implementation":
                    files.extend(list(stage_path.glob("implementation-*.json")))
                if files:
                    typer.echo(f"✓ {stage}: Completed ({len(files)} files)")
                else:
                    typer.echo(f"○ {stage}: Started (empty)")
            else:
                typer.echo(f"○ {stage}: Not started")
        else:
            typer.echo(f"○ {stage}: Not started")

    typer.echo("\nMemory Lifecycle Progress")
    typer.echo("-" * 40)
    progress = compute_workflow_progress(
        project_root,
        run_id=run_id,
        version=resolved_version,
        feature=feature,
    )
    resolved = progress.get("run_id")
    typer.echo(f"run_id: {resolved or 'N/A'}")
    if progress.get("feature"):
        typer.echo(f"feature: {progress.get('feature')}")
    if progress.get("version"):
        typer.echo(f"version: {progress.get('version')}")
    for stage in ("think", "user-story", "prd", "test-case", "implementation", "verify"):
        item = progress.get("stages", {}).get(stage, {})
        typer.echo(f"{stage:12}: {item.get('status', 'not_started')}")
    typer.echo(f"next_stage   : {progress.get('next_stage') or 'none'}")
    typer.echo(f"closure_complete: {bool(progress.get('closure_complete'))}")
    typer.echo(f"missing_stages : {progress.get('missing_closure_stages', [])}")


@app.command()
def gate(
    stage: Optional[str] = typer.Argument(
        None,
        help="Stage to check (think/user-story/prd/test-case/implementation/verify/release)",
    ),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Run gate checks for stages"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)

    stages = (
        ["think", "user-story", "prd", "test-case", "release"]
        if not stage
        else [stage]
    )

    typer.echo("Beacon Gate Check")
    typer.echo("=" * 50)

    # Check docs/beacon first, fallback to docs/product
    beacon_dir = project_root / "docs" / "beacon" / resolved_version
    product_dir = project_root / "docs" / "product" / resolved_version

    if beacon_dir.exists():
        docs_dir = beacon_dir
        docs_type = "beacon"
    elif product_dir.exists():
        docs_dir = product_dir
        docs_type = "product"
    else:
        docs_dir = beacon_dir  # Use beacon as default
        docs_type = "beacon"

    typer.echo(f"Checking: docs/{docs_type}/{resolved_version}")

    all_passed = True

    for s in stages:
        typer.echo(f"\n--- {s.upper()} Gate ---")

        if s == "think":
            # Check think progress
            state_file = project_root / ".beacon" / "state" / "think-progress" / f"{resolved_version}.json"
            legacy_state_file = project_root / ".beacon" / "state" / "think-progress.json"
            if state_file.exists() or legacy_state_file.exists():
                typer.echo("✓ PASS: Think session exists")
            else:
                typer.echo("✗ FAIL: No think session found")
                all_passed = False

        elif s == "user-story":
            us_dir = docs_dir / "user-story"
            if us_dir.exists() and list(us_dir.glob("*.md")):
                typer.echo("✓ PASS: User stories exist")
            else:
                typer.echo("✗ FAIL: No user stories found")
                all_passed = False

        elif s == "prd":
            prd_dir = docs_dir / "prd"
            if prd_dir.exists() and list(prd_dir.glob("*.md")):
                typer.echo("✓ PASS: PRD exists")
            else:
                typer.echo("✗ FAIL: No PRD found")
                all_passed = False

        elif s == "test-case":
            tc_dir = docs_dir / "qa" / "test-cases"
            if tc_dir.exists() and list(tc_dir.glob("*.md")):
                typer.echo("✓ PASS: Test cases exist")
            else:
                typer.echo("✗ FAIL: No test cases found")
                all_passed = False

        elif s == "implementation":
            marker_dir = project_root / ".beacon" / "state"
            has_marker = marker_dir.exists() and any(marker_dir.glob("implementation-*.json"))
            if has_marker:
                typer.echo("✓ PASS: Implementation run artifacts exist")
            else:
                typer.echo("✗ FAIL: No implementation run artifacts found")
                all_passed = False

        elif s == "verify":
            verify_file = project_root / ".beacon" / "auto-test-status.json"
            if not verify_file.exists():
                typer.echo("✗ FAIL: No verify artifact found (.beacon/auto-test-status.json)")
                all_passed = False
            else:
                data = {}
                try:
                    import json as _json

                    data = _json.loads(verify_file.read_text(encoding="utf-8"))
                except Exception:
                    data = {}
                status_value = str(data.get("status", "")).lower()
                if status_value == "passed":
                    typer.echo("✓ PASS: Verify tests passed")
                else:
                    typer.echo(f"✗ FAIL: Verify status is {status_value or 'unknown'}")
                    all_passed = False

        elif s == "release":
            typer.echo("⚠ WARN: Release gate requires smoke tests")
            typer.echo("Run: beacon auto-test create smoke")

    typer.echo("\n" + "=" * 50)
    if all_passed:
        typer.echo("GATE RESULT: PASS")
    else:
        typer.echo("GATE RESULT: FAIL")


@app.command()
def run(
    command: str = typer.Argument(..., help="Command to run (think/user-story/prd/test-case/analyze/brainstorm/etc)"),
    feature: Optional[str] = typer.Argument(None, help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    options: Optional[str] = typer.Option(None, "--options", "-o", help="Additional options as JSON string"),
):
    """Run any beacon subcommand from workflow"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)

    # Map command names to actual commands
    command_map = {
        "think": "think",
        "user-story": "user-story",
        "user_story": "user-story",
        "prd": "prd",
        "test-case": "test-case",
        "test_case": "test-case",
        "analyze": "analyze",
        "brainstorm": "brainstorm",
        "design": "design",
        "jtbd": "jtbd",
        "kano": "kano",
        "moscow": "moscow",
        "roadmap": "roadmap",
        "persona": "persona",
        "version": "version",
        "doctor": "doctor",
        "status": "status",
        "report": "report",
        "debug": "debug",
        "auto-test": "auto-test",
        "auto_test": "auto-test",
        "release": "release",
        "api-design": "api-design",
        "api_design": "api-design",
        "data-dictionary": "data-dictionary",
        "data_dictionary": "data-dictionary",
        "ui-spec": "ui-spec",
        "ui_spec": "ui-spec",
        "wireframe": "wireframe",
        "save": "save",
        "recall": "recall",
        "remember": "remember",
        "team": "team",
    }

    cmd = command_map.get(command.lower(), command)

    typer.echo(f"Running: beacon {cmd}" + (f" {feature}" if feature else ""))
    typer.echo(f"Project: {project_root}")

    # Build the command
    full_cmd = [cmd]
    if feature:
        full_cmd.append(feature)
    versioned_commands = {
        "think",
        "user-story",
        "prd",
        "test-case",
        "workflow",
        "status",
        "report",
    }
    if cmd in versioned_commands:
        full_cmd.extend(["--version", resolved_version])

    # Run the command
    result = subprocess.run(
        [sys.executable, "-m", "beacon.main"] + full_cmd,
        cwd=project_root,
    )

    if result.returncode == 0:
        typer.echo(f"\n✓ Command completed successfully")
    else:
        typer.echo(f"\n✗ Command failed with code {result.returncode}")
        raise typer.Exit(result.returncode)


if __name__ == "__main__":
    app()
