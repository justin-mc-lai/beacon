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
from xml.sax.saxutils import escape as xml_escape
from typing import Any, Optional
from urllib.parse import urlsplit

import typer

from beacon.utils.browser_task_compiler import build_browser_task, default_browser_runner_command, write_browser_task
from beacon.utils.coverage import write_coverage_summary
from beacon.utils.python_exec import normalize_qa_shell_command
from beacon.utils.qa9 import (
    QA9_TYPES,
    default_command_for_qa_type,
    normalize_qa_type,
    parse_qa_types,
    to_legacy_layer,
)
from beacon.utils.qa_runtime import (
    load_current_qa_session,
    load_qa_session,
    load_qa_status,
    qa_session_manifest_path,
    write_qa_status,
)
from beacon.utils.evidence_manifest import merge_manifest_entries
from beacon.utils.runtime import append_jsonl, now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
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
DEFAULT_LAYER_TIMEOUT_SECONDS = 300
PROTECTED_SURFACE_HOST_HINTS = ("vercel.app",)
ATTACHED_BROWSER_RUNNER_TYPES = {
    "web-access",
    "agent-browser",
    "playwright",
    "playwright-cli",
    "playwright-cdp",
    "playwright-attach",
    "attached-chrome",
    "chrome-cdp",
}
PLACEHOLDER_BROWSER_RUNNER_STATUSES = {
    "task-only",
    "fallback-no-task",
    "missing-task",
    "browser-use-unavailable",
    "fallback-browser-use-unavailable",
    "fallback-executed",
    "deterministic-command-no-task",
    "deterministic-command-browser-use-unavailable",
    "deterministic-command-executed",
}


def _semver_tuple(value: str | None) -> tuple[int, int, int]:
    raw = str(value or "").strip().lower()
    if raw.startswith("v"):
        raw = raw[1:]
    parts = raw.split(".")
    out: list[int] = []
    for part in parts[:3]:
        digits = "".join(ch for ch in part if ch.isdigit())
        out.append(int(digits) if digits else 0)
    while len(out) < 3:
        out.append(0)
    return (out[0], out[1], out[2])


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
    output_payload: dict[str, Any] = {
        "schema_version": "1.0",
        "entries": merge_manifest_entries(
            project_root,
            existing_entries=entries,
            evidence_refs=evidence_refs,
            exclude_paths={manifest_rel},
        ),
        "updated_at": now_iso(),
    }
    next_run_id = str(run_id or payload.get("run_id") or "").strip()
    next_version = str(version or payload.get("version") or "").strip()
    existing_version = str(payload.get("version") or "").strip()
    if existing_version and next_version and _semver_tuple(existing_version) > _semver_tuple(next_version):
        next_version = existing_version
        next_run_id = str(payload.get("run_id") or "").strip() or next_run_id
    existing_run_id = str(payload.get("run_id") or "").strip()
    if existing_version == next_version and existing_run_id.startswith("run-v") and existing_run_id.endswith("release"):
        next_run_id = existing_run_id
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


def _normalize_browser_runner_type(value: str | None) -> str:
    runner = str(value or "").strip().lower().replace("_", "-")
    if runner in {"playwright-cli-cdp", "playwright-cli-attach", "playwright-cdp", "playwright-attach", "chrome-cdp"}:
        return "playwright-cdp"
    if runner in {"attached-browser", "attached-chrome"}:
        return "attached-chrome"
    return runner


def _is_protected_browser_surface(target_url: str, session: dict[str, Any]) -> bool:
    raw_target = str(target_url or "").strip()
    raw_origin = str(session.get("origin") or "").strip() if isinstance(session, dict) else ""
    for raw in (raw_target, raw_origin):
        if not raw:
            continue
        try:
            parts = urlsplit(raw if "://" in raw else f"https://{raw.lstrip('/')}")
        except Exception:
            continue
        host = str(parts.netloc or "").strip().lower()
        if any(host.endswith(suffix) for suffix in PROTECTED_SURFACE_HOST_HINTS):
            return True
    return False


def _browser_session_bridge_present(session: dict[str, Any]) -> bool:
    if not isinstance(session, dict) or not session:
        return False
    return any(
        str(session.get(key) or "").strip()
        for key in ("session_id", "manifest_ref", "profile_ref", "cookies_ref", "storage_state_ref")
    )


def resolve_browser_runtime_admission(
    *,
    item: dict[str, Any],
    active_browser_session: dict[str, Any],
) -> dict[str, Any]:
    target_url = str(item.get("target_url") or item.get("url") or "").strip()
    requested_runner = _normalize_browser_runner_type(str(item.get("exploratory_runner") or ""))
    session_runner = _normalize_browser_runner_type(str(active_browser_session.get("runner_type") or ""))
    protected_surface = _is_protected_browser_surface(target_url, active_browser_session)
    session_bridge_present = _browser_session_bridge_present(active_browser_session)
    attached_runner_available = session_bridge_present and (
        session_runner in ATTACHED_BROWSER_RUNNER_TYPES or requested_runner in {"agent-browser", "web-access"}
    )
    preferred_runner = requested_runner or "playwright"
    if protected_surface:
        if session_runner == "web-access":
            preferred_runner = "web-access"
        elif session_runner in {"agent-browser", "attached-chrome"}:
            preferred_runner = "agent-browser"
        elif session_runner == "playwright-cdp":
            preferred_runner = "playwright-cdp"
        elif not session_bridge_present:
            preferred_runner = ""
    if protected_surface and not session_bridge_present:
        return {
            "status": "blocked",
            "reason_code": "protected_surface_session_bridge_missing",
            "protected_surface": True,
            "session_bridge_present": False,
            "attached_runner_available": False,
            "preferred_runner": "",
            "requested_runner": requested_runner,
            "session_runner": session_runner,
            "target_url": target_url,
        }
    if protected_surface and not attached_runner_available:
        return {
            "status": "blocked",
            "reason_code": "protected_surface_runner_priority_unavailable",
            "protected_surface": True,
            "session_bridge_present": session_bridge_present,
            "attached_runner_available": False,
            "preferred_runner": "",
            "requested_runner": requested_runner,
            "session_runner": session_runner,
            "target_url": target_url,
        }
    return {
        "status": "ready",
        "reason_code": "",
        "protected_surface": protected_surface,
        "session_bridge_present": session_bridge_present,
        "attached_runner_available": attached_runner_available,
        "preferred_runner": preferred_runner,
        "requested_runner": requested_runner,
        "session_runner": session_runner,
        "target_url": target_url,
    }


def _browser_evidence_authenticity(
    *,
    explore_bundle: dict[str, Any],
    replay_bundle: dict[str, Any],
    admission: dict[str, Any],
) -> dict[str, Any]:
    admission_status = str(admission.get("status") or "").strip().lower()
    runner_statuses = {
        str(bundle.get("status") or "").strip().lower()
        for bundle in (explore_bundle, replay_bundle)
        if isinstance(bundle, dict) and str(bundle.get("status") or "").strip()
    }
    real_fallback_execution = False
    for bundle in (explore_bundle, replay_bundle):
        if not isinstance(bundle, dict):
            continue
        bundle_status = str(bundle.get("status") or "").strip().lower()
        if bundle_status not in PLACEHOLDER_BROWSER_RUNNER_STATUSES:
            continue
        report_ref = str(bundle.get("report_ref") or "").strip()
        result_ref = str(bundle.get("result_ref") or "").strip()
        task_ref = str(bundle.get("task_ref") or "").strip()
        if report_ref and result_ref and task_ref:
            real_fallback_execution = True
            break
    placeholder_only = admission_status == "blocked" or (
        bool(runner_statuses)
        and runner_statuses.issubset(PLACEHOLDER_BROWSER_RUNNER_STATUSES)
        and not real_fallback_execution
    )
    authenticity = not placeholder_only
    reason_code = "browser_evidence_placeholder_only" if placeholder_only else ""
    if str(admission.get("status") or "") == "blocked" and not authenticity:
        reason_code = str(admission.get("reason_code") or reason_code)
    return {
        "status": "authentic" if authenticity else "placeholder_only",
        "authentic": authenticity,
        "reason_code": reason_code,
        "runner_statuses": sorted(runner_statuses),
        "real_fallback_execution": real_fallback_execution,
    }


