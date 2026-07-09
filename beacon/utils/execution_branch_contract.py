"""Execution material branch/worktree contract extraction."""

from __future__ import annotations

import json
import re
import subprocess
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


def _normalized_path(value: Any, *, project_root: Path) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    path = Path(text).expanduser()
    if not path.is_absolute():
        path = (project_root / path).resolve()
    else:
        path = path.resolve()
    return str(path)


def _parse_git_workflow_markdown(path: Path, project_root: Path) -> dict[str, Any]:
    text = _read_text(path)
    if not text:
        return {}
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
    if bullets.get("branch_resolution_mode"):
        local["branch_resolution_mode"] = bullets["branch_resolution_mode"]
    if bullets.get("dedicated_worktree_path"):
        local["dedicated_worktree_path"] = _normalized_path(bullets["dedicated_worktree_path"], project_root=project_root)
    if bullets.get("worktree_root"):
        local["worktree_root"] = _normalized_path(bullets["worktree_root"], project_root=project_root)
    if bullets.get("require_clean_worktree_for_switch"):
        local["require_clean_worktree_for_switch"] = bullets["require_clean_worktree_for_switch"].lower() == "true"
    if bullets.get("use_git_worktree"):
        local["use_git_worktree"] = bullets["use_git_worktree"].lower() == "true"
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
    return local


def is_program_level_branch_contract(contract: dict[str, Any] | None) -> bool:
    if not isinstance(contract, dict):
        return False
    mode = str(contract.get("branch_resolution_mode") or "").strip().lower()
    if mode == "program-level":
        return True
    return bool(
        (contract.get("dedicated_worktree_path") or contract.get("worktree_root") or contract.get("worktree_path"))
        and (
            contract.get("expected_branch")
            or contract.get("aggregation_branch")
            or contract.get("program_aggregation_branch")
        )
    )


def _program_level_from_parsed_markdown(
    project_root: Path,
    *,
    path: Path,
    local: dict[str, Any],
    resolved_version: str,
) -> dict[str, Any]:
    try:
        material_path = str(path.relative_to(project_root))
    except ValueError:
        material_path = str(path)
    return {
        **local,
        "source": "execution_markdown",
        "version": resolved_version,
        "program_slug": path.stem.replace("git-workflow-", ""),
        "material_path": material_path,
    }


