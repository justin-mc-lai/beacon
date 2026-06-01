# Research: Beacon Design Human Subskills Closure Contract

**Feature**: `beacon-design-human-subskills-closure-contract`  
**Version**: `v1.4.11`  
**Status**: `research-closed`  
**Date**: `2026-05-27`  
**Revision**: `R3` (2026-05-29: added simplify route)  

**prd_refs**: `docs/beacon/v1.4.11/prd/beacon-design-human-subskills-closure-contract.md`  
**user_story_refs**: `docs/beacon/v1.4.11/user-story/beacon-design-human-subskills-closure-contract.md`  
**test_case_refs**: `docs/beacon/v1.4.11/qa/test-cases/beacon-design-human-subskills-closure-contract.md`  
**coverage_notes**: R3 adds simplify route (AC-013 through AC-017) with Beacon-native first-principles capabilities; 17 AC/TC pairs in scope.  
**out_of_scope_notes**: No new CLI route, no prototype adapter change, no release verdict change, no upstream dependency for simplify route.

## 1. 背景

`beacon-design-product-prototype-rebuild-contract` 已经把旧 prototype 深度重构为 Beacon design 能力。

现有证据显示：

- `beacon design contract` 已经暴露 7 条 deterministic route：`explore`、`extract`、`system`、`review`、`polish`、`library`、`bootstrap`。
- R3 新增：现有 7 条路由全部是"怎么做设计"的能力，缺一条在工程思维进入设计流程前就拦下过度复杂度的前置检查——`simplify` 路由。

## 2. 现有问题

- 用户想探索方向，AI 可能跑去 review。
- 用户想做组件系统，AI 可能只给视觉建议。
- `library` 参考库可能被误当成项目设计 truth。
- `bootstrap` 能力检查可能被误当成 gate 或 release 证据。
- **所有路由都假设"这个 feature 确实需要设计"——没有一条会反问"这个设计是不是本就不该这么复杂"。**

## 3. 收敛结论

保留 `beacon-design` 作为总入口，补齐 8 个 host-visible 子 skill：

```text
beacon-design-explore / extract / system / review / polish / library / bootstrap / simplify
```

每个子 skill 绑定到 CLI route：`beacon design route <intent> "<feature>" --project . --version auto --json`

## 4. Architecture

```text
Layer 1: Python 源码 (beacon/utils/design_contract.py)
  └─ DESIGN_ROUTES dict 新增 "simplify" 条目
  └─ 5 个 first-principles 能力

Layer 2: CLI 合约 (beacon/commands/design.py)
  └─ beacon design route simplify 自动解析为新路由（无需代码改动）
  └─ beacon design contract 返回 8 条路由

Layer 3: Host-visible 子 skill (skills/beacon/beacon-design-simplify/SKILL.md)
  └─ 人类面入口，operator command = beacon design route simplify

Layer 4: 回归测试 (tests/test_v1411_beacon_design_human_subskills_closure.py)
  └─ TC-DESIGN-SKILL-013 至 TC-DESIGN-SKILL-017
```

## 5. Business Flow

```text
Operator requests simplify audit
  → beacon-design-simplify skill resolves
  → beacon design route simplify <feature> --json
  → DESIGN_ROUTES["simplify"] payload returns 5 capabilities
  → AI executes first-principles audit:
      1. lazy_user_axiom: "用户是懒的，最小必要输入是什么？"
      2. core_scenario_extraction: "剥掉 feature 包装，核心场景是什么？"
      3. engineer_abstraction_detection: "哪些 UI 层级是数据模型直接映射？"
      4. information_deduplication: "同一概念在哪里重复出现？"
      5. complexity_burden_score: "屏数 / 输入维度 / 认知负担量化"
  → Output: simplicity_audit_findings + reduction_recommendations
  → Route accepted findings to truth binding or change-refreeze
```

## 6. State Machine

```text
States: idle → audit_requested → auditing → audit_complete | audit_blocked

idle → audit_requested: operator invokes beacon-design-simplify
audit_requested → auditing: route contract resolved, DESIGN_ROUTES has "simplify"
audit_requested → audit_blocked: route not found
auditing → audit_complete: 5 capability checks complete with findings
auditing → audit_blocked: missing truth refs
audit_complete: output simplicity_audit_findings, reduction_recommendations
audit_blocked: reason = missing design route or truth
```

Branch-flow:

```text
Does feature have defined core user scenario?
  YES → Is core scenario ≤ 5 inputs and ≤ 1.5 screens?
    YES → pass simplicity check, green report
    NO  → flag complexity drift, output reduction recommendations
  NO  → block audit, ask operator to define core scenario
```

Decision-priority:

```text
Q1: Core user scenario defined? → YES proceed, NO block
Q2: ≤ 5 inputs and ≤ 1.5 screens? → YES pass, NO flag
Q3: Any concept repeated ≥ 2 UI sections? → YES flag, NO pass
Q4: Any UI layer directly mirror internal data model? → YES flag, NO pass
```

## 7. 子 skill 分工

| 子 skill | route | 上游能力 | 边界 |
| --- | --- | --- | --- |
| `beacon-design-explore` | `explore` | `vibe-to-ui` | UI 方向、信息层级、布局候选，不是 truth。 |
| `beacon-design-extract` | `extract` | `vibe-to-ui` | 从截图 / 参考拆结构和组件候选，不是 truth。 |
| `beacon-design-system` | `system` | `ui-ux-pro-max` | 组件系统、tokens、状态、响应式、无障碍、栈感知基线。 |
| `beacon-design-review` | `review` | `impeccable` | UX 问题、层级、文案、状态缺口、可访问性 review。 |
| `beacon-design-polish` | `polish` | `impeccable` | 上线前间距、对齐、反馈、信任、microcopy 打磨。 |
| `beacon-design-library` | `library` | `awesome-design-md` | 只做 reference-only，不是执行 skill，不是 truth。 |
| `beacon-design-bootstrap` | `bootstrap` | upstream compatibility | 只检查安装 / mirror / bootstrap 可用性，不是 gate / release。 |
| `beacon-design-simplify` | `simplify` | Beacon-native | 第一性原理简洁审计：lazy-user axiom、核心场景提取、工程师抽象检测、信息去重、复杂度负担评分。不依赖外部 skill。 |

## 8. 不做什么

本 feature 不做：

- 不新增 design CLI route（simplify 复用现有 `beacon design route` 框架）。
- 不改 `beacon design` runtime 语义。
- 不改 prototype adapter 行为。
- 不改 PRODUCT.md / DESIGN.md truth 内容。
- 不改 release verdict。
- 不引入新的 lifecycle stage。
- simplify 不依赖任何外部上游 skill。

## 9. 推荐下一跳

进入 `beacon-change-refreeze`，冻结 feature：

```text
beacon-design-human-subskills-closure-contract
```

冻结后再实现缺失的 host-visible `beacon-design-simplify` skill 文件和 discoverability 测试。

## 6.1 Decision Priority

```text
Priority order for simplify audit decisions:

1. Core scenario detection (highest priority)
   - If operator has not defined core user scenario → block audit
   - If core scenario is identified but feature deviates from it → flag

2. Complexity burden scoring
   - If core scenario exceeds 5 input dimensions or 1.5 screens → flag complexity drift

3. Information deduplication
   - If same concept appears in ≥ 2 UI sections → flag duplication, recommend consolidation

4. Engineer abstraction detection
   - If UI layer directly mirrors internal data model structure → flag abstraction leak

Block conditions (override all priorities):
- Missing truth refs for target feature
- Missing DESIGN_ROUTES entry for simplify
- Operator has not consented to audit scope
```
