# PRD：Beacon v1.3.2 Karpathy 边界默认规范

**Feature**: `beacon-v1.3.2-karpathy-boundary-defaults`  
**Version**: `v1.3.2`  
**Date**: `2026-04-15`  
**Status**: `planning line`

## 1. 问题

Beacon 已经有 `docs/beacon/global-boundaries.md`，用于约束人类主面、机器内部复杂度、宿主上下文和输出边界。

但当前全局规范主要回答的是：

- 命令面应该多窄
- team/subagent/precheck 应该藏在哪里
- Beacon 不应变成多运行时桥接调度器

它还没有充分覆盖 LLM 原生 coding agent 常见的四类行为风险：

1. 静默假设并直接执行
2. 过度抽象、过度配置、过度工程
3. 顺手修改无关代码、注释、格式或死代码
4. 只按指令动作，不把任务转成可验证目标闭环

`forrestchang/andrej-karpathy-skills` 仓库把这些风险收敛成四条轻量规则：

- Think Before Coding
- Simplicity First
- Surgical Changes
- Goal-Driven Execution

这些规则与 Beacon 的轻量化方向一致，适合作为 Beacon 默认全局规范的补充来源，但不能被照搬成又一个外部 skill 依赖。

## 2. 目标

把 `andrej-karpathy-skills` 的边界原则转译为 Beacon 自有的默认全局规范：

1. 纳入 `global-boundaries` 的原则层，而不是新增公开命令。
2. 约束 Beacon 源码迭代、目标项目执行、host skill 行为。
3. 与下一迭代的核心瘦身目标一致，避免外部重型 skill 依赖。
4. 保持规则可验证、可审计、可映射到 PRD / user-story / test-case / implement / qa。

## 3. 来源边界

本 PRD 使用 `forrestchang/andrej-karpathy-skills` 作为参考来源。

仓库核心内容：

- `README.md`
- `CLAUDE.md`
- `skills/karpathy-guidelines/SKILL.md`

提炼原则：

| 来源原则 | Beacon 转译 |
|----------|-------------|
| Think Before Coding | 需求/实现前必须显式假设、歧义、取舍 |
| Simplicity First | 最小正确改动，不做 speculative abstraction |
| Surgical Changes | 只改请求相关范围，不做 drive-by refactor |
| Goal-Driven Execution | 每个执行阶段必须绑定成功标准与验证闭环 |

## 4. 功能需求

### FR-001 全局规范必须要求显式假设

Beacon 在进入实现、QA 或自动修复前，必须能显式记录关键假设。

要求：

- 不允许 silently pick one interpretation
- 多种解释并存时必须记录取舍
- 需求不清时优先阻断或回到 `prd/user-story`
- 简单任务可快速处理，但不得隐藏关键不确定性

### FR-002 全局规范必须要求简单优先

Beacon 默认实现策略必须是最小正确变化。

禁止默认行为：

- 为单次需求新增抽象层
- 为未请求的未来扩展增加配置
- 为不可能路径增加复杂错误处理
- 为了“看起来完整”扩大 scope

允许行为：

- 现有结构已需要抽象时复用抽象
- 需求明确要求扩展性时记录理由
- 复杂性来自业务必要性时写入 evidence

### FR-003 全局规范必须要求外科手术式改动

Beacon 对源码和文档的改动必须可追溯到当前请求或冻结材料。

要求：

- 不主动重构无关代码
- 不主动格式化无关文件
- 不删除预先存在的死代码，除非需求明确要求
- 自己新增后产生的 orphan imports / vars / files 必须清理
- 每个 changed file 应能解释为什么属于当前 scope

### FR-004 全局规范必须要求目标驱动执行

Beacon 不应只执行用户给出的动作，而应把非平凡任务转成可验证目标。

要求：

- bug fix 应有复现或验证证据
- feature 应有 acceptance criteria 或 test case 映射
- refactor 应说明 before/after 验证
- 多步骤任务应有每步 verify 信号

### FR-005 规则必须进入 Beacon 自有规范，不形成外部 skill 依赖

`andrej-karpathy-skills` 只能作为参考来源。

Beacon 不应要求：

- 安装该仓库
- 安装其 Claude plugin
- 调用其 `karpathy-guidelines` skill
- 把该外部 skill 加入默认 host-visible skill pack

正确做法是：

- 提炼原则
- 写入 Beacon `global-boundaries`
- 通过 Beacon 自有 tests / docs / doctor 验证

### FR-006 默认全局规范必须同时约束 Beacon 自身与目标项目

规则适用于两层：

1. Beacon 源码迭代自身
2. Beacon 接入的目标项目

目标项目同步 context 时，应能继承这些边界：

- AGENTS.md
- CLAUDE.md
- docs/beacon/global-boundaries.md

### FR-007 规则必须与 6+3 主面兼容

不得新增公开主命令。

规则应嵌入现有阶段：

- `prd`: 澄清假设与边界
- `user-story`: 明确验收范围
- `test-case`: 转成可验证目标
- `implement`: 最小外科手术式改动
- `qa`: 验证目标与新增发现
- `release`: 检查未越界改动
- `help/status/doctor`: 只在阻断或诊断时展示细节

### FR-008 规则必须支持轻重任务区分

Karpathy 风格规则偏谨慎。

Beacon 必须避免把所有 trivial task 都变成重流程。

要求：

- 简单拼写、单行文案、明显 typo 可快速处理
- 非平凡实现、重构、bug fix、数据变更必须启用完整边界
- 是否进入完整边界应可由风险、scope、文件影响面判断

## 5. 边界清单

### 应进入 `global-boundaries`

1. 显式假设与歧义管理。
2. 简单优先与反过度工程。
3. 外科手术式改动范围。
4. 目标驱动验证闭环。
5. trivial task 的轻量例外。

### 不应进入 `global-boundaries`

1. 对 `andrej-karpathy-skills` 的安装步骤。
2. 对 Claude plugin 的依赖。
3. 任何新增 Beacon 公开命令。
4. 任何外部 skill 调用要求。

## 6. 验收标准

1. 新 PRD 明确引用并转译 `andrej-karpathy-skills` 的四条原则。
2. 后续实现必须把规则写入 Beacon 默认全局规范。
3. 后续实现不得新增外部 skill 依赖。
4. 后续实现必须保持 `6+3` 人类主面。
5. 后续验证必须覆盖：
   - 文档存在
   - context sync 继承
   - help/doctor 不默认扩张主面
   - implementation/qa 能记录 assumption / scope / verification evidence

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 规则过重导致小任务变慢 | 中 | 明确 trivial task 轻量例外 |
| 外部仓库变成新依赖 | 高 | 只提炼原则，不安装不调用 |
| 规则只写文档不被执行 | 高 | 后续补 tests / doctor / context sync 验证 |
| 与现有 Beacon 全局约束重复 | 低 | 作为行为边界补充，不替代 6+3 / host-native 约束 |

---

**Created**: 2026-04-15  
**Version**: v1.3.2  
**Status**: Draft  
**Reference**: `https://github.com/forrestchang/andrej-karpathy-skills`
