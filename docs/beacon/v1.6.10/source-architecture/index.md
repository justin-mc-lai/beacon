# Beacon v1.6.10 Source Architecture Index

## Truth and governance

| Module | Responsibility |
|--------|----------------|
| `beacon/utils/project_governance.py` | Parse canonical project/version governance Markdown |
| `beacon/utils/project_metadata.py` | Project metadata transactions and freeze-time version contract registration |
| `beacon/utils/truth_map.py` | Resolve feature package and version truth surfaces |

## Implement admission

| Module | Responsibility |
|--------|----------------|
| `beacon/utils/workspace_admission.py` | Resolve, materialize, validate, and persist workspace admission |
| `beacon/utils/git_scope_graph.py` | Resolve single-repo, monorepo, and multi-git service scopes |
| `beacon/utils/execution_branch_contract.py` | Compile governed branch/worktree facts |
| `beacon/utils/git_alignment.py` | Create/inspect real git worktrees and branch alignment |
| `beacon/utils/branch_governance.py` | Strict branch governance verification |
| `beacon/utils/goal_implement_admission.py` | Goal adapter; delegates policy to shared admission |
| `beacon/commands/implement/commands.py` | Direct/team/ralph implement entrypoints and dispatch |
| `beacon/utils/product_goal_runtime.py` | Goal stage orchestration and implement dispatch |

## Verification

| Module | Responsibility |
|--------|----------------|
| `beacon/utils/standard_execution_precheck.py` | CLI-owned pre-implementation verification bundle |
| `beacon/utils/implement_lane_enforcement.py` | Commit/push defense-in-depth |
| `tests/test_v1610_unified_implement_admission.py` | Real Git topology and execution-surface parity regression |

## Dependency direction

```text
governance truth
  -> shared implement admission
  -> topology-specific worktree materialization
  -> direct / goal / team / ralph dispatch
  -> QA revalidation
```

Config seeds and generated JSON may supply defaults only when governance is silent. They cannot override an active version contract.
