# beacon-prd-us-to-plan-implementation-progress-closure 测试用例

**版本**: v1.1.12
**Feature**: `beacon-prd-us-to-plan-implementation-progress-closure`
**状态**: Draft
**更新时间**: 2026-04-01

---

## 1. 目标

验证 Beacon 能把 `user-story + prd + test-case` 编译成 implementation plan，并在 implement / status / help / writeback 中形成任务级进度闭环，而不是只停留在 run-level / stage-level 摘要。

---

## 2. 测试分组

| 组别 | 目标 |
|---|---|
| PTP-TC-001 ~ 004 | plan compiler |
| PTP-TC-101 ~ 104 | plan artifact integrity |
| PTP-TC-201 ~ 205 | pre-implement plan gate |
| PTP-TC-301 ~ 305 | task progress model |
| PTP-TC-401 ~ 405 | traceability / writeback |
| PTP-TC-501 ~ 504 | status / help visibility |
| PTP-TC-601 ~ 603 | compatibility with implement runners |

---

## 3. Plan compiler

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| PTP-TC-001 | PRD/US-to-plan 语义存在 | 输入 user-story + prd + test-case | 生成 implementation plan | unit |
| PTP-TC-002 | plan 编译包含 source refs | 编译后读取 plan artifact | 至少包含 user-story / prd / test-case source refs | unit |
| PTP-TC-003 | plan 编译保留 frozen baseline 绑定 | 输入 frozen revision / baseline truth | plan 绑定当前 version、revision_id、baseline_hash | unit |
| PTP-TC-004 | plan 编译输出任务结构 | 读取编译结果 | 至少存在 workstreams / tasks / dependencies / status model | regression |

---

## 4. Plan artifact integrity

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| PTP-TC-101 | machine-readable artifact 存在 | 生成 plan 后读取 `.json` | 可解析，且 schema 字段完整 | unit |
| PTP-TC-102 | human-readable artifact 存在 | 生成 plan 后读取 `.md` | 可读、可引用、与 `.json` 同步 | regression |
| PTP-TC-103 | plan hash / baseline hash 一致性 | 对相同输入重复编译 | hash 稳定，未引入无关抖动 | unit |
| PTP-TC-104 | artifact 路径与 feature 绑定 | 针对不同 feature 编译 plan | 产物路径与 feature slug 一一对应 | regression |

---

## 5. Pre-implement plan gate

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| PTP-TC-201 | plan gate 先于 runner | 运行 implement | 先校验 plan readiness，再考虑 runner | integration |
| PTP-TC-202 | plan 缺失阻断 | 删除 plan artifact 后运行 implement | 返回 blocked，reason=`implementation_plan_missing` 或等价值 | integration |
| PTP-TC-203 | baseline 不一致阻断 | plan baseline_hash 与 frozen revision 不一致 | implement blocked，不进入 runner | integration |
| PTP-TC-204 | revision 不匹配阻断 | plan 绑定的 revision_id 与当前 active revision 不一致 | implement blocked | integration |
| PTP-TC-205 | source refs 不完整阻断 | plan 缺少 prd / test-case / user-story 任一 source ref | blocked，并给出修复方向 | unit |

---

## 6. Task progress model

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| PTP-TC-301 | task 状态枚举完整 | 读取 plan tasks | 至少支持 `draft / planned / in_progress / blocked / completed` | unit |
| PTP-TC-302 | task 级进度可见 | 在 plan 中标记部分任务完成 | status 能展示 task-level progress | regression |
| PTP-TC-303 | blocked task 保留原因 | 设置某 task blocked | task 包含 blocked_reason / evidence refs | unit |
| PTP-TC-304 | task 时间戳可回溯 | 任务开始/结束后读取 plan | started_at / completed_at 可追踪 | unit |
| PTP-TC-305 | task 进度不被 run summary 覆盖 | run summary 存在但 plan task 未完成 | task 状态仍以 plan 为准 | regression |

---

## 7. Traceability / writeback

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| PTP-TC-401 | AC 到 task 的映射存在 | 读取 plan tasks | 每个 task 至少能追踪 mapped_ac_ids | unit |
| PTP-TC-402 | TEST 到 task 的映射存在 | 读取 plan tasks | 每个 task 至少能追踪 mapped_test_ids | unit |
| PTP-TC-403 | writeback 更新 plan 状态 | 触发 implement / verify / accept writeback | plan task 状态同步更新 | integration |
| PTP-TC-404 | evidence refs 可回溯 | task 完成后检查 plan | 留下 evidence refs 与 changed_files | regression |
| PTP-TC-405 | story/revision/plan 一致 | 对同一 feature 查看 story / revision / plan | 三者状态不冲突，能互相解释 | regression |

---

## 8. Status / help visibility

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| PTP-TC-501 | status 展示 plan id | 查询 status | 包含 current plan id 或等价字段 | regression |
| PTP-TC-502 | status 展示下一任务 | plan 存在且有未完成任务 | 显示 next task / blocked task / task count | regression |
| PTP-TC-503 | help 解释 plan gate | plan 缺失或 baseline 不一致时调用 help | help 推荐先补 plan / 修复 baseline | integration |
| PTP-TC-504 | help/status 不混淆 stage 与 plan | stage 完成但 plan 任务未完 | 输出能区分 stage progress 与 task progress | regression |

---

## 9. Compatibility with existing implement runners

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| PTP-TC-601 | native-single 兼容 | 在 plan ready 下运行 `implement --runner native-single` | 仍可执行，且保留 plan traceability | integration |
| PTP-TC-602 | native-team 兼容 | 在 plan ready 下运行 `implement --runner native-team` | 仍可执行，且任务进度可回写 | integration |
| PTP-TC-603 | adapter runner 兼容 | 使用配置化 runner 运行 implement | plan gate 不破坏既有 adapter 语义 | regression |

---

## 10. First-principles Loop

正确链路应是：

```text
user-story + prd + test-case
→ prd-us-to-plan compiler
→ implementation plan artifact
→ pre-implement plan gate
→ implement execution
→ task progress writeback
→ status / help / review consume plan truth
```

不是：

```text
user-story + prd
→ 直接丢给 implement prompt
→ 只看 run summary
→ task progress 不可见
```

