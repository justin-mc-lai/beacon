# UX PRD

## Goal

将 `llm decision surface` 这条 feature 中对人类可见的 route、state、reasoning、guardrail handoff 结构冻结下来，避免实现阶段重新发明交互面。

## Primary User Questions

1. 当前 freeform intent 应进入哪条 Beacon surface？
2. 当前 recommendation 是基于哪些 learning hint 与 reasoning inputs？
3. 为什么当前必须回到 `change`，或者为什么仍不能切走 legacy Python 判定？
4. 什么时候才能进入 `implement`？

## Frozen UX Principles

- 先解释 route 与理由，再展开底层 contract
- learning、diagram、semantic 都必须以“影响判断的输入”身份出现，而不是背景资料
- dual-read mismatch 与 guardrail blocked 必须被首屏高亮
- 不把 machine transaction 细节暴露成主界面内容

## Required Surfaces

- Intent Router
- Decision Surface Overview
- Skill Surface Detail
- Learning Disclosure Center
- Reasoning Contract Review
- Guardrail Cutover Audit

## Handoff Contract

- 实现阶段必须保留这六个 surface 的职责切分
- 允许调整代码结构
- 不允许把 route / state / cutover 审计重新混成单一长文档或纯日志界面
