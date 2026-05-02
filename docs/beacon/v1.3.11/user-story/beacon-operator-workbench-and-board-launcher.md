# User Story: beacon-operator-workbench-and-board-launcher

## Story Boundary

- version: `v1.3.11`
- feature: `beacon-operator-workbench-and-board-launcher`
- status: `draft`
- upstream_prd: `docs/beacon/v1.3.11/prd/beacon-operator-workbench-and-board-launcher.md`
- runtime_dependency: `docs/beacon/v1.3.11/prd/beacon-execution-runtime-kernel.md`
- current_revision: `R2`
- source_revision: `R1`

本故事线覆盖 Beacon 在 `v1.3.11` 中把现有 management board / status board 演进为真正的 operator workbench，并冻结 board launcher 的本地可执行入口 contract。它不让 UI 成为新的真相层，也不把 Beacon 退化成通用 agent IDE。

本次修订补入两类显式约束：

- 原型失真约束：禁止继续输出通用后台资产页或 design asset catalog 作为可交付 workbench prototype
- 语义失真约束：operator-facing 文案必须满足正式、克制、严谨、专业、简洁、准确的软件语义规范

## Story 1: workbench 信息架构必须先于视觉实现冻结

作为 Beacon operator，我希望 workbench 先冻结真正可用的信息架构，而不是继续只做 status 页美化，这样后续执行看板才能围绕长任务运营而不是围绕被动汇报。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | workbench-ia | Workbench 至少定义 `portfolio-board / execution-board / feature-detail / run-detail / review-surface / recovery-diagnostics` 六类正式视图。 |
| AC-002 | lifecycle-first-navigation | 主导航优先体现 lifecycle / execution / delivery 主轴，而不是先按 `team / ralph / validation` 等运行模式组织。 |
| AC-003 | contract-driven-views | 每个视图都有明确输入 contract，不允许页面自己猜文件结构或扫描散落 artifacts。 |
| AC-004 | operator-not-reporter | 视图设计目标明确是帮助 operator 判断、干预和验收，而不是只展示摘要。 |

## Story 2: execution board 与 run detail 必须成为正式操作面

作为执行面操作者，我希望存在真正的 execution board 和 run detail，而不是只看文本摘要，这样我能知道什么在跑、什么被阻塞、下一步该怎么处理。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | execution-board-state | 执行主看板至少展示 `queued / active / blocked / retry scheduled / needs review` 五类运行分组。 |
| AC-102 | ordering-and-host-visibility | 执行主看板同时展示 feature ordering / wave grouping / baseline host health，而不是只显示单 run 列表。 |
| AC-103 | run-detail-surface | run detail 至少聚合 `work item metadata / run timeline / workspace root / writable services / retry history / latest evidence refs / operator recommendation`。 |
| AC-104 | minimal-actions | execution board 或 run detail 至少支持 `open run detail / continue / stop / retry / open repair path` 五类最小操作。 |

## Story 3: review 与 recovery surfaces 必须帮助真正闭环

作为验收者，我希望 board 不只是告诉我 run 失败了，而是直接把 review 与 recovery 入口放在同一个 workbench 中，这样我能完成判断和回修闭环。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | review-surface | review surface 至少提供 `diff entrypoint / acceptance evidence entrypoint / related feature-revision-baseline context / qa-release readiness hint`。 |
| AC-202 | recovery-diagnostics | recovery diagnostics 至少覆盖 `stale baseline host / stale mirror / workspace drift / retry orphan / blocked dependency / missing evidence sink`。 |
| AC-203 | diagnostic-guidance | 每类诊断都给出 `reason code / affected feature or run / recommended command or path / whether self-repair is allowed`。 |
| AC-204 | no-silent-failure | 当 run 状态漂移或关键前置条件不满足时，workbench 优先显示诊断与 repair path，而不是继续允许误操作。 |

## Story 4: board launcher 必须是本地可执行启动 contract

