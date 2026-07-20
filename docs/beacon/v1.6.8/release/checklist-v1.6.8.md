# Release Checklist: v1.6.8

**Version**: v1.6.8  
**Created**: 2026-07-20 14:04  
**Refreshed**: 2026-07-20 (host-subagent SHIP closeout)  
**Status**: **SHIP confirmed (human GO)**

---

## Formal gates

- [x] `beacon release check v1.6.8` → pass / `release_ready=true`
  - evidence: `docs/beacon/v1.6.8/release/release-check-v1.6.8-host-subagent-latest.json`
- [x] Host subagent contract suite → **17 passed**
  - `python3 -m pytest tests/test_v168_host_subagent_keyword.py -q`
- [x] Curated pack install/verify (codex + claude, 6 roles)
  - `beacon doctor install-subagent-pack … --pack minimal`
  - `beacon doctor verify-subagent-runtime … --require-agents`
- [x] Agent surfaces (codex/claude strict) → PASS
- [x] Post-release local install hook → passed / side_effect_executed
  - run: `.beacon/state/hooks/beacon-post-release-local-install/run-20260720T053345Z-b45d.json`
- [x] Codex HUD hook setup applied (restart session recommended for fresh activation)
- [x] Global CLI: `beacon --version` → **Beacon CLI v1.6.8**

## Pre-release product checks

- [x] Contract tests for host-subagent keyword gate green
- [x] Default single-thread / keyword fail-closed verified by tests
- [x] No second public entry (`beacon-goal` only)
- [x] Subagents cannot complete GoalRun / auto-release (contract)
- [x] Documentation: feature package + examples + pln-review + GO note
- [x] Version change document includes host-subagent feature package

## Change / scope documents

- [x] Version change MD: `docs/beacon/v1.6.8/change/v1.6.8.md`
- [x] Version change JSON: `docs/beacon/v1.6.8/.machine/change/v1.6.8.json`
- [x] Feature change: `docs/beacon/v1.6.8/change/beacon-host-subagent-lifecycle-keyword-v168.md`
- [x] Feature package: `docs/beacon/v1.6.8/features/beacon-host-subagent-lifecycle-keyword-v168/`
- [x] v2/Loom mirror package: `docs/beacon/v2.0.0/features/loom-host-subagent-lifecycle-keyword-v200/`
- [x] Reviewer confirmed included packages match intended SHIP scope (host-subagent + release gate repair for worktree progressive driver)

## SHIP decision

| Field | Value |
|-------|-------|
| Decision | **SHIP / GO** |
| Date | 2026-07-20 |
| Operator | user confirm via chat + `beacon-eval-release` |
| Public entry | `$beacon-goal` / `beacon goal run` only |
| Line | `current_runtime_release_line = v1.6.8` |

### Included this SHIP slice

1. Host subagent keyword gate + curated 6-role pack (Codex/Claude)
2. Doctor: `install-subagent-pack`, `verify-subagent-runtime --require-agents`
3. Skill/examples for off/on paths
4. Release gate closure for scorecard driver feature + post-release hooks

### Explicit non-goals (still deferred)

- Full VoltAgent 150+ role dump
- Skill_MAS auto skill rewrite
- Auto product tag/publish outside this repo commit

## Notes

- Formal SHIP note: `docs/beacon/v1.6.8/release/SHIP-v1.6.8-host-subagent-2026-07-20.md`
- Prior line GOs remain valid: `v1.6.8-go.md`, friction-closeout GO
