# PRD：Beacon v1.3.5 冻结后需求调整闭环与 Requirement Re-freeze Surface

**Feature**: `beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface`  
**Version**: `v1.3.5`  
**Date**: `2026-04-20`  
**Status**: `frozen-pending-implementation`  
**Track**: `parallel`  
**Scenario**: `requirement_change_loop + tooling_surface`  
**Template**: `并行 PRD / change-loop`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/v1.3.5/SUMMARY.md`
- Main PRD: `docs/beacon/v1.3.5/prd/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md`
- Parallel repair PRD: `docs/beacon/v1.3.5/prd/beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler.md`
- New lifecycle draft: `docs/beacon/v1.3.5/execution/lifecycle-state-machine.md`
- New host-visible skill draft: `skills/beacon/beacon-change/SKILL.md`

## 1. 问题

Beacon 当前已经接近形成完整的 requirement-driven delivery kernel，但公开人机工作流仍主要覆盖 happy path：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release
```

这条链足以支撑新功能立项到初次交付，但在“需求冻结后又发生调整”的真实场景里，公开 surface 仍有明显缺口。

### 1.1 当前缺口

1. 冻结后新增需求、边界补充、范围删减，还没有稳定的人机入口。
2. 仓库内部虽然已有 `reopen` / `freeze` 能力，但用户仍需要理解隐藏命令和内部状态。
3. 变更后的 requirement truth 重编译路径不清晰：
   - `prd` 怎么 revise
   - `user-story` 怎么 refresh
   - `test-case` 怎么做 delta coverage
   - `prototype` 怎么 refresh / re-freeze
4. `implement` 和 `qa` 对“这是 revised baseline 还是首次 baseline”缺少统一语义。
5. `release` 可以做 gate 审计，但没有把“这是 revised delivery / hotfix delivery”作为正式闭环对象。

### 1.2 为什么不能继续让用户手工兜底

如果 Beacon 继续默认用户自己理解：

- 什么时候 `reopen`
- 什么时候补 PRD
- 什么时候重新冻结
- 什么时候做 delta QA

就会持续出现三类漂移：

1. Requirement drift
2. Lifecycle drift
3. Surface drift

### 1.3 本并行线要关闭的核心缺口

`v1.3.5` 需要正式补齐：

1. 一个宿主可见但克制的 `beacon-change` 子 skill 草案。
2. 一份 Beacon 生命周期状态机文档草案。
3. 一套冻结后变更的 requirement re-freeze 规则。
4. 一条不新增 Beacon 一级主命令的 change loop 主链映射。

规则：

> Beacon 可以新增一个宿主路由子 skill，但不能把 change loop 扩张成新的公开一级主流程。

## 2. 目标

### 2.1 主要目标

把 Beacon 从“只擅长首轮 requirement freeze”升级为“能够处理冻结后需求调整再闭环”的系统。

这条线必须明确做到：

1. 允许用户用自然语言稳定进入冻结后变更闭环。
2. 不新增 Beacon 一级主命令。
3. 变更后仍回到同一条 requirement truth 主链。
4. 用 revision/re-freeze 语义明确“旧冻结基线”和“新冻结基线”的关系。

### 2.2 非目标

- 不把 `beacon-change` 变成新的 Beacon 一级命令。
- 不引入新的公开 stage。
- 不在 `v1.3.5` 完成全部实现代码产品化。

### 2.3 输出目标

本线的正式输出必须至少包括：

1. 冻结后需求调整闭环的正式 PRD / user-story / test-case。
2. `skills/beacon/beacon-change/SKILL.md` 草案。
3. `docs/beacon/v1.3.5/execution/lifecycle-state-machine.md` 草案。
4. 对 `help/status` 路由规则的明确要求。

## 3. 设计原则

### 3.1 主链不扩张，子路由补齐

