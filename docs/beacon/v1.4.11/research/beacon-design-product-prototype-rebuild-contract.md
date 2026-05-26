# Research Closure: Beacon Design / Product / Prototype Rebuild Contract

**Feature candidate**: `beacon-design-product-prototype-rebuild-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`  
**Source surfaces**:

- `docs/beacon/v1.4.11/research/friction-cd1809c3220a-ui-ux-design-truth-writeback-incident.md`
- `docs/beacon/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`
- `docs/beacon/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`
- `docs/brainstorms/2026-05-26-beacon-brainstorm-v1.4.11-beacon-prototype-design-complete-rebuild-distill-ui-ux-dev-into-built-in.md`

## Support Findings

### Brainstorm

#### Round 2026-05-26-ui-ux-dev-upstream-route-delta

- source_skill: `beacon-brainstorm`
- round_id: `2026-05-26-ui-ux-dev-upstream-route-delta`
- material_effect: `accepted_requirement_delta`
- adoption_status: `adopted_into_refreeze_delta`
- route_decision: expand `$beacon:beacon-design` requirement scope through `beacon-change-refreeze`
- finding_summary: `ui-ux-dev` is not a single design engine. It is a stable UI/UX intent router backed by four upstream open-source capability sources: `vibe-to-ui`, `ui-ux-pro-max`, `impeccable`, and `awesome-design-md`. Therefore `$beacon:beacon-design` must preserve those capability boundaries through stable support routes while adding Beacon truth binding, accepted UI/UX writeback, and downstream fail-closed behavior.
- adopted_delta: AC-015 is expanded and AC-016 through AC-020 are added to cover `explore`, `system`, `review`, `polish`, `extract`, `library`, and `bootstrap` route coverage.
- boundary: `beacon-design` remains support-only. Upstream design skills are not Beacon truth sources, not gates, not lifecycle stages, and `awesome-design-md` remains reference-only.

## 1. 结论

原来的 Phase 7 `prototype-legacy-inspector-split-contract` 太小，只能把旧 wireframe 降级为 migration input。

现在根据 `friction:cd1809c3220a`，真正问题更大：

```text
Beacon 没有自己的可审计 design/product truth intake。
外部 ui-ux-dev 结果被人验收后，没有稳定写回 Beacon truth。
所以 implement / QA 越严格，越会按旧 truth 把正确 UI/UX 回滚掉。
```

因此这一刀应从“小清理 prototype legacy”升级为一个完整 feature：

```text
重建 Beacon design / product / prototype 能力边界。
把 ui-ux-dev 的经验蒸馏成 Beacon 内置基础设计能力。
用版本级 design style contract、PRODUCT.md、DESIGN.md 和 versioned requirements 承接设计真相。
让 prototype 从旧 wireframe 生成器退场，变成 accepted design truth adapter。
```

## 2. 大白话目标

Beacon 以后不能只会写 PRD、user story、test case。

对于真实产品，很多需求不是一句功能描述，而是：

- 页面应该长什么样。
- 信息层级怎么排。
- 状态怎么展示。
- 组件怎么选。
- 用户什么时候看到什么反馈。
- 哪些 UI 行为其实代表产品能力。

这些如果不进 truth，后续实现和 QA 就会拿旧文档当圣旨。

所以 Beacon 需要内置一套基础 design 能力，不是为了替代专业设计工具，而是为了让产品设计事实能被 Beacon 管起来。

## 3. 事故约束

来自 `friction:cd1809c3220a` 的硬约束：

```text
accepted UI/UX facts 必须进入 Beacon 可审计 truth；
如果没有写回 truth，implement / QA / release 必须停住。
```

这意味着：

- `ui-ux-dev` 可以继续作为强设计执行器。
- Beacon 不能盲目依赖 `ui-ux-dev` 的运行上下文。
- 被接受的 UI/UX 结果必须写入 Beacon truth binding。
- 没有 binding 时，后续自动化必须 fail closed。

