# Test Cases: Beacon 原生 implement 与 revision 生命周期闭环（v1.1.6）

**Feature**: beacon-native-implement-lifecycle-closure
**Version**: v1.1.6

## 前置 Gate 结论

- Gate0 输入完整性：Pass（已具备研究分析、现状代码判断、目标设计）
- Gate1 冲突未决判定：Pass（方向明确，无 blocker 未决）
- Gate2 AC→TC 映射：目标 100% 覆盖

## 测试用例

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | contract | 创建 feature 后默认状态为 draft | 生成 feature / revision / story 基础对象，状态为 draft |
| TC-002 | contract | refined 后执行 freeze | 生成 frozen revision，并写 baseline_hash |
| TC-003 | contract | 未 freeze 时调用 implement | 被拒绝，并返回 deterministic blocked reason |
| TC-004 | functional | `native-single` 执行实现 | 生成 implementation run，写 changed files / summary / verification |
| TC-005 | functional | `native-team` 执行实现 | planner / implementer / reviewer / tester 角色协同完成 run |
| TC-006 | contract | implement 写回 story items | `TASK-*` / `AC-*` 的 implemented 状态被回写 |
| TC-007 | contract | verify 写回 story items | `TEST-*` / `AC-*` 的 verified 状态被回写 |
| TC-008 | contract | accept 写回 story/revision | revision 与 story 状态进入 accepted |
| TC-009 | integration | status board 查看当前进度 | 能看到 current revision、implemented/verified coverage、blocked reason |
| TC-010 | contract | frozen 后发起 reopen/change | 创建新 revision，旧 revision 标记 superseded |
| TC-011 | integration | implementing 中途变更需求 | 当前 run 被 supersede，新 revision 重新 refined/freeze/implement |
| TC-012 | integration | accepted 后发起 rewrite | 保留历史 accepted revision，新 revision 重新闭环 |
| TC-013 | review | review spec 发现 drift | 能影响 item/lifecycle 状态，而非只产出 markdown 报告 |
| TC-014 | review | review quality 发现 verify 未通过 | story / revision 状态进入 blocked 或 verifying-failed |
| TC-015 | contract | markdown 与 machine state 双面一致 | human docs 能投影 machine truth，不发生主状态漂移 |
| TC-016 | regression | adapter runner 与 native runner 共存 | adapter 仍可用，但 native 为默认闭环能力 |
| TC-017 | security | reopen 不覆盖旧 revision 历史 | 旧 revision 可追踪、可审计、不可静默篡改 |
| TC-018 | recovery | 任意阶段 change/reopen 后继续 workflow continue | next_stage 计算正确，closure 重新建立 |
| TC-019 | coverage | AC/TC 覆盖率可计算 | coverage/story/ac/tc 统计可落到 status board |
| TC-020 | release-gate | accepted 前不得进入 released | release 保持 post-gate action 语义 |
| TC-021 | navigation | `beacon help` 在 draft/refined 阶段给出 freeze 建议 | next step.action=freeze，且说明 why |
| TC-022 | navigation | `beacon help` 在 frozen 阶段给出 implement 建议 | next step.action=implement，命令指向 native runner |
| TC-023 | navigation | `beacon help` 在 verifying 阶段给出 review/accept 建议 | 输出 review quality 或 accept 推荐 |
| TC-024 | diagnosis | `doctor advise` 在 blocked verify 下输出 blocked reason | 返回明确阻塞层与修复建议 |
| TC-025 | scoring | test/closure/readiness/quality score 可计算且与 status/coverage 一致 | score 输出与底层状态一致 |
| TC-026 | skill-routing | 未 freeze 时 skill contract 阻止直接 implement | 推荐 freeze 或补齐物料 |
| TC-027 | skill-routing | superseded revision 下 skill/help 转向 active revision | 不在旧 revision 上继续 implement/verify |

## 分类覆盖

- 生命周期测试
- native implement 测试
- team mode 测试
- writeback 测试
- review 联动测试
- reopen / rewrite 测试
- status / coverage 测试
- release gate 测试
- navigator/help/doctor/scoring 测试

## 风险与未决

- 风险：如果 machine state 不先落地，writeback 将无法形成正式闭环
- 风险：如果 reopen 不创建新 revision，旧闭环历史会被污染
- 风险：如果 team mode 只是外挂命令，不接 implement 主链，则复杂需求仍需要外部 adapter 才能闭环
- 风险：如果评分只是展示文案，不绑定底层 state/coverage，导航层会失真

## 执行语义

- `Pass`：原生 implement 与 revision lifecycle 可以完整闭环
- `Fail`：实现、verify、accept 中任一步无法回写或无法计算下一阶段
- `Blocked`：核心对象模型未落地（feature/revision/story/item/run）

