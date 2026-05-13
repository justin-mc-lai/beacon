"""Beacon test-case command - Generate test cases."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import typer

from beacon.utils.artifact_paths import qa_docs_dir, qa_matrix_candidates, qa_matrix_output, uses_machine_surface
from beacon.utils.qa9 import (
    QA9_TYPES,
    build_qa_strategy,
    build_qa_llm_plan,
    default_assertion_for_qa_type,
    default_command_for_qa_type,
    normalize_qa_type,
    parse_qa_types,
    to_legacy_layer,
)
from beacon.utils.runtime import write_json
from beacon.utils.requirement_parsing import build_feature_ac_items, extract_qa_case_rows
from beacon.utils.requirement_deepening import (
    requirement_deepening_supported,
    sync_requirement_deepening_artifacts,
)
from beacon.utils.semantic_runtime import (
    build_mode_contract,
    build_semantic_capability_snapshot,
    execute_host_bridge_command,
    load_host_response_json,
    normalize_requested_mode,
)
from beacon.utils.story_scenarios import expand_story_scenarios, write_story_scenario_map
from beacon.utils.versioning import discover_versions, normalize_version, resolve_operational_docs_version, resolve_target_version

app = typer.Typer(name="test-case", help="Generate test cases")


def _slug(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "-")


def _candidate_doc_paths(project_root: Path, version: str, category: str, slug: str) -> list[Path]:
    return [project_root / "docs" / "beacon" / version / category / f"{slug}.md"]


def _read_first_existing(paths: list[Path]) -> tuple[Path | None, str]:
    for path in paths:
        if path.exists():
            return path, path.read_text(encoding="utf-8", errors="ignore")
    return None, ""


def _extract_ac_items(content: str, source: str) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()
    if not content.strip():
        return items

    # Markdown table pattern: | AC-001 | text | ...
    for line in content.splitlines():
        if "|" not in line:
            continue
        m = re.search(r"\b(AC-\d{3,})\b", line, flags=re.I)
        if not m:
            continue
        ac_id = m.group(1).upper()
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        theme = cells[1] if len(cells) > 1 else ""
        text = cells[2] if len(cells) > 2 else (cells[1] if len(cells) > 1 else line.strip())
        if ac_id in seen:
            continue
        seen.add(ac_id)
        items.append({"ac_id": ac_id, "theme": theme, "text": text, "source": source})

    # Fallback bullet/text pattern: AC-001: xxx
    for m in re.finditer(r"\b(AC-\d{3,})\b[:：]?\s*([^\n]+)", content, flags=re.I):
        ac_id = m.group(1).upper()
        text = m.group(2).strip()
        if ac_id in seen:
            continue
        seen.add(ac_id)
        items.append({"ac_id": ac_id, "theme": "", "text": text, "source": source})

    return items


def _infer_layer_from_ac(text: str) -> str:
    t = (text or "").lower()
    if "prototype" in t and any(token in t for token in ("映射", "orphan", "anchor", "ui 模块", "状态")):
        return "unit"
    # Guidance/support-surface semantics should stay in deterministic non-browser layers
    # unless they explicitly mention UI/browser interaction.
    support_surface_patterns = (
        r"\broute explainability\b",
        r"\bguidance surface\b",
        r"\bguidance surfaces\b",
        r"\bsupport-surface\b",
        r"\bsupport-surfaces\b",
        r"\bsupport surface\b",
        r"\bsupport surfaces\b",
        r"\bnon-software\b",
    )
    if any(re.search(pattern, t, flags=re.I) for pattern in support_surface_patterns):
        if any(
            phrase in t
            for phrase in (
                "unless ui/browser interaction is explicitly declared",
                "unless ui interaction is explicitly declared",
                "unless browser interaction is explicitly declared",
                "default to deterministic non-browser qa mapping",
            )
        ):
            return "unit"
        return "unit"
    ui_patterns = (
        "登录",
        "注册",
        "浏览",
        "表单",
        "页面",
        "点击",
        r"\bsubmit\b",
        r"\bform\b",
        r"\bui\b",
        r"\bpage\b",
        r"\bclick\b",
        r"\bbrowser\b",
        r"\bscreen\b",
    )
    if any(re.search(pattern, t, flags=re.I) for pattern in ui_patterns):
        return "ui"
    if any(re.search(pattern, t, flags=re.I) for pattern in (r"\bapi\b", "接口", r"\bhttp\b", r"\bcurl\b", r"\bendpoint\b")):
        return "api-curl"
    if any(re.search(pattern, t, flags=re.I) for pattern in ("单元", r"\bunit\b", "函数", "边界", r"\berror\b", "异常", "校验", r"\bsecurity\b")):
        return "unit"
    # Default to unit for deterministic commandability in minimal setups.
    return "unit"


def _default_command_for_layer(layer: str) -> str:
    qa_type = normalize_qa_type(layer)
    return default_command_for_qa_type(qa_type)


def _default_assertion_for_layer(layer: str) -> str:
    qa_type = normalize_qa_type(layer)
    return default_assertion_for_qa_type(qa_type)


def _default_priority_for_qa_type(qa_type: str) -> str:
    return {
        "functional": "P0",
        "smoke": "P0",
        "unit": "P0",
        "interface": "P0",
        "contract": "P1",
        "integration": "P1",
        "regression": "P1",
        "exception": "P1",
        "compatibility": "P1",
    }.get(qa_type, "P2")


def _strip_markdown_ticks(value: str) -> str:
    text = str(value or "").strip()
    if text.startswith("`") and text.endswith("`") and len(text) >= 2:
        return text[1:-1].strip()
    return text


def _load_prototype_contract_artifacts(project_root: Path, version: str, feature_slug: str) -> tuple[dict, dict]:
    proto_root = project_root / "docs" / "beacon" / version / "prototype" / feature_slug
    navigation = {}
    interaction = {}
    nav_path = proto_root / "navigation-map.json"
    interaction_path = proto_root / "interaction-map.json"
    if nav_path.exists():
        try:
            payload = json.loads(nav_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                navigation = payload
        except Exception:  # noqa: BLE001
            navigation = {}
    if interaction_path.exists():
        try:
            payload = json.loads(interaction_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                interaction = payload
        except Exception:  # noqa: BLE001
            interaction = {}
    return navigation, interaction


def _load_route_closure_artifacts(project_root: Path, version: str, feature_slug: str) -> tuple[dict, dict]:
    proto_root = project_root / "docs" / "beacon" / version / "prototype" / feature_slug
    route_payload = {}
    impl_payload = {}
    route_path = proto_root / "route-closure-contract.json"
    impl_path = proto_root / "implementation-map.json"
    if route_path.exists():
        try:
            route_payload = json.loads(route_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            route_payload = {}
    if impl_path.exists():
        try:
            impl_payload = json.loads(impl_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            impl_payload = {}
    return route_payload, impl_payload


def _load_prototype_v2_artifacts(project_root: Path, version: str, feature_slug: str) -> tuple[dict, dict]:
    proto_root = project_root / "docs" / "beacon" / version / "prototype" / feature_slug
    plan_payload = {}
    coverage_payload = {}
    plan_path = proto_root / "prototype-plan.json"
    coverage_path = proto_root / "coverage-report.json"
    if plan_path.exists():
        try:
            payload = json.loads(plan_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                plan_payload = payload
        except Exception:  # noqa: BLE001
            plan_payload = {}
    if coverage_path.exists():
        try:
            payload = json.loads(coverage_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                coverage_payload = payload
        except Exception:  # noqa: BLE001
            coverage_payload = {}
    return plan_payload, coverage_payload


def _story_sequence_for_feature(project_root: Path, version: str, feature_slug: str, *, fallback_entries: list[dict]) -> list[dict]:
    machine_story = project_root / "docs" / "beacon" / version / ".machine" / "user-story" / f"{feature_slug}.json"
    if machine_story.exists():
        try:
            payload = json.loads(machine_story.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            payload = {}
        if isinstance(payload, dict):
            active_revision = str(payload.get("current_revision_id") or "")
            for story in payload.get("stories", []):
                if not isinstance(story, dict) or str(story.get("revision_id") or "") != active_revision:
                    continue
                items = story.get("items") if isinstance(story.get("items"), list) else []
                rows = [
                    {
                        "ac_id": str(item.get("id") or ""),
                        "theme": str(item.get("theme") or ""),
                        "text": str(item.get("text") or ""),
                    }
                    for item in items
                    if isinstance(item, dict) and str(item.get("kind") or "") == "ac" and str(item.get("id") or "").strip()
                ]
                if rows:
                    return rows

    us_path, us_content = _read_first_existing(_candidate_doc_paths(project_root, version, "user-story", feature_slug))
    ac_items = _extract_ac_items(us_content, f"user-story:{us_path}" if us_path else "user-story:missing")
    if ac_items:
        return [{"ac_id": item["ac_id"], "theme": str(item.get("source") or ""), "text": str(item.get("text") or "")} for item in ac_items]
    return [
        {
            "ac_id": str(item.get("ac_id") or ""),
            "theme": str(item.get("layer") or item.get("qa_type") or ""),
            "text": str(item.get("assertion") or ""),
        }
        for item in fallback_entries
        if isinstance(item, dict) and str(item.get("ac_id") or "").strip()
    ]


def _build_qa_requirements(qa_types: list[str], qa_applicability: Optional[dict[str, str]] = None) -> list[dict]:
    qa_set = set(qa_types)
    applicability_map = qa_applicability or {}
    out: list[dict] = []
    for qa_type in QA9_TYPES:
        selected = qa_type in qa_set
        applicability = str(applicability_map.get(qa_type) or ("required" if selected else "conditional")).strip().lower()
        if applicability not in {"required", "conditional", "na"}:
            applicability = "required" if selected else "conditional"
        required = selected and applicability == "required"
        out.append(
            {
                "qa_type": qa_type,
                "required": bool(required),
                "automation_required": bool(required),
                "min_cases": 1 if required else 0,
                "applicability": applicability,
                "waiver": {
                    "ticket": "",
                    "approved_by": "",
                    "expires_at": "",
                },
            }
        )
    return out


def _supports_profile_required_type_narrowing(version: str) -> bool:
    normalized = normalize_version(version) or ""
    if not normalized.startswith("v"):
        return False
    try:
        major, minor, patch = [int(part) for part in normalized[1:].split(".")]
    except Exception:  # noqa: BLE001
        return False
    return (major, minor, patch) >= (1, 2, 0)


def _qa_case_type_to_qa_type(case_type: str, execution: str) -> str:
    kind = str(case_type or "").strip().lower()
    mode = str(execution or "").strip().lower()

    if "doc review" in mode:
        return "contract"
    if "db" in mode:
        return "integration"
    if "api" in mode:
        return "interface"
    if "agent-browser" in mode or "browser" in mode:
        if "回归" in kind:
            return "regression"
        return "functional"
    if "契约" in kind:
        return "contract"
    if "回归" in kind:
        return "regression"
    if "边界" in kind or "异常" in kind:
        return "exception"
    return "functional"


def _qa_case_automation(execution: str) -> str:
    mode = str(execution or "").strip().lower()
    markers = [token for token in ("agent-browser", "api", "db", "manual", "doc review") if token in mode]
    if len(markers) > 1 or "+" in mode:
        return "mixed"
    if "manual" in mode or "doc review" in mode:
        return "manual"
    return "auto"


_BEACON_JUNIT_ARG = '--junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"'


def _ensure_pytest_junit_command(command: str) -> str:
    raw = str(command or "").strip()
    if not raw:
        return raw
    lowered = raw.lower()
    if "pytest" not in lowered or "--junitxml" in lowered:
        return raw
    return f"{raw} {_BEACON_JUNIT_ARG}"


def _build_entries_from_qa_case_rows(
    *,
    feature: str,
    feature_slug: str,
    qa_rows: list[dict[str, Any]],
    ac_items: list[dict[str, Any]],
    ui_runner: str,
) -> list[dict[str, Any]]:
    story_to_ac = {
        str(item.get("story_id") or "").strip().upper(): str(item.get("ac_id") or "").strip()
        for item in ac_items
        if str(item.get("story_id") or "").strip() and str(item.get("ac_id") or "").strip()
    }
    fallback_ac_id = str(ac_items[0].get("ac_id") or "AC-001") if ac_items else "AC-001"
    entries: list[dict[str, Any]] = []
    for index, row in enumerate(qa_rows, start=1):
        explicit_layer = str(row.get("explicit_layer") or "").strip()
        qa_type = (
            normalize_qa_type(explicit_layer)
            if explicit_layer
            else _qa_case_type_to_qa_type(str(row.get("case_type") or ""), str(row.get("execution") or ""))
        )
        tc_id = str(row.get("tc_id") or f"TC-{index:03d}").strip() or f"TC-{index:03d}"
        story_id = str(row.get("story_id") or "").strip().upper()
        ac_id = str(row.get("ac_id") or story_to_ac.get(story_id, fallback_ac_id)).strip() or fallback_ac_id
        assertion = str(
            row.get("explicit_assertion")
            or row.get("expected_result")
            or row.get("scenario")
            or default_assertion_for_qa_type(qa_type)
        ).strip()
        command = _strip_markdown_ticks(
            str(
            row.get("explicit_command")
            or default_command_for_qa_type(qa_type, ui_runner=ui_runner)
            )
        ) or default_command_for_qa_type(qa_type, ui_runner=ui_runner)
        command = _ensure_pytest_junit_command(command)
        evidence_path = _strip_markdown_ticks(
            str(
            row.get("explicit_evidence_path")
            or f".beacon/evidence/test-results/{feature_slug}/{{run_id}}/{tc_id}.json"
            )
        )
        entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac_id,
                "story_id": story_id,
                "layer": to_legacy_layer(qa_type),
                "qa_type": qa_type,
                "title": f"{feature} {story_id or ac_id} :: {str(row.get('scenario') or assertion).strip()[:80]}",
                "priority": _default_priority_for_qa_type(qa_type),
                "automation": _qa_case_automation(str(row.get("execution") or "")),
                "command": command,
                "assertion": assertion,
                "evidence_path": evidence_path,
                "required_files": ["command.txt", "stdout.log", "stderr.log", "result.json", "junit.xml"],
                "status": "pending",
                "source": str(row.get("source") or "qa:test-cases"),
                "execution_method": str(row.get("execution") or ""),
                "scenario": str(row.get("scenario") or ""),
                "steps": str(row.get("steps") or ""),
            }
        )
    return entries

_BROWSER_HINT_TOKENS: tuple[str, ...] = (
    "ui",
    "browser",
    "page",
    "form",
    "click",
    "login",
    "dashboard",
    "viewport",
    "页面",
    "表单",
    "浏览器",
    "点击",
    "登录",
)
_ASCII_BROWSER_HINT_TOKENS: tuple[str, ...] = (
    "ui",
    "browser",
    "page",
    "form",
    "click",
    "login",
    "dashboard",
    "viewport",
)
_CJK_BROWSER_HINT_TOKENS: tuple[str, ...] = (
    "页面",
    "表单",
    "浏览器",
    "点击",
    "登录",
)


def _ac_pool_requires_browser(ac_items: list[dict]) -> bool:
    text = " ".join(str(item.get("text") or "") for item in ac_items if isinstance(item, dict)).lower()
    if any(re.search(rf"\\b{re.escape(token)}\\b", text) for token in _ASCII_BROWSER_HINT_TOKENS):
        return True
    return any(token in text for token in _CJK_BROWSER_HINT_TOKENS)


def _build_qa9_entries(
    *,
    feature: str,
    feature_slug: str,
    ac_items: list[dict],
    qa_types: list[str],
    ui_runner: str = "playwright",
    command_baseline: Optional[dict[str, str]] = None,
) -> list[dict]:
    entries: list[dict] = []
    if not ac_items:
        ac_items = [{"ac_id": "AC-001", "text": f"{feature} core flow works", "source": "fallback"}]

    qa_pool = list(qa_types) or list(QA9_TYPES)
    baseline = command_baseline or {}
    present_types: set[str] = set()
    idx = 0
    browser_semantics_required = _ac_pool_requires_browser(ac_items)

    # Rule 1: each AC must map to at least one executable TC.
    for ac_idx, ac in enumerate(ac_items, start=1):
        inferred = normalize_qa_type(_infer_layer_from_ac(ac.get("text", "")))
        qa_type = inferred if inferred in qa_pool else qa_pool[(ac_idx - 1) % len(qa_pool)]
        idx += 1
        tc_id = f"TC-{idx:03d}"
        command = str(baseline.get(qa_type) or "").strip() or default_command_for_qa_type(qa_type, ui_runner=ui_runner)
        present_types.add(qa_type)
        entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac.get("ac_id", "AC-001"),
                "layer": to_legacy_layer(qa_type),
                "qa_type": qa_type,
                "title": f"{feature} {qa_type} :: {str(ac.get('text', '')).strip()[:80]}",
                "priority": _default_priority_for_qa_type(qa_type),
                "automation": "auto",
                "command": command,
                "assertion": default_assertion_for_qa_type(qa_type),
                "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{{run_id}}/{tc_id}.json",
                "required_files": ["command.txt", "stdout.log", "stderr.log", "result.json", "junit.xml"],
                "status": "pending",
                "source": ac.get("source", ""),
            }
        )

    # Rule 2: required qa_types must be fully covered.
    for qa_type in qa_pool:
        if qa_type in present_types:
            continue
        if qa_type in {"functional", "compatibility"} and not browser_semantics_required:
            continue
        idx += 1
        ac = ac_items[(idx - 1) % len(ac_items)]
        tc_id = f"TC-{idx:03d}"
        command = str(baseline.get(qa_type) or "").strip() or default_command_for_qa_type(qa_type, ui_runner=ui_runner)
        entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac.get("ac_id", "AC-001"),
                "layer": to_legacy_layer(qa_type),
                "qa_type": qa_type,
                "title": f"{feature} {qa_type} coverage",
                "priority": _default_priority_for_qa_type(qa_type),
                "automation": "auto",
                "command": command,
                "assertion": default_assertion_for_qa_type(qa_type),
                "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{{run_id}}/{tc_id}.json",
                "required_files": ["command.txt", "stdout.log", "stderr.log", "result.json", "junit.xml"],
                "status": "pending",
                "source": ac.get("source", ""),
            }
        )
    return entries


def _load_think_progress(project_root: Path, version: str) -> dict:
    candidates = [
        project_root / ".beacon" / "state" / "think-progress" / f"{version}.json",
        project_root / ".beacon" / "state" / "think-progress.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(payload, dict):
            return payload
    return {}


def _load_existing_qa9_payload(project_root: Path, version: str, feature_slug: str) -> dict:
    for path in qa_matrix_candidates(project_root, version, feature_slug, "qa9-matrix"):
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            payload = {}
        if isinstance(payload, dict) and isinstance(payload.get("entries"), list):
            return payload
    return {}


def _normalize_existing_qa9_entries(
    *,
    feature: str,
    feature_slug: str,
    entries: list[dict],
    ac_items: list[dict],
    ui_runner: str,
) -> list[dict]:
    normalized: list[dict] = []
    ac_seed = ac_items or [{"ac_id": "AC-001", "text": f"{feature} core flow works", "source": "fallback"}]
    browser_semantics_required = _ac_pool_requires_browser(ac_seed)
    for index, item in enumerate(entries, start=1):
        if not isinstance(item, dict):
            continue
        ac = ac_seed[(index - 1) % len(ac_seed)]
        qa_type = normalize_qa_type(
            str(item.get("qa_type") or item.get("type") or item.get("layer") or _infer_layer_from_ac(str(ac.get("text") or "")))
        )
        if qa_type not in QA9_TYPES:
            qa_type = normalize_qa_type(_infer_layer_from_ac(str(ac.get("text") or "")))
        if qa_type not in QA9_TYPES:
            qa_type = "contract"
        assertion = str(item.get("assertion") or default_assertion_for_qa_type(qa_type))
        if (
            qa_type in {"functional", "compatibility"}
            and not browser_semantics_required
            and not bool(item.get("browser_required"))
            and assertion == default_assertion_for_qa_type(qa_type)
        ):
            continue
        tc_id = str(item.get("tc_id") or item.get("id") or f"TC-{index:03d}").strip() or f"TC-{index:03d}"
        normalized.append(
            {
                "tc_id": tc_id,
                "ac_id": str(item.get("ac_id") or ac.get("ac_id") or f"AC-{index:03d}").strip() or f"AC-{index:03d}",
                "layer": str(item.get("layer") or to_legacy_layer(qa_type)),
                "qa_type": qa_type,
                "title": str(item.get("title") or f"{feature} {qa_type} :: {str(item.get('assertion') or ac.get('text') or '').strip()[:80]}"),
                "priority": str(item.get("priority") or _default_priority_for_qa_type(qa_type)),
                "automation": str(item.get("automation") or "auto"),
                "command": _ensure_pytest_junit_command(
                    str(item.get("command") or "").strip() or default_command_for_qa_type(qa_type, ui_runner=ui_runner)
                ),
                "assertion": assertion,
                "evidence_path": str(item.get("evidence_path") or f".beacon/evidence/test-results/{feature_slug}/{{run_id}}/{tc_id}.json"),
                "required_files": item.get("required_files") if isinstance(item.get("required_files"), list) else ["command.txt", "stdout.log", "stderr.log", "result.json", "junit.xml"],
                "status": str(item.get("status") or "pending"),
                "source": str(item.get("source") or ac.get("source") or "qa9:existing"),
            }
        )
    return normalized


def _extract_host_test_case_payload() -> dict[str, Any]:
    payload, _ = load_host_response_json("test-case")
    if not payload:
        return {}
    for candidate in (payload.get("test_case"), payload.get("payload"), payload):
        if isinstance(candidate, dict):
            return candidate
    return {}


def _load_bridge_payload(payload_json: str = "") -> dict[str, Any]:
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


def _build_test_case_host_bridge_request(
    feature: str,
    feature_slug: str,
    ac_items: list[dict[str, Any]],
    qa_case_rows: list[dict[str, Any]],
    ui_runner: str,
    project_root: Path,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "command_name": "test-case",
        "request_kind": "test-case-semantic-compile",
        "feature": feature,
        "feature_slug": feature_slug,
        "ac_items": ac_items,
        "qa_case_rows": qa_case_rows,
        "ui_runner": ui_runner,
        "project_root": str(project_root),
    }


def _extract_host_test_case_payload_with_bridge(request_payload: dict[str, Any]) -> dict[str, Any]:
    payload, _ = execute_host_bridge_command("test-case", request_payload)
    for candidate in (
        payload.get("test_case") if isinstance(payload, dict) else None,
        payload.get("payload") if isinstance(payload, dict) else None,
        payload,
    ):
        if isinstance(candidate, dict):
            return candidate
    return _extract_host_test_case_payload()


@app.command("host-bridge", hidden=True)
def host_bridge(
    payload_json: str = typer.Argument("", help="Optional bridge request JSON; default reads stdin"),
):
    """Hidden host-native bridge endpoint for test-case semantic compile."""
    try:
        payload = _load_bridge_payload(payload_json)
    except typer.BadParameter as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc
    if str(payload.get("request_kind") or "").strip() != "test-case-semantic-compile":
        typer.echo("unsupported test-case bridge request_kind", err=True)
        raise typer.Exit(2)
    bridge_project_root = Path(str(payload.get("project_root") or Path.cwd())).resolve()
    feature = str(payload.get("feature") or "").strip()
    feature_slug = str(payload.get("feature_slug") or _slug(feature)).strip() or _slug(feature)
    raw_items = payload.get("ac_items")
    ac_items = [item for item in raw_items if isinstance(item, dict)] if isinstance(raw_items, list) else []
    raw_qa_rows = payload.get("qa_case_rows")
    qa_case_rows = [item for item in raw_qa_rows if isinstance(item, dict)] if isinstance(raw_qa_rows, list) else []
    ui_runner = str(payload.get("ui_runner") or "").strip()
    if qa_case_rows:
        entries = _build_entries_from_qa_case_rows(
            feature=feature,
            feature_slug=feature_slug,
            qa_rows=qa_case_rows,
            ac_items=ac_items,
            ui_runner=ui_runner or "browser-use",
        )
    else:
        entries: list[dict[str, Any]] = []
        seed = ac_items or [{"ac_id": "AC-001", "text": f"{feature} core flow works"}]
        idx = 0
        for ac in seed:
            ac_id = str(ac.get("ac_id") or f"AC-{idx + 1:03d}").strip() or f"AC-{idx + 1:03d}"
            candidate_texts = [str(ac.get("text") or "").strip()]
            candidate_texts.extend(str(item).strip() for item in (ac.get("details") or []) if str(item).strip())
            for candidate in [item for item in candidate_texts if item]:
                idx += 1
                layer = _infer_layer_from_ac(candidate)
                entries.append(
                    {
                        "tc_id": f"TC-{idx:03d}",
                        "ac_id": ac_id,
                        "layer": layer,
                        "command": _default_command_for_layer(layer),
                        "assertion": candidate,
                        "evidence_path": f".beacon/evidence/test-results/{feature_slug}/TC-{idx:03d}.json",
                        "status": "pending",
                        "source": "host-bridge",
                    }
                )
    typer.echo(json.dumps({"entries": entries, "model": "beacon-test-case-host-bridge"}, ensure_ascii=False))


def _normalize_host_matrix_entries(
    *,
    feature: str,
    feature_slug: str,
    entries_payload: list[dict[str, Any]],
    ac_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    ac_seed = ac_items or [{"ac_id": "AC-001", "text": f"{feature} core flow works", "source": "fallback"}]
    for index, item in enumerate(entries_payload, start=1):
        if not isinstance(item, dict):
            continue
        ac = ac_seed[(index - 1) % len(ac_seed)]
        layer = str(item.get("layer") or "").strip() or _infer_layer_from_ac(
            str(item.get("assertion") or item.get("title") or ac.get("text") or "")
        )
        tc_id = str(item.get("tc_id") or item.get("id") or f"TC-{index:03d}").strip() or f"TC-{index:03d}"
        normalized.append(
            {
                "tc_id": tc_id,
                "ac_id": str(item.get("ac_id") or ac.get("ac_id") or "AC-001").strip() or "AC-001",
                "layer": layer,
                "command": _ensure_pytest_junit_command(
                    str(item.get("command") or _default_command_for_layer(layer)).strip() or _default_command_for_layer(layer)
                ),
                "assertion": str(item.get("assertion") or _default_assertion_for_layer(layer)).strip() or _default_assertion_for_layer(layer),
                "evidence_path": str(item.get("evidence_path") or f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json"),
                "status": str(item.get("status") or "pending"),
                "source": str(item.get("source") or "host:test-case"),
            }
        )
    return normalized


def _ensure_minimum_ac_coverage(
    *,
    feature: str,
    feature_slug: str,
    entries: list[dict[str, Any]],
    ac_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    covered = {
        str(item.get("ac_id") or "").strip()
        for item in entries
        if isinstance(item, dict) and str(item.get("ac_id") or "").strip()
    }
    next_index = len(entries)
    for ac in ac_items:
        ac_id = str(ac.get("ac_id") or "").strip()
        if not ac_id or ac_id in covered:
            continue
        layer = _infer_layer_from_ac(str(ac.get("text") or ""))
        next_index += 1
        tc_id = f"TC-{next_index:03d}"
        entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac_id,
                "layer": layer,
                "command": _default_command_for_layer(layer),
                "assertion": str(ac.get("text") or _default_assertion_for_layer(layer)).strip() or _default_assertion_for_layer(layer),
                "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                "status": "pending",
                "source": str(ac.get("source") or "ac-coverage"),
            }
        )
        covered.add(ac_id)
    return entries


def _ensure_deepening_coverage_entries(
    *,
    feature_slug: str,
    entries: list[dict[str, Any]],
    ac_items: list[dict[str, Any]],
    deepening_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    coverage_candidates = [
        item
        for item in (deepening_payload.get("coverage_candidates") or [])
        if isinstance(item, dict) and str(item.get("family") or "").strip()
    ]
    if not coverage_candidates:
        return entries

    existing_families = {
        str(item.get("coverage_family") or "").strip()
        for item in entries
        if isinstance(item, dict) and str(item.get("coverage_family") or "").strip()
    }
    ac_anchor = str(ac_items[0].get("ac_id") or "AC-001") if ac_items else "AC-001"
    next_index = len(entries)
    for candidate in coverage_candidates:
        family = str(candidate.get("family") or "").strip()
        if not family or family in existing_families:
            continue
        layer = _infer_layer_from_ac(family)
        next_index += 1
        tc_id = f"TC-{next_index:03d}"
        entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac_anchor,
                "layer": layer,
                "command": _default_command_for_layer(layer),
                "assertion": f"coverage family {family} remains executable",
                "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                "status": "pending",
                "source": "requirement-deepening:coverage-family",
                "coverage_family": family,
            }
        )
        existing_families.add(family)
    return entries


def _build_story_scenario_payload(
    *,
    project_root: Path,
    version: str,
    feature: str,
    expansion_profile: str,
    scenario_depth: str,
    ui_runner: str,
) -> tuple[dict, str]:
    feature_slug = _slug(feature)
    us_path, us_content = _read_first_existing(
        _candidate_doc_paths(project_root, version, "user-story", feature_slug)
    )
    prd_path, prd_content = _read_first_existing(
        _candidate_doc_paths(project_root, version, "prd", feature_slug)
    )
    qa_path, qa_content = _read_first_existing(
        _candidate_doc_paths(project_root, version, "qa/test-cases", feature_slug)
    )
    research_path, research_content = _read_first_existing(
        _candidate_doc_paths(project_root, version, "research", feature_slug)
    )
    ac_items = build_feature_ac_items(
        user_story_content=us_content,
        prd_content=prd_content,
        qa_content=qa_content,
        research_content=research_content,
        user_story_source=f"user-story:{us_path}" if us_path else "user-story:missing",
        prd_source=f"prd:{prd_path}" if prd_path else "prd:missing",
        qa_source=f"qa:test-cases:{qa_path}" if qa_path else "qa:test-cases:missing",
        research_source=f"research:{research_path}" if research_path else "research:missing",
    )
    if not ac_items:
        ac_items = [{"ac_id": "AC-001", "text": f"{feature} core flow works", "source": "fallback"}]
    qa_rows = extract_qa_case_rows(qa_content, f"qa:test-cases:{qa_path}" if qa_path else "qa:test-cases:missing")
    existing_qa9_payload = _load_existing_qa9_payload(project_root, version, feature_slug)
    existing_entries = (
        [item for item in existing_qa9_payload.get("entries", []) if isinstance(item, dict)]
        if isinstance(existing_qa9_payload.get("entries"), list)
        else []
    )
    display_feature = str(existing_qa9_payload.get("feature") or feature).strip() or feature
    resolved_ui_runner = str(ui_runner or "").strip().lower()

    if qa_rows:
        if not resolved_ui_runner:
            resolved_ui_runner = "browser-use"
        qa9_entries = _build_entries_from_qa_case_rows(
            feature=display_feature,
            feature_slug=feature_slug,
            qa_rows=qa_rows,
            ac_items=ac_items,
            ui_runner=resolved_ui_runner or "browser-use",
        )
    elif existing_entries:
        if not resolved_ui_runner:
            strategy = existing_qa9_payload.get("qa_strategy") if isinstance(existing_qa9_payload.get("qa_strategy"), dict) else {}
            resolved_ui_runner = str(
                strategy.get("ui_runner")
                or existing_qa9_payload.get("ui_runner")
                or "browser-use"
            ).strip().lower()
        qa9_entries = _normalize_existing_qa9_entries(
            feature=display_feature,
            feature_slug=feature_slug,
            entries=existing_entries,
            ac_items=ac_items,
            ui_runner=resolved_ui_runner or "browser-use",
        )
    else:
        think_progress = _load_think_progress(project_root, version)
        think_strategy = think_progress.get("qa_strategy") if isinstance(think_progress, dict) else None
        strategy = think_strategy if isinstance(think_strategy, dict) else {}
        strategy_ui_runner = str(strategy.get("ui_runner") or "").strip().lower()
        resolved_ui_runner = resolved_ui_runner or strategy_ui_runner or "browser-use"
        qa_types_resolved = parse_qa_types(None, profile="web-full")
        if not strategy:
            strategy = build_qa_strategy(
                project_root=project_root,
                qa_types=qa_types_resolved,
                ui_runner=resolved_ui_runner,
            )
        command_baseline = strategy.get("command_baseline") if isinstance(strategy, dict) else {}
        if not isinstance(command_baseline, dict):
            command_baseline = {}
        for qa_type in qa_types_resolved:
            command_baseline.setdefault(
                qa_type,
                default_command_for_qa_type(qa_type, ui_runner=resolved_ui_runner),
            )
        qa9_entries = _build_qa9_entries(
            feature=display_feature,
            feature_slug=feature_slug,
            ac_items=ac_items,
            qa_types=qa_types_resolved,
            ui_runner=resolved_ui_runner,
            command_baseline=command_baseline,
        )

    story_sequence = _story_sequence_for_feature(
        project_root,
        version,
        feature_slug,
        fallback_entries=qa9_entries,
    )
    scenario_payload = expand_story_scenarios(
        feature=feature,
        version=version,
        story_sequence=story_sequence,
        entries=qa9_entries,
        expansion_profile=expansion_profile,
        scenario_depth=scenario_depth,
        ui_runner=resolved_ui_runner or "browser-use",
    )
    scenario_payload["feature"] = display_feature
    return scenario_payload, (resolved_ui_runner or "browser-use")


def _feature_slugs_for_version(project_root: Path, version: str) -> list[str]:
    root = project_root / "docs" / "beacon" / version / "user-story"
    if not root.exists():
        return []
    return sorted(path.stem for path in root.glob("*.md") if path.is_file() and path.stem != "index")


def _versions_for_prefix(project_root: Path, version_prefix: str) -> list[str]:
    normalized_prefix = str(version_prefix or "").strip().lower()
    versions = discover_versions(project_root)
    if not normalized_prefix:
        return versions
    return [version for version in versions if version.lower().startswith(normalized_prefix)]


def generate_test_cases(feature: str, test_type: str) -> list:
    """Generate legacy test case structure (kept for compatibility)."""
    cases = []

    if test_type in ("all", "smoke"):
        cases.extend(
            [
                {"id": "TC-001", "type": "smoke", "title": "Feature loads correctly", "status": "pending"},
                {"id": "TC-002", "type": "smoke", "title": "Core functionality works", "status": "pending"},
            ]
        )

    if test_type in ("all", "new"):
        cases.extend(
            [
                {"id": "TC-003", "type": "new", "title": "Happy path test", "status": "pending"},
                {"id": "TC-004", "type": "new", "title": "Edge case test", "status": "pending"},
            ]
        )

    if test_type in ("all", "regression"):
        cases.extend(
            [
                {
                    "id": "TC-005",
                    "type": "regression",
                    "title": "Existing functionality preserved",
                    "status": "pending",
                },
            ]
        )

    return cases


@app.command("story-scenarios")
def story_scenarios(
    feature: str = typer.Argument("", help="Feature name/slug. Omit with --all-features."),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    version_prefix: str = typer.Option("", "--version-prefix", help="Generate across versions with matching prefix, e.g. v1.1."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    all_features: bool = typer.Option(False, "--all-features", help="Generate for all features in selected version(s)."),
    skip_existing: bool = typer.Option(True, "--skip-existing/--force", help="Skip features with existing story-scenario-map."),
    expansion_profile: str = typer.Option("pua-web", "--expansion-profile", help="Scenario expansion profile."),
    scenario_depth: str = typer.Option("standard", "--scenario-depth", help="Scenario expansion depth."),
    ui_runner: str = typer.Option("", "--ui-runner", help="UI runner override for generated browser scenarios."),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Generate story-scenario-map artifacts for one feature or batch across versions."""
    project_root = Path(project) if project else Path.cwd()
    if not all_features and not str(feature or "").strip():
        raise typer.BadParameter("feature is required unless --all-features is set")

    if version_prefix.strip():
        target_versions = _versions_for_prefix(project_root, version_prefix)
    else:
        target_versions = [resolve_target_version(project_root, version)]

    results: list[dict[str, object]] = []
    for resolved_version in target_versions:
        target_features = _feature_slugs_for_version(project_root, resolved_version) if all_features else [feature]
        for feature_name in target_features:
            path = qa_matrix_output(project_root, resolved_version, _slug(feature_name), "story-scenario-map")
            if skip_existing and path.exists():
                results.append(
                    {
                        "version": resolved_version,
                        "feature": feature_name,
                        "path": str(path.relative_to(project_root)),
                        "status": "skipped",
                    }
                )
                continue
            scenario_payload, resolved_ui_runner = _build_story_scenario_payload(
                project_root=project_root,
                version=resolved_version,
                feature=feature_name,
                expansion_profile=expansion_profile,
                scenario_depth=scenario_depth,
                ui_runner=ui_runner,
            )
            written_path = write_story_scenario_map(
                project_root,
                version=resolved_version,
                feature=feature_name,
                payload=scenario_payload,
            )
            results.append(
                {
                    "version": resolved_version,
                    "feature": feature_name,
                    "path": str(written_path.relative_to(project_root)),
                    "status": "generated",
                    "ui_runner": resolved_ui_runner,
                    "scenario_count": len(scenario_payload.get("scenarios", [])) if isinstance(scenario_payload.get("scenarios"), list) else 0,
                }
            )

    payload = {
        "version_prefix": version_prefix,
        "versions": target_versions,
        "generated_count": len([item for item in results if item.get("status") == "generated"]),
        "skipped_count": len([item for item in results if item.get("status") == "skipped"]),
        "results": results,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    typer.echo("Story scenario map generation")
    typer.echo(f"- versions: {', '.join(target_versions) or '-'}")
    typer.echo(f"- generated: {payload['generated_count']}")
    typer.echo(f"- skipped: {payload['skipped_count']}")
    for item in results:
        marker = "✓" if item.get("status") == "generated" else "-"
        typer.echo(f"{marker} {item.get('version')} {item.get('feature')} -> {item.get('path')}")


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    test_type: str = typer.Option("all", "--type", "-t", help="Test type: smoke/new/regression/all"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    overwrite_doc: bool = typer.Option(
        False,
        "--overwrite-doc",
        help="Allow overwriting the human-readable QA markdown when it already exists.",
    ),
    qa_profile: str = typer.Option(
        "web-full",
        "--qa-profile",
        help="QA profile: web-core/web-full/custom",
    ),
    qa_types: Optional[list[str]] = typer.Option(
        None,
        "--qa-types",
        help="QA types list (comma-separated or repeatable), default follows profile.",
    ),
    llm_auto: bool = typer.Option(
        True,
        "--llm-auto/--no-llm-auto",
        help="Enable LLM dynamic QA planning.",
    ),
    llm_mode: str = typer.Option(
        "auto",
        "--llm-mode",
        help="LLM mode: rule/real/auto",
    ),
    automation_target_rate: float = typer.Option(
        0.85,
        "--automation-target-rate",
        help="Target automation coverage rate [0,1].",
    ),
    matrix_output: Optional[str] = typer.Option(
        None,
        "--matrix-output",
        help="QA9 matrix output file path (*.qa9-matrix.json).",
    ),
    qa9: bool = typer.Option(False, "--qa9", help="Legacy compatibility flag to emit QA9 mirror output."),
    expand_scenarios: bool = typer.Option(
        False,
        "--expand-scenarios",
        help="Legacy compatibility flag to force scenario expansion metadata in mirror outputs.",
    ),
    expansion_profile: str = typer.Option(
        "pua-web",
        "--expansion-profile",
        help="Scenario expansion profile for story-native QA planning.",
    ),
    scenario_depth: str = typer.Option(
        "standard",
        "--scenario-depth",
        help="Scenario expansion depth: minimal/standard/deep.",
    ),
    prototype_contract: bool = typer.Option(
        False,
        "--prototype-contract",
        help="Legacy compatibility flag for prototype contract-aware test case generation.",
    ),
    mode: str = typer.Option("auto", "--mode", help="Compile mode: auto/llm/rule"),
    model: str = typer.Option("beacon-test-case-compiler", "--model", help="Compiler model label for evidence"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
    ui_runner: str = typer.Option(
        "",
        "--ui-runner",
        help="UI runner for QA9 command generation: playwright/cypress/browser-use/agent-browser",
    ),
):
    """Create test cases and executable AC matrix."""
    prototype_contract_requested = prototype_contract
    project_root = Path(project) if project else Path.cwd()
    try:
        resolved_version = resolve_operational_docs_version(
            project_root,
            version,
            command_name="test-case create",
        )
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)
    feature_slug = _slug(feature)
    memory_context_path = os.environ.get("BEACON_STAGE_CONTEXT_PATH", "").strip()
    try:
        requested_mode = normalize_requested_mode(mode)
    except ValueError:
        typer.echo("Invalid --mode. Use auto/llm/rule.", err=True)
        raise typer.Exit(2)
    capability_snapshot = build_semantic_capability_snapshot(
        "test-case",
        disable_env="BEACON_TEST_CASE_DISABLE_LLM",
    )
    fallback_reason = ""
    effective_mode = requested_mode
    host_payload: dict[str, Any] = {}
    host_requested = False
    if requested_mode == "rule":
        effective_mode = "rule"
    elif bool(capability_snapshot.get("llm_disabled")):
        if requested_mode == "llm":
            typer.echo("LLM compile disabled by BEACON_TEST_CASE_DISABLE_LLM.", err=True)
            raise typer.Exit(2)
        effective_mode = "rule"
        fallback_reason = "llm_disabled"
    elif bool(capability_snapshot.get("host_semantic_ready")):
        host_requested = True
    else:
        if requested_mode == "llm":
            typer.echo("Test case semantic compile requires host semantic response.", err=True)
            raise typer.Exit(2)
        effective_mode = "rule"
        fallback_reason = "llm_unavailable"
    # Read ACs from existing user-story/prd docs
    us_path, us_content = _read_first_existing(
        _candidate_doc_paths(project_root, resolved_version, "user-story", feature_slug)
    )
    prd_path, prd_content = _read_first_existing(
        _candidate_doc_paths(project_root, resolved_version, "prd", feature_slug)
    )
    qa_path, qa_content = _read_first_existing(
        _candidate_doc_paths(project_root, resolved_version, "qa/test-cases", feature_slug)
    )
    research_path, research_content = _read_first_existing(
        _candidate_doc_paths(project_root, resolved_version, "research", feature_slug)
    )
    legacy_story_path = project_root / ".beacon" / "user-story" / f"{feature_slug}.json"
    docs_story_dir = project_root / "docs" / "beacon" / resolved_version / "user-story"
    legacy_story_dir = project_root / ".beacon" / "user-story"
    story_surface_exists = any(
        directory.exists() and any(directory.iterdir())
        for directory in (docs_story_dir, legacy_story_dir)
    )
    ac_items = build_feature_ac_items(
        user_story_content=us_content,
        prd_content=prd_content,
        qa_content=qa_content,
        research_content=research_content,
        user_story_source=f"user-story:{us_path}" if us_path else "user-story:missing",
        prd_source=f"prd:{prd_path}" if prd_path else "prd:missing",
        qa_source=f"qa:test-cases:{qa_path}" if qa_path else "qa:test-cases:missing",
        research_source=f"research:{research_path}" if research_path else "research:missing",
    )
    if not ac_items:
        if legacy_story_path.exists():
            try:
                legacy_story = json.loads(legacy_story_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                legacy_story = {}
            acceptance = legacy_story.get("acceptance_criteria") if isinstance(legacy_story, dict) else {}
            legacy_rows: list[str] = []
            if isinstance(acceptance, dict):
                for values in acceptance.values():
                    if isinstance(values, list):
                        legacy_rows.extend(str(item).strip() for item in values if str(item).strip())
            if legacy_rows:
                ac_items = [
                    {"ac_id": f"AC-{idx:03d}", "text": item, "source": f"legacy-user-story:{legacy_story_path}"}
                    for idx, item in enumerate(legacy_rows, start=1)
                ]
        if not ac_items:
            if story_surface_exists and not prd_path and not qa_path and not legacy_story_path.exists():
                typer.echo(f"user story not found for feature: {feature_slug}", err=True)
                raise typer.Exit(2)
            ac_items = [{"ac_id": "AC-001", "text": f"{feature} core flow works", "source": "fallback"}]
    qa_case_rows = extract_qa_case_rows(qa_content, f"qa:test-cases:{qa_path}" if qa_path else "qa:test-cases:missing")

    if host_requested:
        host_payload = _extract_host_test_case_payload_with_bridge(
            _build_test_case_host_bridge_request(feature, feature_slug, ac_items, qa_case_rows, ui_runner, project_root)
        )
        if host_payload:
            effective_mode = "host"
        elif requested_mode == "llm":
            typer.echo("Test case semantic compile requires host semantic response.", err=True)
            raise typer.Exit(2)
        else:
            effective_mode = "rule"
            fallback_reason = "host_compile_failed"
    compiler = build_mode_contract(
        requested_mode=requested_mode,
        effective_mode=effective_mode,
        fallback_reason=fallback_reason,
        capability_snapshot=capability_snapshot,
    )
    deepening_payload: dict[str, Any] = {}
    if requirement_deepening_supported(resolved_version):
        deepening_payload = sync_requirement_deepening_artifacts(
            project_root,
            version=resolved_version,
            feature=feature,
            prd_content=prd_content,
            user_story_content=us_content,
            qa_content=qa_content,
            prd_source=f"prd:docs/beacon/{resolved_version}/prd/{feature_slug}.md",
            user_story_source=f"user-story:docs/beacon/{resolved_version}/user-story/{feature_slug}.md",
            qa_source=f"qa:test-cases:docs/beacon/{resolved_version}/qa/test-cases/{feature_slug}.md",
            compiler=compiler,
            target_artifact="test-case",
        )

    prototype_navigation, prototype_interaction = _load_prototype_contract_artifacts(
        project_root, resolved_version, feature_slug
    )
    prototype_plan, prototype_coverage = _load_prototype_v2_artifacts(
        project_root, resolved_version, feature_slug
    )
    route_closure_contract, implementation_map = _load_route_closure_artifacts(
        project_root, resolved_version, feature_slug
    )
    host_matrix_entries = host_payload.get("entries") if isinstance(host_payload.get("entries"), list) else []
    if effective_mode == "host" and host_matrix_entries:
        entries = _normalize_host_matrix_entries(
            feature=feature,
            feature_slug=feature_slug,
            entries_payload=host_matrix_entries,
            ac_items=ac_items,
        )
    elif qa_case_rows:
        entries = _build_entries_from_qa_case_rows(
            feature=feature,
            feature_slug=feature_slug,
            qa_rows=qa_case_rows,
            ac_items=ac_items,
            ui_runner="browser-use",
        )
    else:
        entries = []
        for idx, ac in enumerate(ac_items, start=1):
            layer = _infer_layer_from_ac(ac.get("text", ""))
            tc_id = f"TC-{idx:03d}"
            evidence_path = f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json"
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac["ac_id"],
                    "layer": layer,
                    "command": _default_command_for_layer(layer),
                    "assertion": _default_assertion_for_layer(layer),
                    "evidence_path": evidence_path,
                    "status": "pending",
                    "source": ac.get("source", ""),
                }
            )

        synthetic_idx = len(entries)
        ac_anchor = ac_items[0]["ac_id"] if ac_items else "AC-001"
        for jump in prototype_navigation.get("jump_map", []) or []:
            synthetic_idx += 1
            tc_id = f"TC-{synthetic_idx:03d}"
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac_anchor,
                    "layer": "ui",
                    "command": "python3 -c \"print('prototype-jump-check')\"",
                    "assertion": f"jump {jump.get('from', '')} -> {jump.get('to', '')} is represented",
                    "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                    "status": "pending",
                    "source": "prototype:navigation-map",
                }
            )
        for state_name in prototype_interaction.get("states", []) or []:
            synthetic_idx += 1
            tc_id = f"TC-{synthetic_idx:03d}"
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac_anchor,
                    "layer": "ui",
                    "command": "python3 -c \"print('prototype-state-check')\"",
                    "assertion": f"state {state_name} is represented in prototype",
                    "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                    "status": "pending",
                    "source": "prototype:interaction-map",
                }
            )
        if prototype_coverage:
            synthetic_idx += 1
            tc_id = f"TC-{synthetic_idx:03d}"
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac_anchor,
                    "layer": "ui",
                    "command": "python3 -c \"print('prototype-coverage-report-check')\"",
                    "assertion": "coverage report is consumed as a first-class prototype artifact",
                    "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                    "status": "pending",
                    "source": "prototype:coverage-report",
                }
            )
        for page_spec in prototype_plan.get("page_specs", []) or []:
            if not isinstance(page_spec, dict):
                continue
            page_id = str(page_spec.get("page_id") or "").strip()
            if not page_id:
                continue
            synthetic_idx += 1
            tc_id = f"TC-{synthetic_idx:03d}"
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac_anchor,
                    "layer": "ui",
                    "command": "python3 -c \"print('prototype-page-spec-check')\"",
                    "assertion": f"page-spec {page_id} compiles required sections and route targets",
                    "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                    "status": "pending",
                    "source": "prototype:page-specs",
                }
            )
        for missing_state in prototype_coverage.get("missing_state_variants", []) or []:
            if not isinstance(missing_state, str):
                continue
            synthetic_idx += 1
            tc_id = f"TC-{synthetic_idx:03d}"
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac_anchor,
                    "layer": "ui",
                    "command": "python3 -c \"print('prototype-coverage-check')\"",
                    "assertion": f"coverage report flags missing variant {missing_state}",
                    "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                    "status": "pending",
                    "source": "prototype:coverage-report",
                }
            )
        closure_cases = route_closure_contract.get("closure_cases") if isinstance(route_closure_contract.get("closure_cases"), list) else []
        bound_cases = {
            str(item.get("case_id") or ""): item
            for item in (implementation_map.get("closure_bindings") or [])
            if isinstance(item, dict) and str(item.get("case_id") or "").strip()
        }
        for case in closure_cases:
            if not isinstance(case, dict):
                continue
            synthetic_idx += 1
            tc_id = f"TC-{synthetic_idx:03d}"
            case_id = str(case.get("case_id") or "").strip()
            binding = bound_cases.get(case_id, {})
            target = str(binding.get("runtime_target") or binding.get("state_target") or case.get("target_surface_id") or "").strip()
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac_anchor,
                    "layer": "ui",
                    "command": "python3 -c \"print('prototype-route-closure-check')\"",
                    "assertion": f"route closure {case.get('source_label', '')} -> {target or case.get('target_surface_id', '')} remains deterministic",
                    "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                    "status": "pending",
                    "source": "prototype:route-closure-contract",
                }
            )

    if effective_mode == "host" or qa_case_rows:
        synthetic_idx = len(entries)
        ac_anchor = ac_items[0]["ac_id"] if ac_items else "AC-001"
        for jump in prototype_navigation.get("jump_map", []) or []:
            synthetic_idx += 1
            tc_id = f"TC-{synthetic_idx:03d}"
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac_anchor,
                    "layer": "ui",
                    "command": "python3 -c \"print('prototype-jump-check')\"",
                    "assertion": f"jump {jump.get('from', '')} -> {jump.get('to', '')} is represented",
                    "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                    "status": "pending",
                    "source": "prototype:navigation-map",
                }
            )
        for state_name in prototype_interaction.get("states", []) or []:
            synthetic_idx += 1
            tc_id = f"TC-{synthetic_idx:03d}"
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac_anchor,
                    "layer": "ui",
                    "command": "python3 -c \"print('prototype-state-check')\"",
                    "assertion": f"state {state_name} is represented in prototype",
                    "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                    "status": "pending",
                    "source": "prototype:interaction-map",
                }
            )
        if prototype_coverage:
            synthetic_idx += 1
            tc_id = f"TC-{synthetic_idx:03d}"
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac_anchor,
                    "layer": "ui",
                    "command": "python3 -c \"print('prototype-coverage-report-check')\"",
                    "assertion": "coverage report is consumed as a first-class prototype artifact",
                    "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                    "status": "pending",
                    "source": "prototype:coverage-report",
                }
            )
        for page_spec in prototype_plan.get("page_specs", []) or []:
            if not isinstance(page_spec, dict):
                continue
            page_id = str(page_spec.get("page_id") or "").strip()
            if not page_id:
                continue
            synthetic_idx += 1
            tc_id = f"TC-{synthetic_idx:03d}"
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac_anchor,
                    "layer": "ui",
                    "command": "python3 -c \"print('prototype-page-spec-check')\"",
                    "assertion": f"page-spec {page_id} compiles required sections and route targets",
                    "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                    "status": "pending",
                    "source": "prototype:page-specs",
                }
            )
        for missing_state in prototype_coverage.get("missing_state_variants", []) or []:
            if not isinstance(missing_state, str):
                continue
            synthetic_idx += 1
            tc_id = f"TC-{synthetic_idx:03d}"
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac_anchor,
                    "layer": "ui",
                    "command": "python3 -c \"print('prototype-coverage-check')\"",
                    "assertion": f"coverage report flags missing variant {missing_state}",
                    "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                    "status": "pending",
                    "source": "prototype:coverage-report",
                }
            )
        closure_cases = route_closure_contract.get("closure_cases") if isinstance(route_closure_contract.get("closure_cases"), list) else []
        bound_cases = {
            str(item.get("case_id") or ""): item
            for item in (implementation_map.get("closure_bindings") or [])
            if isinstance(item, dict) and str(item.get("case_id") or "").strip()
        }
        for case in closure_cases:
            if not isinstance(case, dict):
                continue
            synthetic_idx += 1
            tc_id = f"TC-{synthetic_idx:03d}"
            case_id = str(case.get("case_id") or "").strip()
            binding = bound_cases.get(case_id, {})
            target = str(binding.get("runtime_target") or binding.get("state_target") or case.get("target_surface_id") or "").strip()
            entries.append(
                {
                    "tc_id": tc_id,
                    "ac_id": ac_anchor,
                    "layer": "ui",
                    "command": "python3 -c \"print('prototype-route-closure-check')\"",
                    "assertion": f"route closure {case.get('source_label', '')} -> {target or case.get('target_surface_id', '')} remains deterministic",
                    "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                    "status": "pending",
                    "source": "prototype:route-closure-contract",
                }
            )

    entries = _ensure_minimum_ac_coverage(
        feature=feature,
        feature_slug=feature_slug,
        entries=entries,
        ac_items=ac_items,
    )
    entries = _ensure_deepening_coverage_entries(
        feature_slug=feature_slug,
        entries=entries,
        ac_items=ac_items,
        deepening_payload=deepening_payload,
    )

    matrix_payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "generated_at": datetime.now().isoformat(),
        "compiler": {
            **compiler,
            "model": model,
        },
        "entries": entries,
    }
    if deepening_payload:
        matrix_payload["requirement_deepening"] = {
            "coverage_families": [
                str(item.get("family") or "")
                for item in deepening_payload.get("coverage_candidates", [])
                if isinstance(item, dict) and str(item.get("family") or "").strip()
            ],
            "candidate_ledger_ref": str((deepening_payload.get("paths") or {}).get("candidate_ledger") or ""),
            "completeness_ref": str((deepening_payload.get("paths") or {}).get("completeness") or ""),
            "supplement_focus_areas": [
                str(item).strip()
                for item in ((deepening_payload.get("human_loop_handoff") or {}).get("focus_areas") or [])
                if str(item).strip()
            ],
            "supplement_recommended_command": str((deepening_payload.get("human_loop_handoff") or {}).get("recommended_command") or ""),
            "supplement_task": deepening_payload.get("supplement_task", {}),
            "re_freeze_transaction": deepening_payload.get("re_freeze_transaction", {}),
        }

    qa_types_resolved = parse_qa_types(qa_types, profile=qa_profile)
    think_progress = _load_think_progress(project_root, resolved_version)
    think_strategy = think_progress.get("qa_strategy") if isinstance(think_progress, dict) else None
    strategy = think_strategy if isinstance(think_strategy, dict) else {}
    strategy_ui_runner = str(strategy.get("ui_runner") or "").strip()
    resolved_ui_runner = str(ui_runner or strategy_ui_runner or "browser-use").strip().lower()
    if not resolved_ui_runner:
        resolved_ui_runner = "browser-use"
    explicit_ui_runner = bool(str(ui_runner or "").strip())
    if not strategy:
        strategy = build_qa_strategy(
            project_root=project_root,
            qa_types=qa_types_resolved,
            ui_runner=resolved_ui_runner,
        )
    required_types = strategy.get("qa_required_types") if isinstance(strategy, dict) else []
    if (
        qa_types is None
        and _supports_profile_required_type_narrowing(resolved_version)
        and str(qa_profile or "").strip().lower() == "web-full"
        and isinstance(required_types, list)
        and required_types
    ):
        narrowed = [normalize_qa_type(item) for item in required_types if normalize_qa_type(item) in QA9_TYPES]
        if narrowed:
            qa_types_resolved = narrowed
    command_baseline = strategy.get("command_baseline") if isinstance(strategy, dict) else {}
    if not isinstance(command_baseline, dict):
        command_baseline = {}
    for qa_type in qa_types_resolved:
        command_baseline.setdefault(
            qa_type,
            default_command_for_qa_type(qa_type, ui_runner=resolved_ui_runner),
        )
    if explicit_ui_runner:
        for qa_type in ("functional", "compatibility"):
            if qa_type in qa_types_resolved:
                command_baseline[qa_type] = default_command_for_qa_type(qa_type, ui_runner=resolved_ui_runner)
    if automation_target_rate < 0 or automation_target_rate > 1:
        raise typer.BadParameter("--automation-target-rate must be between 0 and 1")
    host_qa9_entries = host_payload.get("qa9_entries") if isinstance(host_payload.get("qa9_entries"), list) else []
    if effective_mode == "host" and host_qa9_entries:
        qa9_entries = _normalize_existing_qa9_entries(
            feature=feature,
            feature_slug=feature_slug,
            entries=host_qa9_entries,
            ac_items=ac_items,
            ui_runner=resolved_ui_runner,
        )
    elif effective_mode == "host" and host_matrix_entries:
        qa9_entries = _normalize_existing_qa9_entries(
            feature=feature,
            feature_slug=feature_slug,
            entries=host_matrix_entries,
            ac_items=ac_items,
            ui_runner=resolved_ui_runner,
        )
    elif qa_case_rows:
        qa9_entries = _build_entries_from_qa_case_rows(
            feature=feature,
            feature_slug=feature_slug,
            qa_rows=qa_case_rows,
            ac_items=ac_items,
            ui_runner=resolved_ui_runner,
        )
    else:
        qa9_entries = _build_qa9_entries(
            feature=feature,
            feature_slug=feature_slug,
            ac_items=ac_items,
            qa_types=qa_types_resolved,
            ui_runner=resolved_ui_runner,
            command_baseline=command_baseline,
        )
    qa9_payload = {
        "schema_version": "1.0.2",
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "compiler": {
            **compiler,
            "model": model,
        },
        "qa_profile": qa_profile,
        "qa_types": qa_types_resolved,
        "llm_plan": build_qa_llm_plan(
            project_root=project_root,
            llm_auto=llm_auto,
            llm_mode=llm_mode,
            qa_types=qa_types_resolved,
        ),
        "qa_strategy": strategy,
        "qa_requirements": _build_qa_requirements(
            qa_types_resolved,
            qa_applicability=strategy.get("qa_applicability") if isinstance(strategy, dict) else None,
        ),
        "automation_target_rate": automation_target_rate,
        "entries": qa9_entries,
        "compatibility_matrix": {
            "browsers": ["chromium", "firefox", "webkit"],
            "devices": ["desktop", "iphone14"],
            "required_pairs": [
                {"browser": "chromium", "device": "desktop"},
                {"browser": "firefox", "device": "desktop"},
                {"browser": "webkit", "device": "desktop"},
            ],
        },
        "generated_at": datetime.now().isoformat(),
    }
    if deepening_payload:
        handoff = deepening_payload.get("human_loop_handoff") if isinstance(deepening_payload.get("human_loop_handoff"), dict) else {}
        qa9_payload["coverage_families"] = [
            str(item.get("family") or "")
            for item in deepening_payload.get("coverage_candidates", [])
            if isinstance(item, dict) and str(item.get("family") or "").strip()
        ]
        qa9_payload["requirement_completeness_verdict"] = str(
            (deepening_payload.get("completeness") or {}).get("completeness_verdict") or ""
        )
        qa9_payload["supplement_focus_areas"] = [str(item).strip() for item in (handoff.get("focus_areas") or []) if str(item).strip()]
        qa9_payload["supplement_recommended_command"] = str(handoff.get("recommended_command") or "")
        qa9_payload["supplement_task"] = deepening_payload.get("supplement_task", {})
        qa9_payload["re_freeze_transaction"] = deepening_payload.get("re_freeze_transaction", {})
    story_sequence = _story_sequence_for_feature(
        project_root,
        resolved_version,
        feature_slug,
        fallback_entries=qa9_entries,
    )
    scenario_payload = expand_story_scenarios(
        feature=feature,
        version=resolved_version,
        story_sequence=story_sequence,
        entries=qa9_entries,
        expansion_profile=expansion_profile,
        scenario_depth=scenario_depth,
        ui_runner=resolved_ui_runner,
    )
    if deepening_payload:
        handoff = deepening_payload.get("human_loop_handoff") if isinstance(deepening_payload.get("human_loop_handoff"), dict) else {}
        scenario_payload["requirement_deepening_story_families"] = [
            str(item.get("family") or "")
            for item in deepening_payload.get("story_candidates", [])
            if isinstance(item, dict) and str(item.get("family") or "").strip()
        ]
        scenario_payload["requirement_completeness_ref"] = str(
            (deepening_payload.get("paths") or {}).get("completeness") or ""
        )
        scenario_payload["supplement_focus_areas"] = [str(item).strip() for item in (handoff.get("focus_areas") or []) if str(item).strip()]
        scenario_payload["supplement_recommended_command"] = str(handoff.get("recommended_command") or "")
        scenario_payload["supplement_task"] = deepening_payload.get("supplement_task", {})
        scenario_payload["re_freeze_transaction"] = deepening_payload.get("re_freeze_transaction", {})

    output_path = (
        Path(output)
        if output
        else project_root / "docs" / "beacon" / resolved_version / "qa" / "test-cases" / f"{feature_slug}.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path = qa_matrix_output(project_root, resolved_version, feature_slug, "ac-test-matrix")
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text(json.dumps(matrix_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    qa9_matrix_path = (
        Path(matrix_output)
        if matrix_output
        else qa_matrix_output(project_root, resolved_version, feature_slug, "qa9-matrix")
    )
    qa9_matrix_path.parent.mkdir(parents=True, exist_ok=True)
    qa9_matrix_path.write_text(json.dumps(qa9_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    scenario_map_path = write_story_scenario_map(
        project_root,
        version=resolved_version,
        feature=feature,
        payload=scenario_payload,
    )
    legacy_qa_path = project_root / ".beacon" / "qa" / f"{feature_slug}.json"
    legacy_qa_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_mapping = {
        str(item.get("ac_id") or f"AC-{idx:03d}"): [str(item.get("tc_id") or "")]
        for idx, item in enumerate(entries, start=1)
        if str(item.get("tc_id") or "").strip()
    }
    legacy_payload = {
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "ac_to_tc_mapping": legacy_mapping,
        "scenarios": list(scenario_payload.get("scenarios") or []),
    }
    if prototype_navigation or prototype_interaction:
        legacy_payload["prototype_contract"] = {
            "navigation": prototype_navigation,
            "interaction": prototype_interaction,
        }
    if deepening_payload:
        handoff = deepening_payload.get("human_loop_handoff") if isinstance(deepening_payload.get("human_loop_handoff"), dict) else {}
        legacy_payload["requirement_deepening"] = {
            "completeness_verdict": str((deepening_payload.get("completeness") or {}).get("completeness_verdict") or ""),
            "supplement_focus_areas": [str(item).strip() for item in (handoff.get("focus_areas") or []) if str(item).strip()],
            "supplement_task": deepening_payload.get("supplement_task", {}),
            "re_freeze_transaction": deepening_payload.get("re_freeze_transaction", {}),
        }
    elif prototype_contract_requested:
        legacy_contract_path = project_root / "docs" / "beacon" / resolved_version / "prototype" / feature_slug / "contract.json"
        if legacy_contract_path.exists():
            try:
                legacy_payload["prototype_contract"] = json.loads(legacy_contract_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                legacy_payload["prototype_contract"] = {}
    write_json(legacy_qa_path, legacy_payload)
    if qa9:
        legacy_qa9_path = project_root / ".beacon" / "qa" / f"{feature_slug}-qa9-matrix.json"
        legacy_qa9_path.parent.mkdir(parents=True, exist_ok=True)
        legacy_qa9_payload = {
            "feature": feature,
            "feature_slug": feature_slug,
            "version": resolved_version,
            "qa_types": [
                "functional",
                "smoke",
                "unit",
                "interface",
                "contract",
                "integration",
                "regression",
                "exception",
                "compatibility",
            ],
        }
        write_json(legacy_qa9_path, legacy_qa9_payload)
    elif expand_scenarios:
        legacy_payload["scenarios"] = list(scenario_payload.get("scenarios") or [])
        write_json(legacy_qa_path, legacy_payload)

    md_rows = "\n".join(
        f"| {x['ac_id']} | {x['tc_id']} | {x['layer']} | `{x['command']}` | {x['assertion']} | `{x['evidence_path']}` |"
        for x in entries
    )
    result_rows = "\n".join(f"| {x['tc_id']} | Pending | from {x['ac_id']} |" for x in entries)
    host_markdown = str(host_payload.get("markdown") or "").strip() if effective_mode == "host" else ""
    md_content = host_markdown or f"""# Test Cases: {feature}

## Overview

**Feature**: {feature}
**Test Type**: {test_type.upper()}
**Version**: {resolved_version}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Requested Mode**: {compiler['requested_mode']}
**Effective Mode**: {compiler['effective_mode']}
**Fallback Reason**: {compiler['fallback_reason'] or 'N/A'}
**Memory Context**: {memory_context_path or 'N/A'}
**AC Matrix JSON**: {matrix_path}
**QA9 Matrix JSON**: {qa9_matrix_path}
**Story Scenario Map JSON**: {scenario_map_path}
**Prototype Plan Present**: {bool(prototype_plan)}
**Prototype Coverage Present**: {bool(prototype_coverage)}
**Prototype Navigation Contract**: {bool(prototype_navigation)}
**Prototype Interaction Contract**: {bool(prototype_interaction)}

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
{md_rows}

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
{result_rows}
"""

    doc_written = False
    if output or not output_path.exists() or overwrite_doc:
        output_path.write_text(md_content, encoding="utf-8")
        doc_written = True
    if uses_machine_surface(resolved_version):
        index_path = output_path.parent / "index.md"
        if not index_path.exists():
            index_path.write_text(
                "\n".join(
                    [
                        f"# QA Test Case Index ({resolved_version})",
                        "",
                        "- Human-readable QA markdown lives in this directory.",
                        f"- Machine QA matrices live under `docs/beacon/{resolved_version}/.machine/qa/`.",
                        f"- Current feature: `{feature_slug}`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

    if json_output:
        typer.echo(
            json.dumps(
                {
                    "status": "ok",
                    "feature": feature,
                    "feature_slug": feature_slug,
                    "version": resolved_version,
                    "model": model,
                    **compiler,
                    "output_path": str(output_path),
                    "matrix_path": str(matrix_path),
                    "qa9_matrix_path": str(qa9_matrix_path),
                    "scenario_map_path": str(scenario_map_path),
                    "entry_count": len(entries),
                    "qa9_entry_count": len(qa9_entries),
                    "scenario_count": len(scenario_payload.get("scenarios", [])),
                    "requirement_deepening": {
                        "enabled": bool(deepening_payload),
                        "paths": deepening_payload.get("paths", {}),
                        "coverage_family_count": len(deepening_payload.get("coverage_candidates", []) or []),
                        "completeness_verdict": (deepening_payload.get("completeness") or {}).get("completeness_verdict", ""),
                    },
                    "supplement_focus_areas": [
                        str(item).strip()
                        for item in ((deepening_payload.get("human_loop_handoff") or {}).get("focus_areas") or [])
                        if str(item).strip()
                    ],
                    "supplement_recommended_command": str((deepening_payload.get("human_loop_handoff") or {}).get("recommended_command") or ""),
                    "supplement_task": deepening_payload.get("supplement_task", {}),
                    "re_freeze_transaction": deepening_payload.get("re_freeze_transaction", {}),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if doc_written:
        typer.echo(f"✓ Test cases created: {output_path}")
    else:
        typer.echo(f"✓ Test cases preserved: {output_path}")
    typer.echo(f"✓ AC matrix created: {matrix_path}")
    typer.echo(f"✓ QA9 matrix created: {qa9_matrix_path}")
    typer.echo(f"✓ Story scenario map created: {scenario_map_path}")
    typer.echo(f"  Type: {test_type}")
    typer.echo(f"  Entries: {len(entries)}")
    typer.echo(f"  QA9 Entries: {len(qa9_entries)}")
    typer.echo(f"  Scenario Entries: {len(scenario_payload.get('scenarios', []))}")
    typer.echo(f"  QA Runner: {resolved_ui_runner}")


@app.command("list")
def list_tests(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """List all test cases."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    test_dir = qa_docs_dir(project_root, resolved_version)

    if not test_dir.exists():
        typer.echo("No test cases found")
        return

    tests = list(test_dir.glob("*.md"))
    typer.echo(f"Test Cases ({len(tests)} found):")
    for test in tests:
        typer.echo(f"  - {test.name}")


@app.command()
def gate(
    feature: str = typer.Argument(..., help="Feature to check"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Run gate check for AC matrix coverage."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)

    typer.echo(f"\nTest Coverage Gate: {feature}")
    typer.echo("=" * 40)

    slug = _slug(feature)
    test_dir = qa_docs_dir(project_root, resolved_version)
    test_file = test_dir / f"{slug}.md"
    matrix_file = qa_matrix_output(project_root, resolved_version, slug, "ac-test-matrix")

    if not test_file.exists():
        typer.echo(f"✗ FAIL: Test file not found: {test_file}")
        raise typer.Exit(1)
    typer.echo("✓ PASS: Test file exists")

    if not matrix_file.exists():
        typer.echo(f"✗ FAIL: AC matrix not found: {matrix_file}")
        raise typer.Exit(1)

    payload = json.loads(matrix_file.read_text(encoding="utf-8"))
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        typer.echo(f"✗ FAIL: AC matrix empty: {matrix_file}")
        raise typer.Exit(1)

    required_fields = {"ac_id", "tc_id", "layer", "command", "assertion", "evidence_path"}
    broken = [
        idx + 1
        for idx, item in enumerate(entries)
        if not isinstance(item, dict) or not required_fields.issubset(set(item.keys()))
    ]
    if broken:
        typer.echo(f"✗ FAIL: AC matrix entries missing fields: {broken[:10]}")
        raise typer.Exit(1)

    typer.echo(f"✓ PASS: AC executable matrix entries={len(entries)}")
    typer.echo("\nGate Result: PASS")


if __name__ == "__main__":
    app()