def infer_program_level_from_governance(
    project_root: Path,
    *,
    version: str,
    admission_contract: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Infer program-level branch/worktree from project-version-governance when git-workflow is off-main."""
    from beacon.utils.project_governance import governance_md_path, load_governance_payload

    resolved_version = resolve_target_version(project_root, version)
    contract = admission_contract if isinstance(admission_contract, dict) else {}
    root = project_root.expanduser().resolve()
    payload = load_governance_payload(root)
    version_meta = payload.get("version_scoped_metadata") if isinstance(payload.get("version_scoped_metadata"), dict) else {}
    version_contract = version_meta.get(resolved_version) if isinstance(version_meta.get(resolved_version), dict) else {}
    pattern = str(
        contract.get("aggregation_branch")
        or contract.get("program_aggregation_branch")
        or contract.get("expected_branch")
        or version_contract.get("aggregation_branch")
        or version_contract.get("program_aggregation_branch")
        or version_contract.get("expected_branch")
        or contract.get("feature_branch_pattern")
        or version_contract.get("next_version_feature_branch")
        or ""
    ).strip()
    worktree_path = str(
        contract.get("dedicated_worktree_path")
        or contract.get("worktree_path")
        or contract.get("worktree_root")
        or contract.get("worktree_base")
        or version_contract.get("dedicated_worktree_path")
        or version_contract.get("worktree_root")
        or version_contract.get("worktree_path")
        or ""
    ).strip()
    mode = str(
        contract.get("branch_resolution_mode")
        or version_contract.get("branch_resolution_mode")
        or ""
    ).strip().lower()
    per_service = (
        version_contract.get("per_service_canonical_branch")
        if isinstance(version_contract.get("per_service_canonical_branch"), dict)
        else {}
    )
    expected_branch = pattern
    if not expected_branch and per_service:
        expected_branch = str(next(iter(per_service.values()), "")).strip()
    if not expected_branch or not worktree_path:
        return None
    if mode != "program-level" and "<feature" in expected_branch.lower():
        return None
    gov_path = governance_md_path(root)
    payload_out = {
        "branch_resolution_mode": "program-level",
        "expected_branch": expected_branch,
        "dedicated_worktree_path": _normalized_path(worktree_path, project_root=root),
        "source": "project_governance",
        "version": resolved_version,
        "program_slug": str(version_contract.get("program_slug") or contract.get("program_slug") or "").strip(),
        "material_path": str(gov_path.relative_to(root)) if gov_path.is_file() else "",
    }
    return payload_out if is_program_level_branch_contract(payload_out) else None


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _parse_frontmatter(path: Path) -> dict[str, str]:
    text = _read_text(path)
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    out: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        out[_normalize_key(key)] = _clean_cell(value.strip().strip('"').strip("'"))
    return out


def _lake_slug_set(payload: dict[str, Any]) -> set[str]:
    lakes = payload.get("lakes")
    if not isinstance(lakes, list):
        return set()
    slugs: set[str] = set()
    for lake in lakes:
        if not isinstance(lake, dict):
            continue
        for key in ("feature_slug", "slug"):
            slug = feature_slug(str(lake.get(key) or "").strip())
            if slug:
                slugs.add(slug)
    return slugs


def _current_branch(path: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:  # noqa: BLE001
        return ""
    return str(result.stdout or "").strip() if result.returncode == 0 else ""


def _program_worktree_path(project_root: Path, *, version: str, preferred_root: Path | None = None) -> str:
    expected_branch = f"beacon/{version}"
    if preferred_root and preferred_root.exists() and _current_branch(preferred_root) == expected_branch:
        return str(preferred_root.resolve())
    root = project_root.expanduser().resolve()
    if _current_branch(root) == expected_branch:
        return str(root)
    return str(root / ".beacon" / "worktrees" / version)


def infer_program_level_from_program_topology(
    project_root: Path,
    *,
    version: str,
    feature: str,
    admission_contract: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Infer aggregation branch from frozen program/lake topology surfaces."""

    resolved_version = resolve_target_version(project_root, version)
    root = project_root.expanduser().resolve()
    contract = admission_contract if isinstance(admission_contract, dict) else {}
    requested_root_raw = str(contract.get("requested_project_root") or "").strip()
    requested_root = Path(requested_root_raw).expanduser().resolve() if requested_root_raw else root
    slug = feature_slug(feature)
    search_roots = list(dict.fromkeys([root, requested_root]))
    if not any((candidate / "docs" / "beacon" / resolved_version / "programs").is_dir() for candidate in search_roots):
        return None
    expected_branch = str(
        contract.get("aggregation_branch")
        or contract.get("program_aggregation_branch")
        or contract.get("expected_branch")
        or ""
    ).strip() or f"beacon/{resolved_version}"
    mode = str(contract.get("branch_resolution_mode") or "").strip().lower()
    worktree_path = str(
        contract.get("dedicated_worktree_path")
        or contract.get("worktree_path")
        or contract.get("worktree_root")
        or (contract.get("worktree_base") if mode == "program-level" else "")
        or ""
    ).strip()
    if worktree_path and Path(worktree_path).name == slug:
        worktree_path = str(Path(worktree_path).parent)
    if not worktree_path:
        worktree_path = _program_worktree_path(root, version=resolved_version, preferred_root=requested_root)

    for search_root in search_roots:
        programs_root = search_root / "docs" / "beacon" / resolved_version / "programs"
        if not programs_root.is_dir():
            continue
        for program_dir in sorted(path for path in programs_root.iterdir() if path.is_dir()):
            program_slug = program_dir.name
            manifest = _parse_frontmatter(program_dir / "program-manifest.md")
            graph = _read_json(program_dir / "feature-graph.json")
            freeze = _read_json(program_dir / "program-truth-freeze.json")
            lakes = _lake_slug_set(graph) | _lake_slug_set(freeze)
            program_slug_matches = slug == feature_slug(program_slug)
            if not lakes and not program_slug_matches:
                continue
            if slug not in lakes and not program_slug_matches:
                continue
            frozen = (
                str(freeze.get("status") or "").strip().lower() == "frozen"
                or str(manifest.get("program_plan_frozen") or "").strip().lower() == "true"
                or str(graph.get("program_plan_frozen") or "").strip().lower() == "true"
            )
            if not frozen:
                continue
            material_path = program_dir / "program-truth-freeze.json"
            if not material_path.exists():
                material_path = program_dir / "feature-graph.json"
            try:
                material_rel = str(material_path.relative_to(root))
            except ValueError:
                material_rel = str(material_path)
            return {
                "branch_resolution_mode": "program-level",
                "expected_branch": expected_branch,
                "dedicated_worktree_path": _normalized_path(worktree_path, project_root=root),
                "source": "program_topology",
                "version": resolved_version,
                "program_slug": program_slug,
                "material_path": material_rel,
                "lake_slug": "" if program_slug_matches else slug,
            }
    return None


def find_program_level_git_workflow(project_root: Path, *, version: str) -> dict[str, Any] | None:
    """Return the first program-level git-workflow contract for a version, if any."""
    resolved_version = resolve_target_version(project_root, version)
    root = project_root.expanduser().resolve()
    search_roots: list[Path] = [root]
    inferred = infer_program_level_from_governance(root, version=resolved_version)
    if inferred:
        dedicated = str(inferred.get("dedicated_worktree_path") or "").strip()
        if dedicated:
            dedicated_path = Path(dedicated)
            if dedicated_path not in search_roots:
                search_roots.append(dedicated_path)
    for search_root in search_roots:
        execution_dir = search_root / "docs" / "beacon" / resolved_version / "execution"
        if not execution_dir.is_dir():
            continue
        for path in sorted(execution_dir.glob("git-workflow-*.md")):
            local = _parse_git_workflow_markdown(path, root)
            if not is_program_level_branch_contract(local):
                continue
            return _program_level_from_parsed_markdown(
                root,
                path=path,
                local=local,
                resolved_version=resolved_version,
            )
    return inferred


def resolve_workspace_branch_targets(
    project_root: Path,
    *,
    version: str,
    feature: str,
    admission_contract: dict[str, Any],
) -> dict[str, Any]:
    """Resolve governed branch/worktree for workspace admit (R5 program-level aware)."""
    from beacon.utils.workspace_admission import resolve_feature_branch, resolve_worktree_path

    root = project_root.expanduser().resolve()
    program = find_program_level_git_workflow(root, version=version)
    per_feature = load_execution_branch_contract(root, version=version, feature=feature)
    ctx: dict[str, Any] | None = program
    if not ctx:
        ctx = infer_program_level_from_governance(
            root,
            version=version,
            admission_contract={**admission_contract, "version": version},
        )
    if not ctx:
        ctx = infer_program_level_from_program_topology(
            root,
            version=version,
            feature=feature,
            admission_contract={**admission_contract, "version": version},
        )
    if not ctx and is_program_level_branch_contract(per_feature):
        ctx = per_feature
    if ctx and is_program_level_branch_contract(ctx):
        branch = str(
            ctx.get("expected_branch")
            or ctx.get("aggregation_branch")
            or ctx.get("program_aggregation_branch")
            or ""
        ).strip()
        if not branch:
            branch = resolve_feature_branch(admission_contract, feature=feature, version=version)
        worktree_path = str(ctx.get("dedicated_worktree_path") or ctx.get("worktree_root") or ctx.get("worktree_path") or "").strip()
        if not worktree_path:
            worktree_path = resolve_worktree_path(root, admission_contract, feature=feature)
        return {
            "branch_resolution_mode": "program-level",
            "feature_branch": branch,
            "worktree_path": worktree_path,
            "program_slug": str(ctx.get("program_slug") or ctx.get("feature") or "").strip(),
            "material_path": str(ctx.get("material_path") or (per_feature.get("material_paths") or [""])[0]).strip(),
            "source": str(ctx.get("source") or "").strip(),
        }
    return {
        "branch_resolution_mode": "per-feature",
        "feature_branch": resolve_feature_branch(admission_contract, feature=feature, version=version),
        "worktree_path": resolve_worktree_path(root, admission_contract, feature=feature),
        "program_slug": "",
        "material_path": str((per_feature.get("material_paths") or [""])[0]).strip(),
    }


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
        if name.startswith("git-workflow-"):
            local = _parse_git_workflow_markdown(path, project_root)
        else:
            bullets = _parse_bullets(text)
            local = {}
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
