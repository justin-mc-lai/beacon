"""Beacon gate command - Gate validation with 20+ reason codes"""
import typer
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from datetime import datetime, timezone
from enum import Enum
import hashlib
import os

from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.memory import load_memory_entries
from beacon.utils.memory import scope_memory_paths
from beacon.utils.qa9 import QA9_TYPES, normalize_qa_type, parse_qa_types
from beacon.utils.versioning import resolve_target_version
from beacon.utils.workflow_memory import compute_memory_metrics, load_lifecycle_events

app = typer.Typer(name="gate", help="Run gate checks for workflow stages")

# Gate modes
class GateMode(str, Enum):
    STRICT = "strict"
    NORMAL = "normal"
    DEBUG = "debug"
    DRY_RUN = "dry-run"


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
    "evidence_timestamp_out_of_window",
    "assertion_count_zero_pass",
    "junit_missing_or_invalid",
    "report_result_mismatch",
    "flaky_rate_exceeded",
    "manual_waiver_unapproved",
]

# Workflow stages
WORKFLOW_STAGES = ["think", "user-story", "prd", "test-case", "release"]

# Gate configuration file
GATE_CONFIG_FILE = "gate-config.json"


def get_gate_config_path(project_root: Path) -> Path:
    """Get gate config file path"""
    return project_root / ".beacon" / GATE_CONFIG_FILE


def load_gate_config(project_root: Path) -> Dict[str, Any]:
    """Load gate configuration"""
    config_path = get_gate_config_path(project_root)
    if config_path.exists():
        return json.loads(config_path.read_text())
    # Default configuration
    return {
        "strict_default": True,
        "mode": "strict",
        "warn_on_force": True,
        "log_risks": True,
        "scope_guard_enabled": True,
    }


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
    """Return ordered candidate paths for execution artifacts.

    Order preserves backward compatibility:
    1) legacy docs/<version>/execution
    2) docs/product/<version>/execution
    3) docs/beacon/<version>/execution
    """
    return [
        project_root / "docs" / version / "execution" / filename,
        project_root / "docs" / "product" / version / "execution" / filename,
        project_root / "docs" / "beacon" / version / "execution" / filename,
    ]


def _resolved_gate_version(project_root: Path) -> str:
    requested = str(os.environ.get("BEACON_VERSION", "") or "").strip()
    return resolve_target_version(project_root, requested or None)


def _resolve_existing_execution_file(project_root: Path, version: str, filename: str) -> Path:
    candidates = _execution_file_candidates(project_root, version, filename)
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def check_boundaries(project_root: Path, mode: GateMode) -> List[Dict[str, Any]]:
    """Check boundaries.md exists"""
    issues = []
    version = _resolved_gate_version(project_root)
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


def check_terminal_artifact(project_root: Path, mode: GateMode) -> List[Dict[str, Any]]:
    """Check terminal.json exists and is valid"""
    issues = []
    version = _resolved_gate_version(project_root)
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


def check_memory_closure(project_root: Path, mode: GateMode, stage: str) -> List[Dict[str, Any]]:
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

    metrics = compute_memory_metrics(project_root)
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


def check_release_memory_profile(project_root: Path, mode: GateMode, stage: str) -> List[Dict[str, Any]]:
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

    metrics = compute_memory_metrics(project_root)
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


def _candidate_matrix_paths(project_root: Path) -> list[Path]:
    paths = []
    for base in (
        project_root / "docs" / "product",
        project_root / "docs" / "beacon",
    ):
        if not base.exists():
            continue
        paths.extend(sorted(base.glob("*/qa/test-cases/*.ac-test-matrix.json")))
    # Keep insertion order unique
    seen: set[str] = set()
    unique: list[Path] = []
    for p in paths:
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


def _candidate_qa9_matrix_paths(project_root: Path) -> list[Path]:
    paths = []
    for base in (
        project_root / "docs" / "product",
        project_root / "docs" / "beacon",
    ):
        if not base.exists():
            continue
        paths.extend(sorted(base.glob("*/qa/test-cases/*.qa9-matrix.json")))
    seen: set[str] = set()
    unique: list[Path] = []
    for p in paths:
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


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
        matrix_path = Path(str(matrix_report.get("matrix_path")))
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


