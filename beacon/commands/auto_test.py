"""Beacon auto-test command - Automated testing."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit

import typer

app = typer.Typer(name="auto-test", help="Automated testing")

NEGATIVE_KEYWORDS = (
    "unauthorized",
    "forbidden",
    "access denied",
    "permission denied",
    "login",
    "sign in",
    "denied",
    "invalid",
    "error",
    "未授权",
    "无权限",
    "拒绝",
    "禁止",
    "登录",
    "错误",
    "失败",
    "异常",
)

LAYER_NAMES = ("ui", "api-curl", "unit", "smoke")

DEFAULT_REQUIRED_UI_ACTIONS = ("login", "register", "browse", "submit-form")


def _normalize_url(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        return ""
    try:
        parts = urlsplit(value)
    except Exception:
        return value
    path = parts.path or (value if value.startswith("/") else "")
    if not path and (parts.scheme or parts.netloc):
        path = "/"
    out = path or ""
    if parts.query:
        out = f"{out}?{parts.query}" if out else f"?{parts.query}"
    if parts.fragment:
        out = f"{out}#{parts.fragment}" if out else f"#{parts.fragment}"
    return out or value


def _extract_snapshot_text(snapshot_file: Optional[str], snapshot_text: Optional[str]) -> str:
    if snapshot_text:
        return snapshot_text
    if not snapshot_file:
        return ""

    path = Path(snapshot_file)
    if not path.exists():
        return ""

    raw = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw

    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict) and isinstance(data.get("snapshot"), str):
            return data["snapshot"]
        if isinstance(payload.get("snapshot"), str):
            return payload["snapshot"]
    return raw


def _parse_layer_overrides(items: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items or []:
        raw = (item or "").strip()
        if "=" not in raw:
            continue
        layer, command = raw.split("=", 1)
        layer = layer.strip().lower().replace("_", "-")
        command = command.strip()
        if layer in LAYER_NAMES and command:
            out[layer] = command
    return out


def _load_layer_commands_from_config(config_path: str | None) -> dict[str, str]:
    if not config_path:
        return {}
    path = Path(config_path)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    if not isinstance(payload, dict):
        return {}
    commands = payload.get("commands", payload)
    if not isinstance(commands, dict):
        return {}
    out: dict[str, str] = {}
    for key, value in commands.items():
        layer = str(key).strip().lower().replace("_", "-")
        command = str(value).strip()
        if layer in LAYER_NAMES and command:
            out[layer] = command
    return out


def _parse_ui_action_evidence(items: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items or []:
        raw = (item or "").strip()
        if "=" not in raw:
            continue
        action, path = raw.split("=", 1)
        action = action.strip().lower()
        path = path.strip()
        if action and path:
            out[action] = path
    return out


def _resolve_layers(scope: str) -> list[str]:
    normalized = (scope or "all").strip().lower().replace("_", "-")
    if normalized == "all":
        return list(LAYER_NAMES)
    if normalized in LAYER_NAMES:
        return [normalized]
    if normalized == "integration":
        return ["api-curl"]
    if normalized == "e2e":
        return ["ui", "smoke"]
    if normalized == "api":
        return ["api-curl"]
    return [normalized]


def _detect_ui_actions(
    *,
    snapshot_payload: str,
    ui_assertions: list[str],
    target_url: str,
    origin_url: str,
) -> set[str]:
    haystack = "\n".join(
        [
            (snapshot_payload or "").lower(),
            "\n".join(ui_assertions).lower(),
            (target_url or "").lower(),
            (origin_url or "").lower(),
        ]
    )
    observed: set[str] = set()
    if any(token in haystack for token in ("login", "sign in", "/login", "登录")):
        observed.add("login")
    if any(token in haystack for token in ("register", "sign up", "signup", "注册")):
        observed.add("register")
    if any(token in haystack for token in ("browse", "list", "dashboard", "浏览")):
        observed.add("browse")
    if any(token in haystack for token in ("submit", "form", "提交", "保存")):
        observed.add("submit-form")
    return observed


def evaluate_ui_false_positive_guard(
    *,
    expectation: str,
    target_url: str,
    origin_url: str,
    snapshot_text: str,
    strict_ui_assertion: bool,
    assertion_count: int,
    allow_unknown_skip: bool = False,
) -> dict:
    expectation_norm = (expectation or "").strip().lower()
    target_norm = _normalize_url(target_url)
    origin_norm = _normalize_url(origin_url)

    if not origin_norm:
        origin_vs_target = "unknown"
    elif origin_norm == target_norm:
        origin_vs_target = "match"
    else:
        origin_vs_target = "mismatch"

    haystack = f"{origin_url}\n{snapshot_text}".lower()
    negative_hit = any(keyword in haystack for keyword in NEGATIVE_KEYWORDS)

    detail = (
        f"origin_vs_target={origin_vs_target},"
        f"origin={origin_norm or 'unknown'},"
        f"target={target_norm or 'unknown'},"
        f"negative_hit={1 if negative_hit else 0}"
    )

    def outcome(status: str, reason_code: str) -> dict:
        return {
            "status": status,
            "reason_code": reason_code,
            "detail": detail,
            "expectation": expectation_norm or "unknown",
            "strict_ui_assertion": bool(strict_ui_assertion),
            "assertion_count": int(assertion_count),
            "origin_vs_target": origin_vs_target,
            "origin": origin_norm or "",
            "target": target_norm or "",
            "negative_hit": bool(negative_hit),
        }

    if strict_ui_assertion and assertion_count <= 0:
        return outcome("blocked", "ui_assertion_missing_strict")

    if expectation_norm in {"", "unknown"}:
        if strict_ui_assertion:
            return outcome("blocked", "ui_expectation_unknown_strict")
        if allow_unknown_skip:
            return outcome("passed", "ui_expectation_unknown_skipped")
        return outcome("blocked", "ui_real_execution_required")

    if expectation_norm == "success":
        if origin_vs_target == "match":
            return outcome("passed", "ui_expectation_success_matched")
        if origin_vs_target == "unknown":
            return outcome("blocked", "ui_origin_target_unknown")
        return outcome("failed", "ui_expectation_success_mismatch")

    if expectation_norm == "error":
        if origin_vs_target == "mismatch":
            return outcome("passed", "ui_expectation_error_redirect")
        if negative_hit:
            return outcome("passed", "ui_expectation_error_keyword")
        if origin_vs_target == "unknown":
            return outcome("blocked", "ui_origin_target_unknown")
        return outcome("failed", "ui_expectation_error_not_observed")

    return outcome("blocked", "ui_expectation_invalid")


def _run_layer_command(
    *,
    layer: str,
    command: str,
    project_root: Path,
    layer_dir: Path,
) -> dict:
    command_log = layer_dir / "command.txt"
    stdout_log = layer_dir / "stdout.log"
    stderr_log = layer_dir / "stderr.log"
    result_file = layer_dir / "result.json"

    layer_dir.mkdir(parents=True, exist_ok=True)
    command_log.write_text(command + "\n", encoding="utf-8")
    result = subprocess.run(
        command,
        cwd=project_root,
        shell=True,
        text=True,
        capture_output=True,
    )
    stdout_log.write_text(result.stdout or "", encoding="utf-8")
    stderr_log.write_text(result.stderr or "", encoding="utf-8")

    status = "passed" if result.returncode == 0 else "failed"
    payload = {
        "layer": layer,
        "command": command,
        "exit_code": result.returncode,
        "status": status,
        "evidence_ref": [
            str(command_log.relative_to(project_root)),
            str(stdout_log.relative_to(project_root)),
            str(stderr_log.relative_to(project_root)),
        ],
    }
    result_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    payload["evidence_ref"].append(str(result_file.relative_to(project_root)))
    return payload


def _merge_status_from_layers(layer_results: list[dict]) -> str:
    statuses = [str(item.get("status", "unknown")) for item in layer_results]
    if any(status == "blocked" for status in statuses):
        return "blocked"
    if any(status == "failed" for status in statuses):
        return "failed"
    if any(status == "not_executed" for status in statuses):
        return "blocked"
    if any(status == "passed" for status in statuses):
        return "passed"
    return "blocked"


def _write_matrix_evidence(
    *,
    project_root: Path,
    matrix_path: Path,
    run_id: str,
    layer_results: list[dict],
) -> dict:
    if not matrix_path.exists():
        return {"status": "missing_matrix", "matrix_path": str(matrix_path)}

    try:
        payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"status": "invalid_matrix", "matrix_path": str(matrix_path)}

    entries = payload.get("entries")
    if not isinstance(entries, list):
        return {"status": "invalid_matrix", "matrix_path": str(matrix_path)}

    passed_layers = {str(x.get("layer")) for x in layer_results if str(x.get("status")) == "passed"}
    touched = 0
    for item in entries:
        if not isinstance(item, dict):
            continue
        layer = str(item.get("layer", "")).strip()
        evidence_path = str(item.get("evidence_path", "")).strip()
        if not layer or not evidence_path or layer not in passed_layers:
            continue
        p = Path(evidence_path)
        full = p if p.is_absolute() else project_root / p
        full.parent.mkdir(parents=True, exist_ok=True)
        content = {
            "run_id": run_id,
            "ac_id": item.get("ac_id"),
            "tc_id": item.get("tc_id"),
            "layer": layer,
            "status": "passed",
            "generated_at": datetime.now().isoformat(),
        }
        full.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
        touched += 1

    return {
        "status": "ok",
        "matrix_path": str(matrix_path),
        "evidence_generated": touched,
        "entry_count": len(entries),
    }


@app.command()
def create(
    scope: str = typer.Argument("all", help="Test scope: ui/api-curl/unit/smoke/all"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Test config file"),
    expectation: str = typer.Option("unknown", "--expectation", help="UI expectation: success/error/unknown"),
    target_url: Optional[str] = typer.Option(None, "--target-url", help="UI target URL/path"),
    origin_url: Optional[str] = typer.Option(None, "--origin-url", help="UI actual origin URL/path"),
    snapshot_file: Optional[str] = typer.Option(None, "--snapshot-file", help="JSON snapshot file path"),
    snapshot_text: Optional[str] = typer.Option(None, "--snapshot-text", help="Snapshot text override"),
    ui_assertion: Optional[list[str]] = typer.Option(
        None,
        "--ui-assertion",
        help="Explicit UI assertion expression (repeatable).",
    ),
    strict_ui_assertion: bool = typer.Option(
        False,
        "--strict-ui-assertion",
        help="Block UI case when no explicit assertion exists.",
    ),
    ui_command: Optional[str] = typer.Option(None, "--ui-command", help="Real UI test command"),
    api_curl_command: Optional[str] = typer.Option(None, "--api-curl-command", help="Real API curl command"),
    unit_command: Optional[str] = typer.Option(None, "--unit-command", help="Real unit test command"),
    smoke_command: Optional[str] = typer.Option(None, "--smoke-command", help="Real smoke test command"),
    layer_command: Optional[list[str]] = typer.Option(
        None,
        "--layer-command",
        help="Layer command override (repeatable): layer=command",
    ),
    matrix_path: Optional[str] = typer.Option(
        None,
        "--matrix-path",
        help="AC/TC executable matrix JSON path",
    ),
    require_ui_actions: bool = typer.Option(
        False,
        "--require-ui-actions",
        help="Require evidence for login/register/browse/submit-form actions.",
    ),
    required_ui_action: Optional[list[str]] = typer.Option(
        None,
        "--required-ui-action",
        help="Required UI action (repeatable). Default: login/register/browse/submit-form",
    ),
    ui_action_evidence: Optional[list[str]] = typer.Option(
        None,
        "--ui-action-evidence",
        help="UI action evidence mapping (repeatable): action=path",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Run automated tests and persist unified evidence."""
    project_root = Path(project) if project else Path.cwd()

    typer.echo(f"Running automated tests: {scope}")
    typer.echo(f"Project: {project_root}")
    debug_mode = str(os.environ.get("BEACON_DEBUG", "")).strip().lower() in {"1", "true", "yes", "on"}

    scope_norm = (scope or "").strip().lower()
    selected_layers = _resolve_layers(scope_norm)
    run_id = datetime.now().strftime("run-%Y%m%dT%H%M%S%f")
    evidence_root = project_root / ".beacon" / "evidence" / "auto-test" / run_id
    evidence_root.mkdir(parents=True, exist_ok=True)

    commands = {
        "ui": ui_command or "",
        "api-curl": api_curl_command or "",
        "unit": unit_command or "",
        "smoke": smoke_command or "",
    }
    # config defaults < cli explicit overrides
    for layer, cmd in _load_layer_commands_from_config(config).items():
        if not commands.get(layer):
            commands[layer] = cmd
    commands.update(_parse_layer_overrides(layer_command))

    test_status: dict = {
        "scope": scope,
        "timestamp": datetime.now().isoformat(),
        "project": str(project_root),
        "status": "running",
        "selected_layers": selected_layers,
        "execution": {
            "run_id": run_id,
            "evidence_dir": str(evidence_root.relative_to(project_root)),
            "layers": [],
        },
    }

    ui_assertions = ui_assertion or []
    snapshot_payload = _extract_snapshot_text(snapshot_file, snapshot_text)
    ui_guard_requested = bool(
        target_url
        or origin_url
        or snapshot_file
        or snapshot_text
        or strict_ui_assertion
        or ui_assertions
        or (expectation or "").strip().lower() not in {"", "unknown"}
        or "ui" in selected_layers
    )

    ui_guard = None
    if ui_guard_requested:
        ui_guard = evaluate_ui_false_positive_guard(
            expectation=expectation,
            target_url=target_url or "",
            origin_url=origin_url or "",
            snapshot_text=snapshot_payload,
            strict_ui_assertion=strict_ui_assertion,
            assertion_count=len(ui_assertions),
            allow_unknown_skip=debug_mode,
        )
        test_status["ui_guard"] = ui_guard

    layer_results: list[dict] = []
    for layer in selected_layers:
        layer_dir = evidence_root / layer
        command = str(commands.get(layer, "")).strip()
        if command:
            result = _run_layer_command(layer=layer, command=command, project_root=project_root, layer_dir=layer_dir)
            layer_results.append(result)
            continue

        if layer == "ui" and ui_guard is not None:
            payload = {
                "layer": "ui",
                "status": ui_guard["status"],
                "reason_code": ui_guard["reason_code"],
                "detail": ui_guard["detail"],
                "command": None,
                "exit_code": None,
                "evidence_ref": [],
            }
            if snapshot_payload:
                snap_path = layer_dir / "snapshot.txt"
                layer_dir.mkdir(parents=True, exist_ok=True)
                snap_path.write_text(snapshot_payload, encoding="utf-8")
                payload["evidence_ref"].append(str(snap_path.relative_to(project_root)))
            layer_results.append(payload)
        else:
            layer_results.append(
                {
                    "layer": layer,
                    "status": "not_executed",
                    "reason_code": "layer_command_missing",
                    "command": None,
                    "exit_code": None,
                    "evidence_ref": [],
                }
            )

    ui_action_map = _parse_ui_action_evidence(ui_action_evidence)
    detected_actions = _detect_ui_actions(
        snapshot_payload=snapshot_payload,
        ui_assertions=ui_assertions,
        target_url=target_url or "",
        origin_url=origin_url or "",
    )
    observed_actions = sorted(set(ui_action_map.keys()) | detected_actions)
    required_actions = [x.lower() for x in (required_ui_action or []) if str(x).strip()]
    if require_ui_actions and not required_actions:
        required_actions = list(DEFAULT_REQUIRED_UI_ACTIONS)
    missing_actions = sorted(set(required_actions) - set(observed_actions))

    key_action_guard = {
        "required": bool(require_ui_actions),
        "required_actions": required_actions,
        "observed_actions": observed_actions,
        "missing_actions": missing_actions,
        "status": "failed" if missing_actions else "passed",
    }
    if require_ui_actions:
        test_status["key_action_guard"] = key_action_guard

    execution_payload = test_status["execution"]
    execution_payload["layers"] = layer_results
    execution_payload["ui_action_evidence"] = ui_action_map

    matrix_report = None
    if matrix_path:
        matrix_report = _write_matrix_evidence(
            project_root=project_root,
            matrix_path=Path(matrix_path),
            run_id=run_id,
            layer_results=layer_results,
        )
        execution_payload["matrix_report"] = matrix_report

    status_from_layers = _merge_status_from_layers(layer_results)
    if require_ui_actions and missing_actions:
        status_from_layers = "failed"
    test_status["status"] = status_from_layers

    summary_path = evidence_root / "summary.json"
    summary_path.write_text(json.dumps(test_status, ensure_ascii=False, indent=2), encoding="utf-8")
    execution_payload.setdefault("artifacts", []).append(str(summary_path.relative_to(project_root)))

    status_file = project_root / ".beacon" / "auto-test-status.json"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    status_file.write_text(json.dumps(test_status, ensure_ascii=False, indent=2), encoding="utf-8")

    typer.echo("✓ Test execution started")
    typer.echo(f"  Scope: {scope}")
    typer.echo(f"  Layers: {', '.join(selected_layers)}")
    typer.echo(f"  Status file: {status_file}")
    typer.echo(f"  Evidence: {evidence_root}")
    if ui_guard_requested and isinstance(ui_guard, dict):
        typer.echo(f"  UI Guard: {ui_guard.get('status')} ({ui_guard.get('reason_code')})")
    if require_ui_actions:
        typer.echo(f"  UI Actions: {key_action_guard['status']} (missing={','.join(missing_actions) or '-'})")
    if matrix_report and verbose:
        typer.echo(f"  Matrix: {matrix_report}")


