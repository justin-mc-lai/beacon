# Beacon v1.3.7 Implement Direct Bootstrap and Conflict Gate Analysis

**Date**: 2026-04-23  
**Method**: 基于现有 `implement` 命令源码、`memory-friction-evolution` 信号、全局边界约束做收敛分析  
**Purpose**: 判断 Beacon 是否可以提供“直接实现”入口，并在不破坏 requirement truth 的前提下，把 requirement/bootstrap/freeze/technical-review 的前置动作尽量内嵌到 `implement`。

---

## 1. Summary

这份调研的核心结论是：

- Beacon 当前不支持“没有 formal requirement package 就直接开始正式实现”。
- 这不是单纯的产品习惯，而是当前源码和全局边界共同决定的硬约束。
- `implement` 可以在 `v1.3.7` 变得更极简，但正确方向不是删除 `prd`，而是把 requirement bootstrap 和前置核实内嵌到 `implement` 内部。
- 推荐的演进方向是：
  - 对外仍保持 `implement` 作为唯一实现入口。
  - 对内新增 `direct bootstrap` 子流程。
  - 默认先核实、自动补齐、自动冻结、自动生成技术交付基础信息。
  - 只有在和已冻结 truth 冲突、边界不清、canonical baseline 无法稳定生成、或 git/worktree 约束不满足时才阻断。
- `v1.3.7` 最关键的新要求，不应是“允许跳过 PRD”，而应是：
  - `implement plan` 阶段必须先定义 canonical 的 implementation delivery baseline envelope
  - `architecture-blueprint.md`、deterministic implementation contract、git workflow contract、implementation plan 全部从这个 canonical envelope 单向投影生成
  - gate 校验的是这些投影和 canonical envelope 的一致性，而不是允许多个文档互相对表后都算真相。
- `architecture-blueprint.md` 仍然需要支持：
  - 版本级唯一 baseline mirror
  - feature 显式分块 baseline mirror
- 但它的角色是 human-readable projection，不是可反向驱动 machine truth 的平级真相源。

一句话：

> `v1.3.7` 应该把 “先补齐 truth，再直接实现” 内嵌成 `implement` 的默认机器行为，而不是把 “无 truth 直接实现” 变成合法主路径。

---

## 2. Current Baseline

### 2.1 当前 `implement` 的真实前置条件

当前实现中，`compile_implementation_plan(...)` 会先做三层硬 gate：

1. revision 必须已经 `frozen`
2. technical review contract 必须存在且通过校验
3. `prd / user-story / test-case` source refs 必须齐全

关键代码路径：

- `beacon/utils/implementation_plan.py`
  - `revision_not_frozen`
  - `technical_review_contract_missing` / `technical_review_contract_invalid`
  - `implementation_plan_source_refs_incomplete`
- `beacon/commands/implement.py`
  - `run_implement_stage(...)` 在真实执行前会先跑 implementation plan gate
  - `implement dev-run` 也会先 `compile_implementation_plan(...)`

这意味着：

- 当前 Beacon 不是“有 feature 名就可以开始实现”
- 而是“有 frozen requirement truth + technical delivery contract + plan truth 后，才能正式进入实现”

### 2.2 当前 `freeze` 也不是空动作

`freeze` 本身也不是简单打标，而是先跑 requirement clarity gate，再冻结 revision。

这说明当前系统语义是：

```text
requirement clarity
-> freeze
-> technical review contract
-> implementation plan
-> implement run
```

### 2.3 当前 release 已依赖 implementation plan truth

`release` gate 已经依赖 implementation plan 的存在、完成度和 AC/TC/QA 对齐关系。

这意味着 implementation plan 已经不是“可选辅助文档”，而是正式交付真相的一部分。

---

## 3. Global Boundary Constraint

Beacon 全局边界已经明确要求：

- `implement` 仍是唯一公开实现入口
- `prd -> user-story -> test-case -> acceptance` 是立项根本
- 所有 implement lane 都必须绑定同一份 `prd / user-story / test-case`
- runtime mode 只能改变执行形态，不能改变 requirement truth

这带来一个非常清楚的边界：

### 3.1 可以做的

- 把更多前置动作内嵌到 `implement`
- 自动生成 requirement package 的最小初稿
- 自动跑 clarity/freeze/contract/plan
- 自动在无冲突情况下继续实现

### 3.2 不能做的

- 让 `implement` 脱离 `prd / user-story / test-case`
- 让 `single / team / ralph` 使用不同 truth
- 让 runtime 完成信号代替 formal requirement truth

所以真正的问题不是：

