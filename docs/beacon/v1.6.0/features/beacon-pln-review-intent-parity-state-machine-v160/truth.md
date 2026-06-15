---
slug: beacon-pln-review-intent-parity-state-machine-v160
version: v1.6.0
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md
  user_story: docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md
  test_case: docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# 需求真相：Beacon Planner Review Intent Parity State Machine v1.6.0

## 概述

`beacon-pln-review-intent-parity-state-machine-v160` 定义 Beacon v1.6.0 planner 面的下一轮收敛：新增一个 host-visible `beacon-pln-review` 作为多角度 planner review 入口，同时把过细 planner 公开面收敛为内部 reviewer catalog。

这个 feature 的核心目标不是“多加一个 skill”，而是防止 Beacon 在 `plan -> truth` 过程中把用户真实意图、source parity 和有限状态机闭环压缩成最小 MVP 骨架。Planner review 必须在不写 truth、不实现、不验收的边界内，系统产出可路由的 support advisory，帮助后续 `beacon-gen-truth` / `beacon-gen-change` 把真实意图落到 package truth。

## 背景

Beacon 当前具备强 truth/evidence/gate 闭环，但 plan 层有三类缺口：

- 当用户说“完整复刻”“同等能力”“做全”或引用成熟 source 项目时，planner/generator 可能把意图收缩为“最小可验收 MVP 骨架”。
- planner public skill 面过宽，`founder`、`security`、`performance`、`doubt`、`context`、`simplify`、`adr`、`design`、`deep` 等能力直接出现在 host autocomplete 中，增加路由负担。
- 原有 business flow / state-machine / diagram truth 能力仍存在于 support references、legacy truth templates 和 `requirement_clarity` gate，但在 v1.6.0 package-authoritative truth 中没有重新作为 planner review 的一等落点表达清楚。

本 feature 接受 Compound Engineering skill 写法中的 `thin SKILL.md + references/persona-catalog + structured findings + synthesis` 模式，也接受 `qi-dev-skill-creator` 的 skill package 标准：入口精简、progressive disclosure、直接引用 references、metadata/eval/benchmark 可验证。

## 范围

### In Scope

- 新增 host-visible planner skill：`beacon-pln-review`。
- 将 v1.6.0 planner public surface 收敛为少量入口：`beacon-pln-brainstorm`、`beacon-pln-source`、`beacon-pln-review`、`beacon-pln-friction`。
- 将过细 planner 能力降级为 `beacon-pln-review` 的内部 reviewer，而不是继续作为默认 host-visible public skills。
- 建立内部 reviewer catalog，覆盖 intent fidelity、source parity、scope mode、coverage shape、route boundary、state machine、security、performance、design flow、simplification risk、brownfield contract、evidence proof shape 和 deferral sovereignty。
- 建立 structured finding schema，要求 severity、confidence、authority level、evidence refs、affected truth surface、recommended route 和 user decision fields。
- 建立 intent/parity/deferral artifact contract，防止 full parity 用户意图被静默降级为 MVP。
- 恢复并强化有限状态机审查：当 feature 涉及 lifecycle、workflow、multi-agent loop、resume/stop/recovery、权限/可见性、状态切换、非法转移或 source parity 时，planner review 必须触发 state-machine reviewer。
- 在 package truth 中提供状态机落点：`truth.md` 需要能承载 `State Model` / `Diagram Truth Layer`；`tests.md` 需要覆盖状态转移、非法转移、恢复路径和状态轴组合。
- 按 skill-creator 标准优化 Beacon skill package 约束：`SKILL.md` 精简入口，复杂规则进入直连 `references/`，非平凡 skill 必须有 eval/benchmark 证据或至少 smoke evaluation contract。

### Out of Scope

- 不改变 Beacon 主生命周期：仍然是 `plan -> truth -> generate -> evaluate -> release`。
- 不让 planner 写 package truth、implementation、QA verdict 或 release verdict。
- 不让 generator 自证完成。
- 不让 evaluator 修复 implementation 或改写 truth。
- 不恢复 legacy `prd`、`user-story`、`test-case` 作为 host-visible authority。
- 不要求本 feature 一次性删除历史源码目录；公开可见投影和安装包必须先收敛，历史内容可作为 compatibility/internal reference 迁移或归档。

## Planner Public Surface Contract

v1.6.0 目标 public planner surface 是：

