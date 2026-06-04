# Change: Beacon Design / Product / Prototype Rebuild Contract

**Feature**: `beacon-design-product-prototype-rebuild-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## 1. Change Reason

`friction:cd1809c3220a` exposed a P0 Beacon truth gap:

```text
accepted UI/UX facts did not enter Beacon truth,
so implement / QA followed stale frozen requirements
and risked rolling accepted UI back to an older baseline.
```

The earlier small Phase 7 plan, `prototype-legacy-inspector-split-contract`, is no longer enough. It only demotes legacy wireframe source. The accepted scope is now a complete Beacon design capability rebuild.

Follow-up accepted delta:

```text
The first frozen package said Beacon should distill ui-ux-dev,
but AC-015 was too narrow.
It did not explicitly preserve the four upstream open-source capability sources
behind ui-ux-dev or the seven Beacon design sub-routes needed for auditable use.
```

## 2. Accepted Change

Freeze one complete design capability feature containing five ordered sub-contracts:

1. `beacon-design-product-truth-contract`
2. `beacon-design-component-system-contract`
3. `accepted-ui-ux-truth-writeback-gate-contract`
4. `beacon-prototype-adapter-rebuild-contract`
5. `beacon-design-subskill-contract`

These are not five separate features. They are ordered slices inside one frozen requirement package.

## 3. Scope

### In Scope

- Introduce project-level `PRODUCT.md` / `DESIGN.md` truth participation.
- Introduce version-wide design style truth under `docs/beacon/<version>/design/`.
- Treat design style as a version-wide contract, not a feature-local `design/product.md` surface.
- Distill basic `ui-ux-dev` design practice into Beacon-owned deterministic design guidance.
- Add open-source component system planning and validation.
- Add accepted UI/UX result ledger and truth writeback gate.
- Rebuild prototype as accepted design truth adapter.
- Move legacy wireframe inspection behind explicit compat / include-legacy behavior.
- Add a `$beacon:beacon-design` child skill that routes design/product truth drafting and component design planning.
- Expand `$beacon:beacon-design` into seven support-only routes: `explore`, `system`, `review`, `polish`, `extract`, `library`, and `bootstrap`.
- Preserve upstream capability ownership from `vibe-to-ui`, `ui-ux-pro-max`, `impeccable`, and `awesome-design-md`.
- Keep `awesome-design-md` reference-only.
- Keep upstream bootstrap / mirror checks as capability admission evidence only, not truth/gate/release authority.

### Out Of Scope

- Do not embed all of `ui-ux-dev` implementation internals into Beacon.
- Do not treat upstream design skills as Beacon truth sources.
- Do not treat `awesome-design-md` as an execution skill.
- Do not let `ui-ux-dev` or design support output directly overwrite Beacon truth.
- Do not make design support a new lifecycle stage or release gate.
- Do not remove legacy prototype artifacts immediately.
- Do not change browser fallback, memory migration, intent routing, or test marker layering in this feature.
- Do not make screenshots or polish notes release truth by themselves.

## 4. Source Evidence

- Research closure: `docs/beacon/archive/v1.4.11/research/beacon-design-product-prototype-rebuild-contract.md`
- Friction record: `docs/beacon/archive/v1.4.11/research/friction-cd1809c3220a-ui-ux-design-truth-writeback-incident.md`
- Legacy burden plan: `docs/beacon/archive/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`
- Markdown-first authority research: `docs/beacon/archive/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`
- Brainstorm artifact: `docs/brainstorms/2026-05-26-beacon-brainstorm-v1.4.11-beacon-prototype-design-complete-rebuild-distill-ui-ux-dev-into-built-in.md`
- Brainstorm delta: `docs/brainstorms/2026-05-26-beacon-brainstorm-v1.4.11-使用中文重写-beacon-design-product-prototype-rebuild-contract-并分析-ui-ux-dev-四个.md`

## 5. Route Decision

This change supersedes the small next feature suggestion `prototype-legacy-inspector-split-contract`.

The correct route is:

```text
version-wide design/product truth
  -> component system contract
  -> accepted UI/UX truth writeback gate
  -> prototype adapter rebuild
  -> Beacon design child skill with upstream-preserving route surface
```

The child skill route surface is:

```text
beacon-design-explore  -> vibe-to-ui
beacon-design-extract  -> vibe-to-ui
beacon-design-system   -> ui-ux-pro-max
beacon-design-review   -> impeccable
beacon-design-polish   -> impeccable
beacon-design-library  -> awesome-design-md reference-only
beacon-design-bootstrap -> upstream install / mirror / bootstrap admission
```

Downstream implementation may start only after PRD, user-story, test-case, requirement clarity, and freeze complete.

## 6. Freeze Deliverables

- `docs/beacon/archive/v1.4.11/research/beacon-design-product-prototype-rebuild-contract.md`
- `docs/beacon/archive/v1.4.11/change/beacon-design-product-prototype-rebuild-contract.md`
- `docs/beacon/archive/v1.4.11/prd/beacon-design-product-prototype-rebuild-contract.md`
- `docs/beacon/archive/v1.4.11/user-story/beacon-design-product-prototype-rebuild-contract.md`
- `docs/beacon/archive/v1.4.11/qa/test-cases/beacon-design-product-prototype-rebuild-contract.md`

## 7. Boundary

This feature freezes requirement truth only. It does not implement the rebuild, run QA, or issue release verdicts.
