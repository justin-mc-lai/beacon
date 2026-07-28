---
slug: design-craft-absorption-v1611
version: v1.6.11
status: draft
revision_id: R1
language: zh
domain_required: true
domain_kind: platform
ux_required: false
ux_deferred: true
package_maturity: filled
materials_status: current
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
program_ref: docs/beacon/v1.6.11/programs/beacon-plan-goal-task-closure-v1611/program-manifest.md
baseline_commit: ce8b1be75ba3ef06c38b69de226150702739f3e8
truth_map_contract: beacon-truth-map-v1
participating_services: beacon
git_canonical_branch: main
previous_revision: ""
change_reason: "Absorb ui-skills craft modules into beacon-design as support-only capabilities without expanding 1+6 lifecycle"
parent_truth: docs/beacon/v1.6.11/SUMMARY.md
inherited_contracts: "skills/beacon/beacon-design/SKILL.md; docs/beacon/global-boundaries.md"
canonical_refs:
  prd: docs/beacon/v1.6.11/features/design-craft-absorption-v1611/truth.md
  user_story: docs/beacon/v1.6.11/features/design-craft-absorption-v1611/truth.md
  test_case: docs/beacon/v1.6.11/features/design-craft-absorption-v1611/tests.md
source_refs:
  ui_skills_mirror: /Users/apple/Developer/Personal/oss-sync/design/skills/ui-skills
  ui_skills_upstream: https://github.com/ibelick/ui-skills
  analysis: /Users/apple/Developer/Personal/oss-sync/index/analysis/ibelick-ui-skills.md
---

# Requirement Truth: Design Craft Absorption into beacon-design

## 人话

Beacon 的 design 已经会“管设计、绑真相、卡住实现乱发挥”，但还不够会“亲手把 UI 修漂亮、修可访问、修动效性能”。  
本需求只做一件事：把 `ui-skills` 里最有用的 4 把 craft 手术刀，装进现有 `beacon-design` 作为 **support craft 能力**，**不新开生命周期，不重做 design 主链路**。

- 能做：在 design harness 内路由/执行 4 个 craft；产出 finding/plan/candidate；保留 support-only 边界
- 不能做：新增 public stage、让 craft 直接改 requirement truth、把 ui-skills 当 Beacon 真相源、整包吞 185 个 registry skill
- 怎样算完：4 craft 有明确入口、输出合同、绑定路径与非法转换拒绝；主生命周期 1+6 不变

## User Intent

为 v1.6.11 冻结“design craft absorption”需求真相草案：  
`baseline-ui + a11y + motion + improve-ui` → Beacon design support craft layer。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: full_parity
feature: design-craft-absorption-v1611
docs_target: v1.6.11
runtime_target: v1.6.11
truth_canonical: main
lifecycle_change: none
public_surface_change: none  # still only beacon-design inside 1+6
compatibility: no_old_shape_soft_compat
absorption_source: ibelick/ui-skills
craft_modules:
  - design-craft-baseline   # from baseline-ui
  - design-craft-a11y       # from fixing-accessibility
  - design-craft-motion     # from fixing-motion-performance
  - design-craft-improve    # from improve-ui (read-only audit + plans)
out_of_scope:
  - redesign design lifecycle
  - new public harness beyond design
  - SEO/metadata craft (defer)
  - full ui-skills registry import
  - implement/qa/release contract rewrite
