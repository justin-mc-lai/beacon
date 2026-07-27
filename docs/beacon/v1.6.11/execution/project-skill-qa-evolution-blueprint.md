# Beacon v1.6.11 Project Skill and QA Evolution Blueprint

## Public lifecycle

```text
goal
  -> plan
  -> truth (canonical main)
  -> design (conditional)
  -> implement (shared real-worktree admission)
  -> qa (independent verifier)
  -> release (human gate)
```

## Goal and task execution

- GoalRun owns program slug, graph revision, truth revisions, ready set, human decisions, admission refs, trace refs and verifier refs。
- TaskNode declares intent/AC/code/evidence plus execution mode、role、service、worktree/admission contract。
- Subagents cannot complete Goal; parent synthesizes findings and performs state transitions。

## Shared admission

- direct/goal/team/ralph consume one `allow_implement` decision。
- Implementation dispatch receives admitted cwd/worktree map and may not invent directories。
- Refreeze invalidates stale admission and requires main truth reconcile。

## QA obligations

- Real Git tests cover single-repo and nested-service worktrees。
- Parity tests cover direct/goal/team/ralph and host-subagent fallback。
- Negative tests cover main writes、branch-only、soft skip、mkdir-only、empty gitlink、stale truth and cancelled dependency。
- No-compat tests prove old package/ledger routes to replan/refreeze rather than soft compatibility。
- End-to-end Gold proves drift pause → human cancel/replace → ready-set recompute → Goal closure。

## Coding standard

- Reuse existing Goal、admission、agent_trace and lifecycle authorities。
- Internal task machinery must not add public harnesses。
- Stable reason codes and evidence refs are mandatory。
- No legacy reader or compatibility branch for invalid active shapes。

