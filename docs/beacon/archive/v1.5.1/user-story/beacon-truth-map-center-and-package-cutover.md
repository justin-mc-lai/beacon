# User Story: Beacon Truth Map Center and Package Cutover

- version: `v1.5.1`
- feature: `beacon-truth-map-center-and-package-cutover`
- status: `frozen`

## Story

As a Beacon maintainer, I want every CLI command and LLM skill to resolve truth through one deterministic truth-map resolver, so Beacon can later cut over to feature-package Markdown as the only truth source without production or consumption drift.

As a Beacon maintainer, I also want requirement-derived machine JSON to be fully regenerated from resolver-selected Markdown with source hashes and role labels, so stale `.machine` artifacts cannot keep old truth alive during the v1.5.2 cutover.

As a Beacon maintainer, I also want version governance truth to resolve through the same truth-map center, so QA, release, material audit, status, and manifest readers cannot drift back to old version-level paths when feature package becomes the only feature truth source.

As a Beacon maintainer, I also want implement planning and dev-run entry points to fail fast on version governance branch drift, so wrong project metadata cannot generate apparently valid implementation materials and only surface later in QA or release.

As a Beacon maintainer, I also want v1.5.1 to unify normal truth read/write/gate/rebuild/absorb entrypoints through truth_center without changing truth authority yet, so v1.5.2 can be a controlled policy flip instead of another large code sweep.

As a Beacon maintainer, I also want high-risk truth entrypoints to be tracked in an explicit inventory, so broad resolver-first language cannot hide command, utility, or skill surfaces that still read or write old truth paths directly.

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | resolver-center | `beacon.utils.truth_map` exists and exposes resolver APIs for feature truth package paths. |
| AC-002 | no-json-authority | Generated truth-map JSON is marked projection/diagnostic and cannot be accepted as authoritative input. |
| AC-003 | md-authority-ready | Feature package Markdown carries enough contract markers for v1.5.2 canonical promotion. |
| AC-004 | static-contract | Resolver exposes stable constants for source model and parser contracts. |
| AC-005 | source-read-unification | New truth consumers call resolver APIs instead of constructing legacy truth paths. |
| AC-006 | skill-read-unification | Skill templates instruct LLMs to read truth map and feature package before legacy artifacts. |
| AC-007 | no-md-json-multiwrite | QA must not require an equivalent JSON projection for every Markdown truth document. |
| AC-008 | doctor-rebuild-path | Doctor route can rebuild legacy triptych from feature package or reports unsupported gaps explicitly. |
| AC-009 | change-absorb-path | Change route can absorb legacy triptych into feature package or reports unsupported gaps explicitly. |
| AC-010 | drift-prevention | Verify command fails or warns when resolver output disagrees with package files or rebuild metadata. |
| AC-011 | machine-json-rebuild | Truth-map route can rebuild requirement-derived `.machine` JSON from resolver-selected Markdown. |
| AC-012 | machine-json-role-labels | Generated machine JSON is labeled as generated state/evidence, not truth. |
| AC-013 | source-hash-freshness | Generated machine JSON records resolver contract, source paths, and source hashes. |
| AC-014 | runtime-json-exemption | Runtime/process JSON is allowed without Markdown twins and is not requirement authority. |
| AC-015 | stale-machine-fail-closed | Verify fails closed when `.machine` JSON is stale, non-resolver-generated, or source-hash mismatched. |
| AC-016 | version-governance-resolver | Resolver resolves version governance truth in addition to feature package truth. |
| AC-017 | governance-authority-classification | Resolver classifies feature truth, version governance truth, generated governance state, and runtime/process records. |
| AC-018 | manifest-index-not-truth | Manifest/index/cache JSON is never accepted as truth authority. |
| AC-019 | material-audit-resolver-first | Material audit reads through resolver before using manifest or old paths. |
| AC-020 | qa-release-resolver-first | QA, release, and status read governance truth through resolver-first routes. |
| AC-021 | governance-fail-closed | Missing governance truth or drifted generated governance state fails closed. |
| AC-022 | no-feature-package-overload | Version governance materials are not moved into `features/<slug>/`. |
| AC-023 | generated-governance-state-labels | Generated governance JSON/state carries non-authority labels or equivalent declarations. |
| AC-024 | implement-governance-preflight | Implement plan/dev-run surfaces verify version governance metadata branch contract before planning or execution, and fail closed when metadata, current branch, and git workflow expected branch disagree. |
| AC-025 | truth-center-integration-sweep | v1.5.1 may route normal truth reads, write-target resolution, gate input resolution, legacy rebuild targets, and legacy absorb targets through truth_center; it must not switch truth authority from `feature_package_authoritative_ready` to `feature_package_authoritative` until v1.5.2 policy flip. |
| AC-026 | truth-center-entrypoint-inventory | v1.5.1 tracks high-risk truth read/write entrypoints, including PRD/user-story/test-case/workflow/truth/gate commands, PRD bootstrap, requirement clarity/deepening, manifest, acceptance kit, packaged skills, and `.agents/skills`; each entrypoint routes through truth_center/resolver or is explicitly classified as a v1.5.1 legacy/generated/runtime exception with fail-closed or v1.5.2 cutover handling. |

## User Outcome

- LLM skills no longer guess which Beacon files are truth.
- CLI commands share one truth resolver.
- Future truth-source changes happen by changing resolver/schema, not by editing every command.
- Old truth surfaces are not kept alive as a parallel authority.
- Machine JSON remains useful for gates and runtime records, but only as regenerated state/evidence.
- Version governance remains findable and auditable without turning manifests or old paths into hidden truth sources.
- Implement cannot produce plan/dev-run materials when version metadata branch truth and execution git workflow projection disagree.
- v1.5.2 does not need another broad entrypoint migration before switching package authority.
- High-risk command, utility, and skill surfaces cannot silently remain on old truth paths because they are covered by an explicit migration inventory.
