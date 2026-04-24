"""Implementation plan compiler and progress helpers."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

from beacon.utils.artifact_paths import human_execution_file, machine_execution_file, qa_matrix_candidates
from beacon.utils.delivery_baseline import (
    baseline_revision_id,
    load_implementation_delivery_baseline,
    materialize_implementation_delivery_baseline,
    projection_metadata,
    validate_projection_against_baseline,
)
from beacon.utils.diagram_truth import load_feature_diagram_truth
from beacon.utils.global_boundaries import global_boundary_principle_summaries
from beacon.utils.implement_adapters import load_beacon_config
from beacon.utils.revision_state import load_revision_state
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug, load_story_state
from beacon.utils.team_surface import implement_team_contract
from beacon.utils.technical_review_contract import (
    approved_technical_review_contract,
    build_technical_review_gate_payload,
    load_technical_review_contract,
    materialize_technical_review_contract,
    technical_review_git_workflow_seed,
)
from beacon.utils.versioning import normalize_version, release_line_key, resolve_target_version


TASK_STATUSES = ("draft", "planned", "in_progress", "blocked", "completed")
_HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
_AC_RE = re.compile(r"\b(AC-\d{3,})\b", flags=re.I)
_FR_RE = re.compile(r"\b(FR-\d{3,})\b", flags=re.I)
_FR_LINE_RE = re.compile(r"^(FR-\d{3,})\s*(.+?)\s*$", flags=re.I)
_FR_BULLET_RE = re.compile(r"^(?:[-*+]\s+)(FR-\d{3,})\s*(.+?)\s*$", flags=re.I)
_FR_NUMBERED_RE = re.compile(r"^(?:\d+[.)]\s+)(FR-\d{3,})\s*(.+?)\s*$", flags=re.I)
_FUNCTIONAL_REQUIREMENT_TITLES = {
    "functional requirements",
    "requirements",
    "product requirements",
    "功能需求",
    "功能要求",
    "需求",
}
_FUNCTIONAL_REQUIREMENT_END_TITLES = (
    "non-goals",
    "out of scope",
    "suggested output contract",
    "success standard",
    "first-principles",
    "notes",
    "验收标准",
    "接受标准",
    "测试",
    "qa",
)


def implementation_plan_supported(version: str | None) -> bool:
    normalized = release_line_key(version) or normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch)) >= (1, 1, 12)
    except Exception:  # noqa: BLE001
        return False


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = release_line_key(version) or normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def _team_mode_contract(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    return implement_team_contract(project_root, version=version, feature=feature)


def _normalize_string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in out:
            out.append(text)
    return out


def _default_implementation_preflight_rules(
    *,
    direct_delivery_services: list[str],
    expected_branch: str,
) -> list[str]:
    target_services = ", ".join(direct_delivery_services or ["repo root only"])
    branch_label = expected_branch or "<expected-branch>"
    return [
        f"Before implementation, verify the target service belongs to: {target_services}.",
        f"Before implementation, verify every direct delivery service is on {branch_label}.",
        "If a branch switch is needed and the worktree is dirty, stop and clean or stash first.",
    ]


def implementation_git_workflow_json_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_execution_file(project_root, resolved_version, f"git-workflow-{feature_slug(feature)}.json")


def implementation_git_workflow_markdown_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return human_execution_file(project_root, resolved_version, f"git-workflow-{feature_slug(feature)}.md")


def list_implementation_git_workflow_contracts(project_root: Path, *, version: str = "auto") -> list[dict[str, Any]]:
    resolved_version = resolve_target_version(project_root, version)
    machine_dir = machine_execution_file(project_root, resolved_version, "placeholder.json").parent
    out: list[dict[str, Any]] = []
    if not machine_dir.exists():
        return out
    for path in sorted(machine_dir.glob("git-workflow-*.json")):
        payload = read_json(path, {})
        if not isinstance(payload, dict) or not payload:
            continue
        out.append(
            {
                "path": str(path.relative_to(project_root)),
                "feature": str(payload.get("feature", "") or ""),
                "feature_slug": str(payload.get("feature_slug", "") or ""),
                "mode": str(payload.get("mode", "") or ""),
                "expected_branch": str(payload.get("expected_branch", "") or ""),
                "service_directories": list(payload.get("service_directories", [])) if isinstance(payload.get("service_directories"), list) else [],
                "direct_delivery_services": list(payload.get("direct_delivery_services", [])) if isinstance(payload.get("direct_delivery_services"), list) else [],
                "use_git_worktree": bool(payload.get("use_git_worktree", False)),
                "payload": payload,
            }
        )
    return out


def _default_git_workflow_contract(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    approved_contract = approved_technical_review_contract(project_root, version=version, feature=feature)
    if approved_contract:
        payload = technical_review_git_workflow_seed(approved_contract)
        if payload:
            envelope = load_implementation_delivery_baseline(project_root, version=version, feature=feature)
            if envelope:
                payload.update(projection_metadata(envelope, project_root=project_root, version=version, feature=feature))
            return payload
    config = load_beacon_config(project_root)
    implementation_cfg = config.get("implementation") if isinstance(config.get("implementation"), dict) else {}
    branch_guard_cfg = implementation_cfg.get("branch_guard") if isinstance(implementation_cfg.get("branch_guard"), dict) else {}
    expected_branch = str(branch_guard_cfg.get("expected_branch", "") or "").strip() or f"beacon/{version}"
    branch_prefix = str(branch_guard_cfg.get("branch_prefix", "") or "").strip()
    if not branch_prefix:
        branch_prefix = expected_branch.split("/", 1)[0] + "/" if "/" in expected_branch else "beacon/"
    configured_service_directories = _normalize_string_list(branch_guard_cfg.get("git_roots"))
    service_directories = configured_service_directories or ["."]
    direct_delivery_services = list(service_directories)
    mode = "workspace" if configured_service_directories else "single-repo"
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": version,
        "mode": mode,
        "expected_branch": expected_branch,
        "branch_prefix": branch_prefix,
        "base_branch": str(branch_guard_cfg.get("base_branch", "") or "main").strip() or "main",
        "use_git_worktree": bool(branch_guard_cfg.get("use_git_worktree", False)),
        "require_clean_worktree_for_switch": bool(branch_guard_cfg.get("require_clean_worktree_for_switch", True)),
        "service_directories": service_directories,
        "direct_delivery_services": direct_delivery_services,
        "git_roots": service_directories,
        "worktree_root": str(project_root),
        "implementation_preflight": _default_implementation_preflight_rules(
            direct_delivery_services=direct_delivery_services,
            expected_branch=expected_branch,
        ),
        "source": "project_config_seed" if branch_guard_cfg else "version_default",
        "generated_at": now_iso(),
    }
    envelope = load_implementation_delivery_baseline(project_root, version=version, feature=feature)
    if not envelope:
        envelope = materialize_implementation_delivery_baseline(project_root, version=version, feature=feature, seed=payload)
    payload.update(projection_metadata(envelope, project_root=project_root, version=version, feature=feature))
    return payload


def _render_git_workflow_markdown(payload: dict[str, Any]) -> str:
    services = payload.get("service_directories") if isinstance(payload.get("service_directories"), list) else []
    direct_delivery_services = payload.get("direct_delivery_services") if isinstance(payload.get("direct_delivery_services"), list) else []
    implementation_preflight = payload.get("implementation_preflight") if isinstance(payload.get("implementation_preflight"), list) else []
    lines = [
        "# Beacon Git Workflow Contract",
        "",
        f"- feature: `{payload.get('feature', '')}`",
        f"- version: `{payload.get('version', '')}`",
        f"- mode: `{payload.get('mode', '')}`",
        f"- expected_branch: `{payload.get('expected_branch', '')}`",
        f"- branch_prefix: `{payload.get('branch_prefix', '')}`",
        f"- base_branch: `{payload.get('base_branch', '')}`",
        f"- use_git_worktree: `{bool(payload.get('use_git_worktree', False))}`",
        f"- require_clean_worktree_for_switch: `{bool(payload.get('require_clean_worktree_for_switch', True))}`",
        f"- worktree_root: `{payload.get('worktree_root', '')}`",
        f"- source: `{payload.get('source', '')}`",
        "",
        "## Service Directories",
    ]
    if services:
        lines.extend(f"- `{item}`" for item in services)
    else:
        lines.append("- repo root only")
    lines.extend(["", "## Direct Delivery Services"])
    if direct_delivery_services:
        lines.extend(f"- `{item}`" for item in direct_delivery_services)
    elif services:
        lines.extend(f"- `{item}`" for item in services)
    else:
        lines.append("- repo root only")
    lines.extend(["", "## Implementation Preflight"])
    if implementation_preflight:
        lines.extend(f"- {item}" for item in implementation_preflight if str(item).strip())
    else:
        lines.extend(
            f"- {item}"
            for item in _default_implementation_preflight_rules(
                direct_delivery_services=direct_delivery_services or services,
                expected_branch=str(payload.get("expected_branch", "") or ""),
            )
        )
    return "\n".join(lines) + "\n"


def materialize_implementation_git_workflow_contract(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    json_path = implementation_git_workflow_json_path(project_root, resolved_version, feature)
    payload = _default_git_workflow_contract(project_root, version=resolved_version, feature=feature)
    baseline = load_implementation_delivery_baseline(project_root, version=resolved_version, feature=feature)
    if not baseline:
        baseline = materialize_implementation_delivery_baseline(project_root, version=resolved_version, feature=feature, seed=payload)
    payload.update(projection_metadata(baseline, project_root=project_root, version=resolved_version, feature=feature))
    existing = read_json(json_path, {})
    if (
        isinstance(existing, dict)
        and str(existing.get("feature", "") or "") == feature
        and str(existing.get("version", "") or "") == resolved_version
        and existing == payload
    ):
        return existing
    write_json(json_path, payload)
    markdown_path = implementation_git_workflow_markdown_path(project_root, resolved_version, feature)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_git_workflow_markdown(payload), encoding="utf-8")
    return payload


def has_implementation_git_workflow_contract(project_root: Path, *, version: str, feature: str) -> bool:
    resolved_version = resolve_target_version(project_root, version)
    return implementation_git_workflow_json_path(project_root, resolved_version, feature).exists()


def load_or_seed_implementation_git_workflow_contract(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    approved_contract = approved_technical_review_contract(project_root, version=resolved_version, feature=feature)
    if approved_contract:
        payload = technical_review_git_workflow_seed(approved_contract)
        if payload:
            return payload
    if has_implementation_git_workflow_contract(project_root, version=resolved_version, feature=feature):
        return load_implementation_git_workflow_contract(project_root, version=resolved_version, feature=feature)
    return _default_git_workflow_contract(project_root, version=resolved_version, feature=feature)


def ensure_implementation_git_workflow_contract(
    project_root: Path,
    *,
    version: str,
    feature: str,
    force_refresh_from_seed: bool = False,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    approved_contract = approved_technical_review_contract(project_root, version=resolved_version, feature=feature)
    if approved_contract and not force_refresh_from_seed:
        return materialize_implementation_git_workflow_contract(project_root, version=resolved_version, feature=feature)
    if force_refresh_from_seed:
        return materialize_implementation_git_workflow_contract(project_root, version=resolved_version, feature=feature)
    existing = load_implementation_git_workflow_contract(project_root, version=resolved_version, feature=feature)
    if existing and str(existing.get("feature", "") or "") == feature and str(existing.get("version", "") or "") == resolved_version:
        json_path = implementation_git_workflow_json_path(project_root, resolved_version, feature)
        markdown_path = implementation_git_workflow_markdown_path(project_root, resolved_version, feature)
        if json_path.exists() and markdown_path.exists():
            return existing
    return materialize_implementation_git_workflow_contract(project_root, version=resolved_version, feature=feature)


def load_implementation_git_workflow_contract(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    json_path = implementation_git_workflow_json_path(project_root, resolved_version, feature)
    payload = read_json(json_path, {})
    if (
        isinstance(payload, dict)
        and str(payload.get("feature", "") or "") == feature
        and str(payload.get("version", "") or "") == resolved_version
    ):
        return payload
    plan = load_implementation_plan(project_root, version=resolved_version, feature=feature)
    plan_contract = plan.get("git_workflow") if isinstance(plan.get("git_workflow"), dict) else {}
    if isinstance(plan_contract, dict) and str(plan_contract.get("version", "") or "") == resolved_version:
        return plan_contract
    return _default_git_workflow_contract(project_root, version=resolved_version, feature=feature)


def implementation_plan_json_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_execution_file(project_root, resolved_version, f"implementation-plan-{feature_slug(feature)}.json")


def implementation_plan_markdown_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return human_execution_file(project_root, resolved_version, f"implementation-plan-{feature_slug(feature)}.md")


def implementation_plan_progress_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_execution_file(project_root, resolved_version, f"implementation-plan-{feature_slug(feature)}.progress.json")


def _task_title(ac_id: str, text: str) -> str:
    body = str(text or "").strip() or "Implementation task"
    if len(body) > 72:
        body = body[:69].rstrip() + "..."
    return f"{ac_id} {body}".strip()


def _normalize_ids(values: Iterable[str] | None) -> set[str]:
    out: set[str] = set()
    for value in values or []:
        text = str(value or "").strip().upper()
        if text:
            out.add(text)
    return out


def _normalize_text_list(values: Iterable[str] | None) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _task_counts(tasks: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"total": len(tasks), **{status: 0 for status in TASK_STATUSES}}
    for task in tasks:
        status = str(task.get("status", "draft") or "draft").strip().lower()
        if status not in TASK_STATUSES:
            status = "draft"
        counts[status] += 1
    return counts


def _derive_plan_status(tasks: list[dict[str, Any]]) -> str:
    statuses = [str(task.get("status", "draft") or "draft").strip().lower() for task in tasks]
    if not statuses:
        return "draft"
    if any(status == "blocked" for status in statuses):
        return "blocked"
    if all(status == "completed" for status in statuses):
        return "completed"
    if any(status == "in_progress" for status in statuses):
        return "in_progress"
    if any(status == "planned" for status in statuses):
        return "planned"
    return "draft"


def _next_task_id(tasks: list[dict[str, Any]]) -> str:
    for preferred in ("in_progress", "planned", "draft", "blocked"):
        for task in tasks:
            if str(task.get("status", "")).strip().lower() == preferred:
                return str(task.get("task_id", "") or "")
    return ""


def summarize_implementation_plan(plan: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(plan, dict):
        return {
            "plan_id": "",
            "status": "missing",
            "counts": {"total": 0, **{status: 0 for status in TASK_STATUSES}},
            "next_task_id": "",
            "blocked_task_ids": [],
            "completed_task_ids": [],
        }
    tasks = [task for task in plan.get("tasks", []) if isinstance(task, dict)]
    counts = _task_counts(tasks)
    return {
        "plan_id": str(plan.get("plan_id", "") or ""),
        "status": _derive_plan_status(tasks),
        "counts": counts,
        "next_task_id": _next_task_id(tasks),
        "blocked_task_ids": [str(task.get("task_id", "") or "") for task in tasks if str(task.get("status", "")).strip().lower() == "blocked"],
        "completed_task_ids": [str(task.get("task_id", "") or "") for task in tasks if str(task.get("status", "")).strip().lower() == "completed"],
        "feature": str(plan.get("feature", "") or ""),
        "version": str(plan.get("version", "") or ""),
        "revision_id": str(plan.get("revision_id", "") or ""),
        "updated_at": str(plan.get("updated_at", "") or plan.get("generated_at", "") or ""),
    }


def _plan_hash(payload: dict[str, Any]) -> str:
    serializable = dict(payload)
    serializable["plan_hash"] = ""
    return "sha256:" + hashlib.sha256(json.dumps(serializable, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _matching_test_ids(test_items: list[dict[str, Any]], ac_id: str) -> list[str]:
    matched: list[str] = []
    for item in test_items:
        covers = [str(value).strip().upper() for value in item.get("covers", []) if str(value).strip()]
        if ac_id.upper() in covers:
            test_id = str(item.get("id", "") or "").strip().upper()
            if test_id:
                matched.append(test_id)
    return matched


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return ""


def _is_functional_requirements_heading(title: str) -> bool:
    normalized = str(title or "").strip().lower().rstrip(":：")
    if normalized in _FUNCTIONAL_REQUIREMENT_TITLES:
        return True
    return normalized.endswith("functional requirements") or normalized.endswith("功能需求")


def _is_functional_requirements_end_heading(title: str) -> bool:
    normalized = str(title or "").strip().lower().rstrip(":：")
    return normalized.startswith(_FUNCTIONAL_REQUIREMENT_END_TITLES)


def _split_requirement_title_and_description(text: str) -> tuple[str, str]:
    source = str(text or "").strip()
    if not source:
        return "", ""
    for separator in (" — ", " – ", " - ", ": ", "：", ":"):
        if separator in source:
            left, right = source.split(separator, 1)
            left = left.strip()
            right = right.strip()
            if left and right:
                return left, right
    return source, ""


def _extract_requirement_number(value: str) -> int | None:
    match = _FR_RE.search(str(value or "").upper())
    if not match:
        return None
    digits = re.findall(r"\d+", match.group(1))
    if not digits:
        return None
    try:
        return int(digits[-1])
    except Exception:  # noqa: BLE001
        return None


def _extract_ac_number(value: str) -> int | None:
    match = _AC_RE.search(str(value or "").upper())
    if not match:
        return None
    digits = re.findall(r"\d+", match.group(1))
    if not digits:
        return None
    try:
        return int(digits[-1])
    except Exception:  # noqa: BLE001
        return None


def _load_matrix_entries(project_root: Path, version: str, feature: str, suffix: str) -> list[dict[str, Any]]:
    slug = feature_slug(feature)
    for path in qa_matrix_candidates(project_root, version, slug, suffix):
        if not path.exists():
            continue
        payload = read_json(path, {})
        entries = payload.get("entries") if isinstance(payload, dict) else []
        if isinstance(entries, list):
            return [item for item in entries if isinstance(item, dict)]
    return []


def _load_story_scenarios(project_root: Path, version: str, feature: str) -> list[dict[str, Any]]:
    slug = feature_slug(feature)
    for path in qa_matrix_candidates(project_root, version, slug, "story-scenario-map"):
        if not path.exists():
            continue
        payload = read_json(path, {})
        scenarios = payload.get("scenarios") if isinstance(payload, dict) else []
        if not isinstance(scenarios, list) and isinstance(payload, dict):
            stories = payload.get("stories")
            if isinstance(stories, list):
                flattened: list[dict[str, Any]] = []
                for story in stories:
                    if not isinstance(story, dict):
                        continue
                    story_ac_id = str(story.get("ac_id", "") or "").strip()
                    for item in story.get("scenarios", []) if isinstance(story.get("scenarios"), list) else []:
                        if not isinstance(item, dict):
                            continue
                        merged = dict(item)
                        merged.setdefault("ac_id", story_ac_id)
                        flattened.append(merged)
                scenarios = flattened
        if isinstance(scenarios, list):
            return [item for item in scenarios if isinstance(item, dict)]
    return []


def _extract_prd_task_candidates(content: str) -> list[dict[str, str]]:
    if not str(content or "").strip():
        return []
    lines = content.splitlines()
    candidates: list[dict[str, str]] = []
    current_title = ""
    current_lines: list[str] = []
    in_functional_requirements = False

    def _push_candidate(title: str, description: str = "") -> None:
        normalized_title = str(title or "").strip()
        normalized_description = str(description or "").strip()
        if not normalized_title:
            return
        candidates.append({"title": normalized_title, "description": normalized_description})

    def _flush() -> None:
        nonlocal current_title, current_lines
        if not current_title:
            current_lines = []
            return
        description = " ".join(line.strip() for line in current_lines if line.strip()).strip()
        _push_candidate(current_title, description)
        current_title = ""
        current_lines = []

    for raw in lines:
        line = str(raw or "").rstrip()
        heading = _HEADING_RE.match(line.strip())
        if heading:
            title = heading.group(2).strip()
            if _is_functional_requirements_heading(title):
                _flush()
                in_functional_requirements = True
                continue
            if in_functional_requirements and _is_functional_requirements_end_heading(title):
                _flush()
                in_functional_requirements = False
            if in_functional_requirements and _FR_RE.search(title.upper()):
                _flush()
                current_title = title
                continue
        if not in_functional_requirements:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        heading_match = _FR_LINE_RE.match(stripped)
        bullet_match = _FR_BULLET_RE.match(stripped)
        numbered_match = _FR_NUMBERED_RE.match(stripped)
        if heading_match and not current_title:
            requirement_id = heading_match.group(1).upper()
            title_body, desc = _split_requirement_title_and_description(heading_match.group(2))
            current_title = f"{requirement_id} {title_body}".strip()
            if desc:
                current_lines.append(desc)
            continue
        if bullet_match or numbered_match:
            match = bullet_match or numbered_match
            requirement_id = str(match.group(1)).upper()
            title_body, desc = _split_requirement_title_and_description(match.group(2))
            _flush()
            current_title = f"{requirement_id} {title_body}".strip()
            if desc:
                current_lines.append(desc)
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if len(cells) >= 3 and not all(set(cell) <= {"-"," "} for cell in cells):
                first_cell = str(cells[0] or "").strip()
                if first_cell.lower() in {"fr id", "fr", "requirement id"}:
                    continue
                fr_match = _FR_LINE_RE.match(first_cell)
                if fr_match:
                    requirement_id = fr_match.group(1).upper()
                    title_body = fr_match.group(2).strip() or str(cells[1] or "").strip()
                    description = str(cells[2] or "").strip()
                elif _FR_RE.search(first_cell.upper()):
                    requirement_id = _FR_RE.search(first_cell.upper()).group(1).upper()
                    title_body = str(cells[1] or "").strip()
                    description = str(cells[2] or "").strip()
                else:
                    requirement_id = ""
                    title_body = ""
                    description = ""
                if requirement_id and title_body:
                    _flush()
                    _push_candidate(f"{requirement_id} {title_body}".strip(), description)
                    continue
        if current_title:
            if stripped.startswith(("- ", "* ", "+ ")):
                current_lines.append(stripped[2:].strip())
            else:
                current_lines.append(stripped)
    _flush()
    return candidates


def _tokenize_for_match(text: str) -> set[str]:
    lowered = str(text or "").lower()
    tokens = {token for token in re.split(r"[^a-z0-9\u4e00-\u9fff]+", lowered) if len(token) >= 2}
    return tokens


def _matrix_test_ids(project_root: Path, version: str, feature: str, ac_id: str) -> list[str]:
    matched = [
        str(item.get("tc_id", "") or "").strip().upper()
        for item in _load_matrix_entries(project_root, version, feature, "ac-test-matrix")
        if str(item.get("ac_id", "") or "").strip().upper() == ac_id.upper() and str(item.get("tc_id", "") or "").strip()
    ]
    return _normalize_text_list(matched)


def _scenario_ids(project_root: Path, version: str, feature: str, ac_ids: Iterable[str] | None, test_ids: Iterable[str] | None) -> list[str]:
    normalized_ac_ids = _normalize_ids(ac_ids)
    normalized_test_ids = _normalize_ids(test_ids)
    matched: list[str] = []
    for item in _load_story_scenarios(project_root, version, feature):
        ac_id = str(item.get("ac_id", "") or "").strip().upper()
        source_tc_id = str(item.get("source_tc_id", "") or item.get("tc_id", "") or "").strip().upper()
        if normalized_ac_ids and ac_id and ac_id in normalized_ac_ids:
            scenario_id = str(item.get("scenario_id", "") or "").strip().upper()
            if scenario_id:
                matched.append(scenario_id)
            continue
        if normalized_test_ids and source_tc_id and source_tc_id in normalized_test_ids:
            scenario_id = str(item.get("scenario_id", "") or "").strip().upper()
            if scenario_id:
                matched.append(scenario_id)
    return _normalize_text_list(matched)


def _qa_case_ids(project_root: Path, version: str, feature: str, ac_ids: Iterable[str] | None, test_ids: Iterable[str] | None) -> list[str]:
    normalized_ac_ids = _normalize_ids(ac_ids)
    normalized_test_ids = _normalize_ids(test_ids)
    matched: list[str] = []
    for item in _load_matrix_entries(project_root, version, feature, "qa9-matrix"):
        ac_id = str(item.get("ac_id", "") or "").strip().upper()
        tc_id = str(item.get("tc_id", "") or item.get("source_tc_id", "") or "").strip().upper()
        qa_case_id = str(item.get("id", "") or item.get("qa_id", "") or tc_id).strip().upper()
        if not qa_case_id:
            continue
        if normalized_ac_ids and ac_id and ac_id in normalized_ac_ids:
            matched.append(qa_case_id)
            continue
        if normalized_test_ids and tc_id and tc_id in normalized_test_ids:
            matched.append(qa_case_id)
    return _normalize_text_list(matched)


def _normalize_test_id(value: str) -> str:
    text = str(value or "").strip().upper()
    if not text:
        return ""
    match = re.match(r"^(TC-\d{3,})\b", text)
    return match.group(1) if match else text


def _scenario_test_ids(project_root: Path, version: str, feature: str, ac_ids: Iterable[str] | None, test_ids: Iterable[str] | None) -> list[str]:
    normalized_ac_ids = _normalize_ids(ac_ids)
    normalized_test_ids = _normalize_ids(test_ids)
    matched: list[str] = []
    for item in _load_story_scenarios(project_root, version, feature):
        ac_id = str(item.get("ac_id", "") or "").strip().upper()
        source_tc_id = _normalize_test_id(str(item.get("source_tc_id", "") or item.get("tc_id", "") or ""))
        if normalized_ac_ids and ac_id and ac_id in normalized_ac_ids and source_tc_id:
            matched.append(source_tc_id)
            continue
        if normalized_test_ids and source_tc_id and source_tc_id in normalized_test_ids:
            matched.append(source_tc_id)
    return _normalize_text_list(matched)


def _qa_test_ids(project_root: Path, version: str, feature: str, ac_ids: Iterable[str] | None, test_ids: Iterable[str] | None) -> list[str]:
    normalized_ac_ids = _normalize_ids(ac_ids)
    normalized_test_ids = _normalize_ids(test_ids)
    matched: list[str] = []
    for item in _load_matrix_entries(project_root, version, feature, "qa9-matrix"):
        ac_id = str(item.get("ac_id", "") or "").strip().upper()
        tc_id = _normalize_test_id(str(item.get("tc_id", "") or item.get("source_tc_id", "") or ""))
        if normalized_ac_ids and ac_id and ac_id in normalized_ac_ids and tc_id:
            matched.append(tc_id)
            continue
        if normalized_test_ids and tc_id and tc_id in normalized_test_ids:
            matched.append(tc_id)
    return _normalize_text_list(matched)


def _build_alignment_profiles(project_root: Path, version: str, feature: str, ac_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scenarios = _load_story_scenarios(project_root, version, feature)
    qa_entries = _load_matrix_entries(project_root, version, feature, "qa9-matrix")
    profiles: list[dict[str, Any]] = []
    for item in ac_items:
        ac_id = str(item.get("id", "") or "").strip().upper()
        if not ac_id:
            continue
        theme = str(item.get("theme", "") or "").strip()
        text = str(item.get("text", "") or "").strip()
        related_scenarios = [entry for entry in scenarios if str(entry.get("ac_id", "") or "").strip().upper() == ac_id]
        related_qa_entries = [entry for entry in qa_entries if str(entry.get("ac_id", "") or "").strip().upper() == ac_id]
        scenario_text = " ".join(
            " ".join(
                [
                    str(entry.get("title", "") or ""),
                    str(entry.get("assertion", "") or ""),
                    str(entry.get("scenario_family", "") or ""),
                    str(entry.get("qa_type", "") or ""),
                ]
            ).strip()
            for entry in related_scenarios
        )
        qa_text = " ".join(
            " ".join(
                [
                    str(entry.get("title", "") or ""),
                    str(entry.get("assertion", "") or ""),
                    str(entry.get("qa_type", "") or ""),
                    str(entry.get("layer", "") or ""),
                ]
            ).strip()
            for entry in related_qa_entries
        )
        profiles.append(
            {
                "ac_id": ac_id,
                "ac_number": _extract_ac_number(ac_id),
                "theme": theme,
                "text": text,
                "theme_tokens": _tokenize_for_match(theme),
                "text_tokens": _tokenize_for_match(text),
                "scenario_tokens": _tokenize_for_match(scenario_text),
                "qa_tokens": _tokenize_for_match(qa_text),
                "all_tokens": _tokenize_for_match(" ".join([theme, text, scenario_text, qa_text])),
            }
        )
    return profiles


def _candidate_alignment_score(candidate: dict[str, str], profile: dict[str, Any]) -> int:
    source = " ".join([str(candidate.get("title", "") or ""), str(candidate.get("description", "") or "")]).strip()
    explicit = [match.upper() for match in _AC_RE.findall(source)]
    if str(profile.get("ac_id", "") or "").upper() in explicit:
        return 10_000
    title = str(candidate.get("title", "") or "").strip()
    description = str(candidate.get("description", "") or "").strip()
    title_tokens = _tokenize_for_match(title)
    description_tokens = _tokenize_for_match(description)
    source_tokens = title_tokens | description_tokens

    theme = str(profile.get("theme", "") or "").strip().lower()
    text = str(profile.get("text", "") or "").strip().lower()
    normalized_source = source.lower()
    normalized_title = title.lower()
    score = 0
    theme_overlap = len(title_tokens & set(profile.get("theme_tokens", set())))
    text_overlap = len(source_tokens & set(profile.get("text_tokens", set())))
    scenario_overlap = len(source_tokens & set(profile.get("scenario_tokens", set())))
    qa_overlap = len(source_tokens & set(profile.get("qa_tokens", set())))
    all_overlap = len(source_tokens & set(profile.get("all_tokens", set())))
    if theme_overlap:
        score += 30 + theme_overlap * 15
    if text_overlap:
        score += text_overlap * 7
    if scenario_overlap:
        score += scenario_overlap * 5
    if qa_overlap:
        score += qa_overlap * 5
    if all_overlap:
        score += all_overlap * 2
    if theme and theme in normalized_source:
        score += 20
    if theme and normalized_title and normalized_title in theme:
        score += 12
    if text and text in normalized_source:
        score += 8
    candidate_number = _extract_requirement_number(title)
    ac_number = profile.get("ac_number")
    if candidate_number is not None and isinstance(ac_number, int):
        distance = abs(candidate_number - ac_number)
        if distance == 0:
            score += 35
        else:
            score += max(0, 12 - distance * 4)
    return score


def _map_candidates_to_ac_ids(
    project_root: Path,
    version: str,
    feature: str,
    candidates: list[dict[str, str]],
    ac_items: list[dict[str, Any]],
) -> list[list[str]]:
    if not candidates:
        return []
    remaining = _build_alignment_profiles(project_root, version, feature, ac_items)
    mappings: list[list[str]] = []
    for index, candidate in enumerate(candidates):
        scored_entries = sorted(
            [(_candidate_alignment_score(candidate, item), item) for item in remaining],
            key=lambda pair: (-pair[0], pair[1]["ac_id"]),
        )
        selected: list[str] = []
        if scored_entries and scored_entries[0][0] > 0:
            best_score = scored_entries[0][0]
            threshold = max(18, best_score - 20)
            selected = [item["ac_id"] for score, item in scored_entries if score >= threshold]
            candidate_number = _extract_requirement_number(str(candidate.get("title", "") or ""))
            description_tokens = _tokenize_for_match(str(candidate.get("description", "") or ""))
            if candidate_number is not None and description_tokens:
                for score, item in scored_entries:
                    ac_id = item["ac_id"]
                    ac_number = item.get("ac_number")
                    if ac_id in selected or not isinstance(ac_number, int):
                        continue
                    text_overlap = len(description_tokens & set(item.get("text_tokens", set())))
                    if abs(candidate_number - ac_number) <= 1 and text_overlap >= 2 and score >= 12:
                        selected.append(ac_id)
        if not selected and remaining:
            slice_size = max(1, len(remaining) // max(1, len(candidates) - index))
            selected = [item["ac_id"] for item in remaining[:slice_size]]
        mappings.append(selected)
        remaining = [item for item in remaining if item["ac_id"] not in selected]
    if remaining and mappings:
        mappings[-1].extend(item["ac_id"] for item in remaining if item["ac_id"] not in mappings[-1])
    return [list(dict.fromkeys(group)) for group in mappings]


def _render_plan_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Beacon Implementation Plan",
        "",
        f"- plan_id: `{payload.get('plan_id', '')}`",
        f"- feature: `{payload.get('feature', '')}`",
        f"- version: `{payload.get('version', '')}`",
        f"- revision_id: `{payload.get('revision_id', '')}`",
        f"- baseline_hash: `{payload.get('baseline_hash', '')}`",
        f"- delivery_baseline_id: `{payload.get('baseline_id', '')}`",
        f"- delivery_baseline_source_hash: `{payload.get('source_hash', '')}`",
        f"- plan_hash: `{payload.get('plan_hash', '')}`",
        f"- status: `{payload.get('status', '')}`",
        "",
        "## Source Refs",
    ]
    source_refs = payload.get("source_refs") if isinstance(payload.get("source_refs"), dict) else {}
    if source_refs:
        for key, value in source_refs.items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- none")
    boundary_principles = payload.get("boundary_principles") if isinstance(payload.get("boundary_principles"), list) else []
    lines.extend(["", "## Boundary Principles"])
    if boundary_principles:
        for item in boundary_principles:
            if not isinstance(item, dict):
                continue
            lines.append(f"- `{item.get('id', '')}`: `{item.get('heading', '')}`")
    else:
        lines.append("- none")
    team_mode = payload.get("team_mode") if isinstance(payload.get("team_mode"), dict) else {}
    if team_mode:
        lines.extend(
            [
                "",
                "## Team Mode",
                f"- preferred_surface: `{team_mode.get('preferred_surface', '')}`",
                f"- preferred_runner: `{team_mode.get('preferred_runner', '')}`",
                f"- plan_command: `{team_mode.get('plan_command', '')}`",
                f"- run_command: `{team_mode.get('run_command', '')}`",
                f"- dev_run_command: `{team_mode.get('dev_run_command', '')}`",
                f"- qa_team_command: `{team_mode.get('qa_team_command', '')}`",
                f"- roles: {', '.join(team_mode.get('roles', [])) or '-'}",
            ]
        )
        execution_order = team_mode.get("execution_order") if isinstance(team_mode.get("execution_order"), list) else []
        if execution_order:
            lines.append(f"- execution_order: {', '.join(execution_order)}")
    git_workflow = payload.get("git_workflow") if isinstance(payload.get("git_workflow"), dict) else {}
    if git_workflow:
        lines.extend(
            [
                "",
                "## Git Workflow",
                f"- mode: `{git_workflow.get('mode', '')}`",
                f"- expected_branch: `{git_workflow.get('expected_branch', '')}`",
                f"- branch_prefix: `{git_workflow.get('branch_prefix', '')}`",
                f"- base_branch: `{git_workflow.get('base_branch', '')}`",
                f"- use_git_worktree: `{bool(git_workflow.get('use_git_worktree', False))}`",
                f"- require_clean_worktree_for_switch: `{bool(git_workflow.get('require_clean_worktree_for_switch', True))}`",
                f"- service_directories: {', '.join(git_workflow.get('service_directories', [])) or '-'}",
                f"- git_workflow_ref: `{payload.get('git_workflow_ref', '')}`",
            ]
        )
    diagram_truth = payload.get("diagram_truth") if isinstance(payload.get("diagram_truth"), dict) else {}
    if diagram_truth:
        lines.extend(
            [
                "",
                "## Diagram Truth",
                f"- required: `{bool(diagram_truth.get('required', False))}`",
                f"- ready: `{bool(diagram_truth.get('ready', False))}`",
                f"- diagram_types: {', '.join(diagram_truth.get('diagram_types', [])) or '-'}",
                f"- state_axes: {', '.join(diagram_truth.get('state_axes', [])) or '-'}",
                f"- review_gates: {', '.join(diagram_truth.get('review_gates', [])) or '-'}",
                f"- qa_coverage_hints: {', '.join(diagram_truth.get('qa_coverage_hints', [])) or '-'}",
            ]
        )
    lines.extend(["", "## Tasks"])
    tasks = [task for task in payload.get("tasks", []) if isinstance(task, dict)]
    if not tasks:
        lines.append("- none")
    for task in tasks:
        lines.extend(
            [
                "",
                f"### {task.get('task_id', '')} — {task.get('title', '')}",
                f"- status: `{task.get('status', '')}`",
                f"- mapped_ac_ids: {', '.join(task.get('mapped_ac_ids', [])) or '-'}",
                f"- mapped_test_ids: {', '.join(task.get('mapped_test_ids', [])) or '-'}",
                f"- mapped_scenario_ids: {', '.join(task.get('mapped_scenario_ids', [])) or '-'}",
                f"- mapped_qa_case_ids: {', '.join(task.get('mapped_qa_case_ids', [])) or '-'}",
                f"- depends_on: {', '.join(task.get('depends_on', [])) or '-'}",
                f"- target_modules: {', '.join(task.get('target_modules', [])) or '-'}",
                f"- diagram_review_gates: {', '.join(task.get('diagram_review_gates', [])) or '-'}",
            ]
        )
    return "\n".join(lines) + "\n"


def load_implementation_plan(project_root: Path, *, version: str = "auto", feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    path = implementation_plan_json_path(project_root, resolved_version, feature)
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def load_implementation_plan_progress(project_root: Path, *, version: str = "auto", feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    path = implementation_plan_progress_path(project_root, resolved_version, feature)
    payload = read_json(path, {})
    if isinstance(payload, dict) and payload:
        return payload
    plan = load_implementation_plan(project_root, version=resolved_version, feature=feature)
    summary = summarize_implementation_plan(plan)
    return {
        "schema_version": "1.0",
        "plan_id": summary.get("plan_id", ""),
        "feature": summary.get("feature", ""),
        "version": summary.get("version", ""),
        "revision_id": summary.get("revision_id", ""),
        "status": summary.get("status", "missing"),
        "counts": summary.get("counts", {}),
        "blocked_task_ids": summary.get("blocked_task_ids", []),
        "completed_task_ids": summary.get("completed_task_ids", []),
        "next_task_id": summary.get("next_task_id", ""),
        "updated_at": summary.get("updated_at", ""),
        "task_states": [
            {
                "task_id": str(task.get("task_id", "") or ""),
                "status": str(task.get("status", "") or ""),
                "blocked_reason": str(task.get("blocked_reason", "") or ""),
                "mapped_ac_ids": [str(item) for item in task.get("mapped_ac_ids", []) if str(item).strip()],
                "mapped_test_ids": [str(item) for item in task.get("mapped_test_ids", []) if str(item).strip()],
                "mapped_scenario_ids": [str(item) for item in task.get("mapped_scenario_ids", []) if str(item).strip()],
                "mapped_qa_case_ids": [str(item) for item in task.get("mapped_qa_case_ids", []) if str(item).strip()],
            }
            for task in plan.get("tasks", [])
            if isinstance(task, dict)
        ],
    }


def _write_implementation_plan(project_root: Path, *, version: str, feature: str, payload: dict[str, Any]) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    payload = dict(payload)
    payload["version"] = resolved_version
    payload["feature"] = feature
    payload["feature_slug"] = feature_slug(feature)
    payload["updated_at"] = now_iso()
    payload["status"] = _derive_plan_status([task for task in payload.get("tasks", []) if isinstance(task, dict)])
    payload["plan_hash"] = _plan_hash(payload)
    write_json(implementation_plan_json_path(project_root, resolved_version, feature), payload)
    markdown_path = implementation_plan_markdown_path(project_root, resolved_version, feature)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_plan_markdown(payload), encoding="utf-8")
    progress_summary = summarize_implementation_plan(payload)
    progress_payload = {
        "schema_version": "1.0",
        "plan_id": progress_summary.get("plan_id", ""),
        "feature": feature,
        "version": resolved_version,
        "revision_id": str(payload.get("revision_id", "") or ""),
        "status": progress_summary.get("status", "missing"),
        "counts": progress_summary.get("counts", {}),
        "blocked_task_ids": progress_summary.get("blocked_task_ids", []),
        "completed_task_ids": progress_summary.get("completed_task_ids", []),
        "next_task_id": progress_summary.get("next_task_id", ""),
        "task_states": [
            {
                "task_id": str(task.get("task_id", "") or ""),
                "status": str(task.get("status", "") or ""),
                "blocked_reason": str(task.get("blocked_reason", "") or ""),
                "mapped_ac_ids": [str(item) for item in task.get("mapped_ac_ids", []) if str(item).strip()],
                "mapped_test_ids": [str(item) for item in task.get("mapped_test_ids", []) if str(item).strip()],
                "mapped_scenario_ids": [str(item) for item in task.get("mapped_scenario_ids", []) if str(item).strip()],
                "mapped_qa_case_ids": [str(item) for item in task.get("mapped_qa_case_ids", []) if str(item).strip()],
            }
            for task in payload.get("tasks", [])
            if isinstance(task, dict)
        ],
        "updated_at": payload["updated_at"],
    }
    write_json(implementation_plan_progress_path(project_root, resolved_version, feature), progress_payload)
    return payload


def compile_implementation_plan(project_root: Path, *, version: str = "auto", feature: str) -> tuple[int, dict[str, Any]]:
    resolved_version = resolve_target_version(project_root, version)
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=True)
    if str(revision.get("doc_status", "draft") or "draft") != "frozen":
        payload = {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": "revision_not_frozen",
            "feature": feature,
            "feature_slug": feature_slug(feature),
            "version": resolved_version,
            "recommended_command": f'beacon freeze "{feature}" --project-root {project_root} --version {resolved_version}',
        }
        return 2, payload
    existing_contract = load_technical_review_contract(project_root, version=resolved_version, feature=feature)
    if existing_contract:
        materialize_technical_review_contract(
            project_root,
            version=resolved_version,
            feature=feature,
            revision_id=str(revision.get("revision_id", "") or ""),
        )
    technical_review_gate = build_technical_review_gate_payload(
        project_root,
        version=resolved_version,
        feature=feature,
        revision_id=str(revision.get("revision_id", "") or ""),
    )
    if bool(technical_review_gate.get("blocked")):
        payload = {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": str(technical_review_gate.get("reason_code") or "technical_review_contract_missing"),
            "feature": feature,
            "feature_slug": feature_slug(feature),
            "version": resolved_version,
            "technical_review_gate": technical_review_gate,
            "recommended_command": str(technical_review_gate.get("contract_json_path") or ""),
        }
        return 2, payload

    story = load_story_state(
        project_root,
        version=resolved_version,
        feature=feature,
        create_if_missing=True,
        revision_id=str(revision.get("revision_id", "R1") or "R1"),
    ) or {}
    items = [item for item in story.get("items", []) if isinstance(item, dict)]
    ac_items = [item for item in items if str(item.get("kind", "") or "") == "ac" and bool(item.get("required", True))]
    test_items = [item for item in items if str(item.get("kind", "") or "") == "test" and bool(item.get("required", True))]
    source_refs = {
        "user_story": str((project_root / "docs" / "beacon" / resolved_version / "user-story" / f"{feature_slug(feature)}.md").relative_to(project_root)),
        "prd": str((project_root / "docs" / "beacon" / resolved_version / "prd" / f"{feature_slug(feature)}.md").relative_to(project_root)),
        "test_case": str((project_root / "docs" / "beacon" / resolved_version / "qa" / "test-cases" / f"{feature_slug(feature)}.md").relative_to(project_root)),
    }
    ac_matrix_candidate = next((path for path in qa_matrix_candidates(project_root, resolved_version, feature_slug(feature), "ac-test-matrix") if path.exists()), None)
    if ac_matrix_candidate is not None:
        source_refs["ac_matrix"] = str(ac_matrix_candidate.relative_to(project_root))
    scenario_map_candidate = next((path for path in qa_matrix_candidates(project_root, resolved_version, feature_slug(feature), "story-scenario-map") if path.exists()), None)
    if scenario_map_candidate is not None:
        source_refs["story_scenario_map"] = str(scenario_map_candidate.relative_to(project_root))
    qa9_matrix_candidate = next((path for path in qa_matrix_candidates(project_root, resolved_version, feature_slug(feature), "qa9-matrix") if path.exists()), None)
    if qa9_matrix_candidate is not None:
        source_refs["qa9_matrix"] = str(qa9_matrix_candidate.relative_to(project_root))
    missing_refs = [path for path in source_refs.values() if not (project_root / path).exists()]
    if missing_refs:
        payload = {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": "implementation_plan_source_refs_incomplete",
            "feature": feature,
            "feature_slug": feature_slug(feature),
            "version": resolved_version,
            "missing_source_refs": missing_refs,
        }
        return 2, payload
    diagram_truth = load_feature_diagram_truth(project_root, version=resolved_version, feature=feature)
    if bool(diagram_truth.get("required")) and not bool(diagram_truth.get("ready")):
        payload = {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": "diagram_truth_missing",
            "feature": feature,
            "feature_slug": feature_slug(feature),
            "version": resolved_version,
            "diagram_truth": diagram_truth,
            "recommended_command": (
                f'beacon brainstorm run "补齐 {feature} 的 diagram truth layer" '
                f'--project-root {project_root} --version {resolved_version} --feature "{feature}" --json'
            ),
        }
        return 2, payload

    prd_content = _read_text(project_root / source_refs["prd"])
    prd_candidates = _extract_prd_task_candidates(prd_content)
    diagram_task_projection = {
        "diagram_types": list(diagram_truth.get("diagram_types", [])),
        "state_axes": list(diagram_truth.get("state_axes", [])),
        "review_gates": list(diagram_truth.get("review_gates", [])),
        "qa_coverage_hints": list(diagram_truth.get("qa_coverage_hints", [])),
    }
    tasks: list[dict[str, Any]] = []
    previous_task_id = ""
    if prd_candidates:
        mapped_groups = _map_candidates_to_ac_ids(project_root, resolved_version, feature, prd_candidates, ac_items)
        ac_lookup = {str(item.get("id", "") or "").strip().upper(): item for item in ac_items}
        for idx, candidate in enumerate(prd_candidates, start=1):
            mapped_ac_ids = mapped_groups[idx - 1] if idx - 1 < len(mapped_groups) else []
            mapped_test_ids: list[str] = []
            for ac_id in mapped_ac_ids:
                mapped_test_ids.extend(_matrix_test_ids(project_root, resolved_version, feature, ac_id) or _matching_test_ids(test_items, ac_id))
            mapped_test_ids.extend(_scenario_test_ids(project_root, resolved_version, feature, mapped_ac_ids, mapped_test_ids))
            mapped_test_ids.extend(_qa_test_ids(project_root, resolved_version, feature, mapped_ac_ids, mapped_test_ids))
            normalized_test_ids = _normalize_text_list(_normalize_test_id(test_id) for test_id in mapped_test_ids)
            description = candidate.get("description", "").strip()
            if not description and mapped_ac_ids:
                description = " / ".join(str(ac_lookup.get(ac_id, {}).get("text", "")).strip() for ac_id in mapped_ac_ids if ac_lookup.get(ac_id))
            task_id = f"ITASK-{idx:03d}"
            task = {
                "task_id": task_id,
                "title": candidate.get("title", "").strip() or f"FR task {idx}",
                "description": description or "Implementation task",
                "mapped_story_ids": [str(story.get("story_id", "US-001") or "US-001")],
                "mapped_ac_ids": mapped_ac_ids,
                "mapped_test_ids": normalized_test_ids,
                "mapped_scenario_ids": _scenario_ids(project_root, resolved_version, feature, mapped_ac_ids, normalized_test_ids),
                "mapped_qa_case_ids": _qa_case_ids(project_root, resolved_version, feature, mapped_ac_ids, normalized_test_ids),
                "depends_on": [previous_task_id] if previous_task_id else [],
                "target_modules": [],
                "diagram_review_gates": list(diagram_task_projection["review_gates"]),
                "diagram_state_axes": list(diagram_task_projection["state_axes"]),
                "status": "planned",
                "evidence_refs": [],
                "changed_files": [],
                "blocked_reason": "",
                "started_at": "",
                "completed_at": "",
            }
            previous_task_id = task_id
            tasks.append(task)
    else:
        for idx, ac in enumerate(ac_items, start=1):
            ac_id = str(ac.get("id", "") or "").strip().upper()
            text = str(ac.get("text", "") or "").strip() or str(ac.get("theme", "") or "").strip() or "Implementation task"
            task_id = f"ITASK-{idx:03d}"
            mapped_test_ids = _matrix_test_ids(project_root, resolved_version, feature, ac_id) or _matching_test_ids(test_items, ac_id)
            mapped_test_ids.extend(_scenario_test_ids(project_root, resolved_version, feature, [ac_id], mapped_test_ids))
            mapped_test_ids.extend(_qa_test_ids(project_root, resolved_version, feature, [ac_id], mapped_test_ids))
            normalized_test_ids = _normalize_text_list(_normalize_test_id(test_id) for test_id in mapped_test_ids)
            task = {
                "task_id": task_id,
                "title": _task_title(ac_id, text),
                "description": text,
                "mapped_story_ids": [str(story.get("story_id", "US-001") or "US-001")],
                "mapped_ac_ids": [ac_id] if ac_id else [],
                "mapped_test_ids": normalized_test_ids,
                "mapped_scenario_ids": _scenario_ids(project_root, resolved_version, feature, [ac_id], normalized_test_ids),
                "mapped_qa_case_ids": _qa_case_ids(project_root, resolved_version, feature, [ac_id], normalized_test_ids),
                "depends_on": [previous_task_id] if previous_task_id else [],
                "target_modules": [],
                "diagram_review_gates": list(diagram_task_projection["review_gates"]),
                "diagram_state_axes": list(diagram_task_projection["state_axes"]),
                "status": "planned",
                "evidence_refs": [],
                "changed_files": [],
                "blocked_reason": "",
                "started_at": "",
                "completed_at": "",
            }
            previous_task_id = task_id
            tasks.append(task)
    if not tasks:
        tasks.append(
            {
                "task_id": "ITASK-001",
                "title": "Implementation baseline task",
                "description": "Implement current frozen revision",
                "mapped_story_ids": [str(story.get("story_id", "US-001") or "US-001")],
                "mapped_ac_ids": [],
                "mapped_test_ids": [],
                "mapped_scenario_ids": [],
                "mapped_qa_case_ids": [],
                "depends_on": [],
                "target_modules": [],
                "diagram_review_gates": list(diagram_task_projection["review_gates"]),
                "diagram_state_axes": list(diagram_task_projection["state_axes"]),
                "status": "planned",
                "evidence_refs": [],
                "changed_files": [],
                "blocked_reason": "",
                "started_at": "",
                "completed_at": "",
            }
        )

    git_workflow = materialize_implementation_git_workflow_contract(project_root, version=resolved_version, feature=feature)
    baseline = load_implementation_delivery_baseline(project_root, version=resolved_version, feature=feature)
    expected_revision_id = str(revision.get("revision_id", "") or "")
    if not baseline or baseline_revision_id(baseline) != expected_revision_id:
        baseline = materialize_implementation_delivery_baseline(
            project_root,
            version=resolved_version,
            feature=feature,
            revision_id=expected_revision_id,
            seed=git_workflow,
        )
    baseline_projection = projection_metadata(baseline, project_root=project_root, version=resolved_version, feature=feature)
    git_workflow.update(baseline_projection)
    payload = {
        "schema_version": "1.0",
        "plan_id": f"plan-{feature_slug(feature)}-{str(revision.get('revision_id', 'R1') or 'R1').lower()}",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "revision_id": str(revision.get("revision_id", "") or ""),
        "baseline_hash": str(revision.get("baseline_hash", "") or ""),
        "plan_hash": "",
        "status": "planned",
        "source_refs": source_refs,
        "boundary_principles": global_boundary_principle_summaries(),
        "workstreams": [
            {
                "workstream_id": "implementation-main",
                "title": "Implementation Mainline",
                "task_ids": [str(task.get("task_id", "") or "") for task in tasks],
            }
        ],
        "task_mapping_source": "prd-sections" if prd_candidates else "acceptance-criteria",
        "diagram_truth": diagram_truth,
        "review_gates": list(diagram_truth.get("review_gates", [])),
        "qa_coverage_hints": list(diagram_truth.get("qa_coverage_hints", [])),
        "tasks": tasks,
        "team_mode": _team_mode_contract(project_root, version=resolved_version, feature=feature),
        "git_workflow": git_workflow,
        "git_workflow_ref": str(implementation_git_workflow_json_path(project_root, resolved_version, feature).relative_to(project_root)),
        "git_workflow_markdown_ref": str(implementation_git_workflow_markdown_path(project_root, resolved_version, feature).relative_to(project_root)),
        "base_branch": str(git_workflow.get("base_branch", "") or ""),
        "target_branch": str(git_workflow.get("expected_branch", "") or ""),
        "branch_prefix": str(git_workflow.get("branch_prefix", "") or ""),
        "use_git_worktree": bool(git_workflow.get("use_git_worktree", False)),
        "worktree_root": str(git_workflow.get("worktree_root", "") or ""),
        "direct_delivery_services": _normalize_string_list(git_workflow.get("direct_delivery_services")) or ["."],
        "writable_services": _normalize_string_list(git_workflow.get("writable_services"))
        or _normalize_string_list(git_workflow.get("direct_delivery_services"))
        or ["."],
        "reference_only_services": _normalize_string_list(git_workflow.get("reference_only_services")) or ["docs"],
        "delivery_baseline": baseline_projection,
        "canonical_envelope_ref": str(baseline_projection.get("canonical_envelope_ref", "") or ""),
        "generated_at": now_iso(),
    }
    payload.update(baseline_projection)
    written = _write_implementation_plan(project_root, version=resolved_version, feature=feature, payload=payload)
    return 0, {
        "schema_version": "1.0",
        "status": "planned",
        "blocked": False,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "plan_id": written.get("plan_id", ""),
        "revision_id": written.get("revision_id", ""),
        "baseline_hash": written.get("baseline_hash", ""),
        "plan_path": str(implementation_plan_json_path(project_root, resolved_version, feature).relative_to(project_root)),
        "plan_markdown_path": str(implementation_plan_markdown_path(project_root, resolved_version, feature).relative_to(project_root)),
        "progress_path": str(implementation_plan_progress_path(project_root, resolved_version, feature).relative_to(project_root)),
        "git_workflow_ref": str(implementation_git_workflow_json_path(project_root, resolved_version, feature).relative_to(project_root)),
        "git_workflow_markdown_ref": str(implementation_git_workflow_markdown_path(project_root, resolved_version, feature).relative_to(project_root)),
        "counts": _task_counts(tasks),
        "team_mode": payload.get("team_mode", {}),
        "git_workflow": payload.get("git_workflow", {}),
        "diagram_truth": payload.get("diagram_truth", {}),
    }


def build_implementation_plan_gate_payload(project_root: Path, *, version: str = "auto", feature: str, run_id: str = "") -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=False)
    plan_path = implementation_plan_json_path(project_root, resolved_version, feature)
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "run_id": run_id,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "expected_plan": str(plan_path.relative_to(project_root)),
        "expected_revision_id": str(revision.get("revision_id", "") or ""),
        "baseline_hash": str(revision.get("baseline_hash", "") or ""),
        "recommended_command": f'beacon implement plan "{feature}" --project-root {project_root} --version {resolved_version}',
        "generated_at": now_iso(),
    }
    if str(revision.get("doc_status", "draft") or "draft") != "frozen":
        payload.update({"status": "blocked", "blocked": True, "reason_code": "revision_not_frozen"})
        return payload
    technical_review_gate = build_technical_review_gate_payload(
        project_root,
        version=resolved_version,
        feature=feature,
        revision_id=str(revision.get("revision_id", "") or ""),
    )
    if bool(technical_review_gate.get("blocked")):
        payload.update(
            {
                "status": "blocked",
                "blocked": True,
                "reason_code": str(technical_review_gate.get("reason_code") or "technical_review_contract_missing"),
                "technical_review_gate": technical_review_gate,
                "recommended_command": str(technical_review_gate.get("contract_json_path") or ""),
            }
        )
        return payload
    if not plan_path.exists():
        payload.update({"status": "blocked", "blocked": True, "reason_code": "implementation_plan_missing"})
        return payload
    plan = read_json(plan_path, {})
    if not isinstance(plan, dict) or not plan:
        payload.update({"status": "blocked", "blocked": True, "reason_code": "implementation_plan_invalid"})
        return payload
    source_refs = plan.get("source_refs") if isinstance(plan.get("source_refs"), dict) else {}
    tasks = plan.get("tasks") if isinstance(plan.get("tasks"), list) else None
    if not source_refs or not tasks:
        payload.update({"status": "blocked", "blocked": True, "reason_code": "implementation_plan_invalid"})
        return payload
    missing_refs = [str(path) for path in source_refs.values() if not (project_root / str(path)).exists()]
    if missing_refs:
        payload.update(
            {
                "status": "blocked",
                "blocked": True,
                "reason_code": "implementation_plan_source_refs_incomplete",
                "missing_source_refs": missing_refs,
            }
        )
        return payload
    if str(plan.get("feature", "") or "") != feature or str(plan.get("version", "") or "") != resolved_version:
        payload.update({"status": "blocked", "blocked": True, "reason_code": "implementation_plan_feature_version_mismatch"})
        return payload
    if str(plan.get("revision_id", "") or "") != str(revision.get("revision_id", "") or ""):
        payload.update({"status": "blocked", "blocked": True, "reason_code": "implementation_plan_revision_mismatch"})
        return payload
    if str(plan.get("baseline_hash", "") or "") != str(revision.get("baseline_hash", "") or ""):
        payload.update({"status": "blocked", "blocked": True, "reason_code": "implementation_plan_baseline_mismatch"})
        return payload
    baseline = load_implementation_delivery_baseline(project_root, version=resolved_version, feature=feature)
    if not baseline:
        payload.update({"status": "blocked", "blocked": True, "reason_code": "delivery_baseline_missing"})
        return payload
    plan_projection_issues = validate_projection_against_baseline(plan, baseline, projection_name="implementation_plan")
    git_workflow = plan.get("git_workflow") if isinstance(plan.get("git_workflow"), dict) else {}
    git_projection_issues = validate_projection_against_baseline(git_workflow, baseline, projection_name="git_workflow") if git_workflow else []
    if plan_projection_issues or git_projection_issues:
        payload.update(
            {
                "status": "blocked",
                "blocked": True,
                "reason_code": "delivery_baseline_projection_drift",
                "projection_issues": [*plan_projection_issues, *git_projection_issues],
            }
        )
        return payload
    payload.update(
        {
            "status": "pass",
            "blocked": False,
            "plan_id": str(plan.get("plan_id", "") or ""),
            "plan_path": str(plan_path.relative_to(project_root)),
            "progress_path": str(implementation_plan_progress_path(project_root, resolved_version, feature).relative_to(project_root)),
        }
    )
    return payload


def mark_implementation_plan_started(project_root: Path, *, version: str = "auto", feature: str, run_id: str) -> dict[str, Any]:
    plan = load_implementation_plan(project_root, version=version, feature=feature)
    if not plan:
        return {}
    tasks = [task for task in plan.get("tasks", []) if isinstance(task, dict)]
    for task in tasks:
        if str(task.get("status", "draft") or "draft").strip().lower() in {"planned", "draft"}:
            task["status"] = "in_progress"
            task["started_at"] = str(task.get("started_at", "") or now_iso())
            task["active_run_id"] = run_id
            refs = _normalize_text_list([*(task.get("evidence_refs", []) or []), f"run:{run_id}"])
            task["evidence_refs"] = refs
            break
    return _write_implementation_plan(project_root, version=version, feature=feature, payload=plan)


def mark_implementation_plan_failed(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    run_id: str,
    reason_code: str,
) -> dict[str, Any]:
    plan = load_implementation_plan(project_root, version=version, feature=feature)
    if not plan:
        return {}
    tasks = [task for task in plan.get("tasks", []) if isinstance(task, dict)]
    for task in tasks:
        if str(task.get("status", "")).strip().lower() == "in_progress" and str(task.get("active_run_id", "") or "").strip() == run_id:
            task["status"] = "blocked"
            task["blocked_reason"] = str(reason_code or "implementation_failed")
            task["active_run_id"] = ""
            task["evidence_refs"] = _normalize_text_list([*(task.get("evidence_refs", []) or []), f"run:{run_id}"])
    return _write_implementation_plan(project_root, version=version, feature=feature, payload=plan)


def update_plan_progress_for_implementation(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    run_id: str,
    implemented_item_ids: Iterable[str] | None = None,
    task_ids: Iterable[str] | None = None,
    changed_files: Iterable[str] | None = None,
    evidence_refs: Iterable[str] | None = None,
) -> dict[str, Any]:
    plan = load_implementation_plan(project_root, version=version, feature=feature)
    if not plan:
        return {}
    item_ids = _normalize_ids(implemented_item_ids)
    target_task_ids = _normalize_ids(task_ids)
    normalized_changed_files = _normalize_text_list(changed_files)
    normalized_evidence_refs = _normalize_text_list([*(evidence_refs or []), f"run:{run_id}"])
    touched = False
    for task in [task for task in plan.get("tasks", []) if isinstance(task, dict)]:
        mapped_ac_ids = _normalize_ids(task.get("mapped_ac_ids", []))
        task_id = str(task.get("task_id", "") or "").strip().upper()
        active_run_id = str(task.get("active_run_id", "") or "").strip()
        if target_task_ids and active_run_id == run_id and task_id not in target_task_ids and str(task.get("status", "")).strip().lower() == "in_progress":
            task["status"] = "planned"
            task["active_run_id"] = ""
        if target_task_ids and task_id not in target_task_ids:
            continue
        if item_ids and mapped_ac_ids and item_ids.isdisjoint(mapped_ac_ids):
            continue
        if item_ids or target_task_ids or len([task for task in plan.get("tasks", []) if isinstance(task, dict)]) == 1:
            task["status"] = "completed"
            task["started_at"] = str(task.get("started_at", "") or now_iso())
            task["completed_at"] = now_iso()
            task["blocked_reason"] = ""
            task["active_run_id"] = ""
            task["evidence_refs"] = _normalize_text_list([*(task.get("evidence_refs", []) or []), *normalized_evidence_refs])
            task["changed_files"] = _normalize_text_list([*(task.get("changed_files", []) or []), *normalized_changed_files])
            touched = True
    if not touched and plan.get("tasks"):
        first = next((task for task in plan.get("tasks", []) if isinstance(task, dict)), None)
        if first is not None:
            first["status"] = "completed"
            first["started_at"] = str(first.get("started_at", "") or now_iso())
            first["completed_at"] = now_iso()
            first["active_run_id"] = ""
            first["evidence_refs"] = _normalize_text_list([*(first.get("evidence_refs", []) or []), *normalized_evidence_refs])
            first["changed_files"] = _normalize_text_list([*(first.get("changed_files", []) or []), *normalized_changed_files])
    return _write_implementation_plan(project_root, version=version, feature=feature, payload=plan)


def update_plan_progress_for_verification(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    run_id: str,
    verified_item_ids: Iterable[str] | None = None,
    failed_item_ids: Iterable[str] | None = None,
    evidence_refs: Iterable[str] | None = None,
) -> dict[str, Any]:
    plan = load_implementation_plan(project_root, version=version, feature=feature)
    if not plan:
        return {}
    verified_ids = _normalize_ids(verified_item_ids)
    failed_ids = _normalize_ids(failed_item_ids)
    refs = _normalize_text_list([*(evidence_refs or []), f"verify:{run_id}"])
    for task in [task for task in plan.get("tasks", []) if isinstance(task, dict)]:
        mapped_ac_ids = _normalize_ids(task.get("mapped_ac_ids", []))
        mapped_test_ids = _normalize_ids(task.get("mapped_test_ids", []))
        if failed_ids and (not failed_ids.isdisjoint(mapped_test_ids) or not failed_ids.isdisjoint(mapped_ac_ids)):
            task["status"] = "blocked"
            task["blocked_reason"] = "verification_failed"
            task["active_run_id"] = ""
            task["evidence_refs"] = _normalize_text_list([*(task.get("evidence_refs", []) or []), *refs])
            continue
        if verified_ids and (not verified_ids.isdisjoint(mapped_test_ids) or not verified_ids.isdisjoint(mapped_ac_ids)):
            if str(task.get("status", "")).strip().lower() in {"draft", "planned", "in_progress", "blocked"}:
                task["status"] = "completed"
                task["completed_at"] = str(task.get("completed_at", "") or now_iso())
                task["active_run_id"] = ""
                task["blocked_reason"] = ""
            task["evidence_refs"] = _normalize_text_list([*(task.get("evidence_refs", []) or []), *refs])
    return _write_implementation_plan(project_root, version=version, feature=feature, payload=plan)


def mark_implementation_plan_accepted(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    accepted_by: str,
) -> dict[str, Any]:
    plan = load_implementation_plan(project_root, version=version, feature=feature)
    if not plan:
        return {}
    plan["accepted_at"] = now_iso()
    plan["accepted_by"] = accepted_by
    if all(str(task.get("status", "")).strip().lower() == "completed" for task in plan.get("tasks", []) if isinstance(task, dict)):
        plan["status"] = "completed"
    return _write_implementation_plan(project_root, version=version, feature=feature, payload=plan)
