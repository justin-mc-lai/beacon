"""Complete DESIGN.md baseline + unattended visual defaults for Beacon.

Absorbs open-source UI agent principles into Beacon-owned design truth without
runtime dependency on external skills.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beacon.utils.versioning import resolve_target_version

OPEN_SOURCE_UI_AGENT_PRINCIPLES: dict[str, dict[str, Any]] = {
    "vibe-to-ui": {
        "routes": ["explore", "extract"],
        "absorbed_into": ["information_hierarchy", "layout_models", "first_screen_intent"],
        "execution_kind": "execution-capable",
    },
    "ui-ux-pro-max": {
        "routes": ["system"],
        "absorbed_into": ["tokens", "component_system", "states", "responsive", "accessibility"],
        "execution_kind": "execution-capable",
    },
    "impeccable": {
        "routes": ["review", "polish"],
        "absorbed_into": ["spacing", "focus_visibility", "microcopy", "ship_readiness", "anti_ai_ui"],
        "execution_kind": "execution-capable",
    },
    "awesome-design-md": {
        "routes": ["library"],
        "absorbed_into": ["pattern_references_only"],
        "execution_kind": "reference-only",
    },
}

PRESET_VISUAL_TOKENS: dict[str, dict[str, str]] = {
    "restrained-product": {
        "source": "apple",
        "label": "Restrained Product",
        "bg": "#F5F5F7",
        "fg": "#1D1D1F",
        "card": "#FFFFFF",
        "border": "#D2D2D7",
        "muted": "#6E6E73",
        "primary": "#0071E3",
        "primary_fg": "#FFFFFF",
        "danger": "#FF3B30",
        "success": "#34C759",
        "warning": "#FF9F0A",
        "radius": "8px",
        "font": '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif',
        "density": "comfortable",
    },
    "operator-console": {
        "source": "vercel",
        "label": "Operator Console",
        "bg": "#FAFAFA",
        "fg": "#171717",
        "card": "#FFFFFF",
        "border": "#E5E5E5",
        "muted": "#737373",
        "primary": "#000000",
        "primary_fg": "#FFFFFF",
        "danger": "#E00",
        "success": "#0A7",
        "warning": "#F5A623",
        "radius": "6px",
        "font": 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif',
        "density": "compact",
    },
    "editorial-calm": {
        "source": "apple+vercel hybrid",
        "label": "Editorial Calm",
        "bg": "#FBFBFA",
        "fg": "#222222",
        "card": "#FFFFFF",
        "border": "#E8E6E3",
        "muted": "#7A7A7A",
        "primary": "#2F6FED",
        "primary_fg": "#FFFFFF",
        "danger": "#C0392B",
        "success": "#1E8E3E",
        "warning": "#B7791F",
        "radius": "10px",
        "font": 'ui-sans-serif, system-ui, "Iowan Old Style", "Palatino Linotype", serif',
        "density": "airy",
    },
}

_PRESET_ALIASES = {
    "apple-inspired-design-md": "restrained-product",
    "vercel-inspired-design-md": "operator-console",
    "apple": "restrained-product",
    "vercel": "operator-console",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _rel(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def resolve_design_preset(preset: str | None) -> dict[str, str]:
    key = str(preset or "restrained-product").strip() or "restrained-product"
    key = _PRESET_ALIASES.get(key, key)
    tokens = dict(PRESET_VISUAL_TOKENS.get(key) or PRESET_VISUAL_TOKENS["restrained-product"])
    tokens["preset"] = key if key in PRESET_VISUAL_TOKENS else "restrained-product"
    if key not in PRESET_VISUAL_TOKENS:
        tokens = dict(PRESET_VISUAL_TOKENS["restrained-product"])
        tokens["preset"] = "restrained-product"
    return tokens



def render_complete_design_md(
    *,
    product_name: str = "Product",
    preset: str = "restrained-product",
    existing_design_md: str = "",
    version: str = "v1.6.7",
    mode: str = "baseline",
    surface: str = "web",
    surface_decision: dict | None = None,
) -> str:
    from beacon.utils.design_surfaces import (
        SURFACE_PACKS,
        google_yaml_frontmatter,
        resolve_surface,
        surface_copy_elements,
    )

    surface_key = resolve_surface(surface)
    if surface_key == "auto" or surface_key not in SURFACE_PACKS:
        surface_key = "web"
    pack = SURFACE_PACKS[surface_key]
    if not preset or preset == "restrained-product":
        preset = str(pack.get("preset") or preset)
    tokens = resolve_design_preset(preset)
    elements = surface_copy_elements(surface_key)
    decision = surface_decision if isinstance(surface_decision, dict) else {}

    anti_forbidden = [
        "gradient text",
        "purple-to-blue ai gradient",
        "card inside card",
        "accent side stripe",
        "glassmorphism used as decoration",
        "bounce_or_elastic_easing",
    ]
    interaction_rules = [
        "focus-visible must exist for keyboard users",
        "primary interactive targets should be at least 44x44",
        "button hierarchy must distinguish primary from secondary actions",
        "empty/loading/error/success states must be intentional and explicit",
    ]
    existing = str(existing_design_md or "").strip()
    fine_tune_note = ""
    if mode == "fine_tune" and existing:
        fine_tune_note = f"""

