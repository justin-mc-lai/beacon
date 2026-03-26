# User Story: Beacon implement 子命令与自定义实现 Skill 适配（v1.1.4）

## Story

**As a** 使用 Beacon 的产品负责人 / 研发 / AI Agent 使用者，  
**I want** Beacon 提供正式的 `implement` 子命令，并允许我通过配置接入自定义实现 Skill / Runner（例如 OMX），  
**So that** 我可以在 Beacon 的需求闭环内触发外部实现能力执行编码实现、回写实现证据，并驱动 `review spec / review quality / verify / gate` 继续推进，而不是只靠 `--implementation-command` 这种薄占位能力。

## Acceptance Criteria

| AC ID | 维度 | 标准 |
|------|------|------|
| AC-001 | Command Surface | Beacon 提供顶层 `implement` 子命令组，而不是仅依赖 workflow 内部的 `implementation_command` 占位参数 |
| AC-002 | Subcommands | `implement` 至少提供：`run`、`status`、`list-runners` |
| AC-003 | Runner Model | `implement run` 支持 `--runner <id>`，Runner 不得被硬编码为单一 OMX 实现 |
| AC-004 | Config Priority | Runner 选择遵循优先级：CLI 参数 > 项目配置 > 全局配置 > 默认值 |
| AC-005 | User-defined Skill | 用户可通过配置注册自定义实现 Skill / Runner，而不是只能使用 Beacon 内置固定命令 |
| AC-006 | OMX Example | Beacon 至少支持 `omx` 作为一个实现 Runner 示例，可将 Beacon 需求物料组装为 OMX 可消费的任务输入 |
| AC-007 | Request Contract | `implement run` 必须写出结构化请求文件（如 `.beacon/implement/<run_id>/request.json`），记录 feature/version/source-of-truth/artifacts/runner 信息 |
| AC-008 | Result Contract | 外部 Skill / Runner 执行后，Beacon 可读取结构化结果文件（如 `.beacon/implement/<run_id>/result.json`），包括状态、变更文件、验证结果、artifact update 建议 |
| AC-009 | Runtime Evidence | `implement` 运行过程必须产出原始执行证据：stdout/stderr/command/request/result |
| AC-010 | Implementation Marker | 成功实现后，Beacon 必须创建 `.beacon/state/implementation-<feature>.json` 作为 implementation stage 的正式承接标记 |
| AC-011 | Execution Summary | Beacon 必须在 `docs/beacon/<version>/execution/` 下生成 `implementation-summary-<feature>.json/.md` 作为正式交付摘要 |
| AC-012 | Workflow Integration | 当 workflow 进入 implementation 阶段时，可解析 Runner 配置并自动调用 `beacon implement run` |
| AC-013 | Backward Compatibility | 若未配置 Runner，系统仍保留当前 `--implementation-command` / `BEACON_IMPLEMENTATION_COMMAND` 路径；若两者都无，则保持 Blocked |
| AC-014 | Spec Writeback | `implement` 结束后，Beacon 必须能够触发 `review spec <feature>`，用于判断 PRD / User Story / Test Case / Prototype 是否需要回填 |
| AC-015 | Quality Writeback | `implement` 结束后，Beacon 必须能够触发 `review quality <feature>`，用于判断 verify/gate-ready 状态 |
| AC-016 | Artifact Update Semantics | Runner 结果契约中必须允许声明 `artifact_updates`，指明是否需要更新 user-story/prd/test-case/prototype 及原因 |
| AC-017 | Source of Truth | `implement` 的长期事实源仍然是 `docs/beacon/<version>/`；`.beacon/implement/` 仅是运行时状态和 raw evidence |
| AC-018 | Boundary | Beacon 不直接变成编码编排平台 / scheduler；`implement` 是 implementation stage 的适配器，不是通用 agent orchestrator |
| AC-019 | Runner Types | 初版 Runner 模型至少支持：`command`、`command-skill` 两种适配方式 |
| AC-020 | Task Prompt Assembly | Beacon 必须能将 User Story / PRD / Test Case / Prototype / execution context 组装为外部 Skill 的实现任务提示 |
| AC-021 | Result Validation | 若 Runner 未输出结果文件或结果结构无效，`implement run` 必须失败并给出 reason code，而不是静默视为成功 |
| AC-022 | Reviewability | `implement status` 必须能展示当前 run、runner、request/result 路径、implementation marker、review 状态 |
| AC-023 | Config Model | Beacon 必须定义 `implementation.runners.<id>` 的配置结构，包括 type/command/args/env/timeout/result_file 等字段 |
| AC-024 | OMX Skill Binding | 对 OMX Runner，Beacon 必须支持通过配置指定 skill（如 `$workflows-work`）和 task prompt 模板 |
| AC-025 | Reason Codes | 失败路径必须具备明确的 reason code，例如：runner_not_configured / runner_result_missing / runner_result_invalid / implement_execution_failed |
| AC-026 | Draft Stage | 文档必须明确：v1.1.4 当前先冻结 `implement` 子命令需求与契约，不要求当前版本已完成全部运行时实现 |

## Notes

- 这不是把 Beacon 变成编码平台，而是把 implementation stage 从“外部命令占位符”升级为“有契约的实现承接动作”。
- OpenSpec 值得借鉴的是 `/opsx:apply` 的显式动作化设计、配置驱动和工具适配层，而不是把 Beacon 变成 OpenSpec 的复制品。
- 与 `bridge` 的差异在于：`implement` 是 Beacon 闭环里的正式动作；`bridge` 仍然是实验/运行时通道。
- 对个人用户而言，OMX 是最具代表性的实现 Runner 示例；但产品设计必须允许别的 Skill / 命令接入。
- `review spec` 不应只是报告，还应成为判断“是否需要回填需求物料”的标准接口；后续可再演进到 `--apply-writeback`。
- 当前 v1.1.4 需求稿重点是冻结：命令形态、Runner 配置模型、request/result 契约、workflow 接入点、物料回填语义。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 8 |
| Status | draft |
| Version | v1.1.4 |
| Feature Slug | beacon-implement-skill-runner |
