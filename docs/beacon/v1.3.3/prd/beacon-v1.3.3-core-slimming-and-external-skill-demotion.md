# PRD：Beacon v1.3.3 核心瘦身与外部 skill 降级

**Feature**: `beacon-v1.3.3-core-slimming-and-external-skill-demotion`  
**Version**: `v1.3.3`  
**Date**: `2026-04-15`  
**Status**: `planning line`

## 1. 问题

Beacon 当前已经不再把 `gstack` 作为默认实现 runner，但源码与产品面仍然保留了一整层偏重的外部 skill / profile / orchestration / bridge 能力：

1. `implement` 的默认路径已经收敛到宿主原生执行面，但 builtin adapter 中仍内置：
   - `omx`
   - `omc`
   - `gstack`
2. `skill / profile / orchestrate` 仍是正式命令面的一部分，而不是明确的 compatibility plane。
3. `qa` 的主路径在存在 project profile 时，仍可能自动触发外部 orchestration，而不是始终优先停留在 Beacon 内部主链。
4. `ralph-bridge` 仍以独立 bridge 命令和状态机存在，保留了明显的外部桥接叙事。
5. README、测试与 discover/registry 机制仍在把外部 skill 兼容层固化成正式产品能力，而不只是历史兼容。

这导致 Beacon 现状更像：

- 一部分已经是轻量宿主原生 workflow kernel
- 另一部分仍是外部 skill / runner / profile orchestration 控制层

而这和 `v1.3.1` 已经明确的全局约束存在偏差：

- 人类主面应收敛为 `prd -> user-story -> test-case -> implement -> qa -> release`
- `team / subagent / precheck / Ralph` 复杂度应留在机器内部
- Beacon 不应演进成多运行时桥接调度器

## 2. 目标

`v1.3.3` 在不破坏已有交付能力的前提下，把 Beacon 收敛成更轻的核心：

### 2.1 核心目标

1. **宿主原生优先**
   - Beacon 核心执行面默认只面向：
     - Codex native
     - Claude native
2. **外部 skill 降级**
   - 外部 skill / runner / orchestration 只能作为 compatibility plane
   - 不再成为正式主叙事
3. **主链不扩张**
   - 人类主链继续保持：
     - `prd`
     - `user-story`
     - `test-case`
     - `implement`
     - `qa`
     - `release`
4. **QA 不再隐式依赖外部编排**
   - `qa` 默认优先 Beacon 内部能力
   - 外部 orchestration 只在显式 profile mode 下启用
5. **文档与测试同步瘦身**
   - README、help、tests、skill docs 一起收敛
   - 不允许代码瘦了，但叙事还在推外部重型 skill

### 2.2 非目标

本线不做：

- 删除所有历史兼容代码
- 删除真实项目需要的 project contract / required evidence 能力
- 把 Beacon 改成只支持单一宿主
- 把 `team`、`qa-team`、`ralph` 这些机器面能力删除
- 在 `v1.3.2` 一次性重写所有旧版本文档

## 3. 用户故事

| As a | I want to | So that |
|------|-----------|---------|
| Beacon 人类操作者 | 只记住 6+3 主面 | 不被 skill/profile/bridge/runtime 淹没 |
| Beacon 维护者 | 把外部 skill 支持降到兼容层 | 减少随着外部 agent 演进产生的维护成本 |
| 真实项目操作者 | 默认先走 Beacon 内部 `implement/qa` 主链 | 不需要先理解 project skill orchestration |
| 高级项目用户 | 在必要时显式启用 compatibility plane | 保留特种项目扩展能力但不污染 core |

## 4. 功能需求

### FR-001 默认 runner 必须保持宿主原生优先

`implement` 的默认执行路径必须继续保持宿主原生优先：

- `single` -> native single
- `team` -> host-native bounded team runtime
- `ralph` -> host-native loop controller

不得再把外部 runner 恢复成默认主路径。

### FR-002 外部 runner 必须从 core 叙事降级为 compatibility

以下能力必须被视为 compatibility plane，而不是 Beacon core：

- `omx`
- `omc`
- `gstack`
- 未来新增的 command-skill / handoff adapters

要求：

- 可以保留兼容
- 不能继续作为 README 主推荐路径
- 不能继续作为默认 discover / runner narrative 的核心样本

### FR-003 `skill/profile/orchestrate` 必须退出默认主叙事

以下命令或能力不再应被描述为 Beacon 默认使用路径：

- `skill`
- `profile`
- `orchestrate`
- project external registry

要求：

- 它们可以保留
- 但必须被标记为 optional / advanced / compatibility
- 不得作为初次使用 Beacon 的推荐主链

### FR-004 `qa` 不得隐式自动触发外部 orchestration

