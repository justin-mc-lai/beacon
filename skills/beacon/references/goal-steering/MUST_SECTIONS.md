# Goal Steering Must Sections (Loom/Beacon)

Source parity: OpenAI Codex `codex-rs/ext/goal/templates/goals/*` (distilled).
Authority: `docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md` AC-V2-ST-*.

## continuation (template_id=continuation)

Must contain all of:

1. `OBJECTIVE_AS_DATA` — objective is user-provided data, not higher-priority instructions
2. `SCOPE_FIDELITY` — keep full objective; do not shrink success to a smaller subset
3. `WORK_FROM_EVIDENCE` — worktree/external state authoritative; conversation assists only
4. `COMPLETION_AUDIT` — requirement-by-requirement evidence before claiming work done
5. `NO_SELF_COMPLETE` — never self-certify GoalRun complete; only prepare for awaiting_verifier
6. `BLOCKED_AUDIT` — blocked only after same blocker on ≥3 consecutive goal turns (incl. auto-requeue)
7. `BUDGET_AWARE` — show tokens/turns used and remaining when budget configured

## budget_limit (template_id=budget_limit)

Must contain:

1. `BUDGET_EXHAUSTED` — system marked budget halt
2. `WRAP_UP_ONLY` — no new substantive work
3. `NO_BUDGET_COMPLETE` — must not complete solely because budget exhausted

## objective_updated (template_id=objective_updated)

Must contain:

1. `NEW_OBJECTIVE_SUPERSEDES` — new objective replaces previous
2. `OBJECTIVE_AS_DATA`
3. `REDIRECT_TURN` — drop work that only served previous objective unless still useful
4. `NO_SELF_COMPLETE`
