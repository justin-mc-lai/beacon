# 用户故事：Beacon v1.3.3 核心瘦身与外部 skill 降级

**Feature**: `beacon-v1.3.3-core-slimming-and-external-skill-demotion`  
**Version**: `v1.3.3`  
**Date**: `2026-04-17`  
**Status**: `current release snapshot`

## US-001：作为 Beacon 人类操作者，我希望默认只面对 `6+3` 极简主面，而不是先学习 skill/profile/orchestrate

**验收标准**：

- 默认主叙事仍然是 `prd -> user-story -> test-case -> implement -> qa -> release`
- 默认辅助面仍然是 `help / status / doctor`
- `skill / profile / orchestrate` 不得继续出现在普通用户的主教学路径里

## US-002：作为 Beacon 维护者，我希望外部 runner 只作为 compatibility plane，而不是 core 主面

**验收标准**：

- `omx / omc / gstack` 只能作为 compatibility 能力被描述
- 默认 runner 不得回退为外部 runner
- README / help / runner narrative 不得把它们继续当成正式默认路径

## US-003：作为真实项目操作者，我希望 `implement` 默认先走 Beacon 内部宿主原生执行面

**验收标准**：

- `single` 默认面向 native single
- `team` 默认面向 host-native bounded team runtime
- `ralph` 默认面向 host-native loop controller
- 外部 runner 只能通过显式兼容配置进入

## US-004：作为 QA 负责人，我希望 `qa` 默认不再隐式自动触发外部 orchestration

**验收标准**：

- `qa` 默认不自动执行 project orchestration
- 只有在显式 profile mode 或显式开关下，才允许执行 external orchestration
- 当未显式启用时，系统应返回清晰阻断与推荐下一步

## US-005：作为 Beacon 维护者，我希望 `ralph-bridge` 退出正式产品叙事

**验收标准**：

- `ralph-bridge` 不再作为未来主线能力出现
- 如果保留，必须标记为 deprecated compatibility
- 如果替代，必须由 Beacon 内部 `ralph` 控制面接住语义

## US-006：作为文档维护者，我希望主面文档只教学 6+3，而不是把 project-aware compatibility 当默认路径

**验收标准**：

- README 只教学 6+3 主面
- help/status 文案对 external plane 做 compatibility 标识
- host-visible skill 文案不再默认扩张到 skill/profile/orchestrate

## US-007：作为测试维护者，我希望 core 与 compatibility 测试边界清晰

**验收标准**：

- core tests 只验证 Beacon core 主链与宿主原生面
- compatibility tests 承接 legacy/external runner 断言
- 不得继续在 core tests 中隐含 `gstack / omx / omc` 是正式主面组成部分

## US-008：作为平台维护者，我希望 discover/registry 输出分层，不把 external skill 冒充成 Beacon core

**验收标准**：

- builtin native 能力必须单独展示
- external compatibility 能力必须单独展示
- 输出文案必须明确区分 core 与 compatibility

## US-009：作为真实项目负责人，我希望 project contract 能力保留，但不再强绑 external orchestration

**验收标准**：

- required evidence / required cases / contract drift 继续存在
- contract evaluation 必须与 external command execution 解耦
- 不应因为保留 contract plane，就必须保留重型 external orchestration 主路径

## US-010：作为首次接入 Beacon 的新用户，我希望 compatibility plane 默认不干扰我

**验收标准**：

- 初次使用 Beacon 时不应先看到 `skill bind`
- 不应先看到 `profile create`
- 不应先看到 `orchestrate run`
- 不应先被要求理解 external adapter registry

## US-011：作为需求操作者，我希望 `beacon-prd-bootstrap` 一键生成 requirement 三件套且默认安全

**验收标准**：

- `beacon-prd-bootstrap` 作为 optional 人类 skill，不新增公开一级命令
- 默认必须 `dry-run`，仅显式 `--apply` 才允许落盘
- 默认必须 `--no-overwrite`，遇到既有文档必须阻断并给单一恢复命令
- 执行前必须跑 `beacon doctor verify-context --project-root . --strict`
- 写入必须原子化，失败不得留下半成品
- 必须写出 `.beacon/state/prd-bootstrap/<run-id>.json` 与回滚清单
- 必须持有 `.beacon/state/locks/prd-bootstrap.lock` 防并发写冲突

## US-012：作为 Codex 用户，我希望输入框下方固定显示 Beacon HUD，并在提交输入和会话刷新时自动更新

**验收标准**：

- Codex 输入框下方可稳定显示来自 `minimal_hud` 的 1-3 行 HUD
- `UserPromptSubmit` 事件触发后 HUD 必须立即刷新
- 会话刷新事件（`SessionStart/SessionResume/SessionRefresh`）至少支持其一并可配置
- hook 输出必须通过 `hookSpecificOutput.additionalContext` 返回 HUD 文本，不得返回长解释段落
- hook 异常时不得阻断用户输入提交流程，必须降级并写 debug 证据
- hook wiring 的安装/校验必须通过 `beacon doctor`，禁止未确认自动改写全局 `~/.codex` 配置

## Acceptance Criteria Matrix

| ID | Theme | Acceptance Criteria |
|----|-------|---------------------|
| AC-001 | minimal-mainline | Beacon 默认主叙事必须继续保持 `6+3`，不得把 `skill / profile / orchestrate` 作为普通用户主教学路径。 |
| AC-002 | external-runner-demotion | `omx / omc / gstack` 必须被定义为 compatibility plane，而不是 Beacon core 默认能力。 |
| AC-003 | host-native-default | `implement` 默认执行面必须继续保持宿主原生优先，不得回退成外部 runner 优先。 |
| AC-004 | qa-no-implicit-orchestration | `qa` 默认不得隐式自动执行 project orchestration；只有显式 mode 或开关下才允许。 |
| AC-005 | ralph-bridge-demotion | `ralph-bridge` 必须退出正式主叙事，只能作为 deprecated compatibility 或被内化替代。 |
| AC-006 | docs-teach-6-plus-3 | README / help / host skill 文案必须只教学 `6+3` 默认主面。 |
| AC-007 | core-vs-compat-tests | 测试必须拆分为 core 与 compatibility，两者责任边界明确。 |
| AC-008 | layered-discovery | `skill detect / registry / discovery` 的输出必须分层展示 builtin core 与 external compatibility。 |
| AC-009 | contract-decoupled | project contract 能力必须与 external orchestration 解耦。 |
| AC-010 | new-user-unblocked | 新用户在默认路径下不应先接触 compatibility plane 命令和概念。 |
| AC-011 | prd-bootstrap-safe-by-default | `beacon-prd-bootstrap` 必须支持一键生成 `prd/user-story/test-case`，且默认 `dry-run + no-overwrite + strict context verify + atomic write + rollback/lock`。 |
| AC-012 | codex-fixed-hud-hook | Codex 输入框下固定 HUD 必须通过 hook 自动注入，覆盖 `UserPromptSubmit` 与会话刷新，且失败可降级不阻断。 |