| Public skill | Role |
|---|---|
| `beacon-pln-brainstorm` | 粗提示词拆分、湖/海判断、需求探索和 route convergence。 |
| `beacon-pln-source` | source-driven / OSS parity / brownfield takeover / source evidence anchoring。 |
| `beacon-pln-review` | 多角度 planner review、intent parity、state-machine review、pre-truth readiness synthesis。 |
| `beacon-pln-friction` | friction capture、queue governance 和 support advisory 入队。 |

以下能力不得继续作为 v1.6.0 默认 host-visible planner public surface 暴露；它们应进入 `beacon-pln-review` 的内部 reviewer catalog 或 references：

- founder / CEO review
- doubt / adversarial review
- security review
- performance review
- context engineering
- simplify review
- documentation ADR
- design review
- deep state/risk review

如果 host compatibility 需要保留旧目录，必须标记为 compatibility/internal，不得在 v1.6.0 materialized public package、metadata、router help 或 recommended route 中作为默认 public route 出现。

## `beacon-pln-review` Skill Contract

`beacon-pln-review` 是 planner harness skill，必须遵守 planner HARD GATE：

- 不能写代码；
- 不能搭脚手架；
- 不能修改 package truth；
- 不能修改 `.machine/`；
- 不能给 QA/release verdict；
- 不能调用 generator/evaluator/release 类 skill 执行动作；
- 唯一产物是 research/planning artifact、gap/risk/finding、湖/海判断、route recommendation。

`beacon-pln-review/SKILL.md` 必须保持薄入口，只保留：

- 触发条件；
- 边界；
- 模式；
- reviewer selection；
- output contract；
- route rules；
- 直接 references。

详细规则必须进入直接引用的 `references/`：

- `references/reviewer-catalog.md`
- `references/finding-schema.md`
- `references/intent-parity-artifacts.md`
- `references/state-machine-review.md`
- `references/skill-package-standard.md`

## Reviewer Catalog Contract

`beacon-pln-review` 必须提供内部 reviewer catalog。Always-on reviewer：

| Reviewer | Purpose |
|---|---|
| `intent-fidelity` | 检查用户真实意图是否被丢失、弱化、误译或 MVP 化。 |
| `scope-mode` | 判定 scope 是 `full_parity`、`mvp`、`patch`、`research`、`brownfield_takeover` 还是 `compatibility_only`。 |
| `coverage-shape` | 检查 acceptance 能否转成真实行为测试，而不是 mock-only 或 docs-only 证明。 |
| `route-boundary` | 检查 planner 是否越权写 truth、实现、QA verdict 或 release verdict。 |
| `state-machine` | 从整体状态机、生命周期、分支流、非法转移、恢复路径和状态轴组合审查 plan/truth readiness。 |

Conditional reviewer：

| Reviewer | Trigger |
|---|---|
| `source-parity` | 用户引用 source 项目、OSS、成熟系统、完整复刻、同等能力或做全。 |
| `deferral-sovereignty` | 存在延期、裁剪、降级、MVP 或未实现能力。 |
| `security-boundary` | 涉及权限、身份、公开入口、用户输入、密钥或敏感数据。 |
| `performance-boundary` | 涉及长任务、循环、并发、缓存、查询、token/时间预算或批量处理。 |
| `design-flow` | 涉及 UI/UX、用户流程或跨界面状态。 |
| `brownfield-contract` | 接管既有项目、旧 truth、legacy/mixed state 或兼容迁移。 |
| `evidence-proof-shape` | 交付声称依赖测试、benchmark、runtime evidence 或 release readiness。 |
| `simplification-risk` | 存在“简化”可能破坏用户完整意图或 source parity 的风险。 |

Reviewer catalog 是内部能力，不新增同名 public planner skills。

## Intent / Parity / Deferral Artifact Contract

`beacon-pln-review` 输出的 planner review artifact 至少包含：

- `intent_snapshot`：保留用户原始意图、关键措辞、强度信号和不可静默改变的承诺。
- `scope_mode`：`full_parity`、`mvp`、`patch`、`research`、`brownfield_takeover`、`compatibility_only` 等。
- `source_capability_inventory`：当 source 项目存在时，列出 source 的能力、流程、状态、边界和证据。
- `parity_matrix`：source capability 到目标 Beacon truth / tasks / tests / evidence 的映射。
- `promotion_diff`：planner support advisory 被用户接受后，进入 truth/change 的变更摘要。
- `deferral_ledger`：任何延期、裁剪、MVP 降级或未覆盖能力，必须有用户可见理由和 user decision。
- `state_model`：当 state-machine reviewer 触发时，列出状态、转移、非法转移、恢复路径、副作用和状态轴。
- `recommended_route`：只能推荐 `beacon-gen-truth`、`beacon-gen-change`、`beacon-gen-refreeze`、`beacon-gen-implement`、`beacon-eval-qa`、`beacon-eval-release`、`beacon-pln-friction` 或 `defer/queue`。

