"""Utilities for contract-driven Bootstrap prototype generation and governance."""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from beacon import __toolkit_version__
from beacon.utils.learning_loop import write_prototype_design_rewrite_input
from beacon.utils.versioning import resolve_target_version

BOOTSTRAP_VERSION = "5.3.3"
BOOTSTRAP_ICONS_VERSION = "1.11.3"
ALPINE_VERSION = "3.14.1"
DEFAULT_UI_KIT = "bootstrap-5.3.x"
DEFAULT_GENERATOR_VERSION = f"prototype:{__toolkit_version__}"
_ALLOWED_ARCHETYPES = {
    "dashboard",
    "list-detail",
    "form-wizard",
    "marketing-page",
    "admin-workbench",
    "mobile-task-flow",
}
_REQUIRED_CONTRACT_KEYS = {
    "prototype_archetype",
    "theme_mood",
    "theme_primary",
    "sections",
    "navigation",
    "primary_entry",
    "primary_exit",
    "primary_cta",
    "jump_map",
    "states",
}
_LIST_KEYS = {
    "sections",
    "navigation",
    "brand_keywords",
    "states",
    "drift_guardrails",
    "required_pages",
    "required_states",
    "page_inventory",
    "page_inventory_source",
    "design_reference_sources",
}
_COMPLEX_LIST_KEYS = {"jump_map", "modal_map", "drawer_map", "tab_map"}
_BOOL_KEYS = {
    "route_closure_required",
    "ui_visualization_required",
    "design_governance_required",
}
_MULTILINE_KEYS = {
    "page_inventory_source",
    "required_pages",
    "required_states",
    "baseline_protection",
    "page_inventory",
}
_CJK_PUNCT_MAP = str.maketrans({"；": ";", "：": ":", "，": ",", "、": ","})
WEB_GUIDELINE_SOURCE_URL = "https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md"
_GENERIC_FONT_MARKERS = ("inter", "roboto", "arial", "system-ui")
_DESIGN_FONT_PRESETS = {
    "disciplined": {"display": "Fraunces", "body": "IBM Plex Sans", "mono": "JetBrains Mono"},
    "trusted": {"display": "Bitter", "body": "Source Sans 3", "mono": "JetBrains Mono"},
    "warm": {"display": "Cormorant Garamond", "body": "Source Sans 3", "mono": "JetBrains Mono"},
    "premium": {"display": "DM Serif Display", "body": "Manrope", "mono": "JetBrains Mono"},
}


def slugify_feature(text: str) -> str:
    raw = (text or "").strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", raw)
    return slug.strip("-") or "prototype-feature"


def prototype_dir(project_root: Path, version: str, feature: str) -> Path:
    return project_root / "docs" / "beacon" / version / "prototype" / slugify_feature(feature)


