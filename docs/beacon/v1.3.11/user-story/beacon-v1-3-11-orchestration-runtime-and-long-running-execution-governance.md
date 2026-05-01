# User Story: Beacon v1.3.11 orchestration runtime and long-running execution governance

## Story Boundary

- version: `v1.3.11`
- feature: `beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance`
- status: `prd_frozen`
- upstream_prd: `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`

本故事线只覆盖 Beacon 在 `v1.3.11` 中的 orchestration runtime requirement line，不扩展成新的一级公开 stage，也不让 runtime 反向篡改 requirement truth。

## Story 1: 统一 work item 与 run 模型

作为 Beacon runtime owner，我希望所有长任务都能进入统一 `work item -> run` 模型，而不是继续散落在不同 surface 的私有状态里。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | work-item-model | Beacon 能定义统一 work item 模型，至少覆盖 `item_id / item_type / feature / version / source_surface / priority / requested_action / truth_refs / status`。 |
| AC-002 | run-model | 每个已派发 work item 都会生成统一 run 记录，至少包含 `run_id / item_id / workspace_ref / runtime_mode / status / attempt_seq / next_action / evidence_refs`。 |
| AC-003 | supported-item-types | 最小 item type 集合至少覆盖 `team_task / ralph_step / real_project_validation_case / implement_delivery / qa_repair / release_closure`。 |
| AC-004 | status-contract | run 状态至少覆盖 `queued / running / retry_waiting / blocked / handoff_required / completed / cancelled`。 |

## Story 2: 统一 scheduler、workspace isolation 与恢复语义

作为执行面维护者，我希望长任务通过统一 scheduler 派发，并拥有清晰的 workspace isolation 与 retry/reconciliation 语义，这样真实项目长任务不会继续靠人工拼接上下文。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | scheduler-contract | Beacon 提供统一 run scheduler，至少支持入队、派发、并发限制、continuation、失败重试、人工介入挂起与取消。 |
| AC-102 | workspace-isolation | 每个 run 都有独立 workspace boundary，并且能够绑定 run_id、控制清理策略、阻断越界写入。 |
| AC-103 | retry-reconciliation | Beacon 显式支持 backoff retry、stale run detection、eligibility re-check、blocked -> repair -> resume、abandoned run reconciliation。 |
| AC-104 | deterministic-recovery | 对 `real-project-validation` 与 `qa repair` 一类失败 run，系统能给出明确恢复路径，而不是只能整条命令重跑。 |

## Story 3: runtime board 与 delivery closure bridge

作为版本操作者，我希望运行面能直接告诉我“现在发生了什么”，并且与 `implement / qa / release` 的正式闭环入口保持稳定边界。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | runtime-board | Beacon 提供 runtime board，至少展示 running runs、retry queue、blocked/handoff runs、stage 分布、人工介入项与 next action。 |
| AC-202 | evidence-driven-board | runtime board 优先显示高信号运行判断，而不是直接暴露 machine noise。 |
| AC-203 | delivery-bridge | orchestration runtime 能桥接 `implement / qa / release`，但不替代其正式闭环角色。 |
| AC-204 | truth-boundary | runtime 只做调度、状态、证据与桥接，不反向改写 `prd / user-story / test-case / prototype`。 |

## Story 4: 首批消费方接入

作为 Beacon 产品负责人，我希望 `team / ralph / real-project-validation` 在本版本内成为首批 runtime 消费方，而不是继续各自维护半套调度逻辑。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | team-consumer | `team` 能以 work item 派发任务、以 run 观察任务、以 runtime board 观察整体运行态。 |
| AC-302 | ralph-controller | `ralph` 被明确定位为 `what next` controller，而不是直接持有所有执行态的执行器。 |
| AC-303 | validation-consumer | `real-project-validation` 支持 validation case -> work item -> per-run workspace -> retry/repair 的 runtime 接入路径。 |
| AC-304 | no-fragmented-schedulers | `team / ralph / validation / implement / qa` 不再各自维护不可见的私有调度语义。 |

## Delivery Notes

- 本故事线是 orchestration runtime 的版本级 requirement truth，不代表已经实现。
- 下一阶段应基于本 story 补齐 test-case，并进入实现闭环。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 13 |
| Status | draft-frozen-prd-line |
| Created | 2026-05-01 |
| Change Scope | orchestration-runtime / scheduler / runtime-board / delivery-bridge |
