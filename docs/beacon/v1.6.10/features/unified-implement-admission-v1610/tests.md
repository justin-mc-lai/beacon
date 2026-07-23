---
slug: unified-implement-admission-v1610
version: v1.6.10
revision_id: R1
materials_status: current
---

# Tests: unified-implement-admission-v1610

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-UIA-001 | AC-UIA-001 | `pytest -q tests/test_v1610_unified_implement_admission.py::test_direct_goal_team_ralph_share_admission_contract` | 四种 execution surface 返回同 schema、同 worktree/cwd 决策，blocked/pass 保持一致 |
| TC-UIA-002 | AC-UIA-002 | `pytest -q tests/test_v1610_unified_implement_admission.py::test_branch_only_soft_skip_never_authorizes_write` | `branch-only`/optional 合同不会以 skipped pass 授权写入 |
| TC-UIA-003 | AC-UIA-003 | `pytest -q tests/test_v1610_unified_implement_admission.py::test_single_repo_materializes_real_leaf_worktree` | 路径出现在 `git worktree list --porcelain`，branch/cwd/reconcile 全部通过 |
| TC-UIA-004 | AC-UIA-004 | `pytest -q tests/test_v1610_unified_implement_admission.py::test_monorepo_materializes_every_writable_service_worktree` | `service_worktree_map` 精确覆盖全部 writable services |
| TC-UIA-005 | AC-UIA-005 | `pytest -q tests/test_v1610_unified_implement_admission.py::test_monorepo_rejects_mkdir_only_and_empty_gitlink_services` | illegal worktree transitions：mkdir-only 与 empty gitlink 均 blocked，不能 dispatch |
| TC-UIA-006 | AC-UIA-006 | `pytest -q tests/test_v1610_unified_implement_admission.py::test_governance_overrides_stale_global_seed` | 生成合同使用 version governance；stale seed 不得返回错误 materialized contract |
| TC-UIA-007 | AC-UIA-007 | `pytest -q tests/test_v1610_unified_implement_admission.py::test_strict_branch_cwd_and_head_mismatch_block_before_write` | 任一 branch/cwd/HEAD mismatch 返回 blocked |
| TC-UIA-008 | AC-UIA-008 | `pytest -q tests/test_v1610_unified_implement_admission.py::test_worker_dispatch_requires_prewrite_admission` | direct/team/ralph 在 admission blocked 时均未调用写入 worker |
| TC-UIA-009 | AC-UIA-009 | `pytest -q tests/test_v1610_unified_implement_admission.py::test_artifact_records_parent_and_service_reconcile_evidence` | artifact 含 parent reconcile、每服务 branch/path/HEAD/reconcile/verified |
| TC-UIA-010 | AC-UIA-010 | `pytest -q tests/test_v1610_unified_implement_admission.py` | 真实临时 Git 仓覆盖 single-repo、nested child repos 与全部 negative paths |

## Coverage Notes

- 所有 TC 都执行真实 Git 命令；不接受只检查静态字符串或文件路径的 contract-only 替代。
- monorepo fixture 使用独立 child repositories，并由父仓 governance 绑定为 writable services。
- 每个 negative path 都断言 `allow_implement=false` 且没有 worker write callback。
