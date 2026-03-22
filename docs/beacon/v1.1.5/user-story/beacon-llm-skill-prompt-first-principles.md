# User Story: Beacon v1.1.5 LLM / Skill Prompt First-Principles Contract

**Feature**: beacon-llm-skill-prompt-first-principles  
**Version**: v1.1.5

**As a** Beacon skill / agent / runner consumer  
**I want** Beacon 给 LLM 的提示词遵守第一性原理的人机协作规范  
**So that** LLM 既能读到完整需求与机器细节，又不会把机器细节当作人类主阅读路径，且不会在目标不清晰时擅自脑补方案。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | First Principles | LLM 提示词必须先回答“人类需要什么、机器需要什么、Beacon 应负责什么” |
| AC-002 | Human First | 提示词要求 LLM 先读 human primary surface，再按需读取 `.machine` 与 `.beacon/memory` |
| AC-003 | Progressive Disclosure | 对人类输出默认采用渐进式披露，不先倾倒机器细节 |
| AC-004 | Machine Completeness | LLM 仍然可以读取 `.machine` 与 `.beacon memory` 的完整信息 |
| AC-005 | No Compatibility Thinking | 提示词中明确：v1.1.5 不以兼容旧结构为默认目标 |
| AC-006 | No Overdesign | 提示词中明确：保持最短路径实现，不做额外兜底和降级设计 |
| AC-007 | Clarification Gate | 当目标、动机、边界不清晰时，LLM 必须先停下来澄清，而不是假设用户已想清楚 |
| AC-008 | Human vs Machine Surface | 提示词明确区分 human primary surface / machine secondary surface / runtime internal surface |
| AC-009 | Memory Reading Contract | 提示词明确 memory 四层模型及其读取顺序 |
| AC-010 | Doctor Role | 提示词明确 doctor 是破坏性修复器，而不是兼容层 |

## Notes
- 这不是一般性的“写提示词技巧”；
- 而是 Beacon 作为 skill / delivery kernel 应该向 LLM 明确灌输的工作法。
