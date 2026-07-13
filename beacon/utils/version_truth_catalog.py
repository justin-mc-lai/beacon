"""MD-only version truth catalog and archive plane helpers (v1.5.2+)."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, read_json, utc_compact_ts, write_json
from beacon.utils.versioning import normalize_version, release_line_key, resolve_target_version

PARSER_CONTRACT = "beacon-version-truth-catalog-v1"
CATALOG_MD_REL = Path("docs/beacon/governance/version-truth-catalog.md")
CATALOG_JSON_REL = Path("docs/beacon/.machine/version-truth-catalog.json")
ARCHIVE_INDEX_MD_REL = Path("docs/beacon/archive/INDEX.md")
DEFAULT_ACTIVE_WINDOW = 3
ACTIVE_STATES = frozenset({"active"})
ARCHIVED_STATES = frozenset({"archived-reference-only", "archived"})

_VERSION_HEADING_RE = re.compile(r"^###\s+(v\S+)\s*$", re.IGNORECASE)
_KV_BULLET_RE = re.compile(r"^\s*-\s+`?([A-Za-z0-9_ -]+)`?:\s*`?([^`\n]+?)`?\s*$")
_AC_ROW_RE = re.compile(r"^\|\s*(AC-\d{3})\s*\|", re.MULTILINE)
_EXCLUDED_BEACON_CHILDREN = frozenset(
    {".machine", "governance", "archive", "research", "hooks", "global-boundaries.md", "VERSION"}
)


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = release_line_key(version) or normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def catalog_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 5, 2)


def catalog_md_path(project_root: Path) -> Path:
    return project_root.expanduser().resolve() / CATALOG_MD_REL


def catalog_json_path(project_root: Path) -> Path:
    return project_root.expanduser().resolve() / CATALOG_JSON_REL


def archive_index_md_path(project_root: Path) -> Path:
    return project_root.expanduser().resolve() / ARCHIVE_INDEX_MD_REL


def catalog_md_authoritative(project_root: Path) -> bool:
    return catalog_md_path(project_root).is_file()


def _rel(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _stable_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    frontmatter: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    return frontmatter, parts[2]


def _default_payload(project_root: Path) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "active_delivery_window": DEFAULT_ACTIVE_WINDOW,
        "active_truth_root_pattern": "docs/beacon/{version}/",
        "archived_truth_root_pattern": "docs/beacon/archive/{version}/",
        "support_research_root": "docs/beacon/research/",
        "versions": {},
        "transaction": {},
    }


def _normalize_validation_state(value: str) -> str:
    text = str(value or "").strip().lower()
    if text in ACTIVE_STATES:
        return "active"
    if text in ARCHIVED_STATES or text == "archived-reference-only":
        return "archived-reference-only"
    return text or "active"


def _parse_version_sections(body: str) -> dict[str, dict[str, Any]]:
    versions: dict[str, dict[str, Any]] = {}
    current_version = ""
    current: dict[str, Any] = {}
    section = ""

    for line in body.splitlines():
        stripped = line.strip()
        if stripped == "## Active Delivery Versions":
            section = "active"
            continue
        if stripped == "## Archived Versions":
            section = "archived"
            continue
        version_match = _VERSION_HEADING_RE.match(stripped)
        if version_match:
            if current_version:
                versions[current_version] = current
            current_version = normalize_version(version_match.group(1)) or version_match.group(1)
            current = {"version": current_version, "section": section}
            continue
        if not current_version:
            continue
        if stripped.startswith("## "):
            break
        kv = _KV_BULLET_RE.match(line)
        if kv:
            key = kv.group(1).strip().lower().replace(" ", "_")
            value = kv.group(2).strip()
            if key == "validation_state":
                current["validation_state"] = _normalize_validation_state(value)
            elif key == "truth_root":
                current["truth_root"] = value
            elif key == "archived_at":
                current["archived_at"] = value
            elif key == "reason":
                current["reason"] = value
    if current_version:
        versions[current_version] = current
    return versions


def parse_catalog_markdown(text: str, *, project_root: Path) -> dict[str, Any]:
    frontmatter, body = _parse_frontmatter(text)
    payload = _default_payload(project_root)
    payload["active_delivery_window"] = int(frontmatter.get("active_delivery_window") or DEFAULT_ACTIVE_WINDOW)
    versions = _parse_version_sections(body)
    if versions:
        payload["versions"] = versions
    payload["transaction"] = {
        "transaction_id": frontmatter.get("transaction_id", ""),
        "committed_at": frontmatter.get("committed_at", ""),
        "source_hash": frontmatter.get("source_hash", ""),
        "event_type": frontmatter.get("event_type", ""),
        "parser_contract": frontmatter.get("parser_contract", PARSER_CONTRACT),
    }
    return payload


def sync_catalog_versions(
    project_root: Path,
    *,
    dry_run: bool = False,
    active_window: int = 0,
) -> dict[str, Any]:
    """Discover version dirs under docs/beacon/ and sync them into the catalog.

    New versions are registered as active. When the active window is exceeded,
    the oldest active versions are moved to archived-reference-only.
    """
    root = project_root.expanduser().resolve()
    catalog = load_catalog_payload(root)
    window = active_window or int(catalog.get("active_delivery_window") or DEFAULT_ACTIVE_WINDOW)
    existing_versions = catalog.get("versions") if isinstance(catalog.get("versions"), dict) else {}
    discovered = _glob_discovered_versions(root)
    added: list[str] = []
    skipped: list[str] = []
    for version in discovered:
        if version in existing_versions:
            skipped.append(version)
            continue
        # Determine if this version's truth_root exists
        active_root = root / "docs" / "beacon" / version
        is_active_on_disk = active_root.is_dir()
        archived_root = root / "docs" / "beacon" / "archive" / version
        is_archived_on_disk = archived_root.is_dir() and not is_active_on_disk
        state = "archived-reference-only" if is_archived_on_disk else "active"
        truth_root = _default_truth_root(root, version, archived=is_archived_on_disk)
        entry: dict[str, Any] = {
            "version": version,
            "validation_state": state,
            "truth_root": truth_root,
            "section": "archived" if state == "archived-reference-only" else "active",
        }
        if is_archived_on_disk:
            entry["archived_at"] = now_iso()
            entry["reason"] = "discovered-in-archive"
        existing_versions[version] = entry
        added.append(version)
    # Enforce active window: sort active versions, archive oldest beyond window
    archived_by_window: list[str] = []
    active_entries = [
        (v, e) for v, e in existing_versions.items()
        if isinstance(e, dict) and str(e.get("validation_state") or "") == "active"
    ]
    active_sorted = sorted(active_entries, key=lambda pair: _semver_tuple(pair[0]))
    if len(active_sorted) > window:
        to_archive = active_sorted[: len(active_sorted) - window]
        for version, entry in to_archive:
            entry["validation_state"] = "archived-reference-only"
            entry["truth_root"] = _default_truth_root(root, version, archived=True)
            entry["archived_at"] = now_iso()
            entry["reason"] = "release-line-window"
            entry["section"] = "archived"
            existing_versions[version] = entry
            archived_by_window.append(version)
    catalog["versions"] = existing_versions
    summary = {
        "schema_version": "1.0",
        "dry_run": dry_run,
        "discovered_count": len(discovered),
        "added": added,
        "added_count": len(added),
        "skipped_already_registered": skipped,
        "archived_by_window": archived_by_window,
        "archived_by_window_count": len(archived_by_window),
        "active_window": window,
    }
    if dry_run:
        summary["status"] = "dry_run"
        return summary
    commit_result = commit_catalog_payload(root, catalog, event_type="catalog-sync")
    summary["status"] = "committed"
    summary["commit"] = commit_result
    return summary


def load_catalog_payload(project_root: Path) -> dict[str, Any]:
    path = catalog_md_path(project_root)
    if not path.is_file():
        return _default_payload(project_root)
    return parse_catalog_markdown(path.read_text(encoding="utf-8"), project_root=project_root)


def _glob_discovered_versions(project_root: Path) -> list[str]:
    root = project_root / "docs" / "beacon"
    if not root.is_dir():
        return []
    versions: list[str] = []
    for child in root.iterdir():
        if not child.is_dir():
            continue
        if child.name in _EXCLUDED_BEACON_CHILDREN:
            continue
        if not release_line_key(child.name):
            continue
        versions.append(child.name)
    archive_root = root / "archive"
    if archive_root.is_dir():
        for child in archive_root.iterdir():
            if child.is_dir():
                if release_line_key(child.name) and child.name not in versions:
                    versions.append(child.name)
    return sorted(set(versions), key=_semver_tuple)


def _default_truth_root(project_root: Path, version: str, *, archived: bool) -> str:
    if archived:
        return f"docs/beacon/archive/{version}"
    return f"docs/beacon/{version}"


def resolve_version_truth_root(project_root: Path, version: str, *, include_archived: bool = True) -> Path:
    resolved = normalize_version(version) or version
    root = project_root.expanduser().resolve()
    payload = load_catalog_payload(root)
    versions = payload.get("versions") if isinstance(payload.get("versions"), dict) else {}
    entry = versions.get(resolved) if isinstance(versions.get(resolved), dict) else {}
    truth_root = str(entry.get("truth_root") or "").strip()
    if truth_root:
        path = root / truth_root
        if path.is_dir() or include_archived:
            return path
    active_path = root / "docs" / "beacon" / resolved
    if active_path.is_dir():
        return active_path
    archive_path = root / "docs" / "beacon" / "archive" / resolved
    if archive_path.is_dir():
        return archive_path
    return active_path


def list_active_catalog_versions(project_root: Path) -> list[str]:
    payload = load_catalog_payload(project_root)
    versions = payload.get("versions") if isinstance(payload.get("versions"), dict) else {}
    active = [
        key
        for key, item in versions.items()
        if isinstance(item, dict) and str(item.get("validation_state") or "") == "active"
    ]
    if active:
        return sorted(active, key=_semver_tuple)
    discovered = _glob_discovered_versions(project_root)
    if not discovered:
        return []
    window = int(payload.get("active_delivery_window") or DEFAULT_ACTIVE_WINDOW)
    return discovered[-window:]


def list_all_catalog_versions(project_root: Path) -> list[str]:
    payload = load_catalog_payload(project_root)
    versions = payload.get("versions") if isinstance(payload.get("versions"), dict) else {}
    if versions:
        return sorted(versions.keys(), key=_semver_tuple)
    return _glob_discovered_versions(project_root)


def render_catalog_markdown(payload: dict[str, Any]) -> str:
    transaction = payload.get("transaction") if isinstance(payload.get("transaction"), dict) else {}
    versions = payload.get("versions") if isinstance(payload.get("versions"), dict) else {}
    frontmatter = {
        "schema_version": payload.get("schema_version", "1.0"),
        "parser_contract": PARSER_CONTRACT,
        "active_delivery_window": payload.get("active_delivery_window", DEFAULT_ACTIVE_WINDOW),
        "transaction_id": transaction.get("transaction_id", ""),
        "committed_at": transaction.get("committed_at", ""),
        "source_hash": transaction.get("source_hash", ""),
        "event_type": transaction.get("event_type", ""),
    }
    fm_lines = "\n".join(f'{key}: "{value}"' for key, value in frontmatter.items())
    lines = [
        "---",
        fm_lines,
        "---",
        "",
        "# Version Truth Catalog",
        "",
        "## Policy",
        f"- active_delivery_window: `{payload.get('active_delivery_window', DEFAULT_ACTIVE_WINDOW)}`",
        f"- active_truth_root_pattern: `{payload.get('active_truth_root_pattern', 'docs/beacon/{version}/')}`",
        f"- archived_truth_root_pattern: `{payload.get('archived_truth_root_pattern', 'docs/beacon/archive/{version}/')}`",
        f"- support_research_root: `{payload.get('support_research_root', 'docs/beacon/research/')}`",
        "",
        "## Active Delivery Versions",
        "",
    ]
    active_versions = [
        (version, item)
        for version, item in sorted(versions.items(), key=lambda pair: _semver_tuple(pair[0]))
        if isinstance(item, dict) and str(item.get("validation_state") or "") == "active"
    ]
    if not active_versions:
        lines.append("- none")
    else:
        for version, item in active_versions:
            lines.append(f"### {version}")
            lines.append(f"- validation_state: `{item.get('validation_state', 'active')}`")
            lines.append(f"- truth_root: `{item.get('truth_root', '')}`")
            lines.append("")
    lines.extend(["## Archived Versions", ""])
    archived_versions = [
        (version, item)
        for version, item in sorted(versions.items(), key=lambda pair: _semver_tuple(pair[0]))
        if isinstance(item, dict) and str(item.get("validation_state") or "") in ARCHIVED_STATES
    ]
    if not archived_versions:
        lines.append("- none")
    else:
        for version, item in archived_versions:
            lines.append(f"### {version}")
            lines.append(f"- validation_state: `{item.get('validation_state', 'archived-reference-only')}`")
            lines.append(f"- truth_root: `{item.get('truth_root', '')}`")
            if item.get("archived_at"):
                lines.append(f"- archived_at: `{item.get('archived_at')}`")
            if item.get("reason"):
                lines.append(f"- reason: `{item.get('reason')}`")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _write_json_projection(project_root: Path, payload: dict[str, Any]) -> Path:
    path = catalog_json_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    projection = {
        "schema_version": "1.0",
        "parser_contract": PARSER_CONTRACT,
        "generated_at": now_iso(),
        "active_delivery_window": payload.get("active_delivery_window", DEFAULT_ACTIVE_WINDOW),
        "versions": payload.get("versions", {}),
        "source_hash": (payload.get("transaction") or {}).get("source_hash", ""),
        "transaction_id": (payload.get("transaction") or {}).get("transaction_id", ""),
    }
    write_json(path, projection)
    return path


def commit_catalog_payload(
    project_root: Path,
    payload: dict[str, Any],
    *,
    event_type: str = "catalog-upsert",
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    body_payload = dict(payload)
    body_payload["transaction"] = {
        **(body_payload.get("transaction") if isinstance(body_payload.get("transaction"), dict) else {}),
        "transaction_id": f"tx-catalog-{utc_compact_ts().lower()}",
        "committed_at": now_iso(),
        "event_type": event_type,
        "parser_contract": PARSER_CONTRACT,
    }
    markdown = render_catalog_markdown(body_payload)
    source_hash = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
    body_payload["transaction"]["source_hash"] = source_hash
    markdown = render_catalog_markdown(body_payload)
    md_path = catalog_md_path(root)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(markdown, encoding="utf-8")
    json_path = _write_json_projection(root, body_payload)
    index_path = materialize_archive_index_md(root, body_payload)
    return {
        "status": "committed",
        "catalog_md_path": _rel(root, md_path),
        "catalog_json_path": _rel(root, json_path),
        "archive_index_path": _rel(root, index_path),
        "source_hash": source_hash,
        "transaction_id": body_payload["transaction"]["transaction_id"],
    }


def _count_features(project_root: Path, version: str) -> int:
    root = resolve_version_truth_root(project_root, version)
    features = root / "features"
    if features.is_dir():
        return len(list(features.glob("*/truth.md")))
    prd = root / "prd"
    return len(list(prd.glob("*.md"))) if prd.is_dir() else 0


def materialize_archive_index_md(project_root: Path, payload: dict[str, Any] | None = None) -> Path:
    root = project_root.expanduser().resolve()
    catalog = payload or load_catalog_payload(root)
    versions = catalog.get("versions") if isinstance(catalog.get("versions"), dict) else {}
    active_rows: list[tuple[str, str, int]] = []
    archived_rows: list[tuple[str, str, str]] = []
    for version, item in sorted(versions.items(), key=lambda pair: _semver_tuple(pair[0])):
        if not isinstance(item, dict):
            continue
        truth_root = str(item.get("truth_root") or _default_truth_root(root, version, archived=False))
        state = str(item.get("validation_state") or "active")
        if state == "active":
            active_rows.append((version, truth_root, _count_features(root, version)))
        elif state in ARCHIVED_STATES:
            archived_rows.append((version, truth_root, str(item.get("archived_at") or "")))
    active_labels = ", ".join(row[0] for row in active_rows)
    lines = [
        "# Beacon Archive Index",
        "",
        "> Generated from version-truth-catalog.md — do not edit by hand.",
        "",
        f"- active_window: {catalog.get('active_delivery_window', DEFAULT_ACTIVE_WINDOW)}",
        f"- active: {active_labels or 'none'}",
        f"- archived_count: {len(archived_rows)}",
        "",
        "## Active (delivery plane)",
        "",
        "| Version | Path | Features (count) |",
        "|---------|------|------------------|",
    ]
    if active_rows:
        for version, path, count in active_rows:
            lines.append(f"| {version} | {path} | {count} |")
    else:
        lines.append("| — | — | 0 |")
    lines.extend(
        [
            "",
            "## Archived (inspect / lineage)",
            "",
            "| Version | Path | Archived at |",
            "|---------|------|-------------|",
        ]
    )
    if archived_rows:
        for version, path, archived_at in archived_rows:
            lines.append(f"| {version} | {path} | {archived_at or '—'} |")
    else:
        lines.append("| — | — | — |")
    lines.extend(
        [
            "",
            "## Quick commands",
            "",
            "- Status: `beacon archive catalog status`",
            "- Feature history: `beacon archive lineage <slug>`",
            "- Active capability map: `beacon archive inventory`",
            "",
        ]
    )
    index_path = archive_index_md_path(root)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def build_catalog_plan(
    project_root: Path,
    *,
    active_versions: list[str] | None = None,
    target_version: str = "",
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    discovered = _glob_discovered_versions(root)
    active = active_versions or []
    if not active and target_version:
        window = DEFAULT_ACTIVE_WINDOW
        if normalize_version(target_version) in discovered:
            idx = discovered.index(normalize_version(target_version) or target_version)
            start = max(0, idx - window + 1)
            active = discovered[start : idx + 1]
        else:
            active = discovered[-DEFAULT_ACTIVE_WINDOW:]
    if not active:
        active = discovered[-DEFAULT_ACTIVE_WINDOW:] if discovered else []
    active = [normalize_version(item) or item for item in active]
    active_set = set(active)
    relocations: list[dict[str, str]] = []
    for version in discovered:
        if version in active_set:
            continue
        src = root / "docs" / "beacon" / version
        dst = root / "docs" / "beacon" / "archive" / version
        if src.is_dir():
            relocations.append(
                {
                    "version": version,
                    "from_path": _rel(root, src),
                    "to_path": _rel(root, dst),
                }
            )
    version_entries: dict[str, dict[str, Any]] = {}
    for version in active:
        version_entries[version] = {
            "version": version,
            "validation_state": "active",
            "truth_root": _default_truth_root(root, version, archived=False),
            "section": "active",
        }
    for version in discovered:
        if version in active_set:
            continue
        archived_root = _default_truth_root(root, version, archived=True)
        version_entries[version] = {
            "version": version,
            "validation_state": "archived-reference-only",
            "truth_root": archived_root,
            "archived_at": now_iso(),
            "reason": "release-line-window",
            "section": "archived",
        }
    return {
        "schema_version": "1.0",
        "status": "planned",
        "active_delivery_window": len(active) or DEFAULT_ACTIVE_WINDOW,
        "active_versions": active,
        "relocations": relocations,
        "relocation_count": len(relocations),
        "versions": version_entries,
        "generated_at": now_iso(),
    }


def _rewrite_links_bounded(tree_root: Path, version: str) -> int:
    old_prefix = f"docs/beacon/{version}/"
    new_prefix = f"docs/beacon/archive/{version}/"
    rewritten = 0
    if not tree_root.is_dir():
        return rewritten
    for path in tree_root.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if old_prefix not in text:
            continue
        path.write_text(text.replace(old_prefix, new_prefix), encoding="utf-8")
        rewritten += 1
    return rewritten


def apply_catalog_plan(project_root: Path, plan: dict[str, Any], *, confirm: bool = False) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    if not confirm:
        return {
            "status": "dry_run",
            "confirm_required": True,
            "relocation_count": plan.get("relocation_count", 0),
            "relocations": plan.get("relocations", []),
            "active_versions": plan.get("active_versions", []),
        }
    relocations = plan.get("relocations") if isinstance(plan.get("relocations"), list) else []
    applied: list[dict[str, Any]] = []
    for item in relocations:
        if not isinstance(item, dict):
            continue
        version = str(item.get("version") or "")
        src = root / str(item.get("from_path") or "")
        dst = root / str(item.get("to_path") or "")
        if not src.is_dir():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            continue
        shutil.move(str(src), str(dst))
        rewritten = _rewrite_links_bounded(dst, version)
        applied.append({"version": version, "from_path": _rel(root, src), "to_path": _rel(root, dst), "rewritten_md_files": rewritten})
    payload = {
        "schema_version": "1.0",
        "active_delivery_window": plan.get("active_delivery_window", DEFAULT_ACTIVE_WINDOW),
        "active_truth_root_pattern": "docs/beacon/{version}/",
        "archived_truth_root_pattern": "docs/beacon/archive/{version}/",
        "support_research_root": "docs/beacon/research/",
        "versions": plan.get("versions") if isinstance(plan.get("versions"), dict) else {},
        "transaction": {},
    }
    commit_result = commit_catalog_payload(root, payload, event_type="catalog-bootstrap" if applied else "catalog-upsert")
    verify = verify_catalog_projection(root, strict=True)
    return {
        "status": "applied",
        "relocations_applied": applied,
        "commit": commit_result,
        "verify": verify,
    }


def verify_catalog_projection(project_root: Path, *, strict: bool = False) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    md_path = catalog_md_path(root)
    json_path = catalog_json_path(root)
    if not md_path.is_file():
        return {
            "status": "fail" if strict else "skipped",
            "reason_code": "catalog_md_missing",
            "strict": strict,
        }
    md_text = md_path.read_text(encoding="utf-8")
    payload = parse_catalog_markdown(md_text, project_root=root)
    tx_hash = str((payload.get("transaction") or {}).get("source_hash") or "")
    body_payload = dict(payload)
    body_tx = dict(body_payload.get("transaction") if isinstance(body_payload.get("transaction"), dict) else {})
    body_tx["source_hash"] = ""
    body_payload["transaction"] = body_tx
    expected_hash = hashlib.sha256(render_catalog_markdown(body_payload).encode("utf-8")).hexdigest()
    if tx_hash and tx_hash != expected_hash:
        return {
            "status": "fail",
            "reason_code": "catalog_md_hash_mismatch",
            "expected_hash": expected_hash,
            "tx_hash": tx_hash,
        }
    projection = read_json(json_path, {})
    proj_hash = str(projection.get("source_hash") or "")
    if json_path.is_file() and proj_hash and proj_hash != tx_hash:
        return {"status": "fail", "reason_code": "catalog_projection_drift", "tx_hash": tx_hash, "json_hash": proj_hash}
    path_errors: list[dict[str, str]] = []
    versions = payload.get("versions") if isinstance(payload.get("versions"), dict) else {}
    for version, item in versions.items():
        if not isinstance(item, dict):
            continue
        truth_root = str(item.get("truth_root") or "").strip()
        if not truth_root:
            continue
        disk_path = root / truth_root
        if not disk_path.is_dir():
            path_errors.append({"version": version, "truth_root": truth_root, "issue": "missing_on_disk"})
    if path_errors:
        return {"status": "fail", "reason_code": "catalog_path_mismatch", "path_errors": path_errors}
    return {"status": "pass", "reason_code": "", "source_hash": tx_hash}


def load_catalog_status(project_root: Path) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    payload = load_catalog_payload(root)
    active = list_active_catalog_versions(root)
    return {
        "schema_version": "1.0",
        "catalog_authoritative": catalog_md_authoritative(root),
        "active_delivery_window": payload.get("active_delivery_window", DEFAULT_ACTIVE_WINDOW),
        "active_versions": active,
        "all_versions": list_all_catalog_versions(root),
        "catalog_md_path": _rel(root, catalog_md_path(root)),
        "catalog_json_path": _rel(root, catalog_json_path(root)) if catalog_json_path(root).is_file() else "",
        "archive_index_path": _rel(root, archive_index_md_path(root)) if archive_index_md_path(root).is_file() else "",
    }


def version_catalog_validation_state(project_root: Path, version: str) -> str:
    """Return catalog validation_state for a version, or empty when catalog is absent."""
    root = project_root.expanduser().resolve()
    resolved = normalize_version(version) or version
    if not catalog_md_authoritative(root):
        return ""
    payload = load_catalog_payload(root)
    versions = payload.get("versions") if isinstance(payload.get("versions"), dict) else {}
    entry = versions.get(resolved) if isinstance(versions.get(resolved), dict) else {}
    return str(entry.get("validation_state") or "").strip()


def is_version_active_for_delivery(project_root: Path, version: str) -> bool:
    state = version_catalog_validation_state(project_root, version)
    if not state:
        return True
    return state == "active"


def evaluate_catalog_delivery_preflight(
    project_root: Path,
    *,
    version: str,
    include_archived: bool = False,
) -> dict[str, Any]:
    """Fail closed when delivery surfaces target a non-active catalog version."""
    root = project_root.expanduser().resolve()
    resolved = normalize_version(version) or version
    if not catalog_supported(resolved):
        return {
            "schema_version": "1.0",
            "status": "not_applicable",
            "blocked": False,
            "reason_code": "",
            "version": resolved,
            "include_archived": include_archived,
        }
    if not catalog_md_authoritative(root):
        return {
            "schema_version": "1.0",
            "status": "not_applicable",
            "blocked": False,
            "reason_code": "",
            "version": resolved,
            "include_archived": include_archived,
        }
    state = version_catalog_validation_state(root, resolved)
    if include_archived or state == "active" or not state:
        return {
            "schema_version": "1.0",
            "status": "pass",
            "blocked": False,
            "reason_code": "",
            "version": resolved,
            "validation_state": state or "active",
            "include_archived": include_archived,
        }
    return {
        "schema_version": "1.0",
        "status": "blocked",
        "blocked": True,
        "reason_code": "version_not_on_active_delivery_plane",
        "version": resolved,
        "validation_state": state,
        "include_archived": include_archived,
        "repair_command": (
            f"beacon archive catalog status --project-root {root} "
            f"&& beacon truth-map resolve <feature> --project {root} --version {resolved}"
        ),
    }


def verify_version_truth_catalog(project_root: Path, *, strict: bool = False) -> dict[str, Any]:
    """Doctor-facing wrapper over catalog projection drift and path checks."""
    root = project_root.expanduser().resolve()
    if not catalog_md_authoritative(root):
        payload = {
            "schema_version": "1.0",
            "status": "skipped" if not strict else "fail",
            "reason_code": "catalog_md_missing",
            "strict": strict,
            "checks": [],
        }
        return payload
    projection = verify_catalog_projection(root, strict=strict)
    checks: list[dict[str, Any]] = [
        {
            "name": "catalog_projection_drift",
            "status": "pass" if projection.get("status") == "pass" else "fail",
            "reason_code": str(projection.get("reason_code") or ""),
        }
    ]
    status = "pass"
    reason_code = ""
    if projection.get("status") != "pass":
        status = "fail"
        reason_code = str(projection.get("reason_code") or "catalog_verify_failed")
    payload = {
        "schema_version": "1.0",
        "status": status,
        "reason_code": reason_code,
        "strict": strict,
        "projection": projection,
        "checks": checks,
        "catalog_md_path": _rel(root, catalog_md_path(root)),
        "catalog_json_path": _rel(root, catalog_json_path(root)) if catalog_json_path(root).is_file() else "",
    }
    return payload
