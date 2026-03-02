"""Beacon gate command - Gate validation with 20+ reason codes"""
import typer
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from datetime import datetime
from enum import Enum
import hashlib
import os

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


def check_boundaries(project_root: Path, mode: GateMode) -> List[Dict[str, Any]]:
    """Check boundaries.md exists"""
    issues = []
    version = os.environ.get("BEACON_VERSION", "v1.0.0")
    boundaries_path = project_root / "docs" / version / "execution" / "boundaries.md"

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

    return issues


def check_terminal_artifact(project_root: Path, mode: GateMode) -> List[Dict[str, Any]]:
    """Check terminal.json exists and is valid"""
    issues = []
    version = os.environ.get("BEACON_VERSION", "v1.0.0")
    terminal_path = project_root / "docs" / version / "execution" / "terminal.json"

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
    elif mode == GateMode.DEBUG:
        typer.echo(f"  [DEBUG] raw-command-log.jsonl exists")

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
            # Check manifest structure
            if "entries" not in manifest:
                issue = {
                    "reason_code": "evidence_sha256_manifest_invalid",
                    "severity": "high",
                    "message": "evidence-manifest missing 'entries' field",
                    "blocked": mode == GateMode.STRICT,
                }
                issues.append(issue)
            elif mode == GateMode.DEBUG:
                typer.echo(f"  [DEBUG] evidence-manifest.json valid with {len(manifest.get('entries', []))} entries")

            # Check integrity
            for entry in manifest.get("entries", []):
                if "sha256" not in entry or "path" not in entry:
                    issue = {
                        "reason_code": "evidence_sha256_manifest_incomplete",
                        "severity": "medium",
                        "message": f"evidence-manifest entry missing sha256 or path: {entry}",
                        "blocked": False,
                    }
                    issues.append(issue)
                    continue

                # Verify file exists and hash matches
                file_path = project_root / entry["path"]
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

    return issues


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

    return issues


def run_gate_checks(
    stage: str,
    mode: GateMode,
    project_root: Path,
    force: bool = False,
) -> Dict[str, Any]:
    """Run all gate checks for a stage"""
    all_issues = []

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

    if mode == GateMode.STRICT or mode == GateMode.DEBUG:
        if mode == GateMode.DEBUG:
            typer.echo(f"[DEBUG] Checking scope guard...")
        all_issues.extend(check_scope_guard(project_root, mode))

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


@app.command()
def list(
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
    # Determine mode
    gate_mode = GateMode.STRICT if strict else GateMode.NORMAL
    if mode:
        try:
            gate_mode = GateMode(mode)
        except ValueError:
            typer.echo(f"Error: Invalid mode '{mode}'. Use strict/normal/debug/dry-run")
            raise typer.Exit(1)

    # Get project root
    root = Path(project_root) if project_root else Path.cwd()

    # Load config
    config = load_gate_config(root)

    # Override mode from config if not explicitly set
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

    # Run checks
    result = run_gate_checks(stage, gate_mode, root, force)

    # Output
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

    # Exit code
    if result["status"] == "Blocked":
        raise typer.Exit(2)


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


if __name__ == "__main__":
    app()
