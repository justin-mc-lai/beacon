---
slug: beacon-v1614-feature-map
version: v1.6.14
status: frozen
language: zh
domain_required: false
ux_required: false
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
package_maturity: filled
materials_status: current
canonical_refs:
  prd: docs/beacon/v1.6.14/features/beacon-v1614-feature-map/truth.md
  user_story: docs/beacon/v1.6.14/features/beacon-v1614-feature-map/truth.md
  test_case: docs/beacon/v1.6.14/features/beacon-v1614-feature-map/tests.md
---

# Requirement Truth: beacon-v1614-feature-map (v1.6.14)

## 人话

给每个功能配一张**"功能地图"**：讲清楚"这个功能在哪、怎么进去、怎么验证"。分三步建：

1. **骨架**（先用起来）：每个功能有 `feature-map.md`，列出代码入口 + 验证命令，每个都挂到冻结的验收标准编号上 —— 解决"在哪改、怎么验证"
2. **复现路由**（第二步）：给一句模糊的 bug 描述（"点这个没反应"），地图能指到对应的入口和验证方法 —— 解决"从哪开始查"
3. **agent 自验证**（第三步）：agent 按地图自己跑验证命令、看信号（复用 code2truth 资产），人不用盯着 —— 解决"谁验证"

- 能做：地图随需求冻结生成骨架；实现时填入口/验证命令；QA 用同一地图验收
- 不能做：地图绝不反过来改需求真相（单向投影）；不新增命令面
- 怎样算完：任何 feature 打开 truth 就能看到"做什么 + 在哪改 + 怎么验证"，agent 能按地图自证

## User Intent

把方法论 M2 的 feature map 落地为 beacon 支撑面：`features/<slug>/feature-map.md`（入口 + 验证命令 + 复现路由），绑定 truth AC，分三阶段（骨架 → 复现路由 → agent 自验证）。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
truth_review_gate: required
fill_depth: filled
intent_source: 2026-08-27 beacon-feature-map-design-2026-08-27.md + codemap 调研
```

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-001 | 骨架：entry_points + verification 绑定 AC | must | AC-001 | covered |
| INT-002 | 复现路由：模糊描述 → 定位 | must | AC-002 | covered |
| INT-003 | agent 自验证（code2truth 复用） | must | AC-003 | covered |
| INT-004 | 单向投影 + 不新增命令面 | must | AC-004 | covered |

## 用户旅程

1. 触发：feature 冻结/实现/验收任意阶段
2. 关键操作：读地图 → 找入口 → 跑验证命令 → 看信号；模糊 bug 描述 → 地图路由
3. 结果：迭代时"在哪改/怎么验证"一眼可见；QA 用同一地图验收
4. 异常：地图与 truth 漂移（AC 删了 map 还引用）→ 检测并提示同步

## First principles

- 系统边界：地图是 truth 的投影/支撑面，不是新 truth 源
- 不可变：AC/FSM/旅程是权威；地图只引用；验证命令必须可执行
- 可推翻假设：入口/验证命令由实现填充（源码锚定），但地图结构由冻结派生

## Domain Model

| Entity | Key fields | Notes |
|--------|------------|-------|
| FeatureMap | slug, entry_points[], verification[], reproduce[] | `features/<slug>/feature-map.md` |
| EntryPoint | ac_id, type(route/function/file/ui), path, how_to_enter | 功能入口 |
| Verification | ac_id, command, assertion, signal | 验证命令 + 信号 |
| ReproduceRoute | symptom_hint, steps[] | 模糊描述 → 定位 |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | 每个 feature 有 `feature-map.md` 骨架：entry_points + verification_commands 均绑定 AC ID；骨架随 truth 冻结派生。 |
| AC-002 | 复现路由：map 含 `reproduce[]`（symptom_hint → 定位 steps），模糊 bug 描述可路由到对应 entry/verification。 |
| AC-003 | agent 自验证：map 的 verification 命令可被 agent 执行（复用 code2truth 资产），输出可观测信号供断言。 |
| AC-004 | 单向投影：map 引用 truth（AC），不反向改 truth；不新增命令面；AC 变化时 map 漂移可检测。 |

## Domain FSM Order

| State | From | Guard |
|-------|------|-------|
| scaffolded | truth_frozen | ac_bind |
| filled | implement | source_anchored |
| routable | reproduce_added | hints_bound |
| self_verifying | agent_verified | signals_ok |

## Illegal transitions

- map → truth（反向改写）
- map 不绑定 AC 仍填充（无锚）

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| scaffolded | fill | ac_bound | filled | add_entrypoints |
| filled | route | hints_added | routable | add_reproduce |
| routable | verify | agent_runs | self_verifying | run_commands |
| self_verifying | sync | truth_stable | scaffolded | refresh |

**终态：** self_verifying（agent 可自验证）

### invalid / illegal

- map 反向改写 truth（illegal：投影越权）
- map 不绑定 AC 仍作交付（illegal：无锚）

## Non-goals

- 地图不替代 truth（不新增需求语义）
- 不自动生成入口/验证命令（由实现源码锚定填充）
- 不引入新命令面

## Freeze readiness

- [x] Intent Matrix must 无 missing
- [x] 用户旅程非「待补」占位
- [x] First principles / Domain Model 已具体化
- [x] 元状态 FSM + illegal
- [x] 每 AC ≥ 1 TC（Command+Assertion）+ exec-layer TC
- [x] tasks 均有 ac= + evidence= 绑定
- [x] package_maturity: filled
- [x] `beacon truth review` pass 后再 freeze

### Gap vs gold (订单支付示例)

- 对照：`docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md`
- 对照：`skills/beacon/beacon-truth/references/examples/gold-order-pay-package.md`

## Source Excerpt

```markdown
beacon-v1614-feature-map
设计：docs/beacon/research/beacon-feature-map-design-2026-08-27.md（骨架→复现路由→agent自验证）
调研：qxbyte/codemap（AST 确定性索引，无 LLM，SCIP+MCP）—— 作为 entry_points 索引底座评估
对接：.beacon/code2truth/（system map 资产）+ eval-real-project
```
