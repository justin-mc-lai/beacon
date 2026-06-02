# User Story: Beacon Truth Map Center and Package Cutover

- version: `v1.5.1`
- feature: `beacon-truth-map-center-and-package-cutover`
- status: `frozen`

## Story

As a Beacon maintainer, I want every CLI command and LLM skill to resolve truth through one deterministic truth-map resolver, so Beacon can later cut over to feature-package Markdown as the only truth source without production or consumption drift.

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

## User Outcome

- LLM skills no longer guess which Beacon files are truth.
- CLI commands share one truth resolver.
- Future truth-source changes happen by changing resolver/schema, not by editing every command.
- Old truth surfaces are not kept alive as a parallel authority.