## 4. 当前问题

### 4.1 `beacon design` 太弱

当前 `beacon/commands/design.py` 只是 Design Thinking 模板生成器。

它不能表达：

- 产品定位。
- 页面信息架构。
- 组件系统。
- 状态矩阵。
- 交互契约。
- 设计验收边界。
- open-source component design choice。
- design facts 到 PRD / user-story / test-case 的绑定。

它是文档模板，不是 Beacon 设计能力。

### 4.2 `beacon prototype` 职责混乱

当前 prototype 同时背了三类职责：

- v1.4.8- 的 legacy wireframe bundle。
- v1.4.9+ 的 design-result adapter。
- 旧 bundle status / list / preview / gate compatibility。

这导致两个问题：

- legacy wireframe 仍容易被看成 current closure。
- accepted UI/UX result 没有被强制写入 product/design/requirement truth。

### 4.3 `PRODUCT.md` / `DESIGN.md` 缺位

事故中明确出现了 project-level truth 缺口：

- `PRODUCT.md` 没记录新的产品事实。
- `DESIGN.md` 没记录新的设计事实。
- PRD / user-story / test-case 没同步。

Beacon 当前主要围绕 `docs/beacon/<version>/` 工作，但对 project-level product/design truth 没有稳定协议。

### 4.4 外部设计能力没有蒸馏成内置能力

`ui-ux-dev` 代表一套更完整的设计工作方式：

- 组件库意识。
- 视觉基线。
- 状态覆盖。
- 页面层级。
- 交互反馈。
- 设计 review / polish。
- accepted design result handoff。

Beacon 现在只是把它当外部结果来源，没有把其中“可固化的基本流程”下沉成确定性 design/product contract。

### 4.5 `ui-ux-dev` 的四个上游能力没有进入 Beacon design 边界

`ui-ux-dev` 本身不是单体设计引擎，而是一个意图路由壳。

它的能力来自四个上游开源来源：

| 上游能力 | `ui-ux-dev` 意图 | Beacon design 必须保留的能力 |
| --- | --- | --- |
| `vibe-to-ui` | `explore`, `extract` | 设计方向探索、页面结构、截图/参考提取 |
| `ui-ux-pro-max` | `system` | 设计系统、组件规则、token、技术栈约束 |
| `impeccable` | `review`, `polish` | UX 评审、可用性硬化、发版前打磨 |
| `awesome-design-md` | `library` | 设计参考库，只能 reference-only |

因此 `$beacon:beacon-design` 不能只提供“component-system planning”。

它必须明确拥有七个稳定子入口：

- `beacon-design-explore`
- `beacon-design-system`
- `beacon-design-review`
- `beacon-design-polish`
- `beacon-design-extract`
- `beacon-design-library`
- `beacon-design-bootstrap`

但这些子入口仍然是 support surface。它们不能成为 truth source、gate 或 lifecycle stage。

## 5. Architecture

本节定义 Beacon design / product / prototype 重建后的目标架构。

### 5.1 新的职责切分

```text
beacon design
  -> 生成 / 维护 version-wide design style truth draft
  -> 内置基础 open-source component design guidance
  -> 通过 explore/system/review/polish/extract/library/bootstrap 子入口保留 ui-ux-dev 上游能力
  -> 产出版本级 design style contract、PRODUCT.md、DESIGN.md 候选更新

beacon prototype
  -> accepted design result adapter
  -> 绑定 accepted design facts 到 Beacon truth refs
  -> 不再作为 v1.4.11+ 默认 wireframe 生成器

beacon change/refreeze
  -> 当设计事实改变承诺面时，正式刷新 PRD / user-story / test-case

beacon implement / qa / release
  -> 发现 accepted design facts 未绑定时 fail closed
```

### 5.2 推荐文件结构

