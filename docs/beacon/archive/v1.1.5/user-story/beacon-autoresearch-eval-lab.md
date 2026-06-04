# User Story: Beacon autoresearch-inspired benchmark / keep-discard / drift-auditor loop

**Feature**: beacon-autoresearch-eval-lab  
**Version**: v1.1.5

**As a** Beacon 维护者  
**I want** 为 Beacon 建立一套固定 benchmark 面、keep/discard 规则与漂移审计最小闭环  
**So that** Beacon 可以像 autoresearch 一样迭代自己的规则层与提示词层，同时保证稳定性、置信度与需求到实现不漂移。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Fixed Eval Surface | Beacon 必须先定义固定 benchmark 面，不能先做任意自我修改 |
| AC-002 | Small Editable Surface | Beacon 自动研究阶段只允许优化规则层 / 提示词层 / 漂移审计规则层 |
| AC-003 | Keep or Discard | 每次改动必须有 keep/discard 判定，而不是累积式污染主规则 |
| AC-004 | Hard Gates | verify-materials / verify-delivery / status/report/gate 不通过时必须 discard |
| AC-005 | Drift Audit | 需要最小 requirement -> db -> api -> ui 的漂移审计链 |
| AC-006 | Confidence Audit | 需要置信度校准指标，防止高置信度假通过 |
| AC-007 | Evidence Ledger | 每次实验/规则迭代都要落盘可审计账本 |
| AC-008 | Doctor Interaction | doctor 只能修复到规范，不替代研究账本和 keep/discard 判定 |
| AC-009 | No Full Self-Modification | 不允许 Beacon 一开始就把整仓源码纳入自动研究面 |
| AC-010 | Delivery Kernel Position | 整体仍然围绕 Beacon 作为 delivery kernel，而不是 runtime agent lab |

## Notes
- 学 autoresearch 的不是“训模型”，而是“固定评估面 + 小改动面 + keep/discard + 研究账本”；
- 目标是稳定性、置信度、反漂移与可审计，不是追求炫技式自治。
