# Beacon v1.3.0 Summary

**Theme**: introduce a simplified Codex native subagent lane across requirement, QA, and implementation surfaces without turning Beacon into a generic agent runtime  
**Status**: planning line  
**Date**: 2026-04-10

---

## One-line summary

`v1.3.0` plans a bounded subagent capability line: Beacon should let selected stages delegate to Codex native child agents with explicit scope, evidence output, and stage contracts, while keeping `PRD → user-story → QA → implement/gate` as the only mainline.

## Why this line exists

`v1.2.0` proved Beacon can harden the mainline and project-skill workflow.

`v1.2.1` added Codex prompt-ingress visibility.

The next friction is now clear:

1. `ask` can detect intent, but it cannot express "this stage may benefit from a bounded subagent lane".
2. `implement run` has `native-single` and `native-team`, but those are Beacon-owned summaries, not Codex-native child-agent contracts.
3. `think / user-story / prd / test-case / qa` still run as single-surface generation flows, even when the work naturally separates into:
   - research
   - structure
   - critique
   - verification

## What changes in this line

1. Add a simplified `subagent_mode` contract for selected stages.
2. Keep subagent usage opt-in, bounded, and evidence-backed.
3. Promote "stage worker roles" instead of a generic orchestration shell.
4. Reuse current Beacon artifacts and gates instead of inventing a second runtime truth.
5. Fix `beacon ask` planning prompts so next-version capability requests route to `think`, not to QA.

## Scope

In scope:

- `ask` / intent routing for subagent-planning prompts
- `think`, `user-story`, `prd`, `test-case`, `qa`, `implement run`
- run-scoped subagent plan/evidence artifacts
- minimal role catalog and stage-specific delegation templates

Out of scope:

- a universal multi-agent operating system
- arbitrary shell orchestration expansion
- implicit background delegation without artifact writeback
- replacing project-skill orchestration or release gates

## Primary reading order

1. `./execution/index.md`
2. `./execution/architecture-blueprint.md`
3. `./research/beacon-v1.3.0-codex-native-subagent-direction.md`
4. `./think/beacon-v1.3.0-simplified-codex-native-subagents.md`
5. `./user-story/beacon-v1.3.0-simplified-codex-native-subagents.md`
6. `./prd/beacon-v1.3.0-simplified-codex-native-subagents.md`
7. `./qa/test-cases/beacon-v1.3.0-simplified-codex-native-subagents.md`
8. `./release/v1.3.0.md`
