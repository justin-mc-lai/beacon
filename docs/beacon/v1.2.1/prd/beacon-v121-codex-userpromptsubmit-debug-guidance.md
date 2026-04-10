# PRD: Beacon v1.2.1 Codex UserPromptSubmit Debug Guidance

**Feature**: Beacon v1.2.1 - Codex UserPromptSubmit Debug Guidance  
**Version**: v1.2.1  
**Date**: 2026-04-10  
**Status**: Drafted supplement line

---

## 1. Problem

Beacon currently learns a lot from:

- `beacon prompt optimize`
- `beacon ask`
- debug sync of prompt-router history

But a real Codex session has an earlier observation point:

> the raw user prompt at `UserPromptSubmit`

Without using that ingress point, Beacon misses:

- ambiguous raw user intent before later command normalization
- prompt-shape friction that never reaches a Beacon command
- the opportunity to tell the model how to guide the user into a full Beacon workflow

## 2. Goal

Add a bounded debug surface that can:

1. ingest raw Codex `UserPromptSubmit` payloads
2. map them to Beacon intent/boundary/confidence
3. generate a normalized Beacon prompt suggestion
4. persist the event into Beacon debug evidence
5. return a concise model-facing guidance string

## 3. Functional requirements

### FR-001 Hook payload ingestion

Beacon must accept a JSON hook payload and recognize `UserPromptSubmit`.

### FR-002 Raw prompt extraction

Beacon must read the first non-empty prompt candidate from:

- `prompt`
- `input`
- `user_prompt`
- `userPrompt`
- `text`

### FR-003 Shared routing

Beacon must reuse `intent_router.optimize_prompt_to_plan()` for the raw prompt.

### FR-004 Prompt adaptation pack

Beacon must output:

- inferred intent
- confidence
- boundary state
- recommended Beacon command
- normalized prompt suggestion
- missing prompt fields / normalization actions

### FR-005 Hook response contract

Beacon must emit:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "..."
  }
}
```

### FR-006 Debug persistence

Beacon must persist the event into:

- `.beacon/memory/prompt-router-history.jsonl`
- `.beacon/state/debug-feedback/<run>.jsonl`
- `.beacon/debug/runs/<run>/codex-user-prompt-submit.jsonl`

## 4. Non-goals

- editing global Codex hook config automatically
- auto-executing the recommended Beacon command
- replacing the existing `prompt optimize` command
- broadening Beacon into a generic Codex hook framework

## 5. Risks

- hook payload shapes may vary by Codex runtime build
- prompt adaptation copy can become noisy if it is too long
- if the routing heuristic is weak, guidance may overfit to `workflow`

## 6. Success signal

The model can now tell the user, at prompt-submit time, how to rephrase a vague request into a Beacon-native workflow request while preserving a structured debug record of that interaction.