> “Beacon 能不能不要 PRD”

而是：

> “Beacon 能不能让用户不必手工先走完整 PRD 流程，但系统内部仍然自动形成并冻结同一份 truth”

答案是：可以，而且这正是 `v1.3.7` 最值得做的收敛方向。

---

## 4. Friction Signals

### 4.1 用户侧摩擦

从人类视角，当前主要摩擦是：

- 想直接开始实现，却必须先理解多段前置流程
- requirement package 需要先显式准备，启动成本高
- technical delivery metadata 分散在多个 artifact 中，不够集中
- `architecture-blueprint.md` 还没有承担实现前置基础信息的稳定 truth 角色

### 4.2 已有 memory/friction 证据

最新一次 `memory-friction-evolution` 报告在：

- `.beacon/analysis/memory-friction-evolution-mfe-20260422T153436Z.md`

其中和本议题直接相关的 friction 包括：

- `runtime_feedback`
- `prd-create-generic-template-only`
- `prd-implement-delivery-drift-gate-missing`

这些信号说明：

- 用户希望 Beacon 更像“核实后直接推进”的系统
- 但系统又必须避免 requirement drift 和 delivery metadata drift

---

## 5. Real Problem to Solve in v1.3.7

`v1.3.7` 真正需要解决的不是“让 implement 更随意”，而是同时解决以下两件事：

1. 降低启动摩擦  
   让用户可以从 `implement` 直接开始，不必手工逐段操作。

2. 保持交付真相一致  
   让 requirement truth、architecture blueprint、technical review contract、git workflow contract、implementation plan 保持同源一致。

因此，`v1.3.7` 的核心命题应定义为：

> Implement Direct Bootstrap with Conflict Gate

即：

- 用户从 `implement` 进入
- 机器自动补 requirement / freeze / technical delivery metadata
- 冲突时阻断
- 一致时继续实现

---

## 6. Candidate Approaches

## 6.1 Approach A: 保持现状，只优化文档

做法：

- 不改命令逻辑
- 只补文档说明 `implement` 的前置条件

优点：

- 风险最低
- 不改 runtime

缺点：

- 无法降低真实启动摩擦
- 用户仍然必须手工走前置流程
- 不能解决“技术实现交付物分散且易漂移”的问题

结论：

- 不推荐作为 `v1.3.7` 主方案

## 6.2 Approach B: 允许完全跳过 requirement truth

做法：

- `implement` 直接根据用户输入开工
- 结束后再反写 requirement

优点：

- 入口最短

缺点：

- 直接违反全局边界
- release gate 语义会塌
- implementation plan、QA、release 都失去统一 truth

结论：

- 明确拒绝

## 6.3 Approach C: `implement` 内嵌 direct bootstrap

做法：

- `implement` 发现 source-of-truth 缺失时，不立即失败
- 先进入内部 bootstrap 流程
- 自动补齐 requirement package、freeze、technical contract、architecture blueprint、implementation plan
- 若无冲突则继续实现

优点：

- 保留 Beacon 的 truth discipline
- 大幅降低人类启动摩擦
- 符合“复杂度留在机器内部”的全局原则

缺点：

- 需要重整前置 contract 之间的写入顺序和 ownership
- 需要更严格的一致性校验

结论：

- 推荐作为 `v1.3.7` 主方向

---

## 7. Recommended v1.3.7 Model

推荐模型：

```text
implement
-> detect requirement readiness
-> if missing: direct bootstrap
-> requirement clarity
-> freeze
-> synthesize canonical implementation delivery baseline envelope
-> validate and commit canonical envelope
-> project architecture blueprint mirror
-> materialize deterministic implementation contract
-> materialize git workflow contract
-> compile implementation plan
-> verify projection consistency against canonical envelope
-> implementation run
```

### 7.1 对外命令面

对外不新增新的一级命令。

保持：

- `implement`

允许的产品语义有两种：

- `implement run "<feature>"`
- `implement run "<feature>" --direct`

其中 `--direct` 只是显式提示“允许自动补齐前置 truth”，不是第二套工作流。

也可以进一步收敛成：

- 默认即 direct bootstrap
- 用 `--strict-preflight` 强制只有 formal package 才能运行

从产品极简角度，后者更干净。

### 7.2 对内机器流程

内部新增一个不可见阶段：

- `implement bootstrap`

它不是新的人类命令，而是 `implement` 内嵌 preflight。

职责：

