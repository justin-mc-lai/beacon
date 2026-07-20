# Git Worktree Execution Flow (Beacon / Loom)

Stable process for **truth on canonical branch** + **implement on git worktree**.  
Applies to production Beacon (`beacon`) and Loom evolution (`loom`). Dual-install does **not** replace this flow.

Schema hint: `git-worktree-execution-flow.v1`

## Non-negotiables

1. **Truth / freeze / refreeze** only on `truth_canonical` (`main` or `master`).
2. **Implement / QA write paths** only in an **admitted feature/delivery worktree** (real `git worktree`, not mkdir-only fake).
3. **Align delivery with main via `git merge` / `rebase`**, never cherry-pick as the primary “catch up to main” strategy.
4. **cwd == admitted_worktree** for harness/agent project-root.
5. **Clean worktree** before implement (stash or commit noise); do not develop on a dirty primary checkout mixed with unrelated versions.
6. **CLI dual-install** (`beacon` + `loom`) ≠ development tree; installing skills does not choose your git worktree for you.

## Standard sequence

```text
support_advisory (optional)
  -> canonical_truth_authoring   # main/master only
  -> canonical_refreeze
  -> canonical_commit
  -> feature_worktree_reconcile  # merge main into feature/delivery worktree
  -> governance_verify
  -> workspace_admission          # beacon workspace admit --json
  -> implement_resume            # cwd = worktree_path
  -> qa-evidence / release       # release remains human
```

Illegal:

| Illegal | reason_code (conceptual) |
|---------|---------------------------|
| Write requirement revision on feature worktree | `truth_canonical_branch_mismatch` |
| Implement on primary dirty `main` without admission | `workspace_admission_missing` / process violation |
| Cherry-pick main→delivery as routine alignment | process violation (use merge/rebase) |
| current-branch + isolated-worktree | `worktree_illegal_mode_combo` |
| mkdir-only path pretending to be worktree | `mkdir_only_worktree_forbidden` |

## Progressive skill load (always-on refs)

When a stage loads, agents **must** also open this file (or the stage slice below):

| Stage | Must load this flow | Extra focus |
|-------|---------------------|-------------|
| **goal** (facade) | **full** | entry + route; never skip admit before implement |
| plan | summary | authoring vs implement split |
| truth / change / refreeze | **canonical-only** | no feature worktree writes |
| implement | **full** | admit + real worktree + merge main first |
| qa / release | admit + correct tree | do not write evidence on wrong tree |
| loop (support) | full + `standard_execution_precheck` | CLI-owned precheck |

Do **not** bulk-load historical skills; load this shared reference instead of pasting 200 lines into every SKILL.md.

## CLI anchors

```bash
# Admission (Tier A/B when version+feature known)
beacon workspace admit --project-root . --version <v> --feature <slug> --json
# → cwd = worktree_path; do not git checkout elsewhere to "fix" branch

# Real worktree materialize (v2 / loom kernel when available)
beacon-v2 worktree resolve --project-root . --mode worktree --materialize --json
# or delivery worktree for this monorepo:
# git worktree add .beacon/worktrees/v2.0.0/dev-kernel-goal-delivery beacon/v2.0.0/dev-kernel-goal-delivery
# git -C .beacon/worktrees/v2.0.0/dev-kernel-goal-delivery merge main

# Standard execution precheck (loop / implement gate)
beacon status standard-execution-precheck <feature> --project-root . --version <v> --run-id <id> --json
```

## Process-correct delivery worktree (example)

See: `skills/beacon/examples/git-worktree-process-correct-30s.md`

## Parallel lakes

- Mode `main_star_satellite_pool`: one lake → one satellite worktree; merge to main star only.
- Mode `single_worktree`: serial; still admit once before implement.

## Install note

| Surface | Meaning |
|---------|---------|
| `pip install` / skill install | Runtime dual-install of `beacon` and/or `loom` |
| git worktree path | **Where humans/agents edit this repo** for a feature |

Both must succeed independently. Skill install never implies worktree admission.

## Goal implement admission hard gate (product-goal)

**Runtime (Must for goal implement write path):**

1. `ensure_goal_implement_admission` → `run_workspace_admit` (same branch governance contract).
2. Existing worktree lane → **switch**; else **`git worktree add`** (real worktree).
3. Register **workspace pool** when `worktree_mode=pooled` (`.beacon/state/workspace-pool/<version>/pool.json`).
4. **Merge** `truth_canonical` / baseline (`main`) into feature branch; conflict → `merge_main_conflict` blocked.
5. `tick --execute` dispatch `ralph` **only if** `allow_implement=true`; else goal `blocked`.
6. When version contract has `require_workspace_admission=false`, goal still **forces** a dedicated leaf worktree (closes main-write hole) — see UD-GIA-009.
7. Align `parallel_plan.satellites[].worktree` to admit-resolved path (do not invent a second satellite tree).

**Does not** auto-confirm release. Complete still needs verifier.

Code: `beacon/utils/goal_implement_admission.py` · feature packages:
- `docs/beacon/v1.6.9/features/beacon-goal-implement-admission-hard-gate-v169/`
- `docs/beacon/v2.0.0/features/loom-goal-implement-admission-hard-gate-v200/`

Human surface remains: `beacon doctor branch-governance` / `$beacon-gov-branch`.

