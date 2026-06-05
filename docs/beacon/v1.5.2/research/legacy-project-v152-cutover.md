# Research: legacy-project-v152-cutover

**Feature**: `legacy-project-v152-cutover`
**Version**: `v1.5.2`
**Status**: `support-research`

## Support Findings

### CEO Review

#### Round 2026-06-05T03:18:24.611147+00:00

- source_skill: `beacon-ceo-review`
- round_id: `2026-06-05T03:18:24.611147+00:00`
- material_effect: `read_only_route_only`
- adoption_status: `route_only`
- route_decision: implement
- finding_summary: CEO review did not find a version-level reframing blocker after challenging default downside axes.
- source_refs: `docs/beacon/v1.5.2/.machine/execution/beacon-ceo-review-transaction.json`, `docs/beacon/v1.5.2/execution/beacon-ceo-review-transaction.md`

### Brainstorm

#### Round 2026-06-05T02:33:33.913344+00:00

- source_skill: `beacon-brainstorm`
- round_id: `2026-06-05T02:33:33.913344+00:00`
- material_effect: `read_only_route_only`
- adoption_status: `promoted_to_change`
- route_decision: beacon-change-refreeze
- finding_summary: Treat legacy project v1.5.2 migration as a cutover preflight plus phased migration transaction before refreeze/freeze/implement.
- source_refs: `docs/beacon/global-boundaries.md`, `docs/beacon/v1.5.2/SUMMARY.md`, `docs/beacon/v1.5.2/execution/index.md`, `docs/beacon/v1.5.2/execution/architecture-blueprint.md`, `docs/beacon/v1.5.2/research/legacy-project-v152-cutover-convergence.md`

## Deep Summary

## Learning Influence Summary

## Route Decisions

#### Round 2026-06-05T06:27:48.805058+00:00

- source_skill: `beacon-brainstorm`
- round_id: `2026-06-05T06:27:48.805058+00:00`
- material_effect: `read_only_route_only`
- adoption_status: `route_only`
- route_decision: beacon-brainstorm
- finding_summary: Converge missing or ambiguous requirement points into explicit questions and candidate decisions before editing frozen truth.
- source_refs: `docs/beacon/global-boundaries.md`, `docs/beacon/v1.5.2/SUMMARY.md`, `docs/beacon/v1.5.2/execution/index.md`, `docs/beacon/v1.5.2/execution/architecture-blueprint.md`, `docs/beacon/v1.5.2/features/legacy-project-v152-cutover/truth.md`, `docs/beacon/v1.5.2/features/legacy-project-v152-cutover/truth.md`, `docs/beacon/v1.5.2/features/legacy-project-v152-cutover/tests.md`
### Converged Direction

旧项目切到 v1.5.2 不能靠 `beacon-change-refreeze` 单点补丁解决。正确抽象是一个 **legacy project cutover preflight + migration transaction**：

```text
detect legacy/mixed truth state
  -> classify required migration phases
  -> materialize/validate feature package
  -> install v1.5.2 version governance materials
  -> verify resolver + doctor metadata
  -> only then allow refreeze/freeze/implement
```

This research has been promoted into `docs/beacon/v1.5.2/features/legacy-project-v152-cutover/`.

### Why `change-refreeze` Alone Fails

`beacon-change-refreeze` is intentionally narrow: it routes accepted post-freeze changes to `beacon change ... --refreeze-chain`. In a legacy project this is insufficient because the operator's real intent is not only "refreeze accepted truth"; it is "move the project from old truth topology to v1.5.2 authority." Those are different transactions.

The failing state has two independent gaps:

| Plane | Legacy/mixed symptom | v1.5.2 required state |
|---|---|---|
| Requirement truth | `docs/beacon/v0.0.1/{prd,user-story,qa/test-cases}` still acts as normal truth | `docs/beacon/v1.5.2/features/<slug>/{truth,tests,tasks,evidence}.md` is resolver-selected authority |
| Project governance | `docs/beacon/governance/project-version-governance.md` and sqlite projection may be missing | Governance MD is authority; sqlite/runtime state is generated projection only |

### Minimal Operator Experience

The operator should not need to know every low-level command. A v1.5.2-aware surface should say:

```text
This project is legacy/mixed. Refreeze is blocked until cutover preflight passes.
Run: beacon truth-cutover run <feature> --project-root . --target-version v1.5.2
```

The command name is provisional. `truth-cutover`, `v152-migrate`, or `doctor migrate-to-v152` are acceptable names only if they preserve the same transaction boundary.

### Detection Contract

Cutover preflight should classify, not mutate:

| Check | Signal | Result |
|---|---|---|
| legacy triptych present | `docs/beacon/v*/prd`, `user-story`, `qa/test-cases` exist for active feature | mark `legacy_truth_present` |
| package missing | no `features/<slug>/truth.md` or `tests.md` under target version | require `materialize-feature-package` |
| package draft/incomplete | package exists but validate fails or status is draft when freeze requested | block freeze, route to truth/coverage |
| governance missing | no `docs/beacon/governance/project-version-governance.md` or active version contract | require governance MD setup/migrate |
| projection missing/drift | sqlite row absent or source hash mismatch | regenerate projection, fail closed if verify still fails |
| agent surface stale | installed skills mention old normal triptych for v1.5.2 | run setup/verify agent surface |

### Migration Phases

1. **Inventory**
   - Resolve target version through `truth-map`.
   - Report legacy, package, governance, projection, and agent-surface state.
   - No writes.

2. **Requirement package cutover**
   - If package missing, run `materialize-feature-package <feature> --version v1.5.2`.
   - Run `validate-feature-package`.
   - Run `truth-map verify`.
   - Legacy triptych stays on disk but becomes absorb/rebuild/archive-only.

3. **Project governance cutover**
   - Ensure `docs/beacon/governance/project-version-governance.md` exists.
   - Ensure target version contract includes topology, service bindings, canonical branch, and validation state.
   - Regenerate sqlite/runtime projection from MD only.
   - Run `doctor metadata verify`.

4. **Agent surface refresh**
   - Run setup/verify for active agent surfaces so skills say resolver-first and package-authoritative.
   - This avoids the "skill told me the old route" failure mode.

5. **Resume original user intent**
   - If the original request was refreeze, return to `beacon change ... --refreeze-chain`.
   - If clarity still blocks, route to `truth.define`, `truth.acceptance`, or `truth.coverage`.
   - If all gates pass, continue to implement/QA/release.

### Failure Closure

The migration must not silently "best effort" through mixed authority. Failure should stop at the first unverified plane and print the next exact route:

| Failure | Closure |
|---|---|
| package missing | run materialize, then validate |
| package invalid | route to `truth.define/acceptance/coverage` or compatibility aliases |
| governance MD missing | run doctor metadata setup/migrate |
| governance projection drift | regenerate from MD; if mismatch remains, fail closed |
| old triptych conflicts with package | package wins; legacy drift is diagnostic |
| refreeze requested before cutover pass | block refreeze and show cutover command |

## Version Evolution Notes

This research extends v1.5.2's package-authoritative and markdown-only governance line with a migration experience for older projects.

## Promotion Log

- 2026-06-05: promoted into feature package `legacy-project-v152-cutover`.
