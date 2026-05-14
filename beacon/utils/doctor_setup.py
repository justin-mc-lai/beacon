"""Helpers for beacon doctor launcher setup and uninstall flows."""

from __future__ import annotations

import os
import shlex
import stat
from pathlib import Path
from typing import TypedDict

DEFAULT_BIN_DIR = Path("~/.local/bin")
LAUNCHER_NAMES = ("beacon", "beacon-cli")
DOCTOR_MANAGED_MARKER = "# beacon-doctor-managed: true"
DOCTOR_SOURCE_MARKER = "# beacon-doctor-source: "
DOCTOR_NAME_MARKER = "# beacon-doctor-name: "
PREFERRED_BIN_DIRS = (
    Path("~/.local/bin"),
    Path("~/bin"),
    Path("/opt/homebrew/bin"),
    Path("/usr/local/bin"),
)
TRANSIENT_PATH_HINTS = (
    "/.codex/tmp/",
    "/.claude/tmp/",
    "/tmp/",
    "/var/folders/",
)


class LauncherActionResult(TypedDict):
    installed: list[str]
    removed: list[str]
    skipped: list[str]
    warnings: list[str]
    path_in_path: bool


def _is_writable_bin_dir(path: Path) -> bool:
    return path.exists() and path.is_dir() and os.access(path, os.W_OK | os.X_OK)


def _is_transient_path(path: Path) -> bool:
    normalized = str(path.resolve(strict=False))
    return any(marker in normalized for marker in TRANSIENT_PATH_HINTS)


def resolve_bin_dir(bin_dir: str | Path | None = None) -> Path:
    """Resolve launcher target bin directory.

    Priority:
    1) explicit --bin-dir
    2) BEACON_BIN_DIR
    3) first writable PATH entry
    4) ~/.local/bin fallback
    """
    if bin_dir not in (None, ""):
        return Path(bin_dir).expanduser()

    env_dir = os.environ.get("BEACON_BIN_DIR", "").strip()
    if env_dir:
        return Path(env_dir).expanduser()

    path_entries: list[Path] = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        path_entry = Path(entry).expanduser().resolve(strict=False)
        if path_entry not in path_entries:
            path_entries.append(path_entry)

    for preferred in PREFERRED_BIN_DIRS:
        preferred_path = preferred.expanduser().resolve(strict=False)
        if preferred_path in path_entries and _is_writable_bin_dir(preferred_path):
            return preferred_path

    for path_entry in path_entries:
        if _is_writable_bin_dir(path_entry) and not _is_transient_path(path_entry):
            return path_entry

    for path_entry in path_entries:
        if _is_writable_bin_dir(path_entry):
            return path_entry

    return DEFAULT_BIN_DIR.expanduser()


def launcher_targets(bin_dir: str | Path | None = None) -> tuple[Path, ...]:
    """Return expected launcher target paths for a bin directory."""
    target_dir = resolve_bin_dir(bin_dir)
    return tuple(target_dir / launcher_name for launcher_name in LAUNCHER_NAMES)


def path_in_path(bin_dir: str | Path | None = None) -> bool:
    """Check whether bin_dir is currently present in PATH."""
    target = resolve_bin_dir(bin_dir).resolve(strict=False)
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        if Path(entry).expanduser().resolve(strict=False) == target:
            return True
    return False


def is_doctor_managed_launcher(path: str | Path) -> bool:
    """Whether a launcher file is managed by doctor setup."""
    launcher_path = Path(path)
    if not launcher_path.exists() or not launcher_path.is_file():
        return False

    try:
        content = launcher_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return DOCTOR_MANAGED_MARKER in content


def _empty_result(target_dir: Path) -> LauncherActionResult:
    return {
        "installed": [],
        "removed": [],
        "skipped": [],
        "warnings": [],
        "path_in_path": path_in_path(target_dir),
    }


def _resolve_launcher_sources(launcher_source: str | Path) -> tuple[dict[str, Path], list[str]]:
    source = Path(launcher_source).expanduser()
    warnings: list[str] = []

    if source.is_file():
        return {name: source for name in LAUNCHER_NAMES}, warnings

    if source.is_dir():
        resolved: dict[str, Path] = {}
        for name in LAUNCHER_NAMES:
            candidate = source / name
            if candidate.is_file():
                resolved[name] = candidate

        if "beacon" not in resolved and "beacon-cli" in resolved:
            resolved["beacon"] = resolved["beacon-cli"]

        if "beacon-cli" not in resolved and "beacon" in resolved:
            resolved["beacon-cli"] = resolved["beacon"]
            warnings.append(
                f"launcher source missing beacon-cli, fallback to beacon: {resolved['beacon']}"
            )

        if not resolved:
            warnings.append(f"no launcher file found in source directory: {source}")

        return resolved, warnings

    warnings.append(f"launcher source does not exist: {source}")
    return {}, warnings


