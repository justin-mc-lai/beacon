# Beacon v1.6.11 Execution Boundaries

## Canonical truth lane

- Truth、Change、Truth Review、freeze 和 refreeze 只在 governance `truth_canonical=main`。
- 旧冻结 Truth 保留只读；v1.6.11 通过 parent/inherited refs 向前迁移，不原地篡改。
- active package 只接受 v1.6.10+ shape；旧 package/ledger fail-closed。

## Implementation lane

- direct、goal、team、ralph 和 host subagent 的 implementation task 共享同一个 pre-write admission。
- 第一次 repository write 前必须获得真实 git worktree、governed branch、cwd、HEAD 和 main truth reconcile 证明。
- `branch-only`、`skipped=true`、mkdir-only、empty gitlink 或仅安装 hook 均不能授权写入。
- refreeze 或 graph revision 变化使旧 admission、ready set、tests/tasks/evidence stale。

## Subagent boundary

- 默认单线程；intent-on 时才启用 host subagent。
- 子代理只返回 finding、patch 或 evidence；主代理持有 TaskRun/GoalRun 状态转换。
- 无 host runtime 时诚实降级，不宣称 parallel。
- 子代理不得 freeze Truth、签署 QA/release 或完成 Goal。

## Lifecycle boundary

- 公共生命周期保持 goal → plan → truth → design(条件) → implement → qa → release。
- task graph、progress ledger、drift gate、cancel/replan 和 convergence verifier 是内部机制。
- 关键出口复用 Goal run_id，写入 `agent_trace.v1`；append 失败不得静默成功。

## No-compat route

`old shape → package_shape_upgrade_required → plan → truth/change → Truth Review Gate → freeze new revision`。

