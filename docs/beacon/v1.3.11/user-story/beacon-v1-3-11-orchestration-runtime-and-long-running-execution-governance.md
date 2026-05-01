# User Story: Beacon v1.3.11 orchestration runtime and long-running execution governance

## Story Boundary

- version: `v1.3.11`
- feature: `beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance`
- status: `prd_revised_after_reopen`
- upstream_prd: `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- current_revision: `R2`
- source_revision: `R1`

本故事线覆盖 Beacon 在 `v1.3.11` 中的 orchestration runtime requirement line，并补充同版本多 feature 共存、版本级 baseline host，以及 host-driven 自动实现顺序分析。它不扩展成新的一级公开 stage，也不让 runtime 反向篡改 requirement truth。

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

## Story 5: 同版本多 feature 共存与自动实现顺序分析

作为版本操作者，我希望同一版本下多个 feature package 可以共存而不互相覆盖，并且系统能通过版本级 baseline host 自动给出推荐实现顺序，这样我不需要手工维护 blueprint 覆盖关系、feature baseline 注册表和 feature 串并行表。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | feature-aware-blueprint | `execution/architecture-blueprint.md` 的 managed projection 至少按 `feature_slug` 独立投影与独立校验，同版本多个 feature 不会互相覆盖。 |
| AC-402 | feature-scoped-gate | `implement plan / implement run / release gate` 只校验当前 feature 对应的 blueprint projection block，不把其他 feature block 误判成 drift。 |
| AC-403 | implementation-order-analysis | Beacon 能基于显式 feature dependency 与 writable/direct delivery service 冲突，自动生成 `ordered_feature_slugs / waves / depends_on_features / reason_code`。 |
| AC-404 | version-level-order-surface | 版本级 change/release 面能把 implementation order 结果以人类可读方式投影出来，明确哪些 feature 可并行、哪些必须串行。 |
| AC-405 | version-level-baseline-host | Beacon 必须维护版本级 `implementation-delivery-host`，至少注册 `feature_slug / revision_id / baseline_ref / writable_services / depends_on_features / target_branch`，作为同版本多 feature baseline 的唯一宿主视图。 |
| AC-406 | host-driven-ordering | 版本级 implementation ordering 必须优先读取 baseline host；当部分 feature 的 technical review contract 尚未完整时，系统仍能基于 host registry 给出稳定的串并行建议。 |

## Delivery Notes

- 本故事线是 orchestration runtime 的版本级 requirement truth，不代表已经实现。
- `R2` 相比 `R1` 补充了 feature-aware blueprint projection 与 version-scoped implementation ordering。
- 当前补充进一步把模型层下沉到 `version-level baseline host + host-driven ordering`，避免多 feature 共存仍共享隐式单容器语义。
- 下一阶段应基于本 story 进入实现修订、delta QA 与 release recheck，而不是继续停留在“手工重投影 baseline”。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 18 |
| Status | revised-after-reopen-R2 |
| Created | 2026-05-01 |
| Change Scope | orchestration-runtime / scheduler / runtime-board / delivery-bridge / feature-aware-blueprint / version-level-baseline-host / implementation-ordering |
