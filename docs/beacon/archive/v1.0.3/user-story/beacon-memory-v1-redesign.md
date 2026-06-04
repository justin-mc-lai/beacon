# User Story: beacon-memory-v1-redesign

## Epic

作为 Beacon 维护者，我希望 workflow 与 memory 能形成真实可恢复闭环，使发布判定基于真实工件且记忆可持续自我修订，从而降低假闭环、假通过与重复问题成本。

## Stories

### US-001 记忆修订语义
作为 Dev，我希望记忆支持 update/archive/revision，而不是只 append，这样相同问题不会重复污染记忆库。

### US-002 分层召回
作为 Dev/QA，我希望 recall 支持 index/timeline/detail 三层召回，这样能在低 token 成本下快速定位高价值上下文。

### US-003 自反馈修订
作为 QA Lead，我希望 feedback 能基于 gate/auto-test reason_code 自动提炼并修订记忆，这样修复经验可复用。

### US-004 失败可恢复
作为 Dev，我希望 stage 失败后可重试覆盖并恢复 completed，这样 workflow 不会被一次失败永久卡死。

### US-005 workflow 完成态真实性
作为 Tech Lead，我希望 `workflow --auto` 只在 closure_complete 且 gate pass 时写 completed，这样避免假闭环。

### US-006 resume 推进
作为 Dev，我希望 `resume continue` 能自动推进 next_stage，这样续跑流程更稳定。

### US-007 release 真实校验
作为 Release Owner，我希望 `release check` 读取真实工件（auto-test/gate/evidence/coverage），这样发布结论可信。

### US-008 dry-run 非阻断
作为 QA，我希望 `gate --mode dry-run` 只输出问题不阻断退出码，这样可用于演练与预检查。

## Acceptance Criteria

| AC ID | User Story | Description | Priority |
| --- | --- | --- | --- |
| AC-001 | US-001 | Memory v1 支持 `status/superseded_by/revision_of/content_hash`，并可 update/archive | Must |
| AC-002 | US-002 | remember/recall 支持 `mode+layer` 分层召回（index/timeline/detail） | Must |
| AC-003 | US-003 | feedback 支持 `extract/apply`，可基于 reason_code 写回修订记忆 | Must |
| AC-004 | US-004 | lifecycle 支持 attempt，stage 状态按最新 attempt 终态判定 | Must |
| AC-005 | US-005 | `workflow --auto --skip` 不误报 completed；主状态机包含 gate | Must |
| AC-006 | US-006 | `resume continue` 可按 next_stage 推进执行并更新 run 状态 | Should |
| AC-007 | US-007 | `release check` 仅基于真实工件判定 pass/blocked | Must |
| AC-008 | US-008 | `gate --mode dry-run` 退出码 0 且不阻断 | Must |

## Blocking Semantics

- 任一 Must AC 失败 => v1.0.3 不可发布
- Should AC 失败 => 可发布但必须登记风险与补丁计划
