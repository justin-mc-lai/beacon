# Beacon v1.3.2 Beacon Toolkit Lighthouse 分析工具包蓝图

## 目标

把 `Beacon Toolkit Lighthouse` 定义成一个 **workflow 外的分析工具包面**：

- 不进入 `prd -> user-story -> test-case -> implement -> qa -> release`
- 但可以为这些阶段提供高质量认知输入

## 核心判断

Toolkit Lighthouse 不是：

- 新的 workflow stage
- 新的 truth owner
- 新的 runtime

Toolkit Lighthouse 是：

- 一个快速分析 surface
- 一个单文件图文 artifact generator
- 一个项目理解加速器

## 推荐定位

```text
陌生项目 / 开源库 / package / infra chain / feature slice
→ Toolkit Lighthouse 分析
→ 单文件 Mermaid + 文字解构
→ 用户建立正确心智模型
→ 如有需要，再进入 PRD / implement / QA
```

## 与主工作流的关系

### 默认关系

- 与主工作流解耦
- 不自动 freeze
- 不自动写回 requirement truth

### 可选关系

如果用户明确要求，Toolkit Lighthouse 输出可以成为：

- `beacon-prd` 的输入
- `beacon-implement` 的输入
- `beacon-qa` 的输入

## 分析模式

### 1. `repo-ramp`

用于快速理解整个项目：

- 系统分层
- 关键入口
- 关键模块
- 依赖关系

### 2. `system-architecture-map`

用于输出类似：

- `system-architecture-map.md`

这种整体架构图文工件。

### 3. `package-brief`

用于快速解构：

- 开源库
- 第三方包
- 依赖组件

### 4. `infra-chain-map`

用于快速梳理：

- gateway
- API/BFF
- service
- queue
- storage

### 5. `feature-slice`

用于快速拆解：

- 某个功能入口
- 涉及模块
- 依赖边界
- 上下游链路

## 输出合同

默认输出为单文件：

- `.beacon/analysis/<slug>.md`

文档最少包含：

1. Summary
2. Scope
3. Mermaid Map(s)
4. Key Files / Entry Points
5. Module / Subsystem Breakdown
6. Dependencies / Infra Chain
7. Confirmed Facts
8. Inferred Structure
9. Open Questions
10. Recommended Next Steps

## Mermaid 最低要求

至少一张 Mermaid 图，推荐最多三张：

1. overall system map
2. execution / dependency / infra map
3. optional module map

## 证据合同

每份 Toolkit Lighthouse 输出至少应包含：

- source refs
- key files
- inferred vs confirmed separation

规则：

> Toolkit Lighthouse 可以帮助理解系统，但不能把推断冒充成正式 truth。

## Skill 形态

建议新增：

- `skills/beacon/beacon-toolkit-lighthouse/SKILL.md`

并定义它为：

- optional Beacon toolkit
- not a mainline workflow surface

## Toolkit 命名规则

这类能力必须统一进入 toolkit 命名空间：

- `beacon-toolkit-lighthouse`

后续同类能力统一遵循：

- `beacon-toolkit-*`

而不是：

- `beacon-<tool>`

## Beacon 源码默认交付规则

当分析对象是 Beacon 源码自身时，默认交付物应为：

1. 工作目录内便捷分析：
   - `.beacon/analysis/<slug>.md`
2. versioned 正式交付：
   - `docs/beacon/<version>/execution/beacon-toolkit-lighthouse-<slug>.md`

第二项必须成为 Beacon 源码迭代的默认交付物之一。

## 人类使用方式

推荐提示语义：

- “分析这个项目的系统架构”
- “快速解构这个开源库”
- “输出一个类似 system-architecture-map 的单文件”
- “帮我梳理这个功能切片和链路”

## 为什么值得做

Beacon 当前强在：

- requirement
- execution
- QA
- release governance

但用户在进入这些面之前，常常先需要：

- 一个快速理解系统的入口

Toolkit Lighthouse 正是对这个“进入前认知成本”的补位。
