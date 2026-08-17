# Research: goal main-bypass admit gate

## Problem
Agents ran `$beacon-goal` then edited/committed business code on `main` without `workspace admit`.
Root cause: admit hard gate only ran on `tick --execute` → ralph; `goal run` stayed in plan; consumer hooks soft-skipped without monorepo sources; product v0.x defaulted `require_workspace_admission=false`.

## Fix (this lake)
1. Hook template: import installed `beacon` package on consumer repos.
2. Admission default: product 0.x or dedicated/pooled → require true.
3. `create_goal_run`: implement/交付 intent → `ensure_goal_implement_admission` preflight + discipline fields.
4. Skill ops discipline: tick --execute / admit cwd only.

## Non-goals
- Auto-spawn agent into worktree (host-specific)
- Block all main commits (docs/truth still allowed)
