---
slug: unified-implement-admission-v1610
version: v1.6.10
status: frozen
revision_id: R1
language: zh
domain_required: true
ux_required: false
package_maturity: filled
parser_contract: beacon-feature-package-v2
git_canonical_branch: main
participating_services: [beacon]
materials_status: current
canonical_refs:
  prd: docs/beacon/v1.6.10/features/unified-implement-admission-v1610/truth.md
  user_story: docs/beacon/v1.6.10/features/unified-implement-admission-v1610/truth.md
  test_case: docs/beacon/v1.6.10/features/unified-implement-admission-v1610/tests.md
truth_source_model: feature_package_authoritative
promotion_ref: docs/beacon/v1.6.10/research/implement-worktree-admission-prewrite-review-20260723.md
change_reason: "R1: direct implement、goal、team、ralph 共用 fail-closed pre-write admission；single-repo 与 monorepo 只在真实 worktree 写入"
humanizer_applied: true
---

# Requirement Truth: Unified Implement Admission (v1.6.10 R1)

## 人话

Beacon 现在有两套实现准入：goal 会补建 worktree，direct implement 在 `branch-only` 合同时却可能直接放行。monorepo 更麻烦，父仓 worktree 看似存在，真正要改的服务仓仍可能只是空 gitlink。

这次只收口一条规则：任何 implement 执行面在第一次代码写入前，都必须拿到同一种 admission。单仓要进入真实 feature worktree；monorepo 要给每个 writable service 建真实 service worktree，并核对分支、HEAD、cwd 与 baseline。做不到就停，不能用 `skipped=true`、branch-only、mkdir 目录或 hook 兜底当授权。

- 能做：统一四种 implement 入口，给单仓和每个可写服务建真实 worktree，并在 dispatch 前严格验分支、cwd、HEAD 与 baseline。
- 不能做：在 main 写实现、用 soft-skip 或 hook 冒充准入、自动确认 release。
- 怎样算完：真实 Git 回归覆盖 single-repo、nested child repos 和全部负路径，implement preflight 与独立 QA 都能重放 admission 证据。

## User Intent

让 direct implement、goal、team、ralph 共用同一个强制 admission，并把 single-repo 与 monorepo 的 worktree 管理变成可验证、可交付的编码规范。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
outcome: all_implement_surfaces_write_only_after_real_worktree_admission
non_negotiables:
  - main_or_master_only_hosts_truth_freeze_and_refreeze
  - branch_only_or_soft_skip_never_authorizes_implementation_writes
  - every_writable_monorepo_service_has_a_real_service_worktree
  - direct_goal_team_ralph_share_one_admission_decision
  - governance_overrides_stale_global_seed
out_of_scope:
  - automatic_release_confirmation
  - replacing_git_hooks_as_defense_in_depth
  - changing_customer_business_code
