# Beacon Brainstorm

## prompt_summary
基于当前 Beacon 代码实现，核实现阶段 `implement` 之前到底对冻结材料做了哪些严格 gate，哪些只是默认 seed；并收敛 `v1.4.8` 后续应正式冻结的“最低可实现闭环前置文档目录”。重点关注：开发服务、开发分支、是否 worktree、takeover baseline、architecture blueprint projection、implementation delivery baseline 等是否必须存在，缺失时是否真的阻断。

- date: `2026-05-21`
- version_context: `v1.4.8`
- mode: `project-evolution`
- canonical_mode: `project-evolution`

## source_anchors
- `beacon/commands/implement.py`
- `beacon/utils/implementation_plan.py`
- `beacon/utils/technical_review_contract.py`
- `beacon/utils/delivery_baseline.py`
- `beacon/utils/governance.py`
- `beacon/utils/branch_governance.py`
- `beacon/utils/git_alignment.py`
- `tests/test_v138_takeover_implementation_blueprint.py`
- `tests/test_v147_automation_support_review_and_promotion_contract.py`
- `docs/beacon/v1.4.8/research/beacon-v1.4.8-human-subskill-material-closure-and-gate-contract.md`

## confirmed_facts

### 1. 当前 Beacon 在 `implement` 前确实有多层 gate

代码层已明确存在：

- requirement closure preflight
- automation runtime preflight
- branch preflight
- takeover baseline gate
- implementation plan gate
- technical review contract gate
- implementation delivery baseline gate
- architecture blueprint projection gate

其中关键阻断路径已在 `beacon/commands/implement.py` 接线：

- `takeover_gate` blocked -> implement blocked
- `branch_preflight` blocked -> implement blocked
- `implementation_plan_gate` blocked -> implement blocked

### 2. takeover 项目当前被严格要求的前置文档只有 3 个

`beacon/utils/governance.py` 当前 hard gate 的 takeover baseline 文档是：

- `execution/architecture-blueprint.md`
- `execution/current-state-service-map.md`
- `execution/refactor-boundaries.md`

只要是 takeover 项目：

- 缺文件会阻断
- 文档状态是 `draft` 也会阻断
- baseline 未 frozen 也会阻断

### 3. implementation plan gate 已经强制要求 delivery baseline 和 architecture blueprint projection

`beacon/utils/implementation_plan.py` 当前会阻断：

- `delivery_baseline_missing`
- `architecture_blueprint_projection_missing`
- `architecture_blueprint_projection_drift`

这意味着：

- `execution/architecture-blueprint.md` 不只是建议存在
- 它必须存在
- 还必须带有受控 managed projection block

### 4. branch / service / worktree 信息当前并非全部要求“先由人显式冻结”

这是当前实现最关键的不足。

`technical_review_contract` 和 `git_workflow_contract` 在很多情况下会从默认值或配置 seed：

- `target_branch` 没给 -> 默认 `beacon/<version>`
- `service_directories` 没给 -> 默认 `["."]`
- `writable_services` 没给 -> 默认等于 `service_directories`
- `worktree_root` 没给 -> 默认 `project_root`
- `use_git_worktree` 没给 -> 默认 `False`

也就是说：

- 当前 Beacon 对“这些字段最终要存在”是有 gate 的
- 但对“这些字段必须先由真实冻结材料显式提供，而不是靠默认 seed”还不够严格

### 5. 目前并没有对 `service-slice-map.md` 做 implement 前硬 gate

从代码看：

- `service-slice-map.md` 不是当前 `takeover baseline gate` 的 required docs
- `branch-governance` 也不是 implement 前固定必需文档
- `execution/index.md` 也不是 implement 前固定必需文档

这和一些更完整的历史执行面相比，是收缩过的最低实现集。

## strongest_claim

当前 Beacon 已经不是“完全不 gate”。

更准确的结论是：

> 当前 Beacon 已经对 requirement closure、takeover baseline、delivery baseline、architecture blueprint projection 做了较强 gate；但对“开发服务 / 开发分支 / worktree 是否必须来自显式冻结材料而非默认 seed”仍然不够严苛。

## weakest_proof

当前最弱的一点不是 gate 不存在，而是：

- `technical_review_contract` 缺失时，很多字段可以由默认模板生成
- `git_workflow_contract` 缺失时，也会 seed 默认 branch / service / worktree 信息

因此现在更像：

```text
必须有 contract
但 contract 中的部分关键事实仍可能由默认值兜底
```

而不是：

```text
必须有来自冻结材料的显式真实事实
否则 implement 不得继续
```

## risk_register

### Risk 1: 假真值问题

当以下字段由默认 seed 生成时：

