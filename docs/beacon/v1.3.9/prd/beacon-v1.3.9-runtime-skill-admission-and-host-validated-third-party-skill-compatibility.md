# PRD: Beacon v1.3.9 runtime skill admission and host-validated third-party skill compatibility

## 1. Overview

- 目标版本: `v1.3.9`
- 需求描述: Beacon v1.3.9 需要新增一条并行 requirement 子线，把第三方 skill 的接入从静态 beacon.config.yaml 自动生成，收敛为 runtime skill admission 模型。目标是让 Beacon 在 implement --skill 调用前，借助当前 host runtime（codex 或 claude）直接分析和验证 skill 的可消费性，而不是先信任静态配置。要求：1）Codex/Claude 继续负责 skill 创建，Beacon 不再造 skill create 包装器；2）Beacon 只定义并消费 Beacon-compatible skill contract；3）implement --skill 在运行前必须做 skill discovery、host-runtime compatibility analysis、admission validation、admission cache writeback；4）beacon.config.yaml 只保留最小提示层，不再承担完整 contract truth；5）该模型必须支持非编码实现面，如 storyverse 这类长任务 workbench / content production；6）runtime admission 的结果要能被 qa/release/gate 消费，并进入 evidence/acceptance 闭环。

## 2. Scope

- In scope: `Beacon v1.3.9 runtime skill admission and host-validated third-party skill compatibility` 的核心业务流程与必要风控校验。
- Out of scope: 与该需求无关的跨域重构或新增平台能力。

## 3. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | 用户可以完成「Beacon v1.3.9 runtime skill admission and host-validated third-party skill compatibility」主流程，满足：Beacon v1.3.9 需要新增一条并行 requirement 子线，把第三方 skill 的接入从静态 beacon.config.yaml 自动生成，收敛为 runtime skill admission 模型。目标是让 Beacon 在 implement --skill 调用前，借助当前 host runtime（codex 或 claude）直接分析和验证 skill 的可消费性，而不是先信任静态配置。要求：1）Codex/Claude 继续负责 skill 创建，Beacon 不再造 skill create 包装器；2）Beacon 只定义并消费 Beacon-compatible skill contract；3）implement --skill 在运行前必须做 skill discovery、host-runtime compatibility analysis、admission validation、admission cache writeback；4）beacon.config.yaml 只保留最小提示层，不再承担完整 contract truth；5）该模型必须支持非编码实现面，如 storyverse 这类长任务 workbench / content production；6）runtime admission 的结果要能被 qa/release/gate 消费，并进入 evidence/acceptance 闭环。 |
| FR-002 | AC-002 | 输入校验规则明确，非法输入会返回可读错误。 |
| FR-003 | AC-003 | 依赖失败时系统可恢复并提供下一步指引。 |
| FR-004 | AC-004 | 关键步骤具备可追踪日志与最小化诊断信息。 |
| FR-005 | AC-005 | 仅授权用户可执行敏感操作，越权请求被拒绝。 |

## 4. Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | happy-path | 用户可以完成「Beacon v1.3.9 runtime skill admission and host-validated third-party skill compatibility」主流程，满足：Beacon v1.3.9 需要新增一条并行 requirement 子线，把第三方 skill 的接入从静态 beacon.config.yaml 自动生成，收敛为 runtime skill admission 模型。目标是让 Beacon 在 implement --skill 调用前，借助当前 host runtime（codex 或 claude）直接分析和验证 skill 的可消费性，而不是先信任静态配置。要求：1）Codex/Claude 继续负责 skill 创建，Beacon 不再造 skill create 包装器；2）Beacon 只定义并消费 Beacon-compatible skill contract；3）implement --skill 在运行前必须做 skill discovery、host-runtime compatibility analysis、admission validation、admission cache writeback；4）beacon.config.yaml 只保留最小提示层，不再承担完整 contract truth；5）该模型必须支持非编码实现面，如 storyverse 这类长任务 workbench / content production；6）runtime admission 的结果要能被 qa/release/gate 消费，并进入 evidence/acceptance 闭环。 |
| AC-002 | validation | 输入校验规则明确，非法输入会返回可读错误。 |
| AC-003 | error-handling | 依赖失败时系统可恢复并提供下一步指引。 |
| AC-004 | observability | 关键步骤具备可追踪日志与最小化诊断信息。 |
| AC-005 | security | 仅授权用户可执行敏感操作，越权请求被拒绝。 |

## 5. Risks

- 需求理解偏差：通过 AC 与 TC 一一映射降低语义漂移。
- 交付回归风险：通过测试用例覆盖主流程、异常路径与安全边界。

## 6. Release Guard

- 通过 `qa` 验证 AC 关闭状态后方可进入 release 评审。
