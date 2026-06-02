# Project Skill QA Evolution Blueprint (v1.5.1)

## Intent

This blueprint defines how Beacon skills and QA should consume the v1.5.1 truth-map resolver capability:

```text
beacon-truth-map-center-and-package-cutover
```

v1.5.1 introduces a resolver center and machine JSON convergence path. It does not complete the v1.5.2 hard cutover.

## Skill Material Effects

Relevant skill invocations must resolve truth in this order:

1. `beacon truth-map resolve <feature> --project . --version v1.5.1 --json`
2. `features/<slug>/{truth,tests,tasks,evidence}.md` from resolver-selected paths
3. legacy PRD / user-story / test-case refs only as canonical-ready references for this version

Generated `.machine` JSON and truth-map JSON projections are generated state/evidence, not truth authority.

## Required Skill QA Dimensions

QA for this version must verify:

- `beacon.utils.truth_map` exposes stable resolver constants and APIs.
- New truth consumers route through resolver rather than hardcoding old truth paths.
- Skills tell LLMs to read truth-map output before package files.
- Feature package Markdown carries v1.5.2 canonical-ready markers.
- Missing JSON twins do not invalidate Markdown truth.
- Requirement-derived `.machine` JSON carries resolver contract, source paths, source hashes, and generated-state role labels.
- Runtime/process JSON remains exempt from Markdown twin requirements.
- Stale, non-resolver, or source-hash mismatched machine JSON fails closed.

## Acceptance Evidence

Promotion-grade evidence for this line requires:

- frozen PRD / user-story / test-case for the feature;
- synced version feature manifest or resolver fallback for v1.5.1 material discovery;
- feature package under `docs/beacon/v1.5.1/features/<slug>/`;
- resolver-owned machine JSON under `.machine/requirement/`;
- executable tests covering resolver, CLI, validator, drift, runtime JSON exemption, and v1.5.0 regression;
- formal QA record showing JSON remains generated state and not truth authority.

## Current Status

Requirement truth is frozen for v1.5.1. Runtime implementation and targeted tests exist for the truth-map resolver center and machine JSON convergence path. Release promotion still depends on formal QA and release checks.
