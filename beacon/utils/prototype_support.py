"""Support helpers for Beacon prototype gate and lifecycle checks."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beacon.utils.prototype_utils import (
    evaluate_prototype_status,
    prototype_files,
    slugify_feature,
    source_doc_paths,
)
from beacon.utils.versioning import normalize_version, release_line_key


PROTOTYPE_TRIGGER_PATTERNS = (
    re.compile(r"ui_visualization_required\s*[:=]\s*true", re.IGNORECASE),
    re.compile(r"prototype_freeze_required\s*[:=]\s*true", re.IGNORECASE),
    re.compile(r"interactive_prototype_required\s*[:=]\s*true", re.IGNORECASE),
    re.compile(r"prototype_ux_prd_required\s*[:=]\s*true", re.IGNORECASE),
)
ROUTE_CLOSURE_PATTERNS = (
    re.compile(r"route_closure_required\s*[:=]\s*true", re.IGNORECASE),
)
ACCEPTED_DESIGN_RESULT_PATTERNS = (
    re.compile(r"accepted_design_result_required\s*[:=]\s*true", re.IGNORECASE),
    re.compile(r"design_result_binding_required\s*[:=]\s*true", re.IGNORECASE),
    re.compile(r"ui_ux_result_accepted\s*[:=]\s*true", re.IGNORECASE),
)


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = release_line_key(version) or normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def prototype_adapter_only_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 4, 9)


def prototype_generation_deprecated(version: str | None) -> bool:
    return prototype_adapter_only_supported(version)


def prototype_dir(project_root: Path, version: str, feature: str) -> Path:
    return project_root / "docs" / "beacon" / version / "prototype" / slugify_feature(feature)


def prototype_adapter_dir(project_root: Path, version: str, feature: str) -> Path:
    return project_root / "docs" / "beacon" / version / "prototype-adapter" / slugify_feature(feature)


def prototype_adapter_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    root = prototype_adapter_dir(project_root, version, feature)
    return {
        "root": root,
        "binding_json": root / "design-result-binding.json",
        "binding_md": root / "design-result-binding.md",
    }


def prototype_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    return prototype_files(project_root, version, feature)


def _sha256_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_refs(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    resolved = source_doc_paths(project_root, version, feature)
    return {
        "user_story": resolved["user-story"],
        "prd": resolved["prd"],
        "test_case": resolved["test-case"],
    }


def source_fingerprints(project_root: Path, version: str, feature: str) -> dict[str, str]:
    refs = source_refs(project_root, version, feature)
    out: dict[str, str] = {}
    for key, path in refs.items():
        if path.exists():
            out[key] = _sha256_file(path)
    if "user_story" in out and "user-story" not in out:
        out["user-story"] = out["user_story"]
    return out


def build_ui_ux_dev_route(
    *,
    feature: str,
    version: str,
    project_root: Path,
    intent: str = "review",
) -> dict[str, str]:
    normalized_intent = str(intent or "review").strip().lower().replace("_", "-")
    if normalized_intent not in {"explore", "system", "review", "polish", "extract", "library", "bootstrap"}:
        normalized_intent = "review"
    if normalized_intent == "bootstrap":
        skill_name = "ui-ux-dev-bootstrap"
        command = f'$ui-ux-dev:{skill_name} "{feature}" --project {project_root} --version {version}'
    else:
        skill_name = f"ui-ux-dev-{normalized_intent}"
        command = f'$ui-ux-dev:{skill_name} "{feature}" --project {project_root} --version {version}'
    return {
        "target_surface": "ui-ux-dev",
        "skill": skill_name,
        "command": command,
        "bootstrap_command": f'$ui-ux-dev:ui-ux-dev-bootstrap "{feature}" --project {project_root} --version {version}',
    }


def _relative(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _render_adapter_binding_markdown(payload: dict[str, Any]) -> str:
    truth = payload.get("truth_bindings") if isinstance(payload.get("truth_bindings"), dict) else {}
    result = payload.get("accepted_design_result") if isinstance(payload.get("accepted_design_result"), dict) else {}
    refs = result.get("refs") if isinstance(result.get("refs"), list) else []
    lines = [
        "# Prototype Adapter Binding",
        "",
        f"- feature: `{payload.get('feature', '')}`",
        f"- version: `{payload.get('version', '')}`",
        f"- status: `{payload.get('status', '')}`",
        f"- adapter_role: `{payload.get('adapter_role', '')}`",
        "",
        "## Accepted Design Result",
        f"- source: `{result.get('source', '')}`",
        f"- accepted_by: `{result.get('accepted_by', '')}`",
        f"- accepted_at: `{result.get('accepted_at', '')}`",
        f"- summary: {result.get('summary', '')}",
        "",
        "## Result Refs",
    ]
    if refs:
        lines.extend(f"- `{item}`" for item in refs)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Screen Intent",
        ]
    )
    screen_intent = _string_list(payload.get("screen_intent"))
    lines.extend(f"- {item}" for item in screen_intent) if screen_intent else lines.append("- none")
    lines.extend(["", "## State Visibility"])
    state_visibility = _string_list(payload.get("state_visibility"))
    lines.extend(f"- {item}" for item in state_visibility) if state_visibility else lines.append("- none")
    lines.extend(["", "## Interaction Handoff"])
    interaction_handoff = _string_list(payload.get("interaction_handoff"))
    lines.extend(f"- {item}" for item in interaction_handoff) if interaction_handoff else lines.append("- none")
    lines.extend(
        [
            "",
            "## Truth Bindings",
            f"- prd_refs: `{truth.get('prd_refs', '')}`",
            f"- user_story_refs: `{truth.get('user_story_refs', '')}`",
            f"- test_case_refs: `{truth.get('test_case_refs', '')}`",
            f"- coverage_notes: {truth.get('coverage_notes', '')}",
            f"- out_of_scope_notes: {truth.get('out_of_scope_notes', '')}",
            "",
            "## Diagnostics",
            f"- binding_ready: `{bool(payload.get('binding_ready', False))}`",
            f"- missing_truth_bindings: {', '.join(payload.get('missing_truth_bindings', [])) if isinstance(payload.get('missing_truth_bindings'), list) else 'none'}",
            "",
        ]
    )
    return "\n".join(lines)


def write_design_result_adapter_binding(
    project_root: Path,
    version: str,
    feature: str,
    *,
    design_result_ref: str = "",
    design_result_source: str = "",
    accepted_by: str = "",
    summary: str = "",
    screen_intent: list[str] | None = None,
    state_visibility: list[str] | None = None,
    interaction_handoff: list[str] | None = None,
    coverage_notes: str = "",
    out_of_scope_notes: str = "",
) -> dict[str, Any]:
    refs = source_refs(project_root, version, feature)
    paths = prototype_adapter_paths(project_root, version, feature)
    missing_truth_bindings = [
        key
        for key, path in refs.items()
        if not path.exists()
    ]
    truth_bindings = {
        "prd_refs": _relative(project_root, refs["prd"]),
        "user_story_refs": _relative(project_root, refs["user_story"]),
        "test_case_refs": _relative(project_root, refs["test_case"]),
        "source_hashes": source_fingerprints(project_root, version, feature),
        "coverage_notes": str(coverage_notes or "accepted design result is mapped to frozen PRD, user-story, and test-case truth").strip(),
        "out_of_scope_notes": str(out_of_scope_notes or "adapter binding does not make UI/UX projection canonical truth").strip(),
    }
    result_refs = _string_list([design_result_ref] if design_result_ref else [])
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slugify_feature(feature),
        "version": version,
        "status": "ready" if not missing_truth_bindings else "blocked",
        "adapter_role": "design-result-adapter",
        "source_surface": "ui-ux-dev",
        "consumption_surface": "implement",
        "accepted_design_result": {
            "source": str(design_result_source or "ui-ux-dev").strip(),
            "refs": result_refs,
            "summary": str(summary or "").strip(),
            "accepted_by": str(accepted_by or "").strip(),
            "accepted_at": _now_iso(),
        },
        "screen_intent": _string_list(screen_intent or []),
        "state_visibility": _string_list(state_visibility or []),
        "interaction_handoff": _string_list(interaction_handoff or []),
        "truth_bindings": truth_bindings,
        "binding_ready": not missing_truth_bindings,
        "missing_truth_bindings": missing_truth_bindings,
        "paths": {
            "binding_json": _relative(project_root, paths["binding_json"]),
            "binding_md": _relative(project_root, paths["binding_md"]),
        },
        "generated_at": _now_iso(),
    }
    paths["root"].mkdir(parents=True, exist_ok=True)
    paths["binding_json"].write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["binding_md"].write_text(_render_adapter_binding_markdown(payload), encoding="utf-8")
    return payload


def load_design_result_adapter_binding(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    path = prototype_adapter_paths(project_root, version, feature)["binding_json"]
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def feature_has_accepted_design_result(project_root: Path, version: str, feature: str) -> bool:
    binding = load_design_result_adapter_binding(project_root, version, feature)
    if not binding:
        return False
    result = binding.get("accepted_design_result") if isinstance(binding.get("accepted_design_result"), dict) else {}
    return bool(result.get("refs") or result.get("summary") or result.get("source"))


def design_result_adapter_status(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    paths = prototype_adapter_paths(project_root, version, feature)
    binding = load_design_result_adapter_binding(project_root, version, feature)
    if not binding:
        route = build_ui_ux_dev_route(feature=feature, version=version, project_root=project_root, intent="review")
        return {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": slugify_feature(feature),
            "version": version,
            "status": "missing",
            "reason_code": "design_result_adapter_binding_missing",
            "adapter_role": "design-result-adapter",
            "binding_ready": False,
            "paths": {key: _relative(project_root, path) for key, path in paths.items() if key != "root"},
            "recommended_route": route,
            "recommended_command": (
                f'beacon prototype adapt "{feature}" --project {project_root} --version {version} '
                "--design-result-ref <ui-ux-dev-output>"
            ),
        }
    return {
        **binding,
        "reason_code": "" if str(binding.get("status") or "") == "ready" else "design_result_adapter_binding_incomplete",
    }


def prototype_status(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    if prototype_adapter_only_supported(version):
        payload = design_result_adapter_status(project_root, version, feature)
        payload["legacy_prototype"] = evaluate_prototype_status(project_root, version, feature)
        return payload
    payload = evaluate_prototype_status(project_root, version, feature)
    files = prototype_paths(project_root, version, feature)
    payload["files"] = files
    payload["paths"] = {key: str(path) for key, path in files.items()}
    return payload


def feature_requires_prototype(project_root: Path, version: str, feature: str) -> bool:
    refs = source_refs(project_root, version, feature)
    for path in refs.values():
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        if any(pattern.search(text) for pattern in PROTOTYPE_TRIGGER_PATTERNS):
            return True
    return False


def feature_requires_design_result_binding(project_root: Path, version: str, feature: str) -> bool:
    if not prototype_adapter_only_supported(version):
        return False
    if feature_requires_prototype(project_root, version, feature):
        return True
    refs = source_refs(project_root, version, feature)
    for path in refs.values():
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        if any(pattern.search(text) for pattern in ACCEPTED_DESIGN_RESULT_PATTERNS):
            return True
    return False


def version_requires_prototype(project_root: Path, version: str) -> bool:
    roots = [
        project_root / "docs" / "beacon" / version / "user-story",
        project_root / "docs" / "beacon" / version / "prd",
        project_root / "docs" / "beacon" / version / "qa" / "test-cases",
    ]
    for root in roots:
        if not root.exists():
            continue
        for path in root.glob("*.md"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:  # noqa: BLE001
                continue
            if any(pattern.search(text) for pattern in PROTOTYPE_TRIGGER_PATTERNS):
                return True
    return False


def feature_requires_route_closure(project_root: Path, version: str, feature: str) -> bool:
    refs = source_refs(project_root, version, feature)
    for path in refs.values():
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        if any(pattern.search(text) for pattern in ROUTE_CLOSURE_PATTERNS):
            return True
    return False
