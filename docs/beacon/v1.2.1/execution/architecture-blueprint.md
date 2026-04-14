# Beacon v1.2.1 Architecture Blueprint

`v1.2.1` introduces one bounded architectural addition:

```text
Codex UserPromptSubmit hook
→ Beacon debug hook ingestion
→ intent routing
→ prompt adaptation guidance
→ debug feedback / history / snapshot persistence
```

## What this blueprint captures

1. **Prompt ingress earlier than command execution**
   - Beacon can now inspect the raw user prompt before any Beacon command is executed.
   - This closes the gap between "user typed an ambiguous Beacon request" and "Beacon only learns after a later command surface is used."

2. **Shared routing, not duplicated heuristics**
   - The hook adapter reuses `intent_router.optimize_prompt_to_plan()`.
   - Prompt adaptation is derived from the same route/boundary/confidence outcome already used by `beacon prompt optimize`.

3. **Three-layer evidence persistence**
   - prompt router history for compatibility
   - canonical debug feedback for harvest/export
   - run-scoped hook snapshot for raw-prompt traceability

4. **Guidance-first output contract**
   - the hook returns `hookSpecificOutput.additionalContext`
   - the context should help the model steer the user toward a normalized Beacon prompt
   - the hook does not auto-execute Beacon commands

## Deliberate non-goals

- no global mutation of `~/.codex/hooks.json`
- no expansion into a generic Codex hook framework
- no replacement of `beacon prompt optimize`
- no change to Beacon's mainline command center
