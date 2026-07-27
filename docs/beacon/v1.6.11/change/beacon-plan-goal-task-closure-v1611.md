---
schema: beacon-change-truth-v1
version: v1.6.11
program_slug: beacon-plan-goal-task-closure-v1611
status: frozen
baseline_commit: 30b9adffc8ec5442a7691a88faf64a251d97b98f
truth_canonical_branch: main
change_round: D3
target_revision: R2
previous_revision: R1
change_reason: "D3: formalize CLI deterministic scaffold plus Host LLM full-package fill, migrate semantic compile into current feature-package authority, and close authenticated freeze/recovery gaps"
scope_ack_ref: user-confirmation-2026-07-27
---

# Change Truth: Beacon Plan/Goal Task Closure

## 变更原因

当前 Plan/Goal 已有意图拆解、海湖划分、Truth Review、Program graph 与阶段日志，但仍不能证明“大目标被拆全并持续落地”。关键缺口是 brownfield 基线、递归原子任务 DAG、路径级进度、偏差人工门禁、取消/替代/重排，以及全局收敛证明。

## Before → After

| Surface | Before | After |
|---------|--------|-------|
| baseline | 计划可读取局部材料，但不强制绑定 commit/Truth/test baseline | 每个 Change 固定 commit、Truth revision、代码入口、测试基线与历史 Change |
| intent | 可产出海湖与 journey seed | must 意图递归落到 Journey/AC/Non-goal/Deferral，缺失即阻断 |
| change | 主要是计划文本 | 输出 promise/interface/data/FSM/test 的 Before→After diff |
| task | feature/阶段级任务 | AC/状态/代码/证据绑定的原子任务 DAG，可承载 100+ 节点 |
| progress | Goal stage log | task/path 级 attempts、feedback、blocked、cancelled、replacement、remaining |
| drift | review advisory | drift/padding 命中后强制人工决策 |
| cancel | 无完整语义 | cancelled/superseded/replacement + ready set 重算 |
| done | verifier refs 较粗 | intent/path/AC/state/task/evidence 六层收敛证明 |
| subagent | 旧 Goal/Plan 仅有关键词 gate 与 review pack | TaskNode delegation 合同、真实 execution mode、诚实 fallback、parent-only completion |
| worktree | 旧 unified admission 已冻结但未进入新任务图 | 所有 implementation TaskNode 统一绑定 service/worktree/admission/cwd/HEAD |
| lifecycle | 旧 agent_trace 已覆盖 stage，但新 L0–L8 未映射 | 内部状态映射回 1+6，复用 Goal run_id 与 `agent_trace.v1` |
| compatibility | 旧 shape 可能被误认为历史方言 | fail-closed，唯一升级路径为重新 plan/change/review/freeze |
| generation | CLI scaffold 或 intent-first 可被误认为真实需求已填充 | CLI 只确定性建四文件骨架；Host LLM 通过结构化合同填充完整领域语义 |
| semantic compile | 旧 PRD/User Story 有 host-response/bridge 能力，但输出仍偏旧 shape | 复用其语义抽取与 host transport，统一编译为当前 feature package |
| write authority | Host/LLM 可返回自由 Markdown，难以保证多文件一致 | LLM 只返回 `truth-fill-response.v1`；CLI 校验后通过事务确定性投影四文件 |
| freeze proof | promotion 只看 complete 字符串，hash/gate 证据可漂移 | receipt 必须绑定 R2、最终四文件 hash、validation、Truth Review、human ack 与 PAC trace |

## D3 正式生成合同

| Contract | Producer | Consumer | Required fields |
|----------|----------|----------|-----------------|
| `truth-fill-request.v1` | CLI | Host LLM | utterance、version、R2/base hashes、ContextEnvelope、semantic compiler refs、host transport、Humanizer、Program/PAC refs |
| `truth-fill-response.v1` | Host LLM | CLI validator | L0、Intent/Journey、Matrix、AC、Domain Model、FSM/illegal、Non-goals、TC/task/evidence projection inputs、source hash |
| `truth-fill-transaction.v1` | CLI | truth/projection/freeze gates | transaction_id、request/response hash、base revision、allowed paths、patch result、projection hashes、step sequence/reason codes |
| `truth-human-ack.v1` | human gate | freeze/program gate | scope、finding dispositions、actor、time、accepted R2 hash set |

LLM 不得直接覆盖 Markdown。`features/<slug>/{truth,tests,tasks,evidence}.md` 是唯一 active requirement authority；旧 PRD/User Story semantic compiler 只作为输入解析与 Host transport 能力。