Beacon 的人类主链继续保持：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release
```

冻结后变更通过一个宿主可见子 skill 进入，不增加新的公开一级主阶段。

### 3.2 Change loop 不是平行主流程

`beacon-change` 的职责是路由和收口，而不是替代 `prd`、`implement`、`qa`。

它只负责把用户带回正确的 requirement truth 链路：

```text
reopen
→ delta compile
→ re-freeze
→ implement fix
→ qa delta-run
→ release recheck
```

### 3.3 Reopen 与 freeze 必须是正式 revision 语义

任何冻结后需求调整都必须形成新的 revision lineage，不能静默覆盖旧冻结物。

### 3.4 Delta compile 必须是正式 requirement 行为

变更请求不是只改一段 PRD 文案，而是要求：

- `prd revise`
- `user-story refresh`
- `test-case refresh`
- `prototype refresh`

形成新的完整 requirement truth。

### 3.5 Release closure 必须识别 revised baseline

`release` 必须能够区分：

- initial delivery
- revised delivery
- hotfix delivery

## 4. 范围

### In scope

- `beacon-change` 子 skill 草案
- 冻结后需求调整的宿主路由规则
- 生命周期状态机文档草案
- `reopen -> revise -> refresh -> re-freeze` 的 requirement 规则
- `implement fix / hotfix` 的主链映射
- `qa delta-run / regression-run` 的主链映射
- `release recheck` 的闭环要求

### Out of scope

- 新的 Beacon 一级主命令
- 与 change loop 无关的大规模 UI 重构
- 把 release 文案系统全部重写

## 5. 功能需求

### FR-001 增加一个宿主可见子 skill `beacon-change`

系统必须提供一个新的宿主可见 skill：

- 名称：`beacon-change`
- 角色：冻结后需求调整闭环路由器
- 边界：不是新的一级主命令，不替代主链阶段

### FR-002 `beacon-change` 必须稳定接收冻结后调整意图

当用户表达以下意图时，系统应稳定路由到 `beacon-change`：

- 改需求
- 补边界
- 重新冻结
- reopen 后再改
- hotfix 但先补需求
- 版本要调整范围

### FR-003 `beacon-change` 必须把变更请求编译为 change brief

每次变更至少输出：

- why changed
- added
- removed/reduced
- fixed
- impacted requirement surfaces
- recommended next steps

### FR-004 冻结后调整必须触发 revision reopen

当目标 feature 已冻结时，change loop 必须：

1. 检测当前 revision 状态
2. 调用 `reopen`
3. 生成新 revision
4. 保留旧 revision 作为历史冻结基线

### FR-005 变更后必须重编译 requirement truth

系统必须支持把变更请求增量编译回：

- `prd revise`
- `user-story refresh`
- `test-case refresh`
- `prototype refresh`

### FR-006 系统必须支持 requirement re-freeze

完成 delta compile 后，系统必须能够：

- 运行 clarity gate
- 产出新的 frozen baseline
- 为后续 `implement` / `qa` / `release` 提供 revision-aware truth

### FR-007 生命周期状态机必须成为正式文档资产

Beacon 必须新增一份状态机文档，至少覆盖：

- init / context_bootstrap
- requirement drafting
- freeze_ready
- prototype_freeze
- implementation_ready
- qa_ready
- release_ready
- change_requested
- revision_reopened
- delta_recompiled
- re_freeze_ready
- fix_in_progress
- re_release_ready

### FR-008 `implement` 必须识别 revised baseline

`implement` 在 fix/hotfix 模式下必须能够识别：

- 当前 revision
- 是否已 re-freeze
- 是否基于最新 requirement truth

### FR-009 `qa` 必须识别 delta verification

`qa` 必须支持 revised baseline 的正式语义，至少区分：

- `delta-run`
- `regression-run`

### FR-010 `release` 必须识别 recheck 场景

`release` 必须能把 revised baseline 作为正式 gate 对象，不得把旧 baseline 的通过结果沿用到新变更。

### FR-011 `help/status` 必须能路由冻结后调整闭环

当系统检测到：

- feature 已冻结
- 用户表达 change intent

`help/status` 必须推荐：

```text
beacon-change
→ reopen
→ prd revise
→ user-story refresh
→ test-case refresh
→ prototype refresh
→ freeze
→ implement fix
→ qa delta-run
→ release recheck
```

## 6. 非功能需求

### NFR-001 心智克制

用户不需要记忆超过 `7+3 + 1 skill` 的公开表面。

### NFR-002 可审计

变更后的 revision lineage、delta compile、re-freeze receipt 都必须可审计。

### NFR-003 不破坏原主链

新引入的 change loop 不得破坏已有主链。

### NFR-004 宿主稳定路由

Codex / Claude 在识别“冻结后需求调整”类自然语言时，必须稳定命中 `beacon-change`。

## 7. 验收标准

### AC-001 公开表面克制

Beacon 继续不新增新的一级主命令，但新增一个宿主可见 `beacon-change` 子 skill 草案，并明确其不是新主阶段。

### AC-002 需求调整再闭环成立

冻结后的 feature 能走通：

```text
change intake
→ reopen
→ prd revise
→ user-story refresh
→ test-case refresh
→ prototype refresh
→ re-freeze
→ implement fix
→ qa delta-run
→ release recheck
```

### AC-003 生命周期状态机可读可审计

系统能提供一份文档化状态机，明确各状态、迁移条件、阻断条件和产物边界。

### AC-004 revision-aware truth 不漂移

变更后的实现、QA 和 release 都绑定最新 frozen revision，不允许继续沿用旧 baseline。

### AC-005 `help/status` 路由稳定

当用户提出冻结后变更意图时，系统推荐的下一步稳定收敛到 `beacon-change` 或 change loop。

### AC-006 交付类型语义清晰

`release` 能区分 initial delivery、revised delivery、hotfix delivery 的语义与 gate 对象。

## 8. 冻结交付物

本并行 PRD 冻结时，必须同时存在：

1. `docs/beacon/v1.3.5/prd/beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface.md`
2. `docs/beacon/v1.3.5/user-story/beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface.md`
3. `docs/beacon/v1.3.5/qa/test-cases/beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface.md`
4. `docs/beacon/v1.3.5/execution/lifecycle-state-machine.md`
5. `skills/beacon/beacon-change/SKILL.md`