## Fine-tune Against Existing DESIGN.md

An existing project DESIGN.md was detected. Unattended baseline **does not erase** project-specific identity.
Apply this file as the **default visual operating system**, then re-assert only project-specific deltas:

1. Keep project brand names, product-specific components, and domain badges already frozen in truth.
2. Prefer existing token names if they already map 1:1 to CSS variables.
3. Replace only missing axes: tokens, anti-AI UI rules, state coverage, accessibility, Do/Don't.
4. Route promise-changing visual changes through `beacon change ... --refreeze-chain` before implementation.

Previous DESIGN.md size: {len(existing)} chars (preserved; not auto-deleted).
"""

    principle_rows = "\n".join(
        f"| {name} | {', '.join(meta['routes'])} | {meta['execution_kind']} | {', '.join(meta['absorbed_into'])} |"
        for name, meta in OPEN_SOURCE_UI_AGENT_PRINCIPLES.items()
    )
    interaction_bullets = "\n".join(f"- {rule}" for rule in interaction_rules)
    dont_bullets = "\n".join(f"- {item}" for item in anti_forbidden)
    surface_do = "\n".join(f"- {x}" for x in (pack.get("do") or []))
    surface_dont = "\n".join(f"- {x}" for x in (pack.get("dont") or []))
    css_lines = "\n".join(f"  {k}: {v};" for k, v in elements["css_variables"].items())
    front = google_yaml_frontmatter(surface_key, product_name=product_name)

    return f"""{front}

# DESIGN.md — {product_name}

Status: ready
Preset: `{tokens['preset']}` ({tokens['label']}, source: {tokens['source']})
Beacon version context: `{version}`
Generation: unattended-complete-baseline
Delivery surface: `{surface_key}` ({pack['label']})
Surface auto-reason: {decision.get('reason') or 'explicit'}
Nav pattern: {pack['nav']}
Primary layout pattern: {pack['primary_pattern']}
Touch min: {pack['touch_min']} · Density: {pack['density']}

This file is the **project-level visual truth**. Implement / QA / UI ship gates treat it as binding when present.
It is complete enough to ship a coherent UI **without human design decisions**, while remaining fine-tunable against an existing DESIGN.md.

## Open-source UI agent principles (Beacon absorption)

Beacon design routes preserve upstream capabilities but **do not** treat them as runtime truth:

| Upstream | Routes | Kind | Absorbed into this DESIGN.md |
|----------|--------|------|------------------------------|
{principle_rows}

Rules:
- `awesome-design-md` is **reference-only** (patterns / analogies). Never authority for ship.
- `vibe-to-ui` / `ui-ux-pro-max` / `impeccable` may generate candidates; accepted facts still bind via Beacon truth / this DESIGN.md / version `docs/beacon/<v>/design/*`.
- Google `design.md` YAML front matter above is **normative machine-readable tokens**; prose below is rationale.
- No external design skill is required at runtime to apply this baseline (`external_reference_runtime_dependency=false`).

## Overview

{pack['label']}. Density `{pack['density']}`. Navigation: {pack['nav']}. Primary pattern: {pack['primary_pattern']}.

## Design philosophy

