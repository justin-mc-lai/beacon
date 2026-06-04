# PRD: Beacon v1.1.5 LLM / Skill Prompt 第一性原理合同

## 1. 背景

在 Beacon v1.1.5 中，我们不仅要重构人类面与机器面，还要重构：

> **Beacon 给 LLM 的工作法提示。**

如果不明确这层，LLM 仍然可能：
- 先看机器 JSON 而不是人类主文档；
- 把 JSON 工件当成默认人类阅读面；
- 在目标不清晰时继续脑补；
- 继续提出兼容性方案、兜底方案、补丁式方案；
- 因为“读取过多细节”而输出不必要的复杂设计。

## 2. 目标

定义一套给 LLM / skill / agent / runner 的正式工作法合同，使其在 v1.1.5 规范下：

1. 先按第一性原理理解需求；
2. 先读 human primary surface；
3. 再按需读 `.machine` 与 `.beacon memory`；
4. 对人类输出采用渐进式披露；
5. 不默认做兼容性方案；
6. 目标不清晰时先澄清；
7. 保持 Beacon delivery kernel 定位。

## 3. 提示词核心原则

### 3.1 第一性原理顺序
提示词必须引导 LLM 先判断：
1. 人类当前需要读什么
2. 机器当前需要读什么
3. 这次任务的真实目标是什么
4. 哪些细节是必须读，哪些不是

### 3.2 读取顺序
LLM 默认读取顺序必须是：

```text
1. docs/beacon/<version>/ 的人类主入口
2. docs/beacon/<version>/.machine/
3. .beacon/memory/
```

说明：
- 这不是减少机器可见信息；
- 而是先保证人类目标和主线不被 machine artifacts 淹没。

### 3.3 对人类的输出顺序
默认输出顺序：
1. 结论
2. 最小必要解释
3. 如有需要，再展开 machine 细节

### 3.4 禁止事项
提示词必须明确禁止默认行为：
- 不默认兼容旧结构
- 不默认提出补丁性/兜底性/降级方案
- 不默认过度设计
- 不在目标模糊时继续实现

### 3.5 澄清门
若动机、边界、成功标准不清晰：
- 必须停下来澄清
- 不能假设用户非常清楚自己要什么

## 4. Human / Machine / Runtime 三面提示合同

### 4.1 Human Primary Surface
LLM 应将其视为：
- 面向人类的主语义
- 默认回答依据
- 默认摘要来源

### 4.2 Machine Secondary Surface
LLM 应将其视为：
- 校验输入
- doctor/gate/report/status 的结构化依据
- 只在需要时展开引用

### 4.3 Runtime Internal Surface
LLM 应将其视为：
- 运行态
- 原始证据
- 非正式交付面

## 5. Memory 读取合同

提示词中要明确 memory 的 4 层：
- store
- lifecycle
- feedback assimilation
- consumption / projection

规则：
- 默认面向人类时优先引用 projection
- raw memory store 只在需要 debug / doctor / gate 分析时展开

## 6. Doctor 角色合同

提示词中要明确：
- `doctor` 不是长期兼容层
- `doctor` 是把旧包修到新规范的修复器
- 在 v1.1.5 场景下，不应以“继续兼容旧路径”为默认思路

## 7. 成功标准

- LLM 不再优先把 JSON 当主阅读面
- LLM 不再默认输出兼容/补丁方案
- LLM 对人类采用渐进式披露
- LLM 在需要时仍能读取 `.machine` 与 `.beacon memory` 完整信息
- LLM 在目标模糊时会先澄清
