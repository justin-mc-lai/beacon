# Beacon v1.2.1 Summary

**Theme**: strengthen `beacon debug` with Codex `UserPromptSubmit` ingestion, prompt adaptation, and user-guidance for full Beacon workflow usage  
**Status**: partial runtime supplement line  
**Date**: 2026-04-10

---

## One-line summary

`v1.2.1` is the focused supplement line that teaches Beacon how to observe raw Codex user prompts at `UserPromptSubmit` time, normalize them into Beacon-friendly intent guidance, and persist the resulting friction data into the canonical debug surface.

---

## Why this line exists

`v1.2.0` already shipped:

- mainline command simplification
- project-skill discovery
- prototype anchoring
- QA baseline hardening

But one friction still remained in real Codex usage:

> users often type free-form prompts that imply Beacon intent, yet the raw prompt is not captured early enough to normalize, guide, and feed back into Beacon's debug evolution loop.

`v1.2.1` closes that gap by treating Codex `UserPromptSubmit` as a first-class debug input surface.

---

## What changes in this line

1. Beacon adds a dedicated `beacon debug codex-user-prompt-submit` ingestion surface.
2. The command reads raw Codex hook payloads, including prompt/session/thread metadata.
3. Beacon reuses `intent_router.optimize_prompt_to_plan()` to classify the user prompt.
4. Beacon generates a prompt-adaptation guide that tells the model how to steer the user toward:
   - feature context
   - expected Beacon artifact/stage
   - target version
   - plan-only vs execute boundary
5. The event is written into:
   - prompt router history
   - debug feedback canonical surfaces
   - a run-scoped hook snapshot file

---

## Primary reading order

1. `./execution/index.md`
2. `./execution/architecture-blueprint.md`
3. `./user-story/beacon-v121-codex-userpromptsubmit-debug-guidance.md`
4. `./prd/beacon-v121-codex-userpromptsubmit-debug-guidance.md`
5. `./qa/test-cases/beacon-v121-codex-userpromptsubmit-debug-guidance.md`
6. `./release/v1.2.1.md`
