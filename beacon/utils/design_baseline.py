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
) -> str:
    tokens = resolve_design_preset(preset)
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

    return f"""# DESIGN.md — {product_name}

Status: ready
Preset: `{tokens['preset']}` ({tokens['label']}, source: {tokens['source']})
Beacon version context: `{version}`
Generation: unattended-complete-baseline

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
- No external design skill is required at runtime to apply this baseline (`external_reference_runtime_dependency=false`).

## Design philosophy

1. **Lazy-user first**: first screen answers the main job before secondary chrome.
2. **Recognition over recall**: labels and primary actions must be obvious.
3. **State honesty**: empty / loading / error / success / blocked / stale / recovery are first-class.
4. **Restrained density**: no marketing hero, no fake dashboard charts, no AI gradient theater.
5. **Domain-bound chrome**: badges and primary buttons bind to business FSM states when a domain FSM exists.
6. **Fine-tune, don't freestyle**: when a prior DESIGN.md exists, extend it; do not invent a second design system.

## Visual tokens (CSS variables)

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
  --touch-min: 44px;
  --density: {tokens['density']};
}}
```

## Typography

| Role | Size | Weight | Notes |
|------|------|--------|-------|
| Page title | 20–24px | 600 | One primary title per view |
| Section | 16px | 600 | Short, action-oriented |
| Body | 14px | 400 | Line-height 1.5 |
| Meta / muted | 12–13px | 400 | Secondary paths only |
| Code / path | 12px mono | 400 | Never primary judgment copy |

Font stack: `{tokens['font']}`

## Spacing & layout

- Base grid: 4/8px (`--space-*`).
- Page padding: `--space-5` desktop, `--space-4` compact.
- Card padding: `--space-4`.
- Stack gap: `--space-3` default.
- Max content width: 1100–1200px for product surfaces; full-bleed for dense consoles.
- First screen order: **status → primary action → supporting list → secondary disclosure**.

## Component system baseline

| Component | Spec |
|-----------|------|
| Primary button | bg `--primary`, fg `--primary-fg`, min-height `--touch-min`, radius `--radius` |
| Secondary button | border `--border`, bg transparent/card, same min-height |
| Destructive button | border/fg `--danger`, never primary for non-destructive flows |
| Input | border `--border`, focus ring `--primary` (visible), 44px min height |
| Card | bg `--card`, border `--border`, radius `--radius`, no nested cards |
| Badge | pill/chip; color encodes **domain/UI state only** |
| Table/list row | clear hover; row action affordance explicit |
| Empty state | title + one next action + optional secondary help |
| Error/blocked | cause + recovery action (not only red text) |
| Toast/inline feedback | success/error/warning using token colors |

## Interaction principles

{interaction_bullets}
- Keyboard: Tab order matches visual order; Escape closes overlays.
- Loading: skeletons or explicit progress; never blank freeze without explanation.
- Navigation: one primary nav region; overflow tools go to secondary/"更多" when IA is crowded.
- Handoff: deep-links restore page + entity + state, not only route shell.

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

When Domain FSM exists, also bind business states via `ui-state-matrix.md` (badge + primary action per state). Ship gates require matrix states ⊆ domain states.

## Anti-AI UI / visual Do & Don't

### Do
- Quiet neutrals + one accent (`--primary`)
- Explicit empty/loading/error/success
- Domain badges and disabled illegal actions
- Focus-visible rings and 44×44 targets
- Secondary disclosure for machine/debug paths

### Don't
{dont_bullets}
- Marketing hero on operator workbench
- Multiple competing primary CTAs
- Invent FSM states not in truth
- Copy reference-library aesthetics as project law

## Accessibility & responsive

- Contrast: body text on `--bg`/`--card` meets WCAG AA intent.
- Focus visibility: required (never `outline: none` without replacement).
- Touch targets: ≥ 44×44.
- Responsive: collapse secondary detail before primary judgment content; keep primary action reachable.
- Motion: no bounce/elastic; prefer 150–200ms opacity/transform max.

## Version-wide contracts

Pair this file with (when present):
- `docs/beacon/<version>/design/style.md`
- `docs/beacon/<version>/design/component-system.md`
- `docs/beacon/<version>/design/interaction-contract.md`
- `docs/beacon/<version>/design/state-matrix.md`
- feature `ui-state-matrix.md` bound to Domain FSM

## Unattended default & fine-tune policy

1. **No human design decision**: implementers use this DESIGN.md + preset tokens as the visual OS.
2. **Existing DESIGN.md**: run fine-tune mode — keep brand/domain specifics; fill missing axes from this baseline.
3. **Upstream polish**: `beacon design route polish|review|system|explore` may propose deltas; accepted facts bind here or via `beacon prototype adapt` / change-refreeze.
4. **Ship**: UX-required packages need DESIGN.md (or version design contracts) + ui-state-matrix when domain states exist.
{fine_tune_note}
## Truth update policy

Update this file when accepted design facts become project-level truth.
Design support output is not truth until bound. Promise-changing visual changes require change/refreeze before implementation.
"""


VERSION_STYLE_TEMPLATE = """# Version Design Style

Status: ready

## Token inheritance

Inherit project `DESIGN.md` CSS variables. Version may tighten density or accent only when product truth allows.

## Atmosphere

- Quiet neutrals, one accent, no decorative gradients.
- Prefer system fonts declared in DESIGN.md.
- Keep first-screen judgment content above secondary metadata.

## Density

Follow DESIGN.md `--density` (comfortable / compact / airy). Operator surfaces may go compact without reducing touch targets below 44px.
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

- One primary nav region
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
    force: bool = False,
    write_version_contracts: bool = True,
    product_name: str = "",
) -> dict[str, Any]:
    """Unattended visual baseline: complete DESIGN.md + version design contracts.

    - Missing DESIGN.md (or force): write complete reusable DESIGN.md.
    - Existing DESIGN.md and not force: preserve it; write fine-tune proposal under docs/beacon/<v>/design/.
    """
    # local import avoids circular import with design_contract
    from beacon.utils.design_contract import design_truth_paths, write_version_design_contracts

    project_root = project_root.expanduser().resolve()
    resolved = resolve_target_version(project_root, version)
    name = str(product_name or project_root.name or "Product").strip() or "Product"
    tokens = resolve_design_preset(preset)
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
            preset=tokens["preset"],
            existing_design_md=existing,
            version=resolved,
            mode="fine_tune",
        )
        proposal_path = project_root / "docs" / "beacon" / resolved / "design" / "fine-tune-proposal.md"
        writes["fine_tune_proposal"] = _write_file(proposal_path, proposal, force=True)
        writes["design_truth"] = "exists_preserved"
    else:
        body = render_complete_design_md(
            product_name=name,
            preset=tokens["preset"],
            existing_design_md=existing,
            version=resolved,
            mode="baseline",
        )
        writes["design_truth"] = _write_file(design_path, body, force=force or not design_path.exists())

    if write_version_contracts:
        # force only version-wide drafts when force=True; otherwise leave existing
        version_payload = write_version_design_contracts(
            project_root,
            resolved,
            force=force,
            include_project_truth=False,
        )
        # upgrade version templates if still stubs / drafts with incomplete content
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
        "product_name": name,
        "design_path": "DESIGN.md",
        "fine_tune_proposal_path": (
            f"docs/beacon/{resolved}/design/fine-tune-proposal.md" if mode == "fine_tune" else ""
        ),
        "open_source_ui_agent_principles": OPEN_SOURCE_UI_AGENT_PRINCIPLES,
        "writes": writes,
        "paths": paths,
        "generated_at": _now_iso(),
    }
