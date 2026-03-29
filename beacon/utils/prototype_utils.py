"""Utilities for contract-driven Bootstrap prototype generation and governance."""

from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from beacon import __toolkit_version__
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
_LIST_KEYS = {"sections", "navigation", "brand_keywords", "states", "drift_guardrails"}
_COMPLEX_LIST_KEYS = {"jump_map", "modal_map", "drawer_map", "tab_map"}


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
        "manifest": root / "manifest.json",
        "source_map": root / "source-map.json",
        "freeze": root / "freeze.json",
        "prototype_brief": root / "prototype-brief.json",
        "theme": root / "theme.json",
        "navigation_map": root / "navigation-map.json",
        "interaction_map": root / "interaction-map.json",
        "route_closure_contract": root / "route-closure-contract.json",
        "implementation_map": root / "implementation-map.json",
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


def _split_list(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[|,;]", value or "") if item.strip()]


def _parse_jump_entries(value: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for chunk in [item.strip() for item in (value or "").split(";") if item.strip()]:
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


def _extract_as_a_user(text: str) -> str:
    match = re.search(r"\*\*As a\*\*\s+(.+?)[,，]\s*", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"^\s*As a\s+(.+?)$", text, re.IGNORECASE | re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def _normalize_contract_value(key: str, value: str) -> Any:
    if key in _LIST_KEYS:
        return _split_list(value)
    if key in _COMPLEX_LIST_KEYS:
        return _parse_jump_entries(value)
    return value.strip()


def extract_prototype_contract_from_source(source_doc: dict[str, Any]) -> dict[str, Any]:
    text = str(source_doc.get("text", ""))
    raw = _extract_yaml_like_pairs(text)
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
        }:
            contract[key] = _normalize_contract_value(key, value)
    if not contract.get("target_user") and source_doc.get("type") == "user-story":
        target_user = _extract_as_a_user(text)
        if target_user:
            contract["target_user"] = target_user
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
            merged[key] = value

    if merged.get("prototype_archetype"):
        merged["prototype_archetype"] = str(merged["prototype_archetype"]).strip().lower()

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
    return merged


def _feature_requires_route_closure(contract: dict[str, Any]) -> bool:
    value = str(contract.get("route_closure_required", "")).strip().lower()
    return value in {"true", "1", "yes", "required"}


def derive_theme_tokens(contract: dict[str, Any]) -> dict[str, Any]:
    primary = str(contract.get("theme_primary", "#3b82f6"))
    secondary = str(contract.get("theme_secondary", "#0f172a"))
    mood = str(contract.get("theme_mood", "confident"))
    archetype = str(contract.get("prototype_archetype", "dashboard"))
    spacing = "4-8-12-16-24-32" if archetype in {"dashboard", "admin-workbench"} else "8-12-16-24-32-48"
    radius = "14/18/24" if archetype == "marketing-page" else "10/14/18"
    shadow = "soft-elevation" if mood in {"warm", "premium"} else "disciplined-elevation"
    motion = "minimal-functional"
    return {
        "primary": primary,
        "secondary": secondary,
        "accent": primary,
        "mood": mood,
        "surface_style": contract.get("surface_style", "elevated-clean"),
        "brand_keywords": contract.get("brand_keywords", []),
        "typography": {
            "display": "Inter Display",
            "body": "Inter",
            "mono": "JetBrains Mono",
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


def render_professional_prototype_html(feature: str, version: str, contract: dict[str, Any], theme: dict[str, Any], navigation_map: dict[str, Any], interaction_map: dict[str, Any], source_docs: list[dict[str, Any]]) -> str:
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
      body {{ background: var(--beacon-bg); color: #0f172a; }}
      .prototype-nav {{ backdrop-filter: blur(16px); background: rgba(255,255,255,0.82); border-bottom: 1px solid rgba(148,163,184,0.18); }}
      .prototype-hero {{ background: linear-gradient(135deg, var(--beacon-secondary), #1e293b); color: white; border-radius: 28px; box-shadow: 0 28px 80px rgba(15,23,42,0.22); }}
      .prototype-card {{ border: 1px solid rgba(148,163,184,0.24); border-radius: var(--beacon-radius); background: rgba(255,255,255,0.88); box-shadow: 0 18px 50px rgba(15,23,42,0.08); }}
      .prototype-token {{ display: inline-flex; align-items: center; gap: .4rem; padding: .45rem .75rem; border-radius: 999px; background: rgba(59,130,246,0.12); color: var(--beacon-primary); font-size: .85rem; font-weight: 600; }}
      .btn-primary {{ background: var(--beacon-primary); border-color: var(--beacon-primary); box-shadow: 0 14px 30px color-mix(in srgb, var(--beacon-primary) 30%, transparent); }}
      .prototype-sidebar {{ position: sticky; top: 5rem; }}
      :focus-visible {{ outline: 3px solid color-mix(in srgb, var(--beacon-primary) 45%, transparent); outline-offset: 2px; }}
      @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} *, *::before, *::after {{ animation: none !important; transition: none !important; }} }}
    </style>
  </head>
  <body>
    <div x-data=\"{{ tab: 'overview' }}\">
      <nav class=\"navbar navbar-expand-lg prototype-nav sticky-top\">
        <div class=\"container py-2\">
          <a class=\"navbar-brand fw-semibold\" href=\"#top\">Beacon Prototype</a>
          <button class=\"navbar-toggler\" type=\"button\" data-bs-toggle=\"offcanvas\" data-bs-target=\"#prototypeDrawer\" aria-controls=\"prototypeDrawer\" aria-label=\"Open navigation\"><span class=\"navbar-toggler-icon\"></span></button>
          <div class=\"collapse navbar-collapse\"><div class=\"navbar-nav ms-auto\">{nav_links}</div></div>
        </div>
      </nav>
      <div class=\"offcanvas offcanvas-end\" tabindex=\"-1\" id=\"prototypeDrawer\" aria-labelledby=\"prototypeDrawerLabel\">
        <div class=\"offcanvas-header\"><h2 class=\"offcanvas-title h5 mb-0\" id=\"prototypeDrawerLabel\">Navigate</h2><button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"offcanvas\" aria-label=\"Close navigation\"></button></div>
        <div class=\"offcanvas-body d-flex flex-column gap-2\">{''.join(f'<a class="btn btn-outline-primary text-start" href="{html.escape(node["target"])}">{html.escape(node["label"])}</a>' for node in navigation_map.get("navigation_nodes", []))}</div>
      </div>
      <main class=\"container py-4 py-lg-5\" id=\"top\">
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
              <div class=\"d-flex flex-wrap gap-3\"><button class=\"btn btn-primary btn-lg\">{primary_cta}</button><button class=\"btn btn-outline-light btn-lg\">{secondary_cta}</button></div>
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
    route_closure_contract = derive_route_closure_contract(feature, version, contract, navigation_map, interaction_map)
    implementation_map = derive_implementation_map(feature, version, route_closure_contract)
    source_payload = _source_payload(feature, version, source_docs, contract)

    files["root"].mkdir(parents=True, exist_ok=True)
    html_text = render_professional_prototype_html(feature, version, contract, theme, navigation_map, interaction_map, source_docs)
    files["index_html"].write_text(html_text, encoding="utf-8")

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
    }
    manifest_payload = {
        "schema_version": "1.1",
        "feature": feature,
        "version": version,
        "ui_kit": DEFAULT_UI_KIT,
        "generator_version": DEFAULT_GENERATOR_VERSION,
        "prototype_type": contract["prototype_archetype"],
        "artifacts": {
            key: str(path.relative_to(project_root))
            for key, path in files.items()
            if key != "root"
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
            "prototype_brief": sha256_text(json.dumps(brief_payload, ensure_ascii=False, sort_keys=True)),
            "theme": sha256_text(json.dumps(theme, ensure_ascii=False, sort_keys=True)),
            "navigation_map": sha256_text(json.dumps(navigation_map, ensure_ascii=False, sort_keys=True)),
            "interaction_map": sha256_text(json.dumps(interaction_map, ensure_ascii=False, sort_keys=True)),
            "route_closure_contract": sha256_text(json.dumps(route_closure_contract, ensure_ascii=False, sort_keys=True)),
            "implementation_map": sha256_text(json.dumps(implementation_map, ensure_ascii=False, sort_keys=True)),
        },
    }
    _write_json(files["source_map"], source_payload)
    _write_json(files["prototype_brief"], brief_payload)
    _write_json(files["theme"], theme)
    _write_json(files["navigation_map"], navigation_map)
    _write_json(files["interaction_map"], interaction_map)
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
    route_closure_required = _feature_requires_route_closure(contract)
    required_artifacts = ["index_html", "manifest", "source_map", "prototype_brief", "theme", "navigation_map", "interaction_map"]
    if route_closure_required:
        required_artifacts.extend(["route_closure_contract", "implementation_map"])
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
    ]
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
    if files["index_html"].exists():
        html_text = files["index_html"].read_text(encoding="utf-8")
        checks.extend(_check_html_contract(html_text, contract))

    overall_status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "version": version,
        "overall_status": overall_status,
        "contract_summary": {
            "prototype_archetype": contract["prototype_archetype"],
            "target_user": contract.get("target_user"),
            "primary_cta": contract.get("primary_cta"),
            "states": contract.get("states", []),
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
        _write_json(files["manifest"], manifest)
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
    source_docs = load_source_documents(project_root, version, feature)
    if not source_docs:
        raise FileNotFoundError(f"No source documents found for '{feature}'")
    payload = _read_json(files["freeze"])
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
                if key in {"index_html", "manifest", "source_map", "prototype_brief", "theme", "navigation_map", "interaction_map", "route_closure_contract", "implementation_map", "review_json", "review_md"}
            },
            "review_status": review_payload.get("overall_status", "fail"),
        }
    )
    _write_json(files["freeze"], payload)
    manifest = _read_json(files["manifest"])
    manifest["status"] = "frozen"
    manifest["review_status"] = review_payload.get("overall_status", "fail")
    _write_json(files["manifest"], manifest)
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
    if exists:
        status = str(freeze_payload.get("status", "draft") or "draft")
        if status == "frozen" and current_source_hashes and frozen_source_hashes:
            stale = current_source_hashes != frozen_source_hashes
            if stale:
                status = "stale"
        elif status not in {"draft", "frozen", "stale"}:
            status = "draft"
    review_status = str(review_payload.get("overall_status", "missing") or "missing") if review_payload else "missing"
    gate_ready = bool(exists and review_status == "pass" and status == "frozen")
    return {
        "feature": feature,
        "version": version,
        "exists": exists,
        "status": status,
        "stale": stale,
        "ui_kit": str(manifest_payload.get("ui_kit", DEFAULT_UI_KIT) or DEFAULT_UI_KIT),
        "review_status": review_status,
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
