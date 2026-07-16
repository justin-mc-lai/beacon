# Change: beacon-git-scope-graph-v167 GitScopeGraph

**Version**: `v1.6.7`
**Feature**: `beacon-git-scope-graph-v167`
**Revision**: `R1`
**Status**: `draft`
**Promotion ref**: `friction:2e306f7acea7`

## Intent

Introduce `GitScopeGraph.v1` to unify single_repo, monorepo, and multi_git_workspace admission under one topology_gate contract.

## Accepted Change

- `ProjectTopology.v1` + `GitScopeGraph.v1` schema
- `beacon workspace topology-resolve` CLI
- Extend verification bundle with `topology_gate` check
- program-level branch profile as GitScopeGraph profile (v1.6.2 R5 compat)
- v2 `BranchContext.v1` parity fixtures

## Affected Surfaces

- `docs/beacon/v1.6.7/features/beacon-git-scope-graph-v167/{truth,tests,tasks,evidence}.md`
- `beacon/utils/git_scope_graph.py` (new)
- `beacon/commands/workspace.py` or dedicated topology command
- `beacon/utils/workspace_admission.py`
- `tests/test_v167_git_scope_graph.py`

## Downstream Route

- Freeze before `beacon-loop-goal-v166` R7 implement
- Consumer: loop-goal R7 AC-037
