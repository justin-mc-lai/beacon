---
slug: service-scoped-worktree-pool-v1611
version: v1.6.11
status: frozen
revision_id: R0
language: zh
domain_required: true
domain_kind: platform
ux_required: false
ux_deferred: true
package_maturity: filled
materials_status: current
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.11/programs/beacon-plan-goal-task-closure-v1611/program-manifest.md
baseline_commit: 30b9adffc8ec5442a7691a88faf64a251d97b98f
participating_services: beacon
git_canonical_branch: main
parent_truth: docs/beacon/v1.6.10/features/unified-implement-admission-v1610/truth.md
inherited_contracts: "docs/beacon/v1.6.5/features/beacon-workspace-pool-lease-v165/truth.md; docs/beacon/v1.6.7/features/beacon-git-scope-graph-v167/truth.md; docs/beacon/v1.6.10/features/unified-implement-admission-v1610/truth.md"
promotion_ref: "user-confirmation-2026-07-28-rolo-service-scoped-pool"
change_reason: "R0: Rolo multi-git workspace exposed that parent feature pool and stable service bindings are mixed; add service-scoped pool truth before implementation"
canonical_refs:
  prd: docs/beacon/v1.6.11/features/service-scoped-worktree-pool-v1611/truth.md
  user_story: docs/beacon/v1.6.11/features/service-scoped-worktree-pool-v1611/truth.md
  test_case: docs/beacon/v1.6.11/features/service-scoped-worktree-pool-v1611/tests.md
---

# Requirement Truth: Service-scoped Worktree Pool

## 人话

Rolo 这类项目不是“一个仓库里几个目录”那么简单。它有一个外层项目仓，也有一串真正的服务仓。现在 Beacon 把这几层揉在一起：有时把服务根当 worktree，有时把服务 worktree 写进全局绑定，有时只给外层仓发一个 feature pool，真正要写的服务仓还要靠后补的 `service_worktree_map` 兜住。这个模型太容易让 agent 走错目录。

这次先把边界钉死：外层 Rolo 仓只负责 truth、governance 和总 admission；每个可写服务用自己的真实 git worktree。pool 也要跟着服务走，不能只记一个 parent worktree。做不到就停，不能靠“当前目录刚好在某个分支上”放行。

- 能做：把 Rolo governance 迁移到稳定 service repo 绑定；让 Beacon pool 记录 parent + 每个 service 的 lease、branch、base 和 HEAD；实现前验证每个服务 worktree。
- 不能做：把 `.worktrees/feature-*` 写进全局 service binding；把第一个 service 当 primary；用 parent worktree 授权服务代码写入；恢复旧 package 兼容。
- 怎样算完：Rolo v2.3.3/v2.3.4 这类 multi-git fixture 能通过 topology/admission；service worktree pool 可 lease、release、校验；单仓和旧 dedicated 行为不回退。

## User Intent

修正 Rolo 多服务 multi-git workspace 的 Beacon worktree pool 混乱：先收敛治理文件形状，再补 Beacon 的 service-scoped pool/admission 能力。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: focused_migration
accepted_direction_ref: user-confirmation-2026-07-28
target_version: v1.6.11
truth_canonical: main
target_project_example: /Users/apple/Developer/Company/rolo
core_problem:
  - service_bindings_mix_stable_repo_roots_and_version_worktrees
  - workspace_pool_key_has_feature_but_not_service
  - git_scope_graph_can_treat_first_service_as_primary
  - one_global_baseline_branch_is_wrong_for_rolo_child_repos
non_negotiables:
  - primary_root_is_explicit
  - service_binding_repo_root_is_stable
  - service_worktree_map_is_required_for_writable_child_repos
  - service_pool_release_does_not_delete_worktree
  - branch_only_or_parent_only_never_authorizes_service_writes
