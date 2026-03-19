"""Doctor v2 diagnostics helpers."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from beacon.utils.context_files import inspect_context_file
from beacon.utils.runtime import now_iso
from beacon.utils.versioning import discover_versions, normalize_version, release_line_key
from beacon.utils.workflow_memory import compute_workflow_progress

_SKILL_VERSION_PATTERNS = (
    re.compile(r"Skill Version\*\*:\s*v?(\d+\.\d+\.\d+)", re.IGNORECASE),
    re.compile(r"CLI Version\*\*:\s*v?(\d+\.\d+\.\d+)", re.IGNORECASE),
    re.compile(r"^\s*version\s*:\s*v?(\d+\.\d+\.\d+)\s*$", re.IGNORECASE | re.MULTILINE),
)
_PYPROJECT_VERSION_RE = re.compile(r'^\s*version\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
_INIT_VERSION_RE = re.compile(r'^__version__\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
_INIT_TOOLKIT_VERSION_RE = re.compile(r'^__toolkit_version__\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
_LEGACY_TRIGGER_RE = re.compile(r"/beacon:[a-z0-9-]+", re.IGNORECASE)
_SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
_SEMVER_SEARCH_RE = re.compile(r"v?\d+\.\d+\.\d+")

_CONTEXT_FILES = ("AGENTS.md", "CLAUDE.md")


def _semver_key(version: str) -> tuple[int, int, int]:
    match = _SEMVER_RE.match(str(version or "").strip())
    if not match:
        return (0, 0, 0)
    major, minor, patch = match.groups()
    return (int(major), int(minor), int(patch))


def _is_semver(version: str | None) -> bool:
    return bool(_SEMVER_RE.match(str(version or "").strip()))


def _normalize(version: str | None) -> str:
    raw = str(version or "").strip()
    if not raw:
        return ""
    normalized = normalize_version(raw)
    return str(normalized or raw).strip()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return ""


def _module_root() -> Path:
    # .../beacon/beacon/utils/doctor_diagnostics.py -> .../beacon
    return Path(__file__).resolve().parents[2]


def _iter_semver_tokens(text: str) -> list[str]:
    versions: list[str] = []
    for token in _SEMVER_SEARCH_RE.findall(str(text or "")):
        normalized = _normalize(token)
        if normalized and _SEMVER_RE.match(normalized):
            versions.append(normalized)
    return versions


def _read_skill_version(skill_md: Path) -> str:
    text = _read_text(skill_md)
    if not text:
        return ""
    for pattern in _SKILL_VERSION_PATTERNS:
        match = pattern.search(text)
        if match:
            return _normalize(match.group(1))
    fallback = _iter_semver_tokens(text)
    if fallback:
        return fallback[0]
    return ""


def _read_pyproject_version(pyproject: Path) -> str:
    text = _read_text(pyproject)
    if not text:
        return ""
    match = _PYPROJECT_VERSION_RE.search(text)
    if match:
        return _normalize(match.group(1))
    return ""


def _read_init_versions(init_file: Path) -> tuple[str, str]:
    text = _read_text(init_file)
    if not text:
        return ("", "")
    version_match = _INIT_VERSION_RE.search(text)
    toolkit_match = _INIT_TOOLKIT_VERSION_RE.search(text)
    package_version = _normalize(version_match.group(1)) if version_match else ""
    toolkit_version = _normalize(toolkit_match.group(1)) if toolkit_match else ""
    return (package_version, toolkit_version)


def collect_runtime_info() -> dict[str, Any]:
    root = _module_root()
    skill_md = root / "SKILL.md"
    pyproject = root / "pyproject.toml"
    package_init = root / "beacon" / "__init__.py"

    init_package_version, init_toolkit_version = _read_init_versions(package_init)
    pyproject_version = _read_pyproject_version(pyproject)
    package_version = init_package_version or pyproject_version
    toolkit_version = init_toolkit_version or package_version
    skill_md_version = _read_skill_version(skill_md)

    candidate_versions = [v for v in [package_version, toolkit_version, pyproject_version, skill_md_version] if v]
    unique_versions = sorted(set(candidate_versions), key=_semver_key)
    version_consistent = len(unique_versions) <= 1

    if shutil.which("beacon"):
        cli_entry = "beacon"
    elif shutil.which("beacon-cli"):
        cli_entry = "beacon-cli"
    else:
        cli_entry = "python -m beacon.main"

    return {
        "active_skill_path": str(root),
        "skill_md_path": str(skill_md),
        "cli_entry": cli_entry,
        "package": package_version,
        "toolkit": toolkit_version,
        "skill_md": skill_md_version,
        "package_version": package_version,
        "toolkit_version": toolkit_version,
        "pyproject_version": pyproject_version,
        "skill_md_version": skill_md_version,
        "version_consistent": version_consistent,
        "version_candidates": unique_versions,
        "launcher_path": str(root / "beacon-cli"),
    }


def _collect_semvers_from_payload(payload: Any) -> set[str]:
    found: set[str] = set()
    stack = [payload]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            stack.extend(current.values())
            continue
        if isinstance(current, list):
            stack.extend(current)
            continue
        if isinstance(current, str):
            for token in _iter_semver_tokens(current):
                found.add(token)
    return found


def _read_ptk_versions(project_root: Path) -> list[str]:
    history_file = project_root / ".ptk" / "state" / "version-history.json"
    if not history_file.exists():
        return []
    try:
        payload = json.loads(history_file.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []
    versions = _collect_semvers_from_payload(payload)
    return sorted(versions, key=_semver_key)


def detect_iteration_versions(project_root: Path) -> dict[str, Any]:
    docs_versions = discover_versions(project_root)
    ptk_versions = _read_ptk_versions(project_root)

    available = sorted(set(docs_versions + ptk_versions), key=_semver_key)
    if docs_versions:
        latest = docs_versions[-1]
        source = "docs_scan"
    elif ptk_versions:
        latest = ptk_versions[-1]
        source = "ptk_history_fallback"
    else:
        latest = "v1.0.0"
        source = "default_fallback"

    return {
        "available_versions": available,
        "latest_iteration_version": latest,
        "version_source": source,
    }


def _docs_dir_for_version(project_root: Path, version: str) -> Path:
    beacon_dir = project_root / "docs" / "beacon" / version
    if beacon_dir.exists() and any(beacon_dir.rglob("*.md")):
        return beacon_dir
    if beacon_dir.exists():
        return beacon_dir
    return beacon_dir


def compute_artifact_stage_view(project_root: Path, version: str) -> dict[str, str]:
    docs_dir = _docs_dir_for_version(project_root, version)
    state_dir = project_root / ".beacon" / "state"

    def _has_markdown(path: Path) -> bool:
        return path.exists() and any(path.glob("*.md"))

    think_candidates = [
        state_dir / "think-progress" / f"{version}.json",
        state_dir / "think-progress.json",
    ]
    think_done = any(path.exists() for path in think_candidates)
    verify_file = project_root / ".beacon" / "auto-test-status.json"
    gate_file = project_root / ".beacon" / "gate-report.json"

    view: dict[str, str] = {
        "think": "completed" if think_done else "not_started",
        "user-story": "completed" if _has_markdown(docs_dir / "user-story") else "not_started",
        "prd": "completed" if _has_markdown(docs_dir / "prd") else "not_started",
        "test-case": "completed" if _has_markdown(docs_dir / "qa" / "test-cases") else "not_started",
        "implementation": "completed" if any(state_dir.glob("implementation-*.json")) else "not_started",
        "verify": "completed" if verify_file.exists() else "not_started",
        "gate": "completed" if gate_file.exists() else "not_started",
    }

    if verify_file.exists():
        try:
            verify_payload = json.loads(verify_file.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            verify_payload = {}
        verify_status = str(verify_payload.get("status", "")).lower()
        if verify_status and verify_status != "passed":
            view["verify"] = "failed"

    if gate_file.exists():
        try:
            gate_payload = json.loads(gate_file.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            gate_payload = {}
        gate_status = str(gate_payload.get("status", "")).lower()
        if gate_status and gate_status not in {"pass", "passed"}:
            view["gate"] = "failed"

    return view


def _scan_legacy_skill_syntax(project_root: Path, version: str) -> list[str]:
    evidence: list[str] = []
    doc_roots = [
        project_root / "docs" / "beacon" / version,
    ]
    for root in doc_roots:
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            text = _read_text(path)
            if not text:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                if _LEGACY_TRIGGER_RE.search(line):
                    evidence.append(f"{path}:{line_no}")
                    if len(evidence) >= 10:
                        return evidence
    return evidence


def _version_root_semantics_drift(project_root: Path) -> list[str]:
    docs_root = project_root / "docs" / "beacon"
    if not docs_root.exists():
        return []
    by_release_line: dict[str, list[str]] = {}
    invalid: list[str] = []
    for child in docs_root.iterdir():
        if not child.is_dir():
            continue
        key = release_line_key(child.name)
        if not key:
            invalid.append(f"{child}: invalid formal version root")
            continue
        by_release_line.setdefault(key, []).append(child.name)
    drift: list[str] = []
    for release_line, names in sorted(by_release_line.items()):
        unique = sorted(set(names))
        if len(unique) > 1:
            drift.append(f"{docs_root}: release_line={release_line} has multiple roots {unique}")
    return sorted(set(invalid + drift))


def _stale_ptk_references(project_root: Path) -> list[str]:
    history_file = project_root / ".ptk" / "state" / "version-history.json"
    if not history_file.exists():
        return []
    try:
        payload = json.loads(history_file.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []

    docs_versions = set(discover_versions(project_root))
    stale: list[str] = []
    versions = payload.get("versions", [])
    if not isinstance(versions, list):
        versions = []
    for item in versions:
        if not isinstance(item, dict):
            continue
        version = _normalize(str(item.get("version", ""))) or "unknown"
        coverage_file = str(item.get("coverage_file", "")).strip()
        if docs_versions and version != "unknown" and version not in docs_versions:
            stale.append(f"{history_file}: version={version} not found in docs/ semver set")
        if not coverage_file:
            stale.append(f"{history_file}: version={version} missing coverage_file")
            continue
        target = Path(coverage_file)
        if not target.is_absolute():
            target = project_root / target
        if not target.exists():
            stale.append(f"{history_file}: version={version} -> missing {coverage_file}")
    return sorted(set(stale))


def _collect_install_copy_versions(runtime_skill_version: str) -> dict[str, Any]:
    install_paths = {
        "agents": Path.home() / ".agents" / "skills" / "beacon" / "SKILL.md",
        "codex": Path.home() / ".codex" / "skills" / "beacon" / "SKILL.md",
        "claude": Path.home() / ".claude" / "skills" / "beacon" / "SKILL.md",
    }
    versions: dict[str, str] = {}
    evidence: list[str] = []
    for channel, path in install_paths.items():
        if path.exists():
            versions[channel] = _read_skill_version(path)
            evidence.append(f"{channel}:{versions[channel] or 'unknown'} ({path})")
        else:
            versions[channel] = ""
            evidence.append(f"{channel}:missing ({path})")

    resolved_runtime = _normalize(runtime_skill_version)
    existing_versions = {v for v in versions.values() if v}
    mismatched_with_runtime = any(v != resolved_runtime for v in existing_versions) if resolved_runtime else False
    drift_detected = len(existing_versions) > 1 or mismatched_with_runtime

    return {
        "versions": versions,
        "evidence": evidence,
        "drift_detected": drift_detected,
    }


def _context_file_map(project_root: Path) -> dict[str, Path]:
    return {name: project_root / name for name in _CONTEXT_FILES}


def _collect_context_file_presence(
    context_files: dict[str, Path],
    inspections: dict[str, dict[str, Any]],
) -> tuple[bool, list[str]]:
    missing = [str(context_files[name]) for name, info in inspections.items() if not bool(info.get("exists"))]
    present = [str(context_files[name]) for name, info in inspections.items() if bool(info.get("exists"))]
    evidence = [f"missing={missing}", f"present={present}"]
    return (not missing, evidence)


def _collect_managed_block_integrity(
    context_files: dict[str, Path],
    inspections: dict[str, dict[str, Any]],
) -> tuple[bool, list[str]]:
    evidence: list[str] = []
    broken = []
    for name, info in inspections.items():
        if not bool(info.get("exists")):
            continue
        marker_integrity = str(info.get("marker_integrity", "missing"))
        evidence.append(f"{name}: integrity={marker_integrity} ({context_files[name]})")
        if marker_integrity != "ok":
            broken.append(name)
    return (not broken, evidence)


def _collect_managed_block_version_drift(
    inspections: dict[str, dict[str, Any]],
) -> tuple[bool, list[str]]:
    versions: dict[str, str] = {}
    drifted: list[str] = []
    unknown: list[str] = []
    evidence: list[str] = []

    for name, info in inspections.items():
        if not bool(info.get("exists")):
            continue
        managed_version = str(info.get("managed_version") or "")
        versions[name] = managed_version
        version_drift = info.get("version_drift")
        evidence.append(
            f"{name}: managed_version={managed_version or 'missing'}, version_drift={version_drift}"
        )
        if version_drift is True:
            drifted.append(name)
        elif version_drift is None:
            unknown.append(name)

    version_set = {v for v in versions.values() if v}
    version_consistent = len(version_set) <= 1
    drift = bool(drifted or unknown) or not version_consistent
    evidence.append(f"version_set={sorted(version_set)}")

    return (not drift, evidence)


def collect_compatibility_checks(
    *,
    project_root: Path,
    runtime: dict[str, Any],
    version: str,
    artifact_stage_view: dict[str, str],
    memory_view: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    run_id = str(memory_view.get("run_id", "") or "")
    doc_stages = ["think", "user-story", "prd", "test-case"]
    completed_doc_stages = [stage for stage in doc_stages if artifact_stage_view.get(stage) == "completed"]
    docs_have_progress = bool(completed_doc_stages)

    missing = memory_view.get("missing_closure_stages", [])
    if not isinstance(missing, list):
        missing = []
    missing_stage_set = {str(stage) for stage in missing}
    divergent = sorted(
        [
            stage
            for stage, artifact_status in artifact_stage_view.items()
            if artifact_status == "completed" and stage in missing_stage_set
        ]
    )

    stale_refs = _stale_ptk_references(project_root)
    legacy_refs = _scan_legacy_skill_syntax(project_root, version)
    version_root_drift = _version_root_semantics_drift(project_root)
    runtime_skill_version = _normalize(
        str(runtime.get("toolkit_version") or runtime.get("package_version") or "")
    )
    context_files = _context_file_map(project_root)
    context_inspections = {
        name: inspect_context_file(path, runtime_skill_version)
        for name, path in context_files.items()
    }
    context_presence_ok, context_presence_evidence = _collect_context_file_presence(
        context_files,
        context_inspections,
    )
    managed_integrity_ok, managed_integrity_evidence = _collect_managed_block_integrity(
        context_files,
        context_inspections,
    )
    managed_versions_ok, managed_versions_evidence = _collect_managed_block_version_drift(
        context_inspections,
    )
    install_copy_versions = _collect_install_copy_versions(runtime_skill_version)
    material_version = _normalize(version)
    material_ahead_of_runtime = False
    if _is_semver(runtime_skill_version) and _is_semver(material_version):
        material_ahead_of_runtime = _semver_key(material_version) > _semver_key(runtime_skill_version)

    checks: dict[str, dict[str, Any]] = {
        "context_files_presence": {
            "status": "PASS" if context_presence_ok else "FAIL",
            # High because missing context control files disables policy/runtime guidance propagation.
            "severity": "high",
            "summary": "Project root should include required context files (AGENTS.md, CLAUDE.md).",
            "evidence": context_presence_evidence,
            "impact": "Missing context files can break policy inheritance and runtime instruction consistency.",
            "repair": [
                "Create missing context files at project root: AGENTS.md and CLAUDE.md.",
                "Bootstrap managed content with `beacon doctor setup-context --project-root .`.",
            ],
        },
        "managed_block_integrity": {
            "status": "PASS" if managed_integrity_ok else "FAIL",
            "severity": "high",
            "summary": "Managed marker blocks in context files should be well-formed and balanced.",
            "evidence": managed_integrity_evidence,
            "impact": "Malformed markers can break automated upgrades and runtime overlay injection.",
            "repair": [
                "Fix unmatched/misordered managed markers in AGENTS.md and CLAUDE.md.",
                "Run `beacon doctor setup-context --project-root . --force` to repair managed blocks.",
            ],
        },
        "managed_block_version_drift": {
            "status": "PASS" if managed_versions_ok else "WARN",
            "severity": "medium",
            "summary": "Context managed block version markers should align across files and runtime.",
            "evidence": managed_versions_evidence,
            "impact": "Version marker drift causes ambiguous operator guidance and compatibility assumptions.",
            "repair": [
                "Normalize AGENTS.md and CLAUDE.md managed block versions to one semver.",
                "Prefer the active runtime version when updating managed block version markers.",
            ],
        },
        "runless_docs_only": {
            "status": "FAIL" if docs_have_progress and not run_id else "PASS",
            "severity": "high",
            "summary": "Docs artifacts should be backed by workflow lifecycle run data.",
            "evidence": [
                f"version={version}",
                f"artifact_stages={completed_doc_stages}",
                f"memory_run_id={run_id or 'N/A'}",
            ],
            "impact": "Progress appears in docs but cannot be audited end-to-end.",
            "repair": [
                "Run `beacon workflow start \"<feature>\" --version <version>`.",
                "Continue workflow until `.beacon/runs/<run_id>/state.json` and lifecycle events exist.",
            ],
        },
        "status_memory_divergence": {
            "status": "FAIL" if divergent else "PASS",
            "severity": "high",
            "summary": "Docs/status stages should align with workflow memory closure stages.",
            "evidence": [
                f"run_id={run_id or 'N/A'}",
                f"divergent_stages={divergent}",
                f"missing_closure_stages={sorted(missing_stage_set)}",
            ],
            "impact": "Release readiness can be misreported when status and memory diverge.",
            "repair": [
                "Use workflow lifecycle events as source of truth for closure status.",
                "Backfill missing stage events for already completed artifacts when valid.",
            ],
        },
        "stale_ptk_version_refs": {
            "status": "WARN" if stale_refs else "PASS",
            "severity": "medium",
            "summary": "PTK version-history references should point to existing and relevant artifacts.",
            "evidence": stale_refs[:10],
            "impact": "Stale references can break version traceability and doctor accuracy.",
            "repair": [
                "Clean stale entries in `.ptk/state/version-history.json`.",
                "Regenerate coverage artifacts for retained version entries.",
            ],
        },
        "version_root_semantics": {
            "status": "FAIL" if version_root_drift else "PASS",
            "severity": "high",
            "summary": "Formal Beacon version roots should map one release line to one canonical directory.",
            "evidence": version_root_drift[:10],
            "impact": "Multiple roots per release line blur release-package semantics and break source-of-truth discovery.",
            "repair": [
                "Collapse each release line to a single canonical docs/beacon/<version>/ root.",
                "Remove version roots that encode themes/suffixes instead of formal semver versions.",
            ],
        },
        "material_skill_semver_compatibility": {
            "status": "FAIL" if material_ahead_of_runtime else "PASS",
            "severity": "high",
            "summary": "Latest project iteration version should not be ahead of active beacon skill version.",
            "evidence": [
                f"latest_iteration_version={material_version or version}",
                f"runtime_skill_version={runtime_skill_version or 'N/A'}",
            ],
            "impact": "Material authored for newer iterations can require unsupported doctor/workflow behavior.",
            "repair": [
                "Upgrade beacon skill/cli to a version >= latest iteration version.",
                "Or downgrade/normalize project material version to match supported runtime.",
            ],
        },
        "legacy_skill_trigger_syntax": {
            "status": "WARN" if legacy_refs else "PASS",
            "severity": "medium",
            "summary": "Legacy `/beacon:xxx` trigger syntax should be migrated to beacon CLI forms.",
            "evidence": legacy_refs[:10],
            "impact": "Legacy trigger syntax may not work in modern runtime environments.",
            "repair": [
                "Replace `/beacon:workflow` style commands with `beacon workflow`.",
                "Add a migration note in docs for supported trigger syntax.",
            ],
        },
        "runtime_version_consistency": {
            "status": "WARN" if not bool(runtime.get("version_consistent")) else "PASS",
            "severity": "medium",
            "summary": "Runtime version sources should stay aligned across package/toolkit/skill files.",
            "evidence": [
                f"package={runtime.get('package') or runtime.get('package_version')}",
                f"toolkit={runtime.get('toolkit') or runtime.get('toolkit_version')}",
                f"pyproject={runtime.get('pyproject_version')}",
                f"skill_md={runtime.get('skill_md') or runtime.get('skill_md_version')}",
            ],
            "impact": "Version drift can cause wrong diagnostics and operator confusion.",
            "repair": [
                "Align `beacon/__init__.py` version constants with `pyproject.toml`.",
                "Update `SKILL.md` version declaration to the active runtime version.",
            ],
        },
        "installed_skill_copy_drift": {
            "status": "WARN" if install_copy_versions.get("drift_detected") else "PASS",
            "severity": "medium",
            "summary": "Installed beacon skill copies (agents/codex/claude) should stay on one runtime version.",
            "evidence": install_copy_versions.get("evidence", []),
            "impact": "Version drift across local skill copies can cause trigger mismatch and inconsistent behavior.",
            "repair": [
                "Sync ~/.agents/skills/beacon, ~/.codex/skills/beacon, ~/.claude/skills/beacon to the same version.",
                "Reinstall/update launchers with `beacon doctor setup` if CLI entry mismatch persists.",
            ],
        },
    }
    return checks


def _compatibility_checks_to_incompatibilities(
    compatibility_checks: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    check_code_map = {
        "runtime_version_consistency": "COMP-101",
        "runless_docs_only": "COMP-201",
        "status_memory_divergence": "COMP-202",
        "stale_ptk_version_refs": "COMP-203",
        "material_skill_semver_compatibility": "COMP-204",
        "legacy_skill_trigger_syntax": "COMP-205",
        "installed_skill_copy_drift": "COMP-206",
        "context_files_presence": "COMP-207",
        "managed_block_integrity": "COMP-208",
        "managed_block_version_drift": "COMP-209",
        "version_root_semantics": "COMP-210",
    }
    items: list[dict[str, Any]] = []
    for name, check in compatibility_checks.items():
        status = str(check.get("status", "PASS")).upper()
        if status == "PASS":
            continue
        items.append(
            {
                "code": check_code_map.get(name, f"COMP-{name.upper()}"),
                "name": name,
                "severity": str(check.get("severity", "medium")).lower(),
                "summary": str(check.get("summary", "")),
                "evidence": list(check.get("evidence", [])),
                "impact": str(check.get("impact", "")),
                "repair": list(check.get("repair", [])),
                "status": status,
            }
        )
    return items


def detect_incompatibilities(
    *,
    project_root: Path,
    runtime: dict[str, Any],
    version: str,
    artifact_stage_view: dict[str, str],
    memory_view: dict[str, Any],
) -> list[dict[str, Any]]:
    compatibility_checks = collect_compatibility_checks(
        project_root=project_root,
        runtime=runtime,
        version=version,
        artifact_stage_view=artifact_stage_view,
        memory_view=memory_view,
    )
    return _compatibility_checks_to_incompatibilities(compatibility_checks)


def _base_checks(project_root: Path) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    beacon_dir = project_root / ".beacon"
    docs_dir = project_root / "docs"
    skills_dir = project_root / "skills"

    checks.append(
        {
            "name": "beacon_directory",
            "status": "PASS" if beacon_dir.exists() else "WARN",
            "detail": ".beacon" if beacon_dir.exists() else ".beacon missing",
        }
    )
    checks.append(
        {
            "name": "docs_directory",
            "status": "PASS" if docs_dir.exists() else "WARN",
            "detail": "docs" if docs_dir.exists() else "docs missing",
        }
    )
    checks.append(
        {
            "name": "skills_directory",
            "status": "PASS" if skills_dir.exists() else "WARN",
            "detail": "skills" if skills_dir.exists() else "skills missing",
        }
    )
    return checks


def _derive_repair_plan(incompatibilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    severity_priority = {"high": "P0", "medium": "P1", "low": "P2"}
    for item in incompatibilities:
        severity = str(item.get("severity", "medium")).lower()
        plan.append(
            {
                "priority": severity_priority.get(severity, "P1"),
                "code": item.get("code", ""),
                "action": item.get("summary", ""),
                "steps": item.get("repair", []),
            }
        )
    plan.sort(key=lambda x: x.get("priority", "P9"))
    return plan


def build_doctor_payload(project_root: Path, *, strict: bool = False) -> dict[str, Any]:
    runtime = collect_runtime_info()
    normalized_root = Path(project_root)
    if not normalized_root.exists():
        compatibility_checks = {
            "context_files_presence": {"status": "UNKNOWN", "severity": "high", "summary": "project root unavailable"},
            "managed_block_integrity": {"status": "UNKNOWN", "severity": "high", "summary": "project root unavailable"},
            "managed_block_version_drift": {
                "status": "UNKNOWN",
                "severity": "medium",
                "summary": "project root unavailable",
            },
            "runless_docs_only": {"status": "UNKNOWN", "severity": "high", "summary": "project root unavailable"},
            "status_memory_divergence": {"status": "UNKNOWN", "severity": "high", "summary": "project root unavailable"},
            "stale_ptk_version_refs": {"status": "UNKNOWN", "severity": "medium", "summary": "project root unavailable"},
            "material_skill_semver_compatibility": {
                "status": "UNKNOWN",
                "severity": "high",
                "summary": "project root unavailable",
            },
            "legacy_skill_trigger_syntax": {"status": "UNKNOWN", "severity": "medium", "summary": "project root unavailable"},
            "runtime_version_consistency": {"status": "UNKNOWN", "severity": "medium", "summary": "project root unavailable"},
            "installed_skill_copy_drift": {"status": "UNKNOWN", "severity": "medium", "summary": "project root unavailable"},
        }
        return {
            "schema_version": "2.0",
            "beacon_version": runtime.get("toolkit_version") or runtime.get("package_version") or "",
            "project_root": str(normalized_root),
            "overall": "BLOCKED",
            "checks": [
                {
                    "name": "project_root",
                    "status": "FAIL",
                    "detail": "project root not found",
                }
            ],
            "runtime": runtime,
            "project": {
                "project_root": str(normalized_root),
                "available_versions": [],
                "latest_iteration_version": "",
                "version_source": "unavailable",
            },
            "materials": {
                "workflow_artifact_view": {},
                "workflow_memory_view": {
                    "run_id": "",
                    "missing_closure_stages": [],
                    "closure_complete": False,
                },
            },
            "compatibility_checks": compatibility_checks,
            "incompatibilities": [],
            "repair_plan": [],
            "generated_at": now_iso(),
        }

    project_versions = detect_iteration_versions(normalized_root)
    latest_version = str(project_versions.get("latest_iteration_version", "")).strip() or "v1.0.0"
    artifact_view = compute_artifact_stage_view(normalized_root, latest_version)
    workflow_progress = compute_workflow_progress(normalized_root, version=latest_version)
    memory_view = {
        "run_id": workflow_progress.get("run_id") or "",
        "next_stage": workflow_progress.get("next_stage"),
        "closure_complete": bool(workflow_progress.get("closure_complete")),
        "missing_closure_stages": workflow_progress.get("missing_closure_stages", []),
        "stages": workflow_progress.get("stages", {}),
    }

    checks = _base_checks(normalized_root)
    compatibility_checks = collect_compatibility_checks(
        project_root=normalized_root,
        runtime=runtime,
        version=latest_version,
        artifact_stage_view=artifact_view,
        memory_view=memory_view,
    )
    incompatibilities = _compatibility_checks_to_incompatibilities(compatibility_checks)
    repair_plan = _derive_repair_plan(incompatibilities)

    overall = "PASS"
    if any(check.get("status") == "FAIL" for check in checks):
        overall = "BLOCKED"
    elif incompatibilities:
        has_high = any(str(item.get("severity", "")).lower() == "high" for item in incompatibilities)
        overall = "BLOCKED" if strict and has_high else "WARN"
    elif any(check.get("status") == "WARN" for check in checks):
        overall = "WARN"

    return {
        "schema_version": "2.0",
        "beacon_version": runtime.get("toolkit_version") or runtime.get("package_version") or "",
        "project_root": str(normalized_root),
        "overall": overall,
        "checks": checks,
        "runtime": runtime,
        "project": {
            "project_root": str(normalized_root),
            "available_versions": project_versions.get("available_versions", []),
            "latest_iteration_version": latest_version,
            "version_source": project_versions.get("version_source", ""),
        },
        "materials": {
            "workflow_artifact_view": artifact_view,
            "workflow_memory_view": memory_view,
        },
        "compatibility_checks": compatibility_checks,
        "incompatibilities": incompatibilities,
        "repair_plan": repair_plan,
        "generated_at": now_iso(),
    }


def build_doctor_diagnostics(project_root: Path, *, strict: bool = False) -> dict[str, Any]:
    """Compatibility alias for doctor v2 payload builder."""
    return build_doctor_payload(project_root, strict=strict)
