# User Story: Beacon v1.4.0 lightweight kernel and core surface refactor

## Story Boundary

- version: `v1.4.0`
- feature: `beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor`
- status: `frozen-pending-implementation`
- upstream_prd: `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- current_revision: `R2`
- source_revision: `R1`

本故事线覆盖 Beacon 在 `v1.4.0` 中完成“减负不减基座”的正式拆解。它要求 Beacon 在保留 frozen truth、gate、implement/qa、host-runtime、learning、meta、memory、archive 等基座能力的前提下，收敛 machine contract、增强 change 与 implement 闭环、补齐人类面任务进度与全局边界操作面，并对 skill 默认可见性与自仓库版本元信息漂移做正式治理。

## Diagram Truth

- `branch-flow`
  - 人类主链仍固定为 `prd -> user-story -> test-case -> implement -> qa -> release`
  - `prototype` 只在真实 UX/UI surface 或 route/state/interaction handoff 场景下插入为条件层
  - `change` 是 truth 变更路由，不是新 stage
  - `brainstorm` 是只读收敛面，不是 truth 面
  - `help/status/archive/boundaries` 属于 support surface，不取代主链
- `decision-priority`
  - `truth > contract > execution projection > support projection`
  - `gate/qa/release truth` 高于 `goal/task ledger/runtime projection`
  - `public visibility` 与 `capability existence` 必须分开治理
- `state-machine`
  - `draft truth -> frozen truth -> changed truth -> refreezing -> implementing -> verifying -> accepted -> archived`
  - requirement drift 或 acceptance 失败都必须显式回到 `changed truth` 或 `implementing`，不能静默穿越阶段

## Story 1: Beacon 必须先把 truth、contract、projection 三层边界冻结清楚

作为 Beacon 内核 owner，我希望 `v1.4.0` 先明确 `docs/beacon/<version>/**/*.md`、minimal machine contract、optional projection 三层边界，这样减负不会演变为删除基座，也不会继续容忍多真相幻觉。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | truth-root | 系统必须继续把 `docs/beacon/<version>/**/*.md` 定义为唯一冻结真相源。 |
| AC-002 | contract-layer | 系统必须把 `gate / implement / qa / release` 的机器主入口收敛为 compiled contract，而不是继续以碎片 mirror 作为默认主路径。 |
| AC-003 | projection-demotion | sqlite / pocketbase / board / legacy mirror 必须被明确标记为 optional projection，而不是主路径 truth closure 依据。 |
| AC-004 | no-reverse-write | 任意 projection 或 support read-model 都不得反向定义 truth。 |

## Story 2: Beacon 必须把 `change` 从 scattered loop 收敛成正式事务单元

作为 requirement governance owner，我希望 Beacon 的 frozen-scope change 不再分散在 `reopen / freeze / change-impact / release summary` 等零散位置，而是拥有稳定的 change identity 与 contract，这样 change loop 可解释、可验证、可审计。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | change-identity | 每次 truth 变更都必须拥有稳定的 `change_id`，并能绑定 `target_version / target_feature / baseline_revision`。 |
| AC-102 | change-contract | 系统必须存在 machine-readable change contract，至少覆盖 change reason、affected truth refs、affected layers、verification refs、archive status。 |
| AC-103 | single-change-thread | reopen / revise / refreeze / delta implement / delta qa / release recheck 必须沿同一 change identity 继续，而不是重新漂移成多条局部状态线。 |
| AC-104 | change-archive | per-change closure 必须能聚合进 version-level change summary，但 version summary 不能替代 per-change truth。 |

## Story 2A: Beacon 必须把源码仓版本真相收敛到单一 release manifest

作为 Beacon maintainer，我希望 package version、runtime version、docs line、release truth line 不再分散在多个手工编辑文件中，而是统一收口到一个 canonical release manifest，再向各表面单向投影，这样版本升级不会继续产生隐藏漂移。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-105 | single-manifest | Beacon 自仓库必须存在一个 canonical release manifest，作为 package/runtime/docs/release truth 的唯一编辑源。 |
| AC-106 | projected-surfaces | `beacon/__init__.py`、version truth 兼容表面、skill/rules 版本标记、运行期版本解析输出都必须可回溯到同一 manifest。 |
| AC-107 | sync-version-surfaces | 系统必须提供显式的 `sync-version-surfaces` 治理能力，把 drifted 版本表面重新校准到 manifest。 |
| AC-108 | verify-version-surfaces | 系统必须提供显式的 `verify-version-surfaces` 治理能力，并在 strict 模式下对 drift 返回阻断 verdict。 |

## Story 3: Beacon 必须借鉴 OpenSpec 的 change container 可见性，但不能照搬公开命令面

作为 Beacon 产品 owner，我希望系统吸收 OpenSpec 的 change container 优点，而不复制 OPSX 命令膨胀，这样 Beacon 既能获得显式变更工作单元，又能保持极简人类主面。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | borrow-container-not-cli | 系统必须借鉴 OpenSpec 的单 change 工作单元，但不得因此新增新的公开一级主命令集合。 |
| AC-202 | change-visibility | `help/status/report/gate` 至少要能统一投影当前 change id、change state、blocked reason、next action。 |
| AC-203 | no-new-stage | `beacon-change` 仍是 router，不得被误导为新的 primary lifecycle stage。 |
| AC-204 | drift-routing | 当 frozen truth 漂移时，support surface 与 execution surface 必须统一推荐回到 change loop。 |

## Story 4: `implement` 必须把 Codex goal 作为 execution-side capability 接入，而不是新的 truth source

作为 implement runtime owner，我希望当 host 为 Codex 且 goals 可用时，Beacon 能把 requirement package 映射到 persistent thread goal，并把它用作连续执行与预算收尾能力，而不是把它当成 completion truth。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | goal-optional-host-capability | goal integration 只在 host=codex 且 feature enabled 时生效，非 Codex host 必须有显式 fallback。 |
| AC-302 | requirement-to-goal | goal objective 必须可追溯到 requirement package / implementation plan，而不是自由文本。 |
| AC-303 | goal-not-truth | `goal.complete` 不能单独定义 implement complete、qa pass 或 release pass。 |
| AC-304 | budget-limited-closure | 当 goal 进入 `budget_limited` 时，系统必须进入收尾、handoff 或明确阻断，而不是静默继续。 |

## Story 5: Ralph 必须与 goal、verification、QA handoff 形成统一闭环

作为 Beacon delivery owner，我希望 Ralph 的 rounds、stop_state、handoff 和 verification 不再孤立运作，而是与 thread goal、QA handoff 和 gate 形成同一条 implement closure 链。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | goal-aware-ralph | Ralph 每轮 round 至少能读取当前 goal objective 与 status。 |
| AC-402 | unified-stop-semantics | Ralph 的 `release_ready / human_blocked / budget_exhausted` 必须与 goal state 和 verification state 协同解释。 |
| AC-403 | qa-handoff | 当 Ralph 完成实现但未完成 acceptance 时，系统必须能进入明确 QA handoff，而不是直接宣称 release-ready。 |
| AC-404 | execution-audit | Ralph rounds、goal state、QA handoff refs 必须保留为 execution audit evidence。 |

## Story 6: `implement` 必须拥有 human-readable tasks progress ledger

作为人类操作者，我希望 `implement` 不只存在 machine plan 与 progress json，还存在一份人机共读的任务账本，这样我能直观看到完成度、阻断点与下一步动作，并在中断后恢复。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | task-ledger-exists | 系统必须为实现阶段生成 human-readable tasks ledger。 |
| AC-502 | checkbox-or-equivalent | task ledger 必须能表达未完成/已完成状态，至少达到 checkbox 或等价低摩擦进度表达。 |
| AC-503 | progress-and-blockers | task ledger 至少能展示 `N/M progress`、current task、blocked tasks、next task。 |
| AC-504 | interruption-friendly | 人类或 agent 在中断恢复时，能从 task ledger 快速判断从哪继续。 |

## Story 7: `tasks progress ledger` 必须是 implementation-plan 的单向人类投影

作为 contract owner，我希望 task ledger 的存在不会引入第二执行真相源，而是从 canonical implementation plan 单向投影生成，这样既好用，又不会破坏 traceability。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-601 | canonical-plan-source | canonical execution task identity 仍来自 implementation plan json。 |
| AC-602 | machine-progress-source | machine aggregation 仍来自 progress json 或等价 machine progress artifact。 |
| AC-603 | task-ledger-human-projection | `tasks-<feature>.md` 只负责人类面进度与阻断提示，不得单独定义 machine truth。 |
| AC-604 | gate-does-not-trust-checkbox-alone | gate 不得只因为 checkbox 完成就判定实现闭环，而必须继续依赖 evidence、traceability 与 QA closure。 |

## Story 8: Beacon 必须增加显性的人类面 global boundary/context surface

作为 Beacon 使用者，我希望系统不仅内部有 `global-boundaries.md`，还提供显式的人类面入口来解释全局边界、判断越界、校准上下文层级，这样我不需要依赖熟悉者记忆才能正确使用上位约束。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-701 | human-usable-boundary-surface | 系统必须存在显性人类面入口来操作 global boundary/context。 |
| AC-702 | explain-and-calibrate | 该入口至少支持边界解释、越界判断、上下文校准。 |
| AC-703 | truth-layer-separation | 该入口必须能区分 global、version、feature 三层约束。 |
| AC-704 | no-new-primary-stage | 该入口属于 support surface，不得被误解为新的 lifecycle stage。 |

## Story 9: `global-boundaries` 的人类面必须只做解释/校准/路由，不做自由配置真相

作为 boundary governance owner，我希望新增的人类面 boundary surface 不会退化为自由配置入口或 truth 漂移入口，而是只负责解释、校准、建议路由。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-801 | no-config-drift | human boundary surface 不得直接把任意临时输入写成 canonical global truth。 |
| AC-802 | placement-judgment | 系统必须能判断某条原则应进入 global-boundaries、version PRD，还是只保留在 brainstorm/research。 |
| AC-803 | canonical-writeback-route | 若需要正式变更全局边界，必须走明确的 canonical writeback route，而不是 UI/skill 任意修改。 |
| AC-804 | boundary-auditability | 任意上位边界变更建议都必须可被审计与追踪。 |

## Story 10: `help / status / archive` 必须转向 action-oriented human projection

作为人类操作者，我希望 support surface 优先回答“现在该做什么、为什么、做完会解锁什么”，而不是默认把复杂 read-model 暴露给我。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-901 | current-artifact-focus | support surface 至少能回答当前卡在哪个 artifact。 |
| AC-902 | next-action-clarity | support surface 至少能回答下一个动作、原因、建议命令。 |
| AC-903 | unlock-visibility | support surface 至少能说明执行该动作后会 unlock 什么。 |
| AC-904 | machine-detail-second | 复杂 machine/read-model 细节应退到 JSON 或 deeper layer，而不是默认人类输出。 |

## Story 11: Beacon 必须把 artifact dependency 与 interruption recovery 边界正式外显

作为长期使用者，我希望 Beacon 能正式告诉我哪些 artifact ready、哪些 blocked、缺什么 dependency、从哪里恢复，这样并行与中断就不会再依赖隐式记忆。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-1001 | ready-blocked-completed | 关键 artifact 至少能被表达为 ready / blocked / completed。 |
| AC-1002 | dependency-visibility | blocked artifact 必须能说明缺失 dependency。 |
| AC-1003 | recovery-anchor | interruption recovery 必须能锚定到 task / artifact 级别，而不是仅靠 run id 推断。 |
| AC-1004 | no-duplicate-work | 恢复信息必须帮助人类和 agent 避免重复完成已做任务。 |

## Story 12: Beacon 必须建立正式 skill taxonomy

作为 Beacon 产品 owner，我希望 skill 的类型边界正式化，这样主流程 skill、support skill、advanced skill、internal skill 不会继续混在一层污染用户心智。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-1101 | four-tier-taxonomy | 系统至少定义 `lifecycle core / support core / advanced project-specific / internal maintainer` 四层 taxonomy。 |
| AC-1102 | shared-consumption | 该 taxonomy 必须能被 docs、router、help/status、skill discovery 共用。 |
| AC-1103 | audience-model | 每个 skill 至少应具备 intended audience 与 visibility tier。 |
| AC-1104 | no-flat-skill-list | Beacon 不得继续把所有 skill 当作同层默认可见人类入口。 |

## Story 13: Beacon 必须建立默认 skill visibility governance

作为人类面治理 owner，我希望 skill 的存在与默认可见性分开治理，这样仓库中必要但特化的能力不会自然污染默认用户面。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-1201 | existence-vs-visibility | 系统必须正式区分 capability existence 与 default human-surface visibility。 |
| AC-1202 | contextual-recommendation | advanced/internal skill 应由 support surface 在条件满足时推荐，而不是默认暴露。 |
| AC-1203 | public-surface-freeze | 默认 public skill surface 必须被正式冻结。 |
| AC-1204 | visibility-audit | skill visibility 规则必须可被文档化、验证与演进。 |

## Story 14: `beacon-iteration-governance` 与 `beacon-prototype-reconcile` 的定位必须被正式冻结

作为 Beacon 人类面治理 owner，我希望最近审计暴露出的两个特化 skill 有明确定位，这样能力可以保留，但不会继续误导用户。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-1301 | iteration-governance-tier | `beacon-iteration-governance` 必须被标记为 internal/maintainer skill。 |
| AC-1302 | prototype-reconcile-tier | `beacon-prototype-reconcile` 必须被标记为 advanced/project-specific skill。 |
| AC-1303 | not-default-public | 二者都不得进入默认 public skill surface。 |
| AC-1304 | conditional-routing | 只有在 Beacon self-repo release governance 或 severe prototype drift/takeover 等条件成立时，support/router 才应推荐它们。 |

## Delivery Notes

- 本 story package 的目标不是展开所有实现细节，而是把 `v1.4.0` PRD 中新增的减负与人类面治理要求编译成可执行故事。
- `change kernel`、`goal/Ralph`、`task ledger`、`global-boundaries human surface`、`skill visibility governance`、`version surface governance` 是本轮必须覆盖的主轴。
- 下一阶段应基于本 story package 进入 `test-case`，产出对应 contract、projection、routing、gate、audit 的验收矩阵。

## Freeze Notes

- 当前 story package 的冻结前提不是“代码已完成”，而是：
  - 关键能力分组已经完整
  - human surface / machine surface / truth surface 三层边界已经清楚
  - visibility governance 已从隐性经验升级为正式 requirement
  - implementation、change、support、boundary 四类新增面都有对应 story
- 如果后续 `test-case` 无法把：
  - task ledger projection
  - change contract
  - goal/Ralph mapping
  - skill visibility governance
  - canonical release manifest / sync-version-surfaces / verify-version-surfaces
  做成正式验收对象，则本 story package 应从 `freeze-ready` 退回 `blocked`。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 21 |
| Status | frozen-pending-implementation-lightweight-kernel-r2 |
| Created | 2026-05-06 |
| Change Scope | lightweight-kernel / change-kernel / version-surface-governance / codex-goal / ralph-closure / task-ledger / global-boundary-surface / support-projection / skill-taxonomy / visibility-governance |
