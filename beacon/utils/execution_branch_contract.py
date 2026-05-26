"""Execution material branch/worktree contract extraction."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


_BULLET_RE = re.compile(r"^\s*[-*]\s+([A-Za-z0-9_ -]+):\s*`?([^`\n]+?)`?\s*$")


def _clean_cell(value: str) -> str:
    return str(value or "").strip().strip("`").strip()


def _normalize_key(value: str) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return ""


def _markdown_files(project_root: Path, version: str, feature: str) -> list[Path]:
    execution_dir = project_root / "docs" / "beacon" / version / "execution"
    if not execution_dir.exists():
        return []
    slug = feature_slug(feature)
    ordered: list[Path] = []
    for prefix in ("branch-governance", "git-workflow", "deterministic-implementation-contract"):
        exact = execution_dir / f"{prefix}-{slug}.md"
        if exact.exists():
            ordered.append(exact)
    return ordered


def _parse_bullets(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        match = _BULLET_RE.match(line)
        if not match:
            continue
        key = _normalize_key(match.group(1))
        value = _clean_cell(match.group(2))
        if key and value:
            out[key] = value
    return out


def _parse_section_list(text: str, title: str) -> list[str]:
    values: list[str] = []
    in_section = False
    title_norm = title.strip().lower()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            heading = line.lstrip("#").strip().lower()
            if in_section and heading != title_norm:
                break
            in_section = heading == title_norm
            continue
        if not in_section or not line.startswith("- "):
            continue
        value = _clean_cell(line[2:])
        if value and value not in values:
            values.append(value)
    return values


def _looks_like_branch_header(value: str) -> bool:
    text = value.lower()
    return "branch" in text


def _looks_like_worktree_header(value: str) -> bool:
    text = value.lower()
    return "worktree" in text


def _parse_service_table(text: str) -> tuple[dict[str, str], dict[str, str]]:
    branch_map: dict[str, str] = {}
    worktree_map: dict[str, str] = {}
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        cells = [_clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[0].lower() not in {"service", "服务"}:
            continue
        branch_index = next((i for i, cell in enumerate(cells) if _looks_like_branch_header(cell)), -1)
        worktree_index = next((i for i, cell in enumerate(cells) if _looks_like_worktree_header(cell)), -1)
        if branch_index < 0 or worktree_index < 0:
            continue
        for row in lines[index + 1 :]:
            if not row.strip().startswith("|"):
                break
            row_cells = [_clean_cell(cell) for cell in row.strip().strip("|").split("|")]
            if len(row_cells) <= max(branch_index, worktree_index):
                continue
            if all(set(cell) <= {"-", ":"} for cell in row_cells if cell):
                continue
            service = row_cells[0]
            branch = row_cells[branch_index]
            worktree = row_cells[worktree_index]
            if service and branch:
                branch_map[service] = branch
            if service and worktree:
                worktree_map[service] = worktree
    return branch_map, worktree_map


def _merge_non_empty(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
        if isinstance(value, dict):
            current = target.get(key) if isinstance(target.get(key), dict) else {}
            target[key] = {**current, **value}
        elif isinstance(value, list):
            current_list = target.get(key) if isinstance(target.get(key), list) else []
            target[key] = list(dict.fromkeys([*current_list, *value]))
        elif value not in ("", None):
            target[key] = value


def load_execution_branch_contract(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    """Load canonical branch/worktree facts from version execution markdown."""
    resolved_version = resolve_target_version(project_root, version)
    files = _markdown_files(project_root, resolved_version, feature)
    payload: dict[str, Any] = {
        "source": "execution_markdown",
        "version": resolved_version,
        "feature": feature,
        "material_paths": [str(path.relative_to(project_root)) for path in files],
        "loaded_material_types": [],
        "service_branch_map": {},
        "service_worktree_map": {},
    }
    for path in files:
        text = _read_text(path)
        if not text:
            continue
        name = path.name
        if name.startswith("branch-governance-"):
            payload["loaded_material_types"].append("branch-governance")
        elif name.startswith("git-workflow-"):
            payload["loaded_material_types"].append("git-workflow")
        elif name.startswith("deterministic-implementation-contract-"):
            payload["loaded_material_types"].append("deterministic-implementation-contract")
        bullets = _parse_bullets(text)
        local: dict[str, Any] = {}
        if bullets.get("expected_branch"):
            local["expected_branch"] = bullets["expected_branch"]
        if bullets.get("target_branch"):
            local["expected_branch"] = bullets["target_branch"]
        if bullets.get("branch_prefix"):
            local["branch_prefix"] = bullets["branch_prefix"]
        if bullets.get("base_branch"):
            local["base_branch"] = bullets["base_branch"]
        if bullets.get("require_clean_worktree_for_switch"):
            local["require_clean_worktree_for_switch"] = bullets["require_clean_worktree_for_switch"].lower() == "true"
        if bullets.get("worktree_root"):
            local["worktree_root"] = bullets["worktree_root"]
        services = _parse_section_list(text, "Direct Delivery Services") or _parse_section_list(text, "Writable Services")
        if services:
            local["direct_delivery_services"] = services
            local["service_directories"] = services
            local["git_roots"] = services
        branch_map, worktree_map = _parse_service_table(text)
        if branch_map:
            local["service_branch_map"] = branch_map
        if worktree_map:
            local["service_worktree_map"] = worktree_map
        _merge_non_empty(payload, local)
    payload["loaded_material_types"] = list(dict.fromkeys(payload["loaded_material_types"]))
    return payload
