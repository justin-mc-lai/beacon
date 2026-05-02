# User Story: beacon-execution-runtime-kernel

## Story Boundary

- version: `v1.3.11`
- feature: `beacon-execution-runtime-kernel`
- status: `draft`
- upstream_prd: `docs/beacon/v1.3.11/prd/beacon-execution-runtime-kernel.md`
- runtime_anchor_prd: `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- current_revision: `R2`
- source_revision: `R1`

本故事线覆盖 Beacon 在 `v1.3.11` 中把 orchestration runtime 进一步下沉为真正可实现的 execution runtime kernel。它负责统一长任务运行模型、版本级 baseline host、自动实现顺序分析、scheduler / workspace / recovery contract，并作为后续 operator workbench 的唯一稳定执行底座。

## Story 1: 统一 runtime domain model 与 execution host

作为 Beacon runtime owner，我希望长任务不再散落在各 surface 的私有状态里，而是进入统一的 runtime domain model 与 execution host，这样后续调度、恢复和可视化才能建立在同一套权威对象上。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | runtime-domain-model | Beacon 正式定义 `WorkItem / Run / Workspace / AgentSession / RetryEntry / ExecutionHost / OperatorAction` 七类运行实体，并为每类实体保留稳定 machine projection。 |
| AC-002 | entity-core-fields | 每类核心运行实体至少具备 `version / feature_slug / revision_id / status / source_hash-or-transaction / evidence_refs` 字段，保证可追溯。 |
| AC-003 | execution-host | Beacon 维护统一 execution host，而不是由 `implement / qa / team / ralph / validation` 各自保留一套“当前运行态”。 |
| AC-004 | truth-consumption-only | runtime domain model 只消费冻结 requirement truth，不直接回写 `prd / user-story / test-case / prototype`。 |

## Story 2: 版本级 baseline host 与自动实现顺序分析

作为版本操作者，我希望同一版本下多个 feature 能共存，并由版本级 baseline host 自动分析串并行实现顺序，这样 blueprint、baseline 和 feature 顺序不会继续靠人工维护。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | version-level-baseline-host | Beacon 维护版本级 baseline host，至少注册 `feature_slug / revision_id / baseline_ref / writable_services / depends_on_features / target_branch`。 |
| AC-102 | multi-feature-coexistence | 同版本多个 feature baseline 可以稳定共存，不会因共享单一 blueprint container 而互相覆盖。 |
| AC-103 | host-driven-ordering | Beacon 能基于 `depends_on_features / writable_services / direct delivery services / branch target` 自动生成 `ordered_feature_slugs / waves / conflict_reason_codes`。 |
| AC-104 | ordering-fail-closed | 当 feature 依赖不完整、baseline host stale 或 writable scope 冲突无法解析时，系统必须阻断继续执行并给出明确人工介入理由。 |

## Story 3: 统一 scheduler、workspace isolation 与 recovery contract

作为执行面维护者，我希望 Beacon 有统一 scheduler、workspace isolation 与 recovery contract，这样长任务可以稳定地 start / continue / retry / stop，而不是每个 surface 自己拼一套恢复逻辑。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | run-scheduler | Kernel 提供统一 run scheduler，至少支持 `queued / admitted / running / blocked / retry_scheduled / stopped / completed / failed` 状态。 |
| AC-202 | operator-actions | Scheduler 至少支持 `start / continue / stop / retry / reconcile / repair-handoff` 等正式 operator action。 |
| AC-203 | workspace-isolation | 每个 run 都有稳定的 `workspace root / writable service scope / baseline binding / evidence output root / recovery metadata`。 |
| AC-204 | deterministic-recovery | 对 run interrupted、workspace drift、retry orphan、ordering stale、evidence sink missing 等失败类型，Beacon 存在确定性恢复路径，而不是只能整轮重跑。 |

## Story 4: runtime read model 与首批消费方面

作为 Beacon 产品负责人，我希望 runtime kernel 直接输出高信号 read model，并让 `implement / qa / release / team / ralph / real-project-validation` 成为共享消费方，这样执行态不会继续碎片化。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | runtime-read-model | Kernel 暴露正式 runtime read model，至少覆盖 `active_runs / blocked_runs / retry_queue / feature_ordering / baseline_host_state / recovery_alerts / latest_events`。 |
| AC-302 | implement-qa-release-bridge | `implement / qa / release` 能消费同一套 runtime host 与 read model，但不替代自身正式放行职责。 |
| AC-303 | consumer-unification | `team / ralph / real-project-validation` 至少在运行态层面共享同一 kernel contract，不再各自维护不可见私有 scheduler 语义。 |
| AC-304 | board-ready-substrate | runtime read model 足以支撑后续 operator workbench，无需 UI 再自行扫描散落 artifacts 拼装状态。 |

## Story 5: gate、repair 与 truth boundary

作为 Beacon governance owner，我希望 runtime kernel 的 admission、ordering、workspace 与 evidence 校验都能 fail-closed，并始终保持 requirement-first boundary，这样执行层不会重新把漂移引回真相层。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | admission-gate | run admission 前必须校验 frozen truth、baseline host、workspace binding、writable scope 与 ordering projection。 |
| AC-402 | fail-closed-recovery | 当 baseline host、ordering、workspace 或 evidence sink 漂移时，continue/retry 会被阻断并明确指向 repair path。 |
| AC-403 | no-truth-writeback | runtime kernel 只能产出 execution evidence、diagnosis 和 operator recommendation，不得绕过 `beacon-change` 直接篡改 requirement truth。 |
| AC-404 | downstream-consistency | `status / board / release / doctor advise` 对当前运行态的解释必须来源一致，不允许一个 surface 通过、另一个 surface 读到 stale runtime 状态。 |

## Story 6: reason code 与跨 surface host 一致性必须冻结

作为 Beacon operator 与治理维护者，我希望 drift、blocked、stale、orphan、conflict 等运行态异常都共享同一套 reason code 和 host 解释，这样不同入口不会对同一个 run 给出冲突判断。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | shared-reason-codes | `baseline host stale / ordering stale / workspace drift / writable scope conflict / blocked dependency / retry orphan / evidence sink missing` 等场景共享稳定 `reason_code / diagnosis / repair_path`。 |
| AC-502 | cross-surface-host-consistency | `implement / qa / release / team / ralph / real-project-validation / board` 对同一 run 的状态、排序、workspace、evidence 解释一致。 |
| AC-503 | no-surface-local-errors | 不允许不同 surface 再各自产生一套互不兼容的运行错误语义或恢复路径。 |
| AC-504 | fail-closed-precedence | 当 surface 可用性与 host 校验冲突时，必须优先执行 host fail-closed 约束，而不是为保持 UI 或命令连续性跳过校验。 |

## Story 7: prototype host-native runtime admission 与 execution 必须与宿主一致

作为 Beacon prototype 维护者，我希望 prototype compiler 和其他子 skill 一样先走 `codex|claude` host runtime，再按共享 bridge contract 执行宿主编译，这样原型生成不会继续退化为 env/file 注入协议或默认 rule 模板。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-601 | prototype-host-admission | prototype capability snapshot 必须把 host runtime support 与 host execution transport 分开表达，不能再把 `host_response_available` 直接当作唯一 host-ready 判据。 |
| AC-602 | provider-backed-host | 当 `codex|claude` host runtime 已识别且 provider bridge 可执行时，prototype host path 必须可以直接触发真实编译，而不是要求预注入 `BEACON_HOST_PROTOTYPE_RESPONSE_JSON/FILE`。 |
| AC-603 | legacy-injection-compatibility | 旧的 env/file response transport 仅作为兼容输入面保留，不能继续冒充默认 host-native execution 模式。 |
| AC-604 | prototype-host-precedence | `prototype create` 在 `auto` 模式下必须遵循 `host-native -> provider-backed host -> rule fallback` 的优先级，并输出稳定 `fallback_reason / inference_mode / capability_snapshot`。 |

## Delivery Notes

- 本故事线是 `beacon-execution-runtime-kernel` 的 requirement freeze，不代表已经实现。
- 它是 `beacon-operator-workbench-and-board-launcher` 的直接前置 substrate。
- 下一阶段应从本 story 继续进入 test-case，随后再进行 delta implement / delta qa。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 13 |
| Status | draft-runtime-substrate-r2 |
| Created | 2026-05-01 |
| Change Scope | runtime-domain-model / execution-host / version-level-baseline-host / implementation-ordering / scheduler / workspace-isolation / recovery / runtime-read-model / shared-reason-codes / cross-surface-host-consistency / prototype-host-native-runtime-admission |
