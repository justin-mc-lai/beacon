"""Version-aware artifact path helpers.

Project delivery version and Beacon runtime/toolkit version are distinct:

- delivery version controls where artifacts are written
- toolkit version controls whether newer artifact layout features are enabled
"""

from __future__ import annotations

from pathlib import Path

from beacon import __toolkit_version__
from beacon.utils.versioning import normalize_version


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def active_toolkit_version(runtime_version: str | None = None, *, fallback_version: str | None = None) -> str | None:
    return normalize_version(runtime_version or __toolkit_version__ or fallback_version)


def uses_machine_surface(version: str | None, *, runtime_version: str | None = None) -> bool:
    return _semver_tuple(active_toolkit_version(runtime_version, fallback_version=version)) >= (1, 1, 5)


def version_root(project_root: Path, version: str) -> Path:
    return project_root / "docs" / "beacon" / version


def human_execution_dir(project_root: Path, version: str) -> Path:
    return version_root(project_root, version) / "execution"


def human_execution_file(project_root: Path, version: str, filename: str) -> Path:
    return human_execution_dir(project_root, version) / filename


def change_docs_dir(project_root: Path, version: str) -> Path:
    return version_root(project_root, version) / "change"


def change_docs_file(project_root: Path, version: str, filename: str) -> Path:
    return change_docs_dir(project_root, version) / filename


def machine_root(project_root: Path, version: str) -> Path:
    return version_root(project_root, version) / ".machine"


def machine_change_dir(project_root: Path, version: str) -> Path:
    return machine_root(project_root, version) / "change"


def machine_change_file(project_root: Path, version: str, filename: str) -> Path:
    return machine_change_dir(project_root, version) / filename


def machine_execution_dir(project_root: Path, version: str) -> Path:
    return machine_root(project_root, version) / "execution"


def machine_execution_file(project_root: Path, version: str, filename: str) -> Path:
    return machine_execution_dir(project_root, version) / filename


def machine_trace_dir(project_root: Path, version: str, *segments: str) -> Path:
    root = machine_root(project_root, version) / "trace"
    for segment in segments:
        text = str(segment or "").strip().strip("/")
        if text:
            root = root / text
    return root


def machine_trace_file(project_root: Path, version: str, filename: str, *segments: str) -> Path:
    return machine_trace_dir(project_root, version, *segments) / filename


def qa_docs_dir(project_root: Path, version: str) -> Path:
    return version_root(project_root, version) / "qa" / "test-cases"


def qa_docs_file(project_root: Path, version: str, filename: str) -> Path:
    return qa_docs_dir(project_root, version) / filename


def machine_qa_dir(project_root: Path, version: str) -> Path:
    return machine_root(project_root, version) / "qa"


def machine_qa_file(project_root: Path, version: str, filename: str) -> Path:
    return machine_qa_dir(project_root, version) / filename


def execution_file_candidates(project_root: Path, version: str, filename: str) -> list[Path]:
    if not uses_machine_surface(version):
        return [human_execution_file(project_root, version, filename)]
    if filename.endswith(".json"):
        return [
            machine_execution_file(project_root, version, filename),
            human_execution_file(project_root, version, filename),
        ]
    return [human_execution_file(project_root, version, filename)]


def execution_file_output(project_root: Path, version: str, filename: str) -> Path:
    if uses_machine_surface(version) and filename.endswith(".json"):
        return machine_execution_file(project_root, version, filename)
    return human_execution_file(project_root, version, filename)


def change_file_output(project_root: Path, version: str, filename: str) -> Path:
    if uses_machine_surface(version) and filename.endswith(".json"):
        return machine_change_file(project_root, version, filename)
    return change_docs_file(project_root, version, filename)


def release_docs_dir(project_root: Path, version: str) -> Path:
    return version_root(project_root, version) / "release"


def release_note_file(project_root: Path, version: str) -> Path:
    return release_docs_dir(project_root, version) / f"{version}.md"


def release_checklist_file(project_root: Path, version: str) -> Path:
    return release_docs_dir(project_root, version) / f"checklist-{version}.md"


def qa_matrix_candidates(project_root: Path, version: str, feature_slug: str, kind: str) -> list[Path]:
    filename = f"{feature_slug}.{kind}.json"
    if not uses_machine_surface(version):
        return [qa_docs_file(project_root, version, filename)]
    return [
        machine_qa_file(project_root, version, filename),
        qa_docs_file(project_root, version, filename),
    ]


def qa_matrix_output(project_root: Path, version: str, feature_slug: str, kind: str) -> Path:
    filename = f"{feature_slug}.{kind}.json"
    if uses_machine_surface(version):
        return machine_qa_file(project_root, version, filename)
    return qa_docs_file(project_root, version, filename)
