# PRD: Beacon v1.4.7 meta protocol and horizontal engineering support surfaces

**Feature**: `beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces`  
**Version**: `v1.4.7`  
**Date**: `2026-05-14`  
**Status**: `freeze-ready`  
**Track**: `meta-protocol + support-skill-family + human-readable-references`  
**Scenario**: `kernel-preserving-capability-expansion`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Current runtime baseline:
  - `docs/beacon/v1.4.6/SUMMARY.md`
  - `skills/beacon/SKILL.md`
  - `skills/beacon/using-beacon/SKILL.md`
  - `skills/beacon/beacon-prd/SKILL.md`
  - `skills/beacon/beacon-implement/SKILL.md`
  - `skills/beacon/beacon-qa/SKILL.md`
  - `skills/beacon/beacon-release/SKILL.md`
- Research closure:
  - `docs/beacon/archive/v1.4.7/research/beacon-v1.4.7-agent-skills-lifecycle-and-meta-protocol-analysis.md`
- External reference inputs:
  - `oss-sync/agents/agent-skills/addyosmani-agent-skills`
  - `oss-sync/agents/agent-skills/gstack`
- Bootstrap note:
  - `beacon prd-bootstrap ... --version v1.4.7 --dry-run` succeeded at target derivation but blocked on strict context version drift because current runtime/docs context remains `v1.4.6`.
  - This PRD is therefore started manually at the bootstrap target path, without promoting `v1.4.7` into active runtime context.

## Overview

Beacon v1.4.7 should strengthen the human-facing capability surface without breaking Beacon's core identity.

The core identity that must remain intact is:

- evidence-first
- truth-governed
- anti-drift
- release-auditable

The main problem is not that Beacon lacks depth. Beacon already has unusually strong truth, evidence, QA, and release governance.

The real problem is that Beacon still feels narrower than the best open skill systems in two ways:

1. it does not yet feel complete as a cross-project engineering operating kit
2. it does not yet package support capabilities with enough clarity, discoverability, and operator-facing confidence

v1.4.7 should therefore focus on four upgrades:

1. converge the main `beacon` skill into a sharper meta-protocol
2. strengthen `using-beacon` into a clearer host-native route constitution
3. add a first tranche of horizontal engineering support skills
4. add lightweight reference pages that improve human readability without becoming new truth sources

This is an augmentation of Beacon's support and routing layers, not a redefinition of the main lifecycle.

## Scope

- Refactor the public Beacon wrapper so `skills/beacon/SKILL.md` behaves like a compact meta-protocol rather than a mixed wrapper/manual/version anchor.
- Strengthen `skills/beacon/using-beacon/SKILL.md` so it becomes the canonical host-native route surface for truth, execution, verification, gate, and support decisions.
- Introduce a first-class horizontal engineering support skill family under Beacon, starting with the highest-value generic capabilities.
- Introduce thin human-readable reference pages that support requirement, QA, release, and support-surface decisions without duplicating canonical truth.
- Document an explicit lifecycle mapping between external engineering skill models and Beacon's own closure model.
- Improve specialist packaging and multi-host/operator readability without exploding Beacon into a flat command catalog.

## 1. 问题

### 1.1 Beacon 的 kernel 很强，但入口协议还不够锋利

Beacon 当前在 `v1.4.6` 已经明显强于大多数公开 skill pack 的地方是：

- canonical truth
- version surfaces
- requirement traceability
- evidence projection
- QA/release gate
- promotion and anti-drift governance

但它的公共入口仍有一个结构问题：

- `beacon` 主 skill 仍部分承担 wrapper/manual/anchor 角色
- `using-beacon` 已有 route intent，但还不是足够锋利的 host route constitution

结果是：

- Beacon 对内很强，对外的第一跳解释还不够利落
- 用户知道 Beacon 严谨，但不一定知道 Beacon 这轮到底该用哪类能力

### 1.2 Beacon 的主链清楚，但横向工程 support skill 仍偏薄

Beacon 当前主链：

`prd -> user-story -> test-case -> implement -> qa -> release`

这条链已经足够清楚，也不应继续扩张。

但与 `agent-skills` 相比，Beacon 仍缺少一些高频横向工程 support skills，例如：

- context engineering
- source-driven implementation
- doubt-driven challenge/review
- security review
- performance review
- documentation / ADR discipline
- generic debug / recovery support

这使 Beacon 在跨项目工程能力上显得不够完整。

### 1.3 Beacon 的 support surface 已经存在，但 specialist packaging 不够强

与 `gstack` 相比，Beacon 的 support surface 更克制，也更安全。

但 `gstack` 的强项在于：

- specialist framing
- operator-visible capability confidence
- memorable role packaging
- multi-host installation and usage readability

Beacon 目前虽然已经有：

