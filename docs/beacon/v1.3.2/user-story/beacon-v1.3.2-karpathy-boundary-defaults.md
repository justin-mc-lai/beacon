# 用户故事：Beacon v1.3.2 Karpathy 边界默认规范

**Feature**: `beacon-v1.3.2-karpathy-boundary-defaults`  
**Version**: `v1.3.2`  
**Date**: `2026-04-15`  
**Status**: `planning line`

## US-001：作为 Beacon 维护者，我希望默认全局规范要求显式假设与歧义管理

**验收标准**：

- 关键需求不清时不得静默选择一种解释直接执行
- 多种解释并存时必须显式记录假设、取舍或阻断原因
- 关键需求不明时必须回到 `prd / user-story` 收口

## US-002：作为实现负责人，我希望默认行为边界要求简单优先，而不是默认过度工程

**验收标准**：

- 默认采用最小正确改动
- 不为单次需求新增 speculative abstraction
- 不为未请求的未来扩展增加配置或复杂度

## US-003：作为代码维护者，我希望默认行为边界要求外科手术式改动

**验收标准**：

- 只改与当前请求、冻结材料或当前闭环直接相关的范围
- 不做 drive-by refactor
- 不删除无关代码、注释或格式
- 只清理自己这次改动制造的 orphan

## US-004：作为交付负责人，我希望默认行为边界要求目标驱动验证闭环

**验收标准**：

- bug fix 必须有复现或验证证据
- feature 必须有 acceptance 或 test 映射
- refactor 必须有 before/after 验证
- 非平凡多步骤任务必须有 verify 信号

## US-005：作为 Beacon 平台维护者，我希望这些规则只是借鉴自外部规范仓库，而不是形成默认依赖

**验收标准**：

- 不要求默认安装 `andrej-karpathy-skills`
- 不要求默认安装其 plugin
- 不要求运行时调用其外部 skill
- 规则必须被吸收到 Beacon 自己的 `global-boundaries`

## US-006：作为平台维护者，我希望这些默认行为边界同时约束 Beacon 自身和目标项目

**验收标准**：

- Beacon 源码开发自身必须遵守这份边界
- 接入 Beacon 的目标项目也必须继承这份边界
- 目标项目的 managed context 必须能引用或继承它

## US-007：作为 Beacon 人类使用者，我希望这些规则与 `6+3` 主面兼容，而不是新增命令负担

**验收标准**：

- 不得新增新的 Beacon 公开主命令
- 规则必须嵌入 `prd / user-story / test-case / implement / qa / release`
- `help / status / doctor` 只在阻断或诊断时展示细节

## US-008：作为使用者，我希望 trivial task 可以轻量处理，但不能越界

**验收标准**：

- 明显 typo、单行文案、低风险小修正可轻量处理
- 即使是 trivial task，也不得触碰无关文件
- 不得借 trivial task 之名扩大改动范围

## Acceptance Criteria Matrix

| ID | Theme | Acceptance Criteria |
|----|-------|---------------------|
| AC-001 | explicit-assumptions | 默认全局规范必须要求显式假设、歧义管理和需求不清时回到 `prd / user-story`。 |
| AC-002 | simplicity-first | 默认全局规范必须要求简单优先，禁止 speculative abstraction 和未请求的未来扩展。 |
| AC-003 | surgical-changes | 默认全局规范必须要求外科手术式改动范围和 orphan-only cleanup。 |
| AC-004 | goal-driven-verification | 默认全局规范必须要求目标驱动验证闭环。 |
| AC-005 | no-external-dependency | 这些规则只能借鉴外部仓库，不得形成默认安装、plugin 或运行时 skill 依赖。 |
| AC-006 | source-and-target-inheritance | 这些规则必须同时约束 Beacon 自身与目标项目，并可被 managed context 继承。 |
| AC-007 | compatible-with-6-plus-3 | 这些规则必须与 `6+3` 主面兼容，不得新增公开主命令。 |
| AC-008 | trivial-task-exception | 必须允许 trivial task 轻量处理，但不能越界。 |
