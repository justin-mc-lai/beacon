# Beacon v1.6.9 — Public Surface 1+6 Alignment

## Scope

Freeze **Scheme A** host-visible public surface shared with v2.0.0 Loom:

- **1** transversal goal (long-run)
- **6** harness abilities (plan/truth/design/implement/qa/release)

Canonical table: `skills/beacon/references/public-surface-1plus6.md`

## Program

Primary: `beacon-public-surface-1plus6-v169`

### Ship-line feature lakes (frozen)

| Feature | Intent |
|---------|--------|
| beacon-public-surface-1plus6-v169 | 1+6 public surface synonym table |
| beacon-public-surface-progressive-merge-v169 | progressive load without capability loss |
| beacon-plan-subintent-router-v169 | plan strong-intent routing |
| beacon-plan-goal-deep-integration-v169 | plan artifact + goal soft gates |
| beacon-goal-implement-admission-hard-gate-v169 | implement hard admit |
| beacon-implement-lane-enforcement-v169 | git hooks block main business commits |
| beacon-version-default-hotfix-mainline-skill-slim-v169 | version/hotfix defaults + slim skills |
| beacon-fix-version-defaults-dual-axis-v169 | runtime vs project docs dual-axis; greenfield v0.0.1 |
| beacon-scheduled-task-agent-suspend-v169 | project scheduled tasks + execution logs |
| goal-main-bypass-admit-gate | close goal/hooks main bypass paths |

## Brand

| | Beacon (this line) | Loom (v2.0.0) |
|--|--------------------|---------------|
| CLI | Python `beacon` | Rust `loom` / `beacon-v2` |
| Goal skill | `beacon-goal` | `loom-goal` |
| Six skills | `beacon-{plan,truth,design,implement,qa,release}` | `loom-*` same verbs |

## Version axes (permanent)

- **Runtime** = toolkit/CLI line (this release promotes runtime to **v1.6.9**)
- **Project docs** = product delivery line under `docs/beacon/<ver>/`
- External greenfield projects default **v0.0.1**, not toolkit semver

## Status

- truth: frozen (ship-line lakes)
- host surface: Scheme A whitelist only (1+6)
- runtime promote: **v1.6.9**
- release check: `beacon release check v1.6.9`
