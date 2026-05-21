"""Markdown-first freeze truth helpers for Beacon v1.4.8+."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_change_file, machine_root
from beacon.utils.requirement_parsing import build_feature_ac_items, extract_qa_case_rows
from beacon.utils.revision_state import load_revision_state
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, resolve_target_version


MINIMAL_FREEZE_STATE_FIELDS = {
    "schema_version",
    "feature",
    "feature_slug",
    "version",
    "revision_id",
    "source_revision_id",
    "status",
    "baseline_hash",
    "source_paths",
    "diagnostics",
    "transaction_ref",
    "generated_at",
}
FULLTEXT_MIRROR_KEYS = {
    "markdown",
    "content",
    "body",
    "text",
    "raw",
    "raw_markdown",
    "fulltext",
    "full_text",
    "document",
    "source_excerpt",
    "source_markdown",
}


def markdown_first_freeze_supported(version: str | None) -> bool:
    normalized = normalize_version(version) or ""
    if not normalized.startswith("v"):
        return False
    try:
        major, minor, patch = [int(part) for part in normalized[1:].split(".")]
    except Exception:  # noqa: BLE001
        return False
    return (major, minor, patch) >= (1, 4, 8)


def stable_text_hash(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def stable_text_hash_uri(text: str) -> str:
    return f"sha256:{stable_text_hash(text)}"


def markdown_truth_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    root = project_root / "docs" / "beacon" / resolved_version
    return {
        "prd": root / "prd" / f"{slug}.md",
        "user_story": root / "user-story" / f"{slug}.md",
        "test_case": root / "qa" / "test-cases" / f"{slug}.md",
        "research": root / "research" / f"{slug}.md",
        "source_architecture": root / "source-architecture" / f"{slug}.md",
        "change": root / "change" / f"{slug}.md",
    }


def _relative(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def source_path_refs(project_root: Path, version: str, feature: str) -> dict[str, str]:
    return {
        name: _relative(project_root, path)
        for name, path in markdown_truth_paths(project_root, version, feature).items()
        if path.exists()
    }


def read_markdown_truth(project_root: Path, version: str, feature: str) -> dict[str, str]:
    docs: dict[str, str] = {}
    for name, path in markdown_truth_paths(project_root, version, feature).items():
        if path.exists():
            docs[name] = path.read_text(encoding="utf-8")
    return docs


def markdown_truth_hash(project_root: Path, version: str, feature: str) -> str:
    docs = read_markdown_truth(project_root, version, feature)
    ordered = [docs.get("user_story", ""), docs.get("prd", ""), docs.get("test_case", "")]
    return stable_text_hash_uri("\n\n".join(text for text in ordered if text))


def build_markdown_first_compile_payload(
    *,
    feature: str,
    slug: str,
    version: str,
    md_content: str,
    contract: dict[str, object],
    transaction_id: str,
    source_hash: str,
    projection_seq: str,
    committed_at: str,
    sink_checksums: dict[str, str],
    requested_mode: str,
    effective_mode: str,
    generator_mode: str,
    fallback_reason: str,
    capability_snapshot: dict[str, object],
    source_refs: list[str],
    project_metadata_context: dict[str, object],
    model: str,
    requested_diagrams: list[str],
    requested_state_axes: list[str],
    supersedes_transaction_id: str = "",
    supersedes_projection_seq: str = "",
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "effective_mode": effective_mode,
        "generator_mode": generator_mode,
        "requested_mode": requested_mode,
        "model": model,
        "diagram_truth_request": {
            "diagram_types": requested_diagrams,
            "state_axes": requested_state_axes,
        },
        "fallback_reason": fallback_reason,
        "capability_snapshot": capability_snapshot,
        "source_refs": source_refs,
        "project_metadata_context": project_metadata_context,
        "constraint_hits": contract.get("semantic_hits", {}),
        "missing_headings": contract.get("missing_headings", []),
        "open_questions": contract.get("placeholder_hits", []),
        "contract_ok": bool(contract.get("ok", False)),
        "compile_hash": stable_text_hash(md_content),
        "source_hash": source_hash,
        "source_paths": {"prd": f"docs/beacon/{version}/prd/{slug}.md"},
        "projection_seq": projection_seq,
        "transaction_id": transaction_id,
        "committed_at": committed_at,
        "sink_checksums": sink_checksums,
        "status": "applied",
        "supersedes_transaction_id": supersedes_transaction_id,
        "supersedes_projection_seq": supersedes_projection_seq,
    }


def build_markdown_first_prd_canonical(
    *,
    feature: str,
    slug: str,
    version: str,
    template: dict[str, str],
    mode_contract: dict[str, object],
    model: str,
    requested_diagrams: list[str],
    requested_state_axes: list[str],
    source_refs: list[str],
    project_metadata_context: dict[str, object],
    contract: dict[str, object],
    md_content: str,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "track": template["track"],
        "family": template["family"],
        "label": template["label"],
        **mode_contract,
        "model": model,
        "diagram_truth_request": {
            "diagram_types": requested_diagrams,
            "state_axes": requested_state_axes,
        },
        "source_refs": source_refs,
        "source_paths": {"prd": f"docs/beacon/{version}/prd/{slug}.md"},
        "project_metadata_context": project_metadata_context,
        "contract": contract,
        "markdown_hash": stable_text_hash_uri(md_content),
        "markdown_bytes": len(md_content.encode("utf-8")),
        "fulltext_mirror": False,
    }


def build_markdown_first_legacy_prd_payload(
    *,
    feature: str,
    slug: str,
    version: str,
    template: dict[str, str],
    requested_mode: str,
    effective_mode: str,
    generator_mode: str,
    fallback_reason: str,
    md_content: str,
    transaction: dict[str, Any],
) -> dict[str, Any]:
    return {
        "metadata": {
            "feature": feature,
            "feature_slug": slug,
            "version": version,
        },
        "source_paths": {"prd": f"docs/beacon/{version}/prd/{slug}.md"},
        "markdown_hash": stable_text_hash_uri(md_content),
        "markdown_bytes": len(md_content.encode("utf-8")),
        "fulltext_mirror": False,
        "semantic_payload": {
            "track": template["track"],
            "family": template["family"],
            "label": template["label"],
        },
        "mode_contract": {
            "compilation_mode": requested_mode,
            "effective_mode": effective_mode,
            "generator_mode": generator_mode,
            "fallback_reason": fallback_reason,
        },
        "transaction": transaction,
    }


def contains_fulltext_mirror(payload: Any, *, min_length: int = 80) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_text = str(key or "").strip().lower()
            if key_text in FULLTEXT_MIRROR_KEYS and isinstance(value, str) and len(value.strip()) >= min_length:
                return True
            if contains_fulltext_mirror(value, min_length=min_length):
                return True
    if isinstance(payload, list):
        return any(contains_fulltext_mirror(item, min_length=min_length) for item in payload)
    return False


def strip_fulltext_mirrors(payload: Any) -> Any:
    if isinstance(payload, dict):
        cleaned: dict[str, Any] = {}
        for key, value in payload.items():
            key_text = str(key or "").strip().lower()
            if key_text in FULLTEXT_MIRROR_KEYS and isinstance(value, str) and len(value.strip()) >= 80:
                cleaned[f"{key_text}_hash"] = stable_text_hash_uri(value)
                cleaned[f"{key_text}_bytes"] = len(value.encode("utf-8"))
                continue
            cleaned[str(key)] = strip_fulltext_mirrors(value)
        return cleaned
    if isinstance(payload, list):
        return [strip_fulltext_mirrors(item) for item in payload]
    return payload


def build_minimal_freeze_state(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=False)
    transaction_path = machine_change_file(project_root, resolved_version, f"{feature_slug(feature)}.refreeze-transaction.json")
    transaction = read_json(transaction_path, {})
    diagnostics: list[dict[str, Any]] = []
    paths = markdown_truth_paths(project_root, resolved_version, feature)
    for name in ("prd", "user_story", "test_case"):
        path = paths[name]
        if not path.exists():
            diagnostics.append(
                {
                    "reason_code": "missing_markdown_truth",
                    "path": _relative(project_root, path),
                    "section": name,
                    "repair_route": "beacon-change",
                }
            )
    if str(revision.get("baseline_hash") or "").strip() != markdown_truth_hash(project_root, resolved_version, feature):
        diagnostics.append(
            {
                "reason_code": "baseline_hash_mismatch",
                "path": _relative(project_root, paths["user_story"]),
                "hash": str(revision.get("baseline_hash") or ""),
                "current_hash": markdown_truth_hash(project_root, resolved_version, feature),
                "repair_route": "beacon-change",
            }
        )
    refreeze_status = str(transaction.get("refreeze_status") or "").strip()
    if str(revision.get("source_revision_id") or "").strip() and refreeze_status != "complete":
        diagnostics.append(
            {
                "reason_code": "ambiguous_refreeze_status",
                "path": _relative(project_root, transaction_path),
                "section": "refreeze_status",
                "repair_route": "beacon-change-refreeze",
            }
        )
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "revision_id": str(revision.get("revision_id") or ""),
        "source_revision_id": str(revision.get("source_revision_id") or ""),
        "status": "blocked" if diagnostics else "frozen",
        "baseline_hash": str(revision.get("baseline_hash") or ""),
        "source_paths": source_path_refs(project_root, resolved_version, feature),
        "diagnostics": diagnostics,
        "transaction_ref": _relative(project_root, transaction_path) if transaction_path.exists() else "",
        "generated_at": now_iso(),
    }


def minimal_freeze_state_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_root(project_root, resolved_version) / "requirement" / f"{feature_slug(feature)}.freeze-state.json"


def write_minimal_freeze_state(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    payload = build_minimal_freeze_state(project_root, version=version, feature=feature)
    write_json(minimal_freeze_state_path(project_root, str(payload["version"]), feature), payload)
    return payload


def validate_minimal_freeze_state(payload: dict[str, Any]) -> dict[str, Any]:
    keys = set(payload)
    extra = sorted(keys - MINIMAL_FREEZE_STATE_FIELDS)
    fulltext = contains_fulltext_mirror(payload)
    return {
        "status": "pass" if not extra and not fulltext else "fail",
        "extra_fields": extra,
        "contains_fulltext_mirror": fulltext,
        "allowed_fields": sorted(MINIMAL_FREEZE_STATE_FIELDS),
    }


def parse_markdown_truth_projection(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    docs = read_markdown_truth(project_root, resolved_version, feature)
    prd = docs.get("prd", "")
    user_story = docs.get("user_story", "")
    test_case = docs.get("test_case", "")
    prd_ac = build_feature_ac_items(user_story_content="", prd_content=prd, prd_source="prd")
    user_story_ac = build_feature_ac_items(user_story_content=user_story, user_story_source="user-story")
    test_case_rows = extract_qa_case_rows(test_case, source="test-case")
    test_case_ac_ids = sorted({str(row.get("ac_id") or "").upper() for row in test_case_rows if str(row.get("ac_id") or "").strip()})
    ac_ids = sorted({str(item.get("ac_id") or "").upper() for item in prd_ac + user_story_ac if str(item.get("ac_id") or "").strip()})
    diagnostics: list[dict[str, Any]] = []
    if not prd_ac:
        diagnostics.append({"reason_code": "prd_ac_parse_failed", "path": source_path_refs(project_root, resolved_version, feature).get("prd", ""), "repair_route": "beacon-prd"})
    if not user_story_ac:
        diagnostics.append({"reason_code": "user_story_ac_parse_failed", "path": source_path_refs(project_root, resolved_version, feature).get("user_story", ""), "repair_route": "beacon-user-story"})
    missing_coverage = sorted(set(ac_ids) - set(test_case_ac_ids))
    for ac_id in missing_coverage:
        diagnostics.append({"reason_code": "missing_test_case_coverage", "section": ac_id, "path": source_path_refs(project_root, resolved_version, feature).get("test_case", ""), "repair_route": "beacon-test-case"})
    return {
        "feature": feature,
        "version": resolved_version,
        "source_paths": source_path_refs(project_root, resolved_version, feature),
        "prd_ac_ids": sorted({str(item.get("ac_id") or "").upper() for item in prd_ac}),
        "user_story_ac_ids": sorted({str(item.get("ac_id") or "").upper() for item in user_story_ac}),
        "test_case_ac_ids": test_case_ac_ids,
        "diagnostics": diagnostics,
        "status": "blocked" if diagnostics else "pass",
    }
