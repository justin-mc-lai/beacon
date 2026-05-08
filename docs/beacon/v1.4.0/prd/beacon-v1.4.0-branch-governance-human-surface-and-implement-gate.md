# PRD: Beacon v1.4.0 branch governance human surface and implement gate

**Feature**: `beacon-v1.4.0-branch-governance-human-surface-and-implement-gate`  
**Version**: `v1.4.0`  
**Date**: `2026-05-07`  
**Status**: `freeze-ready`  
**Track**: `support-surface + implement-governance`  
**Scenario**: `branch_governance_contract + human_git_surface + implement_preflight_gate`  
**Template**: `parallel toolkit PRD / support-skill + execution-governance`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version package: `docs/beacon/v1.4.0/SUMMARY.md`
- Execution boundaries: `docs/beacon/v1.4.0/execution/index.md`
- Architecture blueprint: `docs/beacon/v1.4.0/execution/architecture-blueprint.md`
- Related PRD:
  - `docs/beacon/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
  - `docs/beacon/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
  - `docs/beacon/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- Existing toolkit precedents:
  - `docs/beacon/v1.3.2/prd/beacon-v1.3.2-lighthouse-project-analysis-toolkit.md`
  - `docs/beacon/v1.3.3/prd/beacon-v1.3.3-memory-friction-evolution-toolkit.md`
- Source-grounded analysis:
  - `docs/brainstorms/external/2026-05-07-基于-users-apple-developer-company-rolo-的既有摩擦证据-分析-beacon-是否应演进一个面向人类的-git-workflo.md`
  - `docs/brainstorms/external/2026-05-07-结合-rolo-三层-friction-证据-个案摘要-fit-20260507t021547z-完整上下文-fit-20260507t035606z-模板治理.md`

## Overview

`v1.4.0` 现有 requirement 已经把 Beacon 收敛成 lightweight kernel + clearer support surface，但在真实项目开发里，git branch / repo / worktree / merge direction / evidence contract 仍然缺少一条正式的人类可见治理面。现状并不是 Beacon 完全没有 branch guard，而是：

- 项目 metadata 已能表达一部分 canonical branch / service binding；
- `implement` 已能执行 branch preflight；
- 真实项目摩擦已经证明双版本并行、生产热修回灌、worktree 隔离等规则必须更强地模板化；
- 但这些规则仍偏向散落在文档、metadata、debug friction 与 runtime 阻断中，缺少一个稳定的人类面来声明、阅读、校验并执行。

本 PRD 旨在新增一个与 `beacon-toolkit-*` 并排的可选 support skill：`beacon-toolkit-branch-governance`。它不是新的一级命令，也不是新的主生命周期阶段，而是让 Beacon 在进入 `implement` 前，先有一份可读、可视、可投影、可 fail-closed 的 branch governance contract，并在允许条件满足时直接切换到合规 branch / worktree 后再开始开发。

## 2. Scope

In scope:

- 新增 `beacon-toolkit-branch-governance` 作为 host-visible optional support skill。
- 定义 branch governance contract 的人类面与机器面最小字段。
- 为人类面提供清楚的分支流程图与治理摘要。
- 让 `implement` 在进入执行前强制消费该 contract。
- 在满足模板规则与工作区约束时，支持直接切换到合规 branch / worktree 后再进入开发。
- 把双版本并行 + 上版生产热修 + 下版 forward-port 作为正式治理场景纳入。

Out of scope:

- 新增新的公开一级主命令。
- 改写 Beacon 主流程：
  - `prd -> user-story -> test-case -> implement -> qa -> release`
- 让 `beacon-toolkit-branch-governance` 替代 `implement` 成为独立开发入口。
- 在本轮要求完整覆盖所有企业 GitFlow 变体、发布平台或 CI 平台细节。
- 在本轮细化到具体命令参数、JSON 文件路径、类名、模块拆分或底层 git 实现细节。

## Diagram Truth

- `branch-flow`
  - `project default workflow -> task-specific override -> branch governance contract -> implement preflight -> compliant branch/worktree -> implementation`
  - `previous baseline -> hotfix -> uat -> forward-port -> next feature`
  - `next feature -X-> first production fix`
- `state-machine`
  - `contract_state: missing -> resolved -> verified -> blocked | switch_ready`
  - `workspace_state: unresolved -> wrong_branch -> wrong_worktree -> compliant`
  - `execution_state: preflight_pending -> blocked -> switched -> implement_ready`
  - `evidence_state: missing -> partial -> complete`
- `decision-priority`
  - `frozen truth > branch governance contract > runtime workspace convenience`
  - `implement gate > direct coding`
  - `forbidden path block > auto-switch convenience`

### State Axes

- `contract_state`
  - `missing | resolved | verified | blocked | switch_ready`
- `workspace_state`
  - `unresolved | wrong_branch | wrong_worktree | compliant`
- `execution_state`
  - `preflight_pending | blocked | switched | implement_ready`
- `evidence_state`
  - `missing | partial | complete`

## 4. 范围（Human-readable mirror）

In scope:

- 新增 `beacon-toolkit-branch-governance` 作为 host-visible optional support skill。
- 定义 branch governance contract 的人类面与机器面最小字段。
- 为人类面提供清楚的分支流程图与治理摘要。
- 让 `implement` 在进入执行前强制消费该 contract。
- 在满足模板规则与工作区约束时，支持直接切换到合规 branch / worktree 后再进入开发。
- 把双版本并行 + 上版生产热修 + 下版 forward-port 作为正式治理场景纳入。

Out of scope:

- 新增新的公开一级主命令。
- 改写 Beacon 主流程：
  - `prd -> user-story -> test-case -> implement -> qa -> release`
- 让 `beacon-toolkit-branch-governance` 替代 `implement` 成为独立开发入口。
- 在本轮要求完整覆盖所有企业 GitFlow 变体、发布平台或 CI 平台细节。
- 在本轮细化到具体命令参数、JSON 文件路径、类名、模块拆分或底层 git 实现细节。

### 4.1 分层与恢复策略

- `toolkit human surface` 负责清楚展示分支图、摘要和推荐动作。
- `metadata/profile layer` 负责沉淀模板字段与默认治理规则。
- `implement gate layer` 负责在执行前阻断非法路径或执行合规切换。
- 若任一层发现 contract 缺失、evidence 缺失或 lane 不合规，恢复策略必须回到：
  - 补齐 metadata / requirement truth
  - 重建 machine projections
  - 重新进入 `implement` 或 `qa`

## 1. 问题

### 1.1 Beacon 已有 branch guard，但没有稳定的人类 branch governance 面

真实项目摩擦证明，Beacon 当前在 git 治理方面更像“具备部分阻断能力”，而不是“具备一套清楚的人类可见 contract”：

1. metadata 可以表达部分 canonical branch / service binding。
2. `implement` preflight 可以发现 branch mismatch、repo mismatch、worktree 不对齐。
3. 但用户仍需要反复人工解释：
   - 当前该进哪个 service
   - 当前该在哪个 repo root
   - 当前该在哪条 branch
   - 是否必须独立 worktree
   - merge 允许朝哪个方向流动

结果是 Beacon 更像在“发现错误”，而不是先把正确 workflow 显式建立出来。

### 1.2 真实摩擦已经从个案升级为模板治理缺口

外部项目证据已经不只是单次事故，而是三层递进：

1. 个案摘要：暴露出上版生产缺陷与下版 feature 并行时，首修容易错误落入下版开发线。
2. 个案完整上下文：证明补救动作需要 hotfix branch、独立 worktree、forward-port 与 UAT/pipeline evidence。
3. 模板治理缺口：进一步证明这些约束目前仍偏人工阅读，缺少更结构化、可复用、可投影的模板字段。

这说明 Beacon 缺的不是“再写一篇 git 文档”，而是：

> 把 branch governance 升级为可声明、可视化、可校验、可执行的正式 contract。

### 1.3 人类面缺少清楚的分支流程图，导致治理规则难以快速判断

当前 branch 相关信息分散在：

- project metadata
- execution 产物
- friction 报告
- 目标项目 AGENTS 规则
- implement branch guard 阻断结果

这些信息对机器已经部分可用，但对人类而言缺少一个统一的“流程图 + 状态解释”界面。用户无法在进入实现前快速看清：

- 当前场景属于哪种 branch governance template
- 哪些路径允许
- 哪些路径禁止
- 当前工作区处在图上的哪个节点
- 进入 `implement` 前还差哪些条件

### 1.4 `implement` 需要从“被动阻断”升级为“按 contract 执行”

Beacon 全局约束要求：

- `implement` 仍是唯一实现入口
- precheck 必须内嵌到 `implement`

因此本轮不能把 git workflow 拆成新主流程，而应把它收敛为：

> `implement` 前置 branch governance gate。

这意味着：

- 若 contract 不满足，必须 fail-closed；
- 若 contract 满足且允许自动切换，应直接切换到正确 branch / worktree；
- 进入编码时，工作区已经处于合规定义的开发 lane 中。

## 2. 目标

### 2.1 主要目标

1. 新增一个与 `beacon-toolkit-*` 并排的人类面 support skill：`beacon-toolkit-branch-governance`。
2. 让该 skill 能清楚表达 service / repo / branch / worktree / merge direction / evidence contract。
3. 让人类面至少能显示一张正式分支流程图，而不是只显示 branch 文本列表。
4. 让项目 metadata / profile 能沉淀 branch governance 模板字段。
5. 让 `implement` 在进入执行前强制校验 branch governance contract。
6. 在允许条件满足时，由 `implement` 直接切换到合规 branch / worktree 后再开发。
7. 把双版本并行 + 生产缺陷热修 + forward-port 场景正式纳入第一批治理模板。
8. 不新增新的一级公开命令，不扩张主 `6+3`。

### 2.2 非目标

- 不让 `beacon-toolkit-branch-governance` 独立承接编码实施。
- 不把所有 git 历史清理、远端清理、发布编排、CI 编排都装进第一版。
- 不要求第一版支持所有组织自定义 merge 策略的自动执行。
- 不让分支图成为第二真相源；唯一正式执行真相仍由 requirement truth 与投影 contract 决定。

### 2.3 核心判断

本特性的第一性原则是：

> Beacon 不需要新增一个“git 工作流阶段”，而需要把 git branch governance 收敛成人类可见、机器可校验、`implement` 强制执行的一份 contract。

## 3. 设计原则

### 3.1 Canonical first

- 分支治理的人类图示、metadata 模板、implement gate 必须共用同一份 contract 投影。
- 不允许人类面单独解释一套规则、运行时再执行另一套规则。

### 3.2 Fail closed

- 分支、worktree、merge direction、evidence contract 任一关键条件不满足时，必须阻断。
- 自动切换只允许发生在模板明确允许且当前工作区满足安全前提时。

### 3.3 Human clarity before execution

- 在进入 `implement` 前，人类必须先看见当前所处 lane、允许路径、禁止路径和推荐动作。
- 不允许继续依赖散落文本或口头解释承接 branch governance。

## 6. 用户故事

| As a | I want to | So that |
|------|-----------|---------|
| Beacon 维护者 / 项目负责人 | 在进入 `implement` 前先看到清楚的 branch 流程图与当前定位 | 不再靠口头解释或反复纠正分支选择 |
| 真实项目 owner | 为当前版本线声明默认 workflow 或本次定制 workflow | 让 Beacon 知道这次开发应该绑定的 repo / branch / worktree |
| 实现执行者 | 在满足条件时被直接切到正确 branch / worktree 后再开始开发 | 避免在错误分支上先写代码再补治理 |
| 版本负责人 | 在双版本并行、热修回灌场景下看到允许路径、禁止路径和证据要求 | 防止版本线倒挂、来源失真和 UAT 归属混乱 |

## 5. 功能需求

### FR-001 新能力必须采用 toolkit 并排命名，而不是新主命令

该能力必须作为 `beacon-toolkit-*` 体系中的并排新增项存在：

- 建议命名：`beacon-toolkit-branch-governance`
- 定位：optional support skill
- 与 `beacon-toolkit-metadata`、`beacon-toolkit-lighthouse` 属于并排 toolkit surface
- 不得新增新的公开一级主命令
- 不得伪装成新的主生命周期阶段

### FR-002 人类面必须展示清楚的 branch 流程图

人类面必须能够输出正式分支流程图，至少覆盖：

- 当前场景名称
- 节点：baseline branch / hotfix branch / feature branch / UAT target / worktree lane
- 允许路径
- 禁止路径
- 当前定位节点
- 下一步推荐动作

流程图必须支持至少两类正式场景：

1. 标准单版本 feature 开发
2. 双版本并行 + 上版生产缺陷热修 + 下版 forward-port

### FR-003 人类面必须有足够清楚的 git 管理摘要

除流程图外，人类面还必须提供结构化摘要，至少包含：

- `service_key`
- `repo_root`
- `base_branch`
- `current_branch`
- `target_branch`
- `worktree_mode`
- `worktree_path`
- `branch_template_name`
- `merge_direction_policy`
- `evidence_contract_status`
- `blocked_reason`
- `recommended_action`

### FR-004 必须支持默认 workflow 与本次定制 workflow

Beacon 必须允许两层 branch governance 规则共存：

1. 项目级默认 workflow template
2. 当前任务/当前版本的显式覆盖规则

覆盖规则必须受约束：

- 可以收窄执行面
- 可以指定当前场景使用哪一类 template
- 不得静默突破 protected branch / merge direction / evidence contract 等项目级硬约束

### FR-005 metadata/profile 必须沉淀 branch governance 最小模板字段

至少必须正式支持以下模板字段：

- `previous_version_baseline_branch`
- `next_version_feature_branch`
- `hotfix_branch_naming_rule`
- `allow_worktree_when_feature_dirty`
- `merge_direction_policy`
- `evidence_contract`

其中第一批正式治理模板必须能表达：

- 单版本 feature 开发线
- 上版生产缺陷热修线
- hotfix -> uat -> next feature forward-port 双线并行场景

### FR-006 `implement` 必须在进入执行前强制消费 branch governance contract

`implement` 仍是唯一实现入口，但进入执行前必须完成：

1. 载入项目 metadata / profile
2. 解析当前 governance template
3. 校验当前 repo / service / branch / worktree / merge direction
4. 判断 evidence contract 要求
5. 产出 pass / warn / blocked verdict

没有通过 contract gate 时，不得进入编码实现。

### FR-007 合规条件满足时，必须支持直接切换到规范 branch / worktree

如果当前场景允许自动治理动作，Beacon 必须支持：

- 切换到既有合规 branch
- 或创建 / 切换到合规 worktree
- 然后再进入 `implement`

该动作必须受以下约束：

- 只能发生在 governance template 明确允许时
- 必须保留人类可见的切换说明
- 若工作区不满足切换条件，必须阻断而不是偷偷继续

### FR-008 merge direction policy 必须正式化，并能阻断非法路径

Beacon 必须把 merge direction policy 作为正式检查对象。

对于双版本并行 + 热修回灌场景，最小要求是：

- `previous_baseline -> hotfix`
- `hotfix -> uat`
- `hotfix -> next_feature`（通过 `cherry-pick` / `forward-port`）

并且必须明确禁止：

- `next_feature` 作为上版生产缺陷的首修承接线

### FR-009 evidence contract 必须可见且可校验

Beacon 必须把 git workflow 的关键证据正式化，至少包括：

- `source_commit`
- `forward_port_commit`
- `origin_uat_head`
- `pipeline_run_id`

人类面必须能看见这些证据是否齐备，`implement` / `gate` 必须能基于这些字段给出明确 verdict。

### FR-010 关键不合规状态必须 fail-closed

以下情况必须默认阻断：

- 当前 repo / service 不在目标执行面
- 当前 branch 不符合 template
- 需要 hotfix lane 但当前停留在下版 feature lane
- 需要 worktree 隔离但当前仍在不合规工作树
- merge direction 不合法
- evidence contract 缺失，导致来源不可审计

## 9. 人类面图示要求

### 5.1 标准 feature 开发图

```text
base_branch
    -> feature_branch
    -> uat
