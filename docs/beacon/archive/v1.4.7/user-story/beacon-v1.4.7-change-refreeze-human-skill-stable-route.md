# User Story: Beacon v1.4.7 change refreeze human skill stable route

**Feature**: `beacon-v1.4.7-change-refreeze-human-skill-stable-route`
**Version**: `v1.4.7`
**Revision**: `R1`
**Status**: `frozen`

## Story

**As a** Beacon operator or agent receiving natural-language change refreeze intent,
**I want** a stable `beacon-change-refreeze` skill that maps that intent to the governed refreeze transaction,
**So that** I can close accepted post-freeze requirement changes without guessing the correct CLI flag or accidentally treating refreeze as a new lifecycle stage.

## Acceptance Criteria

- AC-001 Beacon provides `skills/beacon/beacon-change-refreeze/SKILL.md` and `.agents/skills/beacon-change-refreeze/SKILL.md`.
- AC-002 The skill declares `beacon change ... --refreeze-chain` as the operator route.
- AC-003 The skill declares the closure chain `change -> prd -> user-story -> test-case -> requirement_clarity -> freeze`.
- AC-004 The skill explicitly states it is not a lifecycle stage, not a truth source, and not a gate source.
- AC-005 The skill explicitly states it does not execute implementation, QA, release, or direct canonical truth writes.
- AC-006 The skill metadata/body supports stable matching for change 一键冻结, change refreeze, 重新冻结, refreeze-chain, and post-freeze requirement closure.
- AC-007 Change/deep-facing docs can route adoption-required or accepted post-freeze refreeze intent to `beacon-change-refreeze`.
- AC-008 The feature does not introduce a second refreeze implementation path beyond `beacon change ... --refreeze-chain`.

## Actor Semantics

1. Human operator
   - names a refreeze intent in natural language
   - expects a stable route, not a broad change menu
2. `beacon-change-refreeze` skill
   - explains boundaries
   - routes to the existing refreeze transaction command
   - does not own truth or gates
3. `beacon-change`
   - remains the broader post-freeze change surface
   - owns the refreeze transaction route
4. `deep`
   - may recommend this skill when findings require adoption into change/refreeze

## Boundary Notes

- This is a human routing feature, not a new product stage.
- The skill name can be new; the refreeze execution path must stay single.
- Stable matching is valuable precisely because refreeze is high-risk and fail-closed.
