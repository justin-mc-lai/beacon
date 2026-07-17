# Beacon example — complete reusable DESIGN.md

Use this as the default visual OS when no human design decision exists.

```bash
beacon design baseline --project . --version auto --write --json
# existing DESIGN.md → non-destructive fine-tune proposal
beacon design baseline --project . --version auto --write --json
# overwrite with another preset
beacon design baseline --project . --version auto --write --force --preset operator-console --json
# secondary polish against existing design
beacon design route polish "<feature>" --project . --version auto --json
```

Open-source UI agent mapping absorbed into the template:
- vibe-to-ui → hierarchy / layout / first-screen intent
- ui-ux-pro-max → tokens / components / states / a11y / responsive
- impeccable → spacing / focus / microcopy / anti-AI UI / ship readiness
- awesome-design-md → reference-only pattern notes (never ship authority)

---

# DESIGN.md — Example Product

Status: ready
Preset: `restrained-product` (Restrained Product, source: apple)
Beacon version context: `v1.6.7`
Generation: unattended-complete-baseline

This file is the **project-level visual truth**. Implement / QA / UI ship gates treat it as binding when present.
It is complete enough to ship a coherent UI **without human design decisions**, while remaining fine-tunable against an existing DESIGN.md.

## Open-source UI agent principles (Beacon absorption)

Beacon design routes preserve upstream capabilities but **do not** treat them as runtime truth:

| Upstream | Routes | Kind | Absorbed into this DESIGN.md |
|----------|--------|------|------------------------------|
| vibe-to-ui | explore, extract | execution-capable | information_hierarchy, layout_models, first_screen_intent |
| ui-ux-pro-max | system | execution-capable | tokens, component_system, states, responsive, accessibility |
| impeccable | review, polish | execution-capable | spacing, focus_visibility, microcopy, ship_readiness, anti_ai_ui |
| awesome-design-md | library | reference-only | pattern_references_only |

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
:root {
  --bg: #F5F5F7;
  --fg: #1D1D1F;
  --card: #FFFFFF;
  --border: #D2D2D7;
  --muted: #6E6E73;
  --primary: #0071E3;
  --primary-fg: #FFFFFF;
  --danger: #FF3B30;
  --success: #34C759;
  --warning: #FF9F0A;
  --radius: 8px;
  --font: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --touch-min: 44px;
  --density: comfortable;
}
```

## Typography

| Role | Size | Weight | Notes |
|------|------|--------|-------|
| Page title | 20–24px | 600 | One primary title per view |
| Section | 16px | 600 | Short, action-oriented |
| Body | 14px | 400 | Line-height 1.5 |
| Meta / muted | 12–13px | 400 | Secondary paths only |
| Code / path | 12px mono | 400 | Never primary judgment copy |

Font stack: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif`

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

- focus-visible must exist for keyboard users
- primary interactive targets should be at least 44x44
- button hierarchy must distinguish primary from secondary actions
- empty/loading/error/success states must be intentional and explicit
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
- gradient text
- purple-to-blue ai gradient
- card inside card
- accent side stripe
- glassmorphism used as decoration
- bounce_or_elastic_easing
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

## Truth update policy

Update this file when accepted design facts become project-level truth.
Design support output is not truth until bound. Promise-changing visual changes require change/refreeze before implementation.