```text
PRODUCT.md
DESIGN.md
docs/beacon/<version>/design/style.md
docs/beacon/<version>/design/component-system.md
docs/beacon/<version>/design/interaction-contract.md
docs/beacon/<version>/design/state-matrix.md
docs/beacon/<version>/prototype-adapter/<feature>/design-result-binding.json
docs/beacon/<version>/prototype-adapter/<feature>/design-result-binding.md
docs/beacon/<version>/.machine/design/<feature>.projection.json
```

其中：

- `PRODUCT.md`: project-level product truth，记录产品定位、核心能力、长期体验基线。
- `DESIGN.md`: project-level design truth，记录全局视觉、组件、交互、状态规范。
- `docs/beacon/<version>/design/style.md`: version-wide design style contract，贯穿整个版本，不归属于单个 feature。
- `docs/beacon/<version>/design/component-system.md`: version-wide open-source component system contract。
- `docs/beacon/<version>/design/interaction-contract.md`: version-wide interaction and handoff contract。
- `docs/beacon/<version>/design/state-matrix.md`: version-wide UI state coverage contract。
- `.machine/design/*`: projection，不是 truth。

### 5.3 open-source component design baseline

Beacon 内置设计能力不应是“画漂亮图”，而应是可审计的基础设计系统选择。

最低能力：

- 识别项目技术栈和可用开源组件库。
- 生成组件选型建议，例如 Ant Design、shadcn/ui、MUI、Radix、Headless UI、Tailwind UI 风格约束等。
- 输出页面级 component map。
- 输出状态矩阵。
- 输出交互 handoff。
- 输出 responsive / accessibility baseline。
- 输出 visual density / spacing / typography baseline。

产物要能进入 `DESIGN.md` / `docs/beacon/<version>/design/*.md`，而不是停留在 AI 临时回答里。

### 5.4 Beacon design 子入口与上游能力映射

```text
beacon-design-explore
  -> preserves vibe-to-ui exploration capability
  -> produces concept directions and candidate design truth deltas

beacon-design-extract
  -> preserves vibe-to-ui extraction capability
  -> separates visible facts from inferred interaction assumptions

beacon-design-system
  -> preserves ui-ux-pro-max system capability
  -> produces stack-aware component, token, state, responsive, accessibility baseline

beacon-design-review
  -> preserves impeccable review capability
  -> produces prioritized UX findings and accepted-design candidate deltas

beacon-design-polish
  -> preserves impeccable polish capability
  -> separates support-only polish from promise-changing design facts

beacon-design-library
  -> preserves awesome-design-md reference capability
  -> remains reference-only and cannot produce execution truth by itself

beacon-design-bootstrap
  -> validates installed skill, mirrored source, or bootstrap route
  -> remains capability admission evidence, not release truth
```

## 6. Business Flow

本节定义有 UI/UX 影响时，设计事实如何进入 Beacon truth 并解锁后续执行。

### 6.1 有 UI/UX 影响时

```text
prd / user-story / test-case
  -> design requirement detected
  -> beacon design plan
  -> optional beacon-design explore/system/library/extract/review/polish/bootstrap routes
  -> design/style.md + component-system + interaction-contract + state-matrix
  -> optional external ui-ux-dev execution
  -> accepted design result
  -> beacon prototype adapt
  -> change/refreeze if requirement truth changed
  -> implement
  -> qa
  -> release
```

### 6.2 accepted UI/UX result 写回

```text
accepted design result
  -> accepted design ledger
  -> affected truth refs computed
  -> PRODUCT.md / DESIGN.md participation checked
  -> PRD / user-story / test-case impact checked
  -> prototype adapter binding written
  -> if requirement changed: route to change/refreeze
```

### 6.3 fail closed

```text
accepted design result exists
  -> no binding
  -> no PRODUCT / DESIGN update when required
  -> no PRD / user-story / test-case update when required
  -> implement / QA / release requested
  -> block with accepted_ui_ux_truth_gap
```

## 7. State Machine

