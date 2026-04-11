# Think：Beacon v1.3.0 简化版 Codex 原生子代理

**Feature**: `beacon-v1.3.0-simplified-codex-native-subagents`  
**Version**: `v1.3.0`  
**Date**: `2026-04-10`  
**Status**: `planning line`

## 问题框定

Beacon 现在已经具备两类有价值能力：

1. 强阶段工件能力
2. `native-team` 这类有边界的实现期协同能力

但缺失的是一套“跨阶段可复用的子代理模型”，使需求编写、批判、场景扩展、验证等工作可以在不破坏 evidence-first contract 的前提下被拆分。

## 想要的结果

当用户请求复杂阶段产物时，Beacon 能够在两条路径之间显式选择：

- 单阶段单面生成
- 受约束的子代理 lane

但最终仍然只返回一份 canonical Beacon artifact。

## 约束

1. 必须保持 mainline-first
2. 不得演进成通用 super-agent shell
3. 必须保住 version/package truth
4. 所有委托都必须在 artifacts 与 run state 中可见

## 核心判断

Beacon 应该增加的是“简化版阶段子代理模型”，不是“完整 orchestration 平台”。

这意味着：

- 委托默认关闭
- 角色固定
- worker template 按阶段声明
- evidence writeback 显式化

## 候选阶段

1. `think`
   - `researcher`
   - `critic`
2. `user-story`
   - `story-mapper`
   - `ac-reviewer`
3. `prd`
   - `requirement-parser`
   - `risk-critic`
4. `test-case`
   - `scenario-mapper`
   - `coverage-checker`
5. `qa`
   - `verifier`
   - `repair-handoff-writer`
6. `implement run`
   - `executor`
   - `reviewer`
   - `tester`

## 结论

`v1.3.0` 首先应是一条“规划 + 架构 + 约束冻结”线。

只有最小可验证的运行时变更应该先落地，尤其是：

1. version prompt routing
2. version semantics freeze
3. `implement run` 的第一条 Codex-native 多代理闭环