## ChangePlan FSM

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| goal_utterance_captured | resolve_version_context | goal_present | version_context_resolved | seal ContextEnvelope |
| version_context_resolved | materialize_scaffold | refs_and_version_current | scaffold_materialized | create four-file current-shape scaffold |
| scaffold_materialized | request_host_fill | scaffold_unfilled_and_hash_bound | host_fill_requested | emit `truth-fill-request.v1` |
| host_fill_requested | response_received | response_nonempty | structured_fill_produced | bind response/source hashes |
| host_fill_requested | transport_timeout | retryable | retry_wait | record timeout and budget |
| structured_fill_produced | validate_schema | response_hash_current | fill_patch_validating | validate contract, refs and allowed paths |
| fill_patch_validating | validation_pass | schema_semantics_and_hashes_valid | canonical_truth_patching | open atomic transaction |
| fill_patch_validating | validation_fail | findings_present | awaiting_human | publish continue/rewrite/split/replace/cancel |
| canonical_truth_patching | patch_committed | transaction_atomic | projections_regenerating | write canonical truth then deterministic projections |
| projections_regenerating | projections_current | tests_tasks_evidence_current | package_validating | bind four-file hashes |
| package_validating | package_pass | current_shape_complete | truth_review | run package and Truth Review gates |
| package_validating | package_fail | findings_present | awaiting_human | request correction decision |
| truth_review | review_pass | all_checks_pass | awaiting_human_ack | emit accepted hash set |
| truth_review | review_fail | findings_present | awaiting_human | publish findings |
| awaiting_human_ack | acknowledge | truth_human_ack_valid | frozen | freeze R2 and promotion receipt |
| awaiting_human | rewrite | decision_ref | host_fill_requested | request corrected structured fill |
| awaiting_human | split | decision_ref | version_context_resolved | re-scope lake/change |
| awaiting_human | replace | decision_ref | scaffold_materialized | replace fill request |
| awaiting_human | retry | decision_ref_and_retryable | retry_wait | consume retry budget |
| awaiting_human | cancel | decision_ref | cancelled | abort transaction without partial canonical write |
| retry_wait | retry_due | budget_remaining_and_inputs_current | host_fill_requested | retry host transport |
| retry_wait | retry_exhausted | limit_hit | blocked | publish rewrite/cancel route |

终态：`frozen`、`cancelled`、`blocked`。`awaiting_human` 不得无 decision_ref 自动返回执行链。

### invalid / illegal

- `goal_utterance_captured → host_fill_requested` without version/context/scaffold
- scaffold 占位包直接标记 filled/frozen
- Host LLM 直接覆盖四文件或 patch 越过 allowed paths
- `fill_patch_validating → canonical_truth_patching` with stale request/base hash
- `truth_review → awaiting_human_ack` while any package/semantic check fails
- `awaiting_human → host_fill_requested` without decision_ref
- refreeze 后继续使用旧 graph/admission/promotion hash

## TaskRun FSM

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| proposed | dependencies_ready | all_required_done | ready | enter ready set |
| ready | resolve_admission | implementation_task | admission_resolving | call shared admission |
| admission_resolving | admission_pass | real_worktree_and_truth_reconciled | running | bind cwd/HEAD and increment attempt |
| admission_resolving | admission_fail | reason_present | blocked | record reason and route |
| running | submit_evidence | output_present | evidence_pending | bind evidence |
| evidence_pending | verify_pass | assertion_pass | verified | record verifier |
| verified | close | path_consistent | done | aggregate progress |
| running | drift_detected | score_over_threshold | drift_suspected | pause execution |
| drift_suspected | request_decision | finding_complete | awaiting_human | publish choices |
| awaiting_human | continue | human_continue | running | record decision |
| awaiting_human | rewrite | human_rewrite | proposed | replace task contract |
| awaiting_human | split | human_split | superseded | create child tasks |
| awaiting_human | replace | human_replace | cancelled | link replacement |
| awaiting_human | cancel | human_cancel | cancelled | recompute ready set |
| running | execution_fail | retryable | retry_wait | record failure |
| running | execution_timeout | retryable_and_budget_remaining | retry_wait | record timeout |
| running | execution_fail | non_retryable | blocked | publish rewrite/replace/cancel route |
| retry_wait | retry_due | within_policy | ready | requeue |
| retry_wait | retry_exhausted | limit_hit | blocked | block path |

终态：`done`、`cancelled`、`superseded`、`blocked`。

### invalid / illegal

- `proposed → running` with unmet dependencies
- `ready → running` without shared admission for implementation task
- implementation write on main、branch-only、mkdir-only 或 unreconciled worktree
- `running → done` without evidence
- `drift_suspected → running` without human decision
- `cancelled → done`
- required dependency 被取消且无 replacement 时，下游仍进入 ready
- subagent 直接把 GoalRun 标为 complete

## 跨 Program Acceptance

