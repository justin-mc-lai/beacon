# User Story: Beacon v1.4.0 branch governance human surface and implement gate

## Story Boundary

- version: `v1.4.0`
- feature: `beacon-v1.4.0-branch-governance-human-surface-and-implement-gate`
- status: `freeze-ready`
- upstream_prd: `docs/beacon/v1.4.0/prd/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.md`
- current_revision: `R1`
- source_revision: `R0`

本故事线覆盖 Beacon 在 `v1.4.0` 中新增一条并排 toolkit/support 子线：`beacon-toolkit-branch-governance`。目标不是新增 Git 主流程，而是把 branch governance 收敛成一个清楚的人类面、一个稳定的模板 contract、以及一个 `implement` 内嵌 preflight gate。

## Diagram Truth

- `branch-flow`
  - `project default workflow -> task-specific override -> branch governance contract -> implement preflight -> compliant branch/worktree -> implementation`
  - `previous baseline -> hotfix -> uat -> forward-port -> next feature`
  - `next feature -X-> first production fix`
- `decision-priority`
  - `frozen truth > branch governance contract > runtime workspace state`
  - `mainline lifecycle > optional toolkit`
  - `contract compliance > convenience`

## Story 1: `beacon-toolkit-branch-governance` 必须作为并排 toolkit 暴露，而不是新主命令

作为 Beacon 产品 owner，我希望 branch governance 能力进入 `beacon-toolkit-*` 并排体系，而不是长出新的一级命令或新阶段，这样主流程和人类面仍保持克制。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | toolkit-tier | `beacon-toolkit-branch-governance` 必须作为 optional support/toolkit skill 暴露。 |
| AC-002 | no-public-command | 系统不得为该能力新增新的公开一级主命令。 |
| AC-003 | no-new-stage | 系统不得把该能力升级成新的 lifecycle stage。 |
| AC-004 | alongside-toolkits | 该能力必须与 `beacon-toolkit-metadata`、`beacon-toolkit-lighthouse` 并排存在。 |

## Story 2: 人类面必须有清楚的分支流程图与当前定位

作为项目负责人，我希望在进入 `implement` 前先看到清楚的 branch 流程图、当前节点和下一步动作，这样不需要再口头反复解释当前该走哪条线。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | flow-diagram-required | 人类面必须输出正式分支流程图，而不是只显示 branch 文本。 |
| AC-102 | current-position-visible | 流程图必须显示当前 workspace 位于图上的哪个节点。 |
| AC-103 | allowed-forbidden-visible | 流程图必须明确区分允许路径与禁止路径。 |
| AC-104 | next-action-visible | 人类面必须为当前状态给出下一步推荐动作。 |

## Story 3: 人类面必须有足够清楚的 git 管理摘要

作为执行者，我希望除了图之外，还能看到 service、repo、branch、worktree、evidence 这些关键字段，这样我能快速判断当前是否合规。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | service-repo-visible | 人类面必须显示目标 `service_key` 与 `repo_root`。 |
| AC-202 | branch-state-visible | 人类面必须显示 `base_branch / current_branch / target_branch`。 |
| AC-203 | worktree-state-visible | 人类面必须显示 `worktree_mode / worktree_path`。 |
| AC-204 | governance-verdict-visible | 人类面必须显示 `branch_template_name / evidence_contract_status / blocked_reason / recommended_action`。 |

## Story 4: 系统必须支持默认 workflow 与任务级覆盖 workflow

作为项目 owner，我希望 Beacon 既能遵守项目默认分支规则，也能为当前任务声明一个更具体的治理模板，这样复杂项目里不会所有任务都挤进同一条模糊规则。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | project-default-template | 系统必须支持项目级默认 branch governance template。 |
| AC-302 | task-override-template | 系统必须支持当前任务/当前版本的显式覆盖规则。 |
| AC-303 | override-cannot-break-hard-rules | 覆盖规则不得突破 protected branch、merge direction、evidence contract 等硬约束。 |
| AC-304 | template-selection-visible | 当前采用的是默认模板还是覆盖模板，必须对人类可见。 |

