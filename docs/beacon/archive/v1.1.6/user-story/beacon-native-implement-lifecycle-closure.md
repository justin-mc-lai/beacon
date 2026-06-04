# User Story: Beacon 原生 implement、revision 生命周期与 item 回写闭环（v1.1.6）

**Feature**: beacon-native-implement-lifecycle-closure
**Version**: v1.1.6

**As a** Beacon 使用者 / 维护者 / AI 协作执行者
**I want** Beacon 自带原生实现能力、可冻结/重开/重写的 revision 生命周期，以及 story item 级 writeback 机制
**So that** 需求从草稿、冻结、实现、测试、验收到重开重闭环都能形成确定性、可追踪、可审计的正式流程。

## Story Slices

### US-001: 需求从 draft 到 frozen 的正式冻结
作为 Beacon 使用者，我希望需求文档能从 draft/refined 正式进入 frozen，以便 implementation 有稳定基线。

### US-002: Beacon 提供默认 native implement runner
作为 Beacon 使用者，我希望不依赖外部 adapter 也能触发 implementation，以便 workflow 默认可闭环。

### US-003: implement 结果直接回写到 story items
作为 Beacon 维护者，我希望 implementation / verify / accept 能直接回写 AC/TASK/TEST 项状态，以便 status 与 closure 可验证。

### US-004: 需求在任意阶段可 reopen / rewrite
作为 Beacon 使用者，我希望在 frozen、implementing、verify、accepted 阶段都能发起 change/reopen，以便需求变化后可以重新闭环。

### US-005: Beacon 支持 native-team 多角色实现模式
作为 Beacon 使用者，我希望 Beacon 支持多角色 agent 协作实现，以便复杂需求也能原生闭环。

### US-006: Beacon 提供 lifecycle-aware help / doctor / skill 导航器
作为 Beacon 使用者或 agent，我希望系统能明确告诉我当前阶段、下一步动作、阻塞原因与测试评分，以便我不需要猜命令也能正确闭环。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Lifecycle | 需求生命周期至少包含 `draft / refined / frozen / superseded / archived` |
| AC-002 | Delivery | 实现生命周期至少包含 `idle / implementing / implemented / verifying / accepted / released` |
| AC-003 | Freeze Gate | 没有 frozen revision 不允许进入 implement |
| AC-004 | Revision Binding | implementation run 必须绑定 `revision_id` |
| AC-005 | Native Runner | Beacon 默认提供 `native-single` runner |
| AC-006 | Team Runner | Beacon 默认提供 `native-team` runner |
| AC-007 | Story Object | user story 不再只是 markdown，必须有 machine-backed object |
| AC-008 | Stable IDs | AC / TASK / TEST item 必须有稳定 id |
| AC-009 | Implement Writeback | implement 完成后可回写 `implemented_by_run_id` 与 item 状态 |
| AC-010 | Verify Writeback | verify 完成后可回写 `verified_by_run_id` 与 item 状态 |
| AC-011 | Accept Writeback | accept 是正式动作，可回写 `accepted_at / accepted_by` |
| AC-012 | Human/Machine Split | markdown 是 human projection，machine JSON 是状态真相 |
| AC-013 | Reopen Frozen | frozen 后需求变更时必须产生新 revision |
| AC-014 | Reopen Implementing | implementing 中途需求变更时必须允许 supersede 到新 revision |
| AC-015 | Reopen Accepted | accepted 后发现需求变化时必须允许新 revision 重开闭环 |
| AC-016 | History Safety | reopen / rewrite 不允许直接污染旧 revision 历史 |
| AC-017 | Status Board | status board 能展示 current revision、story/item 覆盖率、closure completeness、blocked reason |
| AC-018 | Review Coupling | review spec / quality 能影响 item 或 lifecycle 状态，而不是只写报告 |
| AC-019 | Team Roles | native-team 最小支持 planner / implementer / reviewer / tester 四角色 |
| AC-020 | Determinism | 任意阶段重入后的 next stage 与 closure 计算必须可确定、可追踪 |
| AC-021 | Help Command | 系统提供 `beacon help`，能输出当前阶段、active revision、next step 与推荐命令 |
| AC-022 | Doctor Advice | `doctor` 除诊断外，还能解释 blocked reason 并给出修复建议 |
| AC-023 | Scoring | 系统输出 `test_score / closure_score / readiness_score / quality_score` |
| AC-024 | Skill Routing | Beacon skill / prompt contract 必须按 stage 正确路由命令 |
| AC-025 | Freeze Routing | 未 freeze 时，skill/help 不得直接建议 implement |
| AC-026 | Reopen Routing | change/reopen 条件出现时，skill/help/doctor 必须优先建议 revision 动作 |

## 前置条件

- 已存在 `workflow.py` 主链与 `workflow_memory.py` 生命周期事件账本
- 已存在 `implement.py` adapter shell
- 已存在 `review.py` / `status.py` / `team.py` 基础能力
- v1.1.6 将沿用 `docs/beacon/<version>/` 作为正式 source of truth

## 交付语义

- `Ready`：需求与设计已完整，可以进入实现
- `Blocked`：若 revision / writeback / lifecycle 任一关键能力缺失，则不能认为 v1.1.6 已闭环

## Warn 风险

- 若只实现 native runner 而不实现 writeback，closure 仍不成立
- 若只实现 reopen 而没有 revision supersede contract，会污染历史状态
- 若 team 模式与 implement 主链割裂，复杂需求仍无法原生闭环
- 若没有 help/doctor/scoring，用户和 agent 仍会在闭环中迷失下一步动作

