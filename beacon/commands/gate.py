"""Beacon gate command - Gate validation with 20+ reason codes"""
import typer
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from datetime import datetime, timezone
from enum import Enum
import hashlib
import os

from beacon.utils.artifact_update_obligations import load_artifact_update_obligations
from beacon.utils.artifact_paths import execution_file_candidates
from beacon.utils.control_plane import build_resume_contract
from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.debug_feedback import (
    append_debug_event_memory,
    append_debug_feedback_event,
    is_debug_mode_enabled,
)
from beacon.utils.memory import load_memory_entries
from beacon.utils.memory import scope_memory_paths
from beacon.utils.qa9 import QA9_TYPES, normalize_qa_type, parse_qa_types
from beacon.utils.qa_runtime import load_qa_status
from beacon.utils.exhaustiveness import load_exhaustiveness_report
from beacon.utils.implementation_plan import (
    implementation_plan_supported,
    list_implementation_git_workflow_contracts,
    load_implementation_plan,
    load_implementation_plan_progress,
)
from beacon.utils.qa_precision import load_feature_qa_ac_closure, load_feature_qa_scorecard
from beacon.utils.prototype_support import feature_requires_route_closure, prototype_status, version_requires_prototype
from beacon.utils.requirement_clarity import (
    build_requirement_clarity_gate_payload,
    load_requirement_clarity_state,
)
from beacon.utils.revision_state import load_revision_state
from beacon.utils.technical_review_contract import (
    build_technical_review_gate_payload,
    load_technical_review_state,
)
from beacon.utils.versioning import project_runtime_feature_enabled, resolve_runtime_version, resolve_target_version
from beacon.utils.v110_baseline import (
    load_latest_baseline_snapshot,
    load_latest_spec_fingerprint,
)
from beacon.utils.workflow_memory import compute_memory_metrics, load_lifecycle_events

app = typer.Typer(name="gate", help="Run gate checks for workflow stages")

# Gate modes
class GateMode(str, Enum):
    STRICT = "strict"
    NORMAL = "normal"
    DEBUG = "debug"
    DRY_RUN = "dry-run"


class GateProfile(str, Enum):
    AUTO = "auto"
    STAGE_LOCAL = "stage-local"
    RELEASE_GLOBAL = "release-global"


# Standard reason codes (25 codes)
REASON_CODES = [
    "blocking_open_question_exists",
    "boundaries_missing",
    "boundaries_schema_invalid",
    "terminal_artifact_missing",
    "terminal_schema_invalid",
    "terminal_status_invalid",
    "ac_tc_mapping_gap",
    "terminal_evidence_missing",
    "evidence_ref_path_style_inconsistent",
    "arch_artifact_missing",
    "ownership_boundary_unclear",
    "control_plane_recovery_open",
    "checkpoint_contract_missing",
    "feature_qa_missing",
    "evidence_not_closed",
    "learning_input_missing",
    "artifact_updates_pending",
    "api_contract_drift",
    "nfr_budget_unproven",
    "evidence_integrity_missing",
    "raw_command_log_missing",
    "raw_command_log_invalid",
    "evidence_sha256_manifest_missing",
    "evidence_sha256_manifest_invalid",
    "evidence_sha256_manifest_incomplete",
    "evidence_sha256_manifest_mismatch",
    "gate_consistency_report_missing",
    "gate_consistency_report_invalid",
    "gate_consistency_report_mismatch",
    "gate_consistency_conflict",
    "scope_guard_violation",
    "scope_guard_confirmation_pending",
    "memory_lifecycle_missing",
    "memory_evidence_missing",
    "memory_feedback_unsynced",
    "release_memory_profile_invalid",
    "memory_run_selector_drift",
    "test_execution_missing",
    "test_key_actions_missing",
    "ac_tc_evidence_chain_broken",
    "coverage_incomplete",
    "qa9_matrix_missing",
    "qa9_matrix_schema_invalid",
    "qa9_required_type_missing",
    "qa9_waiver_missing_approval",
    "qa9_ac_traceability_broken",
    "qa9_command_missing_auto_case",
    "qa9_automation_rate_below_target",
    "qa_llm_plan_missing",
    "qa_llm_plan_invalid",
    "qa_llm_project_scan_missing",
    "qa_llm_skip_without_rationale",
    "contract_spec_missing",
    "contract_verification_missing",
    "integration_env_missing",
    "integration_execution_missing",
    "compatibility_matrix_missing",
    "compatibility_axis_incomplete",
    "compatibility_execution_missing",
    "execution_fingerprint_missing",
    "execution_fingerprint_mismatch",
    "evidence_replay_detected",
    "story_exhaustiveness_missing",
    "story_exhaustiveness_below_threshold",
    "browser_replay_missing",
    "browser_evidence_incomplete",
    "required_scenario_family_missing",
    "implementation_plan_missing",
    "implementation_plan_blocked",
    "implementation_plan_incomplete",
    "implementation_plan_matrix_alignment_missing",
    "evidence_timestamp_out_of_window",
    "assertion_count_zero_pass",
    "junit_missing_or_invalid",
    "report_result_mismatch",
    "flaky_rate_exceeded",
    "manual_waiver_unapproved",
    "spec_impl_drift_detected",
    "baseline_snapshot_missing",
    "baseline_revision_broken",
    "execution_config_missing",
    "execution_config_schema_invalid",
    "source_info_missing",
    "source_info_schema_invalid",
    "git_alignment_missing",
    "git_alignment_schema_invalid",
    "git_alignment_blocked",
    "delivery_manifest_missing",
    "delivery_manifest_schema_invalid",
    "affected_projects_empty",
    "affected_project_git_ref_missing",
    "change_impact_missing",
    "change_impact_schema_invalid",
    "change_impact_open_tasks",
    "prototype_missing",
    "prototype_not_frozen",
    "prototype_stale",
    "prototype_source_untraceable",
    "prototype_ui_contract_failed",
    "prototype_accessibility_contract_failed",
    "prototype_theme_contract_missing",
    "prototype_navigation_contract_missing",
    "prototype_interaction_contract_missing",
    "prototype_design_brief_missing",
    "prototype_design_system_contract_missing",
    "prototype_design_prompt_missing",
    "prototype_web_guideline_review_missing",
    "prototype_plan_missing",
    "prototype_coverage_missing",
    "prototype_page_inventory_missing",
    "prototype_required_page_missing",
    "prototype_required_state_missing",
    "prototype_compact_mode_detected",
    "prototype_baseline_regression",
    "prototype_artifact_inconsistent",
    "prototype_cjk_parse_failed",
    "prototype_review_missing",
    "prototype_review_failed",
    "prototype_design_review_failed",
    "formal_package_closure_missing",
]

# Default gate evaluation stages
GATE_STAGES = ["think", "user-story", "prd", "test-case", "release"]

# Gate configuration file
GATE_CONFIG_FILE = "gate-config.json"
DEFAULT_GATE_CONFIG: Dict[str, Any] = {
    "strict_default": True,
    "mode": "strict",
    "warn_on_force": True,
    "log_risks": True,
    "scope_guard_enabled": True,
}


def resolve_gate_mode(*, strict: bool, mode: Optional[str], project_root: Path) -> tuple[GateMode, Dict[str, Any]]:
    """Resolve effective gate mode with CLI flags + config fallback."""
    gate_mode = GateMode.STRICT if strict else GateMode.NORMAL
    if mode:
        try:
            gate_mode = GateMode(mode)
        except ValueError as exc:
            raise ValueError(f"Invalid mode '{mode}'. Use strict/normal/debug/dry-run") from exc

    config = load_gate_config(project_root)
    if not strict and not mode and "mode" in config:
        try:
            gate_mode = GateMode(config["mode"])
        except ValueError:
            pass
    return gate_mode, config


@app.callback(invoke_without_command=True)
def gate_callback(  # noqa: PLR0913
    ctx: typer.Context,
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
    profile: str = typer.Option(
        "auto",
        "--profile",
        help="Gate profile: auto/stage-local/release-global.",
    ),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    force: bool = typer.Option(False, "--force", help="Force pass with risk logging"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    qa_policy: str = typer.Option("legacy", "--qa-policy", help="QA policy: legacy/qa9-core/qa9-strict"),
    min_automation_rate: float = typer.Option(
        0.85,
        "--min-automation-rate",
        help="Minimum automation coverage rate for QA9 policy.",
    ),
    require_qa_types: Optional[list[str]] = typer.Option(
        None,
        "--require-qa-types",
        help="Required QA types list (comma-separated or repeatable).",
    ),
    require_compat_matrix: bool = typer.Option(
        False,
        "--require-compat-matrix",
        help="Require compatibility matrix checks.",
    ),
    version: Optional[str] = typer.Option(
        None,
        "--version",
        "-v",
        help="Target docs version (default: resolve from env/latest)",
    ),
):
    """Default gate behavior: run checks for all workflow stages."""
    if ctx.invoked_subcommand is not None:
        return

    root = Path(project_root) if project_root else Path.cwd()
    try:
        gate_mode, gate_config = resolve_gate_mode(strict=strict, mode=mode, project_root=root)
    except ValueError as exc:
        typer.echo(f"Error: {exc}")
        raise typer.Exit(code=1)
    compat_required = bool(require_compat_matrix)
    if str(qa_policy or "").strip().lower() == "qa9-strict":
        compat_required = True

    stage_results: list[dict[str, Any]] = []
    for stage in GATE_STAGES:
        result = run_gate_checks(
            stage,
            gate_mode,
            root,
            force,
            config=gate_config,
            qa_policy=qa_policy,
            min_automation_rate=min_automation_rate,
            require_qa_types=require_qa_types,
            require_compat_matrix=compat_required,
            version=version,
            profile=profile,
        )
        stage_results.append(result)

    blocked = [item for item in stage_results if item.get("status") == "Blocked"]
    warned = [item for item in stage_results if item.get("status") == "Warn"]
    if blocked:
        overall_status = "Blocked"
    elif warned:
        overall_status = "Warn"
    else:
        overall_status = "Pass"

    payload = {
        "mode": gate_mode.value,
        "profile": profile,
        "status": overall_status,
        "stage_count": len(stage_results),
        "blocked_stages": [item.get("stage") for item in blocked],
        "warn_stages": [item.get("stage") for item in warned],
        "results": stage_results,
    }

    if json_output:
        typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        color = (
            typer.colors.RED
            if overall_status == "Blocked"
            else typer.colors.YELLOW if overall_status == "Warn" else typer.colors.GREEN
        )
        typer.echo(f"Gate status: {typer.style(overall_status.upper(), fg=color)}")
        for item in stage_results:
            stage_status = str(item.get("status", "Unknown")).upper()
            typer.echo(f"  - {item.get('stage')}: {stage_status} ({len(item.get('issues', []))} issues)")

    raise typer.Exit(code=2 if overall_status == "Blocked" else 0)


def resolve_gate_profile(stage: str, profile: Optional[str]) -> GateProfile:
    raw = str(profile or "auto").strip().lower().replace("_", "-")
    if raw in {"", "auto"}:
        return GateProfile.RELEASE_GLOBAL if stage == "release" else GateProfile.STAGE_LOCAL
    if raw in {"stage-local", "stage", "local"}:
        return GateProfile.STAGE_LOCAL
    if raw in {"release-global", "global", "release"}:
        return GateProfile.RELEASE_GLOBAL
    raise ValueError(f"Invalid gate profile '{profile}'. Use auto/stage-local/release-global")


def get_gate_config_path(project_root: Path) -> Path:
    """Get gate config file path"""
    return project_root / ".beacon" / GATE_CONFIG_FILE


def load_gate_config(project_root: Path) -> Dict[str, Any]:
    """Load gate configuration"""
    config_path = get_gate_config_path(project_root)
    if config_path.exists():
        try:
            loaded = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            typer.echo(
                f"[gate] warning: invalid {config_path.name}; fallback to defaults ({exc})",
                err=True,
            )
            return dict(DEFAULT_GATE_CONFIG)
        if not isinstance(loaded, dict):
            typer.echo(
                f"[gate] warning: invalid {config_path.name} root type; fallback to defaults",
                err=True,
            )
            return dict(DEFAULT_GATE_CONFIG)
        merged = dict(DEFAULT_GATE_CONFIG)
        merged.update(loaded)
        return merged
    return dict(DEFAULT_GATE_CONFIG)


def save_gate_config(project_root: Path, config: Dict[str, Any]):
    """Save gate configuration"""
    config_path = get_gate_config_path(project_root)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))


def get_gate_report_path(project_root: Path) -> Path:
    """Get gate report path"""
    return project_root / ".beacon" / "gate-report.json"


def get_evidence_manifest_path(project_root: Path) -> Path:
    """Get evidence manifest path"""
    return project_root / ".beacon" / "evidence-manifest.json"


def get_raw_command_log_path(project_root: Path) -> Path:
    """Get raw command log path"""
    return project_root / ".beacon" / "raw-command-log.jsonl"


def _execution_file_candidates(project_root: Path, version: str, filename: str) -> list[Path]:
    """Return canonical execution artifact path under docs/beacon."""
    return execution_file_candidates(project_root, version, filename)


def _resolved_gate_version(project_root: Path, requested_version: Optional[str] = None) -> str:
    requested = str(requested_version or "").strip()
    if not requested:
        requested = str(os.environ.get("BEACON_VERSION", "") or "").strip()
    return resolve_target_version(project_root, requested or None)


def _resolve_existing_execution_file(project_root: Path, version: str, filename: str) -> Path:
    candidates = _execution_file_candidates(project_root, version, filename)
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def check_boundaries(project_root: Path, mode: GateMode, version: Optional[str] = None) -> List[Dict[str, Any]]:
    """Check boundaries.md exists"""
    issues = []
    version = _resolved_gate_version(project_root, version)
    boundaries_path = _resolve_existing_execution_file(project_root, version, "boundaries.md")

    if not boundaries_path.exists():
        issue = {
            "reason_code": "boundaries_missing",
            "severity": "critical" if mode == GateMode.STRICT else "high",
            "message": f"boundaries.md not found at {boundaries_path}",
            "blocked": mode == GateMode.STRICT,
        }
        issues.append(issue)
        if mode == GateMode.DEBUG:
            typer.echo(f"  [DEBUG] {issue['reason_code']}: {issue['message']}")

    # Minimal schema validation (non-empty markdown)
    if boundaries_path.exists():
        content = boundaries_path.read_text(encoding="utf-8", errors="ignore").strip()
        if not content or "#" not in content:
            issue = {
                "reason_code": "boundaries_schema_invalid",
                "severity": "critical" if mode == GateMode.STRICT else "high",
                "message": f"boundaries.md appears empty/invalid markdown: {boundaries_path}",
                "blocked": mode == GateMode.STRICT,
            }
            issues.append(issue)

    return issues


