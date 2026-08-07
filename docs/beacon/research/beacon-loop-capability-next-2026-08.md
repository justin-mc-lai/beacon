# Research: Beacon loop 能力完善见解（第一代已运营后）

**日期**：2026-08-05
**前置**：`beacon-longrun-stability-analysis-2026-08.md`（S4/S7 缺口）、`beacon-longrun-pi-agent-evolution-2026-08.md`（三家机制对照）、`beacon-longrun-pi-agent-evolution` 落地后的运营核查
**关键事实（2026-08-05 核实）**：
- v0.0.4 vision-flywheel **已实现并运营**：`adb schedule` 命令族（register/list/show/should-run/ledger/cron-template）+ quota 记账 + heartbeat 事件流，9 项 implement evidence 齐备
- **第一个真实心跳在转**：`schedule_entries` 有 `search-boundary-curate`（0 9 * * *，quota_limit=1，health=healthy）
- v0.0.5 search-boundary-curation 已立项：双层垂直画像 + VerticalGate fail-closed + 每日 5 条待审选题推飞书 + 人工拍板

---

## 1. 现状定位：第一段弧已转，但"环"还没闭

飞轮五段弧：**调研 → 创作 → 分发 → 反馈 → 再调研**。

已转通的：调研（search-boundary 每日 5 条 → 人拍板）借助 vision-flywheel 调度底座。这是历史性的一步——**从"设计好的飞轮"变成"转起来的飞轮"**。

尚未转的：创作/分发/反馈三段。因此当前 loop 的形态是"**一个会定时出题、等人批的调研器**"，还不是"会自己迭代的自媒体系统"。

## 2. 六条完善见解（按价值排序）

### 见解 1：从"单心跳"到"心跳网络"——下一步的第一优先级
- **现状**：只有 1 条 schedule 条目（search-boundary-curate）。飞轮需要多条心跳（调研、日榜、指标采集、回流、digest）并行，且**互相交接**（调研产出 → 触发创作 → 发布 → 触发指标采集）。
- **完善方向**：
  - 心跳间**依赖与交接契约**：前一心跳的产出（如 search-boundary 的 5 条已批选题）成为下一心跳（创作调度）的输入队列——参考 kun steering-queue（32 条/64KB 有界）与 loopx handoff（delivery_contract：must_include + spend-after-validation）。
  - **hard lease（PB-FLY-7 提前）**：多心跳并行时，同一 todo 只能被一个心跳持有——loopx task_lease 的 write_scopes 冲突检测直接可移植。
  - **触发器三态演进**（kun graph-agents 启发）：`schedule → run_count → evidence_threshold`。当前只有时间触发；下一步加"证据阈值触发"（如已批选题 ≥3 条才触发创作心跳），让心跳之间"按需联动"而非"各转各的"。

### 见解 2：补反馈环——loop 从"转"到"学"的唯一路径
- **现状**：指标全 0、analyze-data 空壳（selfmedia-creator 侧）、brain-writeback 未接数据。
- **完善方向**：
  - 指标采集心跳（update-metrics.sh 激活）→ analyze-data 实现（至少微信/小红书/抖音三端）→ **回流 personal-brain**（已批选题的"表现分"写回，反哺 search-boundary 的垂直画像权重）。
  - 这是"环"闭合的最后一笔：**没有反馈，search-boundary 的选题质量无法迭代**——每天 5 条只会是"稳定的噪音"。
  - ADB 侧只需提供心跳注册与配额（已有），实现归 creator 侧（PB-FLY-1）。

### 见解 3：should-run 从"配额+健康"升级为"状态感知"
- **现状**：门卫 = quota 门卫 → 健康门卫（AC-FLY-003 已实现）。
- **完善方向**（loopx decision_summary 借鉴）：
  - 加 **terminal_no_followup 停止态**：当已批选题队列空了/目标达成，心跳自我收敛（stop_until_explicit_resume），而不是继续空转烧配额。
  - 加 **replan 义务触发**（loopx goal_frontier）：连续 N 天产出被全拒 / 长 todo 链 → 强制触发重规划（垂直画像刷新），而不是让系统在错误的方向上稳定地转。
  - 加 **workspace/capability 门卫**：目标仓库不可用（git 损坏/目录移动）时心跳应转 repair 而非 delivery。
