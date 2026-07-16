---
program_slug: beacon-product-goal-domain-delivery-v167
version: v1.6.7
plan_mode: interactive
scope_mode: full_parity
lake_or_ocean: 海拆湖
program_phase: P0
p4_ack: true
delegated_sub_skill: beacon-gen-truth
promotion_ref: analysis:product-goal-domain-delivery-20260716
source: "product-goal + domain-fsm + empty-castle diagnosis; loop-engineering; goal-engineering; ralph; DESIGN.md"
user_decisions:
  UD-PGD-001: product_goal_spans_full_lifecycle_not_implement_only
  UD-PGD-002: domain_fsm_and_entity_precedence_are_freeze_hard_gates
  UD-PGD-003: ralph_is_implement_subcontroller_only
  UD-PGD-004: loop_discovers_goal_finishes
  UD-PGD-005: ui_design_philosophy_bound_to_ship_gate
  UD-PGD-006: golden_fixture_positive_and_negative_required
---

# Program Manifest — Product Goal + Domain Delivery v1.6.7

## User Intent（一行）

让 **Goal 跨越 Beacon 全生命周期到交付**，强制 **业务域 FSM + 实体前置序** 冻结，持续验收证据链完善，并保证 UI 视觉交付服从设计哲学；消灭「用例绿但业务空中楼阁」。

## Utterance（stable paraphrase）

1. implement Ralph 只负责实现段长程，不能冒充 product goal。
2. Goal 必须能从意图拆解走到 release，持续验收，证据链闭合。
3. truth/US/TC 必须冻结业务有限状态机与合法序（例：先商品后订单）。
4. UI 交付要对齐 DESIGN/状态矩阵与软件设计哲学，而非仅页面可打开。
5. skill 需有冻结完整业务产品的 golden fixture（含负例）。

## Ocean → Lakes（拓扑序）

| Phase | Priority | Lake slug | 煮干点 |
|-------|----------|-----------|--------|
| 1 | P0 | `beacon-domain-fsm-authority-v167` | domain-fsm + entity-precedence 成 package 权威；freeze fail-closed |
| 2 | P0 | `beacon-golden-commerce-fixture-v167` | 正例+坏例 fixture；skill 唯一推荐完整示范 |
| 3 | P0 | `beacon-domain-fsm-qa-gate-v167` | QA 强制合法/非法转移与前置实体 |
| 4 | P1 | `beacon-product-goal-runtime-v167` | Product Goal Runtime 跨 truth→release |
| 5 | P1 | `beacon-ui-design-ship-gate-v167` | UI state matrix + DESIGN ship gate |
| 6 | P2 | `beacon-loop-discover-goal-finish-v167` | Loop 发现 / Goal 完成分工 |
| 7 | P2 | `beacon-ralph-implement-boundary-v167` | Ralph 边界：仅 implement 子控制器 |

## Non-Negotiable Boundaries

| UD | Decision |
|----|----------|
| UD-PGD-001 | Product Goal ≠ implement Ralph；Goal 完成条件含业务世界成立 |
| UD-PGD-002 | 缺 domain-fsm / entity-precedence / 非法转移覆盖 → **freeze block** |
| UD-PGD-003 | Ralph 不得替代 QA/release/truth；不得定义产品完成 |
| UD-PGD-004 | Loop heartbeat 只写 discovery STATE；Goal 负责 run-until-done |
| UD-PGD-005 | 有 UX 的 ship 必须 DESIGN + UI state matrix 对齐 FSM |
| UD-PGD-006 | Golden commerce fixture 正例可绿、坏例（无商品下单）必须 fail |

## Non-Goals

- 不在本 program 交付完整电商业务实现（fixture 为示范与门禁）
- 不替代 v1.6.7 topology/loop-goal R7 既有交付
- 不把 support checklist 伪装成已 fail-closed（必须进 package 权威 + CLI 门）

## Route Recommendation

per-lake: `beacon-gen-truth` freeze → `beacon-gen-implement` → `beacon-eval-qa` → (program) `beacon-eval-release`