1. **Lazy-user first**: first screen answers the main job before secondary chrome.
2. **Recognition over recall**: labels and primary actions must be obvious.
3. **State honesty**: empty / loading / error / success / blocked / stale / recovery are first-class.
4. **Restrained density**: no marketing hero, no fake dashboard charts, no AI gradient theater.
5. **Domain-bound chrome**: badges and primary buttons bind to business FSM states when a domain FSM exists.
6. **Fine-tune, don't freestyle**: when a prior DESIGN.md exists, extend it; do not invent a second design system.
7. **Surface honesty**: PC 中台 / Web / H5 / Client each keep their IA; do not paste mobile IA onto desktop console.

## Colors

See YAML `colors` tokens. Primary drives interaction; neutrals carry structure.

## Typography

See YAML `typography` tokens. Prefer system stacks for product OS feel.

## Layout

- Base grid from YAML `spacing`.
- First screen order: **status → primary action → supporting list → secondary disclosure**.
- Surface nav: {pack['nav']}.

## Elevation & Depth

- Prefer borders over shadows.
- No glassmorphism decoration.
- One elevation language only.

## Shapes

See YAML `rounded` scale.

## Components

See YAML `components` map. Implement maps these tokens to real components.

## Delivery surface pack (copy-ready)

Surface: `{surface_key}` — {pack['label']}

### Surface Do
{surface_do}

### Surface Don't
{surface_dont}

### CSS variables (surface)

```css
:root {{
{css_lines}
}}
```

## Visual tokens (CSS variables legacy bridge)

```css
:root {{
  --bg: {tokens['bg']};
  --fg: {tokens['fg']};
  --card: {tokens['card']};
  --border: {tokens['border']};
  --muted: {tokens['muted']};
  --primary: {tokens['primary']};
  --primary-fg: {tokens['primary_fg']};
  --danger: {tokens['danger']};
  --success: {tokens['success']};
  --warning: {tokens['warning']};
  --radius: {tokens['radius']};
  --font: {tokens['font']};
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --touch-min: {pack['touch_min']};
  --density: {pack['density']};
}}
```

## Interaction principles

{interaction_bullets}
- Keyboard: Tab order matches visual order; Escape closes overlays.
- Loading: skeletons or explicit progress; never blank freeze without explanation.
- Navigation: surface-native ({pack['nav']}).
- Handoff: deep-links restore page + entity + state.

## UI state coverage (required)

| State | User sees | Primary action |
|-------|-----------|----------------|
| empty | honest empty + why | create / import / connect |
| loading | progress or skeleton | cancel if long-running |
| error | cause + recovery | retry / fix config |
| success | confirmation without parade | next step or dismiss |
| blocked | gate reason | unblock path |
| stale | data age / refresh needed | refresh |
| recovery | post-failure path | resume / reset |

When Domain FSM exists, bind business states via `ui-state-matrix.md`. Ship gates require matrix states ⊆ domain states.

## Do's and Don'ts

### Do
- Quiet neutrals + one accent
- Explicit empty/loading/error/success
- Domain badges and disabled illegal actions
- Focus-visible rings and adequate targets
{surface_do}

### Don't
{dont_bullets}
- Invent FSM states not in truth
- Copy reference-library aesthetics as project law
- Cross-surface IA paste (e.g. H5 bottom tabs on PC 中台)
{surface_dont}

## Accessibility & responsive

- Contrast: body text meets WCAG AA intent.
- Focus visibility: required.
- Touch/pointer targets: surface min `{pack['touch_min']}` (critical actions still prefer 44px).
- Responsive: collapse secondary detail before primary judgment content.
- Motion: no bounce/elastic; prefer 150–200ms.

## Version-wide contracts

- `docs/beacon/<version>/design/style.md`
- `docs/beacon/<version>/design/component-system.md`
- `docs/beacon/<version>/design/interaction-contract.md`
- `docs/beacon/<version>/design/state-matrix.md`
- `docs/beacon/<version>/design/surfaces/<surface>.DESIGN.md` (copy-ready surface snapshot)
- feature `ui-state-matrix.md` bound to Domain FSM

## Unattended default & fine-tune policy

