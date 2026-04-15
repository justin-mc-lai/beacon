"""Helpers for Beacon global-boundaries inheritance and verification."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.context_files import write_context_file

GLOBAL_BOUNDARIES_RELATIVE_PATH = Path("docs/beacon/global-boundaries.md")


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