`qa` 当前在存在 project profile 且 gate 未通过时，会自动执行 project orchestration。

`v1.3.3` 目标应改为：

- 默认不自动调用外部 orchestration
- 只有在显式 profile mode 或显式开关时才允许调用
- 如果未显式启用，则 `qa` 应返回清晰阻断与推荐下一步，而不是直接跑外部 command

### FR-005 `ralph-bridge` 必须退出正式产品叙事

`ralph-bridge` 的外部桥接语义必须被收敛。

允许两种方向之一：

1. 保留命令，但明确标记为 deprecated compatibility
2. 用 Beacon 内部 `ralph` 控制面替代，并停止把 bridge 作为正式能力名词

无论采用哪种方式，都不得继续把 `ralph-bridge` 当作未来主线。

### FR-006 文档主面必须只教 6+3

README、help、host-visible skills、usage docs 里的默认教学路径必须只教：

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`
- `help`
- `status`
- `doctor`

外部 skill / project profile / orchestration 只能进入：

- compatibility 文档
- migration 文档
- 特种项目扩展文档

### FR-007 测试合同必须与瘦身方向一致

当前把 `gstack`、`omx`、`omc` 视为核心 runner 集合的测试，必须重新分层：

- core tests：只保证 Beacon core 主链与宿主原生面
- compatibility tests：保证 legacy/external adapters 仍可选工作

不得继续让 core 测试隐含“这些外部 runner 是正式主面组成部分”。

### FR-008 discover / registry 结果必须分层展示

如果继续保留 `skill detect`、`skill registry`、project skill discovery：

- builtin native 能力必须单独一层
- external compatibility 能力必须单独一层
- 文案必须明确：
  - builtin = Beacon core
  - external = optional compatibility

### FR-009 project contract 能力必须与 external skill 解耦

真实项目需要的：

- required evidence
- required cases
- contract drift
- profile-bound verification policy

这些能力不应强绑定“外部 skill orchestration”。

要求：

- project contract 继续存在
- 但 contract evaluation 与 external command execution 分离
- 不应因为保留 contract plane，就必须保留重型 external orchestration 主路径

### FR-010 兼容层必须默认不干扰新用户

对于首次接入 Beacon 的新用户或轻量项目：

- 不应先看到 `skill bind`
- 不应先看到 `profile create`
- 不应先看到 `orchestrate run`
- 不应先被要求理解 external adapter registry

默认体验应是：

`prd -> user-story -> test-case -> implement -> qa -> release`

## 5. 瘦身改造清单

### A. 必须收敛

1. README 主路径里的 `skill/profile/orchestrate` 推荐流程。
2. `qa` 主路径中的隐式 project orchestration 自动执行。
3. `ralph-bridge` 作为正式能力名词的存在感。
4. tests 中把 `gstack/omx/omc` 视为 core runner 的断言。

### B. 应降级为 compatibility

1. `implement_adapters` 中的外部 builtin adapters。
2. `skill registry` 中 external skill 的正式产品化叙事。
3. `project_skills.run_profile_orchestration()` 的默认调用地位。
4. README 中面向普通用户的 project-aware skill 文案。

### C. 可保留

1. host-native readiness / delegation precheck。
2. `team` / `qa-team` 作为隐藏机器面能力。
3. project contract / required evidence / required cases。
4. external adapter dry-run / detect / doctor 能力，但仅放 compatibility plane。

## 6. 非功能约束

1. 不破坏当前 `implement` 三模式主线。
2. 不破坏 `qa` 对冻结材料的正式验收能力。
3. 不破坏真实项目需要的 contract drift / evidence gate。
4. 新增收敛动作必须可审计、可测试、可回退。
5. 不得在 `v1.3.3` 再引入新的公开 bridge/runtime 命令。

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 真实项目仍依赖旧 profile/orchestration 路径 | 中到高 | 保留 compatibility plane 与迁移文档 |
| 收敛过快导致旧测试大面积失效 | 中 | 先拆分 core/compatibility tests，再删旧断言 |
| 文档与代码不同步 | 高 | README/help/tests/skill docs 同步收敛 |
| project contract 和 external skill 耦合未拆干净 | 高 | 先做 contract/execution 解耦，再降级 orchestration |

## 8. 成功标准

1. Beacon core 主叙事只剩 6+3。
2. 默认 `implement/qa` 不再依赖外部 skill orchestration。
3. `qa` 不再隐式自动执行外部 orchestration。
4. `ralph-bridge` 不再作为正式主能力出现。
5. README 与 help 不再把 `skill/profile/orchestrate` 当普通用户主路径。
6. 测试被明确分成 core 与 compatibility 两层。

---

**Created**: 2026-04-15  
**Version**: v1.3.2  
**Status**: Draft  
**Memory Context**: N/A
