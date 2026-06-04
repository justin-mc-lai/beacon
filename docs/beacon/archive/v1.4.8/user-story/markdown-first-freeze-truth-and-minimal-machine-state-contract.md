# User Story: Markdown-first Freeze Truth 与 Minimal Machine State Contract

**Feature**: `markdown-first-freeze-truth-and-minimal-machine-state-contract`
**Version**: `v1.4.8`
**Revision**: `R3`
**Status**: `frozen`

## Story

**As a** Beacon maintainer or operator,
**I want** requirement freeze truth to live in strict Markdown documents while machine JSON only stores minimal state and runtime evidence,
**So that** Beacon keeps strong gates without generating large duplicate machine mirrors that increase token cost and drift risk.

## Acceptance Criteria

- AC-001 Beacon treats Markdown PRD, user-story, test-case, research, execution, and release documents as the canonical freeze truth.
- AC-002 Beacon does not treat frozen-stage fulltext machine mirrors as canonical truth.
- AC-003 Beacon stores only minimal freeze state in requirement-stage JSON.
- AC-004 Beacon keeps implement, QA, release runtime evidence JSON.
- AC-005 Beacon parses AC and test-case coverage from Markdown truth before consulting cache.
- AC-006 Beacon blocks when Markdown parser fails.
- AC-007 Beacon blocks when Markdown baseline hash differs from frozen state.
- AC-008 Beacon blocks when refreeze transaction status is missing or ambiguous.
- AC-009 Beacon emits diagnostics with path, line or section, hash, reason_code, and repair route.
- AC-010 Beacon provides a migration boundary so historical fulltext JSON remains readable but new v1.4.8+ freeze artifacts stop duplicating full Markdown.

## Boundary Notes

- Markdown truth is not freeform prose; it must follow strict parseable contracts.
- Minimal state JSON is allowed only as cache/state, not truth.
- Runtime JSON remains necessary for process/session/evidence data.
- Missing or ambiguous cache must not silently pass.