```text
design_unseen
  -> design_required
  -> design_contract_drafted
  -> design_result_produced
  -> design_result_accepted
  -> design_truth_binding_required
  -> design_truth_bound
  -> requirement_refreeze_required
  -> requirement_refrozen
  -> implementation_allowed
```

Blocked states:

- `design_result_accepted -> implementation_allowed` without binding.
- `design_truth_bound -> implementation_allowed` when PRD / user-story / test-case are stale.
- `legacy_wireframe_present -> implementation_allowed` for v1.4.11+ current design closure.

Terminal states:

- `implementation_allowed`: design/product truth and requirement truth agree.
- `blocked_accepted_ui_ux_truth_gap`: accepted design facts exist but are unbound.
- `blocked_requirement_truth_stale`: design facts affect requirements but change/refreeze is missing.
- `legacy_migration_input_only`: old wireframe can be inspected but cannot satisfy current design closure.

## 8. Decision Priority

When rules conflict:

1. Human-accepted design facts cannot be silently ignored.
2. Beacon Markdown truth must be updated before execution trusts it.
3. `PRODUCT.md` / `DESIGN.md` participate when design facts affect product or visual baseline.
4. PRD / user-story / test-case must update when design facts change promise, behavior, AC, or QA coverage.
5. `prototype adapt` records accepted design result binding; it does not bypass change/refreeze.
6. legacy wireframe is inspection / migration input only.
7. open-source component design guidance must remain auditable and deterministic enough for tests.
8. `ui-ux-dev` remains optional external execution power, not canonical truth.

## 8.1 Version Projection Truth Binding

- `prd_refs`: `docs/beacon/v1.4.11/prd/beacon-design-product-prototype-rebuild-contract.md`
- `user_story_refs`: `docs/beacon/v1.4.11/user-story/beacon-design-product-prototype-rebuild-contract.md`
- `test_case_refs`: `docs/beacon/v1.4.11/qa/test-cases/beacon-design-product-prototype-rebuild-contract.md`
- `coverage_notes`: PRD AC-001 through AC-020 are projected into user-story ACs and test-case rows TC-DESIGN-REBUILD-001 through TC-DESIGN-REBUILD-020.
- `out_of_scope_notes`: browser fallback rename, memory migration, intent routing, test marker relayering, and full `ui-ux-dev` embedding are explicitly excluded from this feature.

## 9. Ordered Sub-Contracts Inside One Freezeable Feature

This is one freezeable feature, not five unrelated features.

The feature must implement the following ordered sub-contracts. Each sub-contract has its own acceptance evidence, but the requirement package is frozen as one complete design capability feature:

```text
beacon-design-product-prototype-rebuild-contract
  1. beacon-design-product-truth-contract
  2. beacon-design-component-system-contract
  3. accepted-ui-ux-truth-writeback-gate-contract
  4. beacon-prototype-adapter-rebuild-contract
  5. beacon-design-subskill-contract
```

### 9.1 `beacon-design-product-truth-contract`

Goal:

- Introduce `PRODUCT.md`, `DESIGN.md`, and version-wide `docs/beacon/<version>/design/style.md` participation.
- Define what product/design truth means.
- Add deterministic design/product material validation.

Acceptance sketch:

- design/product/style truth paths are discoverable.
- missing required design truth blocks UI/UX features.
- `.machine/design` is projection only.
- no implementation/QA uses accepted design facts without truth refs.

### 9.2 `beacon-design-component-system-contract`

Goal:

- Distill basic `ui-ux-dev` design method into Beacon-owned deterministic design guidance.
- Add component system selection for open-source UI libraries.
- Produce component map / state matrix / interaction contract.

Acceptance sketch:

- `beacon design` is no longer only Design Thinking template.
- component library candidates are explicit and source-bound.
- generated design contract includes page, component, state, interaction, accessibility, responsive axes.
- output can be reviewed and bound to requirements.