def _build_launcher_script(
    launcher_name: str,
    source_path: Path,
    *,
    beacon_cli_source: Path | None = None,
) -> str:
    source_exec = shlex.quote(str(source_path))
    if launcher_name == "beacon" and beacon_cli_source is not None:
        beacon_cli_exec = shlex.quote(str(beacon_cli_source))
        return (
            "#!/usr/bin/env bash\n"
            f"{DOCTOR_MANAGED_MARKER}\n"
            f"{DOCTOR_NAME_MARKER}{launcher_name}\n"
            f"{DOCTOR_SOURCE_MARKER}{source_path}\n"
            "set -euo pipefail\n"
            f"exec {beacon_cli_exec} \"$@\"\n"
        )
    return (
        "#!/usr/bin/env bash\n"
        f"{DOCTOR_MANAGED_MARKER}\n"
        f"{DOCTOR_NAME_MARKER}{launcher_name}\n"
        f"{DOCTOR_SOURCE_MARKER}{source_path}\n"
        "set -euo pipefail\n"
        f"exec {source_exec} \"$@\"\n"
    )


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def install_launchers(
    bin_dir: str | Path | None,
    launcher_source: str | Path,
    force: bool = False,
    dry_run: bool = False,
) -> LauncherActionResult:
    """Install doctor-managed `beacon` and `beacon-cli` launchers to bin_dir."""
    target_dir = resolve_bin_dir(bin_dir)
    result = _empty_result(target_dir)

    sources, source_warnings = _resolve_launcher_sources(launcher_source)
    result["warnings"].extend(source_warnings)

    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
    elif not target_dir.exists():
        result["warnings"].append(f"dry-run: would create bin directory: {target_dir}")

    for target in launcher_targets(target_dir):
        launcher_name = target.name
        source_path = sources.get(launcher_name)
        beacon_cli_source = sources.get("beacon-cli")
        target_str = str(target)

        if source_path is None:
            result["skipped"].append(target_str)
            result["warnings"].append(f"missing launcher source for {launcher_name}")
            continue

        if not os.access(source_path, os.X_OK):
            result["warnings"].append(f"launcher source is not executable: {source_path}")

        expected_content = _build_launcher_script(
            launcher_name,
            source_path,
            beacon_cli_source=beacon_cli_source,
        )

        if target.exists() and target.is_dir():
            result["skipped"].append(target_str)
            result["warnings"].append(f"target path is a directory, skip: {target}")
            continue

        if target.is_symlink():
            if dry_run:
                result["warnings"].append(f"dry-run: would replace symlink launcher with regular file: {target}")
            else:
                target.unlink(missing_ok=True)

        managed = is_doctor_managed_launcher(target)
        if target.exists() and not managed and not force:
            result["skipped"].append(target_str)
            result["warnings"].append(f"skip unmanaged launcher (use force to overwrite): {target}")
            continue

        if target.exists() and managed:
            try:
                current_content = target.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                current_content = ""
            if current_content == expected_content:
                result["skipped"].append(target_str)
                continue

        if target.exists() and not managed and force:
            result["warnings"].append(f"force overwrite unmanaged launcher: {target}")

        if dry_run:
            result["installed"].append(target_str)
            continue

        _write_executable(target, expected_content)
        result["installed"].append(target_str)

    return result


def uninstall_launchers(
    bin_dir: str | Path | None,
    force: bool = False,
    dry_run: bool = False,
) -> LauncherActionResult:
    """Remove launchers installed by doctor setup (or force remove existing launchers)."""
    target_dir = resolve_bin_dir(bin_dir)
    result = _empty_result(target_dir)

    for target in launcher_targets(target_dir):
        target_str = str(target)

        if not target.exists():
            result["skipped"].append(target_str)
            continue

        if target.is_dir():
            result["skipped"].append(target_str)
            result["warnings"].append(f"target path is a directory, skip: {target}")
            continue

        managed = is_doctor_managed_launcher(target)
        if not managed and not force:
            result["skipped"].append(target_str)
            result["warnings"].append(f"skip unmanaged launcher (use force to remove): {target}")
            continue

        if not managed and force:
            result["warnings"].append(f"force remove unmanaged launcher: {target}")

        if dry_run:
            result["removed"].append(target_str)
            continue

        target.unlink(missing_ok=True)
        result["removed"].append(target_str)

    return result
