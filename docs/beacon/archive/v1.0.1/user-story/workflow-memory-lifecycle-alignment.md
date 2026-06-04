# User Story: Workflow Memory Lifecycle 对齐（v1.0.1）

## Story

**As a** 研发负责人/QA，
**I want** workflow memory 指标准确反映真实 workflow 执行链路，
**So that** gate 与发布决策不被 release 事件干扰。

## Acceptance Criteria

| AC ID | 维度 | 标准 |
|------|------|------|
| AC-001 | Functionality | workflow 闭环阶段扩展为 6 阶段（think/user-story/prd/test-case/implementation/verify） |
| AC-002 | Functionality | release 不纳入通用闭环阶段列表，改用专用 memory profile 校验 |
| AC-003 | Data | `compute_memory_metrics` 默认 run_id 选择优先 workflow run |
| AC-004 | Compatibility | 显式传 run_id 时保持原语义，兼容已有调用 |
| AC-005 | Error Handling | release 证据缺失时返回明确 reason code，避免 silent pass |
| AC-006 | Quality | workflow lifecycle fixture 升级到 6 阶段并通过 |
| AC-007 | Quality | gate memory closure fixture 升级到 6 阶段并通过 |
| AC-008 | Governance | release 专用校验测试覆盖通过（成功/失败路径） |

## Notes

- 本故事为 MVS 基础设施校准，不增加业务功能面。
- 本故事目的是“降低判定失真”，不是“增加流程复杂度”。