- `target_branch`
- `service_directories`
- `writable_services`
- `worktree_root`
- `use_git_worktree`

系统满足了“文件存在”，却不一定满足“事实真实”。

### Risk 2: 多服务项目被单仓默认值弱化

如果没有显式冻结服务映射，多服务项目可能退回：

- `service_directories=["."]`
- `writable_services=["."]`

这会削弱交付边界。

### Risk 3: worktree 约束仍可被默认关闭

如果项目实际需要 worktree，但 contract 只靠默认 `False`，则 implement 前不一定会暴露这个要求。

### Risk 4: 目录级 host contract 仍然过窄

当前强 gate 的最低目录不包含：

- `execution/index.md`
- `execution/service-slice-map.md`
- 独立 branch/worktree governance 文档

所以“可实现闭环”是有了，但“可审计、可读、可恢复的 execution host”仍偏弱。

## converged_recommendation

### A. 当前代码事实判断

如果问题是：

> Beacon 目前是否已经把冻结材料里的版本内容信息做了严格 gate？

答案是：

- `是，部分已经严格 gate`
- `但还没有严格到“关键开发事实必须来自显式冻结材料，不能靠默认 seed”`

### B. `v1.4.8` 应提升的严苛性

后续应把以下信息升级成“必须来自显式冻结材料”的 implement 前 gate：

- 开发服务集合
- 可写服务集合
- target branch / per-service branch
- 是否使用 git worktree
- worktree root / per-service worktree map

至少在多服务或 takeover 项目中，不应允许这些关键字段只靠默认值补齐。

## minimum_directory_under_study

基于当前代码与缺口，我建议 `v1.4.8` 后续正式冻结的“最低可实现闭环前置文档目录”是：

```text
docs/beacon/<version>/
├── SUMMARY.md
├── prd/
├── user-story/
├── qa/test-cases/
├── execution/
│   ├── index.md
│   ├── architecture-blueprint.md
│   ├── current-state-service-map.md        # takeover required
│   ├── refactor-boundaries.md              # takeover required
│   ├── service-slice-map.md                # multi-service / takeover recommended -> v1.4.8 candidate hard gate
│   └── branch-governance-<feature>.md      # branch/worktree 事实推荐升级为固定执行面
└── .machine/
    ├── execution/
    │   ├── implementation-delivery-host.json
    │   ├── implementation-delivery-baseline-<feature>.json
    │   ├── git-workflow-<feature>.json
    │   └── technical-review-contract-<feature>.json
    └── qa/
```

## minimum_gate_proposal_for_v148

### 对所有 execution-bound feature

至少要求：

- `prd`
- `user-story`
- `qa/test-cases`
- frozen revision state
- technical review contract
- implementation delivery baseline
- architecture blueprint projection

### 对 takeover 项目

至少再要求：

- `execution/current-state-service-map.md`
- `execution/refactor-boundaries.md`

### 对 multi-service / takeover 项目

建议 `v1.4.8` 升级成 hard gate：

- `execution/service-slice-map.md`
- branch/worktree governance surface
- 显式 per-service branch/worktree mapping

## human_subskill_material_closure_supplement

本轮新增一个必须纳入 `v1.4.8` 后续 change/PRD 的补充结论：

> 人类面的 Beacon 子 skill 调用不能只停留在“给出建议”。每个子 skill 必须显式落到材料更新、材料更新义务、truth reopen、execution host 更新、evidence 更新，或只读 route-only 结论之一。

补充研究文档：

- `docs/beacon/v1.4.8/research/beacon-v1.4.8-human-subskill-material-closure-and-gate-contract.md`

关键收敛：

- `beacon-toolkit-branch-governance` 如果只是 show / verify，可以保持只读；如果人类意图是更新交付服务、开发分支、worktree，则必须写回 canonical execution host / metadata / git workflow / technical review contract。
- support skill 不应直接写 truth；但 accepted finding 必须转成 `beacon-change`、对应 truth surface、execution host update、QA evidence update、release blocker，或 `artifact_update_obligations`。
- 缺少显式 Beacon 材料不能再被解释为“默认不需要”；如果该 surface 被触发或被下游 gate 依赖，就必须 fail closed。
- 默认 seed 不能等价于冻结事实，尤其是 delivery services、target branch、worktree mode、writable services。

## route_back

这轮结论已经超出单纯实现细节讨论，涉及 execution host truth contract 的提升。

推荐下一跳：

- `beacon-change`

后续应冻结一个新的 `v1.4.8` feature line，专门提升：

- execution host minimum directory contract
- branch/service/worktree explicit-truth gate
- default seed -> explicit frozen fact 的治理升级