1. **No human design decision**: use this DESIGN.md + surface pack as visual OS.
2. **Existing DESIGN.md**: fine-tune mode keeps brand/domain specifics; fills missing axes.
3. **Requirement truth claims visual delivery** (`ux_required` / UI pages): auto-select surface from truth keywords, then freeze DESIGN.md before implement.
4. **Upstream polish**: `beacon design route polish|review|system|explore` may propose deltas; bind via prototype adapt / change-refreeze.
5. **Implement hard rule**: when DESIGN.md exists, LLM must not freestyle colors/spacing/components.
{fine_tune_note}
## Truth update policy

Update this file when accepted design facts become project-level truth.
Design support output is not truth until bound. Promise-changing visual changes require change/refreeze before implementation.
"""


VERSION_STYLE_TEMPLATE = """# Version Design Style

Status: ready

## Token inheritance

Inherit project `DESIGN.md` CSS variables and YAML front matter tokens. Version may tighten density or accent only when product truth allows.

## Atmosphere

- Quiet neutrals, one accent, no decorative gradients.
- Prefer system fonts declared in DESIGN.md.
- Keep first-screen judgment content above secondary metadata.

## Density

Follow DESIGN.md `--density` (comfortable / compact / airy). Operator surfaces may go compact without reducing critical targets below safe minimums.
"""

VERSION_COMPONENT_SYSTEM_TEMPLATE = """# Component System Contract

Status: ready

## Source-bound choices

Component selection should prefer the stack already in the repo. Do not introduce a second component library without change/refreeze.

## Required components

Primary/secondary/destructive buttons, inputs, cards, badges, tables/lists, empty, error, loading, toast/inline alert, modal/drawer (if used).

## States per interactive component

default · hover · focus-visible · active · disabled · loading · error

## Accessibility

Every interactive control has a name, focus style, and keyboard path.
"""

VERSION_INTERACTION_CONTRACT_TEMPLATE = """# Interaction Contract

Status: ready

## Feedback

- Success: quiet confirmation + next action
- Error: cause + recovery
- Blocked: gate reason + unblock path

## Navigation

- One primary nav region matching delivery surface
- Secondary tools fold into overflow when crowded
- Deep links restore entity + state

## Recovery

Blocked/stale/error always expose a recovery action. Never dead-end the user on a red banner only.
"""

VERSION_STATE_MATRIX_TEMPLATE = """# UI State Matrix (version-wide)

Status: ready

| UI state | Page expectation | Primary action |
|----------|------------------|----------------|
| empty | honest empty + why | create/import/connect |
| loading | progress/skeleton | cancel if long |
| error | cause + recovery | retry/fix |
| success | short confirmation | next/dismiss |
| blocked | gate reason | unblock |
| stale | age / freshness | refresh |
| recovery | post-failure path | resume/reset |