### 9.3 `accepted-ui-ux-truth-writeback-gate-contract`

Goal:

- Add accepted UI/UX result ledger and fail-closed gate.
- Consume prototype adapter binding.
- Block implement / QA / release when accepted design facts are unbound.

Acceptance sketch:

- implement blocks on `accepted_ui_ux_truth_gap`.
- QA blocks rather than validating stale UI truth.
- release treats unbound accepted UI/UX facts as P0 blocker.
- status/help show repair commands.

### 9.4 `beacon-prototype-adapter-rebuild-contract`

Goal:

- Rebuild prototype as accepted design truth adapter.
- Remove v1.4.11+ wireframe-generation main path.
- Move legacy wireframe inspection behind explicit compat inspector.

Acceptance sketch:

- current `prototype status` reports adapter binding state by default.
- legacy wireframe appears only with `--include-legacy` or compat inspector.
- `legacy_source_only` is retired in favor of `migration_input_present`.
- legacy source cannot satisfy current prototype gate.

### 9.5 `beacon-design-subskill-contract`

Goal:

- Add a Beacon design child skill distinct from design-review.
- This skill routes design/product truth drafting, component design planning, upstream-inspired exploration, review, polish, extraction, reference lookup, and bootstrap checks.

Acceptance sketch:

- `$beacon:beacon-design` exists.
- It does not become a gate or truth source by itself.
- It routes accepted scope to `beacon-change`, `beacon-prototype`, or `beacon-test-case`.
- It references deterministic CLI/tooling, not only prompt instructions.
- It exposes stable intent routes: `explore`, `system`, `review`, `polish`, `extract`, `library`, and `bootstrap`.
- It preserves `vibe-to-ui`, `ui-ux-pro-max`, `impeccable`, and `awesome-design-md` capability ownership without hiding their boundary differences.
- `awesome-design-md` remains reference-only.
- `beacon-design-bootstrap` validates installed skills, mirrored sources, or bootstrap routes without becoming truth/gate evidence.

## 10. What This Replaces

Replaced or downgraded:

- `beacon design create` as a generic Design Thinking doc generator.
- v1.4.11+ `prototype plan/create` as current native wireframe generation.
- `legacy_source_only` as current status.
- implicit assumption that old Markdown truth is enough after accepted UI/UX changes.

Preserved:

- historical prototype bundle inspection.
- external `ui-ux-dev` as optional high-power design execution.
- current Beacon main chain.
- requirement truth authority under Markdown.
- `.machine` projections and runtime evidence.

## 11. Non Goals

- Do not embed all of `ui-ux-dev` implementation into Beacon.
- Do not turn design support into a new required lifecycle stage for every feature.
- Do not let AI-generated design overwrite PRODUCT / DESIGN / PRD automatically.
- Do not remove legacy prototype artifacts immediately.
- Do not combine browser fallback, memory migration, intent routing, and test marker restructuring in this same feature.
- Do not make design screenshots or polish notes release truth by themselves.

## 12. Recommended Immediate Route

Do not proceed with the small `prototype-legacy-inspector-split-contract` as the next frozen feature.

Recommended next formal route:

```bash
beacon change "beacon-design-product-prototype-rebuild-contract" \
  --project . \
  --version v1.4.11 \
  --reason "freeze full Beacon design/product/prototype rebuild with ordered design capability sub-contracts" \
  --refreeze-chain
```

The frozen feature contains this execution order:

```text
1. beacon-design-product-truth-contract
2. beacon-design-component-system-contract
3. accepted-ui-ux-truth-writeback-gate-contract
4. beacon-prototype-adapter-rebuild-contract
5. beacon-design-subskill-contract
```

Reason:

```text
先有 product/design truth surface，
再有 component design capability，
再有 accepted UI/UX truth gap gate，
最后重建 prototype 和 skill surface。
```

If prototype is rebuilt first without product/design truth, Beacon still has nowhere stable to write accepted UI/UX facts.