```

## Alignment Surface

本 revision 只处理 implement 的 pre-write 边界、worktree 物化、branch/baseline 校验、治理优先级与相应测试。QA 和 release 继续消费 admission 结果，但不在这里重写其 verdict 规则。

## Phased Backlog

| Phase | Scope | Decision |
|-------|-------|----------|
| R1 | shared admission、single-repo leaf worktree、monorepo service worktrees、strict branch/baseline gate | accepted |
| Later | 自动安装 hooks、跨机器 workspace 租约协调、远端 PR/release 自动化 | deferred, not required for R1 closure |

## Intent Coverage Matrix

| Intent ID | Source | Strength | Landing | Status |
|-----------|--------|----------|---------|--------|
| INT-UIA-001 | user confirmed review | must | AC-UIA-001 | covered |
| INT-UIA-002 | user: branch-only/soft-skip 不授权 | must | AC-UIA-002 | covered |
| INT-UIA-003 | original worktree design | must | AC-UIA-003 | covered |
| INT-UIA-004 | monorepo service dispatch | must | AC-UIA-004, AC-UIA-005 | covered |
| INT-UIA-005 | stale seed finding | must | AC-UIA-006 | covered |
| INT-UIA-006 | branch mismatch finding | must | AC-UIA-007 | covered |
| INT-UIA-007 | pre-write, not commit-time | must | AC-UIA-008 | covered |
| INT-UIA-008 | single/monorepo deliverability | must | AC-UIA-009, AC-UIA-010 | covered |

## 用户旅程

### 旅程 A：single-repo

1. 需求在 canonical `main` 冻结并提交。
2. implement 任一入口调用 shared admission。
3. admission 创建或复用 feature leaf branch 的真实 git worktree，merge canonical truth baseline。
4. 执行器切换到返回的 `cwd` 后才允许写代码。
5. QA 使用同一 admission artifact 验证 branch、HEAD 与 cwd。

### 旅程 B：monorepo / nested service repos

1. 父仓保存 truth 与 version governance。
2. admission 读取 participating/writable services，不采用过期全局 seed 覆盖版本治理。
3. 父仓 truth lane 与每个 writable child repo 分别 reconcile。
4. 每个服务生成真实 worktree；`service_worktree_map` 完整登记服务到绝对路径。
5. 任何服务缺 worktree、分支错误、路径不是 git worktree、只有空 gitlink，整次 implement 阻断。

### 旅程 C：team / ralph

1. team 或 ralph 只能消费 shared admission 的 pass payload。
2. worker 的 project root/cwd 来自 service worktree map，不自行发明目录。
3. admission blocked 时不得 dispatch 会写仓库的 worker。

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-UIA-001 | 提供唯一 shared `ensure_implement_admission`（或等价单一入口），direct implement、goal、team、ralph 都消费同一 `allow_implement`、reason codes、cwd 与 worktree map 合同 |
| AC-UIA-002 | `require_workspace_admission=false`、`branch-only`、`skipped=true` 只能触发真实 worktree 物化或 blocked；不得直接返回 implementation write authorization |
| AC-UIA-003 | single-repo pass 必须绑定真实 leaf git worktree、governed feature branch、clean/expected cwd，并记录 canonical truth merge/reconcile 结果 |
| AC-UIA-004 | monorepo pass 必须为每个 participating 且 writable service 生成完整 `service_worktree_map`，不能只 admission 父 superproject |
| AC-UIA-005 | 每个 service worktree 必须由对应 child repo 的 `git worktree list` 证明，分支符合 per-service governance，路径内有有效 `.git` 元数据；mkdir-only、空 gitlink、父仓空目录均 blocked |
| AC-UIA-006 | version governance 是 branch/service/worktree facts 的最高项目权威；stale `beacon.config.yaml` 或 global seed 不得覆盖并返回 `materialized` |
| AC-UIA-007 | implement write path 强制 strict branch/cwd/HEAD mismatch；诊断型 soft mismatch 不得转换为 pass |
| AC-UIA-008 | admission 在 worker dispatch 和第一次 implementation write 前执行；pre-commit/pre-push hooks 只作 defense-in-depth |
| AC-UIA-009 | admission artifact 记录 parent truth reconcile、每个 child baseline reconcile、service branch、worktree path、git HEAD 和验证状态，可供 QA 重放 |
| AC-UIA-010 | 真实 Git 回归覆盖 single-repo、nested child repos monorepo、direct/goal/team/ralph parity、soft-skip、stale seed、mkdir-only 与 empty-gitlink negative paths |

## Domain Model

| Entity | Key | Requires |
|--------|-----|----------|
| ImplementAdmission | version + feature + execution_surface | frozen truth + version governance |
| ParentTruthLane | project_root | truth canonical commit |
| ServiceScope | service_key | writable binding + governed branch |
| ServiceWorktree | service_key + feature | real child repo worktree |
| AdmissionArtifact | version + feature | verified parent/service facts |
| WorkerDispatch | run_id + execution_surface | allow_implement=true |

## Domain FSM ImplementAdmission

| State | From | Guard |
|-------|------|-------|
| TruthFrozen | — | canonical truth committed |
| AdmissionResolving | TruthFrozen | implement requested + governance resolved |
| WorktreesMaterializing | AdmissionResolving | topology and writable services complete |
| BaselinesReconciling | WorktreesMaterializing | all worktree paths are real git worktrees |
| Admitted | BaselinesReconciling | strict branch + cwd + HEAD + reconcile checks pass |
| Implementing | Admitted | allow_implement=true + worker cwd admitted |
| ReadyForQA | Implementing | tests pass + implementation evidence present |
| Blocked | AdmissionResolving, WorktreesMaterializing, BaselinesReconciling | any fail-closed reason |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|----|--------|
| TruthFrozen | ImplementRequested | governance_resolved | AdmissionResolving | resolve shared contract |
| AdmissionResolving | TopologySingle | service_count=1 | WorktreesMaterializing | materialize leaf worktree |
| AdmissionResolving | TopologyMonorepo | writable_services_complete | WorktreesMaterializing | materialize each service worktree |
| WorktreesMaterializing | WorktreesVerified | all_real_git_worktrees | BaselinesReconciling | merge parent truth and child baselines |
| BaselinesReconciling | ReconcilePassed | strict_branch_cwd_head_pass | Admitted | write admission artifact |
| Admitted | DispatchRequested | allow_implement=true | Implementing | dispatch direct/team/ralph in admitted cwd |
| Implementing | TestsPassed | evidence_present | ReadyForQA | emit implementation evidence |
| AdmissionResolving | MissingGovernance | any | Blocked | reason=governance_version_not_registered |
| WorktreesMaterializing | FakeOrMissingWorktree | any | Blocked | reason=service_worktree_invalid |
| BaselinesReconciling | ConflictOrMismatch | any | Blocked | reason from strict verifier |

## Illegal transitions

- `ImplementAdmission.TruthFrozen -> Implementing` without shared admission.
- `TruthFrozen -> Implementing` without shared admission.
- `admission.skipped=true -> Implementing`.
- `branch-only -> Implementing` without a materialized real worktree.
- `parent_worktree_only -> Implementing` when writable child repos exist.
- `mkdir-only path -> ServiceWorktree`.
- `empty gitlink -> ServiceWorktree`.
- `stale global seed -> governed implementation contract`.
- `branch mismatch diagnostic -> allow_implement=true`.
- `hook installed -> admission pass`.
- `Admitted -> release complete` without QA evidence and human release confirmation.

## Deferral Ledger

| Deferral ID | Capability | Reason | User Decision | Impact |
|-------------|------------|--------|---------------|--------|
| D-UIA-001 | hooks as primary gate | too late and optional | rejected | none; hooks remain secondary |
| D-UIA-002 | goal-only force-worktree | direct/team/ralph parity would remain broken | rejected | shared admission required |
| D-UIA-003 | cross-machine distributed lease | separate operational concern | accepted defer | no impact on local real-worktree invariant |

## Non-goals

- 不自动签署 release。
- 不在 `main` 写业务实现。
- 不把 QA evaluator 合并进 admission。
- 不为旧 package 形状保留 soft compatibility。
- 不擅自修改客户仓 remote、push 策略或业务代码。

## Downstream Routes

- implement: shared admission、workspace admission、git scope graph、branch governance、goal/team/ralph dispatch
- qa: real Git topology regression + AC evidence
- release: human gate only