- 解析用户意图、代码上下文、已有 docs
- 判断是否已有 frozen truth
- 如果缺失则生成最小 requirement package
- 自动做 clarity/freeze
- 自动合成 canonical 的 implementation delivery baseline envelope
- 只在 canonical 无法稳定生成或与 frozen truth 冲突时阻断

---

## 8. Canonical Delivery Baseline in Plan Stage

这是 `v1.3.7` 最重要的新收敛点。

当前技术交付基础信息分散在：

- deterministic implementation contract
- git workflow contract
- implementation plan
- project config seed

仅仅把这些信息“补充到 `architecture-blueprint.md`”还不够稳。结合全局边界里的 canonical / projection 约束，更稳的收敛方式应是：

> 先生成 canonical 的 implementation delivery baseline envelope，再把它单向投影到 `architecture-blueprint.md`、deterministic implementation contract、git workflow contract、implementation plan。

### 8.1 为什么必须先有 canonical envelope

原因：

- 全局边界已经要求 canonical envelope 是唯一提交源，不能让 human 文档反向驱动 machine truth。
- 当前分散的 contract 字段高度重叠，如果没有单一 canonical source，后续只会变成多文档对表。
- `architecture-blueprint.md` 适合做人类审阅镜像，但不适合兼任可随意编辑的执行真相源。
- `implement plan`、`release gate`、`doctor/status` 都需要同一份可审计事务元数据，而不是多份互相比对的局部合同。

### 8.2 建议的 canonical envelope 结构

建议在机器侧先定义一个固定 envelope，例如：

```text
implementation_delivery_baseline:
  schema_version:
  version:
  baseline_id:
  transaction_id:
  source_hash:
  projection_seq:
  committed_at:
  baseline_scope:
  workspace_root:
  branch_strategy:
  base_branch:
  branch_prefix:
  default_target_branch:
  use_git_worktree:
  worktree_root:
  environment_mode:
  isolation_strategy:
  direct_delivery_services:
  writable_services:
  reference_only_services:
  shared_contracts:
  service_branch_map:
  service_worktree_map:
  feature_overlays:
```

其中：

- 顶层 envelope 是唯一 canonical truth。
- `feature_overlays` 记录 feature 级精确交付边界。
- version 级字段表达这一条版本线允许的交付总边界。
- 所有人类文档和执行合同都只消费这份 envelope 的投影。

### 8.3 `architecture-blueprint.md` 的固定镜像块

建议在 `docs/beacon/archive/v1.3.7/execution/architecture-blueprint.md` 中新增两层固定章节：

```text
## Version Delivery Baseline

- baseline_scope: version
- baseline_id:
- source_hash:
- projection_seq:
- workspace_root:
- branch_strategy:
- base_branch:
- branch_prefix:
- use_git_worktree:
- worktree_root:
- environment_mode:
- isolation_strategy:

## Version Delivery Service Scope

- direct_delivery_services:
- writable_services:
- reference_only_services:
- shared_contracts:
```

以及按 feature 追加的显式分块：

```text
## Feature Delivery Baseline: <feature-slug>

- baseline_scope: feature
- feature:
- canonical_overlay_id:
- source_hash:
- projection_seq:
- implementation_source_mode:
- workspace_root:
- branch_strategy:
- base_branch:
- target_branch:
- branch_prefix:
- use_git_worktree:
- worktree_root:
- environment_mode:
- isolation_strategy:

## Feature Delivery Service Scope

- direct_delivery_services:
- writable_services:
- reference_only_services:
- shared_contracts:

## Plan-Time Gate Contract

- architecture_blueprint_status:
- contract_sync_status:
- plan_sync_status:
- last_verified_at:
- canonical_baseline_id:
- canonical_source_hash:
- canonical_projection_seq:
```

### 8.4 双层 baseline 的建议语义

`v1.3.7` 推荐直接支持两种 baseline 并存：

1. **版本级唯一 baseline**
   - 作用：声明这一条版本线允许的实现边界总集
   - 语义：是当前版本所有 feature delivery baseline 的统一上界
   - 典型用途：
     - 多服务 monorepo
     - 多 git roots workspace
     - 一条版本线下多个 feature 共用同一组交付边界

2. **feature 显式分块 baseline**
   - 作用：声明单个 feature 在当前版本线内实际使用的服务、分支、worktree、写入边界
   - 语义：是版本级 baseline 的受限子集或等价子集
   - 典型用途：
     - 多服务多 git 项目
     - 不同 feature 落在不同服务组合
     - 同版本不同 feature 需要不同 target branch 或 service worktree 映射

当两者同时存在时，必须满足：