def prototype_files(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    root = prototype_dir(project_root, version, feature)
    return {
        "root": root,
        "index_html": root / "index.html",
        "prototype_plan": root / "prototype-plan.json",
        "design_brief": root / "design-brief.json",
        "design_system_contract": root / "design-system-contract.json",
        "design_prompt_json": root / "design-prompt.json",
        "design_prompt_md": root / "design-prompt.md",
        "ui_style_analysis_json": root / "ui-style-analysis.json",
        "ui_style_analysis_md": root / "ui-style-analysis.md",
        "manifest": root / "manifest.json",
        "source_map": root / "source-map.json",
        "freeze": root / "freeze.json",
        "prototype_brief": root / "prototype-brief.json",
        "theme": root / "theme.json",
        "tokens_css": root / "tokens.css",
        "navigation_map": root / "navigation-map.json",
        "interaction_map": root / "interaction-map.json",
        "coverage_report": root / "coverage-report.json",
        "route_closure_contract": root / "route-closure-contract.json",
        "implementation_map": root / "implementation-map.json",
        "pages_dir": root / "pages",
        "states_dir": root / "states",
        "page_specs_dir": root / "page-specs",
        "web_guideline_review_json": root / "web-guideline-review.json",
        "web_guideline_review_md": root / "web-guideline-review.md",
        "review_json": root / "prototype-review.json",
        "review_md": root / "prototype-review.md",
    }


def source_doc_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    slug = slugify_feature(feature)
    base = project_root / "docs" / "beacon" / version
    return {
        "user-story": base / "user-story" / f"{slug}.md",
        "prd": base / "prd" / f"{slug}.md",
    }


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:  # noqa: BLE001
        pass
    return {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_source_documents(project_root: Path, version: str, feature: str) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for doc_type, path in source_doc_paths(project_root, version, feature).items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        docs.append(
            {
                "type": doc_type,
                "path": path,
                "relative_path": str(path.relative_to(project_root)),
                "text": text,
                "fingerprint": sha256_text(text),
            }
        )
    return docs


def _extract_yaml_like_pairs(text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_-]*)\s*[:=]\s*(.+?)\s*$", line)
        if not match:
            continue
        key = match.group(1).strip().lower().replace("-", "_")
        value = match.group(2).strip()
        pairs[key] = value
    return pairs


def _extract_multiline_key_values(text: str, keys: set[str]) -> dict[str, str]:
    lines = text.splitlines()
    out: dict[str, str] = {}
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        match = re.match(r"^(\s*)([A-Za-z_][A-Za-z0-9_-]*)\s*[:=]\s*(.*?)\s*$", line)
        if not match:
            idx += 1
            continue
        indent = len(match.group(1))
        key = match.group(2).strip().lower().replace("-", "_")
        if key not in keys:
            idx += 1
            continue
        inline_value = match.group(3).strip()
        if inline_value:
            out[key] = inline_value
            idx += 1
            continue
        block_lines: list[str] = []
        cursor = idx + 1
        while cursor < len(lines):
            candidate = lines[cursor]
            if not candidate.strip():
                if block_lines:
                    block_lines.append(candidate)
                cursor += 1
                continue
            candidate_indent = len(candidate) - len(candidate.lstrip(" "))
            if candidate_indent <= indent and re.match(r"^\s*[A-Za-z_][A-Za-z0-9_-]*\s*[:=]", candidate):
                break
            if candidate_indent <= indent and candidate.lstrip().startswith("```"):
                break
            block_lines.append(candidate)
            cursor += 1
        if block_lines:
            out[key] = "\n".join(block_lines).strip()
        idx = cursor
    return out


def _normalize_punctuation(text: str) -> str:
    return (text or "").translate(_CJK_PUNCT_MAP)


def _split_list(value: str) -> list[str]:
    normalized = _normalize_punctuation(value)
    return [item.strip() for item in re.split(r"[|,;]", normalized) if item.strip()]


def _parse_jump_entries(value: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    normalized = _normalize_punctuation(value)
    for chunk in [item.strip() for item in normalized.split(";") if item.strip()]:
        rationale = ""
        if ":" in chunk:
            path_part, rationale = chunk.split(":", 1)
        else:
            path_part = chunk
        source = ""
        target = ""
        if "->" in path_part:
            source, target = [part.strip() for part in path_part.split("->", 1)]
        elif ">" in path_part:
            source, target = [part.strip() for part in path_part.split(">", 1)]
        if source or target:
            rows.append({"from": source or "entry", "to": target or source, "why": rationale.strip()})
    return rows


def _parse_simple_list_block(value: str) -> list[str]:
    rows: list[str] = []
    for line in (value or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            rows.append(stripped[2:].strip())
        else:
            rows.append(stripped)
    return _split_list(",".join(rows))


def _split_key_value(text: str) -> tuple[str, str]:
    normalized = _normalize_punctuation(text)
    if ":" not in normalized:
        return normalized.strip().lower().replace("-", "_"), ""
    key, value = normalized.split(":", 1)
    return key.strip().lower().replace("-", "_"), value.strip()


def _parse_baseline_protection(value: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    list_key: str | None = None
    for line in (value or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            content = stripped[2:].strip()
            if ":" in _normalize_punctuation(content):
                key, val = _split_key_value(content)
                if key in {"page", "page_id", "id"}:
                    current = {"page": val, "preserve": []}
                    items.append(current)
                    list_key = None
                elif current is not None:
                    current[key] = val
                else:
                    current = {key: val}
                    items.append(current)
            elif current is not None:
                target_key = list_key or "preserve"
                bucket = current.setdefault(target_key, [])
                if isinstance(bucket, list):
                    bucket.append(content)
        elif current is not None and ":" in _normalize_punctuation(stripped):
            key, val = _split_key_value(stripped)
            if val:
                current[key] = val
                list_key = None
            else:
                current[key] = []
                list_key = key
    normalized_items: list[dict[str, Any]] = []
    for item in items:
        page = str(item.get("page") or item.get("page_id") or item.get("id") or "").strip()
        if not page:
            continue
        preserve = item.get("preserve")
        if isinstance(preserve, str):
            preserve = _split_list(preserve)
        elif not isinstance(preserve, list):
            preserve = []
        normalized_items.append({"page": slugify_feature(page), "preserve": [str(x).strip() for x in preserve if str(x).strip()]})
    return normalized_items


def _normalize_bool(value: Any) -> bool:
    lowered = str(value or "").strip().lower()
    return lowered in {"true", "1", "yes", "y", "required"}


def _extract_as_a_user(text: str) -> str:
    match = re.search(r"\*\*As a\*\*\s+(.+?)[,，]\s*", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"^\s*As a\s+(.+?)$", text, re.IGNORECASE | re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def _normalize_contract_value(key: str, value: str) -> Any:
    if key in _BOOL_KEYS:
        return _normalize_bool(value)
    if key == "baseline_protection":
        return _parse_baseline_protection(value)
    if "\n" in str(value):
        if key in _COMPLEX_LIST_KEYS:
            rows: list[dict[str, str]] = []
            for raw_line in str(value).splitlines():
                stripped = raw_line.strip()
                if not stripped:
                    continue
                stripped = stripped[2:].strip() if stripped.startswith("- ") else stripped
                rows.extend(_parse_jump_entries(stripped))
            return rows
        if key in _LIST_KEYS:
            return _parse_simple_list_block(value)
    if key in _LIST_KEYS:
        return _split_list(value)
    if key in _COMPLEX_LIST_KEYS:
        return _parse_jump_entries(value)
    return value.strip()


def extract_prototype_contract_from_source(source_doc: dict[str, Any]) -> dict[str, Any]:
    text = str(source_doc.get("text", ""))
    raw = _extract_yaml_like_pairs(text)
    raw.update(_extract_multiline_key_values(text, _MULTILINE_KEYS))
    contract: dict[str, Any] = {}
    for key, value in raw.items():
        if key.startswith("prototype_") or key in {
            "theme_mood",
            "brand_keywords",
            "theme_primary",
            "theme_secondary",
            "surface_style",
            "sections",
            "navigation",
            "primary_entry",
            "primary_exit",
            "primary_cta",
            "secondary_cta",
            "jump_map",
            "modal_map",
            "drawer_map",
            "tab_map",
            "states",
            "target_user",
            "route_closure_required",
            "drift_guardrails",
            "prototype_mode",
            "coverage_mode",
            "required_pages",
            "required_states",
            "page_inventory",
            "page_inventory_source",
            "baseline_protection",
            "ui_visualization_required",
            "design_governance_required",
            "design_generation_mode",
            "interactive_prototype_required",
            "design_reference_sources",
        }:
            contract[key] = _normalize_contract_value(key, value)
    if not contract.get("target_user") and source_doc.get("type") == "user-story":
        target_user = _extract_as_a_user(text)
        if target_user:
            contract["target_user"] = target_user
    contract["__source_has_cjk_punctuation"] = any(token in text for token in ("；", "：", "，"))
    return contract


def merge_prototype_contract(feature: str, version: str, source_docs: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {
        "feature": feature,
        "version": version,
        "design_sources": [doc["relative_path"] for doc in source_docs],
    }
    for doc in source_docs:
        extracted = extract_prototype_contract_from_source(doc)
        for key, value in extracted.items():
            if value in (None, "", [], {}):
                continue
            if key in _LIST_KEYS and isinstance(value, list) and isinstance(merged.get(key), list):
                merged[key] = [*merged[key], *value]
                continue
            if key == "baseline_protection" and isinstance(value, list) and isinstance(merged.get(key), list):
                merged[key] = [*merged[key], *value]
                continue
            merged[key] = value

    if merged.get("prototype_archetype"):
        merged["prototype_archetype"] = str(merged["prototype_archetype"]).strip().lower()
    if "prototype_mode" in merged:
        merged["prototype_mode"] = str(merged["prototype_mode"]).strip().lower()
    if "coverage_mode" in merged:
        merged["coverage_mode"] = str(merged["coverage_mode"]).strip().lower()
    merged["route_closure_required"] = _normalize_bool(merged.get("route_closure_required"))
    merged["ui_visualization_required"] = _normalize_bool(merged.get("ui_visualization_required"))

    for list_key in _LIST_KEYS:
        if isinstance(merged.get(list_key), list):
            deduped: list[str] = []
            for raw_item in merged.get(list_key, []):
                item = str(raw_item).strip()
                if not item or item in deduped:
                    continue
                deduped.append(item)
            merged[list_key] = deduped

    if isinstance(merged.get("baseline_protection"), list):
        baseline_rows: list[dict[str, Any]] = []
        seen_pages: set[str] = set()
        for item in merged["baseline_protection"]:
            if not isinstance(item, dict):
                continue
            page = slugify_feature(str(item.get("page") or ""))
            if not page:
                continue
            preserve = item.get("preserve")
            if isinstance(preserve, str):
                preserve = _split_list(preserve)
            if not isinstance(preserve, list):
                preserve = []
            if page in seen_pages:
                for existing in baseline_rows:
                    if existing.get("page") != page:
                        continue
                    merged_preserve = [*existing.get("preserve", []), *[str(x).strip() for x in preserve if str(x).strip()]]
                    existing["preserve"] = sorted(set(merged_preserve))
                    break
                continue
            seen_pages.add(page)
            baseline_rows.append(
                {
                    "page": page,
                    "preserve": sorted(set(str(x).strip() for x in preserve if str(x).strip())),
                }
            )
        merged["baseline_protection"] = baseline_rows

    if not merged.get("required_states"):
        merged["required_states"] = list(merged.get("states") or [])
    if not merged.get("required_pages"):
        merged["required_pages"] = [*list(merged.get("navigation") or []), *list(merged.get("sections") or [])]
    if not merged.get("page_inventory"):
        merged["page_inventory"] = list(merged.get("required_pages") or [])
    if not merged.get("coverage_mode"):
        merged["coverage_mode"] = "archetype-sections"
    if not merged.get("prototype_mode"):
        merged["prototype_mode"] = "minimal"

    missing = sorted(
        key for key in _REQUIRED_CONTRACT_KEYS if not merged.get(key)
    )
    if merged.get("prototype_archetype") and merged["prototype_archetype"] not in _ALLOWED_ARCHETYPES:
        raise ValueError(
            "prototype_archetype must be one of: " + ", ".join(sorted(_ALLOWED_ARCHETYPES))
        )
    if missing:
        raise ValueError(
            "Prototype Contract missing required fields: " + ", ".join(missing)
        )
    merged["source_has_cjk_punctuation"] = bool(merged.get("__source_has_cjk_punctuation"))
    merged.pop("__source_has_cjk_punctuation", None)
    return merged


def _feature_requires_route_closure(contract: dict[str, Any]) -> bool:
    return _normalize_bool(contract.get("route_closure_required"))


def _design_governance_enabled(contract: dict[str, Any]) -> bool:
    return _normalize_bool(contract.get("design_governance_required"))


def compile_design_brief(feature: str, contract: dict[str, Any], source_docs: list[dict[str, Any]]) -> dict[str, Any]:
    mood = str(contract.get("theme_mood") or "disciplined").strip().lower() or "disciplined"
    target_user = str(contract.get("target_user") or "product team").strip() or "product team"
    keywords = [str(item).strip() for item in (contract.get("brand_keywords") or []) if str(item).strip()]
    visual_direction = f"{mood} / {str(contract.get('prototype_archetype') or 'reference-pack').strip()}"
    design_governance = _design_governance_enabled(contract)
    design_mode_references = [str(item).strip() for item in (contract.get("design_reference_sources") or []) if str(item).strip()]
    if not design_mode_references and design_governance:
        design_mode_references = [
            "GemDesign-style requirement-to-design generation",
            "Figma-style interactive fidelity and freeze discipline",
        ]
    return {
        "schema_version": "1.0",
        "feature": feature,
        "target_user": target_user,
        "tone": mood,
        "visual_direction": visual_direction,
        "design_generation_mode": str(
            contract.get("design_generation_mode")
            or ("description-as-design" if design_governance else "spec-driven")
        ),
        "interactive_prototype_required": bool(
            contract.get("interactive_prototype_required")
            if contract.get("interactive_prototype_required") is not None
            else design_governance
        ),
        "guidance_anchors": ["frontend-design", "web-design-guidelines"] if design_governance else [],
        "design_mode_references": design_mode_references,
        "typography_intent": "distinctive display with practical body text",
        "color_intent": f"primary-led palette anchored on {contract.get('theme_primary') or '#2563eb'}",
        "motion_intent": "minimal-functional with reduced-motion support",
        "differentiator": keywords[0] if keywords else "delivery-grade reference UI",
        "constraints": [
            "shared token system",
            "accessible interactive states",
            "non-generic aesthetic direction",
        ],
        "source_refs": [doc["relative_path"] for doc in source_docs],
    }


def compile_design_system_contract(
    contract: dict[str, Any],
    theme: dict[str, Any],
    design_brief: dict[str, Any],
) -> dict[str, Any]:
    typography = dict(theme.get("typography") or {})
    return {
        "schema_version": "1.0",
        "design_governance_required": _design_governance_enabled(contract),
        "design_generation_mode": design_brief.get("design_generation_mode"),
        "interactive_prototype_required": bool(design_brief.get("interactive_prototype_required")),
        "guidance_anchors": list(design_brief.get("guidance_anchors") or []),
        "design_mode_references": list(design_brief.get("design_mode_references") or []),
        "visual_direction": design_brief.get("visual_direction"),
        "typography": typography,
        "palette": {
            "primary": theme.get("primary"),
            "secondary": theme.get("secondary"),
            "accent": theme.get("accent"),
        },
        "spacing_scale": theme.get("spacing_scale"),
        "radius_scale": theme.get("radius_scale"),
        "shadow_style": theme.get("shadow_style"),
        "motion": theme.get("motion"),
        "component_rules": [
            "pages must consume shared tokens",
            "focus-visible styling is required",
            "reduced-motion must be honored",
        ],
        "anti_generic_rules": [
            "avoid Inter/Roboto/Arial/system-only default stacks",
            "avoid purple-on-white generic gradients",
            "avoid template-like undifferentiated layouts",
        ],
    }


def compile_design_prompt_artifact(
    *,
    feature: str,
    version: str,
    design_brief: dict[str, Any],
    design_system_contract: dict[str, Any],
    contract: dict[str, Any],
    plan_payload: dict[str, Any],
) -> dict[str, Any]:
    required_pages = [str(item).strip() for item in (plan_payload.get("required_pages") or []) if str(item).strip()]
    required_states = [str(item).strip() for item in (plan_payload.get("required_states") or []) if str(item).strip()]
    archetype = str(contract.get("prototype_archetype") or "reference-pack")
    guidance_anchors = [str(item).strip() for item in (design_brief.get("guidance_anchors") or []) if str(item).strip()]
    design_mode_references = [
        str(item).strip() for item in (design_brief.get("design_mode_references") or []) if str(item).strip()
    ]
    prompt_lines = [
        f"Design a high-fidelity interactive prototype for `{feature}`.",
        f"Mode: {design_brief.get('design_generation_mode')}.",
        f"Audience: {design_brief.get('target_user')}.",
        f"Tone: {design_brief.get('tone')}.",
        f"Visual direction: {design_brief.get('visual_direction')}.",
        f"Prototype archetype: {archetype}.",
        f"Required pages: {', '.join(required_pages) if required_pages else 'none declared'}.",
        f"Required states: {', '.join(required_states) if required_states else 'none declared'}.",
        "Use the shared design system contract and avoid generic AI aesthetics.",
        "Preserve accessibility, visible focus, reduced motion, semantic navigation, and URL-reflected state where applicable.",
    ]
    if design_mode_references:
        prompt_lines.append("Reference mode inspirations: " + "; ".join(design_mode_references) + ".")
    if guidance_anchors:
        prompt_lines.append("Guidance anchors: " + ", ".join(guidance_anchors) + ".")
    return {
        "schema_version": "1.0",
        "feature": feature,
        "version": version,
        "design_generation_mode": design_brief.get("design_generation_mode"),
        "interactive_prototype_required": bool(design_brief.get("interactive_prototype_required")),
        "guidance_anchors": guidance_anchors,
        "design_mode_references": design_mode_references,
        "prompt_sections": {
            "context": {
                "audience": design_brief.get("target_user"),
                "tone": design_brief.get("tone"),
                "visual_direction": design_brief.get("visual_direction"),
                "differentiator": design_brief.get("differentiator"),
            },
            "constraints": list(design_brief.get("constraints") or []),
            "visual_system": {
                "typography": design_system_contract.get("typography", {}),
                "palette": design_system_contract.get("palette", {}),
                "motion": design_system_contract.get("motion"),
                "anti_generic_rules": list(design_system_contract.get("anti_generic_rules") or []),
            },
            "prototype_scope": {
                "archetype": archetype,
                "required_pages": required_pages,
                "required_states": required_states,
                "route_closure_required": bool(contract.get("route_closure_required")),
            },
        },
        "llm_design_prompt": "\n".join(prompt_lines),
    }


def _render_design_prompt_markdown(payload: dict[str, Any]) -> str:
    context = payload.get("prompt_sections", {}).get("context", {}) if isinstance(payload.get("prompt_sections"), dict) else {}
    visual_system = payload.get("prompt_sections", {}).get("visual_system", {}) if isinstance(payload.get("prompt_sections"), dict) else {}
    prototype_scope = payload.get("prompt_sections", {}).get("prototype_scope", {}) if isinstance(payload.get("prompt_sections"), dict) else {}
    return "\n".join(
        [
            f"# Design Prompt: {payload.get('feature')}",
            "",
            f"- version: `{payload.get('version')}`",
            f"- design_generation_mode: `{payload.get('design_generation_mode')}`",
            f"- interactive_prototype_required: `{payload.get('interactive_prototype_required')}`",
            f"- guidance_anchors: `{', '.join(payload.get('guidance_anchors', []))}`",
            f"- design_mode_references: `{'; '.join(payload.get('design_mode_references', []))}`",
            "",
            "## Context",
            f"- audience: `{context.get('audience')}`",
            f"- tone: `{context.get('tone')}`",
            f"- visual_direction: `{context.get('visual_direction')}`",
            f"- differentiator: `{context.get('differentiator')}`",
            "",
            "## Prototype Scope",
            f"- archetype: `{prototype_scope.get('archetype')}`",
            f"- required_pages: `{', '.join(prototype_scope.get('required_pages', []))}`",
            f"- required_states: `{', '.join(prototype_scope.get('required_states', []))}`",
            f"- route_closure_required: `{prototype_scope.get('route_closure_required')}`",
            "",
            "## Visual System",
            f"- typography: `{json.dumps(visual_system.get('typography', {}), ensure_ascii=False)}`",
            f"- palette: `{json.dumps(visual_system.get('palette', {}), ensure_ascii=False)}`",
            f"- motion: `{visual_system.get('motion')}`",
            "",
            "## LLM Design Prompt",
            "",
            payload.get("llm_design_prompt", ""),
            "",
        ]
    ) + "\n"


def compile_ui_style_analysis(
    *,
    feature: str,
    version: str,
    contract: dict[str, Any],
    plan_payload: dict[str, Any],
    design_brief: dict[str, Any],
    design_system_contract: dict[str, Any],
) -> dict[str, Any]:
    page_specs = plan_payload.get("page_specs") if isinstance(plan_payload.get("page_specs"), list) else []
    required_pages = [str(item).strip() for item in (plan_payload.get("required_pages") or []) if str(item).strip()]
    required_states = [str(item).strip() for item in (plan_payload.get("required_states") or []) if str(item).strip()]
    page_links: list[dict[str, Any]] = []
    for spec in page_specs:
        if not isinstance(spec, dict):
            continue
        page_id = slugify_feature(str(spec.get("page_id") or ""))
        if not page_id:
            continue
        page_links.append(
            {
                "page_id": page_id,
                "intent": str(spec.get("intent") or ""),
                "path": f"pages/{page_id}.html",
                "state_paths": [f"states/{page_id}--{slugify_feature(state)}.html" for state in required_states],
            }
        )
    secondary_build_rules = [
        "analyze existing shared tokens and interaction patterns before extending pages",
        "preserve the unified prototype directory as the navigation source of truth",
        "extend via design-brief and design-system contract, not ad-hoc page-local styling",
        "route design/security findings back through review before freeze",
    ]
    return {
        "schema_version": "1.0",
        "feature": feature,
        "version": version,
        "analysis_mode": "design-governed-prototype",
        "directory_contract": {
            "directory_page": "index.html",
            "landing_kind": "reference-pack-directory",
            "required_pages": required_pages,
            "required_states": required_states,
            "page_links": page_links,
        },
        "visual_system": {
            "tone": design_brief.get("tone"),
            "visual_direction": design_brief.get("visual_direction"),
            "differentiator": design_brief.get("differentiator"),
            "guidance_anchors": list(design_brief.get("guidance_anchors") or []),
            "design_mode_references": list(design_brief.get("design_mode_references") or []),
            "typography": design_system_contract.get("typography", {}),
            "palette": design_system_contract.get("palette", {}),
            "motion": design_system_contract.get("motion"),
            "anti_generic_rules": list(design_system_contract.get("anti_generic_rules") or []),
        },
        "component_patterns": {
            "navigation": list(contract.get("navigation") or []),
            "primary_cta": str(contract.get("primary_cta") or ""),
            "secondary_cta": str(contract.get("secondary_cta") or ""),
            "states": list(contract.get("states") or []),
            "surface_style": str(contract.get("surface_style") or ""),
        },
        "secondary_build_contract": {
            "source_refs": list(plan_payload.get("source_refs") or []),
            "required_artifacts": [
                "prototype-plan.json",
                "design-brief.json",
                "design-system-contract.json",
                "design-prompt.json",
                "ui-style-analysis.json",
                "tokens.css",
                "navigation-map.json",
                "interaction-map.json",
                "index.html",
            ],
            "extension_rules": secondary_build_rules,
        },
    }


def _render_ui_style_analysis_markdown(payload: dict[str, Any]) -> str:
    directory_contract = payload.get("directory_contract", {}) if isinstance(payload.get("directory_contract"), dict) else {}
    visual_system = payload.get("visual_system", {}) if isinstance(payload.get("visual_system"), dict) else {}
    secondary_build_contract = (
        payload.get("secondary_build_contract", {})
        if isinstance(payload.get("secondary_build_contract"), dict)
        else {}
    )
    component_patterns = payload.get("component_patterns", {}) if isinstance(payload.get("component_patterns"), dict) else {}
    lines = [
        f"# UI Style Analysis: {payload.get('feature')}",
        "",
        f"- version: `{payload.get('version')}`",
        f"- analysis_mode: `{payload.get('analysis_mode')}`",
        "",
        "## Unified Directory",
        f"- directory_page: `{directory_contract.get('directory_page')}`",
        f"- landing_kind: `{directory_contract.get('landing_kind')}`",
        f"- required_pages: `{', '.join(directory_contract.get('required_pages', []))}`",
        f"- required_states: `{', '.join(directory_contract.get('required_states', []))}`",
        "",
        "## Visual System",
        f"- tone: `{visual_system.get('tone')}`",
        f"- visual_direction: `{visual_system.get('visual_direction')}`",
        f"- differentiator: `{visual_system.get('differentiator')}`",
        f"- typography: `{json.dumps(visual_system.get('typography', {}), ensure_ascii=False)}`",
        f"- palette: `{json.dumps(visual_system.get('palette', {}), ensure_ascii=False)}`",
        f"- motion: `{visual_system.get('motion')}`",
        "",
        "## Component Patterns",
        f"- navigation: `{', '.join(component_patterns.get('navigation', []))}`",
        f"- primary_cta: `{component_patterns.get('primary_cta')}`",
        f"- secondary_cta: `{component_patterns.get('secondary_cta')}`",
        f"- states: `{', '.join(component_patterns.get('states', []))}`",
        "",
        "## Secondary Build Contract",
        f"- source_refs: `{', '.join(secondary_build_contract.get('source_refs', []))}`",
        f"- required_artifacts: `{', '.join(secondary_build_contract.get('required_artifacts', []))}`",
        "",
        "## Extension Rules",
    ]
    rules = secondary_build_contract.get("extension_rules", [])
    if isinstance(rules, list) and rules:
        for rule in rules:
            lines.append(f"- {rule}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def derive_theme_tokens(contract: dict[str, Any]) -> dict[str, Any]:
    primary = str(contract.get("theme_primary", "#3b82f6"))
    secondary = str(contract.get("theme_secondary", "#0f172a"))
    mood = str(contract.get("theme_mood", "confident"))
    archetype = str(contract.get("prototype_archetype", "dashboard"))
    spacing = "4-8-12-16-24-32" if archetype in {"dashboard", "admin-workbench"} else "8-12-16-24-32-48"
    radius = "14/18/24" if archetype == "marketing-page" else "10/14/18"
    shadow = "soft-elevation" if mood in {"warm", "premium"} else "disciplined-elevation"
    motion = "minimal-functional"
    font_preset = _DESIGN_FONT_PRESETS.get(mood, _DESIGN_FONT_PRESETS["disciplined"])
    return {
        "primary": primary,
        "secondary": secondary,
        "accent": primary,
        "mood": mood,
        "surface_style": contract.get("surface_style", "elevated-clean"),
        "brand_keywords": contract.get("brand_keywords", []),
        "typography": {
            "display": font_preset["display"],
            "body": font_preset["body"],
            "mono": font_preset["mono"],
            "scale": [48, 32, 24, 18, 16, 14, 12],
        },
        "spacing_scale": spacing,
        "radius_scale": radius,
        "shadow_style": shadow,
        "motion": motion,
        "light_dark_strategy": "light-first with dark-compatible tokens",
    }


def derive_navigation_map(contract: dict[str, Any]) -> dict[str, Any]:
    sections = contract.get("sections", [])
    navigation = contract.get("navigation", [])
    jumps = contract.get("jump_map", [])
    return {
        "primary_entry": contract.get("primary_entry"),
        "primary_exit": contract.get("primary_exit"),
        "sections": [{"id": slugify_feature(name), "label": name} for name in sections],
        "navigation_nodes": [{"label": name, "target": f"#{slugify_feature(name)}"} for name in navigation],
        "jump_map": jumps,
    }


def derive_interaction_map(contract: dict[str, Any]) -> dict[str, Any]:
    primary_cta = str(contract.get("primary_cta", "")).strip()
    secondary_cta = str(contract.get("secondary_cta", "")).strip()
    interactions: dict[str, Any] = {
        "ctas": [{"label": primary_cta, "kind": "primary"}],
        "states": contract.get("states", []),
        "jump_map": contract.get("jump_map", []),
        "modal_map": contract.get("modal_map", []),
        "drawer_map": contract.get("drawer_map", []),
        "tab_map": contract.get("tab_map", []),
        "form_actions": [{"label": primary_cta, "action": contract.get("primary_exit")}],
    }
    if secondary_cta:
        interactions["ctas"].append({"label": secondary_cta, "kind": "secondary"})
    return interactions


def _surface_id_from_target(target: str) -> str:
    text = str(target or "").strip()
    if text.startswith("#"):
        text = text[1:]
    return slugify_feature(text)


def derive_route_closure_contract(
    feature: str,
    version: str,
    contract: dict[str, Any],
    navigation_map: dict[str, Any],
    interaction_map: dict[str, Any],
) -> dict[str, Any]:
    surfaces: list[dict[str, Any]] = []
    seen_surfaces: set[str] = set()
    for section in navigation_map.get("sections", []):
        if not isinstance(section, dict):
            continue
        surface_id = str(section.get("id") or "").strip()
        if not surface_id or surface_id in seen_surfaces:
            continue
        seen_surfaces.add(surface_id)
        surfaces.append(
            {
                "surface_id": surface_id,
                "label": str(section.get("label") or surface_id),
                "entry_kind": "page",
                "mounted_required": True,
            }
        )

    cases: list[dict[str, Any]] = []
    index = 0
    for node in navigation_map.get("navigation_nodes", []):
        if not isinstance(node, dict):
            continue
        index += 1
        cases.append(
            {
                "case_id": f"RC-{index:03d}",
                "source_type": "page-jump",
                "source_label": str(node.get("label") or ""),
                "target_surface_id": _surface_id_from_target(str(node.get("target") or "")),
                "target_type": "page",
                "required_context": [],
                "fallback_behavior": "block",
            }
        )
    for jump in interaction_map.get("jump_map", []):
        if not isinstance(jump, dict):
            continue
        index += 1
        cases.append(
            {
                "case_id": f"RC-{index:03d}",
                "source_type": "button-jump",
                "source_label": str(jump.get("from") or ""),
                "target_surface_id": _surface_id_from_target(str(jump.get("to") or "")),
                "target_type": "page",
                "required_context": [],
                "fallback_behavior": "block",
            }
        )
    for raw_tab in interaction_map.get("tab_map", []):
        if isinstance(raw_tab, dict):
            label = str(raw_tab.get("label") or raw_tab.get("target") or "").strip()
        else:
            label = str(raw_tab or "").strip()
        if not label:
            continue
        index += 1
        cases.append(
            {
                "case_id": f"RC-{index:03d}",
                "source_type": "tab-jump",
                "source_label": label,
                "target_surface_id": _surface_id_from_target(label),
                "target_type": "tab",
                "required_context": ["tab"],
                "fallback_behavior": "safe-fallback",
            }
        )
    for cta in interaction_map.get("ctas", []):
        if not isinstance(cta, dict):
            continue
        label = str(cta.get("label") or "").strip()
        if not label:
            continue
        index += 1
        cases.append(
            {
                "case_id": f"RC-{index:03d}",
                "source_type": "cta",
                "source_label": label,
                "target_surface_id": _surface_id_from_target(str(contract.get("primary_exit") or contract.get("primary_entry") or "")),
                "target_type": "page",
                "required_context": [],
                "fallback_behavior": "block",
            }
        )
    return {
        "schema_version": "1.0",
        "feature": feature,
        "version": version,
        "required": _feature_requires_route_closure(contract),
        "drift_guardrails": contract.get(
            "drift_guardrails",
            ["isolated-page", "fragile-route", "legacy-only-entry", "fake-jump", "tab-route-drift", "param-contract-mismatch"],
        ),
        "surfaces": surfaces,
        "closure_cases": cases,
    }


def derive_implementation_map(feature: str, version: str, route_closure_contract: dict[str, Any]) -> dict[str, Any]:
    surfaces = route_closure_contract.get("surfaces") if isinstance(route_closure_contract.get("surfaces"), list) else []
    closure_cases = route_closure_contract.get("closure_cases") if isinstance(route_closure_contract.get("closure_cases"), list) else []
    return {
        "schema_version": "1.0",
        "feature": feature,
        "version": version,
        "baseline_id": "draft",
        "adapter": "unbound",
        "binding_status": "draft",
        "surfaces": [
            {
                "surface_id": str(item.get("surface_id") or ""),
                "implementation_type": "unknown",
                "runtime_entry": "",
                "route_or_url": "",
                "code_paths": [],
                "selectors": [],
                "state_hooks": [],
                "theme_binding": "",
                "interaction_binding": "",
                "evidence_capture_plan": [],
                "mounted": True,
            }
            for item in surfaces
            if isinstance(item, dict)
        ],
        "closure_bindings": [
            {
                "case_id": str(item.get("case_id") or ""),
                "binding_status": "unbound",
                "runtime_target": "",
                "state_target": "",
                "context_contract": list(item.get("required_context") or []),
                "drift_status": "unknown",
            }
            for item in closure_cases
            if isinstance(item, dict)
        ],
    }


def _version_tuple(version: str) -> tuple[int, int, int]:
    raw = str(version or "").strip().lstrip("v")
    parts = raw.split(".")
    values: list[int] = []
    for part in parts[:3]:
        try:
            values.append(int(part))
        except ValueError:
            values.append(0)
    while len(values) < 3:
        values.append(0)
    return values[0], values[1], values[2]


def _is_reference_pack_v2(contract: dict[str, Any], version: str) -> bool:
    mode = str(contract.get("prototype_mode") or "").strip().lower()
    if mode == "reference-pack-v2":
        return True
    if _version_tuple(version) >= (1, 1, 11):
        return bool(
            str(contract.get("coverage_mode") or "").strip()
            or contract.get("required_pages")
            or contract.get("required_states")
            or contract.get("baseline_protection")
        )
    return False


def _resolve_required_pages(contract: dict[str, Any], navigation_map: dict[str, Any], interaction_map: dict[str, Any]) -> list[str]:
    page_ids: list[str] = []
    explicit_keys = ("required_pages", "page_inventory")
    fallback_keys = ("navigation", "sections")
    explicit_found = False
    for key in explicit_keys:
        value = contract.get(key)
        if isinstance(value, list):
            for raw in value:
                page = slugify_feature(str(raw))
                if page and page not in page_ids:
                    page_ids.append(page)
                    explicit_found = True
    if not explicit_found:
        for key in fallback_keys:
            value = contract.get(key)
            if isinstance(value, list):
                for raw in value:
                    page = slugify_feature(str(raw))
                    if page and page not in page_ids:
                        page_ids.append(page)
    if explicit_found:
        return page_ids
    for node in navigation_map.get("navigation_nodes", []):
        if not isinstance(node, dict):
            continue
        target = _surface_id_from_target(str(node.get("target") or ""))
        if target and target not in page_ids:
            page_ids.append(target)
    coverage_mode = str(contract.get("coverage_mode") or "").strip().lower()
    if coverage_mode == "all-existing-routes":
        for jump in interaction_map.get("jump_map", []):
            if not isinstance(jump, dict):
                continue
            for key in ("from", "to"):
                target = _surface_id_from_target(str(jump.get(key) or ""))
                if target and target not in page_ids:
                    page_ids.append(target)
        for key in ("primary_entry", "primary_exit"):
            target = _surface_id_from_target(str(contract.get(key) or ""))
            if target and target not in page_ids:
                page_ids.append(target)
    return page_ids


def _baseline_map(contract: dict[str, Any]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    rows = contract.get("baseline_protection")
    if not isinstance(rows, list):
        return out
    for row in rows:
        if isinstance(row, str):
            page = slugify_feature(row)
            if page:
                out[page] = ["structure", "cta", "hierarchy"]
            continue
        if not isinstance(row, dict):
            continue
        page = slugify_feature(str(row.get("page") or ""))
        if not page:
            continue
        preserve = row.get("preserve")
        if isinstance(preserve, str):
            preserve = _split_list(preserve)
        if not isinstance(preserve, list):
            preserve = []
        out[page] = sorted(set(str(item).strip() for item in preserve if str(item).strip()))
    return out


def _derive_page_content_model(page_id: str, contract: dict[str, Any], baseline_by_page: dict[str, list[str]]) -> dict[str, Any]:
    title = _title_case_page(page_id)
    primary_cta = str(contract.get("primary_cta") or "Continue")
    secondary_cta = str(contract.get("secondary_cta") or "Details")
    model: dict[str, Any] = {
        "variant": "reference",
        "headline": title,
        "subheadline": f"{title} reference page",
        "primary_cta": primary_cta,
        "secondary_cta": secondary_cta,
        "baseline_guardrails": list(baseline_by_page.get(page_id) or []),
    }
    if page_id == "home":
        model.update(
            {
                "variant": "dashboard-home",
                "subheadline": "赛事创建、加入比赛、进行中运营与工具入口统一收口。",
                "kpis": [
                    {"label": "进行中", "value": "6"},
                    {"label": "待处理", "value": "2"},
                    {"label": "近7天", "value": "18 场"},
                ],
                "cards": [
                    {"title": "当前比赛", "body": "周末双打友谊赛 · 16 人 · 第 3 轮"},
                    {"title": "创建比赛", "body": "智能推荐"},
                    {"title": "加入比赛", "body": "邀请码 / 扫码"},
                    {"title": "球费工具", "body": "实时均摊"},
                ],
                "truth_notes": [
                    "首页首屏需要主动作、当前比赛、工具区和可信状态。",
                    "未登录受保护入口必须走 login + redirect。",
                ],
            }
        )
    elif page_id == "game-detail":
        model.update(
            {
                "variant": "match-hub",
                "subheadline": "对阵、排名、选手、设置与赛事动作在这里聚合。",
                "tabs": ["Matches", "Ranking", "Players", "Settings", "Teams"],
                "matches": [
                    {"left": "李雷 / 韩梅梅", "right": "王强 / 周宁", "score": "21 : 18", "status": "已完成"},
                    {"left": "陈一 / 赵二", "right": "刘八 / 吴九", "score": "17 : 14", "status": "进行中"},
                ],
                "truth_notes": [
                    "game-detail 必须消费 tab 参数，落到确定子态。",
                    "详情页是运营中枢，主 CTA 应引导记分和查看排名。",
                ],
            }
        )
    elif page_id == "spectator":
        model.update(
            {
                "variant": "spectator-board",
                "subheadline": "自动更新比分看板，保留上一帧结果并支持手动刷新。",
                "kpis": [
                    {"label": "当前场次", "value": "4 / 12"},
                    {"label": "已完成", "value": "8 场"},
                    {"label": "刷新状态", "value": "live-update"},
                ],
                "cards": [
                    {"title": "排行榜", "body": "李雷 78 分 · 韩梅梅 74 分 · 王强 70 分"},
                    {"title": "Court A", "body": "21:18"},
                    {"title": "Court B", "body": "17:14"},
                    {"title": "Court C", "body": "待开始"},
                ],
                "truth_notes": [
                    "观战页只表达比分看板自动更新闭环。",
                    "需要空态、加载态、刷新失败态三类状态页。",
                ],
            }
        )
    elif page_id == "rankings":
        model.update(
            {
                "variant": "rankings-podium",
                "subheadline": "名次层级、胜率、积分与最近战绩一屏对比。",
                "podium": [
                    {"rank": "#2", "name": "韩梅梅", "value": "74 分"},
                    {"rank": "#1", "name": "李雷", "value": "78 分"},
                    {"rank": "#3", "name": "王强", "value": "70 分"},
                ],
                "rows": [
                    {"label": "第4名 陈一", "value": "66 分"},
                    {"label": "第5名 赵二", "value": "61 分"},
                    {"label": "第6名 孙七", "value": "58 分"},
                ],
                "truth_notes": [
                    "前三名需要有 podium 层级。",
                    "当前用户需要支持高亮和“我”标签。",
                ],
            }
        )
    elif page_id in {"mine", "my-stats", "my-honors"}:
        model.update(
            {
                "variant": "profile-results",
                "subheadline": "个人成绩、荣誉归档与设置任务合并到结果页体验。",
                "profile": {"name": "阿福", "meta": "本周 8 场 · 胜率 75%"},
                "kpis": [
                    {"label": "总场次", "value": "124"},
                    {"label": "总胜率", "value": "68%"},
                    {"label": "奖牌数", "value": "12"},
                ],
                "truth_notes": [
                    "my-honors 必须以当前登录用户为唯一上下文取数。",
                ],
            }
        )
        if page_id == "mine":
            model["subheadline"] = "个人中心负责收口资料、成绩、荣誉、设置和帮助入口。"
            model["quick_links"] = ["我的战绩", "我的荣誉", "设置", "帮助与反馈"]
        elif page_id == "my-stats":
            model["subheadline"] = "战绩页应优先展示总场次、胜率、近期状态和常用赛制表现。"
            model["trend"] = ["近 5 场 4 胜 1 负", "双打胜率 72%", "本月参赛 8 场"]
        elif page_id == "my-honors":
            model["subheadline"] = "荣誉页应突出冠军卡、奖牌计数和当前用户真实获奖记录。"
            model["medals"] = [
                {"label": "冠军", "value": "5"},
                {"label": "亚军", "value": "4"},
                {"label": "季军", "value": "3"},
            ]
        if page_id == "mine":
            model["subheadline"] = "个人中心负责收口资料、成绩、荣誉、设置和帮助入口。"
            model["quick_links"] = ["我的战绩", "我的荣誉", "设置", "帮助与反馈"]
        elif page_id == "my-stats":
            model["subheadline"] = "战绩页应把总场次、胜率、近期状态和常用赛制表现优先展示。"
            model["trend"] = ["近 5 场 4 胜 1 负", "双打胜率 72%", "本月参赛 8 场"]
        elif page_id == "my-honors":
            model["subheadline"] = "荣誉页应突出奖牌、冠军卡和当前用户的真实获奖记录。"
            model["medals"] = [
                {"label": "冠军", "value": "5"},
                {"label": "亚军", "value": "4"},
                {"label": "季军", "value": "3"},
            ]
    elif page_id == "fee-calculator":
        model.update(
            {
                "variant": "tool-calculator",
                "subheadline": "费用模式切换、人均金额与复制结果一屏完成。",
                "rows": [
                    {"label": "总费用", "value": "¥ 368"},
                    {"label": "参与人数", "value": "16"},
                    {"label": "人均费用", "value": "¥ 23"},
                ],
                "truth_notes": [
                    "球费计算器应突出结论，而不是堆叠输入项。",
                ],
            }
        )
    elif page_id == "edit-profile":
        model.update(
            {
                "variant": "profile-editor",
                "subheadline": "资料编辑页要强调头像、昵称、城市、惯用手等关键字段，而不是普通后台表单。",
                "rows": [
                    {"label": "头像", "value": "已设置"},
                    {"label": "昵称", "value": "阿福"},
                    {"label": "惯用手", "value": "右手"},
                    {"label": "城市", "value": "杭州"},
                ],
            }
        )
    elif page_id in {"login", "register"}:
        model.update(
            {
                "variant": "auth-entry",
                "subheadline": "登录成功后应回跳原目标页，注册与登录保持同一视觉语义。",
                "rows": [
                    {"label": "主入口", "value": "微信快捷登录"},
                    {"label": "备用方案", "value": "账号注册 / 登录"},
                    {"label": "回跳策略", "value": "redirect target"},
                ],
                "truth_notes": [
                    "受保护路由统一登录回跳是用户故事显式要求。",
                ],
            }
        )
    elif page_id in {"player-detail"}:
        model.update(
            {
                "variant": "detail-focus",
                "subheadline": "关键详情页要聚焦单一任务，不做后台式信息堆砌。",
                "rows": [
                    {"label": "核心对象", "value": title},
                    {"label": "关键动作", "value": primary_cta},
                    {"label": "辅助动作", "value": secondary_cta},
                ],
            }
        )
    elif page_id in {"score-entry", "batch-score-entry"}:
        model.update(
            {
                "variant": "score-entry-board",
                "subheadline": "比分录入页要突出当前对阵、比分状态和提交动作。",
                "matches": [
                    {"left": "李雷 / 韩梅梅", "right": "王强 / 周宁", "score": "19 : 17", "status": "第 2 局"},
                    {"left": "陈一 / 赵二", "right": "刘八 / 吴九", "score": "15 : 12", "status": "第 1 局"},
                ],
                "rows": [
                    {"label": "录入模式", "value": "单场 / 批量"},
                    {"label": "待提交", "value": "2 场"},
                    {"label": "下一步", "value": "提交并刷新排行"},
                ],
            }
        )
    elif page_id == "create-team-game":
        model.update(
            {
                "variant": "team-game-flow",
                "subheadline": "团体赛建赛页要强调阵营配置、人数、赛制和后续管理动作。",
                "steps": ["选择模板", "设置阵营", "确认赛制"],
                "rows": [
                    {"label": "阵营数", "value": "2 队"},
                    {"label": "每队人数", "value": "8"},
                    {"label": "下一步", "value": "进入 team-management"},
                ],
            }
        )
    elif page_id in {"scenario-selection", "mode-selection", "add-participants", "preview-matchups", "join-game", "bind-users"}:
        model.update(
            {
                "variant": "flow-step",
                "subheadline": "建赛与报名链路的关键步骤页，强调下一步动作。",
                "steps": ["选择场景", "配置模式", "添加参赛者"],
                "rows": [
                    {"label": "当前选择", "value": title},
                    {"label": "推荐配置", "value": "16 人 / 双打循环"},
                    {"label": "下一步", "value": "预览排阵"},
                ],
            }
        )
        if page_id == "add-participants":
            model["rows"] = [
                {"label": "已添加", "value": "12 / 16"},
                {"label": "游客待绑定", "value": "3"},
                {"label": "下一步", "value": "预览排阵"},
            ]
        elif page_id == "preview-matchups":
            model["rows"] = [
                {"label": "轮次数", "value": "5 轮"},
                {"label": "冲突检测", "value": "0"},
                {"label": "下一步", "value": "进入比赛详情"},
            ]
        elif page_id == "join-game":
            model["rows"] = [
                {"label": "加入方式", "value": "扫码 / 邀请码"},
                {"label": "身份状态", "value": "未登录则回跳"},
                {"label": "成功后", "value": "进入详情页"},
            ]
        elif page_id == "bind-users":
            model["rows"] = [
                {"label": "待绑定人数", "value": "3"},
                {"label": "推荐动作", "value": "搜索并绑定实名"},
                {"label": "成功后", "value": "统计自动归档"},
            ]
    elif page_id.startswith("club") or page_id.startswith("team") or page_id in {"stage-management", "group-management", "promotion-settings", "awards", "tournament-list", "bracket"}:
        model.update(
            {
                "variant": "operations-board",
                "subheadline": "管理型页面采用任务面板 + 列表卡片结构，不再是纯文字占位。",
                "rows": [
                    {"label": "今日待办", "value": "3 项待确认"},
                    {"label": "主要列表", "value": "12 条"},
                    {"label": "状态", "value": "in-progress"},
                ],
            }
        )
        if page_id == "tournament-list":
            model["variant"] = "tournament-list-board"
            model["rows"] = [
                {"label": "进行中", "value": "4 场"},
                {"label": "待开始", "value": "2 场"},
                {"label": "收藏", "value": "6 场"},
            ]
        elif page_id == "bracket":
            model["variant"] = "bracket-board"
            model["rows"] = [
                {"label": "当前轮次", "value": "半决赛"},
                {"label": "可录比分", "value": "2 场"},
                {"label": "下一步", "value": "进入 score-entry"},
            ]
        elif page_id == "awards":
            model["variant"] = "awards-board"
            model["rows"] = [
                {"label": "奖项配置", "value": "3 项"},
                {"label": "已确认", "value": "2 项"},
                {"label": "待操作", "value": "补冠军海报"},
            ]
        elif page_id in {"stage-management", "group-management", "promotion-settings"}:
            model["variant"] = "competition-config-board"
            if page_id == "stage-management":
                model["rows"] = [
                    {"label": "当前阶段", "value": "小组赛 / 半决赛"},
                    {"label": "活跃阶段", "value": "2"},
                    {"label": "上下文", "value": "stageId + tournamentId"},
                ]
                model["panels"] = ["阶段时间线", "阶段切换", "阶段状态"]
            elif page_id == "group-management":
                model["rows"] = [
                    {"label": "当前分组", "value": "A / B / C / D"},
                    {"label": "待确认", "value": "2 个空位"},
                    {"label": "上下文", "value": "stageId + tournamentId"},
                ]
                model["panels"] = ["分组名单", "种子位", "冲突提示"]
            else:
                model["rows"] = [
                    {"label": "晋级规则", "value": "前 2 名出线"},
                    {"label": "待确认", "value": "3 项规则"},
                    {"label": "上下文", "value": "stageId + tournamentId"},
                ]
                model["panels"] = ["出线规则", "加赛条件", "回退策略"]
        elif page_id in {"team-management", "team-stats"}:
            model["variant"] = "team-ops-board"
            if page_id == "team-management":
                model["rows"] = [
                    {"label": "阵营数", "value": "2 队"},
                    {"label": "待调整", "value": "3 人"},
                    {"label": "队长状态", "value": "2 位已确认"},
                ]
                model["panels"] = ["阵容分配", "待调换成员", "队长设置"]
            else:
                model["rows"] = [
                    {"label": "阵营数", "value": "2 队"},
                    {"label": "统计更新", "value": "最近 1 分钟"},
                    {"label": "主指标", "value": "净胜分 / 胜场"},
                ]
                model["panels"] = ["阵营 KPI", "近期走势", "对比排行"]
        elif page_id.startswith("club"):
            if page_id == "club-list":
                model["variant"] = "club-list-board"
                model["rows"] = [
                    {"label": "俱乐部数", "value": "8"},
                    {"label": "活跃赛事", "value": "5"},
                    {"label": "待审批", "value": "5"},
                ]
            elif page_id == "club-detail":
                model["variant"] = "club-detail-board"
                model["rows"] = [
                    {"label": "俱乐部名称", "value": "羽球营地杭州站"},
                    {"label": "成员总数", "value": "126"},
                    {"label": "近期比赛", "value": "12 场"},
                ]
            elif page_id == "club-members":
                model["variant"] = "club-members-board"
                model["rows"] = [
                    {"label": "正式成员", "value": "98"},
                    {"label": "待审批", "value": "5"},
                    {"label": "最近加入", "value": "3 人"},
                ]
            else:
                model["variant"] = "club-create-board"
                model["rows"] = [
                    {"label": "基础信息", "value": "名称 / 城市 / 公告"},
                    {"label": "创建目标", "value": "建立俱乐部主页"},
                    {"label": "后续动作", "value": "邀请成员加入"},
                ]
    elif page_id in {"help", "rules-wiki", "rule-detail", "settings", "coming-soon"}:
        model.update(
            {
                "variant": "support-center",
                "subheadline": "帮助、设置与规则页应该像服务中心，而不是静态说明区。",
                "rows": [
                    {"label": "热门问题", "value": "6"},
                    {"label": "快捷动作", "value": "联系客服 / 提交反馈"},
                    {"label": "当前状态", "value": "ready-for-freeze"},
                ],
            }
        )
        if page_id == "help":
            model["rows"] = [
                {"label": "热门问题", "value": "6"},
                {"label": "快捷动作", "value": "联系客服 / 提交反馈"},
                {"label": "当前状态", "value": "ready-for-freeze"},
            ]
            model["panels"] = ["账号问题", "比赛问题", "反馈记录"]
        elif page_id == "rules-wiki":
            model["rows"] = [
                {"label": "规则分类", "value": "4"},
                {"label": "推荐阅读", "value": "双打轮转 / 晋级规则"},
                {"label": "当前状态", "value": "ready-for-freeze"},
            ]
            model["panels"] = ["规则目录", "高频规则", "最近更新"]
        elif page_id == "rule-detail":
            model["rows"] = [
                {"label": "当前规则", "value": "双打轮转"},
                {"label": "示例局面", "value": "3 个"},
                {"label": "当前状态", "value": "ready-for-freeze"},
            ]
            model["panels"] = ["规则摘要", "示例说明", "相关 FAQ"]
        elif page_id == "settings":
            model["rows"] = [
                {"label": "视觉模式", "value": "浅雾蓝紫"},
                {"label": "消息通知", "value": "已开启"},
                {"label": "当前状态", "value": "ready-for-freeze"},
            ]
            model["panels"] = ["主题设置", "通知偏好", "账号安全"]
        elif page_id == "coming-soon":
            model["rows"] = [
                {"label": "即将上线", "value": "积分商城 / 约球群"},
                {"label": "可登记", "value": "预约提醒"},
                {"label": "当前状态", "value": "planning"},
            ]
            model["panels"] = ["路线图", "预约提醒", "反馈投票"]
        if page_id == "help":
            model["rows"] = [
                {"label": "热门问题", "value": "6"},
                {"label": "快捷动作", "value": "联系客服 / 提交反馈"},
                {"label": "当前状态", "value": "ready-for-freeze"},
            ]
            model["panels"] = ["账号问题", "比赛问题", "反馈记录"]
        elif page_id == "rules-wiki":
            model["rows"] = [
                {"label": "规则分类", "value": "4"},
                {"label": "推荐阅读", "value": "双打轮转 / 晋级规则"},
                {"label": "当前状态", "value": "ready-for-freeze"},
            ]
            model["panels"] = ["规则目录", "高频规则", "最近更新"]
        elif page_id == "rule-detail":
            model["rows"] = [
                {"label": "当前规则", "value": "双打轮转"},
                {"label": "示例局面", "value": "3 个"},
                {"label": "当前状态", "value": "ready-for-freeze"},
            ]
            model["panels"] = ["规则摘要", "示例说明", "相关 FAQ"]
        elif page_id == "settings":
            model["rows"] = [
                {"label": "视觉模式", "value": "浅雾蓝紫"},
                {"label": "消息通知", "value": "已开启"},
                {"label": "当前状态", "value": "ready-for-freeze"},
            ]
            model["panels"] = ["主题设置", "通知偏好", "账号安全"]
        elif page_id == "coming-soon":
            model["rows"] = [
                {"label": "即将上线", "value": "积分商城 / 约球群"},
                {"label": "可登记", "value": "预约提醒"},
                {"label": "当前状态", "value": "planning"},
            ]
            model["panels"] = ["路线图", "预约提醒", "反馈投票"]
    elif page_id in {"closure", "components", "interaction-flows", "overview", "visual-language"}:
        model.update(
            {
                "variant": "design-reference",
                "subheadline": "该页用于沉淀设计原则、组件复用、交互闭环和视觉系统，而不是空白文档页。",
                "rows": [
                    {"label": "页面类型", "value": "Design Reference"},
                    {"label": "主要用途", "value": "支持评审、实现和验收对齐"},
                    {"label": "当前状态", "value": "ready-for-freeze"},
                ],
            }
        )
    elif page_id in {"detail-tabs", "spectator-focus", "hi-fi-prototype", "screens", "status-flow", "inventory"}:
        model.update(
            {
                "variant": "gallery-reference",
                "subheadline": "该页面用于承接原型簇、状态簇或页面目录，服务评审和实施交接。",
                "rows": [
                    {"label": "页面类型", "value": "Gallery / Directory"},
                    {"label": "主要目标", "value": "聚合多页原型入口"},
                    {"label": "当前状态", "value": "ready-for-freeze"},
                ],
            }
        )
    elif page_id == "next-steps":
        model.update(
            {
                "variant": "next-actions",
                "subheadline": "收口当前原型评审、冻结、实现对接和 QA 行动。",
                "rows": [
                    {"label": "立即动作", "value": "冻结当前原型基线"},
                    {"label": "后续动作", "value": "进入实现与视觉验收"},
                    {"label": "风险提示", "value": "避免页面语义再次退化"},
                ],
            }
        )
    elif page_id in {"help", "rules-wiki", "rule-detail", "settings", "coming-soon", "css-config", "audit", "coverage-matrix", "next-steps", "components", "visual-language", "interaction-flows", "closure", "overview", "batch-a-gallery", "batch-b-gallery", "batch-c-gallery"}:
        model.update(
            {
                "variant": "content-reference",
                "subheadline": "说明文档、规则说明与交互盘点通过信息卡片方式组织。",
                "rows": [
                    {"label": "页面类型", "value": "文档 / 规则 / 配置"},
                    {"label": "当前状态", "value": "ready-for-freeze"},
                    {"label": "主要目标", "value": "支持评审与实现对齐"},
                ],
            }
        )
    return model


def compile_prototype_plan(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    source_docs = load_source_documents(project_root, version, feature)
    if not source_docs:
        raise FileNotFoundError(
            f"No source documents found for '{feature}'. Expected at least one of: "
            + ", ".join(str(path) for path in source_doc_paths(project_root, version, feature).values())
        )
    contract = merge_prototype_contract(feature, version, source_docs)
    theme = derive_theme_tokens(contract)
    navigation_map = derive_navigation_map(contract)
    interaction_map = derive_interaction_map(contract)
    reference_pack_v2 = _is_reference_pack_v2(contract, version)
    required_pages = _resolve_required_pages(contract, navigation_map, interaction_map)
    required_states = list(contract.get("required_states") or contract.get("states") or [])
    if not required_states:
        required_states = ["default"]
    baseline_by_page = _baseline_map(contract)
    page_specs: list[dict[str, Any]] = []
    for page_id in required_pages:
        route_targets: list[str] = []
        for jump in interaction_map.get("jump_map", []):
            if not isinstance(jump, dict):
                continue
            target = _surface_id_from_target(str(jump.get("to") or ""))
            if target and target not in route_targets:
                route_targets.append(target)
        route_targets.extend([target for target in [_surface_id_from_target(str(contract.get("primary_exit") or ""))] if target and target not in route_targets])
        content_model = _derive_page_content_model(page_id, contract, baseline_by_page)
        truth_notes = [f"compiled_from:{','.join(contract.get('design_sources', []))}"]
        truth_notes.extend(str(item) for item in (content_model.get("truth_notes") or []) if str(item).strip())
        page_specs.append(
            {
                "page_id": page_id,
                "intent": str(content_model.get("subheadline") or f"{page_id.replace('-', ' ').title()} reference page"),
                "layout_type": str(contract.get("prototype_archetype") or "dashboard"),
                "sections": list(contract.get("sections") or []),
                "components": ["header", "content", "primary-cta"],
                "primary_cta": str(content_model.get("primary_cta") or contract.get("primary_cta") or ""),
                "secondary_ctas": [str(content_model.get("secondary_cta") or contract.get("secondary_cta") or "")] if str(content_model.get("secondary_cta") or contract.get("secondary_cta") or "").strip() else [],
                "states": required_states,
                "route_targets": route_targets,
                "truth_notes": truth_notes,
                "baseline_guardrails": list(content_model.get("baseline_guardrails") or baseline_by_page.get(page_id) or []),
                "content_model": content_model,
            }
        )
    cjk_detected = any(bool(doc.get("text")) and any(token in str(doc.get("text")) for token in ("；", "：", "，")) for doc in source_docs)
    parser_warnings: list[str] = []
    if cjk_detected and not (contract.get("sections") and contract.get("states")):
        parser_warnings.append("cjk_punctuation_detected_but_contract_sections_or_states_missing")
    plan_payload = {
        "schema_version": "2.0" if reference_pack_v2 else "1.1",
        "feature": feature,
        "version": version,
        "prototype_mode": "reference-pack-v2" if reference_pack_v2 else "minimal",
        "coverage_mode": str(contract.get("coverage_mode") or "archetype-sections"),
        "source_refs": [doc["relative_path"] for doc in source_docs],
        "source_fingerprints": {doc["type"]: doc["fingerprint"] for doc in source_docs},
        "required_pages": required_pages,
        "required_states": required_states,
        "page_inventory": [
            {
                "page_id": page_id,
                "baseline_protected": page_id in baseline_by_page,
            }
            for page_id in required_pages
        ],
        "baseline_protection": [{"page": page, "preserve": guards} for page, guards in baseline_by_page.items()],
        "page_specs": page_specs,
        "parser": {
            "cjk_detected": cjk_detected,
            "cjk_parse_failed": bool(parser_warnings),
            "warnings": parser_warnings,
        },
        "contract": contract,
        "theme": theme,
        "navigation_map": navigation_map,
        "interaction_map": interaction_map,
    }
    return plan_payload


def _fetch_web_guideline_source() -> tuple[str, bool]:
    try:
        with urlopen(WEB_GUIDELINE_SOURCE_URL, timeout=5) as response:  # noqa: S310
            return response.read().decode("utf-8"), True
    except (OSError, TimeoutError, URLError):
        return "", False


def _line_number(text: str, token: str) -> int:
    for index, line in enumerate(text.splitlines(), start=1):
        if token in line:
            return index
    return 1


def _append_guideline_finding(
    findings: list[dict[str, Any]],
    *,
    path: Path,
    text: str,
    rule: str,
    severity: str,
    message: str,
    token: str | None = None,
) -> None:
    findings.append(
        {
            "file": str(path),
            "line": _line_number(text, token or ""),
            "rule": rule,
            "severity": severity,
            "message": message,
        }
    )


def _audit_web_guidelines(
    files: dict[str, Path],
    contract: dict[str, Any],
    design_system_contract: dict[str, Any],
) -> dict[str, Any]:
    source_text, fetched = _fetch_web_guideline_source()
    findings: list[dict[str, Any]] = []
    shared_css_text = files["tokens_css"].read_text(encoding="utf-8") if files["tokens_css"].exists() else ""
    html_targets = [files["index_html"]]
    pages_dir = files.get("pages_dir")
    if pages_dir and pages_dir.exists():
        html_targets.extend(sorted(path for path in pages_dir.glob("*.html") if path.is_file()))

    for path in html_targets:
        text = path.read_text(encoding="utf-8")
        if "Skip to main content" not in text:
            _append_guideline_finding(
                findings,
                path=path,
                text=text,
                rule="skip-link",
                severity="critical",
                message="missing skip link for main content",
                token="<body",
            )
        if ":focus-visible" not in text and ":focus-visible" not in shared_css_text:
            _append_guideline_finding(
                findings,
                path=path,
                text=text,
                rule="focus-visible",
                severity="critical",
                message="missing visible focus replacement",
                token="<style",
            )
        if "prefers-reduced-motion" not in text and "prefers-reduced-motion" not in shared_css_text:
            _append_guideline_finding(
                findings,
                path=path,
                text=text,
                rule="reduced-motion",
                severity="critical",
                message="missing prefers-reduced-motion support",
                token="<style",
            )
        if "<button class=\"btn btn-outline-primary text-start\" @click=\"tab='" in text:
            _append_guideline_finding(
                findings,
                path=path,
                text=text,
                rule="url-reflects-state",
                severity="warning",
                message="tab state is local-only and not reflected in URL",
                token='@click="tab=',
            )
        if any(marker in text.lower() for marker in _GENERIC_FONT_MARKERS):
            _append_guideline_finding(
                findings,
                path=path,
                text=text,
                rule="generic-font-stack",
                severity="warning",
                message="generic font markers remain in rendered HTML",
                token="font-family",
            )

    typography = dict(design_system_contract.get("typography") or {})
    body_font = str(typography.get("body") or "").strip().lower()
    if any(marker == body_font for marker in _GENERIC_FONT_MARKERS):
        findings.append(
            {
                "file": str(files["design_system_contract"]),
                "line": 1,
                "rule": "generic-font-contract",
                "severity": "warning",
                "message": "design-system contract still points to a generic body font",
            }
        )

    severity_counts = {
        "critical": sum(1 for item in findings if item.get("severity") == "critical"),
        "warning": sum(1 for item in findings if item.get("severity") == "warning"),
    }
    outcome = "pass"
    if severity_counts["critical"] > 0:
        outcome = "blocked"
    elif severity_counts["warning"] > 0 and _design_governance_enabled(contract):
        outcome = "revise"
    return {
        "schema_version": "1.0",
        "source_url": WEB_GUIDELINE_SOURCE_URL,
        "source_fetched": fetched,
        "source_checksum": sha256_text(source_text) if source_text else "",
        "design_governance_required": _design_governance_enabled(contract),
        "rules_checked": [
            "skip-link",
            "focus-visible",
            "reduced-motion",
            "url-reflects-state",
            "generic-font-stack",
        ],
        "severity_counts": severity_counts,
        "design_review_outcome": outcome,
        "findings": findings,
    }


def _render_tokens_css(theme: dict[str, Any]) -> str:
    typography = dict(theme.get("typography") or {})
    return (
        ":root {\n"
        f"  --beacon-color-primary: {theme.get('primary', '#3b82f6')};\n"
        f"  --beacon-color-secondary: {theme.get('secondary', '#0f172a')};\n"
        f"  --beacon-font-display: \"{typography.get('display', 'Fraunces')}\", serif;\n"
        f"  --beacon-font-body: \"{typography.get('body', 'IBM Plex Sans')}\", sans-serif;\n"
        f"  --beacon-font-mono: \"{typography.get('mono', 'JetBrains Mono')}\", monospace;\n"
        "  --beacon-radius-base: 16px;\n"
        "  --beacon-shadow-base: 0 18px 50px rgba(15,23,42,0.08);\n"
        "  --beacon-space-4: 4px;\n"
        "  --beacon-space-8: 8px;\n"
        "  --beacon-space-12: 12px;\n"
        "  --beacon-space-16: 16px;\n"
        "  --beacon-space-24: 24px;\n"
        "}\n"
        "body { font-family: var(--beacon-font-body); }\n"
        "h1, h2, h3, h4, h5, h6 { font-family: var(--beacon-font-display); scroll-margin-top: 6rem; }\n"
        ":focus-visible { outline: 3px solid color-mix(in srgb, var(--beacon-color-primary) 45%, transparent); outline-offset: 2px; }\n"
        "@media (prefers-reduced-motion: reduce) {\n"
        "  * { animation: none !important; transition: none !important; }\n"
        "}\n"
    )


def _title_case_page(page_id: str) -> str:
    return str(page_id or "page").replace("-", " ").title()


def _render_reference_blocks(page_id: str, page_spec: dict[str, Any], *, state: str | None = None) -> str:
    content_model = page_spec.get("content_model") if isinstance(page_spec.get("content_model"), dict) else {}
    title = html.escape(str(content_model.get("headline") or _title_case_page(page_id)))
    primary_cta = html.escape(str(content_model.get("primary_cta") or page_spec.get("primary_cta") or "Continue"))
    secondary_cta = html.escape(str(content_model.get("secondary_cta") or (page_spec.get("secondary_ctas") or ["Details"])[0]))
    state_line = f"<div class='page-meta-badge'>{html.escape(state)}</div>" if state else ""

    def rows(labels: list[tuple[str, str]]) -> str:
        return "".join(
            f"<div class='data-row'><span>{html.escape(left)}</span><strong>{html.escape(right)}</strong></div>"
            for left, right in labels
        )

    if page_id in {"home", "hero"}:
        kpis = content_model.get("kpis") if isinstance(content_model.get("kpis"), list) else []
        cards = content_model.get("cards") if isinstance(content_model.get("cards"), list) else []
        return f"""
        <section class="hero-panel">
          <div class="eyebrow">Daily Mission</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "赛事创建、加入比赛、进行中运营与工具入口统一收口。"))}</p>
          <div class="cta-row">
            <button class="btn-primary-solid">{primary_cta}</button>
            <button class="btn-secondary-ghost">{secondary_cta}</button>
          </div>
        </section>
        <section class="stat-grid">
          {''.join(f"<div class='stat-card'><span>{html.escape(str(item.get('label') or '指标'))}</span><strong>{html.escape(str(item.get('value') or '--'))}</strong></div>" for item in kpis)}
        </section>
        <section class="card-stack">
          <article class="surface-card emphasis"><div class="eyebrow">{html.escape(str(cards[0].get('title') if len(cards) > 0 and isinstance(cards[0], dict) else '当前比赛'))}</div><h3>{html.escape(str(cards[0].get('body') if len(cards) > 0 and isinstance(cards[0], dict) else '周末双打友谊赛 · 16 人 · 第 3 轮'))}</h3>{state_line}</article>
          <article class="surface-card">{rows([(str(item.get('title') or ''), str(item.get('body') or '')) for item in cards[1:] if isinstance(item, dict)])}</article>
        </section>
        """
    if page_id in {"game-detail", "matches", "detail-tabs"}:
        tabs = content_model.get("tabs") if isinstance(content_model.get("tabs"), list) else ["Matches", "Ranking", "Players", "Settings", "Teams"]
        matches = content_model.get("matches") if isinstance(content_model.get("matches"), list) else []
        return f"""
        <section class="hero-panel compact">
          <div class="eyebrow">Match Hub</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "对阵、排名、选手、设置与赛事动作在这里聚合。"))}</p>
          {state_line}
        </section>
        <section class="tab-strip">
          {''.join(f"<span class='tab{' active' if idx == 0 else ''}'>{html.escape(str(tab))}</span>" for idx, tab in enumerate(tabs))}
        </section>
        <section class="card-stack">
          <article class="surface-card">
            {''.join(f"<div class='match-row'><div><strong>{html.escape(str(item.get('left') or '选手 A'))}</strong><span>{html.escape(str(item.get('right') or item.get('status') or '选手 B'))}</span></div><b>{html.escape(str(item.get('score') or '--'))}</b></div>" for item in matches if isinstance(item, dict))}
          </article>
          <div class="cta-row">
            <button class="btn-primary-solid">录入比分</button>
            <button class="btn-secondary-ghost">查看排名</button>
          </div>
        </section>
        """
    if page_id in {"spectator", "spectator-focus"}:
        kpis = content_model.get("kpis") if isinstance(content_model.get("kpis"), list) else []
        cards = content_model.get("cards") if isinstance(content_model.get("cards"), list) else []
        return f"""
        <section class="hero-panel compact live">
          <div class="eyebrow">Spectator</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "自动更新比分看板，保留上一帧结果并支持手动刷新。"))}</p>
          <div class="live-chip">30s 自动刷新</div>
        </section>
        <section class="surface-card">
          {rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in kpis if isinstance(item, dict)])}
        </section>
        <section class="card-stack">
          <article class="surface-card emphasis"><div class="eyebrow">{html.escape(str(cards[0].get('title') if len(cards) > 0 and isinstance(cards[0], dict) else '排行榜'))}</div><h3>{html.escape(str(cards[0].get('body') if len(cards) > 0 and isinstance(cards[0], dict) else 'Top 3'))}</h3></article>
          <article class="surface-card">{rows([(str(item.get('title') or ''), str(item.get('body') or '')) for item in cards[1:] if isinstance(item, dict)])}</article>
        </section>
        """
    if page_id in {"rankings", "ranking-focus"}:
        podium = content_model.get("podium") if isinstance(content_model.get("podium"), list) else []
        rows_data = content_model.get("rows") if isinstance(content_model.get("rows"), list) else []
        return f"""
        <section class="hero-panel compact">
          <div class="eyebrow">Leaderboard</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "名次层级、胜率、积分与最近战绩一屏对比。"))}</p>
        </section>
        <section class="podium-grid">
          {''.join(f"<article class='podium-card {'gold' if idx == 1 else 'silver' if idx == 0 else 'bronze'}'><span>{html.escape(str(item.get('rank') or '#'))}</span><strong>{html.escape(str(item.get('name') or '选手'))}</strong><small>{html.escape(str(item.get('value') or '--'))}</small></article>" for idx, item in enumerate(podium) if isinstance(item, dict))}
        </section>
        <section class="surface-card">
          {rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}
        </section>
        """
    if page_id in {"mine", "my-stats", "my-honors"}:
        profile = content_model.get("profile") if isinstance(content_model.get("profile"), dict) else {}
        kpis = content_model.get("kpis") if isinstance(content_model.get("kpis"), list) else []
        quick_links = content_model.get("quick_links") if isinstance(content_model.get("quick_links"), list) else []
        trend = content_model.get("trend") if isinstance(content_model.get("trend"), list) else []
        medals = content_model.get("medals") if isinstance(content_model.get("medals"), list) else []
        quick_links_markup = (
            "<section class='surface-card'>"
            + "".join(
                f"<div class='data-row'><span>快捷入口</span><strong>{html.escape(str(link))}</strong></div>"
                for link in quick_links
            )
            + "</section>"
        ) if quick_links else ""
        trend_markup = (
            "<section class='surface-card'>"
            + "".join(
                f"<div class='data-row'><span>近期趋势</span><strong>{html.escape(str(item))}</strong></div>"
                for item in trend
            )
            + "</section>"
        ) if trend else ""
        medals_cards = []
        for idx, item in enumerate(medals):
            if not isinstance(item, dict):
                continue
            medal_tone = "gold" if idx == 0 else "silver" if idx == 1 else "bronze"
            medals_cards.append(
                f"<article class='podium-card {medal_tone}'><span>{html.escape(str(item.get('label') or '奖牌'))}</span><strong>{html.escape(str(item.get('value') or '--'))}</strong><small>已获得</small></article>"
            )
        medals_markup = f"<section class='podium-grid'>{''.join(medals_cards)}</section>" if medals_cards else ""
        return f"""
        <section class="hero-panel compact">
          <div class="eyebrow">Profile</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "个人成绩、荣誉归档与设置任务合并到结果页体验。"))}</p>
        </section>
        <section class="surface-card profile-card">
          <div class="avatar-circle">AF</div>
          <div><strong>{html.escape(str(profile.get('name') or '阿福'))}</strong><span>{html.escape(str(profile.get('meta') or '本周 8 场 · 胜率 75%'))}</span></div>
        </section>
        <section class="stat-grid">
          {''.join(f"<div class='stat-card'><span>{html.escape(str(item.get('label') or '指标'))}</span><strong>{html.escape(str(item.get('value') or '--'))}</strong></div>" for item in kpis if isinstance(item, dict))}
        </section>
        {quick_links_markup}
        {trend_markup}
        {medals_markup}
        """
    if page_id == "fee-calculator":
        rows_data = content_model.get("rows") if isinstance(content_model.get("rows"), list) else []
        return f"""
        <section class="hero-panel compact">
          <div class="eyebrow">Tool</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "费用模式切换、人均金额与复制结果一屏完成。"))}</p>
        </section>
        <section class="surface-card">
          {rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}
        </section>
        <div class="cta-row">
          <button class="btn-primary-solid">复制结论</button>
          <button class="btn-secondary-ghost">切换模式</button>
        </div>
        """
    if page_id == "edit-profile":
        rows_data = content_model.get("rows") if isinstance(content_model.get("rows"), list) else []
        return f"""
        <section class="hero-panel compact">
          <div class="eyebrow">Profile Editor</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "资料编辑页聚焦关键资料字段。"))}</p>
        </section>
        <section class="surface-card profile-card">
          <div class="avatar-circle">AF</div>
          <div><strong>阿福</strong><span>完善资料提升可信度</span></div>
        </section>
        <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
        <div class="cta-row">
          <button class="btn-primary-solid">保存资料</button>
          <button class="btn-secondary-ghost">取消</button>
        </div>
        """
    if page_id in {"login", "register"}:
        rows_data = content_model.get("rows") if isinstance(content_model.get("rows"), list) else []
        return f"""
        <section class="hero-panel compact">
          <div class="eyebrow">Auth</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "登录成功后应回跳原目标页。"))}</p>
        </section>
        <section class="surface-card">
          {rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}
        </section>
        <div class="cta-row">
          <button class="btn-primary-solid">微信快捷登录</button>
          <button class="btn-secondary-ghost">账号方式</button>
        </div>
        """
    if page_id in {"player-detail"}:
        rows_data = content_model.get("rows") if isinstance(content_model.get("rows"), list) else []
        return f"""
        <section class="hero-panel compact">
          <div class="eyebrow">Detail</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "关键详情页聚焦单一任务。"))}</p>
        </section>
        <section class="surface-card">
          {rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}
        </section>
        <article class="surface-card emphasis"><div class="eyebrow">Recent Form</div><h3>近 5 场 4 胜 1 负</h3><p>胜率 80% · 双打更稳定</p></article>
        """
    if page_id in {"score-entry", "batch-score-entry"}:
        matches = content_model.get("matches") if isinstance(content_model.get("matches"), list) else []
        rows_data = content_model.get("rows") if isinstance(content_model.get("rows"), list) else []
        return f"""
        <section class="hero-panel compact">
          <div class="eyebrow">Score Entry</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "比分录入页要突出当前对阵和提交动作。"))}</p>
        </section>
        <section class="card-stack">
          <article class="surface-card">
            {''.join(f"<div class='match-row'><div><strong>{html.escape(str(item.get('left') or '选手 A'))}</strong><span>{html.escape(str(item.get('right') or item.get('status') or '选手 B'))}</span></div><b>{html.escape(str(item.get('score') or '--'))}</b></div>" for item in matches if isinstance(item, dict))}
          </article>
          <article class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</article>
        </section>
        <div class="cta-row">
          <button class="btn-primary-solid">提交比分</button>
          <button class="btn-secondary-ghost">保存草稿</button>
        </div>
        """
    if page_id == "create-team-game":
        steps = content_model.get("steps") if isinstance(content_model.get("steps"), list) else []
        rows_data = content_model.get("rows") if isinstance(content_model.get("rows"), list) else []
        return f"""
        <section class="hero-panel compact">
          <div class="eyebrow">Team Tournament</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "团体赛建赛页强调阵营配置与后续管理动作。"))}</p>
        </section>
        <section class="step-grid">
          {''.join(f"<article class='step-card{' active' if idx == 0 else ''}'><span>{idx+1}</span><strong>{html.escape(str(step))}</strong></article>" for idx, step in enumerate(steps))}
        </section>
        <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
        <div class="cta-row">
          <button class="btn-primary-solid">继续配置</button>
          <button class="btn-secondary-ghost">预览阵营</button>
        </div>
        """
    if page_id in {"scenario-selection", "mode-selection", "add-participants", "preview-matchups", "join-game", "bind-users"}:
        steps = content_model.get("steps") if isinstance(content_model.get("steps"), list) else ["选择场景", "配置模式", "添加参赛者"]
        rows_data = content_model.get("rows") if isinstance(content_model.get("rows"), list) else []
        return f"""
        <section class="hero-panel compact">
          <div class="eyebrow">Flow Step</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "建赛与报名链路的关键步骤页，强调下一步动作。"))}</p>
        </section>
        <section class="step-grid">
          {''.join(f"<article class='step-card{' active' if idx == 0 else ''}'><span>{idx+1}</span><strong>{html.escape(str(step))}</strong></article>" for idx, step in enumerate(steps))}
        </section>
        <section class="surface-card">
          {rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}
        </section>
        <div class="cta-row">
          <button class="btn-primary-solid">{primary_cta}</button>
          <button class="btn-secondary-ghost">返回上一步</button>
        </div>
        """
    if page_id.startswith("club") or page_id.startswith("team") or page_id in {"stage-management", "group-management", "promotion-settings", "awards", "tournament-list", "bracket"}:
        rows_data = content_model.get("rows") if isinstance(content_model.get("rows"), list) else []
        variant = str(content_model.get("variant") or "")
        if variant == "tournament-list-board":
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Tournament List</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or ""))}</p>
            </section>
            <section class="stat-grid">
              {''.join(f"<div class='stat-card'><span>{html.escape(str(item.get('label') or '指标'))}</span><strong>{html.escape(str(item.get('value') or '--'))}</strong></div>" for item in rows_data if isinstance(item, dict))}
            </section>
            <section class="card-stack">
              <article class="surface-card emphasis"><div class="eyebrow">当前焦点</div><h3>周末双打友谊赛</h3><p>进行中 · 16 人 · 第 3 轮</p></article>
              <article class="surface-card"><div class='data-row'><span>收藏赛事</span><strong>企业杯邀请赛</strong></div><div class='data-row'><span>待开始</span><strong>周三夜赛</strong></div></article>
            </section>
            """
        if variant == "bracket-board":
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Bracket</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or ""))}</p>
            </section>
            <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
            <section class="card-stack">
              <article class="surface-card emphasis"><div class="eyebrow">晋级树</div><h3>半决赛 -> 决赛</h3><p>两场进行中，可直接进入 score-entry。</p></article>
            </section>
            """
        if variant == "awards-board":
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Awards</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or ""))}</p>
            </section>
            <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
            <section class="podium-grid">
              <article class="podium-card gold"><span>冠军</span><strong>李雷</strong><small>已确认</small></article>
              <article class="podium-card silver"><span>亚军</span><strong>韩梅梅</strong><small>待海报</small></article>
              <article class="podium-card bronze"><span>季军</span><strong>王强</strong><small>已确认</small></article>
            </section>
            """
        if variant == "competition-config-board":
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Competition Config</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or ""))}</p>
            </section>
            <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
            <div class="cta-row">
              <button class="btn-primary-solid">保存规则</button>
              <button class="btn-secondary-ghost">查看上游上下文</button>
            </div>
            """
        if variant == "team-ops-board":
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Team Ops</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or ""))}</p>
            </section>
            <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
            <section class="card-stack">
              <article class="surface-card emphasis"><div class="eyebrow">阵营 A</div><h3>8 人</h3><p>待调换 1 人</p></article>
              <article class="surface-card emphasis"><div class="eyebrow">阵营 B</div><h3>8 人</h3><p>统计已同步</p></article>
            </section>
            """
        if variant == "club-list-board":
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Club Directory</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or ""))}</p>
            </section>
            <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
            <section class="card-stack">
              <article class="surface-card emphasis"><div class="eyebrow">羽球营地杭州站</div><h3>42 名成员</h3><p>本周 3 场活动</p></article>
              <article class="surface-card emphasis"><div class="eyebrow">城北晨练社</div><h3>31 名成员</h3><p>待审批 2 人</p></article>
            </section>
            """
        if variant == "club-detail-board":
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Club Detail</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or ""))}</p>
            </section>
            <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
            <div class="cta-row">
              <button class="btn-primary-solid">查看成员</button>
              <button class="btn-secondary-ghost">查看近期比赛</button>
            </div>
            """
        if variant == "club-members-board":
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Club Members</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or ""))}</p>
            </section>
            <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
            <section class="card-stack">
              <article class="surface-card emphasis"><div class="eyebrow">最新成员</div><h3>王强 / 赵二 / 刘八</h3><p>最近 7 天加入</p></article>
            </section>
            """
        if variant == "club-create-board":
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Club Create</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or ""))}</p>
            </section>
            <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
            <div class="cta-row">
              <button class="btn-primary-solid">创建俱乐部</button>
              <button class="btn-secondary-ghost">预览主页</button>
            </div>
            """
        return f"""
        <section class="hero-panel compact">
          <div class="eyebrow">Operations</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "管理型页面采用任务面板 + 列表卡片结构，不再是纯文字占位。"))}</p>
        </section>
        <section class="card-stack">
          <article class="surface-card emphasis"><div class="eyebrow">今日待办</div><h3>{html.escape(str(rows_data[0].get('value') if rows_data and isinstance(rows_data[0], dict) else '3 项待确认'))}</h3><p>成员配置、晋级规则、赛事公告</p></article>
          <article class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data[1:] if isinstance(item, dict)] or [('状态', html.escape(state or 'in-progress'))])}</article>
        </section>
        """
    if page_id in {"help", "rules-wiki", "rule-detail", "settings", "coming-soon", "css-config", "audit", "coverage-matrix", "next-steps", "components", "visual-language", "interaction-flows", "closure", "overview", "batch-a-gallery", "batch-b-gallery", "batch-c-gallery"}:
        rows_data = content_model.get("rows") if isinstance(content_model.get("rows"), list) else []
        if page_id in {"help", "rules-wiki", "rule-detail", "settings", "coming-soon"} and str(content_model.get("variant") or "") == "support-center":
            panels = content_model.get("panels") if isinstance(content_model.get("panels"), list) else []
            panels_markup = (
                "<section class='card-stack'>"
                + "".join(
                    f"<article class='surface-card emphasis'><div class='eyebrow'>精选入口</div><h3>{html.escape(str(panel))}</h3><p>围绕当前页面的核心支持动作组织内容。</p></article>"
                    for panel in panels
                )
                + "</section>"
            ) if panels else ""
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Support Center</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or "帮助、设置与规则页应该像服务中心。"))}</p>
            </section>
            <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
            {panels_markup}
            <div class="cta-row">
              <button class="btn-primary-solid">查看帮助</button>
              <button class="btn-secondary-ghost">提交反馈</button>
            </div>
            """
        if str(content_model.get("variant") or "") == "design-reference":
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Design Reference</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or "沉淀设计原则与视觉系统。"))}</p>
            </section>
            <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
            <section class="card-stack">
              <article class="surface-card emphasis"><div class="eyebrow">Reference Block</div><h3>组件 / 交互 / 视觉 token</h3><p>这里承接设计约束与页面交接所需的关键信息。</p></article>
              <article class="surface-card emphasis"><div class="eyebrow">Implementation Note</div><h3>与前端真实实现对照</h3><p>确保页面、组件、状态和路由闭环能被下游消费。</p></article>
            </section>
            """
        if str(content_model.get("variant") or "") == "gallery-reference":
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Gallery Reference</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or "承接多页原型入口。"))}</p>
            </section>
            <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
            <article class="surface-card emphasis"><div class="eyebrow">Entry Model</div><h3>多页入口与状态入口</h3><p>该页应从 index.html 直接进入相关页面簇和状态簇。</p></article>
            """
        if str(content_model.get("variant") or "") == "next-actions":
            return f"""
            <section class="hero-panel compact">
              <div class="eyebrow">Next Actions</div>
              <h2>{title}</h2>
              <p>{html.escape(str(content_model.get("subheadline") or "收口评审与交接动作。"))}</p>
            </section>
            <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)])}</section>
            <div class="cta-row">
              <button class="btn-primary-solid">继续实施</button>
              <button class="btn-secondary-ghost">回看覆盖矩阵</button>
            </div>
            """
        return f"""
        <section class="hero-panel compact">
          <div class="eyebrow">Reference</div>
          <h2>{title}</h2>
          <p>{html.escape(str(content_model.get("subheadline") or "说明文档、规则说明与交互盘点通过信息卡片方式组织。"))}</p>
        </section>
        <section class="surface-card">{rows([(str(item.get('label') or ''), str(item.get('value') or '')) for item in rows_data if isinstance(item, dict)] or [('页面类型', '文档 / 规则 / 配置'), ('当前状态', html.escape(state or 'ready-for-freeze')), ('主要目标', '支持评审与实现对齐')])}</section>
        <article class="surface-card emphasis"><div class="eyebrow">Key Note</div><h3>保持语义密度</h3><p>这个页面现在已经不是空壳，而是带有任务与内容结构的参考稿。</p></article>
        """
    return f"""
    <section class="hero-panel compact">
      <div class="eyebrow">Reference Page</div>
      <h2>{title}</h2>
      <p>{html.escape(str(page_spec.get('intent') or 'Compiled reference page'))}</p>
      {state_line}
    </section>
    <section class="surface-card">{rows([('Sections', str(len(page_spec.get('sections') or []))), ('States', str(len(page_spec.get('states') or []))), ('Route Targets', str(len(page_spec.get('route_targets') or [])))])}</section>
    """


