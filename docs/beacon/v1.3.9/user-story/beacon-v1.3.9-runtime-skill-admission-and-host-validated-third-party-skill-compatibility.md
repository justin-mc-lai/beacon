# User Story: Beacon v1.3.9 runtime skill admission and host-validated third-party skill compatibility

## Story

作为目标用户，我希望系统能够稳定地完成该需求主流程，以便快速完成业务动作。

### 需求描述

Beacon v1.3.9 需要新增一条并行 requirement 子线，把第三方 skill 的接入从静态 beacon.config.yaml 自动生成，收敛为 runtime skill admission 模型。目标是让 Beacon 在 implement --skill 调用前，借助当前 host runtime（codex 或 claude）直接分析和验证 skill 的可消费性，而不是先信任静态配置。要求：1）Codex/Claude 继续负责 skill 创建，Beacon 不再造 skill create 包装器；2）Beacon 只定义并消费 Beacon-compatible skill contract；3）implement --skill 在运行前必须做 skill discovery、host-runtime compatibility analysis、admission validation、admission cache writeback；4）beacon.config.yaml 只保留最小提示层，不再承担完整 contract truth；5）该模型必须支持非编码实现面，如 storyverse 这类长任务 workbench / content production；6）runtime admission 的结果要能被 qa/release/gate 消费，并进入 evidence/acceptance 闭环。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | happy-path | 用户可以完成「Beacon v1.3.9 runtime skill admission and host-validated third-party skill compatibility」主流程，满足：Beacon v1.3.9 需要新增一条并行 requirement 子线，把第三方 skill 的接入从静态 beacon.config.yaml 自动生成，收敛为 runtime skill admission 模型。目标是让 Beacon 在 implement --skill 调用前，借助当前 host runtime（codex 或 claude）直接分析和验证 skill 的可消费性，而不是先信任静态配置。要求：1）Codex/Claude 继续负责 skill 创建，Beacon 不再造 skill create 包装器；2）Beacon 只定义并消费 Beacon-compatible skill contract；3）implement --skill 在运行前必须做 skill discovery、host-runtime compatibility analysis、admission validation、admission cache writeback；4）beacon.config.yaml 只保留最小提示层，不再承担完整 contract truth；5）该模型必须支持非编码实现面，如 storyverse 这类长任务 workbench / content production；6）runtime admission 的结果要能被 qa/release/gate 消费，并进入 evidence/acceptance 闭环。 |
| AC-002 | validation | 输入校验规则明确，非法输入会返回可读错误。 |
| AC-003 | error-handling | 依赖失败时系统可恢复并提供下一步指引。 |
| AC-004 | observability | 关键步骤具备可追踪日志与最小化诊断信息。 |
| AC-005 | security | 仅授权用户可执行敏感操作，越权请求被拒绝。 |

## Metadata

- version: `v1.3.9`
- feature: `Beacon v1.3.9 runtime skill admission and host-validated third-party skill compatibility`
- status: `draft`
- generated_at: `2026-04-28T02:31:02.003392+00:00`