- `ceo-review`
- `design-review`
- `brainstorm`
- `deep`
- `help`
- `status`
- `doctor`

但整体还更像“治理 kernel 的附属能力”，而不像“可直接感知的 specialist overlays”。

### 1.4 Beacon 的 machine 面强，但轻量 human reference 面不足

Beacon 当前 machine truth 很完整。

但对人类来说，很多高频判断还缺少一层轻量 reference：

- requirement closure checklist
- research closure checklist
- freeze readiness checklist
- QA layer checklist
- release blocker taxonomy
- support-surface routing cheatsheet

结果是：

- machine 面完整，但人类快速扫描效率不够高
- skill 必须承担过多解释职责
- operator 很难在低成本阅读下获得稳定判断支架

### 1.5 Beacon 需要吸收外部强项，但不能丢掉自己的根特性

`agent-skills` 的长处是：

- skill anatomy
- anti-rationalization
- broad engineering phase mapping
- lightweight references

`gstack` 的长处是：

- specialist packaging
- host portability
- browser/session/tooling reality
- visible software-factory confidence

Beacon 吸收这些能力时，不能牺牲：

- compact main chain
- truth/gate separation
- canonical source discipline
- evidence-backed release closure

v1.4.7 的真正挑战因此不是“加功能”，而是“在不软化 kernel 的前提下增加能力可见度与可用宽度”。

## 2. 目标

### 2.1 主要目标

1. 把 `beacon` 主 skill 收敛成真正的元协议
2. 把 `using-beacon` 收敛成真正的 host-native route constitution
3. 为 Beacon 增加第一批高价值横向工程 support skills
4. 为关键主链与 support surfaces 补齐薄但高复用的人类 reference
5. 让外部用户更容易理解 Beacon 与 `agent-skills` / `gstack` 的关系与映射
6. 在增强能力面时继续保持主链不扩张、truth/gate 不混淆

### 2.2 非目标

- 不新增新的公开 lifecycle stage
- 不把 support skills 升格成 truth source 或 gate source
- 不把外部 skill pack 作为 Beacon 默认运行前提
- 不为了 specialist packaging 而把 Beacon 扩成大而平的 command catalog
- 不削弱 `prd -> user-story -> test-case -> implement -> qa -> release` 主链
- 不把 skill 默认写回强操作剧本

## 3. 设计原则

### 3.1 Meta-protocol 先于命令扩张

Beacon 首先需要的是更清楚的“怎么判断应该去哪”，而不是更多 top-level names。

### 3.2 主链保持 compact，support family 负责扩张能力宽度

能力增强优先通过 support skills 完成，而不是通过主生命周期继续膨胀。

### 3.3 Support skill 的主要职责是 challenge / explain / verify / strengthen

它们可以：

- challenge framing
- explain route
- verify method or evidence quality
- strengthen execution or review quality

但不能：

- author canonical truth by default
- issue release gate verdicts by default
- silently replace `change`, `implement`, `qa`, or `release`

### 3.4 轻 reference 是人类判断支架，不是 canonical truth

References 必须：

- 可读
- 可复用
- 按需加载
- 不反向驱动 machine truth

### 3.5 借鉴 external systems，优先借鉴 packaging 与 discipline

从 `agent-skills` 借：

- anatomy
- anti-rationalization
- horizontal engineering discipline

从 `gstack` 借：

- specialist packaging
- host/operator readability
- practical browser/session/tooling awareness

但不借它们的默认依赖模型与 public surface 膨胀模式。

### 3.6 Beacon 的根本特性必须保持硬边界

以下必须继续成立：

- main chain remains compact
- support surfaces do not become stages
- truth remains canonical and versioned
- QA/release remain evidence-backed and fail-closed
- learning remains advisory, replayable, and auditable
- skill default remains philosophy + minimum tools + necessary facts

## 4. 范围

### In scope

- `skills/beacon/SKILL.md` meta-protocol convergence
- `skills/beacon/using-beacon/SKILL.md` route constitution convergence
- first-wave horizontal engineering support skills
- first-wave lightweight reference pages
- lifecycle mapping docs between external phase models and Beacon closure model
- stronger specialist packaging language for Beacon support surfaces

### Out of scope

- promoting `v1.4.7` to current runtime release line
- broad rewrite of every historical skill in one pass
- replacing Beacon's current truth/evidence/gate architecture
- importing external repos as runtime dependencies
- flattening Beacon into a slash-command-first specialist catalog

## 5. 功能需求

### FR-001 Beacon 必须把主 `beacon` skill 收敛成元协议

`skills/beacon/SKILL.md` 必须优先回答：

- 当前问题属于哪个决策面
- 哪些原则永远成立
- 哪些 support surface 只能 advisory
- 什么时候必须 route back

它不应继续承担过多 wrapper/manual/version note 混合职责。