def check_terminal_artifact(project_root: Path, mode: GateMode, version: Optional[str] = None) -> List[Dict[str, Any]]:
    """Check terminal.json exists and is valid"""
    issues = []
    version = _resolved_gate_version(project_root, version)
    terminal_path = _resolve_existing_execution_file(project_root, version, "terminal.json")

    if not terminal_path.exists():
        issue = {
            "reason_code": "terminal_artifact_missing",
            "severity": "critical" if mode == GateMode.STRICT else "high",
            "message": f"terminal.json not found at {terminal_path}",
            "blocked": mode == GateMode.STRICT,
        }
        issues.append(issue)
        if mode == GateMode.DEBUG:
            typer.echo(f"  [DEBUG] {issue['reason_code']}: {issue['message']}")
        return issues

    # Validate terminal schema
    try:
        terminal_data = json.loads(terminal_path.read_text())
        required_fields = ["status", "traceability"]
        for field in required_fields:
            if field not in terminal_data:
                issue = {
                    "reason_code": "terminal_schema_invalid",
                    "severity": "critical" if mode == GateMode.STRICT else "high",
                    "message": f"terminal.json missing required field: {field}",
                    "blocked": mode == GateMode.STRICT,
                }
                issues.append(issue)

        # Basic traceability contract validation
        traceability = terminal_data.get("traceability")
        if "traceability" in terminal_data and not isinstance(traceability, dict):
            issue = {
                "reason_code": "terminal_schema_invalid",
                "severity": "critical" if mode == GateMode.STRICT else "high",
                "message": "terminal.json field `traceability` must be an object",
                "blocked": mode == GateMode.STRICT,
            }
            issues.append(issue)
        elif isinstance(traceability, dict):
            ac_to_tc = traceability.get("ac_to_tc")
            if "ac_to_tc" in traceability and not ac_to_tc:
                issue = {
                    "reason_code": "ac_tc_mapping_gap",
                    "severity": "critical" if mode == GateMode.STRICT else "high",
                    "message": "traceability.ac_to_tc is empty",
                    "blocked": mode == GateMode.STRICT,
                }
                issues.append(issue)

            evidence_refs = traceability.get("evidence_refs")
            if "evidence_refs" in traceability:
                if not isinstance(evidence_refs, list) or not evidence_refs:
                    issue = {
                        "reason_code": "terminal_evidence_missing",
                        "severity": "critical" if mode == GateMode.STRICT else "high",
                        "message": "traceability.evidence_refs is missing/empty",
                        "blocked": mode == GateMode.STRICT,
                    }
                    issues.append(issue)
                else:
                    bad_style = [
                        ref for ref in evidence_refs
                        if isinstance(ref, str) and (ref.startswith("/") or "\\" in ref)
                    ]
                    if bad_style:
                        issue = {
                            "reason_code": "evidence_ref_path_style_inconsistent",
                            "severity": "medium",
                            "message": f"traceability.evidence_refs contains non-project-relative paths: {bad_style[:3]}",
                            "blocked": False,
                        }
                        issues.append(issue)

        # Check status validity
        valid_statuses = ["Pass", "Blocked", "Cancelled"]
        if "status" in terminal_data and terminal_data["status"] not in valid_statuses:
            issue = {
                "reason_code": "terminal_status_invalid",
                "severity": "critical" if mode == GateMode.STRICT else "high",
                "message": f"terminal.json invalid status: {terminal_data.get('status')}",
                "blocked": mode == GateMode.STRICT,
            }
            issues.append(issue)

        # Check for blocking open questions
        if "open_questions" in terminal_data:
            blocking_questions = [
                q for q in terminal_data["open_questions"]
                if q.get("blocking", False)
            ]
            if blocking_questions:
                issue = {
                    "reason_code": "blocking_open_question_exists",
                    "severity": "critical" if mode == GateMode.STRICT else "high",
                    "message": f"Found {len(blocking_questions)} blocking open questions",
                    "blocked": mode == GateMode.STRICT,
                }
                issues.append(issue)

        if mode == GateMode.DEBUG:
            typer.echo(f"  [DEBUG] terminal.json schema valid")

    except json.JSONDecodeError as e:
        issue = {
            "reason_code": "terminal_schema_invalid",
            "severity": "critical" if mode == GateMode.STRICT else "high",
            "message": f"terminal.json is not valid JSON: {e}",
            "blocked": mode == GateMode.STRICT,
        }
        issues.append(issue)

    return issues


