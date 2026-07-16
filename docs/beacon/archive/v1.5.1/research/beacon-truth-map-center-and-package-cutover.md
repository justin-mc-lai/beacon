# Research: beacon-truth-map-center-and-package-cutover

**Feature**: `beacon-truth-map-center-and-package-cutover`
**Version**: `v1.5.1`
**Status**: `support-research`

## Support Findings

### Brainstorm

#### Round 2026-06-02T02:23:02.764287+00:00

- source_skill: `beacon-brainstorm`
- round_id: `2026-06-02T02:23:02.764287+00:00`
- material_effect: `read_only_route_only`
- adoption_status: `route_only`
- route_decision: beacon-test-case
- finding_summary: Treat this as an evolution candidate. Capture options in brainstorm output first, then route accepted scope through beacon-prd or beacon-change.
- source_refs: `docs/beacon/global-boundaries.md`, `docs/beacon/archive/v1.5.1/SUMMARY.md`, `docs/beacon/archive/v1.5.1/execution/index.md`, `docs/beacon/archive/v1.5.1/execution/architecture-blueprint.md`, `docs/beacon/archive/v1.5.1/prd/beacon-truth-map-center-and-package-cutover.md`, `docs/beacon/archive/v1.5.1/user-story/beacon-truth-map-center-and-package-cutover.md`, `docs/beacon/archive/v1.5.1/qa/test-cases/beacon-truth-map-center-and-package-cutover.md`

#### Round 2026-06-02T03:00:00Z

- source_skill: `beacon-brainstorm`
- paired_support_skill: `beacon-source-driven`
- source_map: `.understand-anything/graph-build-report.json`
- code_map_stats: `filesScanned=19995`, `structureFilesAnalyzed=630`, `nodes=25813`, `edges=27426`, `importEdges=1636`
- material_effect: `support_research_only`
- adoption_status: `requires_change_refreeze`
- route_decision: `beacon-change-refreeze`
- finding_summary: v1.5.1 cannot stop at adding a truth-map resolver. It also needs an explicit machine-JSON convergence/rebuild lane so old `.machine` JSON cannot remain stale, duplicated, or silently authoritative while v1.5.2 prepares the Markdown package cutover.

## Source-Driven Machine JSON Convergence

#### Round 2026-06-02T04:55:21.284041+00:00

- source_skill: `beacon-brainstorm`
- round_id: `2026-06-02T04:55:21.284041+00:00`
- material_effect: `read_only_route_only`
- adoption_status: `route_only`
- route_decision: beacon-brainstorm
- finding_summary: Converge missing or ambiguous requirement points into explicit questions and candidate decisions before editing frozen truth.
- source_refs: `docs/beacon/global-boundaries.md`, `docs/beacon/archive/v1.5.1/SUMMARY.md`, `docs/beacon/archive/v1.5.1/execution/index.md`, `docs/beacon/archive/v1.5.1/execution/architecture-blueprint.md`, `docs/beacon/archive/v1.5.1/prd/beacon-truth-map-center-and-package-cutover.md`, `docs/beacon/archive/v1.5.1/user-story/beacon-truth-map-center-and-package-cutover.md`, `docs/beacon/archive/v1.5.1/qa/test-cases/beacon-truth-map-center-and-package-cutover.md`

#### Round 2026-06-02T06:55:41.995304+00:00

- source_skill: `beacon-brainstorm`
- round_id: `2026-06-02T06:55:41.995304+00:00`
- material_effect: `read_only_route_only`
- adoption_status: `route_only`
- route_decision: beacon-brainstorm
- finding_summary: Converge missing or ambiguous requirement points into explicit questions and candidate decisions before editing frozen truth.
- source_refs: `docs/beacon/global-boundaries.md`, `docs/beacon/archive/v1.5.1/SUMMARY.md`, `docs/beacon/archive/v1.5.1/execution/index.md`, `docs/beacon/archive/v1.5.1/execution/architecture-blueprint.md`, `docs/beacon/archive/v1.5.1/prd/beacon-truth-map-center-and-package-cutover.md`, `docs/beacon/archive/v1.5.1/user-story/beacon-truth-map-center-and-package-cutover.md`, `docs/beacon/archive/v1.5.1/qa/test-cases/beacon-truth-map-center-and-package-cutover.md`

#### Round 2026-06-02T07:41:44.097332+00:00