def _render_reference_page_html(feature: str, page_spec: dict[str, Any], theme: dict[str, Any], *, state: str | None = None) -> str:
    page_title = str(page_spec.get("page_id") or "page").replace("-", " ").title()
    page_id = slugify_feature(str(page_spec.get("page_id") or "page"))
    content = _render_reference_blocks(page_id, page_spec, state=state)
    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>{html.escape(feature)} · {html.escape(page_title)}</title>
    <link rel=\"stylesheet\" href=\"../tokens.css\">
    <style>
      body {{ font-family: var(--beacon-font-body, sans-serif); background: linear-gradient(180deg, #eef2ff 0%, #f8fafc 100%); color: #0f172a; margin: 0; }}
      h1, h2, h3, h4, h5, h6 {{ font-family: var(--beacon-font-display, serif); scroll-margin-top: 6rem; }}
      .frame {{ max-width: 1180px; margin: 0 auto; padding: 32px; }}
      .skip-link {{ position: absolute; left: 1rem; top: -3rem; background: #0f172a; color: white; padding: .7rem 1rem; border-radius: 999px; z-index: 100; text-decoration: none; }}
      .skip-link:focus-visible {{ top: 1rem; }}
      .phone-shell {{ max-width: 430px; margin: 0 auto; background: #12182d; border-radius: 36px; padding: 14px; box-shadow: 0 30px 80px rgba(15,23,42,.25); }}
      .screen {{ background: #f8fafc; min-height: 820px; border-radius: 28px; overflow: hidden; padding: 18px; }}
      .hero-panel {{ background: linear-gradient(135deg, var(--beacon-color-secondary) 0%, var(--beacon-color-primary) 100%); color: white; border-radius: 24px; padding: 18px; box-shadow: 0 20px 44px rgba(59,130,246,.25); }}
      .hero-panel.compact {{ padding: 16px; }}
      .hero-panel.live {{ background: linear-gradient(135deg, #0f766e 0%, var(--beacon-color-primary) 100%); }}
      .hero-panel h2 {{ margin: 6px 0 8px; font-size: 1.35rem; }}
      .hero-panel p {{ margin: 0; color: rgba(255,255,255,.82); font-size: .95rem; line-height: 1.45; }}
      .eyebrow {{ font-size: .72rem; text-transform: uppercase; letter-spacing: .12em; opacity: .78; font-weight: 700; }}
      .page-meta-badge, .live-chip {{ display: inline-flex; margin-top: 12px; padding: 6px 10px; border-radius: 999px; background: rgba(255,255,255,.16); font-size: .74rem; font-weight: 700; }}
      .surface-card {{ background: rgba(255,255,255,.96); border-radius: 20px; padding: 16px; box-shadow: 0 16px 36px rgba(15,23,42,.08); border: 1px solid rgba(148,163,184,.16); }}
      .surface-card.emphasis {{ background: linear-gradient(180deg, rgba(255,255,255,.98), rgba(239,246,255,.98)); }}
      .card-stack {{ display: flex; flex-direction: column; gap: 14px; margin-top: 14px; }}
      .stat-grid, .podium-grid, .step-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 14px; }}
      .podium-grid {{ grid-template-columns: repeat(3, 1fr); }}
      .step-grid {{ grid-template-columns: repeat(3, 1fr); }}
      .stat-card, .podium-card, .step-card {{ background: rgba(255,255,255,.96); border-radius: 18px; padding: 14px; box-shadow: 0 14px 30px rgba(15,23,42,.06); }}
      .stat-card span, .podium-card span {{ display: block; font-size: .72rem; color: #64748b; }}
      .stat-card strong {{ display: block; font-size: 1.25rem; margin-top: 6px; }}
      .podium-card strong {{ display: block; margin-top: 8px; font-size: 1rem; }}
      .podium-card small {{ color: #64748b; }}
      .podium-card.gold {{ background: linear-gradient(180deg, #fff7d6, #ffffff); }}
      .podium-card.silver {{ background: linear-gradient(180deg, #eef2f7, #ffffff); }}
      .podium-card.bronze {{ background: linear-gradient(180deg, #f8e7d8, #ffffff); }}
      .profile-card {{ display: flex; align-items: center; gap: 12px; }}
      .avatar-circle {{ width: 52px; height: 52px; border-radius: 999px; background: linear-gradient(135deg, var(--beacon-color-primary), var(--beacon-color-secondary)); color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; }}
      .cta-row {{ display: flex; gap: 12px; margin-top: 14px; }}
      .btn-primary-solid, .btn-secondary-ghost {{ border: 0; border-radius: 16px; padding: 12px 14px; font-weight: 700; }}
      .btn-primary-solid {{ background: var(--beacon-color-primary); color: white; flex: 1; }}
      .btn-secondary-ghost {{ background: #eef2ff; color: var(--beacon-color-secondary); flex: 1; }}
      .data-row, .match-row {{ display: flex; justify-content: space-between; gap: 12px; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(226,232,240,.8); }}
      .data-row:last-child, .match-row:last-child {{ border-bottom: 0; }}
      .data-row span, .match-row span {{ color: #64748b; font-size: .88rem; display: block; }}
      .data-row strong, .match-row strong, .match-row b {{ color: #0f172a; font-size: .95rem; }}
      .tab-strip {{ display: flex; gap: 8px; overflow: auto; margin-top: 14px; }}
      .tab {{ padding: 8px 12px; border-radius: 999px; background: #e2e8f0; color: #334155; font-size: .8rem; font-weight: 700; white-space: nowrap; }}
      .tab.active {{ background: var(--beacon-color-primary); color: white; }}
      @media (max-width: 640px) {{ .stat-grid, .podium-grid, .step-grid {{ grid-template-columns: 1fr 1fr; }} .cta-row {{ flex-direction: column; }} }}
    </style>
  </head>
  <body>
    <a class=\"skip-link\" href=\"#main-content\">Skip to main content</a>
    <main class=\"frame\" id=\"main-content\">
      <div class=\"phone-shell\">
        <section class=\"screen\">
          {content}
        </section>
      </div>
    </main>
  </body>
</html>
"""

def _reference_pack_entry_target(*, primary_ref: str, fallback: str, available_pages: list[str]) -> str:
    target = slugify_feature(primary_ref)
    if target and target in available_pages:
        return target
    return available_pages[0] if available_pages else fallback


def _render_reference_pack_directory(required_pages: list[str], required_states: list[str]) -> str:
    if not required_pages:
        return ""
    page_cards = []
    for page in required_pages:
        state_links = "".join(
            f'<a class="badge rounded-pill text-bg-light border text-decoration-none" href="states/{html.escape(page)}--{html.escape(slugify_feature(state))}.html">{html.escape(state)}</a>'
            for state in required_states[:6]
        )
        page_cards.append(
            f"""
            <div class="col-md-6 col-xl-4">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start gap-2 mb-3">
                    <div>
                      <div class="text-uppercase small text-body-secondary mb-1">Reference Page</div>
                      <h3 class="h6 mb-0">{html.escape(page.replace('-', ' ').title())}</h3>
                    </div>
                    <a class="btn btn-sm btn-primary" href="pages/{html.escape(page)}.html" aria-label="Open {html.escape(page)} page">Open</a>
                  </div>
                  <p class="small text-body-secondary mb-3">Direct hi-fi page plus generated state variants.</p>
                  <div class="d-flex flex-wrap gap-2">{state_links or '<span class="badge text-bg-light">default</span>'}</div>
                </div>
              </div>
            </div>
            """
        )
    return (
        '<section id="reference-pack-directory" class="prototype-card p-4 p-lg-5 mt-4">'
        '<div class="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">'
        '<div><div class="text-uppercase small text-body-secondary mb-2">Reference Pack</div>'
        '<h2 class="h3 mb-2">Hi-fi page directory</h2>'
        '<p class="text-body-secondary mb-0">Use these links to open each generated page and its state variants directly.</p></div>'
        f'<div class="prototype-token"><i class="bi bi-grid-3x3-gap"></i>{len(required_pages)} pages / {len(required_states)} states</div>'
        '</div>'
        f'<div class="row g-3">{"".join(page_cards)}</div>'
        '</section>'
    )


def _nav_links(navigation_map: dict[str, Any]) -> str:
    links = []
    for node in navigation_map.get("navigation_nodes", []):
        links.append(
            f'<a class="nav-link text-body-secondary" href="{html.escape(node["target"])}">{html.escape(node["label"])}</a>'
        )
    return "".join(links)


def _render_state_badges(states: list[str]) -> str:
    return "".join(
        f'<span class="badge text-bg-light border border-secondary-subtle me-2 mb-2">{html.escape(state)}</span>'
        for state in states
    )


def _render_jump_cards(jumps: list[dict[str, str]]) -> str:
    if not jumps:
        return '<div class="alert alert-warning">No jump map provided.</div>'
    cards = []
    for item in jumps:
        cards.append(
            f'''
            <div class="col-md-6 col-xl-4">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-body">
                  <div class="text-uppercase small text-body-secondary mb-2">Jump</div>
                  <h3 class="h6 mb-2">{html.escape(item.get("from", "entry"))} → {html.escape(item.get("to", ""))}</h3>
                  <p class="text-body-secondary small mb-0">{html.escape(item.get("why", "No rationale provided."))}</p>
                </div>
              </div>
            </div>
            '''
        )
    return "".join(cards)


def _render_preview_surface(contract: dict[str, Any], interaction_map: dict[str, Any]) -> str:
    archetype = contract["prototype_archetype"]
    sections = contract.get("sections", [])
    states = interaction_map.get("states", [])
    primary_cta = html.escape(str(contract.get("primary_cta", "Continue")))
    secondary_cta = html.escape(str(contract.get("secondary_cta", "Learn More")))

    if archetype == "dashboard":
        stats = "".join(
            f'<div class="col-md-4"><div class="card border-0 shadow-sm h-100"><div class="card-body"><div class="text-uppercase small text-body-secondary mb-2">{html.escape(label)}</div><div class="display-6 fw-semibold">42</div></div></div></div>'
            for label in sections[:3]
        )
        return f'''
        <div class="row g-3">{stats}</div>
        <div class="card border-0 shadow-sm mt-4">
          <div class="card-body">
            <h3 class="h5">Operational Table</h3>
            <table class="table align-middle">
              <thead><tr><th>Item</th><th>Status</th><th>Owner</th></tr></thead>
              <tbody>
                <tr><td>Main flow</td><td><span class="badge text-bg-success">Ready</span></td><td>Product</td></tr>
                <tr><td>Prototype review</td><td><span class="badge text-bg-warning">Pending</span></td><td>Design</td></tr>
              </tbody>
            </table>
            <div class="d-flex gap-2"><button class="btn btn-primary">{primary_cta}</button><button class="btn btn-outline-secondary">{secondary_cta}</button></div>
          </div>
        </div>
        '''
    if archetype == "list-detail":
        items = "".join(f'<button class="list-group-item list-group-item-action">{html.escape(label)}</button>' for label in sections)
        return f'''
        <div class="row g-4">
          <div class="col-lg-4"><div class="list-group">{items}</div></div>
          <div class="col-lg-8"><div class="card border-0 shadow-sm"><div class="card-body"><h3 class="h5">Detail Panel</h3><p class="text-body-secondary">Use this area for the selected item, CTA panel, and related actions.</p><div class="d-flex gap-2"><button class="btn btn-primary">{primary_cta}</button><button class="btn btn-outline-secondary">{secondary_cta}</button></div></div></div></div>
        </div>
        '''
    if archetype == "form-wizard":
        steps = "".join(f'<div class="col"><div class="p-3 border rounded-3 text-center">{html.escape(label)}</div></div>' for label in sections)
        return f'''
        <div class="row row-cols-1 row-cols-md-{max(1, min(len(sections), 4))} g-3 mb-4">{steps}</div>
        <div class="card border-0 shadow-sm"><div class="card-body"><h3 class="h5">Wizard Form</h3><label class="form-label">Primary Field</label><input class="form-control mb-3" placeholder="Enter value"><label class="form-label">State</label><select class="form-select mb-3">{"".join(f'<option>{html.escape(state)}</option>' for state in states)}</select><div class="d-flex gap-2"><button class="btn btn-primary">{primary_cta}</button><button class="btn btn-outline-secondary">{secondary_cta}</button></div></div></div>
        '''
    if archetype == "marketing-page":
        cards = "".join(f'<div class="col-md-4"><div class="card border-0 shadow-sm h-100"><div class="card-body"><h3 class="h5">{html.escape(label)}</h3><p class="text-body-secondary">Benefit narrative aligned to requirement contract.</p></div></div></div>' for label in sections[:3])
        return f'''
        <section class="text-center py-4"><h2 class="display-6 fw-bold">{html.escape(str(contract.get("theme_mood", "Professional"))).title()} landing experience</h2><p class="lead text-body-secondary">Primary message, social proof, and CTA aligned to PRD contract.</p><div class="d-flex justify-content-center gap-2"><button class="btn btn-primary btn-lg">{primary_cta}</button><button class="btn btn-outline-secondary btn-lg">{secondary_cta}</button></div></section>
        <div class="row g-4 mt-2">{cards}</div>
        '''
    if archetype == "admin-workbench":
        side = "".join(f'<a class="list-group-item list-group-item-action">{html.escape(label)}</a>' for label in sections)
        return f'''
        <div class="row g-4">
          <div class="col-lg-3"><div class="list-group">{side}</div></div>
          <div class="col-lg-9"><div class="card border-0 shadow-sm"><div class="card-body"><div class="d-flex justify-content-between align-items-center mb-3"><h3 class="h5 mb-0">Workbench Panel</h3><button class="btn btn-primary">{primary_cta}</button></div><div class="alert alert-primary">Administrative actions, filters, and review context live here.</div><div class="row g-3">{_render_state_badges(states)}</div></div></div></div>
        </div>
        '''
    if archetype == "mobile-task-flow":
        steps = "".join(f'<div class="border rounded-4 p-3 mb-3"><div class="small text-body-secondary">Step</div><div class="fw-semibold">{html.escape(label)}</div></div>' for label in sections)
        return f'''
        <div class="mx-auto" style="max-width:420px;"><div class="card border-0 shadow-lg rounded-5"><div class="card-body p-4"><h3 class="h5 mb-3">Mobile Flow</h3>{steps}<button class="btn btn-primary w-100">{primary_cta}</button></div></div></div>
        '''
    return '<div class="alert alert-danger">Unsupported archetype.</div>'


def render_professional_prototype_html(feature: str, version: str, contract: dict[str, Any], theme: dict[str, Any], navigation_map: dict[str, Any], interaction_map: dict[str, Any], source_docs: list[dict[str, Any]], plan_payload: dict[str, Any] | None = None) -> str:
    title = html.escape(feature)
    source_summary = "".join(
        f'<li><code>{html.escape(doc["relative_path"])}</code></li>' for doc in source_docs
    )
    states = interaction_map.get("states", [])
    jump_cards = _render_jump_cards(interaction_map.get("jump_map", []))
    preview_surface = _render_preview_surface(contract, interaction_map)
    nav_links = _nav_links(navigation_map)
    primary = html.escape(str(theme.get("primary", "#3b82f6")))
    secondary = html.escape(str(theme.get("secondary", "#0f172a")))
    mood = html.escape(str(theme.get("mood", "confident")))
    archetype = html.escape(str(contract.get("prototype_archetype", "dashboard")))
    target_user = html.escape(str(contract.get("target_user", "Product team")))
    primary_cta = html.escape(str(contract.get("primary_cta", "Continue")))
    secondary_cta = html.escape(str(contract.get("secondary_cta", "Learn More")))
    plan_payload = plan_payload if isinstance(plan_payload, dict) else {}
    reference_pack_v2 = str(plan_payload.get("prototype_mode") or contract.get("prototype_mode") or "").strip().lower() == "reference-pack-v2"
    required_pages = [slugify_feature(str(page)) for page in (plan_payload.get("required_pages") or []) if str(page).strip()]
    required_states = [str(state).strip() for state in (plan_payload.get("required_states") or []) if str(state).strip()]
    entry_target = _reference_pack_entry_target(
        primary_ref=str(contract.get("primary_entry") or ""),
        fallback="index",
        available_pages=required_pages,
    )
    exit_target = _reference_pack_entry_target(
        primary_ref=str(contract.get("primary_exit") or ""),
        fallback=entry_target,
        available_pages=required_pages,
    )
    primary_cta_markup = (
        f'<a class="btn btn-primary btn-lg" href="pages/{html.escape(entry_target)}.html">{primary_cta}</a>'
        if reference_pack_v2 and required_pages
        else f'<button class="btn btn-primary btn-lg">{primary_cta}</button>'
    )
    secondary_cta_markup = (
        f'<a class="btn btn-outline-light btn-lg" href="pages/{html.escape(exit_target)}.html">{secondary_cta}</a>'
        if reference_pack_v2 and required_pages
        else f'<button class="btn btn-outline-light btn-lg">{secondary_cta}</button>'
    )
    reference_pack_directory = _render_reference_pack_directory(required_pages, required_states) if reference_pack_v2 else ""
    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>{title} · Beacon Prototype</title>
    <link rel=\"preconnect\" href=\"https://cdn.jsdelivr.net\">
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap-icons@{BOOTSTRAP_ICONS_VERSION}/font/bootstrap-icons.min.css\" rel=\"stylesheet\">
    <script defer src=\"https://cdn.jsdelivr.net/npm/alpinejs@{ALPINE_VERSION}/dist/cdn.min.js\"></script>
    <style>
      :root {{
        --beacon-primary: {primary};
        --beacon-secondary: {secondary};
        --beacon-bg: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        --beacon-radius: 20px;
      }}
      body {{ background: var(--beacon-bg); color: #0f172a; font-family: var(--beacon-font-body, sans-serif); }}
      h1, h2, h3, h4, h5, h6 {{ font-family: var(--beacon-font-display, serif); scroll-margin-top: 6rem; }}
      .prototype-nav {{ backdrop-filter: blur(16px); background: rgba(255,255,255,0.82); border-bottom: 1px solid rgba(148,163,184,0.18); }}
      .prototype-hero {{ background: linear-gradient(135deg, var(--beacon-secondary), #1e293b); color: white; border-radius: 28px; box-shadow: 0 28px 80px rgba(15,23,42,0.22); }}
      .prototype-card {{ border: 1px solid rgba(148,163,184,0.24); border-radius: var(--beacon-radius); background: rgba(255,255,255,0.88); box-shadow: 0 18px 50px rgba(15,23,42,0.08); }}
      .prototype-token {{ display: inline-flex; align-items: center; gap: .4rem; padding: .45rem .75rem; border-radius: 999px; background: rgba(59,130,246,0.12); color: var(--beacon-primary); font-size: .85rem; font-weight: 600; }}
      .btn-primary {{ background: var(--beacon-primary); border-color: var(--beacon-primary); box-shadow: 0 14px 30px color-mix(in srgb, var(--beacon-primary) 30%, transparent); }}
      .prototype-sidebar {{ position: sticky; top: 5rem; }}
      .skip-link {{ position: absolute; left: 1rem; top: -3rem; background: #0f172a; color: white; padding: .7rem 1rem; border-radius: 999px; z-index: 1050; text-decoration: none; }}
      .skip-link:focus-visible {{ top: 1rem; }}
      :focus-visible {{ outline: 3px solid color-mix(in srgb, var(--beacon-primary) 45%, transparent); outline-offset: 2px; }}
      @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} *, *::before, *::after {{ animation: none !important; transition: none !important; }} }}
    </style>
  </head>
  <body>
    <a class=\"skip-link\" href=\"#main-content\">Skip to main content</a>
    <div x-data=\"{{ tab: 'overview' }}\">
      <nav class=\"navbar navbar-expand-lg prototype-nav sticky-top\">
        <div class=\"container py-2\">
          <a class=\"navbar-brand fw-semibold\" href=\"#main-content\">Beacon Prototype</a>
          <button class=\"navbar-toggler\" type=\"button\" data-bs-toggle=\"offcanvas\" data-bs-target=\"#prototypeDrawer\" aria-controls=\"prototypeDrawer\" aria-label=\"Open navigation\"><span class=\"navbar-toggler-icon\"></span></button>
          <div class=\"collapse navbar-collapse\"><div class=\"navbar-nav ms-auto\">{nav_links}</div></div>
        </div>
      </nav>
      <div class=\"offcanvas offcanvas-end\" tabindex=\"-1\" id=\"prototypeDrawer\" aria-labelledby=\"prototypeDrawerLabel\">
        <div class=\"offcanvas-header\"><h2 class=\"offcanvas-title h5 mb-0\" id=\"prototypeDrawerLabel\">Navigate</h2><button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"offcanvas\" aria-label=\"Close navigation\"></button></div>
        <div class=\"offcanvas-body d-flex flex-column gap-2\">{''.join(f'<a class="btn btn-outline-primary text-start" href="{html.escape(node["target"])}">{html.escape(node["label"])}</a>' for node in navigation_map.get("navigation_nodes", []))}</div>
      </div>
      <main class=\"container py-4 py-lg-5\" id=\"main-content\">
        <section class=\"prototype-hero p-4 p-lg-5 mb-4 mb-lg-5\">
          <div class=\"row g-4 align-items-center\">
            <div class=\"col-lg-8\">
              <div class=\"d-flex flex-wrap gap-2 mb-3\">
                <span class=\"prototype-token\"><i class=\"bi bi-bootstrap-fill\"></i> Bootstrap {BOOTSTRAP_VERSION}</span>
                <span class=\"prototype-token\"><i class=\"bi bi-stars\"></i> {mood}</span>
                <span class=\"prototype-token\"><i class=\"bi bi-kanban\"></i> {archetype}</span>
              </div>
              <h1 class=\"display-6 fw-bold mb-3\">{title}</h1>
              <p class=\"lead text-white-50 mb-4\">Professional reference prototype aligned to requirement contracts, navigation intent, and state coverage.</p>
              <div class=\"d-flex flex-wrap gap-3\">{primary_cta_markup}{secondary_cta_markup}</div>
            </div>
            <div class=\"col-lg-4\">
              <div class=\"prototype-card p-4 text-dark\">
                <div class=\"d-flex justify-content-between align-items-center mb-3\"><strong>Prototype Brief</strong><span class=\"badge text-bg-warning\">Draft</span></div>
                <ul class=\"list-unstyled small text-body-secondary mb-0\">
                  <li>Target user: <strong class=\"text-dark\">{target_user}</strong></li>
                  <li>Primary entry: <strong class=\"text-dark\">{html.escape(str(contract.get('primary_entry', '')))}</strong></li>
                  <li>Primary exit: <strong class=\"text-dark\">{html.escape(str(contract.get('primary_exit', '')))}</strong></li>
                  <li>Source materials:</li>
                  <ul>{source_summary}</ul>
                </ul>
              </div>
            </div>
          </div>
        </section>
        <div class=\"row g-4\">
          <aside class=\"col-lg-3\"><div class=\"prototype-card prototype-sidebar p-3\"><div class=\"nav nav-pills flex-column gap-2\"><button class=\"btn btn-outline-primary text-start\" @click=\"tab='overview'\">Overview</button><button class=\"btn btn-outline-primary text-start\" @click=\"tab='jumps'\">Jump Map</button><button class=\"btn btn-outline-primary text-start\" @click=\"tab='states'\">States</button><button class=\"btn btn-outline-primary text-start\" data-bs-toggle=\"toast\" data-bs-target=\"#prototypeToast\" aria-label=\"Show toast sample\">Toast Sample</button></div></div></aside>
          <div class=\"col-lg-9\">
            <section class=\"prototype-card p-4 p-lg-5\">
              <div x-show=\"tab==='overview'\">{preview_surface}</div>
              <div x-show=\"tab==='jumps'\" class=\"row g-3\">{jump_cards}</div>
              <div x-show=\"tab==='states'\" class=\"pt-2\">{_render_state_badges(states)}</div>
            </section>
            {reference_pack_directory}
          </div>
        </div>
      </main>
      <div class=\"toast-container position-fixed bottom-0 end-0 p-3\"><div id=\"prototypeToast\" class=\"toast\" role=\"status\" aria-live=\"polite\" aria-atomic=\"true\"><div class=\"toast-header\"><strong class=\"me-auto\">Beacon Prototype</strong><button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"toast\" aria-label=\"Close toast\"></button></div><div class=\"toast-body\">Review and freeze this prototype before delivery gate checks.</div></div></div>
      <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/js/bootstrap.bundle.min.js\"></script>
    </div>
  </body>
</html>
"""


def _source_payload(feature: str, version: str, source_docs: list[dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "feature": feature,
        "version": version,
        "derived_from": [doc["type"] for doc in source_docs],
        "source_refs": [doc["relative_path"] for doc in source_docs],
        "source_fingerprints": {doc["type"]: doc["fingerprint"] for doc in source_docs},
        "contract_fields": sorted([key for key in contract.keys() if key not in {"feature", "version", "design_sources"}]),
        "sections": contract.get("sections", []),
    }


def write_prototype_bundle(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    plan_payload = compile_prototype_plan(project_root, version, feature)
    source_docs = load_source_documents(project_root, version, feature)
    contract = dict(plan_payload.get("contract") or {})
    theme = dict(plan_payload.get("theme") or derive_theme_tokens(contract))
    navigation_map = dict(plan_payload.get("navigation_map") or derive_navigation_map(contract))
    interaction_map = dict(plan_payload.get("interaction_map") or derive_interaction_map(contract))
    design_brief = compile_design_brief(feature, contract, source_docs)
    design_system_contract = compile_design_system_contract(contract, theme, design_brief)
    design_prompt_payload = compile_design_prompt_artifact(
        feature=feature,
        version=version,
        design_brief=design_brief,
        design_system_contract=design_system_contract,
        contract=contract,
        plan_payload=plan_payload,
    )
    ui_style_analysis = compile_ui_style_analysis(
        feature=feature,
        version=version,
        contract=contract,
        plan_payload=plan_payload,
        design_brief=design_brief,
        design_system_contract=design_system_contract,
    )
    reference_pack_v2 = _is_reference_pack_v2(contract, version)
    route_closure_contract = derive_route_closure_contract(feature, version, contract, navigation_map, interaction_map)
    implementation_map = derive_implementation_map(feature, version, route_closure_contract)
    source_payload = _source_payload(feature, version, source_docs, contract)

    files["root"].mkdir(parents=True, exist_ok=True)
    html_text = render_professional_prototype_html(feature, version, contract, theme, navigation_map, interaction_map, source_docs, plan_payload)
    files["index_html"].write_text(html_text, encoding="utf-8")
    _write_json(files["prototype_plan"], plan_payload)
    files["tokens_css"].write_text(_render_tokens_css(theme), encoding="utf-8")

    brief_payload = {
        "feature": feature,
        "version": version,
        "prototype_archetype": contract["prototype_archetype"],
        "target_user": contract.get("target_user", ""),
        "primary_flow": {
            "entry": contract.get("primary_entry"),
            "exit": contract.get("primary_exit"),
            "jumps": contract.get("jump_map", []),
        },
        "primary_cta": contract.get("primary_cta"),
        "design_intent": {
            "theme_mood": contract.get("theme_mood"),
            "brand_keywords": contract.get("brand_keywords", []),
            "surface_style": contract.get("surface_style"),
        },
        "design_governance_required": _design_governance_enabled(contract),
        "prototype_mode": "reference-pack-v2" if reference_pack_v2 else "minimal",
        "coverage_mode": contract.get("coverage_mode", "archetype-sections"),
    }

    page_specs = plan_payload.get("page_specs") if isinstance(plan_payload.get("page_specs"), list) else []
    required_pages = [str(page) for page in plan_payload.get("required_pages", []) if str(page).strip()]
    required_states = [str(state) for state in plan_payload.get("required_states", []) if str(state).strip()]
    generated_pages: list[str] = []
    generated_states: list[str] = []
    if reference_pack_v2:
        for key in ("pages_dir", "states_dir", "page_specs_dir"):
            if files[key].exists():
                shutil.rmtree(files[key])
            files[key].mkdir(parents=True, exist_ok=True)
        for spec in page_specs:
            if not isinstance(spec, dict):
                continue
            page_id = slugify_feature(str(spec.get("page_id") or ""))
            if not page_id:
                continue
            _write_json(files["page_specs_dir"] / f"{page_id}.json", spec)
            page_html = _render_reference_page_html(feature, spec, theme)
            (files["pages_dir"] / f"{page_id}.html").write_text(page_html, encoding="utf-8")
            generated_pages.append(page_id)
            for state_name in required_states:
                state_slug = slugify_feature(state_name)
                state_html = _render_reference_page_html(feature, spec, theme, state=state_name)
                state_file = files["states_dir"] / f"{page_id}--{state_slug}.html"
                state_file.write_text(state_html, encoding="utf-8")
                generated_states.append(f"{page_id}--{state_slug}")
    else:
        for spec in page_specs:
            if isinstance(spec, dict):
                page_id = slugify_feature(str(spec.get("page_id") or ""))
                if page_id:
                    generated_pages.append(page_id)

    compact_mode_detected = "compact coverage" in html_text.lower()
    coverage_payload = {
        "schema_version": "2.0" if reference_pack_v2 else "1.1",
        "feature": feature,
        "version": version,
        "prototype_mode": "reference-pack-v2" if reference_pack_v2 else "minimal",
        "required_pages": required_pages,
        "generated_pages": generated_pages,
        "missing_pages": [page for page in required_pages if page not in generated_pages],
        "required_states": required_states,
        "generated_state_variants": generated_states,
        "missing_state_variants": [
            f"{page}--{slugify_feature(state)}"
            for page in generated_pages
            for state in required_states
            if f"{page}--{slugify_feature(state)}" not in generated_states
        ],
        "compact_mode_detected": compact_mode_detected,
    }
    _write_json(files["coverage_report"], coverage_payload)

    manifest_payload = {
        "schema_version": "1.1",
        "feature": feature,
        "version": version,
        "ui_kit": DEFAULT_UI_KIT,
        "generator_version": DEFAULT_GENERATOR_VERSION,
        "prototype_type": contract["prototype_archetype"],
        "prototype_mode": "reference-pack-v2" if reference_pack_v2 else "minimal",
        "design_governance_required": _design_governance_enabled(contract),
        "artifacts": {
            key: str(path.relative_to(project_root))
            for key, path in files.items()
            if key != "root"
            and key not in {"review_json", "review_md", "web_guideline_review_json", "web_guideline_review_md"}
            and (
                reference_pack_v2
                or key not in {"pages_dir", "states_dir", "page_specs_dir"}
            )
        },
        "source_refs": source_payload["source_refs"],
        "status": "draft",
        "review_status": "missing",
    }
    freeze_payload = {
        "schema_version": "1.1",
        "feature": feature,
        "version": version,
        "status": "draft",
        "frozen_at": None,
        "ui_kit": DEFAULT_UI_KIT,
        "generator_version": DEFAULT_GENERATOR_VERSION,
        "source_fingerprints": source_payload["source_fingerprints"],
        "artifact_fingerprints": {
            "index_html": sha256_file(files["index_html"]),
            "prototype_plan": sha256_text(json.dumps(plan_payload, ensure_ascii=False, sort_keys=True)),
            "design_brief": sha256_text(json.dumps(design_brief, ensure_ascii=False, sort_keys=True)),
            "design_system_contract": sha256_text(json.dumps(design_system_contract, ensure_ascii=False, sort_keys=True)),
            "design_prompt_json": sha256_text(json.dumps(design_prompt_payload, ensure_ascii=False, sort_keys=True)),
            "ui_style_analysis_json": sha256_text(json.dumps(ui_style_analysis, ensure_ascii=False, sort_keys=True)),
            "prototype_brief": sha256_text(json.dumps(brief_payload, ensure_ascii=False, sort_keys=True)),
            "theme": sha256_text(json.dumps(theme, ensure_ascii=False, sort_keys=True)),
            "tokens_css": sha256_file(files["tokens_css"]),
            "navigation_map": sha256_text(json.dumps(navigation_map, ensure_ascii=False, sort_keys=True)),
            "interaction_map": sha256_text(json.dumps(interaction_map, ensure_ascii=False, sort_keys=True)),
            "coverage_report": sha256_text(json.dumps(coverage_payload, ensure_ascii=False, sort_keys=True)),
            "route_closure_contract": sha256_text(json.dumps(route_closure_contract, ensure_ascii=False, sort_keys=True)),
            "implementation_map": sha256_text(json.dumps(implementation_map, ensure_ascii=False, sort_keys=True)),
        },
    }
    _write_json(files["source_map"], source_payload)
    _write_json(files["design_brief"], design_brief)
    _write_json(files["design_system_contract"], design_system_contract)
    _write_json(files["design_prompt_json"], design_prompt_payload)
    files["design_prompt_md"].write_text(_render_design_prompt_markdown(design_prompt_payload), encoding="utf-8")
    _write_json(files["ui_style_analysis_json"], ui_style_analysis)
    files["ui_style_analysis_md"].write_text(_render_ui_style_analysis_markdown(ui_style_analysis), encoding="utf-8")
    _write_json(files["prototype_brief"], brief_payload)
    _write_json(files["theme"], theme)
    _write_json(files["navigation_map"], navigation_map)
    _write_json(files["interaction_map"], interaction_map)
    _write_json(files["coverage_report"], coverage_payload)
    _write_json(files["route_closure_contract"], route_closure_contract)
    _write_json(files["implementation_map"], implementation_map)
    _write_json(files["manifest"], manifest_payload)
    _write_json(files["freeze"], freeze_payload)
    return {
        "feature": feature,
        "version": version,
        "root": files["root"],
        "files": files,
        "source_docs": source_docs,
        "contract": contract,
        "prototype_mode": manifest_payload["prototype_mode"],
        "plan": plan_payload,
    }


def write_prototype_plan(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    plan_payload = compile_prototype_plan(project_root, version, feature)
    source_docs = load_source_documents(project_root, version, feature)
    contract = dict(plan_payload.get("contract") or {})
    design_brief = compile_design_brief(feature, contract, source_docs)
    design_system_contract = compile_design_system_contract(contract, dict(plan_payload.get("theme") or {}), design_brief)
    design_prompt_payload = compile_design_prompt_artifact(
        feature=feature,
        version=version,
        design_brief=design_brief,
        design_system_contract=design_system_contract,
        contract=contract,
        plan_payload=plan_payload,
    )
    ui_style_analysis = compile_ui_style_analysis(
        feature=feature,
        version=version,
        contract=contract,
        plan_payload=plan_payload,
        design_brief=design_brief,
        design_system_contract=design_system_contract,
    )
    files["root"].mkdir(parents=True, exist_ok=True)
    _write_json(files["prototype_plan"], plan_payload)
    _write_json(files["design_brief"], design_brief)
    _write_json(files["design_system_contract"], design_system_contract)
    _write_json(files["design_prompt_json"], design_prompt_payload)
    files["design_prompt_md"].write_text(_render_design_prompt_markdown(design_prompt_payload), encoding="utf-8")
    _write_json(files["ui_style_analysis_json"], ui_style_analysis)
    files["ui_style_analysis_md"].write_text(_render_ui_style_analysis_markdown(ui_style_analysis), encoding="utf-8")
    return {
        "feature": feature,
        "version": version,
        "plan": plan_payload,
        "path": files["prototype_plan"],
    }


def bind_prototype_bundle(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    if not files["implementation_map"].exists():
        raise FileNotFoundError(f"implementation map missing: {files['implementation_map']}")
    if not files["route_closure_contract"].exists():
        raise FileNotFoundError(f"route closure contract missing: {files['route_closure_contract']}")
    implementation_map = _read_json(files["implementation_map"])
    route_contract = _read_json(files["route_closure_contract"])
    closure_cases = route_contract.get("closure_cases") if isinstance(route_contract.get("closure_cases"), list) else []
    bindings = implementation_map.get("closure_bindings") if isinstance(implementation_map.get("closure_bindings"), list) else []
    bound_cases = 0
    for binding in bindings:
        if not isinstance(binding, dict):
            continue
        case_id = str(binding.get("case_id") or "").strip()
        case = next((item for item in closure_cases if isinstance(item, dict) and str(item.get("case_id") or "").strip() == case_id), {})
        target_surface = slugify_feature(str(case.get("target_surface_id") or "surface"))
        target_type = str(case.get("target_type") or "page").strip().lower()
        binding["binding_status"] = "bound"
        binding["runtime_target"] = f"/{target_surface}"
        if target_type == "tab":
            binding["state_target"] = target_surface
        elif not str(binding.get("state_target") or "").strip():
            binding["state_target"] = ""
        binding["drift_status"] = "closed"
        bound_cases += 1
    surfaces = implementation_map.get("surfaces") if isinstance(implementation_map.get("surfaces"), list) else []
    for surface in surfaces:
        if not isinstance(surface, dict):
            continue
        surface_id = slugify_feature(str(surface.get("surface_id") or "surface"))
        surface["implementation_type"] = "prototype-reference"
        surface["runtime_entry"] = f"/{surface_id}"
        surface["route_or_url"] = f"/{surface_id}"
        surface["theme_binding"] = "tokens.css"
        surface["interaction_binding"] = "route-closure-contract"
        surface["mounted"] = True
    implementation_map["adapter"] = "auto-bind"
    implementation_map["binding_status"] = "bound" if bound_cases else "draft"
    _write_json(files["implementation_map"], implementation_map)
    return {
        "feature": feature,
        "version": version,
        "bound_cases": bound_cases,
        "path": files["implementation_map"],
    }


def _check_html_contract(html_text: str, contract: dict[str, Any]) -> list[dict[str, Any]]:
    checks = []
    checks.append({
        "name": "primary_cta_rendered",
        "status": "pass" if str(contract.get("primary_cta", "")) in html_text else "fail",
        "message": "Primary CTA should be rendered in HTML.",
    })
    checks.append({
        "name": "jump_targets_rendered",
        "status": "pass" if all(str(item.get("to", "")) in html_text for item in contract.get("jump_map", [])) else "fail",
        "message": "Jump targets should appear in generated HTML.",
    })
    required_tokens = ["aria-label", "prefers-reduced-motion", ":focus-visible"]
    checks.append({
        "name": "accessibility_basics",
        "status": "pass" if all(token in html_text for token in required_tokens) else "fail",
        "message": "Generated HTML should include core accessibility markers.",
        "details": {"required_tokens": required_tokens},
    })
    checks.append({
        "name": "generic_shell_avoided",
        "status": "pass" if "Primary Review Card" not in html_text and "Step 1" not in html_text else "fail",
        "message": "Generated HTML should avoid the previous generic shell placeholders.",
    })
    return checks


def review_prototype_bundle(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    source_docs = load_source_documents(project_root, version, feature)
    if not source_docs:
        raise FileNotFoundError(f"No source documents found for '{feature}'")
    contract = merge_prototype_contract(feature, version, source_docs)
    plan_payload = _read_json(files["prototype_plan"]) if files["prototype_plan"].exists() else compile_prototype_plan(project_root, version, feature)
    design_brief = _read_json(files["design_brief"]) if files["design_brief"].exists() else compile_design_brief(feature, contract, source_docs)
    design_system_contract = (
        _read_json(files["design_system_contract"])
        if files["design_system_contract"].exists()
        else compile_design_system_contract(contract, dict(plan_payload.get("theme") or derive_theme_tokens(contract)), design_brief)
    )
    reference_pack_v2 = _is_reference_pack_v2(contract, version)
    route_closure_required = _feature_requires_route_closure(contract)
    design_governance_required = _design_governance_enabled(contract)
    required_artifacts = [
        "index_html",
        "manifest",
        "source_map",
        "prototype_brief",
        "theme",
        "navigation_map",
        "interaction_map",
        "prototype_plan",
        "tokens_css",
        "coverage_report",
    ]
    if route_closure_required:
        required_artifacts.extend(["route_closure_contract", "implementation_map"])
    if reference_pack_v2:
        required_artifacts.extend(["pages_dir", "states_dir", "page_specs_dir"])
    missing_artifacts = [name for name in required_artifacts if not files[name].exists()]
    checks: list[dict[str, Any]] = [
        {
            "name": "contract_resolved",
            "status": "pass",
            "message": "Prototype Contract resolved from PRD + User Story.",
        },
        {
            "name": "required_artifacts_present",
            "status": "pass" if not missing_artifacts else "fail",
            "message": "All contract artifacts should exist.",
            "details": {"missing": missing_artifacts},
        },
        {
            "name": "navigation_contract_present",
            "status": "pass" if files["navigation_map"].exists() else "fail",
            "message": "navigation-map.json should exist.",
        },
        {
            "name": "interaction_contract_present",
            "status": "pass" if files["interaction_map"].exists() else "fail",
            "message": "interaction-map.json should exist.",
        },
        {
            "name": "theme_contract_present",
            "status": "pass" if files["theme"].exists() else "fail",
            "message": "theme.json should exist.",
        },
        {
            "name": "prototype_plan_present",
            "status": "pass" if files["prototype_plan"].exists() else "fail",
            "message": "prototype-plan.json should exist.",
        },
        {
            "name": "tokens_css_present",
            "status": "pass" if files["tokens_css"].exists() else "fail",
            "message": "tokens.css should exist.",
        },
        {
            "name": "coverage_report_present",
            "status": "pass" if files["coverage_report"].exists() else "fail",
            "message": "coverage-report.json should exist.",
        },
    ]
    if design_governance_required:
        checks.extend(
            [
                {
                    "name": "design_brief_present",
                    "status": "pass" if files["design_brief"].exists() else "fail",
                    "message": "design-brief.json should exist.",
                },
                {
                    "name": "design_system_contract_present",
                    "status": "pass" if files["design_system_contract"].exists() else "fail",
                    "message": "design-system-contract.json should exist.",
                },
                {
                    "name": "design_prompt_present",
                    "status": "pass" if files["design_prompt_json"].exists() and files["design_prompt_md"].exists() else "fail",
                    "message": "design-prompt artifacts should exist.",
                },
                {
                    "name": "ui_style_analysis_present",
                    "status": "pass" if files["ui_style_analysis_json"].exists() and files["ui_style_analysis_md"].exists() else "fail",
                    "message": "ui-style-analysis artifacts should exist.",
                },
            ]
        )
    if route_closure_required:
        route_closure_payload = _read_json(files["route_closure_contract"])
        implementation_payload = _read_json(files["implementation_map"])
        closure_cases = route_closure_payload.get("closure_cases") if isinstance(route_closure_payload.get("closure_cases"), list) else []
        bindings = implementation_payload.get("closure_bindings") if isinstance(implementation_payload.get("closure_bindings"), list) else []
        binding_by_case = {
            str(item.get("case_id") or ""): item
            for item in bindings
            if isinstance(item, dict) and str(item.get("case_id") or "").strip()
        }
        unresolved_case_ids: list[str] = []
        drift_case_ids: list[str] = []
        fake_jump_case_ids: list[str] = []
        for case in closure_cases:
            if not isinstance(case, dict):
                continue
            case_id = str(case.get("case_id") or "").strip()
            binding = binding_by_case.get(case_id, {})
            binding_status = str(binding.get("binding_status") or "").strip().lower()
            drift_status = str(binding.get("drift_status") or "").strip().lower()
            if binding_status not in {"bound", "internal", "external"}:
                unresolved_case_ids.append(case_id)
            if drift_status in {"isolated", "fragile", "legacy-only", "tab-route-drift", "param-contract-mismatch"}:
                drift_case_ids.append(case_id)
            runtime_target = str(binding.get("runtime_target") or "").strip()
            if binding_status == "bound":
                if str(case.get("target_type") or "") == "tab":
                    if not str(binding.get("state_target") or "").strip():
                        fake_jump_case_ids.append(case_id)
                elif not runtime_target:
                    fake_jump_case_ids.append(case_id)
        checks.extend(
            [
                {
                    "name": "route_closure_contract_present",
                    "status": "pass" if files["route_closure_contract"].exists() else "fail",
                    "message": "route-closure-contract.json should exist.",
                },
                {
                    "name": "implementation_binding_manifest_present",
                    "status": "pass" if files["implementation_map"].exists() else "fail",
                    "message": "implementation-map.json should exist.",
                },
                {
                    "name": "route_closure_cases_present",
                    "status": "pass" if bool(closure_cases) else "fail",
                    "message": "route closure cases should exist for route-producing controls.",
                },
                {
                    "name": "route_closure_binding_complete",
                    "status": "pass" if not unresolved_case_ids else "fail",
                    "message": "every route closure case should bind to a runtime target or explicit internal/external path.",
                    "details": {"unresolved_case_ids": unresolved_case_ids},
                },
                {
                    "name": "route_closure_no_drift_markers",
                    "status": "pass" if not drift_case_ids else "fail",
                    "message": "route closure bindings should not remain isolated/fragile/legacy-only/tab drift.",
                    "details": {"drift_case_ids": drift_case_ids},
                },
                {
                    "name": "route_closure_no_fake_jump",
                    "status": "pass" if not fake_jump_case_ids else "fail",
                    "message": "bound route-producing controls should not degrade into fake jumps or toast-only placeholders.",
                    "details": {"fake_jump_case_ids": fake_jump_case_ids},
                },
            ]
        )

    if reference_pack_v2:
        required_pages = [slugify_feature(str(item)) for item in plan_payload.get("required_pages", []) if str(item).strip()]
        required_states = [slugify_feature(str(item)) for item in plan_payload.get("required_states", []) if str(item).strip()]
        page_specs = plan_payload.get("page_specs") if isinstance(plan_payload.get("page_specs"), list) else []
        page_spec_ids = {
            slugify_feature(str(item.get("page_id") or ""))
            for item in page_specs
            if isinstance(item, dict) and str(item.get("page_id") or "").strip()
        }
        missing_page_specs = sorted(page for page in required_pages if page not in page_spec_ids)
        missing_pages = sorted(page for page in required_pages if not (files["pages_dir"] / f"{page}.html").exists())
        missing_states: list[str] = []
        for page in required_pages:
            for state in required_states:
                state_id = f"{page}--{state}"
                if not (files["states_dir"] / f"{state_id}.html").exists():
                    missing_states.append(state_id)
        baseline_map = _baseline_map(contract)
        baseline_regression_pages = sorted(
            page for page, guards in baseline_map.items()
            if guards and (page in missing_pages or page in missing_page_specs)
        )
        compact_detected = False
        coverage_payload = _read_json(files["coverage_report"])
        if isinstance(coverage_payload, dict):
            compact_detected = bool(coverage_payload.get("compact_mode_detected"))
        if files["index_html"].exists() and "compact coverage" in files["index_html"].read_text(encoding="utf-8").lower():
            compact_detected = True
        cjk_parse_failed = bool((plan_payload.get("parser") or {}).get("cjk_parse_failed"))
        status_payload = evaluate_prototype_status(project_root, version, feature)
        stale_detected = bool(status_payload.get("stale"))

        manifest_payload = _read_json(files["manifest"])
        inconsistencies: list[str] = []
        artifact_map = manifest_payload.get("artifacts") if isinstance(manifest_payload.get("artifacts"), dict) else {}
        pending_review_artifacts = {
            "web_guideline_review_json",
            "web_guideline_review_md",
            "review_json",
            "review_md",
        }
        for artifact_name, rel_path in artifact_map.items():
            abs_path = project_root / str(rel_path)
            if artifact_name in {"pages_dir", "states_dir", "page_specs_dir"}:
                if not abs_path.exists() or not abs_path.is_dir():
                    inconsistencies.append(f"missing_dir:{artifact_name}")
                continue
            if artifact_name in pending_review_artifacts and not abs_path.exists():
                continue
            if not abs_path.exists():
                inconsistencies.append(f"missing_artifact:{artifact_name}")
        freeze_payload = _read_json(files["freeze"])
        if str(freeze_payload.get("status") or "") == "frozen":
            recorded = freeze_payload.get("artifact_fingerprints")
            if not isinstance(recorded, dict) or not recorded:
                inconsistencies.append("freeze_fingerprints_missing")
        checks.extend(
            [
                {
                    "name": "prototype_page_inventory_missing",
                    "status": "pass" if required_pages else "fail",
                    "message": "reference-pack-v2 requires required page inventory.",
                    "details": {"required_pages": required_pages},
                },
                {
                    "name": "prototype_required_page_missing",
                    "status": "pass" if not missing_pages else "fail",
                    "message": "all required pages must be generated.",
                    "details": {"missing_pages": missing_pages},
                },
                {
                    "name": "prototype_required_state_missing",
                    "status": "pass" if not missing_states else "fail",
                    "message": "all required state variants must be generated.",
                    "details": {"missing_states": missing_states[:50]},
                },
                {
                    "name": "prototype_compact_mode_detected",
                    "status": "fail" if compact_detected else "pass",
                    "message": "full-hi-fi reference pack must not degrade into compact coverage.",
                },
                {
                    "name": "prototype_baseline_regression",
                    "status": "pass" if not baseline_regression_pages else "fail",
                    "message": "baseline-protected pages must not regress.",
                    "details": {"baseline_regression_pages": baseline_regression_pages},
                },
                {
                    "name": "prototype_artifact_inconsistent",
                    "status": "pass" if not inconsistencies else "fail",
                    "message": "manifest/freeze/review artifacts should remain self-consistent.",
                    "details": {"inconsistencies": inconsistencies},
                },
                {
                    "name": "prototype_cjk_parse_failed",
                    "status": "fail" if cjk_parse_failed else "pass",
                    "message": "CJK punctuation parsing should not lose contract fields.",
                },
                {
                    "name": "prototype_stale",
                    "status": "fail" if stale_detected else "pass",
                    "message": "prototype should not be stale relative to source docs.",
                },
            ]
        )
    if files["index_html"].exists():
        html_text = files["index_html"].read_text(encoding="utf-8")
        checks.extend(_check_html_contract(html_text, contract))

    web_guideline_review = _audit_web_guidelines(files, contract, design_system_contract)
    _write_json(files["web_guideline_review_json"], web_guideline_review)
    guideline_lines = [
        f"# Web Guideline Review: {feature}",
        "",
        f"- source_url: `{WEB_GUIDELINE_SOURCE_URL}`",
        f"- source_fetched: `{web_guideline_review.get('source_fetched')}`",
        f"- design_review_outcome: `{web_guideline_review.get('design_review_outcome')}`",
        "",
        "## Findings",
    ]
    for finding in web_guideline_review.get("findings", []):
        if not isinstance(finding, dict):
            continue
        guideline_lines.append(
            f"- [{finding.get('severity')}] {finding.get('file')}:{finding.get('line')} "
            f"{finding.get('rule')}: {finding.get('message')}"
        )
    if len(guideline_lines) == 6:
        guideline_lines.append("- [pass] no findings")
    files["web_guideline_review_md"].write_text("\n".join(guideline_lines) + "\n", encoding="utf-8")
    if design_governance_required:
        critical_findings = int((web_guideline_review.get("severity_counts") or {}).get("critical", 0))
        checks.extend(
            [
                {
                    "name": "web_guideline_review_generated",
                    "status": "pass",
                    "message": "web-guideline-review artifacts should be generated.",
                },
                {
                    "name": "web_guideline_critical_findings_clear",
                    "status": "pass" if critical_findings == 0 else "fail",
                    "message": "critical web guideline findings must be cleared before design-governed freeze/gate.",
                    "details": {"critical_findings": critical_findings},
                },
            ]
        )

    overall_status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "version": version,
        "overall_status": overall_status,
        "design_review_outcome": web_guideline_review.get("design_review_outcome", "pass"),
        "contract_summary": {
            "prototype_archetype": contract["prototype_archetype"],
            "target_user": contract.get("target_user"),
            "primary_cta": contract.get("primary_cta"),
            "states": contract.get("states", []),
            "prototype_mode": "reference-pack-v2" if reference_pack_v2 else "minimal",
        },
        "checks": checks,
    }
    _write_json(files["review_json"], payload)
    lines = [
        f"# Prototype Review: {feature}",
        "",
        f"- version: `{version}`",
        f"- overall_status: `{overall_status}`",
        "",
        "## Checks",
    ]
    for item in checks:
        lines.append(f"- [{item['status']}] {item['name']}: {item['message']}")
    files["review_md"].write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = _read_json(files["manifest"])
    if manifest:
        manifest["review_status"] = overall_status
        manifest["design_review_outcome"] = web_guideline_review.get("design_review_outcome", "pass")
        artifacts = manifest.get("artifacts") if isinstance(manifest.get("artifacts"), dict) else {}
        artifacts.update(
            {
                "review_json": str(files["review_json"].relative_to(project_root)),
                "review_md": str(files["review_md"].relative_to(project_root)),
                "web_guideline_review_json": str(files["web_guideline_review_json"].relative_to(project_root)),
                "web_guideline_review_md": str(files["web_guideline_review_md"].relative_to(project_root)),
            }
        )
        manifest["artifacts"] = artifacts
        _write_json(files["manifest"], manifest)
    if design_governance_required:
        rewrite_payload = write_prototype_design_rewrite_input(
            project_root,
            version=version,
            feature=feature,
            review_payload=payload,
            guideline_payload=web_guideline_review,
            benchmark_refs=[
                str(files["review_json"].relative_to(project_root)),
                str(files["web_guideline_review_json"].relative_to(project_root)),
                str(files["design_brief"].relative_to(project_root)),
                str(files["design_system_contract"].relative_to(project_root)),
            ],
        )
        payload["iteration_writeback_path"] = rewrite_payload.get("path")
    return payload


def freeze_prototype(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    if not files["index_html"].exists():
        raise FileNotFoundError(f"Prototype HTML not found: {files['index_html']}")
    if not files["review_json"].exists():
        raise FileNotFoundError(f"Prototype review missing: {files['review_json']}")
    review_payload = _read_json(files["review_json"])
    if str(review_payload.get("overall_status", "fail")) != "pass":
        raise ValueError("Prototype review must pass before freeze")
    status_payload = evaluate_prototype_status(project_root, version, feature)
    if bool(status_payload.get("stale")):
        raise ValueError("Prototype is stale; regenerate/review before freeze")
    inconsistent_reasons = [
        str(reason)
        for reason in (status_payload.get("inconsistent_reasons") or [])
        if str(reason).strip()
    ]
    hard_inconsistencies = [
        reason
        for reason in inconsistent_reasons
        if not reason.startswith("fingerprint_mismatch:")
        and reason not in {"review_status_mismatch"}
    ]
    if hard_inconsistencies:
        raise ValueError(
            "Prototype artifacts are inconsistent; regenerate/review before freeze: "
            + ", ".join(hard_inconsistencies[:10])
        )
    source_docs = load_source_documents(project_root, version, feature)
    if not source_docs:
        raise FileNotFoundError(f"No source documents found for '{feature}'")
    payload = _read_json(files["freeze"])
    manifest = _read_json(files["manifest"])
    manifest["status"] = "frozen"
    manifest["review_status"] = review_payload.get("overall_status", "fail")
    _write_json(files["manifest"], manifest)
    payload.update(
        {
            "schema_version": "1.1",
            "feature": feature,
            "version": version,
            "status": "frozen",
            "frozen_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "ui_kit": DEFAULT_UI_KIT,
            "generator_version": DEFAULT_GENERATOR_VERSION,
            "source_fingerprints": {doc["type"]: doc["fingerprint"] for doc in source_docs},
            "artifact_fingerprints": {
                key: sha256_file(path)
                for key, path in files.items()
                if key
                in {
                    "index_html",
                    "prototype_plan",
                    "design_brief",
                    "design_system_contract",
                    "ui_style_analysis_json",
                    "ui_style_analysis_md",
                    "manifest",
                    "source_map",
                    "prototype_brief",
                    "theme",
                    "tokens_css",
                    "navigation_map",
                    "interaction_map",
                    "coverage_report",
                    "route_closure_contract",
                    "implementation_map",
                    "web_guideline_review_json",
                    "web_guideline_review_md",
                    "review_json",
                    "review_md",
                }
                and path.exists()
                and path.is_file()
            },
            "review_status": review_payload.get("overall_status", "fail"),
        }
    )
    _write_json(files["freeze"], payload)
    return payload


def evaluate_prototype_status(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    exists = files["index_html"].exists()
    freeze_payload = _read_json(files["freeze"])
    manifest_payload = _read_json(files["manifest"])
    review_payload = _read_json(files["review_json"])
    source_docs = load_source_documents(project_root, version, feature)
    current_source_hashes = {doc["type"]: doc["fingerprint"] for doc in source_docs}
    frozen_source_hashes = freeze_payload.get("source_fingerprints", {}) if isinstance(freeze_payload, dict) else {}
    status = "missing"
    stale = False
    inconsistent = False
    inconsistent_reasons: list[str] = []
    if exists:
        status = str(freeze_payload.get("status", "draft") or "draft")
        if status == "frozen" and current_source_hashes and frozen_source_hashes:
            stale = current_source_hashes != frozen_source_hashes
            if stale:
                status = "stale"
        elif status not in {"draft", "frozen", "stale", "inconsistent"}:
            status = "draft"
    review_status = str(review_payload.get("overall_status", "missing") or "missing") if review_payload else "missing"

    artifact_map = manifest_payload.get("artifacts") if isinstance(manifest_payload.get("artifacts"), dict) else {}
    for artifact_name, rel_path in artifact_map.items():
        abs_path = project_root / str(rel_path)
        if artifact_name in {"pages_dir", "states_dir", "page_specs_dir"}:
            if not abs_path.exists() or not abs_path.is_dir():
                inconsistent_reasons.append(f"missing_dir:{artifact_name}")
            continue
        if not abs_path.exists():
            inconsistent_reasons.append(f"missing_artifact:{artifact_name}")
    if (
        str(manifest_payload.get("review_status") or "").strip()
        and str(manifest_payload.get("review_status") or "").strip() != review_status
    ):
        inconsistent_reasons.append("review_status_mismatch")
    if status == "frozen" and review_status != "pass":
        inconsistent_reasons.append("frozen_without_pass_review")
    recorded_fingerprints = freeze_payload.get("artifact_fingerprints") if isinstance(freeze_payload.get("artifact_fingerprints"), dict) else {}
    for artifact_name, recorded in recorded_fingerprints.items():
        path = files.get(artifact_name)
        if not path or not path.exists() or not path.is_file():
            inconsistent_reasons.append(f"fingerprint_target_missing:{artifact_name}")
            continue
        if str(recorded or "").strip() and str(recorded) != sha256_file(path):
            inconsistent_reasons.append(f"fingerprint_mismatch:{artifact_name}")
    if inconsistent_reasons:
        inconsistent = True
        if status != "stale":
            status = "inconsistent"

    gate_ready = bool(exists and review_status == "pass" and status == "frozen" and not stale and not inconsistent)
    return {
        "feature": feature,
        "version": version,
        "exists": exists,
        "status": status,
        "stale": stale,
        "inconsistent": inconsistent,
        "inconsistent_reasons": inconsistent_reasons,
        "ui_kit": str(manifest_payload.get("ui_kit", DEFAULT_UI_KIT) or DEFAULT_UI_KIT),
        "review_status": review_status,
        "design_review_outcome": str(manifest_payload.get("design_review_outcome", "pass") or "pass"),
        "gate_ready": gate_ready,
        "root": files["root"],
        "files": files,
        "source_refs": [doc["relative_path"] for doc in source_docs],
        "current_source_fingerprints": current_source_hashes,
        "frozen_source_fingerprints": frozen_source_hashes,
    }


def resolve_prototype_requirement(
    project_root: Path,
    *,
    version: str | None = None,
    feature: str | None = None,
    state: dict[str, Any] | None = None,
) -> tuple[bool, str | None]:
    if isinstance(state, dict):
        enabled = bool(state.get("prototype_enabled"))
        run_feature = str(state.get("feature", "") or "") or feature
        if enabled and run_feature:
            return True, run_feature
    resolved_version = resolve_target_version(project_root, version or "auto")
    prototype_root = project_root / "docs" / "beacon" / resolved_version / "prototype"
    if feature and (prototype_root / slugify_feature(feature)).exists():
        return True, feature
    return False, feature