scope_ack_ref: user-request-2026-07-28-design-craft-absorption
```

## 用户旅程

1. 用户在产品交付中提出 UI craft 诉求（去 slop / a11y / 动效卡顿 / 界面改进审计）。
2. 只进入 `$beacon-design`（或 goal 流水线的 design? 阶段），不新开 public skill。
3. design craft router 选择 1–2 个最小 craft（默认不超过 2；广审最多 3 且必须含 improve）。
4. craft 产出 finding / candidate fix / self-contained plan（improve 只写 plan，不改产品源码）。
5. 若只影响视觉执行细节：作为 support evidence 交给 implement 参考。
6. 若改变产品承诺/AC/状态：必须走 `prototype adapt` 或 `change --refreeze-chain`，craft 自己不能升格为 truth。
7. QA/release 仍按原生命周期；craft 证据可作 advisory，不可单独当 GO。

## First principles

1. **Harness 边界优先**：craft 是 design 的 support capability，不是新 lifecycle stage。
2. **最小吸收**：只吸收 4 个高价值模块；registry 长尾不进主仓真相。
3. **真相权限不外溢**：ui-skills / craft 输出 `truth_source=false`、`gate_source=false`、`lifecycle_stage=false`、`support_only=true`。
4. **证据三门（improve）**：contract + runtime path + single correction；无证明不成 finding。
5. **读写分离**：improve 只读产品源；baseline/a11y/motion 可提代码级建议，默认不直接在 design harness 内落地实现（实现归 implement）。
6. **不重做主链路**：保留 gen-design / system / explore / polish / prototype；craft 是附加层。

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| DesignCraftModule | id, source_skill, intent, authority, io_contract | 一个可路由的 craft 能力 |
| DesignCraftRouterDecision | utterance, selected_modules[], reason, max_modules | 最小集合路由结果 |
| DesignCraftFinding | module_id, severity, evidence_refs, proof{contract,runtime,correction}, candidate_fix | 单条可审计发现 |
| DesignCraftPlan | plan_id, surface, findings[], executor_notes, paths under design craft plan root | improve 产出的可转交计划 |
| DesignCraftRun | run_id, feature, version, modules[], status, support_only | 一次 craft 运行记录 |
| BindingRoute | none \| prototype_adapt \| change_refreeze \| implement_advisory | finding 如何进入后续 harness |

### Frozen module map（本草案冻结的进入方式）

| module_id | upstream skill | design entry | primary output | may touch product source? | binding |
|-----------|----------------|--------------|----------------|---------------------------|---------|
| `design-craft-baseline` | `baseline-ui` | `beacon design route craft baseline` 或 polish 子路由 | anti-slop constraints + violation findings | 否（建议/候选 patch 文本） | implement_advisory；承诺变更 → change |
| `design-craft-a11y` | `fixing-accessibility` | `beacon design route craft a11y` | a11y findings + minimal fixes | 否（同上） | implement_advisory；交互合同变更 → change/prototype |
| `design-craft-motion` | `fixing-motion-performance` | `beacon design route craft motion` | motion/perf findings + mechanism choice | 否（同上） | implement_advisory |
| `design-craft-improve` | `improve-ui` | `beacon design route craft improve` | read-only audit + ≤3 plans | **严禁**改产品源；只写 craft plan 目录 | plan executor=implement；文档/设计合同变更记入 plan |

### 进入 beacon-design 的结构冻结

```text
skills/beacon/beacon-design/
  SKILL.md                         # 仍是唯一 public design harness
  references/modes/                # 现有 lifecycle modes 不变
  references/craft/                # 新增 support craft 层（本需求）
    INDEX.md                       # router + selection rules
    baseline.md                    # absorbed from baseline-ui
    a11y.md                        # absorbed from fixing-accessibility
    motion.md                      # absorbed from fixing-motion-performance
    improve.md                     # absorbed from improve-ui
    plan-template.md               # improve plan contract