def check_coverage_metrics(project_root: Path, mode: GateMode, stage: str) -> List[Dict[str, Any]]:
    """Check story/ac/tc coverage metrics and block non-full coverage in strict/debug."""
    issues: list[dict[str, Any]] = []
    if stage not in {"test-case", "release"}:
        return issues
    if mode not in {GateMode.STRICT, GateMode.DEBUG}:
        return issues

    version = _resolved_gate_version(project_root)
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
) -> Dict[str, Any]:
    """Run all gate checks for a stage"""
    all_issues = []
    gate_config = config or load_gate_config(project_root)
    scope_guard_enabled = bool(gate_config.get("scope_guard_enabled", True))

    if mode == GateMode.DRY_RUN:
        typer.echo("[DRY-RUN] Running checks without blocking...")
        mode = GateMode.DEBUG  # Use debug mode for dry-run

    # Run checks
    if mode == GateMode.DEBUG:
        typer.echo(f"[DEBUG] Checking boundaries...")
    all_issues.extend(check_boundaries(project_root, mode))

    if mode == GateMode.DEBUG:
        typer.echo(f"[DEBUG] Checking terminal artifact...")
    all_issues.extend(check_terminal_artifact(project_root, mode))

    if mode == GateMode.DEBUG:
        typer.echo(f"[DEBUG] Checking evidence chain...")
    all_issues.extend(check_evidence_chain(project_root, mode))

    if (mode == GateMode.STRICT or mode == GateMode.DEBUG) and scope_guard_enabled:
        if mode == GateMode.DEBUG:
            typer.echo(f"[DEBUG] Checking scope guard...")
        all_issues.extend(check_scope_guard(project_root, mode))

    if mode == GateMode.STRICT or mode == GateMode.DEBUG:
        if mode == GateMode.DEBUG:
            typer.echo(f"[DEBUG] Checking memory closure...")
        all_issues.extend(check_memory_closure(project_root, mode, stage))

    if mode == GateMode.STRICT or mode == GateMode.DEBUG:
        if mode == GateMode.DEBUG:
            typer.echo(f"[DEBUG] Checking release memory profile...")
        all_issues.extend(check_release_memory_profile(project_root, mode, stage))

    if mode == GateMode.STRICT or mode == GateMode.DEBUG:
        if mode == GateMode.DEBUG:
            typer.echo(f"[DEBUG] Checking test execution integrity...")
        all_issues.extend(check_test_execution_integrity(project_root, mode, stage))
    if mode == GateMode.STRICT or mode == GateMode.DEBUG:
        if mode == GateMode.DEBUG:
            typer.echo(f"[DEBUG] Checking coverage metrics...")
        all_issues.extend(check_coverage_metrics(project_root, mode, stage))
    if mode == GateMode.STRICT or mode == GateMode.DEBUG:
        if mode == GateMode.DEBUG:
            typer.echo(f"[DEBUG] Checking QA9 policy...")
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

    # Determine blocked status
    blocked_issues = [i for i in all_issues if i.get("blocked", False)]
    is_blocked = len(blocked_issues) > 0

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

    return {
        "stage": stage,
        "mode": mode.value,
        "status": "Blocked" if is_blocked else "Pass",
        "issues": all_issues,
        "blocked_count": len(blocked_issues),
        "force": force,
    }


def _run_check_command(
    stage: str,
    strict: bool = False,
    mode: Optional[str] = None,
    json_output: bool = False,
    force: bool = False,
    project_root: str = "",
    qa_policy: str = "legacy",
    min_automation_rate: float = 0.85,
    require_qa_types: Optional[list[str]] = None,
    require_compat_matrix: bool = False,
) -> int:
    """Shared gate check execution."""
    gate_mode = GateMode.STRICT if strict else GateMode.NORMAL
    if mode:
        try:
            gate_mode = GateMode(mode)
        except ValueError:
            typer.echo(f"Error: Invalid mode '{mode}'. Use strict/normal/debug/dry-run")
            return 1

    root = Path(project_root) if project_root else Path.cwd()
    config = load_gate_config(root)
    if not strict and not mode and "mode" in config:
        try:
            gate_mode = GateMode(config["mode"])
        except ValueError:
            pass

    if gate_mode == GateMode.DEBUG:
        typer.echo(f"[DEBUG] Gate Check: {stage}")
        typer.echo(f"[DEBUG] Mode: {gate_mode.value}")
    else:
        typer.echo(f"Gate Check: {stage}")
        typer.echo(f"Mode: {gate_mode.value.upper()}")

    result = run_gate_checks(
        stage,
        gate_mode,
        root,
        force,
        qa_policy=qa_policy,
        min_automation_rate=min_automation_rate,
        require_qa_types=require_qa_types,
        require_compat_matrix=require_compat_matrix,
    )
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
            status_color = typer.colors.GREEN if not force else typer.colors.YELLOW
            status_text = "PASS" + (" (forced)" if force else "")
            typer.echo(f"Status: {typer.style(status_text, fg=status_color)}")

        if result["issues"] and not result["blocked_count"]:
            typer.echo(f"Warnings: {len(result['issues'])}")
            for issue in result["issues"]:
                typer.echo(f"  - {issue['reason_code']}: {issue['message']}")

    return 2 if result["status"] == "Blocked" else 0


@app.command("list")
def list_checks(
    project_root: Optional[str] = typer.Option("", "--project-root", "-p", help="Project root path"),
):
    """List all gate checks"""
    typer.echo("Available Gate Checks:")
    typer.echo("")
    typer.echo("Workflow Stages:")
    for stage in WORKFLOW_STAGES:
        typer.echo(f"  - {stage}")
    typer.echo("")
    typer.echo("Gate Modes:")
    for mode in GateMode:
        typer.echo(f"  - {mode.value}")
    typer.echo("")
    typer.echo(f"Reason Codes ({len(REASON_CODES)} total):")
    for code in REASON_CODES:
        typer.echo(f"  - {code}")


@app.command()
def check(
    stage: str = typer.Argument("think", help="Workflow stage: think/user-story/prd/test-case/release"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
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
):
    """Run gate checks for workflow stages"""
    compat_required = bool(require_compat_matrix)
    if str(qa_policy or "").strip().lower() == "qa9-strict":
        compat_required = True
    code = _run_check_command(
        stage=stage,
        strict=strict,
        mode=mode,
        json_output=json_output,
        force=force,
        project_root=project_root,
        qa_policy=qa_policy,
        min_automation_rate=min_automation_rate,
        require_qa_types=require_qa_types,
        require_compat_matrix=compat_required,
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
            json_output=json_output,
            force=force,
            project_root=project_root,
        )
    )


@app.command("user-story")
def check_user_story(
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
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
            json_output=json_output,
            force=force,
            project_root=project_root,
        )
    )


@app.command("prd")
def check_prd(
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
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
            json_output=json_output,
            force=force,
            project_root=project_root,
        )
    )


@app.command("test-case")
def check_test_case(
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
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
            json_output=json_output,
            force=force,
            project_root=project_root,
        )
    )


@app.command("release")
def check_release(
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Gate mode: strict/normal/debug/dry-run"),
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
            json_output=json_output,
            force=force,
            project_root=project_root,
        )
    )


if __name__ == "__main__":
    app()
