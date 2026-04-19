# User Story: beacon-v1.3.4-runtime-evidence-layering-and-noise-governance

## Story

**As a** Beacon maintainer and release owner,  
**I want** Beacon to distinguish formal machine evidence from ephemeral runtime cache and to treat runtime only as corroboration,  
**So that** `status / qa / release` stay useful for humans, git noise stays bounded, and missing runtime never destroys the requirement closure path.

## Story Slices

### US-001: Formal machine evidence must be explicit

As a release owner, I want the version package to clearly define which machine artifacts are formal evidence and may enter git.

### US-002: Runtime cache must remain local and rebuildable

As a maintainer, I want high-frequency runtime/debug/session state to stay local so the repo does not become permanently noisy.

### US-003: Runtime can help, but cannot override truth

As a QA/release operator, I want runtime data to assist verification only when it is fresh and aligned with the current revision.

### US-004: Missing runtime must degrade, not block

As a Beacon user, I want projects to continue from requirement materials even when `.beacon` runtime cache or projection state is missing.

### US-005: Delivery drift must become visible

As a maintainer, I want Beacon to record when PRD-promised surfaces and shipped surfaces diverge, so requirement drift is auditable instead of silent.

## Acceptance Criteria

- AC-001 Formal evidence list: `docs/beacon/<version>/.machine/` artifacts that participate in gate/release are explicitly classified as formal machine evidence.
- AC-002 Runtime cache list: `.beacon/state`, implement/team/debug streams, and raw host-session traces are explicitly classified as ephemeral runtime cache.
- AC-003 Git boundary: formal machine evidence may be committed; ephemeral runtime cache is not required for release readiness.
- AC-004 Runtime freshness gate: runtime may influence status/qa/release only when revision/fingerprint/freshness alignment is satisfied.
- AC-005 Runtime downgrade: stale or conflicting runtime is surfaced as advisory/partial/stale, not treated as truth.
- AC-006 Missing-runtime recovery: when runtime is absent, Beacon can continue from docs + formal machine evidence and may trigger rebuild/revalidation.
- AC-007 Human-surface noise guard: default `status / help / release` output prioritizes stage, blocker, next step, and truth-line clarity over runtime internals.
- AC-008 Delivery drift capture: requirement-vs-shipped drift can be documented as a formal issue and mapped into requirement repair flow.

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Status | ready-for-planning |
| Version | v1.3.4 |
| Feature Slug | beacon-v1.3.4-runtime-evidence-layering-and-noise-governance |
