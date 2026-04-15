# 测试用例：Beacon v1.3.2 Karpathy 边界默认规范

**Feature**: `beacon-v1.3.2-karpathy-boundary-defaults`  
**Version**: `v1.3.2`  
**Date**: `2026-04-15`  
**Status**: `planning line`

## 测试目标

这组测试用例验证：

1. 外部规范仓库的四条原则是否已被吸收到 Beacon 默认全局边界
2. 这些规则是否同时约束 Beacon 自身与目标项目
3. 这些规则是否仍然兼容 `6+3` 极简主面
4. trivial task 是否存在轻量例外但仍不越界

## 测试用例

## TC-001：默认全局规范必须要求显式假设与歧义管理

- Given：存在需求歧义或多种解释
- When：进入实现、QA 或自动修复前
- Then：系统必须能记录假设、取舍或阻断原因
- Covers：`AC-001`

## TC-002：默认全局规范必须要求简单优先

- Given：实现需求存在多种设计方案
- When：选择默认实现方式
- Then：必须优先采用最小正确改动
- And：不得默认引入 speculative abstraction
- Covers：`AC-002`

## TC-003：默认全局规范必须要求外科手术式改动

- Given：修改现有源码或文档
- When：检查 changed files 和改动范围
- Then：每个 changed file 都必须能追溯到当前请求
- And：只允许 orphan-only cleanup
- Covers：`AC-003`

## TC-004：默认全局规范必须要求目标驱动验证闭环

- Given：执行 bug fix、feature 或 refactor
- When：检查任务输出
- Then：必须存在 success criteria、acceptance 映射或验证证据
- Covers：`AC-004`

## TC-005：这些规则不得形成默认外部依赖

- Given：Beacon 默认安装与运行路径
- When：检查 docs、context、runtime 要求
- Then：不得要求安装 `andrej-karpathy-skills` 仓库、plugin 或外部 skill
- Covers：`AC-005`

## TC-006：这些规则必须同时作用于 Beacon 自身与目标项目

- Given：Beacon 源码仓和接入 Beacon 的目标项目
- When：检查 managed context 与全局边界继承
- Then：两侧都必须能消费这些规则
- Covers：`AC-006`

## TC-007：这些规则不得扩张 `6+3` 主面

- Given：用户查看主流程与公开命令
- When：检查默认主面
- Then：不得因为新增规则而引入新的公开主命令
- Covers：`AC-007`

## TC-008：trivial task 必须允许轻量处理但不能越界

- Given：明显 typo 或单行低风险修正
- When：执行轻量处理
- Then：可以少流程
- And：仍不得触碰无关文件或扩大 scope
- Covers：`AC-008`

## 建议执行节奏

### Round 1

- 验证 `global-boundaries` 是否已写入四条原则
- 验证这些原则没有引入外部依赖

### Round 2

- 验证 Beacon 自身与目标项目上下文继承
- 验证主流程仍保持 `6+3`

### Round 3

- 验证 trivial task 轻量例外
- 验证 implementation / qa 对 assumption / scope / verification evidence 的记录能力
