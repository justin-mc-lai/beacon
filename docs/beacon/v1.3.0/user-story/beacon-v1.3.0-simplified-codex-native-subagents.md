# 用户故事：Beacon v1.3.0 简化版 Codex 原生子代理

**Feature**: `beacon-v1.3.0-simplified-codex-native-subagents`  
**Version**: `v1.3.0`  
**Date**: `2026-04-10`  
**Status**: `planning line`

## US-001：作为 Beacon 使用者，我希望复杂阶段可以显式启用子代理，而不是只能单线程生成

**验收标准**：

- Beacon 必须支持阶段级 `subagent_mode`
- `subagent_mode` 必须默认关闭
- 用户必须能看见当前阶段是否启用了子代理

## US-002：作为 Beacon 维护者，我希望每个阶段只暴露有限角色，而不是任意 agent 自由发挥

**验收标准**：

- 每个阶段必须声明允许角色
- 角色必须映射到明确输入、输出、证据路径
- 未注册角色不得直接进入正式 writeback

## US-003：作为需求作者，我希望 think / user-story / prd 可以借助子代理完成调研、结构化与批判，但最终仍回写到 Beacon 正式材料

**验收标准**：

- `think` 至少支持 `researcher` / `critic`
- `user-story` 至少支持 `story-mapper` / `ac-reviewer`
- `prd` 至少支持 `requirement-parser` / `risk-critic`
- 最终产物仍写入 `docs/beacon/<version>/...`

## US-004：作为 QA 负责人，我希望 test-case / qa 的子代理输出能直接表现为覆盖率、阻塞项与 repair handoff

**验收标准**：

- `test-case` 至少支持 `scenario-mapper` / `coverage-checker`
- `qa` 至少支持 `verifier` / `repair-handoff-writer`
- 证据缺失时必须阻塞，不允许假装通过

## US-005：作为实现负责人，我希望 `implement run` 能先对接 Codex 原生子代理，但不重写 Beacon 主链

**验收标准**：

- `implement run` 必须支持新的 Codex-native subagent adapter
- 现有 `native-single` / `native-team` 仍保留
- release/gate 仍只依赖 Beacon 的正式证据面

## US-006：作为版本规划者，我希望“下一版本 + 子代理演进”类输入先进 `version`，再落到具体阶段实现

**验收标准**：

- `beacon ask` / `beacon prompt optimize` 对此类输入必须优先进入 `version`
- 不允许再误路由到 `qa run all`
- `version` 产物必须指向后续 implement-first 多代理蓝图

## US-007：作为 Beacon 维护者，我希望现有版本字段语义被统一词典化并集中管理，避免源码后续继续混淆

**验收标准**：

- `package_version`、`runtime_version`、`docs_default_line`、`current_runtime_release_line`、`planning_lines`、`partial_runtime_supplement_lines` 必须拥有唯一语义
- `help` / `status` / `doctor` / `init` / `version` / `ask` 不得各自重新解释这些字段
- 后续源码演进必须统一走 versioning 层

## US-008：作为项目操作者，我希望文档线与 Beacon runtime 线始终显式分离，不再因“auto”或“current”产生歧义

**验收标准**：

- docs target resolution 与 runtime target resolution 必须是两条显式不同的语义路径
- planning prompt 可以命中 planning line，但不能因此改写 current runtime release line
- 任何新增版本字段或状态都必须先更新 canonical version semantics contract

## US-009：作为人类读者，我希望 v1.3.0 版本材料默认输出中文，降低理解门槛

**验收标准**：

- `PRD`、`用户故事`、`测试用例` 等人类主读材料默认使用中文
- `SUMMARY`、`execution/index`、`contract` 等关键导航面优先中文
- 不要求机器面 artifact 同步切成中文

## US-010：作为平台维护者，我希望机器可读工件继续保持英文键名与稳定结构，避免影响自动消费

**验收标准**：

- `json` / `.machine` / runtime state 允许默认英文
- 人类中文输出不应破坏机器字段稳定性
- 不允许为了中文展示重命名机器主键

## US-011：作为文档维护者，我希望人类中文镜像与机器英文 contract 保持一体两面同步，而不是手工双写后逐渐漂移

**验收标准**：

- machine-readable artifact 必须作为 source of truth
- human-readable markdown 必须作为中文镜像
- 两侧必须通过统一渲染或测试锁定同步
- 后续演进若只改一侧，测试必须失败

## US-012：作为平台维护者，我希望未来所有新的 contract artifact 都必须复用同一套“四件套”规范，而不是每次重新约定

**验收标准**：

- 任意新的 contract artifact 都必须同时提供 source JSON
- 必须提供中文镜像 Markdown
- 必须提供统一 render 函数
- 必须提供 drift test

## US-013：作为实现负责人，我希望 `implement plan` 与 `implement run` 都能稳定、显性地进入 team-mode，而不是只靠隐式判断

**验收标准**：

- `implement plan` 默认给出 team-mode 优先的执行拆解
- `implement run` 优先使用 `codex-subagents`
- 用户必须能通过显性稳定触发进入 team-mode

## US-014：作为 QA 负责人，我希望 `qa` 也能稳定进入 team-mode，但与实现上下文严格隔离

**验收标准**：

- `qa` 必须存在显性 team-mode 触发方式
- implement 与 qa 只能通过正式工件与 evidence refs 交互
- QA 不得直接继承 implement 的私有上下文