```

CLI / route 冻结（名称可微调，语义不可漂）：

```text
beacon design route craft <baseline|a11y|motion|improve|auto> <feature>
beacon design craft-router --utterance "..." --json   # optional helper
```

规则：

- `auto` 必须走 router，输出 `selected_modules` + reason
- 默认最多 2 个 module；`improve` 广审最多 3
- 不得因 craft 路由创建新的 public skill 目录
- 现有 `explore/system/review/polish/extract/library/bootstrap` 保留；craft 是并行 support intent，不替换它们

### 输出合同冻结

每次 craft run 最少输出：

```yaml
mode_id: gen-design-craft   # or nested under polish; public_id remains design
public_id: design
support_only: true
truth_source: false
gate_source: false
lifecycle_stage: false
craft_modules: [design-craft-baseline]
findings: []
plans: []          # only improve may non-empty
binding_route: implement_advisory | prototype_adapt | change_refreeze | none
recommended_next_harness: design|implement|truth|stop
evidence_refs: []
```

### 非法转换（必须拒绝）

1. craft 直接 `status: frozen` 改写 feature truth
2. craft 自证 QA/release pass
3. improve 修改产品源码或依赖
4. 把 ui-skills registry 远端 skill 运行时当 Beacon truth
5. 新增 public lifecycle stage 如 `craft` / `design-craft`
6. 无 proof 三门的 improve finding 进入 plan
7. craft 输出缺 `support_only=true` 却被 implement 当硬门

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-CRAFT-01 | user | must | AC-CRAFT-001 | covered |
| INT-CRAFT-02 | user | must | AC-CRAFT-002 | covered |
| INT-CRAFT-03 | analysis | must | AC-CRAFT-003 | covered |
| INT-CRAFT-04 | analysis | must | AC-CRAFT-004 | covered |
| INT-CRAFT-05 | boundaries | must | AC-CRAFT-005 | covered |
| INT-CRAFT-06 | boundaries | must | AC-CRAFT-006 | covered |
| INT-CRAFT-07 | user | must | AC-CRAFT-007 | covered |
| INT-CRAFT-08 | defer | should | AC-CRAFT-008 | deferred-metadata |

## Acceptance Criteria

| AC ID | Statement |
|-------|-----------|
| AC-CRAFT-001 | Beacon 仅通过 `beacon-design` public harness 暴露 craft；不新增 1+6 public skill，不新增主生命周期 stage。 |
| AC-CRAFT-002 | 四个 module（baseline/a11y/motion/improve）均有 Beacon-owned progressive reference，并可被 design craft router 选中。 |
| AC-CRAFT-003 | craft 输出必须标记 `support_only=true` 且 `truth_source=false`；缺省或伪造权限字段时路由/校验失败。 |
| AC-CRAFT-004 | improve 在产品源上只读；计划只写入受控 craft plan 根目录；试图改产品源必须被拒绝。 |
| AC-CRAFT-005 | improve finding 必须同时具备 contract/runtime/correction 三门证明，否则不得进入 plan。 |
| AC-CRAFT-006 | craft finding 若改变产品承诺/AC/状态，只能推荐 `prototype_adapt` 或 `change_refreeze`，不能直接升格 truth。 |
| AC-CRAFT-007 | router 默认选择 ≤2 个 module；无 utterance/feature 上下文时不得静默全开 4 个 craft。 |
| AC-CRAFT-008 | SEO/metadata 与 ui-skills 其余 registry skill **明确 defer**，本包不实现、不假装覆盖。 |

## Non-goals

- 重做 design lifecycle（gen-design/system/explore/polish/prototype）
- 把 impeccable / ui-ux-pro-max 替换掉（可并存；craft 是补充）
- 安装或运行时依赖 `npx ui-skills` 作为硬门
- 把 design craft 变成 implement 的替代
- 在 v1.6.11 本草案阶段直接编码落地（本包先真相草案）

## Domain FSM DesignCraftRun

| State | From | Guard |
|-------|------|-------|
| idle | — | no craft run |
| craft_route | idle | design craft intent accepted |
| craft_execute | craft_route | modules selected (1–2 default) |
| craft_bind_decide | craft_execute | findings/plans produced |
| done | craft_bind_decide | binding_route decided |
| blocked | craft_route, craft_execute | schema/permission/write-guard fail |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| idle | craft_requested | design_harness_only | craft_route | open craft router |
| craft_route | modules_selected | count_leq_2_or_improve_broad_leq_3 | craft_execute | load progressive craft refs |
| craft_route | route_invalid | missing_utterance_or_all_four_forced | blocked | emit reason_code |
| craft_execute | findings_ready | support_only_payload_valid | craft_bind_decide | attach findings/plans |
| craft_execute | write_product_source | improve_or_craft_attempts_product_write | blocked | reject write |
| craft_execute | proof_missing | improve_finding_lacks_triple_proof | craft_bind_decide | drop invalid finding |
| craft_bind_decide | bind_advisory | visual_only | done | recommend implement |
| craft_bind_decide | bind_prototype | interaction_or_ux_contract_change | done | recommend prototype_adapt |
| craft_bind_decide | bind_change | promise_or_ac_change | done | recommend change_refreeze |
| blocked | repair | payload_or_scope_fixed | craft_route | rerun router |

终态：`done`。

## Illegal transitions

- `idle → done`
- `craft_execute → truth_freeze`
- `craft_execute → release_go`
- `craft_route → craft_execute` while selecting all four modules silently
- `improve → write_product_source`
- craft output with `truth_source=true` or missing `support_only=true`
- creating a new public lifecycle stage named `craft`
- treating ui-skills registry remote skill as Beacon requirement truth

## Risks / Open Questions

1. `gen-design-craft` 作为新 mode 文件，还是挂在 `gen-design-polish` 子路由？**草案默认：独立 mode 文件 + `design route craft`，避免污染 polish 语义。**
2. craft plan 根目录：`design-plans/`（ui-skills 风格）还是 `docs/beacon/<v>/design/craft-plans/<feature>/`？**草案默认后者**，便于版本审计。
3. 是否允许 implement 阶段自动召回 craft？**草案默认否**；需 design/goal 显式进入。

## Freeze readiness

本文件 `status: draft`（R0）。  
“冻结”的是 **4 craft 如何进入 beacon-design 的结构与权限合同**，不是正式 requirement freeze gate。  
正式冻结需 `$beacon-truth` review + freeze ack。
