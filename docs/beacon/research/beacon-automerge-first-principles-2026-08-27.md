# Research: auto-merge 第一性原理分析 —— 方法论 M4 与 Beacon release gate 并非冲突

**日期**：2026-08-27
**目的**：重新评估 Cursor 方法论 M4「信任自动合入」（auto-merge），用第一性原理拆解"合并"与"发布"两个动作的本质，纠正此前「与 Beacon release gate 冲突、不采纳」的结论。
**输入**：
- `docs/beacon/research/beacon-agent-coding-methodology-cursor-poteto-2026-08.md`（原始方法论记录）
- `docs/beacon/global-boundaries.md`（Beacon 全局边界）
- `beacon-release` skill HARD GATE（"Human gate required; auto-pass forbidden"）
- v1.6.13/14 实测：合并（worktree→main）全程由 agent 自动执行 git merge，无人类 gate
- D7 调研：gstack/loopx 均保留 merge 人类 gate；loopx 用 `user_gate` 表达

---

## 1. 第一性原理拆解：先问「合并」到底是什么

自动合入之所以被此前误判为「与 Beacon release gate 冲突」，是因为把**两个不同层级的动作**混为一谈。先拆开：

| 动作 | 本质 | 影响面 | 可回滚性 |
|------|------|--------|----------|
| **A. 合入（merge）** | 把开发分支的变更并入主干（main）| 仅仓库状态；代码还没对用户生效 | 高（`git revert` / 分支仍在）|
| **B. 发布（release）** | 判定"可以交付"，打 tag / 部署 / 对外生效 | 对真实用户生效 | 低到中（线上回滚成本高）|

**第一性原理问题：合并的不可逆性有多大？**

答案是：合并本身可逆性高（git 历史保留、可 revert、分支保留）。**不可逆的从来不是合并，而是"发布后对用户生效"**——那一步才需要最高的人类把关。方法论 M4 说的 auto-merge 落在 **A（合入）**，而 Beacon 的 release 人类 gate 约束的是 **B（发布判定）**。两者不在同一层，谈不上冲突。

## 2. Beacon 实际状态的核查（非假设）

- **合并早已自动化**：v1.6.13 / v1.6.14 全流程中，`beacon workspace admit` → worktree 实现 → QA → **`git merge` 回 main**，全程无人类 gate。所谓"人类 gate"只存在于 `release` verdict（`beacon-release` HARD GATE：`Human gate required; auto-pass forbidden`）。
- **无硬约束禁止 auto-merge**：`global-boundaries.md` 与 `beacon/` 代码中 grep `merge.*human / auto_merge / automerge` 无任何命中。人类 gate 是 release 专属，不是 merge 专属。
- **release 人类 gate 保留**：v1.6.14 发布时 `beacon hooks run post-release` 仍要求 `manual_confirmation_required`——这一步没有、也不应该被自动化。

结论：Beacon 事实上已经是「agent 自动合并 + 人类发布 gate」的形态。方法论 M4 不是要新增一个冲突机制，而是给**已经发生的自动合并**补上"安全前置条件"。

## 3. 为什么 auto-merge 是安全的（第一性原理条件）

自动合入安全，需要三个条件同时成立；**满足则合并可交给 agent，不满足则人为干预**：

### 条件 1：验证前置（合入前已证"能跑、能测"）
- 合入前必须有**自动化验证通过**的证据（beacon：QA AC↔TC 矩阵全绿 + exec-layer 测试 exit 0）。
- 方法论 M1「验证 > 生成」正是这条：agent 能自己验证，人类才不必当 verifier。
- Beacon 现状：QA 在 worktree 跑、passed 后才合并 → 条件已满足。

### 条件 2：可回滚（合入出错能低成本撤销）
- git 分支保留 + revert 是标准能力 → 合并天然满足。
- 方法论 M4 的「早上醒来在 main 上复核」隐含这一条：就算有 20 个坏 PR，也是可撤销的局部问题，不是灾难。

### 条件 3：观测与问责（事后能发现并定位问题）
- main 上有人复核 / 有 CI / 有 trace，坏变更能被发现。
- Beacon 现状：agent_trace / evidence / QA scorecard 均落盘 → 可审计。

**三条件皆满足时，阻止自动合入不是"安全"，而是"把可并行的人类时间浪费在可逆步骤上"**——这正是方法论 M5「工程管理：环境/流程/验收先行」要消除的瓶颈。

## 4. 分级模型：auto-merge 的程度由验证深度决定

不是"全自动"或"全人工"二选一，而是按证据强度分级（第一性原理：控制强度必须匹配风险强度）：

| 级别 | 验证深度 | 合并方式 | Beacon 对应 |
|------|----------|----------|-------------|
| L0 | 无验证 | 人类逐 PR 审 | 应废弃（浪费）|
| L1 | 有自动化验证（QA passed）| **agent 自动合并**，人类事后复核 main | 当前已是此形态 |
| L2 | L1 + 失败模式回归库命中 0 + 对抗式审查通过 | agent 自动合并 + 自动触发下游（如自动同步 worktree）| 下一批可强化 |
| L3 | L2 + release 门禁全绿 | **仅候选发布**：合并到 main + 打 release tag 前仍需人类 | 人类 gate 保留在此 |

**关键边界：release 人类 gate 永远在 L3 保留。** auto-merge 最多推进到 L2；L3 的"发布判定"始终是人类的。

## 5. 对 Beacon 的落地建议（不改变 release gate）

1. **显式化 L1 为设计契约**：在 `global-boundaries.md` 明确"合并自动化是合法形态；release verdict 才是唯一不可自动覆盖的人类 gate"，消除文档与现状的隐含落差。
2. **L2 强化前置**：把 v1.6.13/14 已建的「失败模式回归库 + 对抗式审查」接入合并前检查（QA passed 后、merge 前），让自动合并有更强证据背书。
3. **发布候选物**：L3 增加"release-candidate"概念——agent 可自动合并 + 构建 + 跑 release 门禁，但**不自动打 tag / 不自动部署**，最后一步 `manual_confirmation_required` 保持。
4. **不采纳的部分**：方法论 M4 中"自动部署 / 自动发布到生产"仍不采纳——那是 B 层，与 Beacon 人类 gate 真冲突。

## 6. 结论（修正此前判断）

**此前的「auto-merge 与 Beacon release gate 冲突、不采纳」判断基于概念混淆**：把 A（合入）当成了 B（发布）。第一性原理拆解后：

- auto-merge（A 层）与 Beacon 不冲突，且 **Beacon 已经在事实上执行自动合并**；
- 方法论 M4 真正值得借鉴的是给自动合并补上**安全前置条件**（验证已过、可回滚、可观测），这正是 Beacon QA-first 已经在做的；
- 人类 gate 的正确位置在 **B 层（release verdict）**，必须保留，且 v1.6.14 已验证此机制有效（post-release hook 要求人工确认）。

**更新结论：方法论 M4 部分采纳——「验证通过后自动合入 main」为合法默认；「自动发布」继续不采纳。**
