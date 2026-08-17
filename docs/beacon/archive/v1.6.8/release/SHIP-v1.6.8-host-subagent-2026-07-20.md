# SHIP Confirmation — v1.6.8 Host Subagent Keyword Line

**Decision**: **SHIP / GO**  
**Date**: 2026-07-20  
**Confirmed by**: user (chat: “把本线记为正式 SHIP”)  
**Evaluators**: `beacon-eval-release` + contract tests  

## Verdict

Promote this delivery slice on the **v1.6.8** runtime line as **shipped to main** (source repo commit). Runtime line remains **v1.6.8**.

## Evidence chain

| Layer | Evidence |
|-------|----------|
| Release check | `docs/beacon/archive/v1.6.8/release/release-check-v1.6.8-host-subagent-latest.json` → pass |
| Checklist | `docs/beacon/archive/v1.6.8/release/checklist-v1.6.8.md` |
| Feature GO note | `docs/beacon/archive/v1.6.8/release/beacon-host-subagent-lifecycle-keyword-v168-go.md` |
| Contract tests | `tests/test_v168_host_subagent_keyword.py` (17 passed) |
| Feature package | `docs/beacon/archive/v1.6.8/features/beacon-host-subagent-lifecycle-keyword-v168/` |
| Pln-review | `docs/beacon/archive/v1.6.8/research/beacon-host-subagent-lifecycle-keyword-pln-review.md` |
| Post-release hook | `run-20260720T053345Z-b45d` passed |

## Locks (reaffirmed)

1. Single public entry: `$beacon-goal` / `$loom-goal` dual-install (Loom does not replace Beacon)
2. Host agents **keyword-gated**; default single-thread
3. `并行` alone → satellite only (UD-SA-001)
4. Minimal pack = 6 roles; vendored under `.codex/agents` / `.claude/agents`
5. Subagents cannot complete GoalRun or auto-release
6. Release remains human-confirmed for future slices

## Operator follow-up after SHIP commit

```bash
# optional session refresh
# restart Codex so HUD hook is fresh

beacon doctor install-subagent-pack -p . --host-runtime codex --pack minimal
beacon doctor verify-subagent-runtime -p . --host-runtime codex --require-agents --json
beacon --version   # expect v1.6.8
```
