# User Story: Beacon v1.4.1 Deep Analysis Support Surface and Risk Closure

## Story Boundary

- version: `v1.4.1`
- feature: `beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure`
- status: `freeze-ready`
- upstream_prd: `docs/beacon/v1.4.1/prd/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- research_supplement: `docs/beacon/v1.4.1/research/beacon-deep-capability-upgrade-research-supplement.md`
- current_revision: `R1`
- source_revision: `R0`

本故事线覆盖 Beacon `v1.4.1` 的 `beacon-deep` 支持面能力。目标是在不扩张 `prd -> user-story -> test-case -> implement -> qa -> release` 主生命周期的前提下，提供一个可多轮但默认一次闭环的 deep loop，用于发现复杂业务的流程、功能、状态机、事实源、一致性和 release 风险缺口，并把被接受的缺口路由回既有 Beacon surface。

## Diagram Truth

- `branch-flow`
  - `prd / user-story / test-case / implement evidence / qa evidence / release evidence -> beacon-deep -> deep loop trace -> route decision -> existing Beacon surface`
  - `deep finding -> PRD gap -> change/refreeze -> implement repair -> supplemental QA -> release closure`
  - `deep finding -> test gap -> test-case delta -> QA execution -> closure brief`
  - `low-risk feature -> explicit skip reason -> release evidence`
- `state-machine`
  - `not_started -> scanning -> modeling -> challenging -> deriving_delta -> routing -> verifying -> closed`
  - `finding_candidate -> classified -> routed -> closed`
  - `delta_proposed -> adopted -> executed -> closed`
  - `risk_open -> waived | backlog | blocked | closed`
- `decision-priority`
  - `global boundaries > frozen truth > accepted change/refreeze > deep finding > learning hint`
  - `one support skill > many public lifecycle stages`
  - `one-pass closure > infinite loop`
  - `route decision > orphan analysis`

## US-001: `beacon-deep` 是支持面人类 skill

作为 Beacon 操作者，我希望 `deep` 以 `beacon-deep` 支持 skill 和 `beacon deep run` 支持命令暴露，而不是加入主生命周期，这样我可以在复杂业务风险上获得深度分析，同时不破坏主流程心智。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | support-skill-boundary | `beacon-deep` 被定义为 support skill / toolkit surface，而不是 `prd / user-story / test-case / implement / qa / release` 之外的新主阶段。 |
| AC-002 | public-entry | `beacon deep run` 是推荐公共入口，能够代表 scan、model、challenge、derive、route、verify 的完整 deep loop。 |
| AC-003 | hidden-toolkit | `beacon-toolkit-deep-loop`、`beacon-toolkit-state-machine`、`beacon-toolkit-test-delta`、`beacon-toolkit-risk-register` 可以作为内部模块存在，但默认不增加人类主入口。 |

## US-002: Deep trigger 与 skip 语义必须稳定

作为 requirement owner，我希望 Beacon 能判断哪些复杂功能需要 deep，哪些低风险功能可以显式跳过，这样 deep 不会变成默认流程负担，也不会漏掉高风险业务模型。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-004 | high-risk-trigger | payment、order、wallet、ranking、scoring、identity binding、invitation、relationship chain、reporting、migration、multi-role、multi-state、post-fact attribution 等高风险类别会触发 deep required 或 recommended 诊断。 |
| AC-005 | skip-reason | 低风险静态页面、简单表单、stateless utility、visual-only change 和低风险配置变更可以显式记录 skip reason。 |
| AC-006 | qa-trigger | QA 中出现由业务建模缺失导致的 P0/P1/P2 缺陷时，可以重新触发 deep loop 作为结构性风险复盘。 |

## US-003: Deep loop 必须默认一次闭环

作为交付 owner，我希望 `deep run` 对同一用户意图尽最大可能一次闭环，这样 deep 能提高交付质量，而不是把团队拖入无限分析。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-007 | loop-state-machine | deep loop 至少覆盖 `scan_truth -> model_business -> challenge_gaps -> derive_delta -> classify_findings -> route_repairs -> verify_closure`。 |
| AC-008 | one-pass-closure | 同一用户意图下，没有新增角色、实体、业务流程、状态机、事实源或跨面不变量时，deep run 应在同一 run 内给出 closure 或 route decision。 |
| AC-009 | reopen-conditions | 只有用户新增 feature、role、state machine、business process、release-blocking evidence，或 QA/implementation evidence 暴露结构性缺口时，才开启新的 deep loop。 |

## US-004: Deep artifacts 必须可审计

作为 release reviewer，我希望 deep 产物形成稳定 artifact family，这样 release 可以审计 deep 是否真的闭环，而不是只看到口头分析。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-010 | artifact-family | deep artifact family 包含 deep analysis report、state machine report、deep test delta、risk register、deep loop trace、deep closure brief。 |
| AC-011 | loop-trace-required | deep loop trace 必须记录 user intent snapshot、iteration list、finding classification、route decision、closure decision、stop reason 和 next allowed route。 |
| AC-012 | closure-brief-required | deep closure brief 必须记录 deep requirement state、verdict、executed delta cases、open findings、waived findings、accepted backlog risks 和 release recommendation。 |

## US-005: Deep findings 必须路由回既有 Beacon surface

作为 Beacon governance owner，我希望 deep finding 被分类并路由，而不是停留在分析文档中，这样所有缺口都能进入已治理的 PRD、用户故事、测试、实现、QA 或 release 路线。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-013 | route-map | PRD gap 路由到 `change/refreeze`，user-story gap 路由到 user-story supplement 或 `change/refreeze`，acceptance gap 路由到 test-case delta。 |
| AC-014 | implementation-qa-route | implementation gap 路由到 implement repair handoff，QA evidence gap 路由到 supplemental QA loop。 |
| AC-015 | release-route | release risk 路由到 release closure、waiver 或 backlog decision。 |
| AC-016 | no-orphan-finding | 每个 deep finding 必须有 classification、route decision、closure decision 或 backlog decision。 |

## US-006: Deep test delta 是 QA 前置演进面

作为 QA owner，我希望 deep 可以在 QA 前生成 test-case delta，并在 QA 后消费结构性缺陷，这样测试用例能多轮演进，但仍由 `qa` 执行验收。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-017 | pre-qa-delta | deep 可以从 PRD、用户故事、状态机、事实源图和现有 test-case 中派生缺失测试，形成 deep test delta。 |
| AC-018 | qa-execution-boundary | deep 不直接替代 QA 执行，adopted deep delta 必须进入 test-case 或 supplemental QA 后由 `qa` 验收。 |
| AC-019 | qa-feedback-loop | QA 缺陷只有在指向结构性状态、事实源、一致性或需求缺口时才重新进入 deep loop。 |

## US-007: Release 必须消费 deep closure 或 skip evidence

作为 release owner，我希望高风险 feature 在 release 前能看到 deep closure、waiver、backlog 或 skip evidence，这样 release 判断不会只依赖已知 acceptance 的 happy path。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-020 | release-supplement | release 可以消费 deep closure brief、risk register、deep loop trace 和 explicit skip reason 作为补充证据。 |
| AC-021 | blocking-findings | P0/P1/P2 release-blocking deep findings 必须 closed 或 waived 后才允许 release readiness 通过。 |
| AC-022 | backlog-is-explicit | backlog findings 不默认阻断 release，但必须有 accepted backlog decision。 |

## US-008: Truth governance 必须保持 canonical-first

作为 Beacon 架构 owner，我希望 deep finding 不能直接改写 frozen truth，而是通过 human acceptance 和 change/refreeze 收敛，这样 deep 增强不会制造第二真相源。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-023 | no-direct-truth-write | deep artifacts、machine mirrors、runtime projections 和 learning hints 都不得直接改写 frozen PRD、user-story 或 test-case truth。 |
| AC-024 | accepted-change-route | 被接受的 requirement gap 必须通过 `change/refreeze` 更新 canonical truth，然后再进入 implement、QA 和 release。 |
| AC-025 | projection-not-truth | `.machine` 和 `.beacon` 产物只能作为 compiled projection、cache 或 audit evidence，不能成为第二 truth root。 |

## US-009: v1.4.1 三件套必须冻结后进入待实现阶段

作为 implementation owner，我希望 `v1.4.1` 的 PRD、user-story 和 test-case 三件套可以冻结为实现基线，这样后续 `implement` 能以稳定 contract 开始，而不是继续在 requirement 阶段漂移。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-026 | three-piece-freeze | PRD、user-story、test-case 三件套均存在并通过 Beacon 校验后，可以生成 frozen revision baseline。 |
| AC-027 | implement-ready-boundary | 冻结后的状态是 requirement-frozen / implement-pending，不代表实现完成，也不代表 QA 通过。 |
| AC-028 | version-safety | v1.4.1 仍为 planning-only line，冻结 requirement package 不改变当前 runtime release line、docs default line 或 package version。 |

## Delivery Notes

- 本 story package 冻结的是 v1.4.1 deep capability 的 requirement baseline。
- 本 feature 不要求 prototype 作为进入 implement 的前置条件，因为核心交付是 CLI / skill / support toolkit / gate supplement surface，而不是 UI handoff。
- 后续 implementation 必须继续遵守 `implement` 唯一实现入口、`qa` 唯一验收入口、`gate` 最终阻断入口。

## Freeze Deliverables

- `docs/beacon/v1.4.1/prd/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- `docs/beacon/v1.4.1/user-story/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- `docs/beacon/v1.4.1/qa/test-cases/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