@app.command()
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """View test status."""
    project_root = Path(project) if project else Path.cwd()
    status_file = project_root / ".beacon" / "auto-test-status.json"

    if not status_file.exists():
        typer.echo("No test status found. Run 'beacon auto-test create' first.")
        return

    status_data = json.loads(status_file.read_text(encoding="utf-8"))

    if json_output:
        typer.echo(json.dumps(status_data, indent=2, ensure_ascii=False))
    else:
        typer.echo("Auto-Test Status")
        typer.echo("=" * 40)
        typer.echo(f"Scope: {status_data.get('scope', 'N/A')}")
        typer.echo(f"Status: {status_data.get('status', 'N/A')}")
        typer.echo(f"Timestamp: {status_data.get('timestamp', 'N/A')}")
        layers = status_data.get("selected_layers")
        if isinstance(layers, list):
            typer.echo(f"Layers: {', '.join(str(x) for x in layers)}")
        execution = status_data.get("execution")
        if isinstance(execution, dict):
            typer.echo(f"Evidence: {execution.get('evidence_dir', 'N/A')}")
        ui_guard = status_data.get("ui_guard")
        if isinstance(ui_guard, dict):
            typer.echo(f"UI Guard: {ui_guard.get('reason_code', 'N/A')}")
            typer.echo(f"UI Detail: {ui_guard.get('detail', 'N/A')}")
        key_guard = status_data.get("key_action_guard")
        if isinstance(key_guard, dict):
            typer.echo(f"UI Key Actions: {key_guard.get('status', 'N/A')}")


if __name__ == "__main__":
    app()
