"""Beacon gate command - Gate validation with 20+ reason codes"""
import typer
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from datetime import datetime
from enum import Enum
import hashlib
import os

from beacon.utils.memory import load_memory_entries
from beacon.utils.memory import scope_memory_paths
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
    "test_execution_missing",
    "test_key_actions_missing",
    "ac_tc_evidence_chain_broken",
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


def _resolve_existing_execution_file(project_root: Path, version: str, filename: str) -> Path:
    candidates = _execution_file_candidates(project_root, version, filename)
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def check_boundaries(project_root: Path, mode: GateMode) -> List[Dict[str, Any]]:
    """Check boundaries.md exists"""
    issues = []
    version = os.environ.get("BEACON_VERSION", "v1.0.0")
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
    version = os.environ.get("BEACON_VERSION", "v1.0.0")
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


def _candidate_matrix_paths(project_root: Path) -> list[Path]:
    paths = []
    for base in (
        project_root / "docs" / "product",
        project_root / "docs" / "beacon",
    ):
        if not base.exists():
            continue
        paths.extend(sorted(base.glob("*/qa/test-cases/*.ac-test-matrix.json")))
        paths.extend(sorted(base.glob("latest/qa/test-cases/*.ac-test-matrix.json")))
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

    executed_layers = {str(item.get("layer")) for item in layers if str(item.get("status")) == "passed"}
    chain_broken = []
    for item in entries:
        layer = str(item.get("layer"))
        if layer not in executed_layers:
            chain_broken.append(item.get("tc_id"))
            continue
        evidence = Path(str(item.get("evidence_path")))
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


def run_gate_checks(
    stage: str,
    mode: GateMode,
    project_root: Path,
    force: bool = False,
    config: Optional[Dict[str, Any]] = None,
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
            typer.echo(f"[DEBUG] Checking test execution integrity...")
        all_issues.extend(check_test_execution_integrity(project_root, mode, stage))

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

    result = run_gate_checks(stage, gate_mode, root, force)
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
    typer.echo("Reason Codes (25 total):")
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
):
    """Run gate checks for workflow stages"""
    code = _run_check_command(
        stage=stage,
        strict=strict,
        mode=mode,
        json_output=json_output,
        force=force,
        project_root=project_root,
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
