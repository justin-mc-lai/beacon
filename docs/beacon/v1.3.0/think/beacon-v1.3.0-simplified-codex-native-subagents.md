# Think: Beacon v1.3.0 Simplified Codex Native Subagents

**Feature**: Beacon v1.3.0 - Simplified Codex Native Subagents  
**Version**: v1.3.0  
**Date**: 2026-04-10  
**Status**: planning line

## Problem framing

Beacon has two useful but separate capabilities today:

1. strong stage artifacts
2. bounded implementation-time coordination via `native-team`

What is missing is a stage-wide delegation model that can help with requirement authoring, critique, scenario expansion, and verification without breaking Beacon's evidence-first contract.

## Desired outcome

When a user asks for a complex next-step artifact, Beacon can choose:

- single-surface generation
- or a bounded subagent lane

while still returning one canonical Beacon artifact.

## Constraints

1. Must remain mainline-first.
2. Must not become a generic super-agent shell.
3. Must preserve version/package truth.
4. Must keep all delegation visible in artifacts and run state.

## Proposed thesis

Beacon should add a simplified stage subagent model, not a full orchestration platform.

That means:

- opt-in delegation
- fixed role catalog
- stage-specific worker templates
- explicit evidence writeback

## Stage candidates

1. `think`
   - `researcher`
   - `critic`
2. `user-story`
   - `story-mapper`
   - `ac-reviewer`
3. `prd`
   - `requirement-parser`
   - `risk-critic`
4. `test-case`
   - `scenario-mapper`
   - `coverage-checker`
5. `qa`
   - `verifier`
   - `repair-handoff-writer`
6. `implement run`
   - `executor`
   - `reviewer`
   - `tester`

## Decision

`v1.3.0` should be a planning and architecture line first.

Only the smallest enabling runtime changes should ship before the full stage rollout is proven.
