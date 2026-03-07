"""Beacon auto-test command - Automated testing."""

from __future__ import annotations

import json
import os
import subprocess
import hashlib
import re
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree
from typing import Any, Optional
from urllib.parse import urlsplit

import typer

from beacon.utils.qa9 import (
    QA9_TYPES,
    default_command_for_qa_type,
    normalize_qa_type,
    parse_qa_types,
    to_legacy_layer,
)
from beacon.utils.runtime import append_jsonl, now_iso, write_json
from beacon.utils.versioning import resolve_target_version
from beacon.utils.v110_baseline import generate_spec_fingerprint, load_latest_spec_fingerprint

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

LAYER_NAMES = (
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
)
DEFAULT_ALL_LAYERS = ("ui", "api-curl", "unit", "smoke")

DEFAULT_REQUIRED_UI_ACTIONS = ("login", "register", "browse", "submit-form")


def _raw_command_log_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "raw-command-log.jsonl"


def _append_raw_command_log(
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    layer: str,
    command: str,
    exit_code: int,
    attempt: int,
    metadata: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "ts": now_iso(),
        "run_id": run_id,
        "stage": stage,
        "layer": layer,
        "command": command,
        "exit_code": int(exit_code),
        "attempt": int(attempt),
    }
    if isinstance(metadata, dict) and metadata:
        payload["metadata"] = metadata
    append_jsonl(_raw_command_log_path(project_root), payload)


def _update_evidence_manifest(
    project_root: Path,
    evidence_refs: list[str],
    *,
    run_id: str | None = None,
    version: str | None = None,
) -> None:
    manifest_path = project_root / ".beacon" / "evidence-manifest.json"
    manifest_rel = str(manifest_path.relative_to(project_root))
    payload: dict[str, Any] = {}
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
        if (
            isinstance(item, dict)
            and str(item.get("path", "")).strip()
            and str(item.get("path", "")).strip() != manifest_rel
        )
    }
    for ref in evidence_refs:
        ref_path = str(ref or "").strip()
        if not ref_path:
            continue
        if ref_path == manifest_rel:
            continue
        full = project_root / ref_path
        if not full.exists() or not full.is_file():
            continue
        by_path[ref_path] = {
            "path": ref_path,
            "sha256": hashlib.sha256(full.read_bytes()).hexdigest(),
            "updated_at": now_iso(),
        }
    output_payload: dict[str, Any] = {
        "schema_version": "1.0",
        "entries": list(by_path.values()),
        "updated_at": now_iso(),
    }
    next_run_id = str(run_id or payload.get("run_id") or "").strip()
    next_version = str(version or payload.get("version") or "").strip()
    if next_run_id:
        output_payload["run_id"] = next_run_id
    if next_version:
        output_payload["version"] = next_version
    write_json(manifest_path, output_payload)


def _normalize_execution_layer(value: str | None) -> str:
    raw = str(value or "").strip().lower().replace("_", "-")
    if raw in LAYER_NAMES:
        return raw
    mapped = normalize_qa_type(raw)
    return mapped


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
        layer = _normalize_execution_layer(layer.strip().lower().replace("_", "-"))
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
        layer = _normalize_execution_layer(str(key).strip().lower().replace("_", "-"))
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
    normalized_raw = (scope or "all").strip().lower().replace("_", "-")
    if normalized_raw == "all":
        return list(DEFAULT_ALL_LAYERS)
    if normalized_raw in {"full", "all-with-visual", "all+visual"}:
        return ["ui", "api-curl", "unit", "smoke", "visual"]
    if normalized_raw in {"ui", "api-curl", "unit", "smoke", "visual"}:
        return [normalized_raw]
    normalized = normalize_qa_type(normalized_raw)
    if normalized == "qa9":
        return list(QA9_TYPES)
    if normalized in LAYER_NAMES:
        return [normalized]
    if normalized == "integration":
        return ["integration"]
    if normalized == "e2e":
        return ["functional", "smoke"]
    if normalized == "regression":
        return ["regression"]
    if normalized == "api":
        return ["interface"]
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


def _extract_assertion_count_from_junit(path: Path) -> int:
    if not path.exists() or not path.is_file():
        return 0
    try:
        tree = ElementTree.parse(path)
        root = tree.getroot()
    except Exception:  # noqa: BLE001
        return 0

    total = 0

    def _read_int(value: Any) -> int:
        try:
            return int(str(value))
        except Exception:  # noqa: BLE001
            return 0

    tests_attr = root.attrib.get("tests")
    if tests_attr is not None:
        total += _read_int(tests_attr)
    for node in root.findall(".//testsuite"):
        total += _read_int(node.attrib.get("tests"))
    if total > 0:
        return total

    testcase_count = len(root.findall(".//testcase"))
    return testcase_count if testcase_count > 0 else 0