- source_skill: `beacon-brainstorm`
- round_id: `2026-06-02T07:41:44.097332+00:00`
- material_effect: `read_only_route_only`
- adoption_status: `route_only`
- route_decision: beacon-brainstorm
- finding_summary: Converge missing or ambiguous requirement points into explicit questions and candidate decisions before editing frozen truth.
- source_refs: `docs/beacon/global-boundaries.md`, `docs/beacon/archive/v1.5.1/SUMMARY.md`, `docs/beacon/archive/v1.5.1/execution/index.md`, `docs/beacon/archive/v1.5.1/execution/architecture-blueprint.md`, `docs/beacon/archive/v1.5.1/prd/beacon-truth-map-center-and-package-cutover.md`, `docs/beacon/archive/v1.5.1/user-story/beacon-truth-map-center-and-package-cutover.md`, `docs/beacon/archive/v1.5.1/qa/test-cases/beacon-truth-map-center-and-package-cutover.md`
### Core Finding

v1.5.0 is not yet the target shape. It has Markdown-first pieces, but it still keeps `features/<slug>/*.md` as a parallel read model while `prd/`, `user-story/`, `qa/test-cases/`, `execution/`, and `.machine` remain the normal stable chain.

Source anchors:

- `beacon/utils/feature_package.py` renders v1.5.0 packages as a `parallel read model` and returns `gate_authority = canonical_surfaces_preserved`.
- `beacon/commands/feature_package.py` validates packages while explicitly saying it does not change canonical gate truth.
- `beacon/utils/artifact_paths.py` centralizes `.machine/change`, `.machine/execution`, `.machine/requirement`, `.machine/qa`, and feature package paths.
- `beacon/utils/markdown_first_freeze.py` reads Markdown truth, but still emits `.machine/requirement/<slug>.freeze-state.json` and exposes `parse_markdown_truth_projection`.
- `beacon/utils/material_sync.py` regenerates `.machine/user-story/<slug>.json`, `.machine/qa/<slug>.ac-test-matrix.json`, `.machine/qa/<slug>.qa9-matrix.json`, and `.machine/qa/<slug>.story-scenario-map.json` from the old requirement chain.
- `beacon/commands/test_case.py` writes QA matrices under `.machine/qa/` and still writes legacy `.beacon/qa/*.json` compatibility artifacts.

Therefore v1.5.1 must define machine JSON as regenerated machine state/evidence from resolver-selected Markdown, not as a parallel source of truth.

### Required v1.5.1 Convergence Boundary

The resolver center must own a full rebuild plan for requirement-derived machine JSON:

```text
truth-map resolver
  -> resolve feature package / legacy source role
  -> parse Markdown deterministically
  -> regenerate requirement-derived .machine JSON
  -> verify hashes/source_paths/contract ids
  -> fail closed on stale or non-resolver machine JSON
```

This does not make JSON authority. It makes JSON rebuildable and auditable.

### Machine JSON Classes

| Class | Examples | v1.5.1 Role | Required Action |
|---|---|---|---|
| Resolver diagnostics | optional `truth-map.json`, truth-map verify report | generated diagnostic only | Generate from resolver, never read as authority. |
| Requirement state | `.machine/requirement/<slug>.freeze-state.json`, `feature-package-validation.json` | regenerated machine state | Rebuild from resolver-selected Markdown and include source hashes/source paths. |
| PRD compile metadata | `.machine/prd/<slug>.canonical.json`, `.machine/prd/<slug>.compile.json` | compatibility metadata | Stop fulltext mirroring; route source selection through resolver. |
| User-story state | `.machine/user-story/<slug>.json` | rebuilt execution input | Regenerate from resolver-selected truth, not direct hardcoded `user-story/` path. |
| QA matrices | `.machine/qa/<slug>.ac-test-matrix.json`, `.qa9-matrix.json`, `.story-scenario-map.json` | rebuilt gate input | Regenerate from resolver-selected `tests.md` or mapped legacy test source. |
| Test contract index | `.machine/testing/test-contract-index.json` | rebuilt release-facing index | Rebuild after QA matrices and fail closed on stale source hashes. |
| Requirement clarity | `.machine/execution/requirement-clarity-<slug>.json` | regenerated diagnostic/gate input | Source all sections through resolver and record `machine_json_role=diagnostic`. |
| Change/refreeze transaction | `.machine/change/*.refreeze-transaction.json`, reconciliation JSON | transaction record | Keep JSON as transaction evidence; source truth through resolver before writing. |
| Runtime/process records | `.beacon/auto-test-status.json`, `.beacon/qa/status.json`, `.beacon/release-gate-report.json`, `.beacon/raw-command-log.jsonl`, run trace JSON | execution record | Keep JSON. Do not treat as requirement truth and do not require Markdown twins. |
| Legacy compatibility copies | `.beacon/qa/<slug>.json`, `.beacon/qa/<slug>-qa9-matrix.json` | temporary compatibility | Either regenerate from resolver or mark legacy/ignored by truth-map verify. |

### Concrete Code Change Points

1. Add `beacon/utils/truth_map.py`.

Required APIs:

```python
TRUTH_MAP_CONTRACT = "beacon-truth-map-v1"
TRUTH_SOURCE_MODEL = "feature_package_authoritative_ready"
MACHINE_JSON_ROLE = "generated_state_not_truth"

resolve_truth_map(project_root, version)
resolve_feature_truth(project_root, version, feature)
resolve_truth_surface(project_root, version, feature, surface)
resolve_machine_json_plan(project_root, version, feature)
verify_truth_map(project_root, version, feature="")
```

2. Add CLI surface for deterministic rebuild/verify.

Recommended shape:

```bash
beacon truth-map resolve "<feature>" --project . --version v1.5.1 --json
beacon truth-map rebuild-machine "<feature>" --project . --version v1.5.1 --json
beacon truth-map verify "<feature>" --project . --version v1.5.1 --strict --json
```

3. Update `beacon/utils/feature_package.py`.

- Replace hardcoded `gate_authority = canonical_surfaces_preserved` for v1.5.1+ with resolver-aware metadata.
- Keep v1.5.0 behavior intact.
- Add source hashes for `truth.md`, `tests.md`, `tasks.md`, and `evidence.md`.
- Report `machine_json_role = generated_state_not_truth`.

4. Update `beacon/utils/markdown_first_freeze.py`.

- Route `markdown_truth_paths`, `read_markdown_truth`, `markdown_truth_hash`, `build_minimal_freeze_state`, and `parse_markdown_truth_projection` through truth-map resolver for v1.5.1+.
- Rename semantics away from `projection` where the output is only verification metadata.
- Ensure freeze-state JSON has no full Markdown body and records resolver contract/source hashes.

5. Update `beacon/utils/material_sync.py`.

- Replace direct regeneration from `user-story/` and `qa/test-cases/` with resolver-selected source.
- Add a mode for package-driven rebuild: feature package Markdown -> machine user-story JSON and QA matrices.
- Preserve existing v1.5.0/legacy behavior behind version checks.

6. Update `beacon/commands/test_case.py`.

- For v1.5.1+, matrix generation must accept resolver/package-derived test rows.
- `.machine/qa/*.json` remains gate input, but its truth source must be resolver-selected Markdown.
- Legacy `.beacon/qa/*.json` copies must be marked compatibility/runtime state, not truth.

7. Update `beacon/utils/test_contract_governance.py`.

- Rebuild `test-contract-index.json` from resolver-derived machine QA artifacts.
- Verify source hash freshness against resolver output, not only path existence.

8. Update `beacon/utils/requirement_clarity.py`.

- Build clarity reports from resolver-selected truth surfaces.
- JSON report remains diagnostic/gate input; Markdown report remains human-readable support.

9. Update `beacon/utils/change_refreeze.py`.

- `run_change_refreeze_chain` must not hardcode `change -> prd -> user-story -> test-case` as the only closure path for v1.5.1+.
- It should call resolver and machine rebuild before freeze-state verification.

10. Update release/QA/status consumers.

Hot spots from code map:

- `beacon/utils/release_scorecard.py`
- `beacon/utils/qa_feature.py`
- `beacon/utils/material_audit.py`
- `beacon/commands/gate.py`
- `beacon/commands/status.py`

These should read machine JSON only after checking resolver contract/source hash, and should not treat legacy `.beacon/qa/*.json` as requirement authority.

### Acceptance Gap

Current v1.5.1 frozen ACs mention resolver and drift prevention, but do not explicitly require machine JSON full rebuild. The accepted change should add:

- resolver-owned machine JSON rebuild plan;
- source-hash freshness checks for regenerated machine JSON;
- strict classification between requirement-derived JSON and runtime/process JSON;
- fail-closed verification for stale `.machine` artifacts;
- no Markdown twin requirement for runtime/process records.

## Deep Summary

- source_skill: `beacon-deep`
- updated_at: `2026-06-02T07:15:42.548116+00:00`
- deep_artifact_root: `docs/beacon/archive/v1.5.1/deep/beacon-truth-map-center-and-package-cutover`
- machine_artifact_root: `docs/beacon/archive/v1.5.1/.machine/deep/beacon-truth-map-center-and-package-cutover`
- deep_requirement_state: `required`
- status: `closed`
- route_decision: `closed`
- release_supplement_ref: `docs/beacon/archive/v1.5.1/.machine/deep/beacon-truth-map-center-and-package-cutover/release-supplement.json`
- adoption_status: `route_only`
## Learning Influence Summary

## Route Decisions

- 2026-06-02: Machine JSON convergence is a material scope addition. Route to `beacon-change-refreeze` before implementation so PRD/user-story/test-case/feature package tests can add explicit AC/TC coverage.

## Version Evolution Notes

- previous_research: `docs/beacon/v1.5.0/research/beacon-truth-map-center-and-package-cutover.md`
- carried_forward: pending operator review
- superseded: none recorded

## Promotion Log