当用户出现以下措辞时，默认 `scope_mode = full_parity`：

- 完整复刻
- 同等能力
- 做全
- 参考某成熟项目实现
- parity
- same capability
- 不要 MVP

任何从 `full_parity` 到 `mvp`、`patch` 或 `defer` 的降级都必须进入 `deferral_ledger`，并要求用户显式接受。没有用户接受时，不得冻结成缩小后的 truth。

## State Machine / Diagram Truth Layer

有限状态机是本 feature 的硬性标准之一，不是附带 checklist。

当 feature 触发以下任一条件时，`state-machine` reviewer 必须运行：

- 存在生命周期、阶段、状态、队列、resume、stop、rollback、recovery、retry 或 long-running loop；
- 存在多 actor、多 agent、多 harness、多权限或跨界面状态；
- 存在 source parity / full parity / 同等能力复刻；
- 存在 illegal transition、blocked state、partial completion、fake completion 或 release gate 风险；
- `diagram_truth` 识别出 `branch-flow`、`state-machine`、`decision-priority` 或两个以上 state axes。

State machine review 必须输出：

- named states；
- allowed transitions；
- invalid / blocked transitions；
- side effects on transition；
- recovery / rollback / resume paths；
- terminal states；
- state axes and axis combinations；
- coverage implications。

Truth 落点要求：

- `features/<slug>/truth.md` 必须能承载 `State Model` 或 `Diagram Truth Layer`，并声明 state-machine 是否 required。
- `features/<slug>/tests.md` 必须覆盖状态转移、非法转移、恢复路径、状态轴组合和 diagram truth propagation。
- `docs/beacon/<version>/research/<feature-slug>.md` 可作为 `support_advisory` 承载状态机图、业务流图和决策优先级，但不能自动成为 requirement truth。
- 如果状态机改变承诺面或 acceptance，必须 route 到 `beacon-gen-change` 或 `beacon-gen-refreeze`。

## Finding Schema Contract

每个 review finding 必须结构化：

```text
finding_id
reviewer
severity: P0 | P1 | P2 | P3
confidence: 0 | 25 | 50 | 75 | 100
authority_level: user_quote | package_truth | source_evidence | implementation_evidence | runtime_evidence | assumption
issue
evidence_refs
affected_truth_surface
recommended_route
user_decision_required
autofix_allowed
```

Planner finding 的 `autofix_allowed` 默认必须是 `false`。Planner 只能 route，不能修。

P0/P1 finding 的默认 gate 行为：

- `intent-fidelity` P0/P1：不能进入实现；route `beacon-gen-truth` 或 `beacon-gen-change`。
- `source-parity` P0/P1：不能 freeze full parity feature；必须补 `source_capability_inventory` 和 `parity_matrix`。
- `state-machine` P0/P1：不能 freeze 或 implement；必须补 State Model / Diagram Truth Layer 和 coverage。
- `route-boundary` P0/P1：当前 planner 输出无效，必须停止并重新路由。

## Skill Creator Package Standard

Beacon skill package 必须吸收 `qi-dev-skill-creator` / OpenAI skill-creator / Anthropic skill-creator 的稳定标准：

- 每个 public skill 的 frontmatter `name` 必须匹配目录名。
- `description` 必须描述做什么、何时触发、边界，不把触发条件藏在正文深处。
- `SKILL.md` 应是精简入口；接近 500 行或包含大量变体细节时，必须拆到直接引用的 `references/`。
- 引用文件必须由 `SKILL.md` 直接命名，避免深层 reference chain。
- 重复、脆弱或可确定性验证的操作应进入 `scripts/` 或 CLI command，而不是让 agent 重写。
- 面向 Codex/OpenAI surface 的 public skill 应提供 `agents/openai.yaml` 或等价 metadata。
- 非平凡 skill 必须有 eval/smoke/benchmark contract；不得用 assistant self-report 声称 skill 合格。
- Skill eval 证据必须标记为 runtime evidence，不得替代 package truth、formal QA 或 release verdict。