Feature packages with Domain FSM must add a **business-state** matrix (`ui-state-matrix.md`) binding badges and primary actions to domain states.
"""


def _write_file(path: Path, content: str, *, force: bool) -> str:
    existed = path.exists()
    if existed and not force:
        return "exists"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "overwritten" if existed else "written"


def synthesize_unattended_design_baseline(
    project_root: Path,
    version: str,
    *,
    preset: str = "restrained-product",
    surface: str = "auto",
    force: bool = False,
    write_version_contracts: bool = True,
    product_name: str = "",
    truth_markdown: str = "",
    company_template: str = "auto",
) -> dict[str, Any]:
    """Unattended visual baseline with surface auto-select from requirement truth."""
    from beacon.utils.design_contract import design_truth_paths, write_version_design_contracts
    from beacon.utils.design_surfaces import (
        SURFACE_PACKS,
        auto_select_surface_from_text,
        resolve_surface,
        scan_truth_for_ux,
    )

    project_root = project_root.expanduser().resolve()
    resolved = resolve_target_version(project_root, version)
    name = str(product_name or project_root.name or "Product").strip() or "Product"

    truth_bits: list[str] = [str(truth_markdown or "")]
    docs = project_root / "docs" / "beacon" / resolved
    if docs.exists():
        for p in list(docs.rglob("truth.md"))[:40]:
            try:
                truth_bits.append(p.read_text(encoding="utf-8")[:8000])
            except OSError:
                pass
    product_md = project_root / "PRODUCT.md"
    if product_md.exists():
        try:
            truth_bits.append(product_md.read_text(encoding="utf-8")[:8000])
        except OSError:
            pass

    surface_key = resolve_surface(surface)
    if surface_key == "auto":
        decision = auto_select_surface_from_text(*truth_bits)
        surface_key = str(decision["surface"])
    else:
        decision = {
            "surface": surface_key,
            "label": SURFACE_PACKS.get(surface_key, {}).get("label", surface_key),
            "preset": SURFACE_PACKS.get(surface_key, {}).get("preset", preset),
            "reason": "explicit",
            "scores": {},
            "hits": [],
        }
    pack_preset = str(SURFACE_PACKS.get(surface_key, {}).get("preset") or preset)
    if not preset or preset == "restrained-product":
        preset = pack_preset
    from beacon.utils.design_company_templates import auto_select_company_template, COMPANY_DESIGN_TEMPLATES
    if company_template and company_template != "auto" and company_template in COMPANY_DESIGN_TEMPLATES:
        company_decision = {
            "company_template": company_template,
            **{k: COMPANY_DESIGN_TEMPLATES[company_template].get(k) for k in ("label", "inspired_by", "default_surface", "default_preset", "colors")},
            "reason": "explicit",
            "catalog_size": len(COMPANY_DESIGN_TEMPLATES),
            "hits": [],
            "scores": {},
        }
    else:
        company_decision = auto_select_company_template(*truth_bits, surface=surface_key)
    if company_decision.get("default_preset") and (not preset or preset == "restrained-product"):
        preset = str(company_decision.get("default_preset"))
    tokens = resolve_design_preset(preset)
    # overlay commercial colors into token bridge when present
    colors = company_decision.get("colors") if isinstance(company_decision.get("colors"), dict) else {}
    if colors:
        if colors.get("primary"):
            tokens["primary"] = str(colors.get("primary"))
        if colors.get("on-primary"):
            tokens["primary_fg"] = str(colors.get("on-primary"))
        if colors.get("canvas") or colors.get("neutral"):
            tokens["bg"] = str(colors.get("neutral") or colors.get("canvas"))
        if colors.get("canvas"):
            tokens["card"] = str(colors.get("canvas"))
        if colors.get("border"):
            tokens["border"] = str(colors.get("border"))
        if colors.get("secondary") or colors.get("muted"):
            tokens["muted"] = str(colors.get("muted") or colors.get("secondary"))
        if colors.get("danger"):
            tokens["danger"] = str(colors.get("danger"))
        if colors.get("success"):
            tokens["success"] = str(colors.get("success"))
        if colors.get("warning"):
            tokens["warning"] = str(colors.get("warning"))
        tokens["company_template"] = str(company_decision.get("company_template") or "")
        tokens["inspired_by"] = str(company_decision.get("inspired_by") or "")
    ux_scan = scan_truth_for_ux("\n".join(truth_bits))

    design_path = project_root / "DESIGN.md"
    existing = design_path.read_text(encoding="utf-8") if design_path.exists() else ""
    writes: dict[str, Any] = {}
    mode = "baseline"
    status = "ready"

    if existing and not force:
        mode = "fine_tune"
        status = "fine_tune_proposed"
        proposal = render_complete_design_md(
            product_name=name,
            preset=tokens.get("preset", "restrained-product"),
            existing_design_md=existing,
            version=resolved,
            mode="fine_tune",
            surface=surface_key,
            surface_decision=decision,
        )
        proposal_path = project_root / "docs" / "beacon" / resolved / "design" / "fine-tune-proposal.md"
        writes["fine_tune_proposal"] = _write_file(proposal_path, proposal, force=True)
        writes["design_truth"] = "exists_preserved"
    else:
        body = render_complete_design_md(
            product_name=name,
            preset=tokens.get("preset", "restrained-product"),
            existing_design_md=existing,
            version=resolved,
            mode="baseline",
            surface=surface_key,
            surface_decision=decision,
        )
        writes["design_truth"] = _write_file(design_path, body, force=force or not design_path.exists())

    if write_version_contracts:
        version_payload = write_version_design_contracts(
            project_root,
            resolved,
            force=force,
            include_project_truth=False,
        )
        style = project_root / "docs" / "beacon" / resolved / "design" / "style.md"
        if force or not style.exists() or "Status: draft" in style.read_text(encoding="utf-8"):
            writes["version_style"] = _write_file(style, VERSION_STYLE_TEMPLATE, force=True)
            writes["version_component_system"] = _write_file(
                project_root / "docs" / "beacon" / resolved / "design" / "component-system.md",
                VERSION_COMPONENT_SYSTEM_TEMPLATE,
                force=True,
            )
            writes["version_interaction"] = _write_file(
                project_root / "docs" / "beacon" / resolved / "design" / "interaction-contract.md",
                VERSION_INTERACTION_CONTRACT_TEMPLATE,
                force=True,
            )
            writes["version_state_matrix"] = _write_file(
                project_root / "docs" / "beacon" / resolved / "design" / "state-matrix.md",
                VERSION_STATE_MATRIX_TEMPLATE,
                force=True,
            )
        writes["version_contracts"] = version_payload.get("writes", {})

    # materialize all surface examples (copy-ready library inside skill/docs)
    surface_example_dir = project_root / "docs" / "beacon" / resolved / "design" / "surfaces"
    surface_example_dir.mkdir(parents=True, exist_ok=True)
    for skey in SURFACE_PACKS:
        example_path = surface_example_dir / f"{skey}.DESIGN.md"
        example_body = render_complete_design_md(
            product_name=f"{name} ({SURFACE_PACKS[skey]['label']})",
            preset=str(SURFACE_PACKS[skey].get("preset") or "restrained-product"),
            version=resolved,
            mode="baseline",
            surface=skey,
            surface_decision={"reason": "surface library materialize", "label": SURFACE_PACKS[skey]["label"]},
        )
        writes[f"surface_example_{skey}"] = _write_file(example_path, example_body, force=True)

    paths = design_truth_paths(project_root, resolved)
    machine_dir = project_root / paths["machine_design_projection"]
    machine_dir.mkdir(parents=True, exist_ok=True)
    projection_path = machine_dir / "unattended-design-baseline.json"
    projection = {
        "schema_version": "1.0",
        "version": resolved,
        "status": status,
        "mode": mode,
        "preset": tokens.get("preset"),
        "preset_label": tokens.get("label"),
        "preset_source": tokens.get("source"),
        "surface": surface_key,
        "surface_decision": decision,
        "company_template": company_decision,
        "visual_delivery_claimed": bool(ux_scan.get("visual_delivery_claimed")),
        "ux_signals": ux_scan.get("signals") or [],
        "open_source_ui_agent_principles": OPEN_SOURCE_UI_AGENT_PRINCIPLES,
        "tokens": tokens,
        "existing_design_preserved": bool(existing and not force),
        "writes": writes,
        "generated_at": _now_iso(),
        "operator_next": {
            "accept_baseline": "keep DESIGN.md / merge fine-tune-proposal sections",
            "polish": f'beacon design route polish "<feature>" --project {project_root} --version {resolved} --json',
            "system": f'beacon design route system "<feature>" --project {project_root} --version {resolved} --json',
            "bind": f'beacon prototype adapt "<feature>" --project {project_root} --version {resolved} --design-result-ref <accepted>',
            "implement_rule": "When DESIGN.md exists, implement must align tokens/components; freestyle UI is process drift",
        },
    }
    projection_path.write_text(json.dumps(projection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    writes["machine_projection"] = _rel(project_root, projection_path)

    return {
        "schema_version": "1.0",
        "version": resolved,
        "status": status,
        "mode": mode,
        "preset": tokens.get("preset"),
        "surface": surface_key,
        "surface_decision": decision,
        "company_template": company_decision,
        "visual_delivery_claimed": bool(ux_scan.get("visual_delivery_claimed")),
        "ux_signals": ux_scan.get("signals") or [],
        "product_name": name,
        "design_path": "DESIGN.md",
        "fine_tune_proposal_path": (
            f"docs/beacon/{resolved}/design/fine-tune-proposal.md" if mode == "fine_tune" else ""
        ),
        "surface_examples_dir": f"docs/beacon/{resolved}/design/surfaces",
        "open_source_ui_agent_principles": OPEN_SOURCE_UI_AGENT_PRINCIPLES,
        "writes": writes,
        "paths": paths,
        "generated_at": _now_iso(),
    }