### FR-002 Beacon 必须把 `using-beacon` 收敛成 host-native route constitution

`using-beacon` 必须更清楚地区分：

- truth
- execution
- verification
- gate
- support

并明确：

- route reasoning
- fallback routing
- support output 何时必须回 `change`

### FR-003 Beacon 必须引入第一批横向工程 support skills

v1.4.7 至少应为以下 skill family 建立正式要求：

- `beacon-context-engineering`
- `beacon-source-driven`
- `beacon-doubt-review`

并为后续以下能力保留一致 contract 入口：

- `beacon-security-review`
- `beacon-performance-review`
- `beacon-documentation-adr`
- `beacon-debug-recovery`

### FR-004 Beacon 必须增加轻量 reference 页面

至少应定义第一批 references：

- `requirement-closure-checklist.md`
- `research-closure-checklist.md`
- `business-flow-checklist.md`
- `state-machine-checklist.md`
- `freeze-readiness-checklist.md`
- `qa-layer-checklist.md`
- `release-blocker-taxonomy.md`
- `support-surface-routing-cheatsheet.md`

### FR-005 Beacon 必须表达外部 lifecycle 与自身 closure model 的映射

Beacon 必须能明确表达：

- `agent-skills` phase model 如何映射到 Beacon
- `gstack` operator sprint / specialist model 如何映射到 Beacon
- 这种映射只服务理解与路由，不改变 Beacon 主链

### FR-006 Beacon 必须增强 support surface 的 specialist packaging

Beacon 不需要复制 `gstack` 的大量 public commands。

但 Beacon 必须让 support surfaces 更清楚地表现出：

- specialist role
- operator intent
- what kind of challenge or strengthening this surface performs

### FR-007 Beacon 必须保持 support-surface constitution 不变硬

无论新增多少 support capability，下列边界都必须保持：

- not truth source
- not gate source
- not new lifecycle stage
- route back to canonical truth or delivery surfaces when scope/promise changes

### FR-008 Beacon 必须提升多宿主与工具现实的可读性

Beacon 已具备多宿主表面投影，但 `v1.4.7` 必须让 host portability 对 operator 更可读。

重点不在于新增更多投影，而在于：

- how Beacon appears on hosts
- what the host-facing entry contract is
- what browser/session/tooling support means for actual operators

### FR-009 Beacon 必须让学习与 route explainability 更人类可读

Beacon 的 learning 仍必须保持可审计与 advisory。

但 `v1.4.7` 应让人类更容易理解：

- 本轮 route 为什么这样建议
- learning 哪些只是 hint
- 哪些判断仍然必须回到 canonical truth 或 hard gate

## 6. 验收标准

| AC ID | 说明 |
| --- | --- |
| AC-001 | `skills/beacon/SKILL.md` 被收敛成更明确的 meta-protocol |
| AC-002 | `using-beacon` 能稳定表达 truth/execution/verification/gate/support 的路由宪法 |
| AC-003 | 第一批横向工程 support skills 被正式定义并保持 support-only 边界 |
| AC-004 | 第一批 lightweight references 被正式引入并可被关键 surfaces 引用 |
| AC-005 | 文档中存在 external lifecycle / Beacon lifecycle 的清晰映射 |
| AC-006 | support surfaces 的 specialist packaging 提升，但 public main chain 未扩张 |
| AC-007 | 多宿主、browser/session/tooling 能力对 operator 的可读性增强 |
| AC-008 | learning 与 route explainability 对人类更清楚，但 truth/gate separation 不被削弱 |

## 7. First-Slice Freeze Decision

`v1.4.7` 当前 requirement package 先冻结 first slice，不一次性承诺全部研究 backlog。

当前冻结边界：

1. `skills/beacon/SKILL.md` 收敛为 meta-protocol
2. `skills/beacon/using-beacon/SKILL.md` 收敛为 host route constitution
3. 正式引入三条 support skills：
   - `beacon-context-engineering`
   - `beacon-source-driven`
   - `beacon-doubt-review`
4. 补齐支撑上述入口与路由判断的第一批 lightweight references
5. 明确 `agent-skills` / `gstack` 到 Beacon main chain 的 lifecycle mapping，但不把这些外部模型升格为 Beacon 主链

后续可扩展项，例如 `beacon-security-review`、`beacon-performance-review`、`beacon-documentation-adr`、`beacon-debug-recovery`，保留在同主题 roadmap 中，但不计入 first-slice freeze 承诺。

## 8. 下一步

This PRD should route to:

- `user-story` for the first accepted slice of meta-protocol, support-skill, and reference-page commitments
- `test-case` for acceptance closure on route clarity, support-surface boundaries, and reference loading behavior

Do not promote this draft into implementation until:

- first-slice scope is narrowed
- the initial support skill set is fixed
- the references package boundary is agreed