| ID | Requirement | Lake |
|----|-------------|------|
| PAC-001 | Change 绑定 main commit、Truth revision、代码入口与测试基线 | L0/L1 |
| PAC-002 | 每条 must 意图落到 Journey/AC/Non-goal/approved Deferral | L2 |
| PAC-003 | 输出 promise/interface/data/FSM/test Before→After diff | L3 |
| PAC-004 | 任务图可承载 100+ 节点，但禁止按数量注水 | L4/L6 |
| PAC-005 | 每个任务绑定 intent、journey、AC、code scope、dependencies、verification、evidence | L4 |
| PAC-006 | 每条路径聚合 completed/blocked/cancelled/replacement/remaining | L5 |
| PAC-007 | drift/padding 强制进入人工选择门 | L6 |
| PAC-008 | 取消或替换后重算 ready set；必要依赖缺替代则 block | L7 |
| PAC-009 | refreeze 使旧 tasks/tests/evidence stale | L0/L8 |
| PAC-010 | Goal 完成要求全部路径与六层追溯闭环 | L8 |
| PAC-011 | TaskNode 声明子代理角色、execution mode、输入输出和 parent-only completion | L4/L6 |
| PAC-012 | direct/goal/team/ralph 共享真实 worktree admission，refreeze 后旧 admission stale | L4/L7 |
| PAC-013 | L0–L8 内部状态映射回 1+6，并在关键出口写 `agent_trace.v1` | L5/L8 |
| PAC-014 | GoalRun 持有 program/graph/truth/ready/human/admission/trace/verifier refs | L8 |
| PAC-015 | 旧 package/ledger fail-closed，不建兼容 reader，只经新 revision 重新冻结 | L0/L1 |
| PAC-016 | CLI 确定性创建当前四文件 scaffold，未填充不得冒充 complete | L0 |
| PAC-017 | Host LLM 通过结构化合同完整填充 L0/Intent/Journey/AC/Domain/FSM/illegal 与投影输入 | L1/L2 |
| PAC-018 | 旧 PRD/User Story semantic compile 与 host transport 前向迁移到 feature package，不恢复平行旧 shape | L0/L1/L4 |
| PAC-019 | CLI 校验 response schema/base hash/allowed paths 后原子 patch，并确定性再生成 tests/tasks/evidence | L3/L4 |
| PAC-020 | fill 进度、hollow/padding review、timeout/reject/retry/cancel 与 no-open-work closure-ready 全部可回放 | L5/L6/L7 |
| PAC-021 | 九湖 Program freeze 绑定完整 PAC→AC→TC→task/evidence→R2/hash、双门报告与 human ack | L8 |

## Frozen Truth Lineage

| Parent truth | Inherited invariant |
|--------------|---------------------|
| `beacon-plan-goal-deep-integration-v169` | Goal host_subagent gate、stage trace、plan 不实现/不 freeze |
| `beacon-plan-host-subagent-voltpack-v1610` | intent-on、10-role pack、诚实 fallback、禁止假 parallel |
| `unified-implement-admission-v1610` | direct/goal/team/ralph shared admission + real worktree |
| `trace-lifecycle-binding-v1610` | 1+6 → `agent_trace.v1`、append fail 不静默 |
| `truth-core-authority-v1610` | Truth Review、freeze/reopen/stale/refreeze |

## Public Lifecycle Boundary

```text
goal
  → plan
  → truth
  → design (conditional)
  → implement (shared worktree admission)
  → qa (independent)
  → release (human gate)
```

Task graph、progress、drift、cancel/replan、verifier 都是内部控制机制，不新增公共 harness。

## No-compat Migration

```text
old package / old ledger detected
→ block(package_shape_upgrade_required)
→ plan re-decompose
→ truth change in current shape
→ Truth Review Gate
→ freeze new revision
```

旧冻结需求保留为 lineage/evidence；禁止通过 soft skip、legacy reader 或 compatibility adapter 继续交付。

## D3 审查结论

- D3 是 Change 轮次，不是 revision ID；九湖由机器治理入口从 R1 reopen 为 R2。
- R2 复用旧 PRD/User Story 的 semantic compile 能力，但只把语义编译进新 feature-package 规范。
- CLI scaffold 与 Host LLM fill 是两段职责：前者可重复、确定性、无语义自作主张；后者完整填充但无直接写 authority。
- 本 Change 只有在九湖 R2 当前 hash、package validation、Truth Review、human ack、promotion receipt 与 PAC trace 全部一致后才能回到 `frozen`。

## 非目标

- 不把“上百个任务”设成最低数量指标。
- 不允许 host hook 成为唯一强门禁。
- 本 Change 不在 truth 阶段实现代码，也不自证 QA/release。
