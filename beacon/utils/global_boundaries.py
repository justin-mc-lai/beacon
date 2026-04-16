"""Helpers for Beacon global-boundaries inheritance and verification."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.context_files import write_context_file

GLOBAL_BOUNDARIES_RELATIVE_PATH = Path("docs/beacon/global-boundaries.md")
REQUIRED_GLOBAL_BOUNDARY_PRINCIPLES: tuple[dict[str, Any], ...] = (
    {
        "id": "explicit_assumptions",
        "heading": "显式假设与歧义管理",
        "markers": (
            "不清楚时不得静默选择一种解释直接执行",
            "多种解释并存时必须显式记录假设、取舍或阻断原因",
        ),
    },
    {
        "id": "simplicity_first",
        "heading": "简单优先",
        "markers": (
            "默认采用最小正确改动",
            "不为单次需求新增 speculative abstraction",
        ),
    },
    {
        "id": "surgical_changes",
        "heading": "外科手术式改动",
        "markers": (
            "不做 drive-by refactor",
            "只清理自己这次改动制造的 orphan",
        ),
    },
    {
        "id": "goal_driven_execution",
        "heading": "目标驱动验证闭环",
        "markers": (
            "非平凡任务必须绑定成功标准与验证信号",
            "feature 要有 acceptance/test 映射",
        ),
    },
    {
        "id": "trivial_task_exception",
        "heading": "trivial task 可以轻量处理，但不能越界",
        "markers": (
            "明显 typo",
            "不因为“简单”而扩大改动范围",
        ),
    },
)


def _module_root() -> Path:
    # .../beacon/beacon/utils/global_boundaries.py -> .../beacon
    return Path(__file__).resolve().parents[2]


def installed_global_boundaries_path() -> Path:
    return _module_root() / GLOBAL_BOUNDARIES_RELATIVE_PATH


def project_global_boundaries_path(project_root: Path | str) -> Path:
    return Path(project_root) / GLOBAL_BOUNDARIES_RELATIVE_PATH


def relative_global_boundaries_reference(path: Path, project_root: Path | str) -> str:
    root = Path(project_root).resolve()
    target = project_global_boundaries_path(root).resolve()
    try:
        return str(target.relative_to(root))
    except Exception:  # noqa: BLE001
        return str(target)


def load_installed_global_boundaries() -> str:
    path = installed_global_boundaries_path()
    try:
        return path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return ""


def load_project_global_boundaries(project_root: Path | str) -> str:
    path = project_global_boundaries_path(project_root)
    try:
        return path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return ""


def project_has_global_boundaries(project_root: Path | str) -> bool:
    return project_global_boundaries_path(project_root).exists()


def path_mentions_global_boundaries(path: Path, *, project_root: Path | str) -> bool:
    if not path.exists():
        return False
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return False
    relative_ref = relative_global_boundaries_reference(path, project_root)
    return "global-boundaries.md" in content or relative_ref in content


def inspect_global_boundary_principles(text: str) -> dict[str, Any]:
    normalized = str(text or "").strip()
    evidence: list[str] = []
    missing_ids: list[str] = []
    missing_headings: list[str] = []
    missing_markers: list[str] = []

    for principle in REQUIRED_GLOBAL_BOUNDARY_PRINCIPLES:
        heading = str(principle.get("heading", "") or "").strip()
        markers = tuple(str(item or "").strip() for item in principle.get("markers", ()) if str(item or "").strip())
        principle_id = str(principle.get("id", heading) or heading)
        has_heading = heading in normalized
        has_markers = all(marker in normalized for marker in markers)
        evidence.append(f"{principle_id}: heading={has_heading} markers={has_markers}")
        if not has_heading or not has_markers:
            missing_ids.append(principle_id)
            if not has_heading:
                missing_headings.append(heading)
            if not has_markers:
                missing_markers.extend([marker for marker in markers if marker not in normalized])

    return {
        "ok": not missing_ids,
        "missing_ids": missing_ids,
        "missing_headings": missing_headings,
        "missing_markers": missing_markers,
        "evidence": evidence,
    }


def global_boundary_principle_summaries() -> list[dict[str, str]]:
    return [
        {
            "id": str(item.get("id", "") or ""),
            "heading": str(item.get("heading", "") or ""),
        }
        for item in REQUIRED_GLOBAL_BOUNDARY_PRINCIPLES
    ]


def global_boundary_prompt_lines() -> list[str]:
    return [
        "Record explicit assumptions and ambiguity tradeoffs instead of silently picking one interpretation.",
        "Prefer the smallest correct change; avoid speculative abstraction or future-facing config unless required.",
        "Keep changes surgical; only touch files in the current scope and only clean up orphan artifacts you introduce.",
        "Bind work to verification signals; include acceptance/test mapping or concrete evidence for non-trivial tasks.",
        "For obvious typo or single-line copy fixes, stay lightweight but do not expand scope or touch unrelated files.",
    ]


def sync_project_global_boundaries(
    project_root: Path | str,
    *,
    dry_run: bool = False,
) -> dict[str, object]:
    root = Path(project_root)
    target = project_global_boundaries_path(root)
    installed_text = load_installed_global_boundaries()
    if not installed_text.strip():
        return {
            "path": str(target),
            "action": "missing_source",
            "changed": False,
            "backup_path": None,
        }
    write_result = write_context_file(target, installed_text.rstrip("\n") + "\n", dry_run=dry_run)
    return {
        "path": str(target),
        **write_result,
    }
