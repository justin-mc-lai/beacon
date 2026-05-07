"""Doctor-managed version surface sync and verification helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Literal, TypedDict

from beacon.utils.runtime import now_iso, write_json
from beacon.utils.versioning import load_version_truth, normalize_version

_INIT_FILE = Path("beacon/__init__.py")
_MANIFEST_FILE = Path("beacon/version-truth.json")
_SKILL_METADATA_FILE = Path("skills/beacon/metadata.json")
_ROOT_SKILL_FILE = Path("SKILL.md")
_AGENT_SURFACE_STATE_FILE = Path(".beacon/state/agent-surfaces.json")
_TRAE_RULES_FILE = Path(".trae/rules/project_rules.md")
VERSION_SURFACE_GOVERNANCE_REASON_CODE = "version_surface_governance_drift"

_PACKAGE_VERSION_RE = re.compile(r'(^__version__\s*=\s*")(?P<value>[^"]+)(")', re.MULTILINE)
_TOOLKIT_VERSION_RE = re.compile(r'(^__toolkit_version__\s*=\s*")(?P<value>[^"]+)(")', re.MULTILINE)
_JSON_VERSION_RE = re.compile(r'("version"\s*:\s*")(?P<value>[^"]+)(")')
_RULE_RUNTIME_RE = re.compile(r"(<!--\s*BEACON:VERSION:)(?P<value>[^>\s]+)(\s*-->)")
_RULE_DOCS_RE = re.compile(r"(<!--\s*BEACON:DOCS_VERSION:)(?P<value>[^>\s]+)(\s*-->)")
_ROOT_SKILL_FRONTMATTER_VERSION_RE = re.compile(r'(^version:\s*)(?P<value>[^\n]+)$', re.MULTILINE)
_ROOT_SKILL_VERSION_LABEL_RE = re.compile(r'(^>\s*\*\*Skill Version\*\*:\s*)(?P<value>[^\n]+)$', re.MULTILINE)
_ROOT_SKILL_CLI_VERSION_LABEL_RE = re.compile(r'(^>\s*\*\*CLI Version\*\*:\s*)(?P<value>[^\n]+)$', re.MULTILINE)
_ROOT_SKILL_RELEASE_LINE_RE = re.compile(r'(^-\s+\*\*当前发布线\*\*：`)(?P<value>[^`]+)(`.*$)', re.MULTILINE)
_ROOT_SKILL_PACKAGE_LINE_RE = re.compile(r'(^-\s+\*\*当前包版本\*\*：`)(?P<value>[^`]+)(`.*$)', re.MULTILINE)
_ROOT_SKILL_DOCS_LINE_RE = re.compile(r'(^-\s+\*\*最新已接受文档线\*\*：`)(?P<value>[^`]+)(`.*$)', re.MULTILINE)


def version_surface_manifest_path(project_root: Path | str) -> Path:
    return Path(project_root).resolve() / _MANIFEST_FILE


def version_surface_repair_commands(
    project_root: Path | str,
    *,
    project_root_arg: str | None = None,
) -> list[str]:
    root_arg = project_root_arg if project_root_arg is not None else str(Path(project_root).resolve())
    return [
        f"beacon doctor sync-version-surfaces --project-root {root_arg}",
        f"beacon doctor verify-version-surfaces --project-root {root_arg} --strict",
    ]


class GovernancePayload(TypedDict):
    """Structured version surface governance payload."""

    reason_code: str
    status: Literal["pass", "fail", "warn", "not_applicable"]
    ok: bool
    blocked: bool
    configured: bool
    manifest_path: str
    repair_commands: list[str]
    verify_command: str
    checks: list[dict[str, Any]]


def format_governance_diagnostic(payload: GovernancePayload) -> dict[str, Any]:
    """Format governance payload for doctor diagnostics."""
    return {
        "status": payload["status"].upper(),
        "severity": "high",
        "summary": "Beacon self-repo version surfaces should stay projected from one canonical release manifest.",
        "evidence": [
            f"manifest_path={payload['manifest_path']}",
            *[
                f"{item.get('name')}={item.get('status')}:{json.dumps(item.get('details', {}), ensure_ascii=False)}"
                for item in payload["checks"]
                if isinstance(item, dict)
            ],
        ],
        "impact": "Drift between manifest, init constants, skill metadata, and managed host surfaces can break version resolution and release governance.",
        "repair": payload["repair_commands"],
        "reason_code": payload["reason_code"],
        "ok": payload["ok"],
        "blocked": payload["blocked"],
        "configured": payload["configured"],
    }


def get_version_surface_governance_payload(
    project_root: Path | str,
    *,
    strict: bool = True,
    project_root_arg: str | None = None,
) -> GovernancePayload:
    """Get structured version surface governance payload."""
    root = Path(project_root).resolve()
    manifest_path = version_surface_manifest_path(root)

    if not manifest_path.exists():
        return {
            "reason_code": "",
            "status": "not_applicable",
            "ok": True,
            "blocked": False,
            "configured": False,
            "manifest_path": str(manifest_path),
            "repair_commands": [],
            "verify_command": "",
            "checks": [],
        }

    res = verify_version_surfaces(root, strict=strict)
    root_arg = project_root_arg if project_root_arg is not None else str(root)
    status = str(res.get("status") or "warn").strip().lower()
    blocked = status == "fail"

    return {
        "reason_code": VERSION_SURFACE_GOVERNANCE_REASON_CODE if blocked else "",
        "status": status,  # type: ignore
        "ok": bool(res.get("ok", False)),
        "blocked": blocked,
        "configured": True,
        "manifest_path": str(res.get("manifest_path") or manifest_path),
        "repair_commands": version_surface_repair_commands(root, project_root_arg=project_root_arg),
        "verify_command": f"beacon doctor verify-version-surfaces --project-root {root_arg} --strict",
        "checks": list(res.get("checks") or []),
    }


def _canonical_manifest_payload(project_root: Path) -> dict[str, Any]:
    truth = load_version_truth(project_root)
    return {
        "schema_version": str(truth.get("schema_version", "") or "1.0"),
        "package_version": str(truth.get("package_version", "") or ""),
        "runtime_version": str(truth.get("runtime_version", "") or ""),
        "docs_default_line": str(truth.get("docs_default_line", "") or ""),
        "current_runtime_release_line": str(truth.get("current_runtime_release_line", "") or ""),
        "planning_lines": list(truth.get("planning_lines", []) or []),
        "partial_runtime_supplement_lines": list(truth.get("partial_runtime_supplement_lines", []) or []),
        "lines": dict(truth.get("lines", {}) or {}),
    }


def _manifest_versions(project_root: Path) -> dict[str, str]:
    manifest = _canonical_manifest_payload(project_root)
    package_version = str(manifest.get("package_version", "") or "").strip()
    runtime_version = normalize_version(str(manifest.get("runtime_version", "") or "").strip()) or ""
    docs_version = normalize_version(str(manifest.get("docs_default_line", "") or "").strip()) or ""
    release_line = normalize_version(str(manifest.get("current_runtime_release_line", "") or "").strip()) or ""
    return {
        "package_version": package_version,
        "runtime_version": runtime_version,
        "docs_version": docs_version,
        "release_line": release_line,
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _replace_or_append(
    content: str,
    pattern: re.Pattern[str],
    replacement: str,
    *,
    append_line: str,
) -> tuple[str, bool]:
    if pattern.search(content):
        updated = pattern.sub(replacement, content, count=1)
        return updated, updated != content
    suffix = "" if not content or content.endswith("\n") else "\n"
    updated = f"{content}{suffix}{append_line}\n"
    return updated, True


def _sync_init_surface(project_root: Path, versions: dict[str, str], *, dry_run: bool) -> dict[str, Any]:
    path = project_root / _INIT_FILE
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    updated, package_changed = _replace_or_append(
        current,
        _PACKAGE_VERSION_RE,
        rf'\g<1>{versions["package_version"]}\g<3>',
        append_line=f'__version__ = "{versions["package_version"]}"',
    )
    updated, runtime_changed = _replace_or_append(
        updated,
        _TOOLKIT_VERSION_RE,
        rf'\g<1>{versions["runtime_version"]}\g<3>',
        append_line=f'__toolkit_version__ = "{versions["runtime_version"]}"',
    )
    changed = package_changed or runtime_changed or not path.exists()
    if changed and not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(updated, encoding="utf-8")
    return {
        "id": "beacon_init",
        "path": str(path),
        "action": "planned" if dry_run and changed else "updated" if changed else "unchanged",
        "changed": changed,
        "expected": {
            "package_version": versions["package_version"],
            "runtime_version": versions["runtime_version"],
        },
    }


def _sync_manifest_surface(project_root: Path, manifest: dict[str, Any], *, dry_run: bool) -> dict[str, Any]:
    path = project_root / _MANIFEST_FILE
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    updated = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    changed = current != updated or not path.exists()
    if changed and not dry_run:
        write_json(path, manifest)
    return {
        "id": "canonical_manifest",
        "path": str(path),
        "action": "planned" if dry_run and changed else "updated" if changed else "unchanged",
        "changed": changed,
        "expected": manifest,
    }


def _sync_skill_metadata_surface(project_root: Path, versions: dict[str, str], *, dry_run: bool) -> dict[str, Any]:
    path = project_root / _SKILL_METADATA_FILE
    if not path.exists():
        return {
            "id": "skill_metadata",
            "path": str(path),
            "action": "skipped",
            "changed": False,
            "optional": True,
            "reason": "missing",
        }
    current = path.read_text(encoding="utf-8")
    updated = _JSON_VERSION_RE.sub(rf'\g<1>{versions["package_version"]}\g<3>', current, count=1)
    changed = updated != current
    if changed and not dry_run:
        path.write_text(updated, encoding="utf-8")
    return {
        "id": "skill_metadata",
        "path": str(path),
        "action": "planned" if dry_run and changed else "updated" if changed else "unchanged",
        "changed": changed,
        "expected": {"version": versions["package_version"]},
    }


def _sync_root_skill_surface(project_root: Path, versions: dict[str, str], *, dry_run: bool) -> dict[str, Any]:
    path = project_root / _ROOT_SKILL_FILE
    if not path.exists():
        return {
            "id": "root_skill_md",
            "path": str(path),
            "action": "skipped",
            "changed": False,
            "optional": True,
            "reason": "missing",
        }
    current = path.read_text(encoding="utf-8")
    updated = _ROOT_SKILL_FRONTMATTER_VERSION_RE.sub(
        rf"\g<1>{versions['package_version']}",
        current,
        count=1,
    )
    updated = _ROOT_SKILL_VERSION_LABEL_RE.sub(
        rf"\g<1>{versions['runtime_version']}",
        updated,
        count=1,
    )
    updated = _ROOT_SKILL_CLI_VERSION_LABEL_RE.sub(
        rf"\g<1>{versions['runtime_version']}",
        updated,
        count=1,
    )
    updated = _ROOT_SKILL_RELEASE_LINE_RE.sub(
        rf"\g<1>{versions['runtime_version']}\g<3>",
        updated,
        count=1,
    )
    updated = _ROOT_SKILL_PACKAGE_LINE_RE.sub(
        rf"\g<1>{versions['package_version']}\g<3>",
        updated,
        count=1,
    )
    updated = _ROOT_SKILL_DOCS_LINE_RE.sub(
        rf"\g<1>{versions['docs_version']}\g<3>",
        updated,
        count=1,
    )
    changed = updated != current
    if changed and not dry_run:
        path.write_text(updated, encoding="utf-8")
    return {
        "id": "root_skill_md",
        "path": str(path),
        "action": "planned" if dry_run and changed else "updated" if changed else "unchanged",
        "changed": changed,
        "expected": {
            "version": versions["package_version"],
            "skill_version": versions["runtime_version"],
            "cli_version": versions["runtime_version"],
            "docs_version": versions["docs_version"],
        },
    }


def _sync_trae_rules_surface(project_root: Path, versions: dict[str, str], *, dry_run: bool) -> dict[str, Any]:
    path = project_root / _TRAE_RULES_FILE
    if not path.exists():
        return {
            "id": "trae_rules",
            "path": str(path),
            "action": "skipped",
            "changed": False,
            "optional": True,
            "reason": "missing",
        }
    current = path.read_text(encoding="utf-8")
    updated = _RULE_RUNTIME_RE.sub(rf"\g<1>{versions['runtime_version']}\g<3>", current)
    updated = _RULE_DOCS_RE.sub(rf"\g<1>{versions['docs_version']}\g<3>", updated)
    changed = updated != current
    if changed and not dry_run:
        path.write_text(updated, encoding="utf-8")
    return {
        "id": "trae_rules",
        "path": str(path),
        "action": "planned" if dry_run and changed else "updated" if changed else "unchanged",
        "changed": changed,
        "expected": {
            "runtime_version": versions["runtime_version"],
            "docs_version": versions["docs_version"],
        },
    }


def _sync_agent_surface_state(project_root: Path, versions: dict[str, str], *, dry_run: bool) -> dict[str, Any]:
    path = project_root / _AGENT_SURFACE_STATE_FILE
    if not path.exists():
        return {
            "id": "agent_surface_state",
            "path": str(path),
            "action": "skipped",
            "changed": False,
            "optional": True,
            "reason": "missing",
        }
    payload = _read_json(path)
    next_payload = {
        **payload,
        "runtime_version": versions["runtime_version"],
        "docs_version": versions["docs_version"],
        "updated_at": now_iso(),
    }
    current = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    updated = json.dumps(next_payload, ensure_ascii=False, indent=2) + "\n"
    changed = current != updated
    if changed and not dry_run:
        write_json(path, next_payload)
    return {
        "id": "agent_surface_state",
        "path": str(path),
        "action": "planned" if dry_run and changed else "updated" if changed else "unchanged",
        "changed": changed,
        "expected": {
            "runtime_version": versions["runtime_version"],
            "docs_version": versions["docs_version"],
        },
    }


def sync_version_surfaces(project_root: Path | str, *, dry_run: bool) -> dict[str, Any]:
    """Project canonical version truth into managed source surfaces."""
    root = Path(project_root).resolve()
    manifest = _canonical_manifest_payload(root)
    versions = _manifest_versions(root)
    surface_results = [
        _sync_manifest_surface(root, manifest, dry_run=dry_run),
        _sync_init_surface(root, versions, dry_run=dry_run),
        _sync_skill_metadata_surface(root, versions, dry_run=dry_run),
        _sync_root_skill_surface(root, versions, dry_run=dry_run),
        _sync_trae_rules_surface(root, versions, dry_run=dry_run),
        _sync_agent_surface_state(root, versions, dry_run=dry_run),
    ]
    changed = [item for item in surface_results if item.get("changed")]
    return {
        "project_root": str(root),
        "manifest_path": str(root / _MANIFEST_FILE),
        "manifest": manifest,
        "surfaces": surface_results,
        "changed_surface_count": len(changed),
        "dry_run": dry_run,
    }


def _read_init_surface(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8")
    package_match = _PACKAGE_VERSION_RE.search(content)
    toolkit_match = _TOOLKIT_VERSION_RE.search(content)
    return {
        "package_version": str(package_match.group("value")) if package_match else "",
        "runtime_version": normalize_version(str(toolkit_match.group("value"))) if toolkit_match else "",
    }


def _read_skill_metadata_surface(path: Path) -> dict[str, str]:
    payload = _read_json(path)
    return {"version": str(payload.get("version", "") or "").strip()} if payload else {}


def _read_root_skill_surface(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8")
    frontmatter = _ROOT_SKILL_FRONTMATTER_VERSION_RE.search(content)
    skill_version = _ROOT_SKILL_VERSION_LABEL_RE.search(content)
    cli_version = _ROOT_SKILL_CLI_VERSION_LABEL_RE.search(content)
    release_line = _ROOT_SKILL_RELEASE_LINE_RE.search(content)
    package_line = _ROOT_SKILL_PACKAGE_LINE_RE.search(content)
    docs_line = _ROOT_SKILL_DOCS_LINE_RE.search(content)
    return {
        "version": str(frontmatter.group("value")).strip() if frontmatter else "",
        "skill_version": normalize_version(str(skill_version.group("value")).strip()) if skill_version else "",
        "cli_version": normalize_version(str(cli_version.group("value")).strip()) if cli_version else "",
        "runtime_version": normalize_version(str(release_line.group("value")).strip()) if release_line else "",
        "package_version": str(package_line.group("value")).strip() if package_line else "",
        "docs_version": normalize_version(str(docs_line.group("value")).strip()) if docs_line else "",
    }


def _read_trae_rules_surface(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8")
    runtime_match = _RULE_RUNTIME_RE.search(content)
    docs_match = _RULE_DOCS_RE.search(content)
    return {
        "runtime_version": normalize_version(str(runtime_match.group("value"))) if runtime_match else "",
        "docs_version": normalize_version(str(docs_match.group("value"))) if docs_match else "",
    }


def _read_agent_surface_state(path: Path) -> dict[str, str]:
    payload = _read_json(path)
    if not payload:
        return {}
    return {
        "runtime_version": normalize_version(str(payload.get("runtime_version", "") or "")) or "",
        "docs_version": normalize_version(str(payload.get("docs_version", "") or "")) or "",
    }


def _compare_optional_surface(
    *,
    name: str,
    path: Path,
    actual: dict[str, str],
    expected: dict[str, str],
    strict: bool,
) -> dict[str, Any]:
    if not path.exists():
        return {
            "name": name,
            "status": "pass",
            "details": {"path": str(path), "configured": False, "optional": True},
        }
    drift = {key: {"expected": expected.get(key, ""), "actual": actual.get(key, "")} for key in expected if actual.get(key, "") != expected.get(key, "")}
    return {
        "name": name,
        "status": "pass" if not drift else ("fail" if strict else "warn"),
        "details": {"path": str(path), "configured": True, "drift": drift},
    }


def verify_version_surfaces(project_root: Path | str, *, strict: bool) -> dict[str, Any]:
    """Verify managed source surfaces against canonical version truth."""
    root = Path(project_root).resolve()
    manifest_path = root / _MANIFEST_FILE
    manifest = _canonical_manifest_payload(root)
    versions = _manifest_versions(root)
    init_path = root / _INIT_FILE
    skill_metadata_path = root / _SKILL_METADATA_FILE
    root_skill_path = root / _ROOT_SKILL_FILE
    trae_rules_path = root / _TRAE_RULES_FILE
    agent_surface_state_path = root / _AGENT_SURFACE_STATE_FILE

    init_actual = _read_init_surface(init_path)
    skill_actual = _read_skill_metadata_surface(skill_metadata_path)

    checks: list[dict[str, Any]] = [
        {
            "name": "canonical_release_manifest_present",
            "status": "pass" if manifest_path.exists() else "fail",
            "details": {"path": str(manifest_path), "exists": manifest_path.exists()},
        },
        {
            "name": "beacon_init_surface",
            "status": (
                "pass"
                if init_actual == {
                    "package_version": versions["package_version"],
                    "runtime_version": versions["runtime_version"],
                }
                else "fail"
            ),
            "details": {
                "path": str(init_path),
                "expected": {
                    "package_version": versions["package_version"],
                    "runtime_version": versions["runtime_version"],
                },
                "actual": init_actual,
            },
        },
        _compare_optional_surface(
            name="skill_metadata_surface",
            path=skill_metadata_path,
            actual=skill_actual,
            expected={"version": versions["package_version"]},
            strict=strict,
        ),
        _compare_optional_surface(
            name="root_skill_md_surface",
            path=root_skill_path,
            actual=_read_root_skill_surface(root_skill_path),
            expected={
                "version": versions["package_version"],
                "skill_version": versions["runtime_version"],
                "cli_version": versions["runtime_version"],
                "runtime_version": versions["runtime_version"],
                "package_version": versions["package_version"],
                "docs_version": versions["docs_version"],
            },
            strict=strict,
        ),
        _compare_optional_surface(
            name="trae_rules_surface",
            path=trae_rules_path,
            actual=_read_trae_rules_surface(trae_rules_path),
            expected={
                "runtime_version": versions["runtime_version"],
                "docs_version": versions["docs_version"],
            },
            strict=strict,
        ),
        _compare_optional_surface(
            name="agent_surface_state",
            path=agent_surface_state_path,
            actual=_read_agent_surface_state(agent_surface_state_path),
            expected={
                "runtime_version": versions["runtime_version"],
                "docs_version": versions["docs_version"],
            },
            strict=strict,
        ),
    ]
    status = "pass"
    if any(str(item.get("status")) == "fail" for item in checks):
        status = "fail"
    elif any(str(item.get("status")) == "warn" for item in checks):
        status = "warn"
    return {
        "project_root": str(root),
        "manifest_path": str(manifest_path),
        "manifest": manifest,
        "strict": strict,
        "status": status,
        "ok": status != "fail",
        "checks": checks,
    }
