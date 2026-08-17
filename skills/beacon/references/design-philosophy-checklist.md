# Design Philosophy Checklist (P2)

Non-canonical support reference for the **design** harness and goal design stage.

Use before treating a UI/UX baseline as shippable. Complements progressive skills under `beacon-design` / `loom-design`.

## Decision boundaries

- [ ] Surface choice (web / miniapp / mobile / desktop) is explicit and justified
- [ ] Company/template or design-system tokens are chosen; no random palette drift
- [ ] States covered: empty, loading, error, success, permission-denied (where applicable)
- [ ] Interaction cost: primary path is one clear action, not multi-dead-end menus

## Anti-slop

- [ ] No decorative noise that does not serve a user job
- [ ] Copy is product language, not placeholder lorem
- [ ] Components reuse system primitives before inventing one-offs
- [ ] Accessibility: contrast, focus, labels considered at baseline

## Ship-gate awareness

- [ ] Design baseline + design.md lint path is known (`design_stage` on goal run)
- [ ] UX-required features do not skip design stage on goal pipeline
- [ ] Fine-tune proposals are separate from frozen truth promises
- [ ] Design does **not** implement product code or freeze requirement truth

## Route

| Situation | Next |
|-----------|------|
| Baseline missing / lint blocked | stay design or fix lint evidence |
| UX not required | goal may skip design stage |
| Ready for code | implement (worktree norms apply) |
| Requirement still moving | truth / change — not polish-as-product |

## Runtime refs

- Progressive map: `skills/beacon/references/public-surface-progressive-map.v1.json` → harness `design`
- Goal stage attaches this checklist on `build_stage_plan` (stage=`design`)
