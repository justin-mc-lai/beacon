# User Story: UI 假通过防护增强（v1.0.1）

## Story

**As a** QA/研发负责人，
**I want** Beacon 的 Verify 阶段只在真实证据成立时通过，
**So that** 我可以基于可靠信号做发布决策。

## Acceptance Criteria（七维抽取）

| AC ID | 维度 | 验收标准 |
|------|------|----------|
| AC-001 | Functionality | 当 `scope=ui` 且未提供真实 `ui-command` 时，状态必须为 `blocked/failed`，不得 `passed` |
| AC-002 | Functionality | 开启 `--require-ui-actions` 时，`login/register/browse/submit-form` 任一缺失必须失败 |
| AC-003 | Data | `ui_action_evidence` 中每个路径必须存在，且可读取 JSON |
| AC-004 | UX | `auto-test status --json` 应明确输出缺失动作与原因码 |
| AC-005 | Security | gate strict/debug 模式下，缺失执行证据必须触发 `test_execution_missing` 或链路错误码 |
| AC-006 | Compatibility | 兼容 `beacon auto-test` 与 `beacon-workflow start --auto` 的 verify 阶段行为 |
| AC-007 | Error Handling | 断言缺失/参数非法时输出稳定 reason_code，不允许 silent pass |

## Notes

- 本故事对应预研文档：`research/ui-test-false-pass-and-coverage-research.md`
