# Test Cases: Beacon v1.1.5 LLM / Skill Prompt First-Principles Contract

**Feature**: beacon-llm-skill-prompt-first-principles  
**Version**: v1.1.5

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | contract | Prompt defines first-principles reasoning order | 明确人类/机器/Beacon 三问 |
| TC-002 | contract | Prompt defines reading order | 先 human surface，后 `.machine`，再 `.beacon memory` |
| TC-003 | contract | Prompt forbids default compatibility thinking | 不默认兼容旧结构 |
| TC-004 | contract | Prompt forbids overdesign and fallback-first behavior | 最短路径实现，不给额外兜底方案 |
| TC-005 | contract | Prompt defines clarification gate | 目标不清时先澄清 |
| TC-006 | contract | Prompt defines progressive disclosure | 对人类默认渐进式披露 |
| TC-007 | integration | Prompt aligns memory 4-layer model | memory 读取顺序与层级一致 |
| TC-008 | integration | Prompt aligns doctor role | doctor 作为修复器而非兼容层 |