```

必须能清楚显示：

- 当前 feature 绑定的 service / repo
- target branch
- 是否要求独立 worktree
- 从当前节点到下一节点的推荐动作

### 5.2 双版本并行 + 热修回灌图

```text
previous_version_baseline
    -> hotfix_branch
    -> uat
    -> forward-port
    -> next_version_feature_branch
```

必须额外清楚显示：

- 上版基线与下版 feature 是两条不同 lane
- hotfix 是上版生产问题的首修承接线
- forward-port 是把 hotfix 回灌到下版 feature 的动作
- `next_version_feature_branch` 不能替代 hotfix 作为首修入口

### 5.3 禁止路径图示

人类面必须显式画出或标记禁止路径，例如：

```text
next_version_feature_branch -X-> first production fix branch
```

禁止路径不能只存在于文字说明中，必须在图或图例中可见。

## 10. 最小 contract 形态

最低限度，Beacon 必须能投影出类似以下语义 contract：

```json
{
  "schema_version": "1.0",
  "template_name": "previous-hotfix-forward-port",
  "service_key": "marketing_sys",
  "repo_root": "marketing_sys",
  "previous_version_baseline_branch": "feature/v1.3.3-all",
  "next_version_feature_branch": "feature/laikunqi_v1.3.4",
  "hotfix_branch_naming_rule": "hotfix/<ticket>-<version>",
  "allow_worktree_when_feature_dirty": true,
  "merge_direction_policy": [
    "previous_baseline->hotfix",
    "hotfix->uat",
    "hotfix->next_feature"
  ],
  "forbidden_directions": [
    "next_feature->first_production_fix"
  ],
  "evidence_contract": [
    "source_commit",
    "forward_port_commit",
    "origin_uat_head",
    "pipeline_run_id"
  ]
}
```

该示例仅用于冻结语义边界，不要求本 PRD 同时冻结底层存储实现。

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 人类面再次膨胀为第二主流程 | 高 | 明确为 toolkit/support skill，`implement` 仍是唯一实现入口 |
| 图示过强但 contract 过弱，变成只读说明书 | 高 | 让图示与 metadata/gate 共享同一 governance contract 投影 |
| 项目特例太多导致模板不可复用 | 中 | 第一版只冻结少数高价值场景，先保留默认 + 覆盖两层模型 |
| 自动切换 branch/worktree 误操作 | 高 | 只在合规条件满足时执行，否则 fail-closed |
| 证据字段过多拖重第一版 | 中 | 先冻结四个最小 evidence 字段，后续再扩展 |

## 8. 验收标准

1. 人类可以在进入 `implement` 前清楚看见分支流程图与当前定位。
2. Beacon 可以区分默认 workflow 与本次定制 workflow。
3. branch governance template 至少支持标准 feature 与双版本热修回灌两类场景。
4. `implement` 会强制消费 governance contract，并在不合规时阻断。
5. 合规条件满足时，Beacon 能先切到规范 branch / worktree，再进入开发。
6. `beacon-toolkit-branch-governance` 与现有 toolkit 并排存在，而不扩张主 `6+3`。

---

**Created**: 2026-05-07  
**Version**: v1.4.0  
**Status**: Draft  
**Change Context**: branch governance human surface + implement gate evolution candidate