def _write_browser_runner_learning_note(
    *,
    project_root: Path,
    version: str,
    feature: str,
    tc_id: str,
    admission: dict[str, Any],
    authenticity: dict[str, Any],
) -> str:
    version_root = project_root / "docs" / "beacon" / resolve_target_version(project_root, version) / ".machine" / "learning" / "qa"
    version_root.mkdir(parents=True, exist_ok=True)
    note_path = version_root / f"{feature_slug(feature)}--{tc_id.lower()}.json"
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "tc_id": tc_id,
        "discovered_at": now_iso(),
        "runner_attempted": str(admission.get("preferred_runner") or admission.get("requested_runner") or ""),
        "outcome": str(admission.get("status") or authenticity.get("status") or ""),
        "reason_code": str(admission.get("reason_code") or authenticity.get("reason_code") or ""),
        "fallback_runner": (
            "web-access"
            if str(admission.get("reason_code") or "") == "protected_surface_session_bridge_missing"
            else "attached-session-required"
        ),
        "expires_after_n_days": 30,
        "target_url": str(admission.get("target_url") or ""),
        "protected_surface": bool(admission.get("protected_surface")),
    }
    write_json(note_path, payload)
    return str(note_path.relative_to(project_root))


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


def _load_json_from_text(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    if not raw:
        return {}
    for start in (0, raw.find("{")):
        if start < 0:
            continue
        try:
            payload = json.loads(raw[start:])
        except Exception:  # noqa: BLE001
            continue
        return payload if isinstance(payload, dict) else {}
    return {}


def _structured_assertion_count(stdout_text: str, stderr_text: str) -> int:
    payload = _load_json_from_text(stdout_text) or _load_json_from_text(stderr_text)
    if not payload:
        return 0
    checks = payload.get("checks")
    if isinstance(checks, list) and checks:
        return len([item for item in checks if isinstance(item, dict)])
    for key in ("cases", "results", "eval_results", "grading_results"):
        value = payload.get(key)
        if isinstance(value, list) and value:
            return len(value)
    benchmark = payload.get("benchmark") if isinstance(payload.get("benchmark"), dict) else {}
    for key in ("cases", "covered_tc_ids", "covered_ac_ids"):
        value = benchmark.get(key)
        if isinstance(value, list) and value:
            return len(value)
    if "ok" in payload or "status" in payload:
        return 1
    return 0


_NATIVE_COMPILE_TEST_PATTERNS = (
    re.compile(r"\bgo\s+(?:build|test|vet)\b", re.I),
    re.compile(r"\bcargo\s+(?:build|test|check)\b", re.I),
    re.compile(r"\bmake\s+(?:test|check|build)\b", re.I),
)


def _is_native_compile_test_command(command: str) -> bool:
    normalized = " ".join(str(command or "").split())
    return any(pattern.search(normalized) for pattern in _NATIVE_COMPILE_TEST_PATTERNS)


def _native_toolchain_pass_assertion_count(
    command: str,
    stdout_text: str,
    stderr_text: str,
) -> int:
    if not _is_native_compile_test_command(command):
        return 0
    text = "\n".join([stdout_text or "", stderr_text or ""])
    if re.search(r"\bgo\s+test\b", command, flags=re.I):
        ok_lines = [
            line
            for line in text.splitlines()
            if re.search(r"^\s*ok\s+\S+", line, flags=re.I)
        ]
        if ok_lines:
            return len(ok_lines)
        if re.search(r"^\s*PASS\b", text, flags=re.M):
            return max(1, len(re.findall(r"^\s*PASS\b", text, flags=re.M)))
    if re.search(r"\bgo\s+(?:build|vet)\b", command, flags=re.I):
        return 1
    if re.search(r"\bcargo\s+test\b", command, flags=re.I):
        passed = len(re.findall(r"test\s+result:\s*ok\.", text, flags=re.I))
        return passed or 1
    if re.search(r"\bcargo\s+(?:build|check)\b", command, flags=re.I):
        return 1
    if re.search(r"\bmake\s+test\b", command, flags=re.I):
        return 1
    return 1


def _successful_command_assertion_evidence(
    *,
    command: str,
    stdout_text: str,
    project_root: Path,
) -> tuple[int, list[str]]:
    normalized_command = str(command or "").strip()
    if normalized_command.startswith("rg "):
        return len([line for line in str(stdout_text or "").splitlines() if line.strip()]), []

    if "beacon skill eval-kit benchmark" in normalized_command:
        match = re.search(r"benchmark:\s*(?P<path>\S+)", str(stdout_text or ""), flags=re.I)
        if not match:
            return 0, []
        benchmark_root = project_root / match.group("path")
        benchmark_json = benchmark_root / "benchmark" / "benchmark.json"
        payload = read_json(benchmark_json, {}) if benchmark_json.exists() else {}
        count = int(payload.get("case_count") or 0) if isinstance(payload, dict) else 0
        refs = [
            str(path.relative_to(project_root))
            for path in sorted(benchmark_root.rglob("*"))
            if path.is_file()
            and path.suffix.lower() in {".json", ".md"}
        ] if benchmark_root.exists() else []
        return count, refs

    return 0, []


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
        r"ℹ\s+pass\s+(?P<count>\d+)(?:\s|\n|$)",
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
    return _structured_assertion_count(stdout_text, stderr_text)


def _is_valid_junit_file(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore").strip().lower()
    if not text:
        return False
    return "<testsuite" in text or "<testsuites" in text


def _write_synthetic_junit(path: Path, *, layer: str, command: str, assertion_count: int, reason: str = "structured_cli_assertions") -> None:
    count = max(1, int(assertion_count or 0))
    cases = "\n".join(
        f'    <testcase classname="{xml_escape(layer)}" name="{xml_escape(reason)}-{index:03d}" />'
        for index in range(1, count + 1)
    )
    path.write_text(
        "\n".join(
            [
                '<?xml version="1.0" encoding="utf-8"?>',
                f'<testsuite name="{xml_escape(layer)}" tests="{count}" failures="0" errors="0" skipped="0">',
                f'  <properties><property name="command" value="{xml_escape(command)}" /></properties>',
                cases,
                "</testsuite>",
                "",
            ]
        ),
        encoding="utf-8",
    )


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
    timeout_seconds: int | None = None,
) -> dict:
    command = normalize_qa_shell_command(command, project_root=project_root)
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
    timeout = max(1, int(timeout_seconds or _layer_timeout_seconds()))
    timeout_expired: subprocess.TimeoutExpired[str] | None = None
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
        try:
            result = subprocess.run(
                command,
                cwd=project_root,
                shell=True,
                executable="/bin/bash",  # TC commands are bash-dialect (e.g. <(...)); /bin/sh rejects them
                text=True,
                capture_output=True,
                env=run_env,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            timeout_expired = exc
            stdout_value = exc.stdout or ""
            stderr_value = exc.stderr or ""
            if isinstance(stdout_value, bytes):
                stdout_value = stdout_value.decode("utf-8", errors="replace")
            if isinstance(stderr_value, bytes):
                stderr_value = stderr_value.decode("utf-8", errors="replace")
            result = subprocess.CompletedProcess(
                args=command,
                returncode=124,
                stdout=str(stdout_value),
                stderr=str(stderr_value),
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
        if timeout_expired is not None:
            break

    assert final_result is not None
    stdout_text = final_result.stdout or ""
    stderr_text = final_result.stderr or ""
    stdout_log.write_text(stdout_text, encoding="utf-8")
    stderr_log.write_text(stderr_text, encoding="utf-8")

    status = "passed" if final_result.returncode == 0 else ("blocked" if timeout_expired is not None else "failed")
    was_flaky = status == "passed" and any(item.get("exit_code") != 0 for item in run_records[:-1])
    assertion_count = _extract_assertion_count(stdout_text, stderr_text, junit_file=junit_file)
    structured_evidence_refs: list[str] = []
    if status == "passed" and assertion_count <= 0:
        command_assertions, command_refs = _successful_command_assertion_evidence(
            command=command,
            stdout_text=stdout_text,
            project_root=project_root,
        )
        if command_assertions > 0:
            assertion_count = command_assertions
            structured_evidence_refs = command_refs
        else:
            native_assertions = _native_toolchain_pass_assertion_count(
                command,
                stdout_text,
                stderr_text,
            )
            if native_assertions > 0:
                assertion_count = native_assertions
    if status == "passed" and assertion_count > 0 and not _is_valid_junit_file(junit_file):
        junit_reason = (
            "native_toolchain_pass"
            if _is_native_compile_test_command(command)
            else "structured_cli_assertions"
        )
        _write_synthetic_junit(
            junit_file,
            layer=layer,
            command=command,
            assertion_count=assertion_count,
            reason=junit_reason,
        )
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
        "reason_code": "runner_execution_timeout" if timeout_expired is not None else "",
        "timeout_seconds": timeout,
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
            *structured_evidence_refs,
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
    extra_refs = [
        str(path.relative_to(project_root))
        for path in sorted(layer_dir.rglob("*"))
        if path.is_file()
        and path not in {command_log, stdout_log, stderr_log, result_file, junit_file}
    ]
    payload["evidence_ref"] = list(dict.fromkeys([*payload["evidence_ref"], *extra_refs]))
    return payload


def _raw_matrix_layer(item: dict[str, Any]) -> str:
    return str(item.get("layer") or item.get("qa_type") or "").strip().lower()


def _is_negative_matrix_entry(item: dict[str, Any]) -> bool:
    return _raw_matrix_layer(item) in {"negative", "neg", "failure", "blocked"}


def _read_evidence_text(project_root: Path, payload: dict[str, Any], suffix: str) -> str:
    refs = payload.get("evidence_ref") if isinstance(payload.get("evidence_ref"), list) else []
    for ref in refs:
        ref_text = str(ref or "").strip()
        if not ref_text.endswith(suffix):
            continue
        path = project_root / ref_text
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace")
    return ""


def _negative_expected_block_observed(project_root: Path, run_payload: dict[str, Any]) -> tuple[bool, str]:
    command = str(run_payload.get("command") or "").strip()
    if "verify-promotion" not in command:
        return False, ""
    stdout_text = _read_evidence_text(project_root, run_payload, "stdout.log")
    stderr_text = _read_evidence_text(project_root, run_payload, "stderr.log")
    payload = _load_json_from_text(stdout_text) or _load_json_from_text(stderr_text)
    gate = payload.get("promotion_gate") if isinstance(payload.get("promotion_gate"), dict) else {}
    if gate and bool(gate.get("allowed")) is False and str(gate.get("status") or "") == "blocked":
        return True, "negative_promotion_gate_block_observed"
    return False, ""


def _mark_negative_expected_block_passed(
    *,
    project_root: Path,
    layer_dir: Path,
    run_payload: dict[str, Any],
    reason_code: str,
) -> dict[str, Any]:
    updated = dict(run_payload)
    updated["original_status"] = str(run_payload.get("status") or "")
    updated["original_exit_code"] = int(run_payload.get("exit_code") or 0)
    updated["status"] = "passed"
    updated["reason_code"] = reason_code
    updated["negative_expected_block_observed"] = True
    updated["assertion_count"] = max(1, int(run_payload.get("assertion_count") or 0))
    junit_file = layer_dir / "junit.xml"
    _write_synthetic_junit(
        junit_file,
        layer=str(updated.get("layer") or "contract"),
        command=str(updated.get("command") or ""),
        assertion_count=int(updated.get("assertion_count") or 1),
        reason=reason_code,
    )
    refs = updated.get("evidence_ref") if isinstance(updated.get("evidence_ref"), list) else []
    updated["junit_path"] = str(junit_file.relative_to(project_root))
    updated["junit_valid"] = True
    updated["evidence_ref"] = list(dict.fromkeys([*refs, str(junit_file.relative_to(project_root))]))
    result_file = layer_dir / "result.json"
    result_file.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")
    updated["evidence_ref"] = list(dict.fromkeys([*updated["evidence_ref"], str(result_file.relative_to(project_root))]))
    return updated


def _layer_timeout_seconds() -> int:
    raw = str(os.environ.get("BEACON_LAYER_TIMEOUT_SECONDS") or "").strip()
    if not raw:
        return DEFAULT_LAYER_TIMEOUT_SECONDS
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_LAYER_TIMEOUT_SECONDS
    return max(1, value)


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


def _load_executable_matrix(matrix_path: Path) -> dict[str, Any]:
    if not matrix_path.exists():
        return {"error": "missing", "path": str(matrix_path)}
    try:
        payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"error": "invalid_json", "path": str(matrix_path)}
    if not isinstance(payload, dict) or not isinstance(payload.get("entries"), list):
        return {"error": "invalid_schema", "path": str(matrix_path)}
    return {"payload": payload}


def _matrix_entry_layer(item: dict[str, Any]) -> str:
    return normalize_qa_type(str(item.get("qa_type") or item.get("layer") or "").strip())


def _execute_matrix_tc_entries(
    *,
    project_root: Path,
    run_id: str,
    evidence_root: Path,
    matrix_payload: dict[str, Any],
    commands: dict[str, str],
    rerun_flaky: int,
) -> list[dict[str, Any]]:
    entries = matrix_payload.get("entries")
    if not isinstance(entries, list):
        return []

    results: list[dict[str, Any]] = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        tc_id = str(item.get("tc_id") or "").strip()
        ac_id = str(item.get("ac_id") or "").strip()
        layer = _matrix_entry_layer(item)
        if not tc_id or not layer:
            continue
        command = str(item.get("command") or commands.get(layer) or "").strip()
        if not command:
            results.append(
                {
                    "layer": layer,
                    "tc_id": tc_id,
                    "ac_id": ac_id,
                    "status": "not_executed",
                    "reason_code": "matrix_command_missing",
                    "command": None,
                    "exit_code": None,
                    "evidence_ref": [],
                }
            )
            continue

        tc_dir = evidence_root / "matrix-tc" / tc_id
        result = _run_layer_command(
            layer=layer,
            command=command,
            project_root=project_root,
            layer_dir=tc_dir,
            retries=rerun_flaky,
            run_id=run_id,
            stage="verify",
            tc_id=tc_id,
            ac_id=ac_id,
        )
        results.append(result)
    return results


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


def _is_browser_required_entry(item: dict[str, Any]) -> bool:
    if bool(item.get("browser_required")):
        return True
    qa_type = normalize_qa_type(str(item.get("qa_type") or item.get("layer") or "").strip())
    return qa_type in {"functional", "compatibility"}


def _relative_project_ref(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _absolute_project_ref(project_root: Path, ref: str) -> str:
    raw = str(ref or "").strip()
    if not raw:
        return ""
    path = Path(raw)
    return str(path if path.is_absolute() else (project_root / path))


def _active_browser_session(project_root: Path) -> dict[str, Any]:
    current = load_current_qa_session(project_root)
    session_id = str(current.get("session_id") or "").strip()
    if not session_id:
        return {}
    payload = load_qa_session(project_root, session_id)
    if not payload:
        return {}
    manifest_path = qa_session_manifest_path(project_root, session_id)
    scopes = payload.get("scopes") if isinstance(payload.get("scopes"), list) else []
    return {
        "session_id": session_id,
        "runner_type": str(payload.get("runner_type") or "").strip(),
        "origin": str(payload.get("origin") or "").strip(),
        "manifest_ref": _relative_project_ref(project_root, manifest_path) if manifest_path.exists() else "",
        "profile_ref": str(payload.get("profile_ref") or "").strip(),
        "cookies_ref": str(payload.get("cookies_ref") or "").strip(),
        "storage_state_ref": str(payload.get("storage_state_ref") or "").strip(),
        "scopes": scopes,
    }


def _browser_session_env(project_root: Path, session: dict[str, Any]) -> dict[str, str]:
    if not isinstance(session, dict) or not session:
        return {}
    scopes = session.get("scopes") if isinstance(session.get("scopes"), list) else []
    return {
        key: value
        for key, value in {
            "BEACON_BROWSER_SESSION_ID": str(session.get("session_id") or "").strip(),
            "BEACON_BROWSER_SESSION_RUNNER": str(session.get("runner_type") or "").strip(),
            "BEACON_BROWSER_ORIGIN": str(session.get("origin") or "").strip(),
            "BEACON_BROWSER_SESSION_MANIFEST": _absolute_project_ref(project_root, str(session.get("manifest_ref") or "")),
            "BEACON_BROWSER_PROFILE_REF": _absolute_project_ref(project_root, str(session.get("profile_ref") or "")),
            "BEACON_BROWSER_COOKIES_REF": _absolute_project_ref(project_root, str(session.get("cookies_ref") or "")),
            "BEACON_BROWSER_STORAGE_STATE_REF": _absolute_project_ref(project_root, str(session.get("storage_state_ref") or "")),
            "BEACON_BROWSER_SESSION_SCOPES": ",".join(str(item).strip() for item in scopes if str(item).strip()),
        }.items()
        if str(value).strip()
    }


def _load_runner_bundle(project_root: Path, layer_dir: Path) -> dict[str, Any]:
    if not layer_dir.exists():
        return {}

    def _safe_load(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}
        return payload if isinstance(payload, dict) else {}

    report_path = layer_dir / "browser-runner-report.json"
    meta_path = layer_dir / "browser-runner-meta.json"
    result_path = layer_dir / "browser-runner-result.json"
    task_path = layer_dir / "browser-runner-task.json"
    transcript_path = layer_dir / "action-transcript.json"
    dom_path = layer_dir / "dom-snapshot.json"
    url_path = layer_dir / "current-url.txt"
    console_path = layer_dir / "browser-runner-console.log"
    network_path = layer_dir / "network-summary.json"

    report = _safe_load(report_path)
    meta = _safe_load(meta_path)
    result = _safe_load(result_path)
    artifact_refs = report.get("artifact_refs") if isinstance(report.get("artifact_refs"), dict) else {}
    session = report.get("session") if isinstance(report.get("session"), dict) else {}
    actions = report.get("actions") if isinstance(report.get("actions"), list) else []

    return {
        "runner": str(report.get("runner") or meta.get("runner") or result.get("runner") or "").strip(),
        "status": str(report.get("status") or meta.get("status") or result.get("status") or "").strip(),
        "task": str(report.get("task") or meta.get("task") or "").strip(),
        "target_url": str(report.get("target_url") or "").strip(),
        "execution_mode": str(report.get("execution_mode") or meta.get("execution_mode") or result.get("execution_mode") or "").strip(),
        "deterministic_command": str(report.get("deterministic_command") or meta.get("deterministic_command") or "").strip(),
        "fallback_cmd": str(report.get("fallback_cmd") or meta.get("fallback_cmd") or "").strip(),
        "browser_agent_requested": bool(report.get("browser_agent_requested") or meta.get("browser_agent_requested") or result.get("browser_agent_requested")),
        "browser_agent_available": bool(report.get("browser_agent_available") or meta.get("browser_agent_available") or result.get("browser_agent_available")),
        "browser_agent_executed": bool(report.get("browser_agent_executed") or meta.get("browser_agent_executed") or result.get("browser_agent_executed")),
        "deterministic_command_configured": bool(
            report.get("deterministic_command_configured")
            or meta.get("deterministic_command_configured")
            or result.get("deterministic_command_configured")
        ),
        "deterministic_command_executed": bool(
            report.get("deterministic_command_executed")
            or meta.get("deterministic_command_executed")
            or result.get("deterministic_command_executed")
        ),
        "compat_alias_used": bool(report.get("compat_alias_used") or meta.get("compat_alias_used") or result.get("compat_alias_used")),
        "compat_id": str(report.get("compat_id") or meta.get("compat_id") or result.get("compat_id") or "").strip(),
        "reason_code": str(report.get("reason_code") or meta.get("reason_code") or result.get("reason_code") or "").strip(),
        "repair_route": str(report.get("repair_route") or meta.get("repair_route") or result.get("repair_route") or "").strip(),
        "browser_agent_repair_route": str(
            report.get("browser_agent_repair_route")
            or meta.get("browser_agent_repair_route")
            or result.get("browser_agent_repair_route")
            or ""
        ).strip(),
        "deterministic_command_repair_route": str(
            report.get("deterministic_command_repair_route")
            or meta.get("deterministic_command_repair_route")
            or result.get("deterministic_command_repair_route")
            or ""
        ).strip(),
        "actions": [item for item in actions if isinstance(item, dict)],
        "session": session,
        "report_ref": _relative_project_ref(project_root, report_path) if report_path.exists() else "",
        "meta_ref": _relative_project_ref(project_root, meta_path) if meta_path.exists() else "",
        "result_ref": _relative_project_ref(project_root, result_path) if result_path.exists() else "",
        "task_ref": str(artifact_refs.get("task_ref") or (_relative_project_ref(project_root, task_path) if task_path.exists() else "")),
        "transcript_ref": str(artifact_refs.get("transcript_ref") or (_relative_project_ref(project_root, transcript_path) if transcript_path.exists() else "")),
        "dom_ref": str(artifact_refs.get("dom_ref") or (_relative_project_ref(project_root, dom_path) if dom_path.exists() else "")),
        "url_ref": str(artifact_refs.get("url_ref") or (_relative_project_ref(project_root, url_path) if url_path.exists() else "")),
        "console_ref": str(artifact_refs.get("console_ref") or (_relative_project_ref(project_root, console_path) if console_path.exists() else "")),
        "network_ref": str(artifact_refs.get("network_ref") or (_relative_project_ref(project_root, network_path) if network_path.exists() else "")),
        "session_manifest_ref": str(artifact_refs.get("session_manifest_ref") or session.get("manifest_ref") or ""),
        "profile_ref": str(artifact_refs.get("profile_ref") or session.get("profile_ref") or ""),
        "cookies_ref": str(artifact_refs.get("cookies_ref") or session.get("cookies_ref") or ""),
        "storage_state_ref": str(artifact_refs.get("storage_state_ref") or session.get("storage_state_ref") or ""),
    }


def _write_browser_evidence_pack(
    *,
    project_root: Path,
    tc_dir: Path,
    run_id: str,
    item: dict[str, Any],
    explore_payload: dict[str, Any],
    admission: dict[str, Any] | None = None,
    replay_payload: dict[str, Any] | None = None,
) -> dict[str, str]:
    pack_path = tc_dir / "browser-evidence-pack.json"
    transcript_path = tc_dir / "action-transcript.json"
    dom_path = tc_dir / "dom-snapshot.json"
    url_path = tc_dir / "current-url.txt"
    console_path = tc_dir / "console-summary.log"
    network_path = tc_dir / "network-summary.json"
    explore_bundle = _load_runner_bundle(project_root, tc_dir / "explore")
    replay_bundle = _load_runner_bundle(project_root, tc_dir / "replay") if isinstance(replay_payload, dict) else {}
    admission_payload = admission if isinstance(admission, dict) else {}
    session = explore_bundle.get("session") if isinstance(explore_bundle.get("session"), dict) else {}
    if not session and isinstance(replay_bundle.get("session"), dict):
        session = replay_bundle.get("session")
    actions = [
        *(
            explore_bundle.get("actions")
            if isinstance(explore_bundle.get("actions"), list)
            else []
        ),
        *(
            replay_bundle.get("actions")
            if isinstance(replay_bundle.get("actions"), list)
            else []
        ),
    ]
    transcript = {
        "run_id": run_id,
        "tc_id": str(item.get("tc_id") or ""),
        "scenario_id": str(item.get("scenario_id") or ""),
        "scenario_family": str(item.get("scenario_family") or ""),
        "qa_type": str(item.get("qa_type") or item.get("layer") or ""),
        "command": str(explore_payload.get("command") or item.get("command") or ""),
        "status": str(explore_payload.get("status") or ""),
        "target_url": str(explore_bundle.get("target_url") or item.get("target_url") or item.get("url") or "/"),
        "session": session,
        "actions": actions,
        "explore_runner_report_ref": str(explore_bundle.get("report_ref") or ""),
        "replay_runner_report_ref": str(replay_bundle.get("report_ref") or ""),
        "generated_at": datetime.now().isoformat(),
    }
    transcript_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")
    dom_ref = str(explore_bundle.get("dom_ref") or "")
    if not dom_ref:
        dom_path.write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "scenario_id": str(item.get("scenario_id") or ""),
                    "tc_id": str(item.get("tc_id") or ""),
                    "status": str(explore_payload.get("status") or ""),
                    "generated_at": datetime.now().isoformat(),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        dom_ref = str(dom_path.relative_to(project_root))
    url_ref = str(explore_bundle.get("url_ref") or "")
    if not url_ref:
        url_path.write_text(str(item.get("target_url") or item.get("url") or "/") + "\n", encoding="utf-8")
        url_ref = str(url_path.relative_to(project_root))
    console_ref = str(explore_bundle.get("console_ref") or "")
    if not console_ref:
        console_path.write_text(
            "\n".join(
                [
                    f"explore.status={str(explore_payload.get('status') or '')}",
                    f"replay.status={str((replay_payload or {}).get('status') or '')}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        console_ref = str(console_path.relative_to(project_root))
    network_ref = str(explore_bundle.get("network_ref") or "")
    if not network_ref:
        network_path.write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "scenario_id": str(item.get("scenario_id") or ""),
                    "requests": 0,
                    "replay_required": bool(item.get("replay_required")),
                    "generated_at": datetime.now().isoformat(),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        network_ref = str(network_path.relative_to(project_root))
    replay_ref = ""
    if isinstance(replay_payload, dict):
        refs = replay_payload.get("evidence_ref") if isinstance(replay_payload.get("evidence_ref"), list) else []
        replay_ref = str(refs[-1]).strip() if refs else ""
    authenticity = _browser_evidence_authenticity(
        explore_bundle=explore_bundle,
        replay_bundle=replay_bundle,
        admission=admission_payload,
    )
    pack_payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "tc_id": str(item.get("tc_id") or ""),
        "source_tc_id": str(item.get("source_tc_id") or item.get("tc_id") or ""),
        "scenario_id": str(item.get("scenario_id") or ""),
        "scenario_family": str(item.get("scenario_family") or ""),
        "browser_required": True,
        "exploratory_runner": str(item.get("exploratory_runner") or "agent-browser"),
        "deterministic_runner": str(item.get("deterministic_runner") or "playwright"),
        "replay_required": bool(item.get("replay_required")),
        "status": str((replay_payload or {}).get("status") or explore_payload.get("status") or ""),
        "runtime_admission": admission_payload,
        "evidence_authenticity": authenticity,
        "explore_ref": str((explore_payload.get("evidence_ref") or [""])[-1]) if isinstance(explore_payload.get("evidence_ref"), list) else "",
        "replay_ref": replay_ref,
        "dom_ref": dom_ref,
        "url_ref": url_ref,
        "console_ref": console_ref,
        "network_ref": network_ref,
        "explore_runner_report_ref": str(explore_bundle.get("report_ref") or ""),
        "explore_runner_meta_ref": str(explore_bundle.get("meta_ref") or ""),
        "explore_runner_result_ref": str(explore_bundle.get("result_ref") or ""),
        "explore_execution_mode": str(explore_bundle.get("execution_mode") or ""),
        "deterministic_command": str(explore_bundle.get("deterministic_command") or ""),
        "browser_agent_requested": bool(explore_bundle.get("browser_agent_requested")),
        "browser_agent_available": bool(explore_bundle.get("browser_agent_available")),
        "browser_agent_executed": bool(explore_bundle.get("browser_agent_executed")),
        "deterministic_command_configured": bool(explore_bundle.get("deterministic_command_configured")),
        "deterministic_command_executed": bool(explore_bundle.get("deterministic_command_executed")),
        "compat_alias_used": bool(explore_bundle.get("compat_alias_used")),
        "compat_id": str(explore_bundle.get("compat_id") or ""),
        "reason_code": str(explore_bundle.get("reason_code") or ""),
        "repair_route": str(explore_bundle.get("repair_route") or ""),
        "browser_agent_repair_route": str(explore_bundle.get("browser_agent_repair_route") or ""),
        "deterministic_command_repair_route": str(explore_bundle.get("deterministic_command_repair_route") or ""),
        "explore_task_ref": str(explore_bundle.get("task_ref") or ""),
        "replay_runner_report_ref": str(replay_bundle.get("report_ref") or ""),
        "replay_runner_meta_ref": str(replay_bundle.get("meta_ref") or ""),
        "replay_runner_result_ref": str(replay_bundle.get("result_ref") or ""),
        "replay_task_ref": str(replay_bundle.get("task_ref") or ""),
        "session_manifest_ref": str(explore_bundle.get("session_manifest_ref") or replay_bundle.get("session_manifest_ref") or ""),
        "profile_ref": str(explore_bundle.get("profile_ref") or replay_bundle.get("profile_ref") or ""),
        "cookies_ref": str(explore_bundle.get("cookies_ref") or replay_bundle.get("cookies_ref") or ""),
        "storage_state_ref": str(explore_bundle.get("storage_state_ref") or replay_bundle.get("storage_state_ref") or ""),
        "evidence_ref": list(
            dict.fromkeys(
                [
                    *(
                        explore_payload.get("evidence_ref")
                        if isinstance(explore_payload.get("evidence_ref"), list)
                        else []
                    ),
                    *(
                        replay_payload.get("evidence_ref")
                        if isinstance(replay_payload, dict) and isinstance(replay_payload.get("evidence_ref"), list)
                        else []
                    ),
                    dom_ref,
                    url_ref,
                    console_ref,
                    network_ref,
                    str(explore_bundle.get("report_ref") or ""),
                    str(explore_bundle.get("meta_ref") or ""),
                    str(explore_bundle.get("result_ref") or ""),
                    str(explore_bundle.get("task_ref") or ""),
                    str(replay_bundle.get("report_ref") or ""),
                    str(replay_bundle.get("meta_ref") or ""),
                    str(replay_bundle.get("result_ref") or ""),
                    str(replay_bundle.get("task_ref") or ""),
                    str(explore_bundle.get("session_manifest_ref") or replay_bundle.get("session_manifest_ref") or ""),
                    str(explore_bundle.get("profile_ref") or replay_bundle.get("profile_ref") or ""),
                    str(explore_bundle.get("cookies_ref") or replay_bundle.get("cookies_ref") or ""),
                    str(explore_bundle.get("storage_state_ref") or replay_bundle.get("storage_state_ref") or ""),
                ]
            )
        ),
        "transcript_ref": str(transcript_path.relative_to(project_root)),
        "generated_at": datetime.now().isoformat(),
    }
    pack_payload["evidence_ref"] = [item for item in pack_payload["evidence_ref"] if str(item).strip()]
    pack_path.write_text(json.dumps(pack_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "pack_ref": str(pack_path.relative_to(project_root)),
        "transcript_ref": str(transcript_path.relative_to(project_root)),
        "replay_ref": replay_ref,
        "dom_ref": str(dom_path.relative_to(project_root)),
        "url_ref": str(url_path.relative_to(project_root)),
        "console_ref": str(console_path.relative_to(project_root)),
        "network_ref": str(network_path.relative_to(project_root)),
    }


def _dependency_blockers(
    *,
    depends_on: list[str],
    tc_map: dict[str, dict[str, Any]],
) -> list[str]:
    if not depends_on:
        return []
    blocked: list[str] = []
    for dep in depends_on:
        token = str(dep or "").strip()
        if not token:
            continue
        dependency = next(
            (
                payload
                for payload in tc_map.values()
                if str(payload.get("scenario_id") or "").strip() == token or str(payload.get("tc_id") or "").strip() == token
            ),
            None,
        )
        if not isinstance(dependency, dict):
            continue
        if str(dependency.get("status") or "").strip().lower() != "passed":
            blocked.append(token)
    return blocked


def _derive_round_stop_reasons(
    *,
    item: dict[str, Any],
    tc_payload: dict[str, Any],
    active_browser_session: dict[str, Any],
) -> list[str]:
    status = str(tc_payload.get("status") or "").strip().lower()
    if status not in {"failed", "blocked"}:
        return []
    reasons: list[str] = []
    if bool(item.get("stop_on_fail")):
        reasons.append("stop_on_fail_triggered")
    if bool(tc_payload.get("browser_required")) and bool(tc_payload.get("replay_required")) and not str(tc_payload.get("replay_ref") or "").strip():
        reasons.append("required_replay_missing")
    if str(tc_payload.get("reason_code") or "").strip() == "browser_evidence_placeholder_only":
        reasons.append("browser_evidence_placeholder_only")
    if (
        bool(active_browser_session)
        and bool(tc_payload.get("browser_required"))
        and str(item.get("scenario_family") or "").strip().lower() == "happy"
    ):
        reasons.append("auth_session_invalid")
    return sorted({reason for reason in reasons if str(reason).strip()})


def _derive_qa_round_stop_issue(tc_execution_map: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    for payload in tc_execution_map.values():
        if not isinstance(payload, dict):
            continue
        if not bool(payload.get("round_stop_trigger")):
            continue
        reasons = [str(item).strip() for item in (payload.get("round_stop_reasons") or []) if str(item).strip()]
        return {
            "reason_code": "qa_round_stopped_for_repair",
            "message": f"qa round stopped for repair: {', '.join(reasons) or 'severe blocker'}",
            "details": {
                "tc_id": str(payload.get("tc_id") or ""),
                "scenario_id": str(payload.get("scenario_id") or ""),
                "stop_reasons": reasons,
            },
        }
    return None


def _is_feature_aware_qa_matrix(matrix_payload: dict[str, Any]) -> bool:
    execution_mode = str(matrix_payload.get("execution_mode") or "").strip().lower()
    source_matrix_path = str(matrix_payload.get("source_matrix_path") or "").strip()
    return execution_mode in {"feature-aware", "story-exhaustive"} or bool(source_matrix_path)


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
    selected_qa_types: list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    entries = matrix_payload.get("entries")
    if not isinstance(entries, list):
        return {}

    tc_map: dict[str, dict[str, Any]] = {}
    active_browser_session = _active_browser_session(project_root)
    resolved_version = str(matrix_payload.get("version") or "").strip() or "auto"
    feature_name = str(matrix_payload.get("feature") or matrix_payload.get("feature_slug") or "").strip()
    prefer_explicit_layer_overrides = _is_feature_aware_qa_matrix(matrix_payload)
    selected_filter = {
        normalize_qa_type(str(item).strip())
        for item in (selected_qa_types or [])
        if normalize_qa_type(str(item).strip())
    }
    round_stop_active = False
    round_stop_reasons: list[str] = []
    round_stop_anchor = ""
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
        if selected_filter and qa_type not in selected_filter:
            continue
        automation = str(item.get("automation") or "auto").strip().lower()
        if round_stop_active:
            tc_map[tc_id] = {
                "tc_id": tc_id,
                "ac_id": ac_id,
                "source_tc_id": str(item.get("source_tc_id") or tc_id),
                "scenario_id": str(item.get("scenario_id") or ""),
                "scenario_family": str(item.get("scenario_family") or ""),
                "qa_type": qa_type,
                "automation": automation,
                "status": "blocked",
                "layer_status": "blocked",
                "reason_code": "qa_round_stopped_for_repair",
                "command": str(item.get("command") or ""),
                "assertion_count": 0,
                "evidence_ref": [],
                "browser_required": _is_browser_required_entry(item),
                "replay_required": bool(item.get("replay_required")),
                "dependency_blockers": [],
                "round_stop_reasons": list(round_stop_reasons),
                "round_stop_anchor": round_stop_anchor,
                "stop_on_fail": bool(item.get("stop_on_fail")),
            }
            continue
        dependency_blockers = _dependency_blockers(
            depends_on=item.get("depends_on") if isinstance(item.get("depends_on"), list) else [],
            tc_map=tc_map,
        )
        if dependency_blockers:
            tc_map[tc_id] = {
                "tc_id": tc_id,
                "ac_id": ac_id,
                "source_tc_id": str(item.get("source_tc_id") or tc_id),
                "scenario_id": str(item.get("scenario_id") or ""),
                "scenario_family": str(item.get("scenario_family") or ""),
                "qa_type": qa_type,
                "automation": automation,
                "status": "blocked",
                "layer_status": "blocked",
                "reason_code": "scenario_dependency_blocked",
                "command": str(item.get("command") or ""),
                "assertion_count": 0,
                "evidence_ref": [],
                "browser_required": _is_browser_required_entry(item),
                "replay_required": bool(item.get("replay_required")),
                "dependency_blockers": dependency_blockers,
                "stop_on_fail": bool(item.get("stop_on_fail")),
            }
            continue
        if prefer_explicit_layer_overrides:
            command = str(
                explicit_layer_overrides.get(qa_type)
                or item.get("command")
                or commands.get(qa_type)
                or ""
            ).strip()
        else:
            command = str(
                item.get("command")
                or explicit_layer_overrides.get(qa_type)
                or commands.get(qa_type)
                or ""
            ).strip()
        tc_dir = evidence_root / "qa9-tc" / tc_id
        tc_dir.mkdir(parents=True, exist_ok=True)

        explicit_layer_command = bool(explicit_layer_overrides.get(qa_type))
        executable_automation = automation in {"auto", "hybrid", "mixed"} or (automation == "manual" and explicit_layer_command)
        if not executable_automation:
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
                "stop_on_fail": bool(item.get("stop_on_fail")),
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
                "stop_on_fail": bool(item.get("stop_on_fail")),
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

        browser_pack_refs = {"pack_ref": "", "transcript_ref": "", "replay_ref": "", "learning_ref": ""}
        replay_payload: dict[str, Any] | None = None
        if _is_browser_required_entry(item):
            admission = resolve_browser_runtime_admission(
                item=item,
                active_browser_session=active_browser_session,
            )
            task_payload = build_browser_task(
                item=item,
                qa_type=qa_type,
                mode="compatibility" if qa_type == "compatibility" else "functional",
                project_root=project_root,
                session=active_browser_session,
            )
            task_path = write_browser_task(tc_dir=tc_dir, payload=task_payload)
            extra_env.update(
                {
                    "BEACON_BROWSER_TASK_FILE": str(task_path),
                    "BEACON_BROWSER_DETERMINISTIC_COMMAND": command,
                }
            )
            extra_env.update(_browser_session_env(project_root, active_browser_session))
            preferred_runner = str(admission.get("preferred_runner") or item.get("exploratory_runner") or "")
            compiled_runner = default_browser_runner_command(
                preferred_runner,
                qa_type=qa_type,
            )
            if str(admission.get("status") or "") == "blocked":
                run_payload = {
                    "status": "blocked",
                    "layer": qa_type,
                    "command": "",
                    "attempt_count": 0,
                    "assertion_count": 0,
                    "reason_code": str(admission.get("reason_code") or ""),
                    "evidence_ref": [],
                }
                explore_payload = dict(run_payload)
            else:
                if prefer_explicit_layer_overrides:
                    explore_command = str(
                        explicit_layer_overrides.get(qa_type)
                        or item.get("explore_command")
                        or compiled_runner
                        or command
                        or commands.get(qa_type)
                        or ""
                    ).strip()
                else:
                    explore_command = str(
                        item.get("explore_command")
                        or compiled_runner
                        or command
                        or explicit_layer_overrides.get(qa_type)
                        or commands.get(qa_type)
                        or ""
                    ).strip()
                explore_payload = _run_layer_command(
                    layer=qa_type,
                    command=explore_command,
                    project_root=project_root,
                    layer_dir=tc_dir / "explore",
                    retries=rerun_flaky,
                    run_id=run_id,
                    stage="verify",
                    extra_env=extra_env,
                    tc_id=tc_id,
                    ac_id=ac_id,
                )
                run_payload = dict(explore_payload)
            if bool(item.get("replay_required")) and str(run_payload.get("status") or "").strip().lower() == "passed":
                if prefer_explicit_layer_overrides:
                    replay_command = str(
                        explicit_layer_overrides.get(qa_type)
                        or item.get("replay_command")
                        or compiled_runner
                        or command
                        or commands.get(qa_type)
                        or ""
                    ).strip()
                else:
                    replay_command = str(
                        item.get("replay_command")
                        or compiled_runner
                        or command
                        or explicit_layer_overrides.get(qa_type)
                        or commands.get(qa_type)
                        or ""
                    ).strip()
                replay_payload = _run_layer_command(
                    layer=qa_type,
                    command=replay_command,
                    project_root=project_root,
                    layer_dir=tc_dir / "replay",
                    retries=rerun_flaky,
                    run_id=run_id,
                    stage="verify",
                    extra_env=extra_env,
                    tc_id=tc_id,
                    ac_id=ac_id,
                )
                run_payload = {
                    **run_payload,
                    "status": "passed" if str(replay_payload.get("status") or "").strip().lower() == "passed" else "failed",
                    "layer": qa_type,
                    "command": explore_command,
                    "assertion_count": int(run_payload.get("assertion_count") or 0) + int(replay_payload.get("assertion_count") or 0),
                    "attempt_count": int(run_payload.get("attempt_count") or 0) + int(replay_payload.get("attempt_count") or 0),
                    "execution_fingerprint": hashlib.sha256(
                        "|".join(
                            [
                                str(run_payload.get("execution_fingerprint") or ""),
                                str(replay_payload.get("execution_fingerprint") or ""),
                            ]
                        ).encode("utf-8")
                    ).hexdigest(),
                    "ended_at": str(replay_payload.get("ended_at") or run_payload.get("ended_at") or ""),
                    "junit_path": str(replay_payload.get("junit_path") or run_payload.get("junit_path") or ""),
                    "junit_valid": bool(replay_payload.get("junit_valid") or run_payload.get("junit_valid")),
                    "evidence_ref": list(
                        dict.fromkeys(
                            [
                                *(
                                    run_payload.get("evidence_ref")
                                    if isinstance(run_payload.get("evidence_ref"), list)
                                    else []
                                ),
                                *(
                                    replay_payload.get("evidence_ref")
                                    if isinstance(replay_payload.get("evidence_ref"), list)
                                    else []
                                ),
                            ]
                        )
                    ),
                    "replay_command": replay_command,
                }
            browser_pack_refs = _write_browser_evidence_pack(
                project_root=project_root,
                tc_dir=tc_dir,
                run_id=run_id,
                item=item,
                explore_payload=explore_payload,
                admission=admission,
                replay_payload=replay_payload,
            )
            pack_payload = read_json(project_root / browser_pack_refs["pack_ref"], {})
            authenticity = pack_payload.get("evidence_authenticity") if isinstance(pack_payload, dict) and isinstance(pack_payload.get("evidence_authenticity"), dict) else {}
            if str(authenticity.get("reason_code") or "").strip():
                run_payload["reason_code"] = str(authenticity.get("reason_code") or "").strip()
            if str(authenticity.get("status") or "") == "placeholder_only" or str(admission.get("status") or "") == "blocked":
                browser_pack_refs["learning_ref"] = _write_browser_runner_learning_note(
                    project_root=project_root,
                    version=resolved_version,
                    feature=feature_name,
                    tc_id=tc_id,
                    admission=admission,
                    authenticity=authenticity if isinstance(authenticity, dict) else {},
                )
            extra_refs = [value for value in browser_pack_refs.values() if value]
            run_payload["browser_evidence_authenticity_status"] = str(authenticity.get("status") or "")
            run_payload["evidence_ref"] = list(
                dict.fromkeys(
                    [
                        *(
                            run_payload.get("evidence_ref")
                            if isinstance(run_payload.get("evidence_ref"), list)
                            else []
                        ),
                        *extra_refs,
                        str(task_path.relative_to(project_root)),
                    ]
                )
            )
        else:
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
        if _is_negative_matrix_entry(item) and str(run_payload.get("status") or "").strip().lower() in {"failed", "blocked"}:
            observed, negative_reason_code = _negative_expected_block_observed(project_root, run_payload)
            if observed:
                run_payload = _mark_negative_expected_block_passed(
                    project_root=project_root,
                    layer_dir=tc_dir,
                    run_payload=run_payload,
                    reason_code=negative_reason_code,
                )
        tc_map[tc_id] = {
            "tc_id": tc_id,
            "ac_id": ac_id,
            "source_tc_id": str(item.get("source_tc_id") or tc_id),
            "scenario_id": str(item.get("scenario_id") or ""),
            "scenario_family": str(item.get("scenario_family") or ""),
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
            "browser_required": _is_browser_required_entry(item),
            "browser_evidence_pack_ref": browser_pack_refs["pack_ref"],
            "browser_evidence_authenticity_status": str(run_payload.get("browser_evidence_authenticity_status") or ""),
            "browser_runner_learning_ref": browser_pack_refs.get("learning_ref", ""),
            "replay_required": bool(item.get("replay_required")),
            "replay_ref": browser_pack_refs["replay_ref"],
            "reason_code": str(run_payload.get("reason_code") or ""),
            "dependency_blockers": dependency_blockers,
            "stop_on_fail": bool(item.get("stop_on_fail")),
        }
        stop_reasons = _derive_round_stop_reasons(
            item=item,
            tc_payload=tc_map[tc_id],
            active_browser_session=active_browser_session,
        )
        if stop_reasons:
            tc_map[tc_id]["round_stop_trigger"] = True
            tc_map[tc_id]["round_stop_reasons"] = stop_reasons
            round_stop_active = True
            round_stop_reasons = stop_reasons
            round_stop_anchor = tc_id
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
    selected_qa_types: list[str] | None = None,
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
    selected_filter = {
        normalize_qa_type(str(item).strip())
        for item in (selected_qa_types or [])
        if normalize_qa_type(str(item).strip())
    }
    for item in entries:
        if not isinstance(item, dict):
            continue
        qa_type = normalize_qa_type(str(item.get("qa_type") or item.get("layer") or "").strip())
        if selected_filter and qa_type not in selected_filter:
            continue
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
                "source_tc_id": str(tc_payload.get("source_tc_id") or item.get("source_tc_id") or tc_id),
                "scenario_id": str(tc_payload.get("scenario_id") or item.get("scenario_id") or ""),
                "scenario_family": str(tc_payload.get("scenario_family") or item.get("scenario_family") or ""),
                "qa_type": qa_type,
                "layer": to_legacy_layer(qa_type),
                "automation": automation,
                "status": tc_status,
                "layer_status": layer_status,
                "reason_code": str(tc_payload.get("reason_code") or ""),
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
                "browser_required": bool(tc_payload.get("browser_required") or item.get("browser_required")),
                "browser_evidence_pack_ref": str(tc_payload.get("browser_evidence_pack_ref") or ""),
                "browser_runner_learning_ref": str(tc_payload.get("browser_runner_learning_ref") or ""),
                "replay_required": bool(tc_payload.get("replay_required") or item.get("replay_required")),
                "replay_ref": str(tc_payload.get("replay_ref") or ""),
                "stop_on_fail": bool(tc_payload.get("stop_on_fail") or item.get("stop_on_fail")),
                "round_stop_trigger": bool(tc_payload.get("round_stop_trigger")),
                "round_stop_reasons": list(tc_payload.get("round_stop_reasons") or []),
                "round_stop_anchor": str(tc_payload.get("round_stop_anchor") or ""),
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
            "round_stop_triggered": any(bool(item.get("round_stop_trigger")) for item in tc_results),
            "round_stop_reasons": next((list(item.get("round_stop_reasons") or []) for item in tc_results if bool(item.get("round_stop_trigger"))), []),
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
    junit_layers = {"unit", "integration", "contract"}
    for layer in layer_results:
        status = str(layer.get("status", "")).lower()
        if status != "passed":
            continue
        name = normalize_qa_type(str(layer.get("layer", "")))
        if require_assertion_count and name in junit_layers and int(layer.get("assertion_count", 0) or 0) <= 0:
            issues.append(
                {
                    "layer": name,
                    "reason_code": "assertion_count_zero_pass",
                    "message": f"layer {name} passed but assertion_count=0",
                }
            )
        if require_junit and name in junit_layers:
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


def _build_gate_report_issues(
    *,
    test_status: dict[str, Any],
    layer_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    issues = [
        {
            "reason_code": str(item.get("reason_code") or "auto_test_issue"),
            "message": str(item.get("message") or item.get("reason_code") or "auto-test quality issue"),
            "blocked": True,
        }
        for item in (test_status.get("quality_issues") or [])
        if isinstance(item, dict)
    ]
    if issues or str(test_status.get("status") or "").strip().lower() == "passed":
        return issues

    for layer in layer_results:
        layer_status = str(layer.get("status") or "").strip().lower()
        if layer_status not in {"failed", "blocked", "cancelled", "error"}:
            continue
        layer_name = normalize_qa_type(str(layer.get("layer") or "unknown"))
        exit_code = layer.get("exit_code")
        detail = f"exit_code={exit_code}" if exit_code not in ("", None) else f"status={layer_status}"
        issues.append(
            {
                "reason_code": "auto_test_layer_failed",
                "message": f"layer {layer_name} {layer_status} ({detail})",
                "blocked": True,
            }
        )

    if issues:
        return issues

    return [
        {
            "reason_code": "auto_test_failed",
            "message": f"auto-test status={str(test_status.get('status') or 'failed').strip().lower()}",
            "blocked": True,
        }
    ]


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
    explicit_qa_types = parse_qa_types(qa_types, profile=qa_profile) if qa_types else []
    if is_qa9_scope:
        selected_layers = explicit_qa_types or parse_qa_types(qa_types, profile=qa_profile)
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
    matrix_payload: dict[str, Any] | None = None
    qa9_matrix_payload: dict[str, Any] | None = None
    if active_matrix_path:
        loaded_matrix = _load_executable_matrix(Path(active_matrix_path))
        if loaded_matrix.get("payload"):
            matrix_payload = loaded_matrix["payload"]
        else:
            typer.echo(
                f"⚠ executable matrix load failed: {loaded_matrix.get('error', 'unknown')} ({loaded_matrix.get('path', active_matrix_path)})"
            )
    qa9_matrix_resolve_path = qa_matrix_path or matrix_path
    if is_qa9_scope and qa9_matrix_resolve_path:
        loaded = {"payload": matrix_payload} if matrix_payload and qa9_matrix_resolve_path == active_matrix_path else _load_qa9_matrix(Path(qa9_matrix_resolve_path))
        if loaded.get("payload"):
            qa9_matrix_payload = loaded["payload"]
            active_matrix_path = qa9_matrix_resolve_path
            if explicit_qa_types:
                selected_layers = explicit_qa_types
            else:
                selected_layers = parse_qa_types(qa9_matrix_payload.get("qa_types"), profile=qa_profile)
                if matrix_payload and not qa9_matrix_payload.get("qa_types"):
                    selected_layers = [
                        layer
                        for layer in dict.fromkeys(
                            _matrix_entry_layer(item)
                            for item in qa9_matrix_payload.get("entries", [])
                            if isinstance(item, dict)
                        )
                        if layer
                    ]
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

    matrix_row_execution = bool(is_qa9_scope and matrix_payload and not explicit_qa_types and not matrix_payload.get("qa_types"))
    if is_qa9_scope and not matrix_row_execution:
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
    has_real_ui_execution = bool(
        str(commands.get("ui") or "").strip()
        or str(commands.get("functional") or "").strip()
    )
    ui_guard_requested = bool(
        target_url
        or origin_url
        or snapshot_file
        or snapshot_text
        or strict_ui_assertion
        or ui_assertions
        or (expectation or "").strip().lower() not in {"", "unknown"}
        or (("ui" in selected_layers or "functional" in selected_layers) and not has_real_ui_execution)
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
    if matrix_row_execution and matrix_payload:
        layer_results = _execute_matrix_tc_entries(
            project_root=project_root,
            run_id=run_id,
            evidence_root=evidence_root,
            matrix_payload=matrix_payload,
            commands=commands,
            rerun_flaky=rerun_flaky,
        )
    else:
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
    if qa9_matrix_payload and not matrix_row_execution:
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
            selected_qa_types=selected_layers,
        )
        qa9_tc_execution_path = evidence_root / "qa9" / "tc-execution-map.json"
        qa9_tc_execution_path.parent.mkdir(parents=True, exist_ok=True)
        qa9_tc_execution_path.write_text(
            json.dumps(qa9_tc_execution_map, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        execution_payload.setdefault("artifacts", []).append(str(qa9_tc_execution_path.relative_to(project_root)))
        round_stop_issue = _derive_qa_round_stop_issue(qa9_tc_execution_map)
        if round_stop_issue:
            test_status["quality_issues"].append(round_stop_issue)

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

    if qa9_matrix_payload and not matrix_row_execution:
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
                if selected_layers and qa_type not in selected_layers:
                    continue
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
            selected_qa_types=selected_layers,
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

    status_paths = write_qa_status(project_root, test_status)
    coverage_summary_path = write_coverage_summary(
        project_root,
        version=resolved_version,
        run_id=run_id,
    )

    gate_report_path = project_root / ".beacon" / "gate-report.json"
    gate_status = "Pass" if str(test_status.get("status")) == "passed" else "Blocked"
    gate_issues = _build_gate_report_issues(test_status=test_status, layer_results=layer_results)
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
            str(coverage_summary_path.relative_to(project_root)),
            status_paths["legacy"],
            status_paths["canonical"],
            str(gate_report_path.relative_to(project_root)),
            str(_raw_command_log_path(project_root).relative_to(project_root)),
        ]
    )
    _update_evidence_manifest(project_root, manifest_refs, run_id=run_id, version=resolved_version)

    signature_chain_ref = _write_evidence_signature_chain(project_root, run_id=run_id, summary_path=summary_path)
    execution_payload.setdefault("artifacts", []).append(signature_chain_ref)
    status_paths = write_qa_status(project_root, test_status)
    _update_evidence_manifest(
        project_root,
        [signature_chain_ref, status_paths["legacy"], status_paths["canonical"]],
        run_id=run_id,
        version=resolved_version,
    )

    typer.echo("✓ Test execution started")
    typer.echo(f"  Scope: {scope}")
    typer.echo(f"  Layers: {', '.join(selected_layers)}")
    typer.echo(f"  QA status: {project_root / status_paths['canonical']}")
    typer.echo(f"  Legacy status: {project_root / status_paths['legacy']}")
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
    status_data = load_qa_status(project_root)
    if not status_data:
        typer.echo("No test status found. Run 'beacon auto-test create' first.")
        return

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

    status_paths = write_qa_status(project_root, status_payload)
    typer.echo(f"✓ qa-use results imported: {project_root / status_paths['canonical']}")
    typer.echo(f"  Layers: {', '.join(status_payload['selected_layers']) or '-'}")
    typer.echo(f"  Status: {status_payload['status']}")


if __name__ == "__main__":
    app()