- version baseline 至少覆盖所有 feature baseline 的：
  - `direct_delivery_services`
  - `writable_services`
  - `reference_only_services`
  - `branch_strategy`
  - `base_branch`
  - `branch_prefix`
  - `use_git_worktree`
  - `worktree_root`
  - `workspace_root`
- feature baseline 不允许声明超出 version baseline 的服务或写入范围
- feature baseline 可以比 version baseline 更窄，但不能更宽
- version / feature baseline 都只是 canonical envelope 的镜像切片，不能绕过 envelope 单独修改为新的 truth

### 8.5 最低必须覆盖的字段

至少应覆盖：

- 实现服务名
- 服务目录
- 当前开发 git 分支
- base branch
- branch prefix
- 是否使用 worktree
- worktree root
- workspace root
- 可写服务范围
- 只读参考服务范围
- isolation strategy
- service-to-branch 映射（至少在多 git roots 项目中）
- service-to-worktree 映射（至少在 use_git_worktree=true 时）
- transaction / projection 元数据：
  - `baseline_id`
  - `transaction_id`
  - `source_hash`
  - `projection_seq`
  - `committed_at`

这些字段必须和：

- deterministic implementation contract
- git workflow contract
- implementation plan

保持一致；如果存在 feature baseline，还必须与 version baseline 满足“子集/超集”关系。更准确地说，是这些投影必须都能回溯到同一个 canonical envelope。

### 8.6 多服务多 git 项目场景

在典型的多服务多 git 项目里，单一 baseline 不够表达真实交付边界。

典型情况：

- 版本线 `v1.3.7` 涉及：
  - `apps/web-console`
  - `services/mero-api`
  - `services/mero-worker`
  - `packages/contracts`
- 但某个 feature 只改：
  - `services/mero-api`
  - `packages/contracts`
- 另一个 feature 则改：
  - `apps/web-console`
  - `services/mero-api`

此时正确语义应是：

- canonical version baseline 记录整条版本线允许的服务全集与默认分支/worktree 策略
- canonical feature overlay 记录当前 feature 实际命中的服务子集、目标分支和 worktree
- `architecture-blueprint.md` 只镜像 version baseline 和 feature overlay 的人类可读切片

所以 `architecture-blueprint.md` 应允许：

- 一个版本级 baseline
- 多个 feature baseline block

而不是二选一。

---

## 9. Strict Gate Rules Needed

`v1.3.7` 如果要支持 direct bootstrap，必须同步增强 gate。

### 9.1 Implement plan gate

`implement plan` 不再只检查：

- frozen revision
- technical review contract
- source refs

还应检查：

- canonical envelope 是否存在且结构完整
- architecture blueprint 是否存在对应 projection 块
- deterministic contract / git workflow / implementation plan 是否都声明同一 `baseline_id`
- 各 projection 的 `source_hash` / `projection_seq` / `transaction_id` 是否与 canonical envelope 一致
- projection 中的 service/branch/worktree 信息是否与 canonical envelope 一致
- 若存在 feature baseline，还要检查 feature baseline 是否被 version baseline 完整覆盖
- 若存在多服务多 git roots，还要检查 service-to-branch / service-to-worktree 映射是否完整

### 9.2 Release gate

`release` 不需要改变主语义，但要新增一致性检查：

- 若 canonical envelope 缺失，阻断
- 若 architecture blueprint projection 缺失，阻断
- 若任一 projection 与 canonical envelope 分叉，阻断
- 若 implementation plan 使用的服务范围与 canonical envelope 不一致，阻断
- 若任一 feature baseline 超出 version baseline，阻断
- 若版本级 baseline 未覆盖本次发布相关 feature 的全部 baseline，阻断

### 9.3 可接受的阻断条件

以下情况必须阻断：

- 与已冻结 requirement truth 冲突
- direct bootstrap 生成的 requirement 与已有 docs 不一致
- technical delivery canonical envelope 字段缺失
- git/worktree 配置不合法
- canonical envelope 与任一 projection 不一致
- feature baseline 超出 version baseline
- 多 git 项目下 service branch/worktree 映射不完整

---

## 10. Required Stop Conditions

为了满足“除非与冻结需求冲突才终止，否则核实完毕自动实现补齐”，需要把 stop condition 写得非常明确。

建议只在以下四类问题上阻断：

1. **Truth conflict**
   - 已有 frozen requirement 与自动推导内容冲突

2. **Boundary ambiguity**
   - 自动推导后仍无法确定 feature 边界、服务边界、交付边界或 canonical baseline 范围

3. **Execution safety**
   - 分支、worktree、dirty workspace、不安全写入范围