def _extract_assertion_count(stdout_text: str, stderr_text: str, *, junit_file: Path | None = None) -> int:
    if isinstance(junit_file, Path):
        junit_count = _extract_assertion_count_from_junit(junit_file)
        if junit_count > 0:
            return junit_count

    text = "\n".join([stdout_text or "", stderr_text or ""])
    patterns = [
        r"(?:^|\n)\s*BEACON_ASSERTIONS\s*[:=]\s*(?P<count>\d+)\s*(?:\n|$)",
        r"=+\s*.*?\b(?P<count>\d+)\s+passed\b.*=+",
        r"tests?\s*[:=]\s*(?P<count>\d+)",
        r"assertions?\s*[:=]\s*(?P<count>\d+)",
        r"(?P<count>\d+)\s+passing(?:\s|\(|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if not match:
            continue
        try:
            count = int(match.group("count"))
        except Exception:  # noqa: BLE001
            count = 0
        if count > 0:
            return count
    return 0


def _is_valid_junit_file(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore").strip().lower()
    if not text:
        return False
    return "<testsuite" in text or "<testsuites" in text


def _run_layer_command(
    *,
    layer: str,
    command: str,
    project_root: Path,
    layer_dir: Path,
    retries: int = 0,
    run_id: str = "",
    stage: str = "verify",
    extra_env: dict[str, str] | None = None,
    tc_id: str = "",
    ac_id: str = "",
) -> dict:
    command_log = layer_dir / "command.txt"
    stdout_log = layer_dir / "stdout.log"
    stderr_log = layer_dir / "stderr.log"
    result_file = layer_dir / "result.json"
    junit_file = layer_dir / "junit.xml"

    layer_dir.mkdir(parents=True, exist_ok=True)
    command_log.write_text(command + "\n", encoding="utf-8")
    attempts = max(0, int(retries)) + 1
    run_records: list[dict[str, Any]] = []
    final_result: subprocess.CompletedProcess[str] | None = None
    started_at = datetime.now().isoformat()
    for attempt in range(1, attempts + 1):
        run_env = os.environ.copy()
        run_env.update(
            {
                "BEACON_STAGE": stage,
                "BEACON_LAYER": layer,
                "BEACON_RUN_ID": run_id,
                "BEACON_PROJECT_ROOT": str(project_root),
                "BEACON_LAYER_DIR": str(layer_dir),
                "BEACON_JUNIT_PATH": str(junit_file),
                "BEACON_COMMAND_LOG": str(command_log),
                "BEACON_STDOUT_LOG": str(stdout_log),
                "BEACON_STDERR_LOG": str(stderr_log),
            }
        )
        if tc_id:
            run_env["BEACON_TC_ID"] = tc_id
        if ac_id:
            run_env["BEACON_AC_ID"] = ac_id
        if isinstance(extra_env, dict):
            run_env.update({str(k): str(v) for k, v in extra_env.items() if str(k).strip()})
        result = subprocess.run(
            command,
            cwd=project_root,
            shell=True,
            text=True,
            capture_output=True,
            env=run_env,
        )
        if run_id:
            _append_raw_command_log(
                project_root,
                run_id=run_id,
                stage=stage,
                layer=layer,
                command=command,
                exit_code=int(result.returncode),
                attempt=attempt,
                metadata={"tc_id": tc_id, "ac_id": ac_id},
            )
        run_records.append(
            {
                "attempt": attempt,
                "exit_code": int(result.returncode),
                "stdout": result.stdout or "",
                "stderr": result.stderr or "",
                "timestamp": datetime.now().isoformat(),
            }
        )
        final_result = result
        if result.returncode == 0:
            break

    assert final_result is not None
    stdout_text = final_result.stdout or ""
    stderr_text = final_result.stderr or ""
    stdout_log.write_text(stdout_text, encoding="utf-8")
    stderr_log.write_text(stderr_text, encoding="utf-8")

    status = "passed" if final_result.returncode == 0 else "failed"
    was_flaky = status == "passed" and any(item.get("exit_code") != 0 for item in run_records[:-1])
    assertion_count = _extract_assertion_count(stdout_text, stderr_text, junit_file=junit_file)
    fingerprint_input = "\n".join(
        [
            command,
            started_at,
            datetime.now().isoformat(),
            str(final_result.returncode),
            stdout_text,
            stderr_text,
        ]
    )
    execution_fingerprint = hashlib.sha256(fingerprint_input.encode("utf-8")).hexdigest()

    payload = {
        "layer": layer,
        "command": command,
        "exit_code": final_result.returncode,
        "status": status,
        "assertion_count": assertion_count,
        "was_flaky": was_flaky,
        "attempt_count": len(run_records),
        "attempts": [
            {"attempt": item.get("attempt"), "exit_code": item.get("exit_code")}
            for item in run_records
        ],
        "execution_fingerprint": execution_fingerprint,
        "started_at": started_at,
        "ended_at": datetime.now().isoformat(),
        "junit_path": str(junit_file.relative_to(project_root)) if junit_file.exists() else "",
        "junit_valid": _is_valid_junit_file(junit_file) if junit_file.exists() else False,
        "evidence_ref": [
            str(command_log.relative_to(project_root)),
            str(stdout_log.relative_to(project_root)),
            str(stderr_log.relative_to(project_root)),
        ],
    }
    if tc_id:
        payload["tc_id"] = tc_id
    if ac_id:
        payload["ac_id"] = ac_id
    if junit_file.exists():
        payload["evidence_ref"].append(str(junit_file.relative_to(project_root)))
    result_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    payload["evidence_ref"].append(str(result_file.relative_to(project_root)))
    return payload


def _collect_files(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    files: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        files[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def _run_visual_comparison(
    *,
    project_root: Path,
    layer_dir: Path,
    baseline_dir: str,
    current_dir: str,
    threshold: float,
) -> dict:
    baseline_root = Path(baseline_dir)
    current_root = Path(current_dir)
    if not baseline_root.is_absolute():
        baseline_root = project_root / baseline_root
    if not current_root.is_absolute():
        current_root = project_root / current_root

    baseline_manifest = _collect_files(baseline_root)
    current_manifest = _collect_files(current_root)

    all_keys = sorted(set(baseline_manifest.keys()) | set(current_manifest.keys()))
    mismatches: list[dict[str, str]] = []
    for key in all_keys:
        left = baseline_manifest.get(key)
        right = current_manifest.get(key)
        if left == right:
            continue
        reason = "changed"
        if left is None:
            reason = "added"
        elif right is None:
            reason = "removed"
        mismatches.append(
            {
                "file": key,
                "reason": reason,
                "baseline_sha256": left or "",
                "current_sha256": right or "",
            }
        )

    total = max(len(all_keys), 1)
    mismatch_ratio = float(len(mismatches)) / float(total)
    status = "passed" if mismatch_ratio <= max(0.0, threshold) else "failed"

    layer_dir.mkdir(parents=True, exist_ok=True)
    baseline_manifest_path = layer_dir / "baseline-manifest.json"
    current_manifest_path = layer_dir / "current-manifest.json"
    diff_summary_path = layer_dir / "visual-diff-summary.json"
    baseline_manifest_path.write_text(json.dumps(baseline_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    current_manifest_path.write_text(json.dumps(current_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    diff_payload = {
        "status": status,
        "baseline_dir": str(baseline_root),
        "current_dir": str(current_root),
        "threshold": threshold,
        "total_files": len(all_keys),
        "mismatch_count": len(mismatches),
        "mismatch_ratio": round(mismatch_ratio, 4),
        "mismatches": mismatches,
        "generated_at": datetime.now().isoformat(),
    }
    diff_summary_path.write_text(json.dumps(diff_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "status": status,
        "report": diff_payload,
        "evidence_ref": [
            str(baseline_manifest_path.relative_to(project_root)),
            str(current_manifest_path.relative_to(project_root)),
            str(diff_summary_path.relative_to(project_root)),
        ],
    }


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
    require_fresh_evidence: bool = False,
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

    passed_layers = {
        normalize_qa_type(str(x.get("layer")))
        for x in layer_results
        if str(x.get("status")) == "passed"
    }
    touched = 0
    freshness_violations: list[str] = []

    def _entry_layer(item: dict[str, Any]) -> str:
        return normalize_qa_type(str(item.get("qa_type") or item.get("layer") or "").strip())

    def _resolve_evidence_path(raw_path: str) -> str:
        value = str(raw_path or "").strip()
        if not value:
            return value
        if "{run_id}" in value:
            value = value.replace("{run_id}", run_id)
        if "$RUN_ID" in value:
            value = value.replace("$RUN_ID", run_id)
        if "__RUN_ID__" in value:
            value = value.replace("__RUN_ID__", run_id)
        return value

    for item in entries:
        if not isinstance(item, dict):
            continue
        layer = _entry_layer(item)
        evidence_path = _resolve_evidence_path(str(item.get("evidence_path", "")).strip())
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
        if require_fresh_evidence and run_id not in str(full):
            freshness_violations.append(str(full))
        touched += 1

    return {
        "status": "ok" if not freshness_violations else "freshness_violation",
        "matrix_path": str(matrix_path),
        "evidence_generated": touched,
        "entry_count": len(entries),
        "freshness_violations": freshness_violations[:20],
    }


def _normalize_required_pairs(raw_pairs: Any) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(raw_pairs, list):
        return out
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
        out.append({"browser": browser, "device": device})
    return out


def _expand_pairs(browsers: list[str], devices: list[str]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for browser in browsers:
        b = str(browser or "").strip().lower()
        if not b:
            continue
        for device in devices:
            d = str(device or "").strip().lower()
            if not d:
                continue
            key = (b, d)
            if key in seen:
                continue
            seen.add(key)
            out.append({"browser": b, "device": d})
    return out


def _load_executed_pairs_from_evidence(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []
    if isinstance(payload, dict):
        pairs = payload.get("executed_pairs")
        if isinstance(pairs, list):
            return _normalize_required_pairs(pairs)
    if isinstance(payload, list):
        return _normalize_required_pairs(payload)
    return []


def _execute_qa9_tc_entries(
    *,
    project_root: Path,
    run_id: str,
    evidence_root: Path,
    matrix_payload: dict[str, Any],
    commands: dict[str, str],
    explicit_layer_overrides: dict[str, str],
    rerun_flaky: int,
    compat_required_pairs: list[dict[str, str]],
    compat_browsers_list: list[str],
    compat_devices_list: list[str],
) -> dict[str, dict[str, Any]]:
    entries = matrix_payload.get("entries")
    if not isinstance(entries, list):
        return {}

    tc_map: dict[str, dict[str, Any]] = {}
    for item in entries:
        if not isinstance(item, dict):
            continue
        tc_id = str(item.get("tc_id") or "").strip()
        if not tc_id:
            continue
        ac_id = str(item.get("ac_id") or "").strip()
        qa_type = normalize_qa_type(str(item.get("qa_type") or item.get("layer") or "").strip())
        if qa_type not in QA9_TYPES:
            continue
        automation = str(item.get("automation") or "auto").strip().lower()
        command = str(
            explicit_layer_overrides.get(qa_type)
            or item.get("command")
            or commands.get(qa_type)
            or ""
        ).strip()
        tc_dir = evidence_root / "qa9-tc" / tc_id
        tc_dir.mkdir(parents=True, exist_ok=True)

        if automation not in {"auto", "hybrid"}:
            tc_map[tc_id] = {
                "tc_id": tc_id,
                "ac_id": ac_id,
                "qa_type": qa_type,
                "automation": automation,
                "status": "pending",
                "layer_status": "not_executed",
                "command": command,
                "assertion_count": 0,
                "evidence_ref": [],
            }
            continue

        if not command:
            tc_map[tc_id] = {
                "tc_id": tc_id,
                "ac_id": ac_id,
                "qa_type": qa_type,
                "automation": automation,
                "status": "blocked",
                "layer_status": "not_executed",
                "reason_code": "qa9_command_missing_auto_case",
                "command": "",
                "assertion_count": 0,
                "evidence_ref": [],
            }
            continue

        extra_env: dict[str, str] = {
            "BEACON_TC_ID": tc_id,
            "BEACON_AC_ID": ac_id,
            "BEACON_QA_TYPE": qa_type,
        }
        if qa_type == "compatibility":
            extra_env.update(
                {
                    "BEACON_COMPAT_EVIDENCE_PATH": str(tc_dir / "pair-evidence.json"),
                    "BEACON_COMPAT_REQUIRED_PAIRS": json.dumps(compat_required_pairs, ensure_ascii=False),
                    "BEACON_COMPAT_BROWSERS": ",".join(compat_browsers_list),
                    "BEACON_COMPAT_DEVICES": ",".join(compat_devices_list),
                }
            )

        run_payload = _run_layer_command(
            layer=qa_type,
            command=command,
            project_root=project_root,
            layer_dir=tc_dir,
            retries=rerun_flaky,
            run_id=run_id,
            stage="verify",
            extra_env=extra_env,
            tc_id=tc_id,
            ac_id=ac_id,
        )
        tc_map[tc_id] = {
            "tc_id": tc_id,
            "ac_id": ac_id,
            "qa_type": qa_type,
            "automation": automation,
            "status": _layer_status_to_tc_status(str(run_payload.get("status") or "")),
            "layer_status": str(run_payload.get("status") or ""),
            "command": command,
            "assertion_count": int(run_payload.get("assertion_count") or 0),
            "evidence_ref": run_payload.get("evidence_ref") if isinstance(run_payload.get("evidence_ref"), list) else [],
            "execution_fingerprint": str(run_payload.get("execution_fingerprint") or ""),
            "started_at": str(run_payload.get("started_at") or ""),
            "ended_at": str(run_payload.get("ended_at") or ""),
            "junit_path": str(run_payload.get("junit_path") or ""),
            "junit_valid": bool(run_payload.get("junit_valid")),
        }
    return tc_map


def _layer_status_to_tc_status(layer_status: str) -> str:
    normalized = str(layer_status or "").strip().lower()
    if normalized == "passed":
        return "passed"
    if normalized == "failed":
        return "failed"
    if normalized in {"blocked", "not_executed"}:
        return "blocked"
    return "pending"


def _build_qa9_tc_backfill(
    *,
    matrix_payload: dict[str, Any],
    layer_results: list[dict[str, Any]],
    run_id: str,
    tc_execution_map: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    entries = matrix_payload.get("entries")
    if not isinstance(entries, list):
        return {
            "summary": {
                "cases_total": 0,
                "passed": 0,
                "failed": 0,
                "blocked": 0,
                "pending": 0,
                "pass_rate": 0.0,
                "automation_rate": 0.0,
                "auto_cases_total": 0,
                "auto_cases_executed": 0,
            },
            "tc_results": [],
        }

    layer_map: dict[str, dict[str, Any]] = {}
    for layer in layer_results:
        if not isinstance(layer, dict):
            continue
        name = normalize_qa_type(str(layer.get("layer") or "").strip())
        if not name:
            continue
        layer_map[name] = layer

    tc_results: list[dict[str, Any]] = []
    passed = failed = blocked = pending = 0
    auto_total = auto_executed = 0
    for item in entries:
        if not isinstance(item, dict):
            continue
        qa_type = normalize_qa_type(str(item.get("qa_type") or item.get("layer") or "").strip())
        tc_id = str(item.get("tc_id") or qa_type or "TC-UNKNOWN").strip()
        ac_id = str(item.get("ac_id") or "AC-UNKNOWN").strip()
        automation = str(item.get("automation") or "auto").strip().lower()
        tc_payload = {}
        if isinstance(tc_execution_map, dict):
            maybe_payload = tc_execution_map.get(tc_id)
            if isinstance(maybe_payload, dict):
                tc_payload = maybe_payload

        layer_payload = layer_map.get(qa_type, {})
        layer_status = str(tc_payload.get("layer_status") or layer_payload.get("status") or "not_executed").strip().lower()
        tc_status = str(tc_payload.get("status") or _layer_status_to_tc_status(layer_status)).strip().lower()
        if tc_status not in {"passed", "failed", "blocked", "pending"}:
            tc_status = _layer_status_to_tc_status(layer_status)
        assertion_count = int(tc_payload.get("assertion_count") or layer_payload.get("assertion_count") or 0)
        evidence_ref = (
            tc_payload.get("evidence_ref")
            if isinstance(tc_payload.get("evidence_ref"), list)
            else (
                layer_payload.get("evidence_ref")
                if isinstance(layer_payload.get("evidence_ref"), list)
                else []
            )
        )
        effective_command = str(tc_payload.get("command") or item.get("command") or "")

        if tc_status == "passed":
            passed += 1
        elif tc_status == "failed":
            failed += 1
        elif tc_status == "blocked":
            blocked += 1
        else:
            pending += 1

        if automation in {"auto", "hybrid"}:
            auto_total += 1
            if tc_status in {"passed", "failed", "blocked"}:
                auto_executed += 1

        tc_results.append(
            {
                "tc_id": tc_id,
                "ac_id": ac_id,
                "qa_type": qa_type,
                "layer": to_legacy_layer(qa_type),
                "automation": automation,
                "status": tc_status,
                "layer_status": layer_status,
                "assertion_count": assertion_count,
                "command": effective_command,
                "run_id": run_id,
                "evidence_path": str(item.get("evidence_path") or ""),
                "evidence_ref": evidence_ref,
                "execution_fingerprint": str(tc_payload.get("execution_fingerprint") or ""),
                "started_at": str(tc_payload.get("started_at") or ""),
                "ended_at": str(tc_payload.get("ended_at") or ""),
                "junit_path": str(tc_payload.get("junit_path") or ""),
                "junit_valid": bool(tc_payload.get("junit_valid")),
            }
        )

    total = len(tc_results)
    pass_rate = float(passed) / float(total or 1)
    automation_rate = float(auto_executed) / float(auto_total or 1)
    return {
        "summary": {
            "cases_total": total,
            "passed": passed,
            "failed": failed,
            "blocked": blocked,
            "pending": pending,
            "pass_rate": round(pass_rate, 4),
            "automation_rate": round(automation_rate, 4),
            "auto_cases_total": auto_total,
            "auto_cases_executed": auto_executed,
        },
        "tc_results": tc_results,
    }


def _write_evidence_signature_chain(project_root: Path, *, run_id: str, summary_path: Path) -> str:
    chain_path = project_root / ".beacon" / "evidence-signature-chain.json"
    manifest_path = project_root / ".beacon" / "evidence-manifest.json"
    chain_path.parent.mkdir(parents=True, exist_ok=True)

    existing: list[dict[str, Any]] = []
    if chain_path.exists():
        try:
            payload = json.loads(chain_path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                existing = [x for x in payload if isinstance(x, dict)]
        except Exception:  # noqa: BLE001
            existing = []

    summary_sha = hashlib.sha256(summary_path.read_bytes()).hexdigest() if summary_path.exists() else ""
    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest() if manifest_path.exists() else ""
    entry = {
        "run_id": run_id,
        "generated_at": datetime.now().isoformat(),
        "summary_path": str(summary_path.relative_to(project_root)) if summary_path.exists() else "",
        "summary_sha256": summary_sha,
        "manifest_path": str(manifest_path.relative_to(project_root)) if manifest_path.exists() else "",
        "manifest_sha256": manifest_sha,
    }
    existing.append(entry)
    existing = existing[-500:]
    chain_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(chain_path.relative_to(project_root))


def _append_flaky_history(project_root: Path, payload: dict[str, Any]) -> str:
    history_path = project_root / ".beacon" / "flaky-history.json"
    history: list[dict[str, Any]] = []
    if history_path.exists():
        try:
            loaded = json.loads(history_path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                history = [x for x in loaded if isinstance(x, dict)]
        except Exception:  # noqa: BLE001
            history = []
    history.append(payload)
    history = history[-1000:]
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(history_path.relative_to(project_root))


def _load_qa9_matrix(matrix_path: Path) -> dict[str, Any]:
    if not matrix_path.exists():
        return {"error": "missing", "path": str(matrix_path)}
    try:
        payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"error": "invalid_json", "path": str(matrix_path)}
    if not isinstance(payload, dict):
        return {"error": "invalid_schema", "path": str(matrix_path)}
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return {"error": "invalid_schema", "path": str(matrix_path)}
    return {"payload": payload}


def _qa9_commands_from_matrix(matrix_payload: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    entries = matrix_payload.get("entries")
    if not isinstance(entries, list):
        return out
    for item in entries:
        if not isinstance(item, dict):
            continue
        qa_type = normalize_qa_type(str(item.get("qa_type") or item.get("layer") or "").strip())
        command = str(item.get("command") or "").strip()
        automation = str(item.get("automation") or "auto").strip().lower()
        if qa_type not in QA9_TYPES:
            continue
        if automation not in {"auto", "hybrid"}:
            continue
        if command and qa_type not in out:
            out[qa_type] = command
    return out


def _collect_required_file_issues(
    *,
    project_root: Path,
    layer_results: list[dict[str, Any]],
    require_junit: bool,
    require_assertion_count: bool,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for layer in layer_results:
        status = str(layer.get("status", "")).lower()
        if status != "passed":
            continue
        name = str(layer.get("layer", ""))
        if require_assertion_count and int(layer.get("assertion_count", 0) or 0) <= 0:
            issues.append(
                {
                    "layer": name,
                    "reason_code": "assertion_count_zero_pass",
                    "message": f"layer {name} passed but assertion_count=0",
                }
            )
        if require_junit:
            junit_path = str(layer.get("junit_path") or "").strip()
            if not junit_path:
                issues.append(
                    {
                        "layer": name,
                        "reason_code": "junit_missing_or_invalid",
                        "message": f"layer {name} missing junit.xml",
                    }
                )
                continue
            full = Path(junit_path)
            if not full.is_absolute():
                full = project_root / full
            if not _is_valid_junit_file(full):
                issues.append(
                    {
                        "layer": name,
                        "reason_code": "junit_missing_or_invalid",
                        "message": f"layer {name} junit invalid: {junit_path}",
                    }
                )
    return issues


@app.command()
def create(
    scope: str = typer.Argument("all", help="Test scope: ui/api-curl/unit/smoke/visual/all/full"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option(
        "auto",
        "--version",
        help="Target docs/version context (auto=largest docs semver).",
    ),
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
    visual_command: Optional[str] = typer.Option(None, "--visual-command", help="Real visual regression command"),
    interface_command: Optional[str] = typer.Option(None, "--interface-command", help="Real interface/API test command"),
    contract_command: Optional[str] = typer.Option(None, "--contract-command", help="Real contract test command"),
    integration_command: Optional[str] = typer.Option(None, "--integration-command", help="Real integration test command"),
    functional_command: Optional[str] = typer.Option(None, "--functional-command", help="Real functional Web UI test command"),
    regression_command: Optional[str] = typer.Option(None, "--regression-command", help="Real regression test command"),
    exception_command: Optional[str] = typer.Option(None, "--exception-command", help="Real exception/negative test command"),
    compatibility_command: Optional[str] = typer.Option(None, "--compatibility-command", help="Real compatibility matrix test command"),
    qa_matrix_path: Optional[str] = typer.Option(
        None,
        "--qa-matrix-path",
        help="QA9 matrix JSON path (*.qa9-matrix.json).",
    ),
    qa_profile: str = typer.Option(
        "web-full",
        "--qa-profile",
        help="QA profile used when scope=qa9: web-core/web-full/custom",
    ),
    qa_types: Optional[list[str]] = typer.Option(
        None,
        "--qa-types",
        help="QA types for scope=qa9 (comma-separated or repeatable).",
    ),
    ui_runner: str = typer.Option(
        "playwright",
        "--ui-runner",
        help="Web UI automation runner: playwright/cypress/browser-use/agent-browser/midscene",
    ),
    compat_browsers: Optional[str] = typer.Option(
        None,
        "--compat-browsers",
        help="Compatibility browsers list, comma-separated.",
    ),
    compat_devices: Optional[str] = typer.Option(
        None,
        "--compat-devices",
        help="Compatibility devices list, comma-separated.",
    ),
    require_fresh_evidence: bool = typer.Option(
        False,
        "--require-fresh-evidence",
        help="Require matrix evidence path to include current run id.",
    ),
    require_junit: bool = typer.Option(
        False,
        "--require-junit",
        help="Require junit.xml evidence for passed layers (QA9 scope defaults to required).",
    ),
    require_assertion_count: bool = typer.Option(
        False,
        "--require-assertion-count",
        help="Require assertion_count > 0 for passed layers (QA9 scope defaults to required).",
    ),
    rerun_flaky: int = typer.Option(
        0,
        "--rerun-flaky",
        help="Retry failed layer command N times for flaky isolation.",
    ),
    max_flaky_rate: float = typer.Option(
        0.02,
        "--max-flaky-rate",
        help="Maximum allowed flaky pass ratio [0,1].",
    ),
    visual_baseline_dir: Optional[str] = typer.Option(
        None,
        "--visual-baseline-dir",
        help="Visual baseline directory for file hash comparison",
    ),
    visual_current_dir: Optional[str] = typer.Option(
        None,
        "--visual-current-dir",
        help="Visual current directory for file hash comparison",
    ),
    visual_threshold: float = typer.Option(
        0.0,
        "--visual-threshold",
        help="Allowed visual mismatch ratio [0,1]",
    ),
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
    resolved_version = resolve_target_version(project_root, version)

    typer.echo(f"Running automated tests: {scope}")
    typer.echo(f"Project: {project_root}")
    debug_mode = str(os.environ.get("BEACON_DEBUG", "")).strip().lower() in {"1", "true", "yes", "on"}

    scope_norm = (scope or "").strip().lower()
    is_qa9_scope = normalize_qa_type(scope_norm) == "qa9"
    effective_require_junit = bool(require_junit) or is_qa9_scope
    effective_require_assertion_count = bool(require_assertion_count) or is_qa9_scope
    selected_layers = _resolve_layers(scope_norm)
    if is_qa9_scope:
        selected_layers = parse_qa_types(qa_types, profile=qa_profile)
    if visual_threshold < 0 or visual_threshold > 1:
        raise typer.BadParameter("--visual-threshold must be between 0 and 1")
    if max_flaky_rate < 0 or max_flaky_rate > 1:
        raise typer.BadParameter("--max-flaky-rate must be between 0 and 1")
    if rerun_flaky < 0:
        raise typer.BadParameter("--rerun-flaky must be >= 0")
    run_id = datetime.now().strftime("run-%Y%m%dT%H%M%S%f")
    evidence_root = project_root / ".beacon" / "evidence" / "auto-test" / run_id
    evidence_root.mkdir(parents=True, exist_ok=True)
    raw_log_path = _raw_command_log_path(project_root)
    raw_log_path.parent.mkdir(parents=True, exist_ok=True)
    raw_log_path.touch(exist_ok=True)

    commands = {
        "ui": ui_command or "",
        "api-curl": api_curl_command or "",
        "unit": unit_command or "",
        "smoke": smoke_command or "",
        "visual": visual_command or "",
        "functional": functional_command or ui_command or "",
        "interface": interface_command or api_curl_command or "",
        "contract": contract_command or "",
        "integration": integration_command or "",
        "regression": regression_command or "",
        "exception": exception_command or "",
        "compatibility": compatibility_command or "",
    }
    explicit_layer_overrides = {layer: cmd for layer, cmd in commands.items() if str(cmd).strip()}
    # config defaults < cli explicit overrides
    for layer, cmd in _load_layer_commands_from_config(config).items():
        if not commands.get(layer):
            commands[layer] = cmd
    parsed_layer_overrides = _parse_layer_overrides(layer_command)
    explicit_layer_overrides.update(parsed_layer_overrides)
    commands.update(parsed_layer_overrides)

    compat_browsers_list = [x.strip().lower() for x in str(compat_browsers or "").split(",") if x.strip()]
    compat_devices_list = [x.strip().lower() for x in str(compat_devices or "").split(",") if x.strip()]
    compat_required_pairs: list[dict[str, str]] = []

    active_matrix_path = matrix_path
    qa9_matrix_payload: dict[str, Any] | None = None
    qa9_matrix_resolve_path = qa_matrix_path or matrix_path
    if is_qa9_scope and qa9_matrix_resolve_path:
        loaded = _load_qa9_matrix(Path(qa9_matrix_resolve_path))
        if loaded.get("payload"):
            qa9_matrix_payload = loaded["payload"]
            active_matrix_path = qa9_matrix_resolve_path
            selected_layers = parse_qa_types(qa9_matrix_payload.get("qa_types"), profile=qa_profile)
            for layer, cmd in _qa9_commands_from_matrix(qa9_matrix_payload).items():
                if not commands.get(layer):
                    commands[layer] = cmd
            compatibility = qa9_matrix_payload.get("compatibility_matrix")
            if isinstance(compatibility, dict):
                compat_required_pairs = _normalize_required_pairs(compatibility.get("required_pairs"))
                if not compat_browsers_list and isinstance(compatibility.get("browsers"), list):
                    compat_browsers_list = [
                        str(x).strip().lower()
                        for x in compatibility.get("browsers", [])
                        if str(x).strip()
                    ]
                if not compat_devices_list and isinstance(compatibility.get("devices"), list):
                    compat_devices_list = [
                        str(x).strip().lower()
                        for x in compatibility.get("devices", [])
                        if str(x).strip()
                    ]
        else:
            typer.echo(
                f"⚠ QA9 matrix load failed: {loaded.get('error', 'unknown')} ({loaded.get('path', qa9_matrix_resolve_path)})"
            )

    if not compat_required_pairs and compat_browsers_list and compat_devices_list:
        compat_required_pairs = _expand_pairs(compat_browsers_list, compat_devices_list)

    if is_qa9_scope:
        for layer in selected_layers:
            if not commands.get(layer):
                commands[layer] = default_command_for_qa_type(layer, ui_runner=ui_runner)

    spec_fingerprint_payload = load_latest_spec_fingerprint(project_root, version=resolved_version)
    if not str(spec_fingerprint_payload.get("fingerprint_hash", "")).strip():
        spec_fingerprint_payload = generate_spec_fingerprint(
            project_root,
            run_id=run_id,
            version=resolved_version,
        )
    spec_fingerprint_hash = str(spec_fingerprint_payload.get("fingerprint_hash", "")).strip()

    test_status: dict = {
        "scope": scope,
        "timestamp": datetime.now().isoformat(),
        "project": str(project_root),
        "version": resolved_version,
        "run_id": run_id,
        "spec_fingerprint_hash": spec_fingerprint_hash,
        "status": "running",
        "selected_layers": selected_layers,
        "execution": {
            "run_id": run_id,
            "version": resolved_version,
            "evidence_dir": str(evidence_root.relative_to(project_root)),
            "spec_fingerprint": {
                "fingerprint_hash": spec_fingerprint_hash,
                "version": resolved_version,
                "generated_at": str(spec_fingerprint_payload.get("generated_at", "")),
            },
            "layers": [],
        },
    }
    if is_qa9_scope:
        test_status["qa9"] = {
            "qa_profile": qa_profile,
            "qa_types": selected_layers,
            "qa_matrix_path": active_matrix_path or "",
            "ui_runner": ui_runner,
            "quality_requirements": {
                "require_junit": effective_require_junit,
                "require_assertion_count": effective_require_assertion_count,
            },
            "compatibility": {
                "browsers": compat_browsers_list,
                "devices": compat_devices_list,
                "required_pairs": compat_required_pairs,
                "executed_pairs": [],
            },
        }
    test_status["quality_issues"] = []

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
        or "functional" in selected_layers
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
            layer_extra_env: dict[str, str] = {}
            if layer == "compatibility":
                layer_extra_env = {
                    "BEACON_COMPAT_EVIDENCE_PATH": str(evidence_root / "compatibility" / "pair-evidence.json"),
                    "BEACON_COMPAT_REQUIRED_PAIRS": json.dumps(compat_required_pairs, ensure_ascii=False),
                    "BEACON_COMPAT_BROWSERS": ",".join(compat_browsers_list),
                    "BEACON_COMPAT_DEVICES": ",".join(compat_devices_list),
                }
            result = _run_layer_command(
                layer=layer,
                command=command,
                project_root=project_root,
                layer_dir=layer_dir,
                retries=rerun_flaky,
                run_id=run_id,
                stage="verify",
                extra_env=layer_extra_env,
            )
            if (
                layer == "visual"
                and visual_baseline_dir
                and visual_current_dir
                and str(result.get("status")) == "passed"
            ):
                comparison = _run_visual_comparison(
                    project_root=project_root,
                    layer_dir=layer_dir,
                    baseline_dir=visual_baseline_dir,
                    current_dir=visual_current_dir,
                    threshold=visual_threshold,
                )
                result["visual_compare"] = comparison["report"]
                result["evidence_ref"] = list(dict.fromkeys(result.get("evidence_ref", []) + comparison["evidence_ref"]))
                if comparison["status"] != "passed":
                    result["status"] = "failed"
                    result["reason_code"] = "visual_diff_exceeded_threshold"
            layer_results.append(result)
            continue

        if layer == "visual" and visual_baseline_dir and visual_current_dir:
            comparison = _run_visual_comparison(
                project_root=project_root,
                layer_dir=layer_dir,
                baseline_dir=visual_baseline_dir,
                current_dir=visual_current_dir,
                threshold=visual_threshold,
            )
            layer_results.append(
                {
                    "layer": "visual",
                    "status": comparison["status"],
                    "reason_code": "visual_compare_only",
                    "command": None,
                    "exit_code": None,
                    "evidence_ref": comparison["evidence_ref"],
                    "visual_compare": comparison["report"],
                }
            )
            continue

        if layer in {"ui", "functional"} and ui_guard is not None:
            payload = {
                "layer": layer,
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

    if is_qa9_scope and isinstance(test_status.get("qa9"), dict):
        compat_block = test_status["qa9"].get("compatibility")
        if isinstance(compat_block, dict) and "compatibility" in selected_layers:
            compat_layer = next(
                (
                    item
                    for item in layer_results
                    if isinstance(item, dict) and normalize_qa_type(str(item.get("layer") or "")) == "compatibility"
                ),
                {},
            )
            compat_status = str(compat_layer.get("status") or "").strip().lower()
            pair_evidence_path = evidence_root / "compatibility" / "pair-evidence.json"
            executed_pairs = (
                _load_executed_pairs_from_evidence(pair_evidence_path)
                if compat_status == "passed"
                else []
            )
            compat_block["executed_pairs"] = executed_pairs
            pair_evidence_path.parent.mkdir(parents=True, exist_ok=True)
            pair_payload = {
                "run_id": run_id,
                "status": compat_status or "not_executed",
                "required_pairs": compat_required_pairs,
                "executed_pairs": executed_pairs,
                "generated_at": datetime.now().isoformat(),
            }
            pair_evidence_path.write_text(json.dumps(pair_payload, ensure_ascii=False, indent=2), encoding="utf-8")
            execution_payload.setdefault("artifacts", []).append(str(pair_evidence_path.relative_to(project_root)))
            if compat_status == "passed" and compat_required_pairs:
                missing_pairs = sorted(
                    set((x["browser"], x["device"]) for x in compat_required_pairs)
                    - set((x["browser"], x["device"]) for x in executed_pairs)
                )
                if missing_pairs:
                    test_status["quality_issues"].append(
                        {
                            "reason_code": "compatibility_execution_missing",
                            "message": f"compatibility pair evidence missing: {missing_pairs[:10]}",
                        }
                    )

    matrix_report = None
    legacy_matrix_report = None
    if active_matrix_path:
        matrix_report = _write_matrix_evidence(
            project_root=project_root,
            matrix_path=Path(active_matrix_path),
            run_id=run_id,
            layer_results=layer_results,
            require_fresh_evidence=require_fresh_evidence,
        )
        execution_payload["matrix_report"] = matrix_report
        active_matrix_obj = Path(active_matrix_path)
        if (
            is_qa9_scope
            and active_matrix_obj.name.endswith(".qa9-matrix.json")
        ):
            legacy_matrix_path = active_matrix_obj.with_name(
                active_matrix_obj.name.replace(".qa9-matrix.json", ".ac-test-matrix.json")
            )
            if legacy_matrix_path.exists():
                legacy_matrix_report = _write_matrix_evidence(
                    project_root=project_root,
                    matrix_path=legacy_matrix_path,
                    run_id=run_id,
                    layer_results=layer_results,
                    require_fresh_evidence=False,
                )
                execution_payload["legacy_matrix_report"] = legacy_matrix_report

    qa9_tc_execution_map: dict[str, dict[str, Any]] = {}
    qa9_tc_failure_detected = False
    if qa9_matrix_payload:
        qa9_tc_execution_map = _execute_qa9_tc_entries(
            project_root=project_root,
            run_id=run_id,
            evidence_root=evidence_root,
            matrix_payload=qa9_matrix_payload,
            commands=commands,
            explicit_layer_overrides=explicit_layer_overrides,
            rerun_flaky=rerun_flaky,
            compat_required_pairs=compat_required_pairs,
            compat_browsers_list=compat_browsers_list,
            compat_devices_list=compat_devices_list,
        )
        qa9_tc_execution_path = evidence_root / "qa9" / "tc-execution-map.json"
        qa9_tc_execution_path.parent.mkdir(parents=True, exist_ok=True)
        qa9_tc_execution_path.write_text(
            json.dumps(qa9_tc_execution_map, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        execution_payload.setdefault("artifacts", []).append(str(qa9_tc_execution_path.relative_to(project_root)))

    required_file_issues = _collect_required_file_issues(
        project_root=project_root,
        layer_results=layer_results,
        require_junit=effective_require_junit,
        require_assertion_count=effective_require_assertion_count,
    )
    if required_file_issues:
        test_status["quality_issues"].extend(required_file_issues)

    if matrix_report and matrix_report.get("status") == "freshness_violation":
        test_status["quality_issues"].append(
            {
                "reason_code": "evidence_replay_detected",
                "message": "matrix evidence path does not include current run id",
                "details": matrix_report.get("freshness_violations", []),
            }
        )

    if qa9_matrix_payload:
        execution_payload["qa9_matrix_schema_version"] = qa9_matrix_payload.get("schema_version")
        auto_missing_command: list[str] = []
        entries = qa9_matrix_payload.get("entries")
        if isinstance(entries, list):
            for item in entries:
                if not isinstance(item, dict):
                    continue
                automation = str(item.get("automation") or "auto").strip().lower()
                if automation not in {"auto", "hybrid"}:
                    continue
                qa_type = normalize_qa_type(str(item.get("qa_type") or item.get("layer") or "").strip())
                command = str(item.get("command") or commands.get(qa_type) or "").strip()
                if not command:
                    auto_missing_command.append(str(item.get("tc_id") or qa_type))
        if auto_missing_command:
            test_status["quality_issues"].append(
                {
                    "reason_code": "qa9_command_missing_auto_case",
                    "message": f"auto cases missing command: {auto_missing_command[:20]}",
                }
            )
        tc_backfill = _build_qa9_tc_backfill(
            matrix_payload=qa9_matrix_payload,
            layer_results=layer_results,
            run_id=run_id,
            tc_execution_map=qa9_tc_execution_map,
        )
        summary = tc_backfill.get("summary") if isinstance(tc_backfill, dict) else {}
        if isinstance(summary, dict):
            qa9_tc_failure_detected = int(summary.get("failed", 0) or 0) > 0 or int(summary.get("blocked", 0) or 0) > 0
        if isinstance(test_status.get("qa9"), dict):
            test_status["qa9"]["summary"] = tc_backfill.get("summary", {})
            test_status["qa9"]["tc_results"] = tc_backfill.get("tc_results", [])
        tc_backfill_path = evidence_root / "qa9" / "tc-results.json"
        tc_backfill_path.parent.mkdir(parents=True, exist_ok=True)
        tc_backfill_path.write_text(json.dumps(tc_backfill, ensure_ascii=False, indent=2), encoding="utf-8")
        execution_payload.setdefault("artifacts", []).append(str(tc_backfill_path.relative_to(project_root)))

    passed_layers = [x for x in layer_results if str(x.get("status")) == "passed"]
    flaky_pass_count = sum(1 for x in passed_layers if bool(x.get("was_flaky")))
    flaky_rate = float(flaky_pass_count) / float(len(passed_layers) or 1)
    execution_payload["flaky"] = {
        "pass_count": len(passed_layers),
        "flaky_pass_count": flaky_pass_count,
        "flaky_rate": round(flaky_rate, 4),
        "max_flaky_rate": max_flaky_rate,
    }
    if flaky_rate > max_flaky_rate:
        test_status["quality_issues"].append(
            {
                "reason_code": "flaky_rate_exceeded",
                "message": f"flaky_rate {round(flaky_rate, 4)} > {max_flaky_rate}",
            }
        )

    status_from_layers = _merge_status_from_layers(layer_results)
    if require_ui_actions and missing_actions:
        status_from_layers = "failed"
    if qa9_tc_failure_detected:
        status_from_layers = "failed"
    if test_status.get("quality_issues"):
        status_from_layers = "failed"
    test_status["status"] = status_from_layers

    summary_path = evidence_root / "summary.json"
    summary_path.write_text(json.dumps(test_status, ensure_ascii=False, indent=2), encoding="utf-8")
    execution_payload.setdefault("artifacts", []).append(str(summary_path.relative_to(project_root)))
    flaky_history_ref = _append_flaky_history(
        project_root,
        {
            "run_id": run_id,
            "timestamp": test_status.get("timestamp"),
            "scope": scope,
            "status": test_status.get("status"),
            "selected_layers": selected_layers,
            "flaky": execution_payload.get("flaky", {}),
        },
    )
    execution_payload.setdefault("artifacts", []).append(flaky_history_ref)

    status_file = project_root / ".beacon" / "auto-test-status.json"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    status_file.write_text(json.dumps(test_status, ensure_ascii=False, indent=2), encoding="utf-8")

    gate_report_path = project_root / ".beacon" / "gate-report.json"
    gate_issues = [
        {
            "reason_code": str(item.get("reason_code") or "auto_test_issue"),
            "message": str(item.get("message") or item.get("reason_code") or "auto-test quality issue"),
            "blocked": True,
        }
        for item in test_status.get("quality_issues", [])
        if isinstance(item, dict)
    ]
    gate_status = "Pass" if str(test_status.get("status")) == "passed" else "Blocked"
    write_json(
        gate_report_path,
        {
            "stage": "verify",
            "mode": "strict",
            "status": gate_status,
            "issues": gate_issues,
            "run_id": run_id,
            "version": resolved_version,
            "updated_at": now_iso(),
        },
    )

    manifest_refs: list[str] = []
    for layer in layer_results:
        if not isinstance(layer, dict):
            continue
        refs = layer.get("evidence_ref")
        if isinstance(refs, list):
            manifest_refs.extend(str(x) for x in refs if str(x).strip())
    artifacts = execution_payload.get("artifacts")
    if isinstance(artifacts, list):
        manifest_refs.extend(str(x) for x in artifacts if str(x).strip())
    manifest_refs.extend(
        [
            str(summary_path.relative_to(project_root)),
            str(status_file.relative_to(project_root)),
            str(gate_report_path.relative_to(project_root)),
            str(_raw_command_log_path(project_root).relative_to(project_root)),
        ]
    )
    _update_evidence_manifest(project_root, manifest_refs, run_id=run_id, version=resolved_version)

    signature_chain_ref = _write_evidence_signature_chain(project_root, run_id=run_id, summary_path=summary_path)
    execution_payload.setdefault("artifacts", []).append(signature_chain_ref)
    status_file.write_text(json.dumps(test_status, ensure_ascii=False, indent=2), encoding="utf-8")
    _update_evidence_manifest(
        project_root,
        [signature_chain_ref, str(status_file.relative_to(project_root))],
        run_id=run_id,
        version=resolved_version,
    )

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
    if test_status.get("quality_issues"):
        typer.echo(f"  Quality Issues: {len(test_status['quality_issues'])}")
        if verbose:
            for item in test_status["quality_issues"]:
                typer.echo(f"    - {item.get('reason_code')}: {item.get('message')}")


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
        qa9 = status_data.get("qa9")
        if isinstance(qa9, dict):
            summary = qa9.get("summary")
            if isinstance(summary, dict):
                typer.echo(
                    "QA9 Summary: "
                    f"total={summary.get('cases_total', 0)} "
                    f"pass={summary.get('passed', 0)} "
                    f"fail={summary.get('failed', 0)} "
                    f"blocked={summary.get('blocked', 0)} "
                    f"automation_rate={summary.get('automation_rate', 0)}"
                )
        ui_guard = status_data.get("ui_guard")
        if isinstance(ui_guard, dict):
            typer.echo(f"UI Guard: {ui_guard.get('reason_code', 'N/A')}")
            typer.echo(f"UI Detail: {ui_guard.get('detail', 'N/A')}")
        key_guard = status_data.get("key_action_guard")
        if isinstance(key_guard, dict):
            typer.echo(f"UI Key Actions: {key_guard.get('status', 'N/A')}")
        quality_issues = status_data.get("quality_issues")
        if isinstance(quality_issues, list):
            typer.echo(f"Quality Issues: {len(quality_issues)}")


@app.command("import-qa-use")
def import_qa_use(
    input_file: str = typer.Argument(..., help="qa-use export JSON path"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    scope: str = typer.Option("qa9", "--scope", help="Scope label for imported status"),
):
    """Import qa-use suite/testRun results into Beacon auto-test status."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, "auto")
    source = Path(input_file)
    if not source.exists():
        raise typer.BadParameter(f"input file not found: {source}")

    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise typer.BadParameter("input JSON must be an object")

    suite = payload.get("suiteRun", payload.get("suite", {}))
    test_runs = payload.get("testRuns", payload.get("tests", []))
    if not isinstance(test_runs, list):
        test_runs = []

    layer_rollup: dict[str, dict[str, Any]] = {}
    for item in test_runs:
        if not isinstance(item, dict):
            continue
        qa_type = normalize_qa_type(str(item.get("qa_type") or item.get("layer") or "functional").strip())
        test_status = str(item.get("status") or "").strip().lower()
        mapped = "passed" if test_status in {"pass", "passed", "success"} else "failed"
        existing = layer_rollup.get(qa_type)
        if existing is None:
            layer_rollup[qa_type] = {
                "layer": qa_type,
                "status": mapped,
                "command": "qa-use:import",
                "exit_code": 0 if mapped == "passed" else 1,
                "assertion_count": 1 if mapped == "passed" else 0,
                "execution_fingerprint": hashlib.sha256(
                    f"qa-use:{qa_type}:{test_status}:{item.get('id', item.get('label', ''))}".encode("utf-8")
                ).hexdigest(),
                "started_at": datetime.now().isoformat(),
                "ended_at": datetime.now().isoformat(),
                "evidence_ref": [],
                "junit_path": "",
                "junit_valid": False,
            }
            continue
        if mapped == "failed":
            existing["status"] = "failed"
            existing["exit_code"] = 1

    layers = [layer_rollup[key] for key in sorted(layer_rollup.keys())]
    has_failed = any(str(item.get("status")) == "failed" for item in layers)
    run_id = datetime.now().strftime("run-%Y%m%dT%H%M%S%f")
    spec_fingerprint_payload = load_latest_spec_fingerprint(project_root, version=resolved_version)
    if not str(spec_fingerprint_payload.get("fingerprint_hash", "")).strip():
        spec_fingerprint_payload = generate_spec_fingerprint(
            project_root,
            run_id=run_id,
            version=resolved_version,
        )
    spec_fingerprint_hash = str(spec_fingerprint_payload.get("fingerprint_hash", "")).strip()
    status_payload = {
        "scope": scope,
        "timestamp": datetime.now().isoformat(),
        "project": str(project_root),
        "version": resolved_version,
        "run_id": run_id,
        "spec_fingerprint_hash": spec_fingerprint_hash,
        "status": "failed" if has_failed else "passed",
        "selected_layers": [str(item.get("layer")) for item in layers],
        "execution": {
            "run_id": run_id,
            "version": resolved_version,
            "source": "qa-use",
            "evidence_dir": "",
            "spec_fingerprint": {
                "fingerprint_hash": spec_fingerprint_hash,
                "version": resolved_version,
                "generated_at": str(spec_fingerprint_payload.get("generated_at", "")),
            },
            "layers": layers,
            "import_source": str(source),
            "suite": suite if isinstance(suite, dict) else {},
        },
        "quality_issues": [],
    }

    status_file = project_root / ".beacon" / "auto-test-status.json"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    status_file.write_text(json.dumps(status_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    typer.echo(f"✓ qa-use results imported: {status_file}")
    typer.echo(f"  Layers: {', '.join(status_payload['selected_layers']) or '-'}")
    typer.echo(f"  Status: {status_payload['status']}")


if __name__ == "__main__":
    app()