作为 Beacon 使用者，我希望 board 能通过正式 launcher 启动，而不是靠临时脚本，这样本地 web console、只读 board 和后续 desktop shell 才能共享一条稳定入口线。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | launcher-command | Beacon 提供正式 `board` 启动 contract，至少覆盖 `beacon board`、`beacon board --open`、`beacon board --host`、`beacon board --port`。 |
| AC-302 | startup-contract | launcher 至少返回 `resolved runtime source / board url or endpoint / mode / readiness status / failure reason`。 |
| AC-303 | local-first | 第一阶段默认交付路径明确为本地 web console first，desktop shell 仅保留扩展位。 |
| AC-304 | public-vs-operator-surface | 只读 public board 与可写 operator workbench 的边界被正式定义，不混成同一权限面。 |

## Story 5: workbench 必须受 runtime kernel 与 truth boundary 约束

作为 Beacon governance owner，我希望 board/workbench 的所有状态和操作都受 runtime kernel 与 truth boundary 约束，这样 UI 不会反客为主成为新的真相源。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | runtime-backed-state | workbench 只消费 runtime kernel 的 read model 和 operator action contract，不自行推导隐式真相。 |
| AC-402 | no-requirement-authority | workbench 不是 requirement 编辑器，也不是 requirement truth source，不直接改写 `prd / user-story / test-case / prototype`。 |
| AC-403 | action-governance | continue / stop / retry / repair 等动作都必须经过 kernel contract，而不是页面绕过后端直接修改状态文件。 |
| AC-404 | status-board-continuity | 现有 `status --board` 继续保留摘要角色，但与 richer workbench 共享同一状态语义，不分叉成两套解释。 |

## Story 6: 软件语义治理必须进入 prototype 与 board 主链

作为 Beacon 产品与治理维护者，我希望 prototype、preview、board 共用同一软件语义合同，这样首屏和操作文案不会继续漂成解释式、评审式或通用 SaaS 话术。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | software-semantic-profile | `ux-prd / page-spec / pages / component catalog / preview / board` 共用同一 `software-semantic-profile`，统一标题、状态、动作、字段、异常句式与禁用词。 |
| AC-502 | no-explanatory-copy-drift | operator-facing 文案不得直接复用 `why / reasoning / review guidance / asset catalog wording`。 |
| AC-503 | terminology-governance | 状态枚举、业务动词、恢复动作、字段约束使用统一术语，不允许混用泛化 SaaS 动词覆盖具体 operator 行为。 |
| AC-504 | semantic-lint-gate | prototype freeze、preview render、board export 前必须执行语义校验；未通过时不得进入可交付状态。 |

## Story 7: 首屏必须先回答恢复判断与下一步动作

作为执行面操作者，我希望 workbench 首屏先告诉我当前状态、阻塞和下一步动作，而不是先看到路径、历史和散乱 run 列表，这样我可以直接执行判断。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-601 | first-screen-priority | 首屏主区优先展示 `当前状态 / 当前阻塞 / 下一步动作 / 恢复路径`。 |
| AC-602 | suppress-artifact-noise | `run 列表 / workspace path / artifact path / 历史时间线 / 机器 trace 明细` 不得抢占首屏主区，只能进入二级展开或详情面。 |
| AC-603 | preview-anti-drift | preview 明确定义为 operator workbench prototype，不得再输出 design asset catalog 型首页。 |
| AC-604 | operator-judgment-over-summary | 首屏目标是支持 operator judgment，不是展示设计摘要、材料索引或路由总览。 |

## Delivery Notes

- 本故事线依赖 `beacon-execution-runtime-kernel` 作为运行态底座。
- 它冻结的是 operator surface 和 launcher contract，不是完整视觉实现完成声明。
- 下一阶段应从本 story 继续生成 test-case，再进入 prototype 或 implement 的具体收口。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 13 |
| Status | draft-operator-surface-r2 |
| Created | 2026-05-01 |
| Change Scope | workbench-ia / execution-board / run-detail / review-surface / recovery-diagnostics / board-launcher / local-first-executable-surface / software-semantic-profile / first-screen-priority / preview-anti-drift |