## Story 5: metadata/profile 必须沉淀 branch governance 模板字段

作为维护者，我希望 Beacon 能把 branch governance 规则写成正式模板字段，而不是继续依赖长篇自然语言说明，这样它才能被复用和校验。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | baseline-field | metadata/profile 必须支持 `previous_version_baseline_branch`。 |
| AC-402 | next-feature-field | metadata/profile 必须支持 `next_version_feature_branch`。 |
| AC-403 | hotfix-and-worktree-fields | metadata/profile 必须支持 `hotfix_branch_naming_rule` 与 `allow_worktree_when_feature_dirty`。 |
| AC-404 | governance-contract-fields | metadata/profile 必须支持 `merge_direction_policy` 与 `evidence_contract`。 |

## Story 6: `implement` 必须在进入执行前执行 branch governance gate

作为平台治理 owner，我希望 `implement` 在真正开始编码前先跑 branch governance preflight，这样 Beacon 不会在错误 branch/worktree 上先干活、后补治理。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | implement-loads-contract | `implement` 进入执行前必须载入 branch governance contract。 |
| AC-502 | implement-verifies-alignment | `implement` 必须校验 repo / service / branch / worktree / merge direction 对齐。 |
| AC-503 | evidence-checked | `implement` 必须校验 evidence contract 要求。 |
| AC-504 | blocked-no-code | contract 不通过时不得进入编码实现。 |

## Story 7: 合规条件满足时，系统必须先切到规范 branch/worktree 再开发

作为实现执行者，我希望如果当前场景允许自动治理，Beacon 能先切到正确 branch/worktree 再进入开发，这样开发现场从第一步就是合规的。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-601 | switch-to-compliant-branch | 合规条件满足时，系统必须支持切换到既有合规 branch。 |
| AC-602 | create-or-switch-worktree | 模板要求 worktree 隔离时，系统必须支持创建或切换到合规 worktree。 |
| AC-603 | switch-explained-to-human | 该切换动作必须对人类可见并有清楚说明。 |
| AC-604 | fail-closed-if-cannot-switch | 不满足切换条件时必须阻断，不得静默继续开发。 |

## Story 8: 双版本并行热修回灌必须成为第一批正式治理场景

作为版本负责人，我希望 Beacon 能正式表达“上版生产缺陷 + 下版 feature 已开工”的双线并行模型，这样版本线不会继续倒挂。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-701 | previous-hotfix-forward-port-template | 系统必须支持 `previous baseline -> hotfix -> uat -> forward-port -> next feature` 模板。 |
| AC-702 | forbidden-next-feature-first-fix | 系统必须明确禁止 `next feature` 作为上版生产缺陷的首修承接线。 |
| AC-703 | evidence-fields-minimum | 该场景至少要求 `source_commit / forward_port_commit / origin_uat_head / pipeline_run_id`。 |
| AC-704 | flow-diagram-shows-dual-lane | 人类面流程图必须清楚表达上版 lane 与下版 lane 是两条不同线。 |

## Delivery Notes

- 这条子线不是把 git workflow 升级成主流程，而是把它收敛成：
  - optional toolkit 人类面
  - metadata/profile 模板层
  - `implement` 内嵌 gate
- 重点在：
  - 清楚图示
  - contract 化
  - fail-closed
  - 直接切换到合规开发现场

## Freeze Notes

- 当前冻结目标不是证明底层 git 自动化已经完全实现，而是把 branch governance 的 requirement contract 正式冻结。
- 如果后续实现仍然：
  - 只输出散乱文本而无流程图
  - 不能表达模板字段
  - `implement` 仍只是被动报错
  - 能在不合规 branch 上继续开发
  则该 feature 不应视为完成。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 8 |
| Status | freeze-ready-r1 |
| Created | 2026-05-07 |
| Change Scope | toolkit-surface / branch-governance-contract / metadata-template / implement-preflight / worktree-switch / dual-version-hotfix |