- **本质**：让 loop 能"自己决定该停、该修、该换方向"，而非等配额耗尽被动停。

### 见解 4：补"无进展退避"——配额管成本，无进展管价值
- **现状**：配额耗尽 → throttled（管"花多少"）。
- **完善方向**（kun goal-resume-coordinator 借鉴）：连续无进展（产出未被批/无有效输出）→ 指数退避（2s×2ⁿ 封顶 60s）→ 5 次 → **blocked + 提请注意**。与 quota 互补：quota 是硬上限，无进展检测是"值不值得继续花"的软信号。对 search-boundary 尤其重要：被拒选题连续 3 天时，系统应该提示"垂直画像可能需要刷新"，而不是继续出同类题。

### 见解 5：事件溯源升级——长程恢复的根
- **现状**：heartbeat_runs 是追加账本（足够审计）。
- **完善方向**（loopx event_sourced_state 借鉴）：幂等 event_id + fingerprint 冲突检测 + 流校验和 + flock 串行。价值在"**从任意历史点重建状态**"——跨宿主（hermes 挂了换 pi）、跨轮次、跨版本的恢复能力。这是 S2（恢复）的最终形态。

### 见解 6：执行器与评测——中期接入 pi，长期建立 Δ 评测
- **执行器**：当前唯一执行面是 hermes。中期接入 pi agent（driver_pi）补创作工具链（image_gen/browser/artifact）与长程原语（steering/deadline/pause 已在 agentLoop 就绪）。
- **评测**（simple-long-horizon-agent 口径）：每个 loop 机制改进（压缩/无进展/触发三态）用 Δ vs Baseline 验收——同一任务预算下，机制带来的 score 提升 + cost/task。让"完善"从直觉变为可度量。

## 3. 架构性判断：自治度的边界才是 loop 演进的真正命题

Beacon loop 的哲学已正确且已证明有效：**不内嵌 daemon、不 auto-approve、fail-closed、人工三扇门**。这些不能动摇。

在此前提下，loop 能力完善的本质 = **在确定的边界内提高自治度**。演进阶梯：

```text
L0 人触发（手动 adb dispatch）            ← 现状起点
L1 时间触发（schedule + quota）           ← 已实现（v0.0.4）
L2 状态触发（evidence_threshold / 队列非空） ← 见解 1 的下一步
L3 自收敛触发（terminal_no_followup / replan） ← 见解 3
L4 自学习触发（反馈回流 → 画像权重更新）    ← 见解 2 的终点
```

每一级都仍有人工门兜底（拍板不撤销），但**触发权和收敛权逐渐交给系统**。这就是"loop 完善"的完整叙事：不是加更多功能，而是把"什么时候跑、什么时候停、跑完往哪走"从人逐步移交到可验证的系统。

## 4. 落地优先级（结合 v0.0.5 后的版本线）

| 优先级 | 内容 | 对应版本建议 | 依赖 |
|---|---|---|---|
| P0 | 反馈环（指标采集心跳 + analyze-data + brain-writeback） | v0.0.6（creator 侧独立或协作） | vision-flywheel（已备） |
| P0 | 心跳交接契约（产出队列 + evidence_threshold 触发） | v0.0.6 | search-boundary（已备） |
| P1 | hard lease（PB-FLY-7） | v0.0.6 | 交接契约 |
| P1 | 无进展退避 + terminal 停止态 | v0.0.7 | — |
| P1 | 事件溯源升级 | v0.0.7 | — |
| P2 | pi 执行器（driver_pi） | v0.1.x | — |
| P2 | Δ 评测口径 | v0.1.x | 任一机制改进 |

## 5. 结论

第一代 loop 底座（vision-flywheel）已经完成从"冻结"到"运营"的跃迁，且第一个业务心跳（search-boundary）验证了架构正确。**接下来的完善主线不是加机制，而是让环闭合**：

1. 反馈环（见解 2）——让 loop 能学习，飞轮才有复利；
2. 心跳网络（见解 1）——让多个 loop 交接协作，飞轮才是"轮"而不是"单臂"；
3. 状态感知（见解 3/4）——让 loop 该停就停、该换方向就换方向，自治度按 L0→L4 阶梯提升，人工门永不撤销。

这三点构成 beacon loop 能力完善的完整叙事。