4. **Contract drift**
   - canonical envelope 与任一 projection 不一致，或 projection 之间引用不同 baseline

其他情况默认不应阻断，而应：

- 自动补齐
- 自动写回
- 自动继续实现

---

## 11. Recommended Write Order

为了避免多写入点漂移，推荐写入顺序：

```text
prepare intent
-> synthesize minimal requirement package
-> requirement clarity validate
-> freeze revision
-> synthesize canonical implementation delivery baseline envelope
-> validate canonical envelope
-> commit canonical envelope
-> project architecture blueprint version baseline mirror
-> project architecture blueprint feature baseline mirror
-> materialize deterministic implementation contract
-> materialize git workflow contract
-> compile implementation plan
-> verify all projections against canonical envelope
-> run implement
```

关键原则：

- 必须先有 canonical envelope，再允许任何 projection 落盘
- `architecture-blueprint.md` 不能事后补写到一个新的 truth，只能重投影
- 所有 projection 必须在同一事务内提交，失败则整体回滚或阻断
- plan pass 之前必须完成 canonical vs projection cross-check

---

## 12. Open Design Questions

### 12.1 `implement run` 是否默认进入 direct bootstrap

两个可选口径：

- 保守：
  - `implement run` 维持现状
  - `implement run --direct` 才启用

- 极简：
  - `implement run` 默认 direct bootstrap
  - `implement run --strict-preflight` 才要求完整 formal package

从 Beacon 当前的产品方向看，推荐后者，但需要一次明确升级说明。

### 12.2 technical review contract 的审批语义

当前 technical review contract 需要 `review_status=approved|accepted`。

若 direct bootstrap 要自动继续实现，需要明确：

- 是否允许 `approved_by=system:implement-bootstrap`
- 还是新增 `system-approved` 并更新 validator

推荐：

- 仍保留 `approved`
- 但允许 `approved_by=system:implement-bootstrap`
- 同时记录 `review_source=auto-bootstrap`

这样不需要扩张状态机。

### 12.3 canonical envelope 与双层 baseline 的冻结策略

这次不再把它当 open question，而是建议直接冻结为：

- canonical envelope 同时承载：
  - 版本级唯一 baseline
  - feature 显式分块 overlay
- `architecture-blueprint.md` 只镜像：
  - 版本级唯一 baseline
  - feature 显式分块 baseline
- version baseline 是所有 feature baseline 的统一超集
- feature baseline 是当前 feature 实际交付边界的精确子集
- gate 必须同时检查：
  - feature baseline 是否落在 version baseline 内
  - 所有 projection 是否与当前 feature baseline 对应的 canonical overlay 一致

仍待细化的问题只剩：

- version baseline 对 `target_branch` 是否允许留空并交给 feature baseline 指定
- 多 feature 共用同一服务但 target branch 不同的情况下，version baseline 应存默认值还是仅存允许集

---

## 13. Recommendation

`v1.3.7` 应采用以下正式方向：

1. 保持 `implement` 作为唯一公开实现入口。
2. 不允许脱离 `prd / user-story / test-case` 直接实现。
3. 允许 `implement` 在内部自动补齐 requirement package，而不是要求用户手工补齐。
4. 在 `implement plan` 阶段先生成 canonical 的 implementation delivery baseline envelope。
5. 把 `execution/architecture-blueprint.md`、deterministic implementation contract、git workflow contract、implementation plan 全部降为 canonical envelope 的单向投影。
6. `architecture-blueprint.md` 保持为 human-readable delivery baseline mirror，并支持版本级 baseline 与 feature baseline 并存。
7. 要求 version baseline 覆盖所有 feature baseline，feature baseline 不得超出 version baseline。
8. gate 校验的是各 projection 与 canonical envelope 的一致性，而不是允许多个文档互相对表。
9. 除非出现 truth conflict、boundary ambiguity、execution safety、contract drift，否则默认自动继续实现。

最终产品语义应是：

> Beacon 不是放弃 requirement truth，而是把 requirement truth 的补齐、核实和实现前准备，全部折叠进 `implement` 内部，并以 canonical envelope 统一投影到各类交付物，让人类看到的仍然只是一个最小入口。

---

## 14. Next Step

如果这份研究结论被接受，下一步应进入：

1. `v1.3.7` execution blueprint 草案
2. `implement direct bootstrap` 命令合同草案
3. canonical implementation delivery baseline envelope schema
4. `architecture-blueprint.md` projection 模板设计
5. strict consistency gate 设计
6. 再进入 PRD / user-story / test-case 正式化