def check_evidence_chain(project_root: Path, mode: GateMode) -> List[Dict[str, Any]]:
    """Check evidence chain integrity"""
    issues = []

    # Check raw-command-log
    raw_log_path = get_raw_command_log_path(project_root)
    if not raw_log_path.exists():
        issue = {
            "reason_code": "raw_command_log_missing",
            "severity": "high",
            "message": f"raw-command-log not found at {raw_log_path}",
            "blocked": mode == GateMode.STRICT,
        }
        issues.append(issue)
    else:
        raw_invalid_count = 0
        has_any = False
        with raw_log_path.open("r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                has_any = True
                try:
                    payload = json.loads(line)
                    if not isinstance(payload, dict):
                        raw_invalid_count += 1
                except Exception:
                    raw_invalid_count += 1
        if not has_any or raw_invalid_count > 0:
            issue = {
                "reason_code": "raw_command_log_invalid",
                "severity": "high",
                "message": (
                    "raw-command-log must be JSONL with object lines"
                    + (f"; invalid_lines={raw_invalid_count}" if raw_invalid_count else "; file is empty")
                ),
                "blocked": mode == GateMode.STRICT,
            }
            issues.append(issue)
        elif mode == GateMode.DEBUG:
            typer.echo(f"  [DEBUG] raw-command-log.jsonl valid")

    # Check evidence-manifest
    manifest_path = get_evidence_manifest_path(project_root)
    if not manifest_path.exists():
        issue = {
            "reason_code": "evidence_sha256_manifest_missing",
            "severity": "high",
            "message": f"evidence-manifest not found at {manifest_path}",
            "blocked": mode == GateMode.STRICT,
        }
        issues.append(issue)
    else:
        try:
            manifest = json.loads(manifest_path.read_text())
            # Check manifest structure (兼容 entries/items)
            entries = manifest.get("entries")
            if entries is None:
                entries = manifest.get("items")
            if not isinstance(entries, list):
                issue = {
                    "reason_code": "evidence_sha256_manifest_invalid",
                    "severity": "high",
                    "message": "evidence-manifest missing list field: entries/items",
                    "blocked": mode == GateMode.STRICT,
                }
                issues.append(issue)
                entries = []
            elif mode == GateMode.DEBUG:
                typer.echo(f"  [DEBUG] evidence-manifest.json valid with {len(entries)} entries")

            # Check integrity
            for entry in entries:
                if not isinstance(entry, dict):
                    issue = {
                        "reason_code": "evidence_sha256_manifest_incomplete",
                        "severity": "medium",
                        "message": f"evidence-manifest entry is not object: {entry}",
                        "blocked": False,
                    }
                    issues.append(issue)
                    continue
                if "sha256" not in entry or "path" not in entry:
                    issue = {
                        "reason_code": "evidence_sha256_manifest_incomplete",
                        "severity": "medium",
                        "message": f"evidence-manifest entry missing sha256 or path: {entry}",
                        "blocked": False,
                    }
                    issues.append(issue)
                    continue

                rel_path = str(entry.get("path", ""))
                if rel_path.startswith("/") or "\\" in rel_path:
                    issue = {
                        "reason_code": "evidence_ref_path_style_inconsistent",
                        "severity": "medium",
                        "message": f"evidence path should be project-relative POSIX style: {rel_path}",
                        "blocked": False,
                    }
                    issues.append(issue)
                    continue
                if (
                    rel_path.startswith(".beacon/state/spec-fingerprints/")
                    or rel_path.startswith(".beacon/state/baselines/")
                ) and rel_path.endswith("/latest.json"):
                    # rolling pointers are validated separately by spec-consistency;
                    # do not fail release gate on mutable alias hash drift here.
                    continue

                # Verify file exists and hash matches
                file_path = project_root / rel_path
                if file_path.exists():
                    file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
                    if file_hash != entry["sha256"]:
                        issue = {
                            "reason_code": "evidence_sha256_manifest_mismatch",
                            "severity": "critical" if mode == GateMode.STRICT else "high",
                            "message": f"Hash mismatch for {entry['path']}",
                            "blocked": mode == GateMode.STRICT,
                        }
                        issues.append(issue)
                else:
                    issue = {
                        "reason_code": "evidence_sha256_manifest_mismatch",
                        "severity": "critical" if mode == GateMode.STRICT else "high",
                        "message": f"evidence file missing: {rel_path}",
                        "blocked": mode == GateMode.STRICT,
                    }
                    issues.append(issue)

        except json.JSONDecodeError as e:
            issue = {
                "reason_code": "evidence_sha256_manifest_invalid",
                "severity": "high",
                "message": f"evidence-manifest is not valid JSON: {e}",
                "blocked": mode == GateMode.STRICT,
            }
            issues.append(issue)

    # Check gate-report
    report_path = get_gate_report_path(project_root)
    if not report_path.exists():
        issue = {
            "reason_code": "gate_consistency_report_missing",
            "severity": "medium",
            "message": f"gate-report not found at {report_path}",
            "blocked": False,
        }
        issues.append(issue)
    else:
        try:
            report_data = json.loads(report_path.read_text(encoding="utf-8"))
            if not isinstance(report_data, dict):
                raise ValueError("gate-report root is not object")
            for field in ("stage", "mode", "status"):
                if field not in report_data:
                    issues.append(
                        {
                            "reason_code": "gate_consistency_report_invalid",
                            "severity": "high",
                            "message": f"gate-report missing required field: {field}",
                            "blocked": mode == GateMode.STRICT,
                        }
                    )

            report_status = report_data.get("status")
            valid_statuses = {"Pass", "Blocked", "Cancelled", "Conditional-Pass"}
            if report_status and report_status not in valid_statuses:
                issues.append(
                    {
                        "reason_code": "gate_consistency_report_invalid",
                        "severity": "high",
                        "message": f"gate-report invalid status: {report_status}",
                        "blocked": mode == GateMode.STRICT,
                    }
                )

            report_issues = report_data.get("issues")
            if report_issues is not None and not isinstance(report_issues, list):
                issues.append(
                    {
                        "reason_code": "gate_consistency_report_invalid",
                        "severity": "high",
                        "message": "gate-report issues must be a list",
                        "blocked": mode == GateMode.STRICT,
                    }
                )
            elif isinstance(report_issues, list):
                report_blocked = any(bool(item.get("blocked")) for item in report_issues if isinstance(item, dict))
                if report_status == "Pass" and report_blocked:
                    issues.append(
                        {
                            "reason_code": "gate_consistency_report_mismatch",
                            "severity": "high",
                            "message": "gate-report status=Pass but contains blocked issues",
                            "blocked": mode == GateMode.STRICT,
                        }
                    )
                if report_status == "Blocked" and not report_blocked:
                    issues.append(
                        {
                            "reason_code": "gate_consistency_conflict",
                            "severity": "high",
                            "message": "gate-report status=Blocked but no blocked issues in report",
                            "blocked": mode == GateMode.STRICT,
                        }
                    )
        except Exception as e:
            issues.append(
                {
                    "reason_code": "gate_consistency_report_invalid",
                    "severity": "high",
                    "message": f"gate-report invalid JSON/schema: {e}",
                    "blocked": mode == GateMode.STRICT,
                }
            )

    return issues


def _read_scope_items(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        items = payload.get("items")
        if isinstance(items, list):
            return [i for i in items if isinstance(i, dict)]
    except Exception:
        return []
    return []


def check_scope_guard(project_root: Path, mode: GateMode) -> List[Dict[str, Any]]:
    """Check Scope Guard integration"""
    issues = []

    if mode != GateMode.STRICT:
        return issues

    # Check for scope guard violations
    scope_guard_path = project_root / ".beacon" / "scope-guard.json"
    if scope_guard_path.exists():
        try:
            scope_data = json.loads(scope_guard_path.read_text())
            violations = scope_data.get("violations", [])

            if violations:
                high_severity = [v for v in violations if v.get("severity") in ["high", "critical"]]
                if high_severity:
                    issue = {
                        "reason_code": "scope_guard_violation",
                        "severity": "critical",
                        "message": f"Found {len(high_severity)} high severity scope violations",
                        "blocked": True,
                        "details": high_severity,
                    }
                    issues.append(issue)

            if not scope_data.get("confirmed", False):
                issue = {
                    "reason_code": "scope_guard_confirmation_pending",
                    "severity": "high",
                    "message": "Scope Guard confirmation not completed",
                    "blocked": True,
                }
                issues.append(issue)

            if mode == GateMode.DEBUG:
                typer.echo(f"  [DEBUG] Scope Guard: {len(violations)} violations, confirmed={scope_data.get('confirmed')}")

        except json.JSONDecodeError:
            pass
    else:
        # PTK-style scope memory fallback
        deviations_path, confirmations_path = scope_memory_paths(project_root)
        deviations = _read_scope_items(deviations_path)
        confirmations = _read_scope_items(confirmations_path)

        high_deviation_ids = {
            str(item.get("id"))
            for item in deviations
            if item.get("risk") == "high" or item.get("type") == "out-of-scope"
        }
        confirmed_ids = {
            str(item.get("deviation_id"))
            for item in confirmations
            if str(item.get("status")) == "confirmed"
        }
        pending_ids = {
            str(item.get("deviation_id"))
            for item in confirmations
            if str(item.get("status")) != "confirmed"
        }
        unconfirmed_high = sorted(x for x in high_deviation_ids if x and x not in confirmed_ids)

        if unconfirmed_high:
            issues.append(
                {
                    "reason_code": "scope_guard_violation",
                    "severity": "critical",
                    "message": f"Found {len(unconfirmed_high)} unconfirmed high-risk scope deviations",
                    "blocked": True,
                    "details": unconfirmed_high,
                }
            )

        if pending_ids or unconfirmed_high:
            issues.append(
                {
                    "reason_code": "scope_guard_confirmation_pending",
                    "severity": "high",
                    "message": "Scope Guard confirmation not completed",
                    "blocked": True,
                    "details": sorted(pending_ids) if pending_ids else unconfirmed_high,
                }
            )

    return issues


def check_memory_closure(project_root: Path, mode: GateMode, stage: str, version: Optional[str] = None) -> List[Dict[str, Any]]:
    """Check workflow memory closure for release-stage strict gates."""
    issues = []
    if mode != GateMode.STRICT or stage != "release":
        return issues

    events = load_lifecycle_events(project_root)
    if not events:
        issues.append(
            {
                "reason_code": "memory_lifecycle_missing",
                "severity": "critical",
                "message": "workflow lifecycle memory events are missing",
                "blocked": True,
            }
        )
        return issues

    contract_run_id = _resolve_release_contract_run_id(project_root, version=version)
    metrics = compute_memory_metrics(project_root, run_id=contract_run_id or None, version=version)
    target_run_id = metrics.get("run_id")
    run_events = load_lifecycle_events(project_root, run_id=target_run_id) if target_run_id else events
    if not metrics.get("closure_complete", False):
        missing = metrics.get("missing_closure_stages", [])
        issues.append(
            {
                "reason_code": "memory_lifecycle_missing",
                "severity": "critical",
                "message": f"workflow memory closure is incomplete: missing stages={missing}",
                "blocked": True,
                "details": {"missing_stages": missing, "run_id": target_run_id},
            }
        )

    bad_evidence = []
    for item in run_events:
        if not isinstance(item, dict):
            continue
        event = str(item.get("event", ""))
        if event not in {"stage_finished", "memory_writeback", "feedback_memory_assimilated"}:
            continue
        refs = item.get("evidence_ref")
        if not isinstance(refs, list) or not refs:
            bad_evidence.append(item.get("event_id"))
    if bad_evidence:
        issues.append(
            {
                "reason_code": "memory_evidence_missing",
                "severity": "critical",
                "message": f"memory lifecycle events missing evidence_ref: {len(bad_evidence)}",
                "blocked": True,
                "details": {"event_ids": bad_evidence[:10], "run_id": target_run_id},
            }
        )

    feedback_dir = project_root / ".beacon" / "state" / "requirement-feedback"
    feedback_files = list(feedback_dir.glob("*.json")) if feedback_dir.exists() else []
    if feedback_files:
        memory_items = load_memory_entries(project_root)
        has_feedback_memory = any(str(item.get("source", "")) == "feedback.sync" for item in memory_items)
        has_feedback_event = any(str(item.get("event", "")) == "feedback_memory_assimilated" for item in run_events)
        if not has_feedback_memory or not has_feedback_event:
            issues.append(
                {
                    "reason_code": "memory_feedback_unsynced",
                    "severity": "high",
                    "message": "requirement-feedback exists but feedback memory assimilation is missing",
                    "blocked": True,
                }
            )

    return issues


def _resolve_release_contract_run_id(project_root: Path, version: Optional[str] = None) -> str:
    gate_report_path = project_root / ".beacon" / "gate-report.json"
    gate_payload, gate_status = _load_json_file(gate_report_path)
    if gate_status == "ok" and isinstance(gate_payload, dict):
        run_id = str(gate_payload.get("run_id", "") or "").strip()
        if run_id.startswith("run-"):
            return run_id

    resolved_version = _resolved_gate_version(project_root, version)
    terminal_path = _resolve_existing_execution_file(project_root, resolved_version, "terminal.json")
    payload, status = _load_json_file(terminal_path)
    if status != "ok" or not isinstance(payload, dict):
        return ""
    run_id = str(payload.get("run_id", "") or "").strip()
    return run_id if run_id.startswith("run-") else ""


def _load_run_scoped_spec_fingerprint(project_root: Path, *, version: str, run_id: str) -> dict[str, Any]:
    if not run_id:
        return {}
    path = project_root / ".beacon" / "state" / "spec-fingerprints" / version / f"{run_id}.json"
    return _load_json_file(path)[0] or {}


def _load_run_scoped_baseline(project_root: Path, *, version: str, run_id: str) -> dict[str, Any]:
    if not run_id:
        return {}
    root = project_root / ".beacon" / "state" / "baselines" / version
    if not root.exists():
        return {}
    matches = sorted(
        [
            path
            for path in root.glob(f"bl-{run_id}-*.json")
            if path.is_file() and path.name != "latest.json"
        ]
    )
    if not matches:
        return {}
    return _load_json_file(matches[-1])[0] or {}


def check_release_memory_profile(project_root: Path, mode: GateMode, stage: str, version: Optional[str] = None) -> List[Dict[str, Any]]:
    """Check release-specific memory profile without polluting workflow closure contract."""
    issues: list[dict[str, Any]] = []
    if stage != "release":
        return issues
    if mode not in {GateMode.STRICT, GateMode.DEBUG}:
        return issues

    events = load_lifecycle_events(project_root)
    if not events:
        # Keep missing-lifecycle diagnosis centralized in check_memory_closure.
        return issues

    contract_run_id = _resolve_release_contract_run_id(project_root, version=version)
    metrics = compute_memory_metrics(project_root, run_id=contract_run_id or None, version=version)
    selected_run_id = str(metrics.get("run_id", "") or "")

    # Guard default selector drift: when workflow run exists, selection should prefer it.
    workflow_run_exists = any(
        isinstance(item, dict)
        and str(item.get("run_id", "")).startswith("run-")
        and str(item.get("event", "")) == "stage_started"
        for item in events
    )
    if workflow_run_exists and (not selected_run_id.startswith("run-")):
        issues.append(
            {
                "reason_code": "memory_run_selector_drift",
                "severity": "critical",
                "message": (
                    "default memory metrics selected non-workflow run_id while workflow run exists: "
                    f"{selected_run_id or 'N/A'}"
                ),
                "blocked": True,
                "details": {"selected_run_id": selected_run_id},
            }
        )

    release_events = [
        item
        for item in events
        if isinstance(item, dict)
        and str(item.get("stage", "")) == "release"
        and str(item.get("event", "")) == "release_decision_recorded"
    ]
    if not release_events:
        issues.append(
            {
                "reason_code": "release_memory_profile_invalid",
                "severity": "critical",
                "message": "release stage missing release_decision_recorded memory event",
                "blocked": True,
            }
        )
        return issues

    refs: list[str] = []
    for item in release_events:
        evidence_ref = item.get("evidence_ref")
        if isinstance(evidence_ref, list):
            refs.extend([str(x) for x in evidence_ref if str(x).strip()])
    refs = sorted(set(refs))

    if not refs:
        issues.append(
            {
                "reason_code": "release_memory_profile_invalid",
                "severity": "critical",
                "message": "release_decision_recorded events exist but evidence_ref is empty",
                "blocked": True,
            }
        )
        return issues

    missing_refs = []
    for ref in refs:
        p = Path(ref)
        full = p if p.is_absolute() else project_root / p
        if not full.exists():
            missing_refs.append(ref)
    if missing_refs:
        issues.append(
            {
                "reason_code": "release_memory_profile_invalid",
                "severity": "critical",
                "message": f"release memory evidence files missing: {missing_refs[:10]}",
                "blocked": True,
                "details": {"missing_refs": missing_refs[:10]},
            }
        )

    return issues


def check_prototype_contract(
    project_root: Path,
    mode: GateMode,
    stage: str,
    version: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Check prototype lifecycle artifacts for UI-visualization workflows."""
    if stage not in {"prototype", "release"}:
        return []
    resolved_version = resolve_target_version(project_root, version)
    if not version_requires_prototype(project_root, resolved_version):
        return []

    proto_root = project_root / "docs" / "beacon" / resolved_version / "prototype"
    if not proto_root.exists():
        return [{
            "reason_code": "prototype_missing",
            "blocked": True,
            "message": f"prototype directory missing for UI visualization version {resolved_version}",
        }]

    issues: list[dict[str, Any]] = []
    feature_dirs = [path for path in proto_root.iterdir() if path.is_dir()]
    if not feature_dirs:
        return [{
            "reason_code": "prototype_missing",
            "blocked": True,
            "message": f"prototype directory is empty for UI visualization version {resolved_version}",
        }]

    for feature_dir in sorted(feature_dirs):
        payload = prototype_status(project_root, resolved_version, feature_dir.name)
        files = payload.get("files", {})
        plan_path = Path(files.get("prototype_plan")) if isinstance(files, dict) and files.get("prototype_plan") else None
        coverage_path = Path(files.get("coverage_report")) if isinstance(files, dict) and files.get("coverage_report") else None
        manifest_path = Path(files.get("manifest")) if isinstance(files, dict) and files.get("manifest") else None
        plan_payload = {}
        coverage_payload = {}
        manifest_payload = {}
        if plan_path and plan_path.exists():
            try:
                plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                plan_payload = {}
        if coverage_path and coverage_path.exists():
            try:
                coverage_payload = json.loads(coverage_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                coverage_payload = {}
        if manifest_path and manifest_path.exists():
            try:
                manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                manifest_payload = {}
        prototype_mode = str((plan_payload or {}).get("prototype_mode") or manifest_payload.get("prototype_mode") or "").strip().lower()
        reference_pack_v2 = prototype_mode == "reference-pack-v2"
        design_governance_required = bool(
            (isinstance(plan_payload, dict) and plan_payload.get("contract", {}).get("design_governance_required"))
            or manifest_payload.get("design_governance_required")
        )
        if payload.get("status") == "missing":
            issues.append({
                "reason_code": "prototype_missing",
                "blocked": True,
                "message": f"prototype artifacts missing for feature {feature_dir.name}",
            })
            continue
        if not payload.get("recorded_source_fingerprints"):
            issues.append({
                "reason_code": "prototype_source_untraceable",
                "blocked": True,
                "message": f"prototype freeze/source metadata missing for feature {feature_dir.name}",
            })
        if payload.get("status") == "draft":
            issues.append({
                "reason_code": "prototype_not_frozen",
                "blocked": True,
                "message": f"prototype not frozen for feature {feature_dir.name}",
            })
        if payload.get("status") == "stale":
            issues.append({
                "reason_code": "prototype_stale",
                "blocked": True,
                "message": f"prototype stale for feature {feature_dir.name}",
            })
        if payload.get("status") == "inconsistent":
            issues.append({
                "reason_code": "prototype_artifact_inconsistent",
                "blocked": True,
                "message": f"prototype artifacts inconsistent for feature {feature_dir.name}",
                "details": {"reasons": payload.get("inconsistent_reasons", [])},
            })
        if reference_pack_v2:
            if not plan_path or not plan_path.exists():
                issues.append({
                    "reason_code": "prototype_plan_missing",
                    "blocked": True,
                    "message": f"prototype-plan.json missing for feature {feature_dir.name}",
                })
            if not coverage_path or not coverage_path.exists():
                issues.append({
                    "reason_code": "prototype_coverage_missing",
                    "blocked": True,
                    "message": f"coverage-report.json missing for feature {feature_dir.name}",
                })
            required_pages = [str(item).strip() for item in (plan_payload.get("required_pages") or []) if str(item).strip()] if isinstance(plan_payload, dict) else []
            required_states = [str(item).strip() for item in (plan_payload.get("required_states") or []) if str(item).strip()] if isinstance(plan_payload, dict) else []
            if not required_pages:
                issues.append({
                    "reason_code": "prototype_page_inventory_missing",
                    "blocked": True,
                    "message": f"required page inventory missing for feature {feature_dir.name}",
                })
            pages_dir = Path(files.get("pages_dir")) if isinstance(files, dict) and files.get("pages_dir") else None
            states_dir = Path(files.get("states_dir")) if isinstance(files, dict) and files.get("states_dir") else None
            missing_pages = [page for page in required_pages if not pages_dir or not (pages_dir / f"{page}.html").exists()]
            missing_states = [f"{page}--{state}" for page in required_pages for state in required_states if not states_dir or not (states_dir / f"{page}--{state}.html").exists()]
            if missing_pages:
                issues.append({
                    "reason_code": "prototype_required_page_missing",
                    "blocked": True,
                    "message": f"required pages missing for feature {feature_dir.name}",
                    "details": {"missing_pages": missing_pages[:50]},
                })
            if missing_states:
                issues.append({
                    "reason_code": "prototype_required_state_missing",
                    "blocked": True,
                    "message": f"required state variants missing for feature {feature_dir.name}",
                    "details": {"missing_states": missing_states[:50]},
                })
            if bool((coverage_payload or {}).get("compact_mode_detected")):
                issues.append({
                    "reason_code": "prototype_compact_mode_detected",
                    "blocked": True,
                    "message": f"compact coverage detected for feature {feature_dir.name}",
                })
        files = payload.get("files", {})
        required_contracts = {
            "theme": "prototype_theme_contract_missing",
            "navigation_map": "prototype_navigation_contract_missing",
            "interaction_map": "prototype_interaction_contract_missing",
            "review_json": "prototype_review_missing",
            "review_md": "prototype_review_missing",
        }
        if design_governance_required:
            required_contracts["design_brief"] = "prototype_design_brief_missing"
            required_contracts["design_system_contract"] = "prototype_design_system_contract_missing"
            required_contracts["design_prompt_json"] = "prototype_design_prompt_missing"
            required_contracts["design_prompt_md"] = "prototype_design_prompt_missing"
            required_contracts["web_guideline_review_json"] = "prototype_web_guideline_review_missing"
            required_contracts["web_guideline_review_md"] = "prototype_web_guideline_review_missing"
        if feature_requires_route_closure(project_root, resolved_version, feature_dir.name):
            required_contracts["route_closure_contract"] = "prototype_route_closure_contract_missing"
            required_contracts["implementation_map"] = "prototype_implementation_map_missing"
        for key, reason_code in required_contracts.items():
            file_path = files.get(key)
            if not file_path or not Path(file_path).exists():
                issues.append({
                    "reason_code": reason_code,
                    "blocked": True,
                    "message": f"{key} missing for feature {feature_dir.name}",
                })
        if payload.get("review_status") == "fail":
            issues.append({
                "reason_code": "prototype_review_failed",
                "blocked": True,
                "message": f"prototype review failed for feature {feature_dir.name}",
            })
            review_path = files.get("review_json")
            if review_path and Path(review_path).exists():
                try:
                    review_payload = json.loads(Path(review_path).read_text(encoding="utf-8"))
                except Exception:  # noqa: BLE001
                    review_payload = {}
                failed_checks = {
                    str(item.get("name") or "")
                    for item in (review_payload.get("checks") or [])
                    if isinstance(item, dict) and str(item.get("status") or "") == "fail"
                }
                if "route_closure_binding_complete" in failed_checks:
                    issues.append({
                        "reason_code": "prototype_surface_unbound",
                        "blocked": True,
                        "message": f"route closure bindings unresolved for feature {feature_dir.name}",
                    })
                if "route_closure_no_drift_markers" in failed_checks:
                    issues.append({
                        "reason_code": "prototype_route_closure_drift",
                        "blocked": True,
                        "message": f"route closure drift markers remain for feature {feature_dir.name}",
                    })
                if "route_closure_no_fake_jump" in failed_checks:
                    issues.append({
                        "reason_code": "prototype_fake_jump",
                        "blocked": True,
                        "message": f"fake jump or toast-only navigation remains for feature {feature_dir.name}",
                    })
                if "prototype_baseline_regression" in failed_checks:
                    issues.append({
                        "reason_code": "prototype_baseline_regression",
                        "blocked": True,
                        "message": f"baseline protected pages regressed for feature {feature_dir.name}",
                    })
                if "prototype_artifact_inconsistent" in failed_checks:
                    issues.append({
                        "reason_code": "prototype_artifact_inconsistent",
                        "blocked": True,
                        "message": f"artifact consistency failed for feature {feature_dir.name}",
                    })
                if "prototype_cjk_parse_failed" in failed_checks:
                    issues.append({
                        "reason_code": "prototype_cjk_parse_failed",
                        "blocked": True,
                        "message": f"CJK parse failure detected for feature {feature_dir.name}",
                    })
                if "web_guideline_critical_findings_clear" in failed_checks:
                    issues.append({
                        "reason_code": "prototype_design_review_failed",
                        "blocked": True,
                        "message": f"design guideline review failed for feature {feature_dir.name}",
                    })
        if design_governance_required and str(payload.get("design_review_outcome") or "pass") == "blocked":
            issues.append({
                "reason_code": "prototype_design_review_failed",
                "blocked": True,
                "message": f"design review outcome blocked for feature {feature_dir.name}",
            })
    return issues


def _load_json_file(path: Path) -> tuple[Optional[Dict[str, Any]], str]:
    if not path.exists():
        return None, "missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{exc}"
    if not isinstance(payload, dict):
        return None, "invalid_root"
    return payload, "ok"


def check_delivery_execution_artifacts(project_root: Path, mode: GateMode, stage: str, version: Optional[str] = None) -> List[Dict[str, Any]]:
    """Check execution-layer delivery governance artifacts."""
    issues: list[dict[str, Any]] = []
    if stage != "release":
        return issues
    if mode not in {GateMode.STRICT, GateMode.DEBUG}:
        return issues

    resolved_version = _resolved_gate_version(project_root, version)
    if _parse_semver_tuple(resolved_version) < (1, 1, 1):
        return issues

    def _required_json(name: str, missing_code: str, invalid_code: str) -> Optional[Dict[str, Any]]:
        path = _resolve_existing_execution_file(project_root, resolved_version, name)
        payload, status = _load_json_file(path)
        if payload is None:
            issues.append(
                {
                    "reason_code": missing_code if status == "missing" else invalid_code,
                    "severity": "critical",
                    "message": f"{name} {status}: {path}",
                    "blocked": True,
                }
            )
            return None
        return payload

    config_payload = _required_json("config.json", "execution_config_missing", "execution_config_schema_invalid")
    if isinstance(config_payload, dict):
        missing = [
            key
            for key in ("resolved_project", "docs", "implementation", "source_info", "git", "research", "delivery")
            if key not in config_payload
        ]
        if missing:
            issues.append(
                {
                    "reason_code": "execution_config_schema_invalid",
                    "severity": "critical",
                    "message": f"config.json missing keys: {missing}",
                    "blocked": True,
                }
            )

    source_payload = _required_json("source.json", "source_info_missing", "source_info_schema_invalid")
    if isinstance(source_payload, dict):
        missing = [
            key
            for key in ("project_name", "project_root", "workspace_root", "repo_url", "branch", "commit", "run_id", "version")
            if key not in source_payload
        ]
        if missing:
            issues.append(
                {
                    "reason_code": "source_info_schema_invalid",
                    "severity": "critical",
                    "message": f"source.json missing keys: {missing}",
                    "blocked": True,
                }
            )

    git_payload = _required_json("git-alignment.json", "git_alignment_missing", "git_alignment_schema_invalid")
    if isinstance(git_payload, dict):
        missing = [key for key in ("git_refs", "alignment", "version_ref", "blocked") if key not in git_payload]
        if missing:
            issues.append(
                {
                    "reason_code": "git_alignment_schema_invalid",
                    "severity": "critical",
                    "message": f"git-alignment.json missing keys: {missing}",
                    "blocked": True,
                }
            )
        elif bool(git_payload.get("blocked")):
            issues.append(
                {
                    "reason_code": "git_alignment_blocked",
                    "severity": "critical",
                    "message": f"git alignment blocked: {git_payload.get('reason_codes', [])}",
                    "blocked": True,
                }
            )

    manifest_payload = _required_json("delivery-manifest.json", "delivery_manifest_missing", "delivery_manifest_schema_invalid")
    if isinstance(manifest_payload, dict):
        affected_projects = manifest_payload.get("affected_projects")
        if not isinstance(affected_projects, list) or not affected_projects:
            issues.append(
                {
                    "reason_code": "affected_projects_empty",
                    "severity": "critical",
                    "message": "delivery-manifest.json affected_projects missing/empty",
                    "blocked": True,
                }
            )
        else:
            required_project_fields = {
                "name",
                "project_root",
                "repo_url",
                "change_scope",
                "changed_layers",
                "base_branch",
                "target_branch",
                "current_branch",
                "commit",
                "tag",
                "worktree_path",
            }
            missing_refs: list[dict[str, Any]] = []
            for idx, item in enumerate(affected_projects):
                if not isinstance(item, dict):
                    missing_refs.append({"index": idx, "missing": sorted(required_project_fields)})
                    continue
                missing = sorted(field for field in required_project_fields if field not in item or item.get(field) is None)
                if missing:
                    missing_refs.append({"index": idx, "missing": missing})
            if missing_refs:
                issues.append(
                    {
                        "reason_code": "affected_project_git_ref_missing",
                        "severity": "critical",
                        "message": f"delivery-manifest.json affected_projects missing fields: {missing_refs[:5]}",
                        "blocked": True,
                    }
                )

    if _parse_semver_tuple(resolved_version) >= (1, 3, 0):
        machine_exec_dir = project_root / "docs" / "beacon" / resolved_version / ".machine" / "execution"
        workflow_contracts = list_implementation_git_workflow_contracts(project_root, version=resolved_version)
        required_workflow_fields = {
            "feature",
            "feature_slug",
            "version",
            "mode",
            "expected_branch",
            "branch_prefix",
            "base_branch",
            "use_git_worktree",
            "require_clean_worktree_for_switch",
            "service_directories",
        }
        missing_contracts: list[str] = []
        invalid_contracts: list[dict[str, Any]] = []
        missing_markdown: list[str] = []
        expected_branches: set[str] = set()
        for plan_path in sorted(machine_exec_dir.glob("implementation-plan-*.json")):
            if str(plan_path.name).endswith(".progress.json"):
                continue
            workflow_path = machine_exec_dir / plan_path.name.replace("implementation-plan-", "git-workflow-")
            if not workflow_path.exists():
                missing_contracts.append(str(workflow_path.relative_to(project_root)))
        for item in workflow_contracts:
            payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
            path = str(item.get("path", "") or "")
            missing = sorted(field for field in required_workflow_fields if field not in payload)
            if missing:
                invalid_contracts.append({"path": path, "missing": missing})
            branch = str(payload.get("expected_branch", "") or "").strip()
            if branch:
                expected_branches.add(branch)
            markdown_path = project_root / path.replace("/.machine/execution/", "/execution/").replace(".json", ".md")
            if not markdown_path.exists():
                missing_markdown.append(str(markdown_path.relative_to(project_root)))
        if missing_contracts:
            issues.append(
                {
                    "reason_code": "git_workflow_contract_missing",
                    "severity": "critical",
                    "message": f"git workflow contracts missing for implementation plans: {missing_contracts[:5]}",
                    "blocked": True,
                }
            )
        if invalid_contracts:
            issues.append(
                {
                    "reason_code": "git_workflow_contract_invalid",
                    "severity": "critical",
                    "message": f"git workflow contracts invalid: {invalid_contracts[:5]}",
                    "blocked": True,
                }
            )
        if missing_markdown:
            issues.append(
                {
                    "reason_code": "git_workflow_markdown_missing",
                    "severity": "critical",
                    "message": f"git workflow markdown mirrors missing: {missing_markdown[:5]}",
                    "blocked": True,
                }
            )
        if expected_branches and isinstance(manifest_payload, dict):
            affected_projects = manifest_payload.get("affected_projects") if isinstance(manifest_payload.get("affected_projects"), list) else []
            mismatches: list[dict[str, Any]] = []
            for idx, item in enumerate(affected_projects):
                if not isinstance(item, dict):
                    continue
                target_branch = str(item.get("target_branch", "") or "")
                if target_branch and target_branch not in expected_branches:
                    mismatches.append({"index": idx, "target_branch": target_branch, "expected_branches": sorted(expected_branches)})
            if mismatches:
                issues.append(
                    {
                        "reason_code": "git_workflow_delivery_manifest_mismatch",
                        "severity": "critical",
                        "message": f"delivery-manifest target branches drift from git workflow contract: {mismatches[:5]}",
                        "blocked": True,
                    }
                )

    change_payload = _required_json("change-impact.json", "change_impact_missing", "change_impact_schema_invalid")
    if isinstance(change_payload, dict):
        missing = [
            key
            for key in ("changed_layers", "tasks", "research_converged", "main_chain_converged", "delivery_manifest_ready")
            if key not in change_payload
        ]
        if missing:
            issues.append(
                {
                    "reason_code": "change_impact_schema_invalid",
                    "severity": "critical",
                    "message": f"change-impact.json missing keys: {missing}",
                    "blocked": True,
                }
            )
        tasks = change_payload.get("tasks")
        if not isinstance(tasks, list):
            issues.append(
                {
                    "reason_code": "change_impact_schema_invalid",
                    "severity": "critical",
                    "message": "change-impact.json tasks missing/invalid",
                    "blocked": True,
                }
            )
        else:
            pending = [
                str(item.get("task", ""))
                for item in tasks
                if isinstance(item, dict) and str(item.get("status", "pending")).strip().lower() != "completed"
            ]
            if pending:
                issues.append(
                    {
                        "reason_code": "change_impact_open_tasks",
                        "severity": "critical",
                        "message": f"change-impact.json has pending tasks: {pending}",
                        "blocked": True,
                    }
                )

    return issues


def check_formal_version_package_closure(
    project_root: Path,
    mode: GateMode,
    stage: str,
    version: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Ensure formal Beacon version packages satisfy the minimum closure contract."""
    issues: list[dict[str, Any]] = []
    if stage != "release":
        return issues
    if mode not in {GateMode.STRICT, GateMode.DEBUG}:
        return issues

    resolved_version = _resolved_gate_version(project_root, version)
    root = project_root / "docs" / "beacon" / resolved_version
    required = {
        "SUMMARY.md": (root / "SUMMARY.md").exists(),
        "execution/boundaries.md": (root / "execution" / "boundaries.md").exists(),
        "prd/": (root / "prd").exists() and any((root / "prd").glob("*.md")),
        "user-story/": (root / "user-story").exists() and any((root / "user-story").glob("*.md")),
        "qa/test-cases/": (root / "qa" / "test-cases").exists() and any((root / "qa" / "test-cases").glob("*.md")),
        "release/": (root / "release").exists() and any((root / "release").glob("*.md")),
    }
    if _parse_semver_tuple(resolved_version) >= (1, 1, 10):
        required["execution/project-skill-qa-evolution-blueprint.md"] = (root / "execution" / "project-skill-qa-evolution-blueprint.md").exists()
        required["source-architecture/index.md"] = (root / "source-architecture" / "index.md").exists()
    missing = [name for name, ok in required.items() if not ok]
    if missing:
        issues.append(
            {
                "reason_code": "formal_package_closure_missing",
                "severity": "critical",
                "message": f"formal Beacon version package incomplete for {resolved_version}: missing {missing}",
                "blocked": True,
                "details": {"version": resolved_version, "missing": missing},
            }
        )
    return issues


def check_v110_precision_contract(
    project_root: Path,
    mode: GateMode,
    stage: str,
    version: Optional[str] = None,
) -> List[Dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if stage != "release":
        return issues
    if mode not in {GateMode.STRICT, GateMode.DEBUG}:
        return issues
    resolved_version = _resolved_gate_version(project_root, version)
    if _parse_semver_tuple(resolved_version) < (1, 1, 10):
        return issues

    qa_status = load_qa_status(project_root)
    if not qa_status:
        issues.append(
            {
                "reason_code": "feature_qa_missing",
                "severity": "critical",
                "message": "v1.1.10 release requires canonical feature-aware QA status",
                "blocked": True,
            }
        )
        return issues

    feature_name = str(qa_status.get("feature", "") or "").strip()
    if not feature_name:
        issues.append(
            {
                "reason_code": "feature_name_missing",
                "severity": "critical",
                "message": "v1.1.10 release requires feature-aware QA to record the feature name",
                "blocked": True,
            }
        )
        return issues

    project_profile_gate = qa_status.get("project_profile_gate") if isinstance(qa_status.get("project_profile_gate"), dict) else {}
    project_gate_status = str(project_profile_gate.get("status") or "not_configured")
    if project_gate_status == "blocked":
        issues.append(
            {
                "reason_code": "project_profile_gate_blocked",
                "severity": "critical",
                "message": "project-specific verify workflow gate is blocked",
                "blocked": True,
                "details": {"issues": project_profile_gate.get("issues", [])},
            }
        )

    ac_closure = load_feature_qa_ac_closure(project_root, feature=feature_name)
    if not ac_closure:
        issues.append(
            {
                "reason_code": "ac_closure_missing",
                "severity": "critical",
                "message": "v1.1.10 release requires AC closure artifact",
                "blocked": True,
            }
        )

    feature_scorecard = load_feature_qa_scorecard(project_root, feature=feature_name)
    if not feature_scorecard:
        issues.append(
            {
                "reason_code": "feature_qa_scorecard_missing",
                "severity": "critical",
                "message": "v1.1.10 release requires feature QA scorecard",
                "blocked": True,
            }
        )
        return issues

    unresolved = [str(item) for item in (feature_scorecard.get("unresolved_closure_outcomes") or []) if str(item).strip()]
    if unresolved:
        issues.append(
            {
                "reason_code": "unresolved_closure_outcome",
                "severity": "critical",
                "message": f"unresolved closure outcomes remain: {unresolved}",
                "blocked": True,
            }
        )
    if int(feature_scorecard.get("review_required_count") or 0) > 0:
        issues.append(
            {
                "reason_code": "review_required_open",
                "severity": "critical",
                "message": f"review-required scenarios remain: {feature_scorecard.get('review_required_count')}",
                "blocked": True,
            }
        )
    if int(feature_scorecard.get("needs_replay_count") or 0) > 0:
        issues.append(
            {
                "reason_code": "needs_replay_open",
                "severity": "critical",
                "message": f"needs-replay scenarios remain: {feature_scorecard.get('needs_replay_count')}",
                "blocked": True,
            }
        )
    release_confidence_min = float(feature_scorecard.get("release_confidence_min") or 0.0)
    if release_confidence_min < 0.85:
        issues.append(
            {
                "reason_code": "release_confidence_below_threshold",
                "severity": "critical",
                "message": f"release confidence floor {release_confidence_min} < 0.85",
                "blocked": True,
            }
        )
    if not bool(feature_scorecard.get("release_ready", False)):
        issues.append(
            {
                "reason_code": "feature_release_not_ready",
                "severity": "critical",
                "message": "feature QA scorecard is not release-ready",
                "blocked": True,
            }
        )
    return issues


def _latest_implement_feature(project_root: Path) -> str:
    implement_root = project_root / ".beacon" / "implement"
    if not implement_root.exists():
        return ""
    for state_path in reversed(sorted(implement_root.glob("*/state.json"))):
        try:
            payload = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(payload, dict):
            continue
        feature = str(payload.get("feature", "") or "").strip()
        if feature:
            return feature
    return ""


def check_v112_implementation_plan_contract(
    project_root: Path,
    mode: GateMode,
    stage: str,
    version: Optional[str] = None,
) -> List[Dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if stage != "release":
        return issues
    if mode not in {GateMode.STRICT, GateMode.DEBUG}:
        return issues
    resolved_version = _resolved_gate_version(project_root, version)
    if not implementation_plan_supported(resolved_version):
        return issues

    qa_status = load_qa_status(project_root)
    feature_name = str(qa_status.get("feature", "") or "").strip() or _latest_implement_feature(project_root)
    if not feature_name:
        issues.append(
            {
                "reason_code": "implementation_plan_missing",
                "severity": "critical",
                "message": "release requires implementation plan truth but no feature context could be resolved",
                "blocked": True,
            }
        )
        return issues

    plan = load_implementation_plan(project_root, version=resolved_version, feature=feature_name)
    progress = load_implementation_plan_progress(project_root, version=resolved_version, feature=feature_name)
    if not plan:
        issues.append(
            {
                "reason_code": "implementation_plan_missing",
                "severity": "critical",
                "message": f"implementation plan missing for feature {feature_name}",
                "blocked": True,
            }
        )
        return issues

    if str(progress.get("status", "")).strip().lower() == "blocked":
        issues.append(
            {
                "reason_code": "implementation_plan_blocked",
                "severity": "critical",
                "message": f"implementation plan has blocked tasks: {progress.get('blocked_task_ids', [])}",
                "blocked": True,
            }
        )
    counts = progress.get("counts") if isinstance(progress.get("counts"), dict) else {}
    if int(counts.get("completed", 0) or 0) < int(counts.get("total", 0) or 0):
        issues.append(
            {
                "reason_code": "implementation_plan_incomplete",
                "severity": "critical",
                "message": f"implementation plan incomplete: {counts}",
                "blocked": True,
            }
        )

    source_refs = plan.get("source_refs") if isinstance(plan.get("source_refs"), dict) else {}
    matrix_ref = str(source_refs.get("ac_matrix", "") or "").strip()
    if matrix_ref:
        matrix_path = project_root / matrix_ref
        if matrix_path.exists():
            matrix_payload = {}
            try:
                matrix_payload = json.loads(matrix_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                matrix_payload = {}
            entries = matrix_payload.get("entries") if isinstance(matrix_payload, dict) and isinstance(matrix_payload.get("entries"), list) else []
            ac_ids_with_tc = {
                str(item.get("ac_id", "") or "").strip().upper()
                for item in entries
                if isinstance(item, dict) and str(item.get("ac_id", "") or "").strip() and str(item.get("tc_id", "") or "").strip()
            }
            missing_alignment: list[str] = []
            for task in plan.get("tasks", []):
                if not isinstance(task, dict):
                    continue
                mapped_ac_ids = [str(item).strip().upper() for item in task.get("mapped_ac_ids", []) if str(item).strip()]
                mapped_test_ids = [str(item).strip().upper() for item in task.get("mapped_test_ids", []) if str(item).strip()]
                if any(ac_id in ac_ids_with_tc for ac_id in mapped_ac_ids) and not mapped_test_ids:
                    missing_alignment.append(str(task.get("task_id", "") or ""))
            if missing_alignment:
                issues.append(
                    {
                        "reason_code": "implementation_plan_matrix_alignment_missing",
                        "severity": "critical",
                        "message": f"implementation plan tasks missing AC/test alignment: {missing_alignment}",
                        "blocked": True,
                    }
                )
    scenario_ref = str(source_refs.get("story_scenario_map", "") or "").strip()
    if scenario_ref:
        scenario_path = project_root / scenario_ref
        if scenario_path.exists():
            scenario_payload = {}
            try:
                scenario_payload = json.loads(scenario_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                scenario_payload = {}
            scenarios = scenario_payload.get("scenarios") if isinstance(scenario_payload, dict) and isinstance(scenario_payload.get("scenarios"), list) else []
            ac_or_tc_with_scenarios = {
                str(item.get("ac_id", "") or item.get("source_tc_id", "") or item.get("tc_id", "") or "").strip().upper()
                for item in scenarios
                if isinstance(item, dict) and str(item.get("scenario_id", "") or "").strip()
            }
            missing_scenarios: list[str] = []
            for task in plan.get("tasks", []):
                if not isinstance(task, dict):
                    continue
                mapped_ac_ids = [str(item).strip().upper() for item in task.get("mapped_ac_ids", []) if str(item).strip()]
                mapped_test_ids = [str(item).strip().upper() for item in task.get("mapped_test_ids", []) if str(item).strip()]
                mapped_scenario_ids = [str(item).strip().upper() for item in task.get("mapped_scenario_ids", []) if str(item).strip()]
                if (set(mapped_ac_ids) | set(mapped_test_ids)) & ac_or_tc_with_scenarios and not mapped_scenario_ids:
                    missing_scenarios.append(str(task.get("task_id", "") or ""))
            if missing_scenarios:
                issues.append(
                    {
                        "reason_code": "implementation_plan_matrix_alignment_missing",
                        "severity": "critical",
                        "message": f"implementation plan tasks missing scenario alignment: {missing_scenarios}",
                        "blocked": True,
                    }
                )
    qa9_ref = str(source_refs.get("qa9_matrix", "") or "").strip()
    if qa9_ref:
        qa9_path = project_root / qa9_ref
        if qa9_path.exists():
            qa9_payload = {}
            try:
                qa9_payload = json.loads(qa9_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                qa9_payload = {}
            entries = qa9_payload.get("entries") if isinstance(qa9_payload, dict) and isinstance(qa9_payload.get("entries"), list) else []
            ac_or_tc_with_qa = {
                str(item.get("ac_id", "") or item.get("tc_id", "") or item.get("source_tc_id", "") or "").strip().upper()
                for item in entries
                if isinstance(item, dict) and str(item.get("id", "") or item.get("tc_id", "") or "").strip()
            }
            missing_qa: list[str] = []
            for task in plan.get("tasks", []):
                if not isinstance(task, dict):
                    continue
                mapped_ac_ids = [str(item).strip().upper() for item in task.get("mapped_ac_ids", []) if str(item).strip()]
                mapped_test_ids = [str(item).strip().upper() for item in task.get("mapped_test_ids", []) if str(item).strip()]
                mapped_qa_case_ids = [str(item).strip().upper() for item in task.get("mapped_qa_case_ids", []) if str(item).strip()]
                if (set(mapped_ac_ids) | set(mapped_test_ids)) & ac_or_tc_with_qa and not mapped_qa_case_ids:
                    missing_qa.append(str(task.get("task_id", "") or ""))
            if missing_qa:
                issues.append(
                    {
                        "reason_code": "implementation_plan_matrix_alignment_missing",
                        "severity": "critical",
                        "message": f"implementation plan tasks missing QA alignment: {missing_qa}",
                        "blocked": True,
                    }
                )
    return issues


def check_v131_human_loop_contract(
    project_root: Path,
    mode: GateMode,
    stage: str,
    version: Optional[str] = None,
) -> List[Dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if stage != "release":
        return issues
    if mode not in {GateMode.STRICT, GateMode.DEBUG}:
        return issues
    resolved_version = _resolved_gate_version(project_root, version)
    resolved_runtime = resolve_runtime_version(project_root, "auto")
    if not project_runtime_feature_enabled(
        project_root,
        "v1.3.1",
        docs_version=resolved_version,
        runtime_version=resolved_runtime,
    ):
        return issues

    feature_name = str(load_qa_status(project_root).get("feature") or "").strip() or _latest_implement_feature(project_root)
    if not feature_name:
        issues.append(
            {
                "reason_code": "feature_name_missing",
                "severity": "critical",
                "message": "v1.3.1 release requires feature context to evaluate human-loop contracts",
                "blocked": True,
            }
        )
        return issues

    revision = load_revision_state(project_root, version=resolved_version, feature=feature_name, create_if_missing=False)
    requirement_gate = build_requirement_clarity_gate_payload(project_root, version=resolved_version, feature=feature_name)
    requirement_state = load_requirement_clarity_state(project_root, feature=feature_name)
    technical_gate = build_technical_review_gate_payload(
        project_root,
        version=resolved_version,
        feature=feature_name,
        revision_id=str(revision.get("revision_id", "") or ""),
    )
    technical_state = load_technical_review_state(project_root, feature=feature_name)

    if bool(requirement_gate.get("required")):
        if not requirement_state:
            issues.append(
                {
                    "reason_code": "requirement_clarity_state_missing",
                    "severity": "critical",
                    "message": f"requirement clarity state missing for feature {feature_name}",
                    "blocked": True,
                }
            )
        if bool(requirement_gate.get("blocked")):
            issues.append(
                {
                    "reason_code": "requirement_clarity_open",
                    "severity": "critical",
                    "message": f"requirement clarity still blocked for feature {feature_name}",
                    "blocked": True,
                    "details": {"findings": requirement_gate.get("findings", [])[:10]},
                }
            )
        for key, reason_code in {
            "report_json_path": "requirement_clarity_report_missing",
            "report_markdown_path": "requirement_clarity_markdown_missing",
        }.items():
            rel = str(requirement_gate.get(key, "") or "")
            if rel and not (project_root / rel).exists():
                issues.append(
                    {
                        "reason_code": reason_code,
                        "severity": "critical",
                        "message": f"requirement clarity artifact missing: {rel}",
                        "blocked": True,
                    }
                )

    if bool(technical_gate.get("required")):
        if not technical_state:
            issues.append(
                {
                    "reason_code": "technical_review_state_missing",
                    "severity": "critical",
                    "message": f"technical review state missing for feature {feature_name}",
                    "blocked": True,
                }
            )
        if bool(technical_gate.get("blocked")):
            issues.append(
                {
                    "reason_code": str(technical_gate.get("reason_code") or "technical_review_contract_invalid"),
                    "severity": "critical",
                    "message": f"technical review gate blocked for feature {feature_name}",
                    "blocked": True,
                    "details": {
                        "validation": technical_gate.get("validation", {}),
                    },
                }
            )
        if str(technical_state.get("review_status") or "").strip().lower() not in {"approved", "accepted"}:
            issues.append(
                {
                    "reason_code": "technical_review_not_approved",
                    "severity": "critical",
                    "message": f"technical review contract not approved for feature {feature_name}",
                    "blocked": True,
                }
            )
    return issues


def check_v119_control_learning_contract(
    project_root: Path,
    mode: GateMode,
    stage: str,
    version: Optional[str] = None,
) -> List[Dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if stage != "release":
        return issues
    if mode not in {GateMode.STRICT, GateMode.DEBUG}:
        return issues
    resolved_version = _resolved_gate_version(project_root, version)
    if _parse_semver_tuple(resolved_version) != (1, 1, 9):
        return issues

    contract_run_id = _resolve_release_contract_run_id(project_root, version=resolved_version)
    control_plane = build_resume_contract(project_root, run_id=contract_run_id or None)
    if int(control_plane.get("failure_streak", 0) or 0) > 0:
        issues.append(
            {
                "reason_code": "control_plane_recovery_open",
                "severity": "critical",
                "message": (
                    "control plane still has an active failure streak "
                    f"(level={control_plane.get('escalation_level')}, stage={control_plane.get('last_failed_stage')})"
                ),
                "blocked": True,
            }
        )
    if int(control_plane.get("failure_streak", 0) or 0) > 0 and not str(control_plane.get("checkpoint_ref", "") or "").strip():
        issues.append(
            {
                "reason_code": "checkpoint_contract_missing",
                "severity": "critical",
                "message": "control plane escalation is active but no checkpoint/resume contract was recorded",
                "blocked": True,
            }
        )

    qa_status = load_qa_status(project_root)
    if not qa_status:
        issues.append(
            {
                "reason_code": "feature_qa_missing",
                "severity": "critical",
                "message": "v1.1.9 release requires canonical feature-aware QA status",
                "blocked": True,
            }
        )
        return issues

    if str(qa_status.get("status", "")).strip().lower() != "passed":
        issues.append(
            {
                "reason_code": "verify_not_passed",
                "severity": "critical",
                "message": f"qa status is {qa_status.get('status')}",
                "blocked": True,
            }
        )
    if not bool(qa_status.get("evidence_done", False)):
        issues.append(
            {
                "reason_code": "evidence_not_closed",
                "severity": "critical",
                "message": "qa status exists but evidence_done is false",
                "blocked": True,
            }
        )

    feature_name = str(qa_status.get("feature", "") or "").strip()
    if feature_name:
        obligations = load_artifact_update_obligations(project_root, feature=feature_name)
        open_items = [
            item
            for item in obligations.get("obligations", [])
            if isinstance(item, dict) and str(item.get("status", "open")).strip().lower() == "open"
        ]
        if open_items:
            issues.append(
                {
                    "reason_code": "artifact_updates_pending",
                    "severity": "critical",
                    "message": f"artifact writeback obligations still open: {[item.get('artifact') for item in open_items]}",
                    "blocked": True,
                }
            )
        exhaustiveness = load_exhaustiveness_report(project_root, feature=feature_name)
        if not exhaustiveness:
            issues.append(
                {
                    "reason_code": "story_exhaustiveness_missing",
                    "severity": "critical",
                    "message": "feature QA is present but no exhaustiveness report was recorded",
                    "blocked": True,
                }
            )
        else:
            score = float(exhaustiveness.get("score", 0.0) or 0.0)
            threshold = float(exhaustiveness.get("threshold", 0.8) or 0.8)
            if score < threshold:
                issues.append(
                    {
                        "reason_code": "story_exhaustiveness_below_threshold",
                        "severity": "critical",
                        "message": f"story exhaustiveness score {score} < {threshold}",
                        "blocked": True,
                    }
                )
            missing_axes = exhaustiveness.get("missing_axes") if isinstance(exhaustiveness.get("missing_axes"), list) else []
            if missing_axes:
                issues.append(
                    {
                        "reason_code": "required_scenario_family_missing",
                        "severity": "critical",
                        "message": f"story exhaustiveness missing axes: {missing_axes}",
                        "blocked": True,
                    }
                )
            missing_replay = exhaustiveness.get("missing_replay_scenarios") if isinstance(exhaustiveness.get("missing_replay_scenarios"), list) else []
            if missing_replay:
                issues.append(
                    {
                        "reason_code": "browser_replay_missing",
                        "severity": "critical",
                        "message": f"browser scenarios missing deterministic replay: {missing_replay[:10]}",
                        "blocked": True,
                    }
                )
            missing_browser_evidence = exhaustiveness.get("missing_browser_evidence_scenarios") if isinstance(exhaustiveness.get("missing_browser_evidence_scenarios"), list) else []
            if missing_browser_evidence:
                issues.append(
                    {
                        "reason_code": "browser_evidence_incomplete",
                        "severity": "critical",
                        "message": f"browser scenarios missing evidence pack: {missing_browser_evidence[:10]}",
                        "blocked": True,
                    }
                )

    learning_required = [
        project_root / ".beacon" / "state" / "learning" / "execution-baseline.json",
        project_root / ".beacon" / "state" / "eval-lab" / "benchmark-corpus.json",
    ]
    missing_learning = [str(path.relative_to(project_root)) for path in learning_required if not path.exists()]
    if missing_learning:
        issues.append(
            {
                "reason_code": "learning_input_missing",
                "severity": "critical",
                "message": f"learning plane artifacts missing: {missing_learning}",
                "blocked": True,
            }
        )
    return issues


def _candidate_matrix_paths(project_root: Path) -> list[Path]:
    root = project_root / "docs" / "beacon"
    if not root.exists():
        return []
    return sorted(
        list(root.glob("*/.machine/qa/*.ac-test-matrix.json"))
        + list(root.glob("*/qa/test-cases/*.ac-test-matrix.json"))
    )


def _candidate_qa9_matrix_paths(project_root: Path) -> list[Path]:
    root = project_root / "docs" / "beacon"
    if not root.exists():
        return []
    return sorted(
        list(root.glob("*/.machine/qa/*.qa9-matrix.json"))
        + list(root.glob("*/qa/test-cases/*.qa9-matrix.json"))
    )


def _is_non_empty_text(value: Any) -> bool:
    return bool(str(value or "").strip())


def _parse_iso_datetime(raw: Any) -> Optional[datetime]:
    text = str(raw or "").strip()
    if not text:
        return None
    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except Exception:  # noqa: BLE001
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _normalize_pair_list(raw_pairs: Any) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if not isinstance(raw_pairs, list):
        return pairs
    seen: set[tuple[str, str]] = set()
    for item in raw_pairs:
        if not isinstance(item, dict):
            continue
        browser = str(item.get("browser") or "").strip().lower()
        device = str(item.get("device") or "").strip().lower()
        if not browser or not device:
            continue
        key = (browser, device)
        if key in seen:
            continue
        seen.add(key)
        pairs.append(key)
    return pairs


def _load_qa9_matrix(path: Path) -> tuple[Optional[Dict[str, Any]], str]:
    if not path.exists():
        return None, "missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None, "invalid_json"
    if not isinstance(payload, dict):
        return None, "invalid_schema"
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return None, "invalid_schema"
    return payload, "ok"


def check_qa9_policy(
    project_root: Path,
    mode: GateMode,
    stage: str,
    *,
    qa_policy: str = "legacy",
    min_automation_rate: float = 0.85,
    require_qa_types: Optional[List[str]] = None,
    require_compat_matrix: bool = False,
) -> List[Dict[str, Any]]:
    """Run QA9-specific strict checks."""
    issues: list[dict[str, Any]] = []
    if stage not in {"test-case", "release"}:
        return issues
    if mode not in {GateMode.STRICT, GateMode.DEBUG}:
        return issues
    if not str(qa_policy or "").strip().lower().startswith("qa9"):
        return issues

    required_types = parse_qa_types(require_qa_types, profile="web-full")
    qa9_paths = _candidate_qa9_matrix_paths(project_root)
    if not qa9_paths:
        issues.append(
            {
                "reason_code": "qa9_matrix_missing",
                "severity": "critical",
                "message": "QA9 matrix missing (*.qa9-matrix.json)",
                "blocked": True,
            }
        )
        return issues

    matrix_path = qa9_paths[0]
    matrix_payload, load_status = _load_qa9_matrix(matrix_path)
    if matrix_payload is None:
        issues.append(
            {
                "reason_code": "qa9_matrix_schema_invalid",
                "severity": "critical",
                "message": f"QA9 matrix invalid: {matrix_path} ({load_status})",
                "blocked": True,
            }
        )
        return issues

    qa_types = matrix_payload.get("qa_types")
    if not isinstance(qa_types, list):
        qa_types = []
    matrix_types = {str(x).strip() for x in qa_types if str(x).strip()}
    missing_types = [x for x in required_types if x not in matrix_types]
    if missing_types:
        issues.append(
            {
                "reason_code": "qa9_required_type_missing",
                "severity": "critical",
                "message": f"QA9 required types missing: {missing_types}",
                "blocked": True,
            }
        )

    llm_plan = matrix_payload.get("llm_plan")
    if not isinstance(llm_plan, dict):
        issues.append(
            {
                "reason_code": "qa_llm_plan_missing",
                "severity": "critical",
                "message": "qa9 matrix llm_plan missing",
                "blocked": True,
            }
        )
    else:
        if not _is_non_empty_text(llm_plan.get("mode")) or not _is_non_empty_text(llm_plan.get("model")):
            issues.append(
                {
                    "reason_code": "qa_llm_plan_invalid",
                    "severity": "critical",
                    "message": "qa9 matrix llm_plan.mode/model invalid",
                    "blocked": True,
                }
            )
        project_scan = llm_plan.get("project_scan")
        if not isinstance(project_scan, dict):
            issues.append(
                {
                    "reason_code": "qa_llm_project_scan_missing",
                    "severity": "critical",
                    "message": "qa9 matrix llm_plan.project_scan missing",
                    "blocked": True,
                }
            )
        if str(llm_plan.get("mode", "")).strip().lower() == "disabled" and not _is_non_empty_text(
            llm_plan.get("skip_reason")
        ):
            issues.append(
                {
                    "reason_code": "qa_llm_skip_without_rationale",
                    "severity": "critical",
                    "message": "llm mode disabled but skip_reason missing",
                    "blocked": True,
                }
            )

    qa_requirements = matrix_payload.get("qa_requirements")
    if not isinstance(qa_requirements, list):
        issues.append(
            {
                "reason_code": "qa9_matrix_schema_invalid",
                "severity": "critical",
                "message": "qa_requirements missing or invalid",
                "blocked": True,
            }
        )
        qa_requirements = []

    for req in qa_requirements:
        if not isinstance(req, dict):
            continue
        applicability = str(req.get("applicability", "")).strip().lower()
        qa_type = str(req.get("qa_type", "")).strip()
        waiver = req.get("waiver")
        if applicability == "na":
            if not isinstance(waiver, dict):
                issues.append(
                    {
                        "reason_code": "qa9_waiver_missing_approval",
                        "severity": "critical",
                        "message": f"qa_type={qa_type} applicability=na but waiver missing",
                        "blocked": True,
                    }
                )
                continue
            approved_by = str(waiver.get("approved_by", "")).strip()
            if not approved_by:
                issues.append(
                    {
                        "reason_code": "manual_waiver_unapproved",
                        "severity": "critical",
                        "message": f"qa_type={qa_type} waiver approved_by missing",
                        "blocked": True,
                    }
                )
            expires_at = str(waiver.get("expires_at", "")).strip()
            parsed_expiry = _parse_iso_datetime(expires_at)
            if not parsed_expiry:
                issues.append(
                    {
                        "reason_code": "qa9_waiver_missing_approval",
                        "severity": "critical",
                        "message": f"qa_type={qa_type} waiver expires_at missing/invalid",
                        "blocked": True,
                    }
                )
            else:
                now_utc = datetime.now(timezone.utc)
                if parsed_expiry < now_utc:
                    issues.append(
                        {
                            "reason_code": "manual_waiver_unapproved",
                            "severity": "critical",
                            "message": f"qa_type={qa_type} waiver expired at {expires_at}",
                            "blocked": True,
                        }
                    )

    entries = matrix_payload.get("entries")
    if not isinstance(entries, list) or not entries:
        issues.append(
            {
                "reason_code": "qa9_matrix_schema_invalid",
                "severity": "critical",
                "message": "qa9 matrix entries missing/empty",
                "blocked": True,
            }
        )
        return issues

    auto_total = 0
    auto_with_command = 0
    missing_traceability: list[str] = []
    missing_contract = True
    missing_integration = True
    missing_compat = True
    for item in entries:
        if not isinstance(item, dict):
            continue
        tc_id = str(item.get("tc_id") or "").strip() or "unknown"
        ac_id = str(item.get("ac_id") or "").strip()
        qa_type = str(item.get("qa_type") or item.get("layer") or "").strip()
        if not ac_id:
            missing_traceability.append(tc_id)
        if qa_type == "contract":
            missing_contract = False
        if qa_type == "integration":
            missing_integration = False
        if qa_type == "compatibility":
            missing_compat = False
        automation = str(item.get("automation") or "auto").strip().lower()
        if automation in {"auto", "hybrid"}:
            auto_total += 1
            if _is_non_empty_text(item.get("command")):
                auto_with_command += 1
            else:
                issues.append(
                    {
                        "reason_code": "qa9_command_missing_auto_case",
                        "severity": "critical",
                        "message": f"auto case missing command: {tc_id}",
                        "blocked": True,
                    }
                )

    if missing_traceability:
        issues.append(
            {
                "reason_code": "qa9_ac_traceability_broken",
                "severity": "critical",
                "message": f"qa9 entries missing ac_id: {missing_traceability[:20]}",
                "blocked": True,
            }
        )

    if "contract" in required_types and missing_contract:
        issues.append(
            {
                "reason_code": "contract_spec_missing",
                "severity": "critical",
                "message": "required contract test entries missing",
                "blocked": True,
            }
        )
    if "integration" in required_types and missing_integration:
        issues.append(
            {
                "reason_code": "integration_execution_missing",
                "severity": "critical",
                "message": "required integration test entries missing",
                "blocked": True,
            }
        )
    if ("compatibility" in required_types or require_compat_matrix) and missing_compat:
        issues.append(
            {
                "reason_code": "compatibility_execution_missing",
                "severity": "critical",
                "message": "required compatibility test entries missing",
                "blocked": True,
            }
        )

    automation_rate = float(auto_with_command) / float(auto_total or 1)
    if auto_total > 0 and automation_rate < float(min_automation_rate):
        issues.append(
            {
                "reason_code": "qa9_automation_rate_below_target",
                "severity": "critical",
                "message": f"automation_rate={round(automation_rate, 4)} < {min_automation_rate}",
                "blocked": True,
                "details": {
                    "auto_total": auto_total,
                    "auto_with_command": auto_with_command,
                },
            }
        )

    if require_compat_matrix:
        compatibility = matrix_payload.get("compatibility_matrix")
        if not isinstance(compatibility, dict):
            issues.append(
                {
                    "reason_code": "compatibility_matrix_missing",
                    "severity": "critical",
                    "message": "compatibility_matrix missing",
                    "blocked": True,
                }
            )
        else:
            browsers = compatibility.get("browsers")
            devices = compatibility.get("devices")
            pairs = compatibility.get("required_pairs")
            if not isinstance(browsers, list) or not browsers or not isinstance(devices, list) or not devices:
                issues.append(
                    {
                        "reason_code": "compatibility_axis_incomplete",
                        "severity": "critical",
                        "message": "compatibility browsers/devices incomplete",
                        "blocked": True,
                    }
                )
            if not isinstance(pairs, list) or not pairs:
                issues.append(
                    {
                        "reason_code": "compatibility_axis_incomplete",
                        "severity": "critical",
                        "message": "compatibility required_pairs missing",
                        "blocked": True,
                    }
                )

    status_path = project_root / ".beacon" / "auto-test-status.json"
    if not status_path.exists():
        issues.append(
            {
                "reason_code": "test_execution_missing",
                "severity": "critical",
                "message": "auto-test status missing for qa9 checks",
                "blocked": True,
            }
        )
        return issues

    try:
        status_data = json.loads(status_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        status_data = {}

    quality_issues = status_data.get("quality_issues")
    if isinstance(quality_issues, list):
        for item in quality_issues:
            if not isinstance(item, dict):
                continue
            reason_code = str(item.get("reason_code", "")).strip()
            if reason_code in {
                "assertion_count_zero_pass",
                "junit_missing_or_invalid",
                "evidence_replay_detected",
                "flaky_rate_exceeded",
                "qa9_command_missing_auto_case",
            }:
                issues.append(
                    {
                        "reason_code": reason_code,
                        "severity": "critical",
                        "message": str(item.get("message", reason_code)),
                        "blocked": True,
                    }
                )

    execution = status_data.get("execution")
    layers = execution.get("layers") if isinstance(execution, dict) else None
    passed_layer_names: set[str] = set()
    fingerprints: list[str] = []
    if isinstance(layers, list):
        for layer in layers:
            if not isinstance(layer, dict):
                continue
            if str(layer.get("status", "")).lower() != "passed":
                continue
            layer_name = str(layer.get("layer", "")).strip()
            if layer_name:
                passed_layer_names.add(layer_name)
            fingerprint = str(layer.get("execution_fingerprint", "")).strip()
            if not _is_non_empty_text(fingerprint):
                issues.append(
                    {
                        "reason_code": "execution_fingerprint_missing",
                        "severity": "critical",
                        "message": f"layer {layer.get('layer')} missing execution_fingerprint",
                        "blocked": True,
                    }
                )
            else:
                fingerprints.append(fingerprint)
            started_at = str(layer.get("started_at", "")).strip()
            ended_at = str(layer.get("ended_at", "")).strip()
            if not started_at or not ended_at:
                issues.append(
                    {
                        "reason_code": "evidence_timestamp_out_of_window",
                        "severity": "critical",
                        "message": f"layer {layer.get('layer')} missing started_at/ended_at",
                        "blocked": True,
                    }
                )

    if fingerprints and len(set(fingerprints)) != len(fingerprints):
        issues.append(
            {
                "reason_code": "execution_fingerprint_mismatch",
                "severity": "critical",
                "message": "duplicate execution fingerprints detected across passed layers",
                "blocked": True,
            }
        )

    if isinstance(layers, list) and layers:
        has_failed = any(str(x.get("status", "")).lower() in {"failed", "blocked"} for x in layers if isinstance(x, dict))
        quality_reason_codes = {
            str(item.get("reason_code", "")).strip()
            for item in quality_issues
            if isinstance(item, dict)
        } if isinstance(quality_issues, list) else set()
        has_quality_failure = bool(quality_reason_codes)
        qa9_status_block = status_data.get("qa9")
        qa9_summary = qa9_status_block.get("summary") if isinstance(qa9_status_block, dict) else {}
        if isinstance(qa9_summary, dict):
            if int(qa9_summary.get("failed", 0) or 0) > 0 or int(qa9_summary.get("blocked", 0) or 0) > 0:
                has_quality_failure = True
        expected_status = "failed" if (has_failed or has_quality_failure) else "passed"
        reported_status = str(status_data.get("status", "")).strip().lower()
        if reported_status in {"passed", "failed", "blocked"} and reported_status != expected_status:
            issues.append(
                {
                    "reason_code": "report_result_mismatch",
                    "severity": "critical",
                    "message": f"auto-test status={reported_status} but computed={expected_status}",
                    "blocked": True,
                }
            )

    if "contract" in required_types and "contract" not in passed_layer_names:
        issues.append(
            {
                "reason_code": "contract_verification_missing",
                "severity": "critical",
                "message": "contract layer not executed/passed in auto-test status",
                "blocked": True,
            }
        )
    if "integration" in required_types and "integration" not in passed_layer_names:
        issues.append(
            {
                "reason_code": "integration_env_missing",
                "severity": "critical",
                "message": "integration layer not executed/passed (env/command missing)",
                "blocked": True,
            }
        )
    if ("compatibility" in required_types or require_compat_matrix) and "compatibility" not in passed_layer_names:
        issues.append(
            {
                "reason_code": "compatibility_execution_missing",
                "severity": "critical",
                "message": "compatibility layer not executed/passed in auto-test status",
                "blocked": True,
            }
        )

    if require_compat_matrix:
        required_pairs: list[tuple[str, str]] = []
        compatibility = matrix_payload.get("compatibility_matrix")
        if isinstance(compatibility, dict):
            required_pairs = _normalize_pair_list(compatibility.get("required_pairs"))
        qa9_status = status_data.get("qa9")
        compatibility_status = qa9_status.get("compatibility") if isinstance(qa9_status, dict) else {}
        executed_pairs = _normalize_pair_list(
            compatibility_status.get("executed_pairs") if isinstance(compatibility_status, dict) else None
        )
        if required_pairs:
            missing_pairs = sorted(set(required_pairs) - set(executed_pairs))
            if missing_pairs:
                issues.append(
                    {
                        "reason_code": "compatibility_execution_missing",
                        "severity": "critical",
                        "message": f"compatibility required_pairs missing execution evidence: {missing_pairs[:10]}",
                        "blocked": True,
                    }
                )

    matrix_report = execution.get("matrix_report") if isinstance(execution, dict) else None
    if isinstance(matrix_report, dict) and matrix_report.get("status") == "freshness_violation":
        issues.append(
            {
                "reason_code": "evidence_replay_detected",
                "severity": "critical",
                "message": "matrix evidence freshness violation",
                "blocked": True,
            }
        )

    return issues


def check_test_execution_integrity(project_root: Path, mode: GateMode, stage: str) -> List[Dict[str, Any]]:
    """Check execution integrity for test-case/release stage."""
    issues: list[dict[str, Any]] = []
    if stage not in {"test-case", "release"}:
        return issues
    if mode not in {GateMode.STRICT, GateMode.DEBUG}:
        return issues

    status_path = project_root / ".beacon" / "auto-test-status.json"
    if not status_path.exists():
        issues.append(
            {
                "reason_code": "test_execution_missing",
                "severity": "critical",
                "message": "auto-test status artifact missing (.beacon/auto-test-status.json)",
                "blocked": True,
            }
        )
        return issues

    try:
        status_data = json.loads(status_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        issues.append(
            {
                "reason_code": "test_execution_missing",
                "severity": "critical",
                "message": "auto-test status artifact is invalid JSON",
                "blocked": True,
            }
        )
        return issues

    execution = status_data.get("execution")
    layers = execution.get("layers") if isinstance(execution, dict) else None
    run_id = str(execution.get("run_id", "")).strip() if isinstance(execution, dict) else ""
    signature_chain_path = project_root / ".beacon" / "evidence-signature-chain.json"
    if not signature_chain_path.exists():
        issues.append(
            {
                "reason_code": "evidence_integrity_missing",
                "severity": "critical",
                "message": "evidence signature chain missing (.beacon/evidence-signature-chain.json)",
                "blocked": True,
            }
        )
    else:
        try:
            signature_payload = json.loads(signature_chain_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            signature_payload = []
        entries = signature_payload if isinstance(signature_payload, list) else []
        matched = None
        for item in reversed(entries):
            if not isinstance(item, dict):
                continue
            if str(item.get("run_id", "")).strip() == run_id:
                matched = item
                break
        if matched is None:
            issues.append(
                {
                    "reason_code": "evidence_integrity_missing",
                    "severity": "critical",
                    "message": f"signature chain does not contain run_id={run_id}",
                    "blocked": True,
                }
            )
        else:
            summary_rel = str(matched.get("summary_path", "")).strip()
            summary_sha = str(matched.get("summary_sha256", "")).strip()
            if summary_rel and summary_sha:
                summary_path = project_root / summary_rel
                if summary_path.exists():
                    actual_sha = hashlib.sha256(summary_path.read_bytes()).hexdigest()
                    if actual_sha != summary_sha:
                        issues.append(
                            {
                                "reason_code": "evidence_sha256_manifest_mismatch",
                                "severity": "critical",
                                "message": "summary hash mismatch against signature chain",
                                "blocked": True,
                            }
                        )

    if not isinstance(layers, list) or not layers:
        issues.append(
            {
                "reason_code": "test_execution_missing",
                "severity": "critical",
                "message": "no execution layers found in auto-test status",
                "blocked": True,
            }
        )
        return issues

    not_executed = [
        item.get("layer")
        for item in layers
        if str(item.get("status", "")).lower() in {"not_executed", "skipped"}
    ]
    if not_executed:
        issues.append(
            {
                "reason_code": "test_execution_missing",
                "severity": "critical",
                "message": f"some selected test layers were not executed: {not_executed}",
                "blocked": True,
            }
        )

    key_guard = status_data.get("key_action_guard")
    if isinstance(key_guard, dict) and key_guard.get("required"):
        missing_actions = key_guard.get("missing_actions")
        if isinstance(missing_actions, list) and missing_actions:
            issues.append(
                {
                    "reason_code": "test_key_actions_missing",
                    "severity": "critical",
                    "message": f"missing required UI key action evidence: {missing_actions}",
                    "blocked": True,
                }
            )

    matrix_path = None
    matrix_report = execution.get("matrix_report") if isinstance(execution, dict) else None
    if isinstance(matrix_report, dict) and matrix_report.get("matrix_path"):
        candidate = Path(str(matrix_report.get("matrix_path")))
        matrix_path = candidate if candidate.is_absolute() else project_root / candidate
    if matrix_path is None:
        candidates = _candidate_matrix_paths(project_root)
        matrix_path = candidates[0] if candidates else None

    if matrix_path is None or not matrix_path.exists():
        issues.append(
            {
                "reason_code": "ac_tc_evidence_chain_broken",
                "severity": "critical",
                "message": "AC/TC executable matrix is missing",
                "blocked": True,
            }
        )
        return issues

    try:
        matrix_data = json.loads(matrix_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        issues.append(
            {
                "reason_code": "ac_tc_evidence_chain_broken",
                "severity": "critical",
                "message": f"matrix JSON invalid: {matrix_path}",
                "blocked": True,
            }
        )
        return issues

    entries = matrix_data.get("entries")
    if not isinstance(entries, list) or not entries:
        issues.append(
            {
                "reason_code": "ac_tc_evidence_chain_broken",
                "severity": "critical",
                "message": f"matrix entries missing/empty: {matrix_path}",
                "blocked": True,
            }
        )
        return issues

    required_fields = {"ac_id", "tc_id", "layer", "evidence_path"}
    malformed = [
        idx + 1 for idx, item in enumerate(entries)
        if not isinstance(item, dict) or not required_fields.issubset(set(item.keys()))
    ]
    if malformed:
        issues.append(
            {
                "reason_code": "ac_tc_evidence_chain_broken",
                "severity": "critical",
                "message": f"matrix entries malformed: {malformed[:10]}",
                "blocked": True,
            }
        )
        return issues

    executed_layers = {
        normalize_qa_type(str(item.get("layer")))
        for item in layers
        if str(item.get("status")) == "passed"
    }

    def _resolve_evidence_path(raw_path: str, current_run_id: str) -> str:
        value = str(raw_path or "").strip()
        if not value:
            return value
        if current_run_id:
            value = value.replace("{run_id}", current_run_id)
            value = value.replace("$RUN_ID", current_run_id)
            value = value.replace("__RUN_ID__", current_run_id)
        return value

    execution_run_id = str(execution.get("run_id", "")).strip() if isinstance(execution, dict) else ""
    chain_broken = []
    for item in entries:
        layer = normalize_qa_type(str(item.get("layer")))
        if layer not in executed_layers:
            chain_broken.append(item.get("tc_id"))
            continue
        evidence = Path(_resolve_evidence_path(str(item.get("evidence_path")), execution_run_id))
        evidence_file = evidence if evidence.is_absolute() else project_root / evidence
        if not evidence_file.exists():
            chain_broken.append(item.get("tc_id"))
    if chain_broken:
        issues.append(
            {
                "reason_code": "ac_tc_evidence_chain_broken",
                "severity": "critical",
                "message": f"AC→TC→evidence chain broken for test cases: {chain_broken[:10]}",
                "blocked": True,
            }
        )

    return issues


def check_coverage_metrics(
    project_root: Path,
    mode: GateMode,
    stage: str,
    *,
    version: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Check story/ac/tc coverage metrics and block non-full coverage in strict/debug."""
    issues: list[dict[str, Any]] = []
    if stage not in {"test-case", "release"}:
        return issues
    if mode not in {GateMode.STRICT, GateMode.DEBUG}:
        return issues

    version = _resolved_gate_version(project_root, version)
    metrics = compute_coverage_metrics(project_root, version=version)
    if metrics.get("full_coverage"):
        return issues

    issues.append(
        {
            "reason_code": "coverage_incomplete",
            "severity": "critical",
            "message": (
                "coverage is incomplete: "
                f"story={metrics.get('implemented_story')}/{metrics.get('planned_story')}, "
                f"ac={metrics.get('tested_ac')}/{metrics.get('total_ac')}, "
                f"tc={metrics.get('executed_tc')}/{metrics.get('total_tc')}"
            ),
            "blocked": True,
            "details": metrics,
        }
    )
    return issues


def _parse_semver_tuple(value: str) -> tuple[int, int, int]:
    raw = str(value or "").strip().lower()
    if raw.startswith("v"):
        raw = raw[1:]
    parts = raw.split(".")
    numbers: list[int] = []
    for part in parts[:3]:
        digits = "".join(ch for ch in part if ch.isdigit())
        if not digits:
            numbers.append(0)
        else:
            numbers.append(int(digits))
    while len(numbers) < 3:
        numbers.append(0)
    return (numbers[0], numbers[1], numbers[2])


def _is_v110_consistency_enabled(project_root: Path, *, version: Optional[str]) -> tuple[bool, str]:
    resolved_version = _resolved_gate_version(project_root, version)
    baseline_latest = project_root / ".beacon" / "state" / "baselines" / resolved_version / "latest.json"
    fingerprint_latest = project_root / ".beacon" / "state" / "spec-fingerprints" / resolved_version / "latest.json"
    status_path = project_root / ".beacon" / "auto-test-status.json"
    has_status_fingerprint = False
    if status_path.exists():
        try:
            status_payload = json.loads(status_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            status_payload = {}
        if isinstance(status_payload, dict):
            execution = status_payload.get("execution")
            if isinstance(execution, dict):
                spec_fp = execution.get("spec_fingerprint")
                if isinstance(spec_fp, dict) and str(spec_fp.get("fingerprint_hash", "")).strip():
                    has_status_fingerprint = True
            if not has_status_fingerprint and str(status_payload.get("spec_fingerprint_hash", "")).strip():
                has_status_fingerprint = True

    if _parse_semver_tuple(resolved_version) < (1, 1, 0):
        return baseline_latest.exists() or fingerprint_latest.exists() or has_status_fingerprint, resolved_version

    return baseline_latest.exists() or fingerprint_latest.exists() or has_status_fingerprint, resolved_version


def check_spec_consistency(
    project_root: Path,
    mode: GateMode,
    stage: str,
    *,
    version: Optional[str] = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    enabled, resolved_version = _is_v110_consistency_enabled(project_root, version=version)
    verdict: dict[str, Any] = {
        "enabled": enabled,
        "version": resolved_version,
        "status": "not_applicable",
        "baseline_present": False,
        "baseline_id": "",
        "expected_spec_fingerprint": "",
        "actual_spec_fingerprint": "",
        "reason_codes": [],
    }
    if stage not in {"test-case", "release"}:
        return issues, verdict
    if mode not in {GateMode.STRICT, GateMode.DEBUG}:
        return issues, verdict
    if not enabled:
        return issues, verdict

    verdict["status"] = "pass"
    contract_run_id = _resolve_release_contract_run_id(project_root, version=resolved_version)
    baseline = _load_run_scoped_baseline(project_root, version=resolved_version, run_id=contract_run_id)
    if not baseline:
        baseline = load_latest_baseline_snapshot(project_root, version=resolved_version)
    fingerprint = _load_run_scoped_spec_fingerprint(project_root, version=resolved_version, run_id=contract_run_id)
    if not fingerprint:
        fingerprint = load_latest_spec_fingerprint(project_root, version=resolved_version)
    expected_hash = str(fingerprint.get("fingerprint_hash", "")).strip()
    verdict["expected_spec_fingerprint"] = expected_hash

    if baseline:
        verdict["baseline_present"] = True
        verdict["baseline_id"] = str(baseline.get("baseline_id", "") or "")
        baseline_fp = baseline.get("spec_fingerprint")
        if isinstance(baseline_fp, dict):
            baseline_hash = str(baseline_fp.get("fingerprint_hash", "") or "").strip()
            if baseline_hash and not expected_hash:
                expected_hash = baseline_hash
                verdict["expected_spec_fingerprint"] = baseline_hash
    else:
        missing_baseline_blocked = mode == GateMode.STRICT
        issues.append(
            {
                "reason_code": "baseline_snapshot_missing",
                "severity": "critical" if missing_baseline_blocked else "warning",
                "message": f"baseline snapshot missing for version={resolved_version}",
                "blocked": missing_baseline_blocked,
            }
        )

    baseline_root = project_root / ".beacon" / "state" / "baselines" / resolved_version
    baseline_run_id = str(baseline.get("run_id", "") or "").strip()
    baseline_pattern = f"bl-{baseline_run_id}-*.json" if baseline_run_id else "*.json"
    baseline_files = sorted(
        [
            p
            for p in baseline_root.glob(baseline_pattern)
            if p.is_file() and p.name != "latest.json"
        ]
    )
    if len(baseline_files) >= 2:
        baseline_id = str(baseline.get("baseline_id", "") or "")
        revision_of = str(baseline.get("revision_of", "") or "")
        if baseline_id and not revision_of:
            issues.append(
                {
                    "reason_code": "baseline_revision_broken",
                    "severity": "critical",
                    "message": f"baseline {baseline_id} missing revision_of chain",
                    "blocked": True,
                }
            )

    status_path = project_root / ".beacon" / "auto-test-status.json"
    status_data: dict[str, Any] = {}
    if status_path.exists():
        try:
            loaded = json.loads(status_path.read_text(encoding="utf-8"))
            status_data = loaded if isinstance(loaded, dict) else {}
        except Exception:  # noqa: BLE001
            status_data = {}
    execution = status_data.get("execution")
    actual_hash = ""
    if isinstance(execution, dict):
        spec_fp = execution.get("spec_fingerprint")
        if isinstance(spec_fp, dict):
            actual_hash = str(spec_fp.get("fingerprint_hash", "") or "").strip()
    if not actual_hash:
        actual_hash = str(status_data.get("spec_fingerprint_hash", "") or "").strip()
    verdict["actual_spec_fingerprint"] = actual_hash

    if expected_hash and actual_hash and expected_hash != actual_hash:
        issues.append(
            {
                "reason_code": "spec_impl_drift_detected",
                "severity": "critical",
                "message": (
                    "spec fingerprint mismatch between docs and execution evidence "
                    f"(expected={expected_hash[:12]}, actual={actual_hash[:12]})"
                ),
                "blocked": True,
            }
        )
    elif expected_hash and not actual_hash:
        issues.append(
            {
                "reason_code": "spec_impl_drift_detected",
                "severity": "critical",
                "message": "execution evidence missing spec fingerprint hash",
                "blocked": True,
            }
        )

    reason_codes = [str(item.get("reason_code", "")).strip() for item in issues if isinstance(item, dict)]
    reason_codes = [code for code in reason_codes if code]
    verdict["reason_codes"] = reason_codes
    if any(bool(item.get("blocked")) for item in issues):
        verdict["status"] = "blocked"
    elif issues:
        verdict["status"] = "warn"
    else:
        verdict["status"] = "pass"
    return issues, verdict


def run_gate_checks(
    stage: str,
    mode: GateMode,
    project_root: Path,
    force: bool = False,
    config: Optional[Dict[str, Any]] = None,
    qa_policy: str = "legacy",
    min_automation_rate: float = 0.85,
    require_qa_types: Optional[list[str]] = None,
    require_compat_matrix: bool = False,
    version: Optional[str] = None,
    profile: str = "auto",
) -> Dict[str, Any]:
    """Run all gate checks for a stage"""
    all_issues = []
    gate_config = config or load_gate_config(project_root)
    scope_guard_enabled = bool(gate_config.get("scope_guard_enabled", True))
    requested_mode = mode
    dry_run_effective = requested_mode == GateMode.DRY_RUN
    resolved_profile = resolve_gate_profile(stage, profile)

    if dry_run_effective:
        typer.echo("[DRY-RUN] Running checks without blocking...")
        mode = GateMode.DEBUG  # Use debug mode for dry-run

    run_stage_local = resolved_profile in {GateProfile.STAGE_LOCAL, GateProfile.RELEASE_GLOBAL}
    run_release_global = resolved_profile == GateProfile.RELEASE_GLOBAL

    if run_stage_local:
        if mode == GateMode.DEBUG:
            typer.echo("[DEBUG] [stage-local] Checking boundaries...")
        all_issues.extend(check_boundaries(project_root, mode, version))

        if (mode == GateMode.STRICT or mode == GateMode.DEBUG) and scope_guard_enabled:
            if mode == GateMode.DEBUG:
                typer.echo("[DEBUG] [stage-local] Checking scope guard...")
            all_issues.extend(check_scope_guard(project_root, mode))

        if mode == GateMode.STRICT or mode == GateMode.DEBUG:
            if mode == GateMode.DEBUG:
                typer.echo("[DEBUG] [stage-local] Checking test execution integrity...")
            all_issues.extend(check_test_execution_integrity(project_root, mode, stage))
            all_issues.extend(check_prototype_contract(project_root, mode, stage, version))
            if mode == GateMode.DEBUG:
                typer.echo("[DEBUG] [stage-local] Checking coverage metrics...")
            all_issues.extend(check_coverage_metrics(project_root, mode, stage, version=version))
            if mode == GateMode.DEBUG:
                typer.echo("[DEBUG] [stage-local] Checking QA9 policy...")
            all_issues.extend(
                check_qa9_policy(
                    project_root,
                    mode,
                    stage,
                    qa_policy=qa_policy,
                    min_automation_rate=min_automation_rate,
                    require_qa_types=require_qa_types or list(QA9_TYPES),
                    require_compat_matrix=require_compat_matrix,
                )
            )

    doc_impl_verdict: dict[str, Any] = {
        "enabled": False,
        "status": "not_applicable",
        "reason_codes": [],
    }

    if run_release_global:
        if mode == GateMode.DEBUG:
            typer.echo("[DEBUG] [release-global] Checking terminal artifact...")
        all_issues.extend(check_terminal_artifact(project_root, mode, version))

        if mode == GateMode.DEBUG:
            typer.echo("[DEBUG] [release-global] Checking evidence chain...")
        all_issues.extend(check_evidence_chain(project_root, mode))

        if mode == GateMode.DEBUG:
            typer.echo("[DEBUG] [release-global] Checking delivery execution artifacts...")
        all_issues.extend(check_delivery_execution_artifacts(project_root, mode, stage, version))
        all_issues.extend(check_formal_version_package_closure(project_root, mode, stage, version))
        all_issues.extend(check_v119_control_learning_contract(project_root, mode, stage, version))
        all_issues.extend(check_v112_implementation_plan_contract(project_root, mode, stage, version))
        all_issues.extend(check_v131_human_loop_contract(project_root, mode, stage, version))
        all_issues.extend(check_v110_precision_contract(project_root, mode, stage, version))
        all_issues.extend(check_prototype_contract(project_root, mode, stage, version))

        if mode == GateMode.STRICT or mode == GateMode.DEBUG:
            if mode == GateMode.DEBUG:
                typer.echo("[DEBUG] [release-global] Checking memory closure...")
            all_issues.extend(check_memory_closure(project_root, mode, stage, version))
            if mode == GateMode.DEBUG:
                typer.echo("[DEBUG] [release-global] Checking release memory profile...")
            all_issues.extend(check_release_memory_profile(project_root, mode, stage, version))
            if mode == GateMode.DEBUG:
                typer.echo("[DEBUG] [release-global] Checking spec-doc consistency...")
            consistency_issues, doc_impl_verdict = check_spec_consistency(
                project_root,
                mode,
                stage,
                version=version,
            )
            all_issues.extend(consistency_issues)

    # Determine blocked status
    blocked_issues = [i for i in all_issues if i.get("blocked", False)]
    is_blocked = len(blocked_issues) > 0

    if dry_run_effective:
        # dry-run semantics: never block pipeline, always exit 0.
        is_blocked = False

    # Handle force mode
    if is_blocked and force:
        is_blocked = False
        # Log risk
        risk_log_path = project_root / ".beacon" / "risks.json"
        risks = []
        if risk_log_path.exists():
            risks = json.loads(risk_log_path.read_text())
        risks.append({
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "mode": mode.value,
            "issues": blocked_issues,
        })
        risk_log_path.parent.mkdir(parents=True, exist_ok=True)
        risk_log_path.write_text(json.dumps(risks, indent=2, ensure_ascii=False))

    if dry_run_effective:
        status = "Pass"
    else:
        status = "Blocked" if is_blocked else ("Warn" if all_issues else "Pass")
    return {
        "stage": stage,
        "mode": requested_mode.value,
        "profile": resolved_profile.value,
        "status": status,
        "issues": all_issues,
        "doc_impl_verdict": doc_impl_verdict,
        "blocked_count": len(blocked_issues),
        "force": force,
        "dry_run": dry_run_effective,
    }


def _run_check_command(
    stage: str,
    strict: bool = False,
    mode: Optional[str] = None,
    profile: str = "auto",
    json_output: bool = False,
    force: bool = False,
    project_root: str = "",
    qa_policy: str = "legacy",
    min_automation_rate: float = 0.85,
    require_qa_types: Optional[list[str]] = None,
    require_compat_matrix: bool = False,
    version: Optional[str] = None,
) -> int:
    """Shared gate check execution."""
    root = Path(project_root) if project_root else Path.cwd()
    try:
        gate_mode, _ = resolve_gate_mode(strict=strict, mode=mode, project_root=root)
    except ValueError as exc:
        typer.echo(f"Error: {exc}")
        return 1

    if not json_output:
        if gate_mode == GateMode.DEBUG:
            typer.echo(f"[DEBUG] Gate Check: {stage}")
            typer.echo(f"[DEBUG] Mode: {gate_mode.value}")
        else:
            typer.echo(f"Gate Check: {stage}")
            typer.echo(f"Mode: {gate_mode.value.upper()}")
            try:
                resolved_profile = resolve_gate_profile(stage, profile)
                typer.echo(f"Profile: {resolved_profile.value.upper()}")
            except ValueError as exc:
                typer.echo(f"Error: {exc}")
                return 1

    try:
        result = run_gate_checks(
            stage,
            gate_mode,
            root,
            force,
            qa_policy=qa_policy,
            min_automation_rate=min_automation_rate,
            require_qa_types=require_qa_types,
            require_compat_matrix=require_compat_matrix,
            version=version,
            profile=profile,
        )
    except ValueError as exc:
        typer.echo(f"Error: {exc}")
        return 1
    if json_output:
        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result["status"] == "Blocked":
            typer.echo(f"Status: {typer.style('BLOCKED', fg=typer.colors.RED)}")
            typer.echo(f"Issues found: {result['blocked_count']}")
            for issue in result["issues"]:
                if issue.get("blocked"):
                    typer.echo(f"  - {issue['reason_code']}: {issue['message']}")
        else:
            is_warn = result["status"] == "Warn"
            if force:
                status_color = typer.colors.YELLOW
            else:
                status_color = typer.colors.YELLOW if is_warn else typer.colors.GREEN
            status_text = ("WARN" if is_warn else "PASS") + (" (forced)" if force else "")
            if result.get("dry_run"):
                status_text += " (dry-run)"
            typer.echo(f"Status: {typer.style(status_text, fg=status_color)}")
            if result.get("dry_run") and result.get("blocked_count", 0):
                typer.echo(f"Dry-run detected {result['blocked_count']} would-block issues.")

        if result["issues"] and (not result["blocked_count"] or result.get("dry_run")):
            typer.echo(f"Warnings: {len(result['issues'])}")
            for issue in result["issues"]:
                typer.echo(f"  - {issue['reason_code']}: {issue['message']}")

    if is_debug_mode_enabled(root):
        blocked = result["status"] == "Blocked"
        reason_codes = [
            str(item.get("reason_code", "")).strip()
            for item in result.get("issues", [])
            if isinstance(item, dict)
        ]
        reason_codes = [code for code in reason_codes if code]
        block_reason = ",".join(reason_codes[:5]) if blocked else ""
        try:
            debug_run_id, debug_path, debug_event = append_debug_feedback_event(
                root,
                source="gate.check",
                goal=f"gate:{stage}",
                intent="gate",
                confidence=1.0 if not blocked else 0.55,
                boundary_state="in_scope",
                block_reason=block_reason,
                recommended_command=f"beacon gate check {stage} --project-root {root}",
                executed=True,
                exit_code=2 if blocked else 0,
                note=result["status"].lower(),
                extra={
                    "mode": gate_mode.value,
                    "profile": profile,
                    "doc_impl_verdict": result.get("doc_impl_verdict", {}),
                },
            )
            append_debug_event_memory(
                root,
                run_id=debug_run_id,
                event_payload=debug_event,
                evidence_path=debug_path,
                source="debug.gate.check",
            )
        except Exception:
            pass

    return 2 if result["status"] == "Blocked" else 0


@app.command("list")
def list_checks(
    project_root: Optional[str] = typer.Option("", "--project-root", "-p", help="Project root path"),
):
    """List all gate checks"""
    typer.echo("Available Gate Checks:")
    typer.echo("")
    typer.echo("Workflow Stages:")
    for stage in GATE_STAGES:
        typer.echo(f"  - {stage}")
    typer.echo("  - prototype")
    typer.echo("")
    typer.echo("Gate Modes:")
    for mode in GateMode:
        typer.echo(f"  - {mode.value}")
    typer.echo("")
    typer.echo("Gate Profiles:")
    for profile in GateProfile:
        typer.echo(f"  - {profile.value}")
    typer.echo("")
    typer.echo(f"Reason Codes ({len(REASON_CODES)} total):")
    for code in REASON_CODES:
        typer.echo(f"  - {code}")


@app.command()
def check(
    stage: str = typer.Argument("think", help="Workflow stage: think/user-story/prd/prototype/test-case/release"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
    profile: str = typer.Option(
        "auto",
        "--profile",
        help="Gate profile: auto/stage-local/release-global.",
    ),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    force: bool = typer.Option(False, "--force", help="Force pass with risk logging"),
    team: str = typer.Option("", "--team", "-t", help="Team name"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    qa_policy: str = typer.Option("legacy", "--qa-policy", help="QA policy: legacy/qa9-core/qa9-strict"),
    min_automation_rate: float = typer.Option(
        0.85,
        "--min-automation-rate",
        help="Minimum automation coverage rate for QA9 policy.",
    ),
    require_qa_types: Optional[list[str]] = typer.Option(
        None,
        "--require-qa-types",
        help="Required QA types list (comma-separated or repeatable).",
    ),
    require_compat_matrix: bool = typer.Option(
        False,
        "--require-compat-matrix",
        help="Require compatibility matrix checks.",
    ),
    version: Optional[str] = typer.Option(
        None,
        "--version",
        "-v",
        help="Target docs version (default: resolve from env/latest)",
    ),
):
    """Run gate checks for workflow stages"""
    compat_required = bool(require_compat_matrix)
    if str(qa_policy or "").strip().lower() == "qa9-strict":
        compat_required = True
    code = _run_check_command(
        stage=stage,
        strict=strict,
        mode=mode,
        profile=profile,
        json_output=json_output,
        force=force,
        project_root=project_root,
        qa_policy=qa_policy,
        min_automation_rate=min_automation_rate,
        require_qa_types=require_qa_types,
        require_compat_matrix=compat_required,
        version=version,
    )
    raise typer.Exit(code)


@app.command()
def config(
    mode: Optional[str] = typer.Argument(None, help="Set gate mode: strict/normal/debug/dry-run"),
    scope_guard: Optional[bool] = typer.Option(None, "--scope-guard", help="Enable/disable scope guard"),
    project_root: Optional[str] = typer.Option("", "--project-root", "-p", help="Project root path"),
):
    """Configure gate settings"""
    root = Path(project_root) if project_root else Path.cwd()
    config = load_gate_config(root)

    if mode:
        try:
            GateMode(mode)
            config["mode"] = mode
        except ValueError:
            typer.echo(f"Error: Invalid mode '{mode}'")
            raise typer.Exit(1)

    if scope_guard is not None:
        config["scope_guard_enabled"] = scope_guard

    save_gate_config(root, config)
    typer.echo(f"Gate configuration saved:")
    typer.echo(f"  mode: {config['mode']}")
    typer.echo(f"  scope_guard_enabled: {config['scope_guard_enabled']}")


@app.command()
def status(
    project_root: Optional[str] = typer.Option("", "--project-root", "-p", help="Project root path"),
):
    """Show gate status"""
    root = Path(project_root) if project_root else Path.cwd()
    config = load_gate_config(root)

    typer.echo("Gate Status:")
    typer.echo(f"  Mode: {config.get('mode', 'strict')}")
    typer.echo(f"  Strict Default: {config.get('strict_default', True)}")
    typer.echo(f"  Scope Guard: {config.get('scope_guard_enabled', True)}")
    typer.echo(f"  Warn on Force: {config.get('warn_on_force', True)}")

    # Check for active risks
    risk_path = root / ".beacon" / "risks.json"
    if risk_path.exists():
        risks = json.loads(risk_path.read_text())
        typer.echo(f"  Active Risks: {len(risks)}")


@app.command("think")
def check_think(
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
    profile: str = typer.Option("auto", "--profile", help="Gate profile: auto/stage-local/release-global."),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    force: bool = typer.Option(False, "--force", help="Force pass with risk logging"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
):
    """Flat syntax compatibility for `gate think`."""
    raise typer.Exit(
        _run_check_command(
            stage="think",
            strict=strict,
            mode=mode,
            profile=profile,
            json_output=json_output,
            force=force,
            project_root=project_root,
        )
    )


@app.command("user-story")
def check_user_story(
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
    profile: str = typer.Option("auto", "--profile", help="Gate profile: auto/stage-local/release-global."),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    force: bool = typer.Option(False, "--force", help="Force pass with risk logging"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
):
    """Flat syntax compatibility for `gate user-story`."""
    raise typer.Exit(
        _run_check_command(
            stage="user-story",
            strict=strict,
            mode=mode,
            profile=profile,
            json_output=json_output,
            force=force,
            project_root=project_root,
        )
    )


@app.command("prd")
def check_prd(
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
    profile: str = typer.Option("auto", "--profile", help="Gate profile: auto/stage-local/release-global."),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    force: bool = typer.Option(False, "--force", help="Force pass with risk logging"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
):
    """Flat syntax compatibility for `gate prd`."""
    raise typer.Exit(
        _run_check_command(
            stage="prd",
            strict=strict,
            mode=mode,
            profile=profile,
            json_output=json_output,
            force=force,
            project_root=project_root,
        )
    )


@app.command("test-case")
def check_test_case(
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
    profile: str = typer.Option("auto", "--profile", help="Gate profile: auto/stage-local/release-global."),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    force: bool = typer.Option(False, "--force", help="Force pass with risk logging"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
):
    """Flat syntax compatibility for `gate test-case`."""
    raise typer.Exit(
        _run_check_command(
            stage="test-case",
            strict=strict,
            mode=mode,
            profile=profile,
            json_output=json_output,
            force=force,
            project_root=project_root,
        )
    )


@app.command("prototype")
def check_prototype(
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
    profile: str = typer.Option("auto", "--profile", help="Gate profile: auto/stage-local/release-global."),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    force: bool = typer.Option(False, "--force", help="Force pass with risk logging"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
):
    """Flat syntax compatibility for `gate prototype`."""
    raise typer.Exit(
        _run_check_command(
            stage="prototype",
            strict=strict,
            mode=mode,
            profile=profile,
            json_output=json_output,
            force=force,
            project_root=project_root,
        )
    )


@app.command("release")
def check_release(
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
    profile: str = typer.Option("auto", "--profile", help="Gate profile: auto/stage-local/release-global."),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    force: bool = typer.Option(False, "--force", help="Force pass with risk logging"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
):
    """Flat syntax compatibility for `gate release`."""
    raise typer.Exit(
        _run_check_command(
            stage="release",
            strict=strict,
            mode=mode,
            profile=profile,
            json_output=json_output,
            force=force,
            project_root=project_root,
        )
    )


if __name__ == "__main__":
    app()
