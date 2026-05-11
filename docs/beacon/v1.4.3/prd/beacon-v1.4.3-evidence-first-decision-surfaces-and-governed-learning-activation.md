# PRD: Beacon v1.4.3 Evidence-First Decision Surfaces and Governed Learning Activation

**Feature**: `beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation`  
**Version**: `v1.4.3`  
**Date**: `2026-05-11`  
**Status**: `freeze-ready`  
**Track**: `human-surface + decision-protocol + prototype-governance + learning-plane + support-explainability`  
**Scenario**: `version-level-requirement-challenge + design-decision-governance + prototype-de-overloading + learning-default-input`  
**Template**: `main PRD / next-version planning`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Current runtime architecture: `docs/beacon/v1.4.0/execution/architecture-blueprint.md`
- Current runtime/default docs line: `docs/beacon/v1.4.0/SUMMARY.md`
- Test-governance planning line: `docs/beacon/v1.4.2/SUMMARY.md`
- Human-surface benchmark: `docs/analysis/beacon-v1.4.0-human-surface-and-subskill-benchmark-vs-gstack.md`
- Command matrix and prototype gap analysis: `docs/analysis/beacon-v1.4.0-gstack-command-matrix-and-prototype-surface-gap.md`
- Related PRD:
  - `docs/beacon/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
  - `docs/beacon/v1.4.0/prd/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`

## 1. 问题

Beacon 当前已经具备：

- frozen truth
- compiled contract
- implement / qa / release gate
- support surfaces
- learning plane kernel

但仍存在 5 个 evidence-first 缺口：

1. **问题定义挑战不足**
   - `brainstorm` 能发散收敛，但不是公开的 CEO-grade challenge surface。
   - 当前缺少版本级的人类面，去挑战 PRD、story、case 是否在严谨推进错误命题。

2. **设计决策缺口被压给 prototype**
   - `prototype` 目前在实践中容易从 requirement-driven freeze 滑向 UI/UX 决策与交付物语义。
   - 这导致设计判断、产品方向与交接冻结混层。

3. **learning 仍是内核能力，不是默认决策输入**
   - learning 存在，但 skill 不会系统性默认召回相关 learning。
   - 用户也看不见 learning 是否被用、为什么被用、是否过期。

4. **support surface explainability 仍偏薄**
   - `help / status / ask / deep` 还不能稳定解释：
     - 为什么推荐当前 route
     - 为什么不是另一条
     - 当前缺哪层证据
     - 哪些 learning 正在影响当前判断

5. **evidence-first 更强地体现在交付后段，而不是前段**
   - 现状更像“冻结后强治理”
   - 而不是“从问题定义到设计交接全程强证据”

## 2. 目标

本需求的目标是在不扩张主生命周期、不新增公开一级主命令的前提下，为 Beacon 增加一组 host-visible decision surfaces 与 learning governance surfaces，使 evidence-first 不只约束实现、QA、release，也约束：

- 问题定义
- scope 决策
- 设计判断
- prototype 交接
- learning 召回
- route explainability

同时，本总线 PRD 要求在本版本内把需求继续细化为 3 条可独立实施但共享边界的正式子线：

1. `beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface`
2. `beacon-v1.4.3-design-review-surface-and-prototype-governance`
3. `beacon-v1.4.3-governed-learning-recall-and-route-explainability`

## 3. 设计原则

### 3.1 不扩张主生命周期

主生命周期仍保持：

```text
prd
-> user-story
-> test-case
-> prototype? 
-> implement
-> qa
-> release
```

`ceo-review`、`design-review`、`learn` 若进入范围，只能是 support/review surfaces。

### 3.2 不新增第二真相源

- `ceo-review` 不能直接冻结 truth
- `design-review` 不能直接替代 prototype truth
- `learn` 不能直接定义 pass/block/release truth
- explainability 不能替代 gate

### 3.3 先分层，再增强

正确分层应为：

```text
CEO-grade challenge
-> requirement truth
-> design-grade challenge
-> prototype freeze / handoff
-> implement / qa / release
-> learning audit / recall
```

### 3.4 learning 是决策输入，不是决策真相

learning 的正式职责是：

- prior pattern recall
- warning
- stale caution
- route hint
- runner/admission recommendation

learning 的非职责是：

- freeze truth
- gate verdict
- release pass

## 4. 范围

In scope:

- 定义 `beacon-ceo-review` 作为版本级或大 feature 级 requirement challenge surface。
- 定义 `beacon-design-review` 作为 UI/UX 决策与可视化判断 surface。
- 定义 `beacon-learn` 作为 learning audit / prune / visibility surface。
- 定义 `prototype` 去负载原则，明确其与 design review 的边界。
- 定义 `help / status / ask / deep` 的 route explainability 与 learning injection 要求。
- 定义 learning 从 latent kernel 能力进入默认 skill decision protocol 的基本 contract。

Out of scope:

- 新增公开一级主命令。
- 让 `ceo-review`、`design-review`、`learn` 成为新的 lifecycle stages。
- 让 `prototype` 直接升级为 UI generator 或设计系统定稿器。
- 让 learning 自动改写 PRD、story、case 或 release verdict。
- 在本轮直接把 `prototype` 从全局边界移除。

## 5. 功能需求

- FR-001: Beacon must expose `beacon-ceo-review`, `beacon-design-review`, and `beacon-learn` as host-visible support surfaces without expanding the public lifecycle.
- FR-002: `ceo-review` must challenge requirement direction and emit explicit strategic judgments that route back into canonical truth surfaces.
- FR-003: `design-review` must own UI/UX direction challenge while `prototype` remains conditional handoff freeze when triggered.
- FR-004: governed learning must become a default decision input with visibility, downgrade, and audit behavior.
- FR-005: `help / status / ask / deep` must explain route recommendation, evidence gap, and learning influence in human-readable form.

## 6. 产品模型

### Evidence-First Decision Chain

```text
problem signal
-> ceo-review challenge
-> prd / user-story / test-case truth
-> design-review challenge
-> prototype freeze when UX/UI handoff is real
-> implement
-> qa
-> release
-> learning audit / prune / reuse
-> next run injection
```

### New Host-Visible Surfaces

| Surface | Role | Boundary |
| --- | --- | --- |
| `beacon-ceo-review` | 问题定义、scope、承诺面、版本级 challenge | support/review only |
| `beacon-design-review` | UI/UX 决策、状态层次、交互一致性 challenge | support/review only |
| `beacon-learn` | learning 可见性、审计、修剪、冲突/过期治理 | support/governance only |

### Subfeature Decomposition

| 子线 | 主要职责 | 主要约束 |
| --- | --- | --- |
| `ceo-review` | 版本级问题定义挑战、scope judgment、承诺面挑战 | 不能直接冻结 truth |
| `design-review + prototype-governance` | UI/UX 决策挑战、prototype 去负载、handoff 边界 | `design-review` 不替代 `prototype truth` |
| `learn + route-explainability` | learning recall、可见性、降级/修剪、support-surface explainability | learning 不能定义 gate/release truth |

### Prototype De-Overloading

`prototype` 若被触发，应只负责：

- requirement-driven wireframe freeze
- route/state/interaction handoff
- UX contract projection

它不再承担：

- 产品战略 challenge
- 设计方向定稿
- 最终 UI 交付物裁决

## 7. Functional Requirements

- FR-001: Beacon must define a host-visible `ceo-review` support surface for version-level or major-feature requirement challenge.
- FR-002: `ceo-review` must support explicit strategic judgments such as `expand`, `hold`, `reduce`, and problem-reframe.
- FR-003: `ceo-review` must route accepted changes back through existing `prd / change / user-story / test-case` truth surfaces instead of freezing truth directly.
- FR-004: Beacon must define a host-visible `design-review` support surface for UI/UX decision challenge before prototype freeze or implementation.
- FR-005: `design-review` must evaluate page hierarchy, state clarity, interaction coherence, and evidence sufficiency for UI/UX direction.
- FR-006: Beacon must redefine `prototype` as a de-overloaded freeze/handoff surface and explicitly forbid it from becoming the default design-decision owner.
- FR-007: Beacon must define a host-visible `learn` surface for learning visibility, audit, staleness handling, pruning, and conflict display.
- FR-008: Core skills must support learning injection by default using a progressive disclosure model rather than requiring manual lookup.
- FR-009: Learning injection must be visible to the operator through `prior learning applied`-style explanation including confidence/staleness context.
- FR-010: `help / status / ask / deep` must explain route recommendation, evidence gaps, and learning influence in human-readable form.
- FR-011: Learning must remain advisory and must not define freeze, gate, or release truth by itself.
- FR-012: `ceo-review`, `design-review`, and `learn` must strengthen evidence-first positioning rather than widen the public lifecycle.

## 风险与缓解

- 风险：新 surface 增加后，用户把它们误认为新的主生命周期阶段。
  - 缓解：所有 surface 都保持 support/review 属性，并继续通过既有 truth/gate surface 完成正式动作。
- 风险：learning 虽进入默认决策路径，但若不可审计会削弱 evidence-first。
  - 缓解：强制提供 learning visibility、staleness/conflict downgrade 和 route explainability。

## 恢复策略

- 当 `ceo-review`、`design-review` 或 `learn` 输出与冻结 truth 冲突时，恢复到 canonical truth surface，由 `change / prd / user-story / test-case` 承接正式修订。
- 当 learning 注入造成 route ambiguity 或 evidence gap 放大时，恢复到无 learning override 的默认 route，并显式显示 caution。

## 8. 验收标准

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | ceo-surface | Beacon defines `beacon-ceo-review` as a support/review surface for version-level or major-feature requirement challenge. |
| AC-002 | scope-judgment | `beacon-ceo-review` supports explicit `expand / hold / reduce / reframe` strategic outputs. |
| AC-003 | truth-routing | `ceo-review` routes accepted changes back to existing truth surfaces and does not directly freeze truth. |
| AC-004 | design-surface | Beacon defines `beacon-design-review` as a support/review surface for UI/UX decision challenge. |
| AC-005 | design-boundary | `design-review` owns UI/UX direction challenge while `prototype` remains formal freeze/handoff when triggered. |
| AC-006 | prototype-de-overloading | Beacon explicitly forbids `prototype` from defaulting into strategic product challenge, design final approval, or deliverable-semantic overload. |
| AC-007 | learn-surface | Beacon defines `beacon-learn` as a visible learning governance surface. |
| AC-008 | learning-injection | Core decision surfaces can inject relevant learning by default through a governed progressive-disclosure contract. |
| AC-009 | learning-visibility | When learning is applied, the operator can see which learning influenced the current route or judgment and its confidence/staleness state. |
| AC-010 | stale-conflict | Stale or conflicting learning is downgraded or flagged, not silently trusted. |
| AC-011 | route-explainability | `help / status / ask / deep` explain route recommendation, evidence gap, and learning influence in human-readable form. |
| AC-012 | boundary-safety | None of the new surfaces become a second truth root, second gate truth, or new public lifecycle stage. |

## 8. Non-Goals

- Not adding a new public primary command.
- Not turning Beacon into a software-factory persona suite.
- Not replacing `prd / user-story / test-case` with `ceo-review`.
- Not replacing `prototype` with `design-review` in this version line.
- Not introducing cross-model review, deploy orchestration, or design generation as the main v1.4.3 scope.

## State Axes

- `requirement_governance_state`: `unreviewed -> ceo_challenged -> truth_routed -> freeze_ready`
- `design_governance_state`: `undifferentiated -> design_reviewed -> prototype_condition_decided -> handoff_ready`
- `learning_governance_state`: `latent -> recalled -> disclosed -> audited -> pruned_or_retained`
- `support_explainability_state`: `implicit -> visible -> route_explained -> evidence_first`

## 9. Diagram Truth

- `branch-flow`
  - `problem signal -> ceo-review -> prd/story/case truth -> design-review -> prototype_when_triggered -> implement -> qa -> release`
  - `learning note -> learn audit -> skill-specific injection -> next run decision`
- `decision-priority`
  - `frozen truth > compiled contract > gate verdict > ceo/design review outputs > learning hints`
  - `design-review direction > prototype freeze packaging`
  - `learning visibility > hidden heuristic reuse`
- `state-machine`
  - `learning_state: latent -> readable -> injected -> audited`
  - `prototype_state: overloaded -> clarified -> governed -> handoff_only`
  - `human_surface_state: thin -> reviewable -> explainable -> evidence_first`