`beacon-pln-review` 是非平凡 skill，必须有至少一组 smoke eval / benchmark case 覆盖：

- full parity intent 不被 MVP 化；
- source parity matrix 缺失被阻断；
- state-machine required 但未落 truth 被阻断；
- planner 被要求改 truth/写代码/验收时被 HARD GATE 阻断；
- finding schema 完整；
- evaluator/release verdict 不被 planner 输出。

## 验收标准

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | public-surface | v1.6.0 planner public surface 收敛为 `beacon-pln-brainstorm`、`beacon-pln-source`、`beacon-pln-review`、`beacon-pln-friction`。 |
| AC-002 | internal-reviewer-catalog | founder/security/performance/doubt/context/simplify/adr/design/deep 等过细 planner 能力进入 `beacon-pln-review` references/reviewer catalog，不作为默认 public route。 |
| AC-003 | thin-skill | `beacon-pln-review/SKILL.md` 是薄入口，详细 reviewer、finding、artifact、state-machine 和 skill-package 规则进入直接引用的 `references/`。 |
| AC-004 | boundary | `beacon-pln-review` 遵守 planner HARD GATE，不能写 truth、代码、`.machine/`、QA verdict 或 release verdict。 |
| AC-005 | intent-fidelity | review artifact 必须保留 `intent_snapshot`，并识别强意图词，防止完整意图被静默弱化。 |
| AC-006 | full-parity-default | 用户说“完整复刻”“同等能力”“做全”或同类表达时，默认 `scope_mode=full_parity`。 |
| AC-007 | source-parity | source 项目存在时，必须生成 `source_capability_inventory` 和 `parity_matrix`，否则不能 freeze/implement。 |
| AC-008 | deferral-sovereignty | 任何 MVP、延期、裁剪或未覆盖能力必须进入 `deferral_ledger` 并要求用户显式接受。 |
| AC-009 | state-machine-reviewer | reviewer catalog 必须包含 `state-machine` reviewer，并在 lifecycle/workflow/loop/recovery/permission/source-parity 场景触发。 |
| AC-010 | state-model-output | state-machine reviewer 必须输出 states、transitions、invalid transitions、side effects、recovery paths、terminal states、state axes 和 coverage implications。 |
| AC-011 | truth-state-landing | package truth 必须支持 `State Model` / `Diagram Truth Layer` 落点；缺失时 route `beacon-gen-truth` 或 `beacon-gen-change`。 |
| AC-012 | coverage-state-landing | package tests 必须覆盖状态转移、非法转移、恢复路径和状态轴组合。 |
| AC-013 | research-support-boundary | research 中的状态机图/业务流图是 `support_advisory`；只有用户接受并存在 `promotion_ref` 后才能进入 truth/change。 |
| AC-014 | finding-schema | 所有 findings 必须包含 reviewer、severity、confidence、authority_level、evidence_refs、affected_truth_surface、recommended_route 和 user_decision_required。 |
| AC-015 | no-autofix | planner findings 默认 `autofix_allowed=false`，不能由 planner 自动改 truth 或实现。 |
| AC-016 | route-synthesis | 多 reviewer 输出必须 merge/dedup/synthesize 成单一 route recommendation，不能把多个 reviewer 的互斥结论直接丢给用户。 |
| AC-017 | skill-creator-standard | Beacon public skills 必须符合 skill-creator anatomy：frontmatter、精简入口、直接 references、metadata/eval 约束。 |
| AC-018 | eval-contract | `beacon-pln-review` 必须有 skill eval/benchmark cases 覆盖 intent parity、source parity、state-machine、boundary negative 和 finding schema。 |
| AC-019 | no-main-lifecycle-change | 本 feature 不改变 Beacon 主生命周期，也不新增 truth/generate/evaluate/release 之外的新主阶段。 |
| AC-020 | install-projection | materialized/installed v1.6.0 skill package 必须只暴露收敛后的 public planner surface；旧细分 planner 能力只作为 internal reviewer/reference 出现。 |

## 下一步路由

本 truth package 冻结后，下一步应进入 `beacon-gen-implement`：

```text
beacon-gen-implement beacon-pln-review-intent-parity-state-machine-v160
```

实现必须先更新 source truth 和 skill package projection，再由 `beacon-eval-qa` 验证。本 truth 不包含 implementation completion、QA pass 或 release readiness。