```

## Alignment Surface

本包只煮干两个面：

1. **Governance 形状**：Rolo 这类 multi-git workspace 的全局 service binding 必须只表达稳定 repo root；版本 worktree 是 admission/runtime 结果，不是全局绑定事实。
2. **Service-scoped pool**：Beacon worktree pool/admission 必须从 `version + feature` 扩展到 `version + feature + service`，并进入 implement/write guard/topology gate 的统一证据链。

不在本包内完成远端 MR、Rolo UAT delivery 或生产 hotfix 清理。

## Phased Backlog

| Phase | Scope | Decision |
|-------|-------|----------|
| R0 | 需求冻结：治理形状、service-scoped lease、admission、write guard、Rolo fixture | accepted |
| R1 | Beacon 实现 + 本地真实 Git fixture + Rolo dry-run 验证 | planned |
| Later | 跨机器分布式 lease 协调、远端自动 MR、Rolo UAT merge 自动化 | deferred |

## First principles

- worktree 是写入授权，不是目录命名习惯。
- service binding 是稳定事实；worktree lease 是运行态事实。
- 多 git workspace 的完成条件来自每个可写 git root，而不是外层 parent 仓。
- baseline branch 必须按 git root 校验；Rolo root 的 `main` 不能默认套给所有 child service。

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| ProjectPrimary | project_root, role=primary, writable=false | truth/governance/admission owner |
| ServiceBinding | service_key, stable_repo_root, role, writable | 长期服务仓事实 |
| VersionServiceContract | version, service_key, canonical_branch, baseline_branch | 当前版本服务分支合同 |
| ParentPoolLease | version, feature_slug, worktree_path, branch, state | 外层 feature bundle lease |
| ServicePoolLease | version, feature_slug, service_key, repo_root, branch, base_branch, worktree_path, state, git_head | 每个服务的真实 worktree lease |
| AdmissionArtifact | parent_reconcile, service_worktree_map, service_reconcile | implement/QA 可重放证据 |
| TopologyGate | scopes, primary_scope, satellite_scopes, topology_gate_status | standard execution precheck 输入 |

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-SSP-001 | user confirmation | must | AC-SSP-001 | covered |
| INT-SSP-002 | Rolo governance evidence | must | AC-SSP-002 | covered |
| INT-SSP-003 | workspace pool truth | must | AC-SSP-003 | covered |
| INT-SSP-004 | unified implement admission | must | AC-SSP-004 | covered |
| INT-SSP-005 | write guard/topology evidence | must | AC-SSP-005 | covered |
| INT-SSP-006 | Rolo regression | must | AC-SSP-006 | covered |
| INT-SSP-007 | compatibility guard | must | AC-SSP-007 | covered |

## 用户旅程

### 旅程 A：修正 Rolo governance 形状

1. 维护者确认 Rolo 是 multi-git workspace。
2. Beacon 读取项目 governance，看到显式 primary root 和稳定 service repo bindings。
3. 版本合同声明参与服务、每服务 canonical branch、每服务 baseline branch。
4. 旧的 service binding 如果指向 `.worktrees/feature-*`，迁移器报告并改为稳定服务根。
5. doctor/metadata verify 不再把第一个 service 当 primary，也不再把旧 worktree 当长期事实。

### 旅程 B：admission 创建 service-scoped pool

1. truth 在 `main` 冻结。
2. implement 前执行 workspace/implement admission。
3. Beacon 创建或复用 parent lease。
4. Beacon 按 participating writable services 创建或复用 service leases。
5. 每个 service worktree 通过对应 child repo 的 `git worktree list`、branch、HEAD 和 baseline reconcile。
6. admission artifact 写入完整 `service_worktree_map` 后，worker 才能进入服务目录写代码。

### 旅程 C：blocked path

1. Rolo governance 缺 primary、service binding 指向 `.worktrees`、baseline branch 不存在、service worktree 不是真实 git checkout 或 parent-only 写入被发现。
2. Beacon 返回 fail-closed reason code。
3. goal standard execution precheck 路由到 debug/repair，不能进入 implement。

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-SSP-001 | Rolo/multi-git governance 必须支持显式 `role=primary` root；global service bindings 的 `repo_root` 只能指稳定 repo root，不能指版本 worktree；`multi_git_workspace` 是合法 topology_kind |
| AC-SSP-002 | Governance parser/render/doctor 必须保留 primary binding 顺序无关语义，metadata verify 接受 `multi_git_workspace`，并在 service binding 指向 `.worktrees/feature-*` 时给出可执行迁移结果 |
| AC-SSP-003 | Workspace pool 必须支持 `workspace-pool-v2` 或等价 schema：一个 feature parent lease 下包含 services lease map，服务 lease 记录 service_key、repo_root、branch、base_branch、worktree_path、lease_holder、leased_at、released_at、git_head；release 只归还 lease，不删除 worktree |
| AC-SSP-004 | Implement admission 对 multi-git/nested child repo 必须为每个 participating 且 writable service 创建或复用真实 service worktree；分支来自 `per_service_canonical_branch`，baseline 来自 `per_service_baseline_branch`，路径来自 `service_worktree_path_pattern` 或默认 `.beacon/worktrees/<version>/<feature_slug>/services/<service_key>` |
| AC-SSP-005 | GitScopeGraph/topology gate/write guard 必须以 explicit primary + service scopes 汇总；parent worktree 不能授权 service write；任何 service branch/cwd/head/baseline mismatch 都阻断 implement dispatch |
| AC-SSP-006 | Rolo v2.3.3/v2.3.4 fixture 必须验证：primary 是 `/Users/apple/Developer/Company/rolo`，participating service map 精确覆盖版本合同，`workspace_admission_cwd_mismatch` 不再由 first-service-primary 误判触发 |
| AC-SSP-007 | Existing single_repo、dedicated-worktree、pooled feature-level lease 行为保持回归通过；本包不得引入旧 package shape 兼容 reader、soft skip write authorization 或 hook-only gate |

## Domain FSM ServiceScopedPool

| State | From | Guard |
|-------|------|-------|
| governance_unresolved | — | no explicit primary/service facts |
| governance_current | governance_unresolved, blocked | primary + stable service bindings + version service contracts pass |
| parent_leased | governance_current | parent worktree lease acquired |
| services_leasing | parent_leased | writable participating services resolved |
| services_admitted | services_leasing | all service worktrees real and reconciled |
| implementing | services_admitted | write target is inside admitted service worktree |
| released | services_admitted, implementing | release returns leases to pool |
| blocked | any non-terminal | missing/mismatched governance, branch, cwd, head, baseline, lease state |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| governance_unresolved | GovernanceMigrated | primary_and_stable_services | governance_current | write/verify governance projection |
| governance_current | AdmitRequested | truth_on_canonical | parent_leased | create_or_reuse_parent_lease |
| parent_leased | ResolveServices | participating_writable_services_complete | services_leasing | build service lease plan |
| services_leasing | ServiceWorktreesVerified | all_real_git_worktrees | services_admitted | write service_worktree_map |
| services_admitted | WriteRequested | target_in_service_worktree | implementing | allow worker dispatch |
| services_admitted | ReleaseRequested | holder_matches | released | mark parent/services released |
| governance_current | MissingPrimary | any | blocked | reason=multi_git_primary_missing |
| services_leasing | BadServiceWorktree | any | blocked | reason=service_worktree_invalid |
| services_admitted | ParentOnlyWrite | any | blocked | reason=parent_only_service_write_forbidden |

终态：`services_admitted` 或 `released`。

## Illegal transitions

- `governance_unresolved → parent_leased`
- first service binding becomes primary because it appears first
- service binding repo_root points at `.worktrees/feature-*`
- `parent_leased → implementing` without `service_worktree_map`
- branch-only or skipped admission authorizes writes
- parent worktree path authorizes child service writes
- service worktree path is mkdir-only or empty gitlink
- service baseline merge uses parent root baseline when service baseline differs
- release deletes worktree by default
- hook-installed state becomes admission pass
- old package shape reader is added to make active v1.6.10+ gates pass

## Deferral Ledger

| Deferral ID | Capability | Reason | User Decision | Impact |
|-------------|------------|--------|---------------|--------|
| D-SSP-001 | Cross-machine distributed lease coordination | 需要进程/主机级 owner 协议，超出本地 Beacon pool 修复湖 | accepted_defer | 本包只保证本地 durable lease fail-closed |
| D-SSP-002 | Rolo UAT merge / pipeline automation | 属于 rolo-dev delivery，不是 Beacon admission truth | accepted_defer | 本包只提供 governance/admission 可验证前提 |

## Non-goals

- 不自动修改 Rolo 远端分支、MR、UAT 或生产热修复线。
- 不把 Rolo 的业务服务初始化、Debug Lab 或 Swagger 规则纳入本包。
- 不把 `.beacon/state/workspace-pool` runtime JSON 变成 requirement truth。
- 不把 service worktree cleanup 做成默认 destructive action。
- 不恢复旧 package truth 形状或旧 ledger soft compatibility。

## Freeze readiness

- [x] Truth Review Gate pass
- [x] 用户确认方向：先修治理文件形状，再补 Beacon service-scoped pool（`user-confirmation-2026-07-28`）
