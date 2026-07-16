# Change: Global Workspace Git Admission v1.6.2

- version: `v1.6.2`
- feature: `beacon-global-workspace-git-admission-v162`
- status: `frozen` R2 → **R3 pending refreeze**
- reason: Host skill slash+prompt stable branch governance; branch resolution first.

## Summary

R2 narrows scope per planner review **scheme A**:

- **Must:** GIT_ADMISSION Step 0 + `workspace admit` + CLI fail-closed + dirty-only invalidation
- **No TTL:** time alone does not invalidate admission
- **Should:** hook Write deny (defense-in-depth; missing hook does not block release)

## User Decisions (locked)

| ID | Decision | Value |
|----|----------|-------|
| UD-001 | Admission CLI | `beacon workspace admit` |
| UD-002 | Branch | `beacon/v1.6.2/<feature-slug>` |
| UD-003 | Worktree | dedicated default |
| UD-004 | Must enforcement | Skill Step 0 + CLI |
| UD-005 | Hook | **Should** (not Must) |
| UD-006 | verify-agent-surface | fail missing preamble; **warn** missing hook |
| UD-007 | Trellis isolation | Beacon hook independent of TRELLIS_DISABLE_HOOKS |
| UD-008 | Invalidation | **dirty-only**; no normative TTL |
| UD-009 | check-branch | keep alias |
| UD-010 | QA/release | shared artifact |
| UD-011 | P0 acceptance | slash/skill → admit → worktree → write |

## Next Steps

1. ~~Revise truth/tests R2~~
2. `beacon change ... --refreeze-chain`
3. governance MD v1.6.2 block
4. implement → qa → release


## R3 — Version-Line Package Operator Closure

- UD-012..015: upgrade-package repair routing + release stub + anti copy-prior-version
- Trigger: implement/qa blocked by requirement_package_contract
- Route: `beacon change ... --refreeze-chain`
