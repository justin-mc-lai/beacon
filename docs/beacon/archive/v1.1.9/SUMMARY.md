# Beacon v1.1.9 Summary

**主题**: 在 v1.1.8 五线闭环之上，引入 exhaustiveness / evidence / recovery / evo 的跨层控制闭环  
**状态**: Implemented / Verified  
**日期**: 2026-03-27

---

## 一句话结论

v1.1.9 不应再被定义成“新增一条独立功能线”，而应被定义成：

> **给 v1.1.8 已有的 `workflow / implement / qa / debug / review / gate / release` 套上一层更强的执行控制与反馈回流机制。**

也就是把 Beacon 从：

```text
requirements / evidence / gate kernel
```

推进为：

```text
requirements / evidence / gate / exhaustiveness / recovery / evo kernel
```

---

## 当前已经具备的闭环基础（v1.1.8 现状）

Beacon 不是从零开始做 v1.1.9。

当前已经有 4 组非常关键的基础能力：

1. **需求主链与生命周期记忆**
   - `beacon/commands/workflow.py`
   - `beacon/utils/workflow_memory.py`
   - 已有 `think → user-story → prd → [prototype] → test-case → implementation → verify → gate`
   - 已有 stage context、attempt、writeback、resume/continue 语义

2. **QA 主入口与 session 治理**
   - `beacon/commands/qa.py`
   - `beacon/utils/qa_runtime.py`
   - 已有 `qa run / status / session save|list|use|show`
   - 已有 `.beacon/qa/sessions/`、当前 session 指针、canonical QA status

3. **技术实现归档与需求回写**
   - `beacon/commands/implement.py`
   - `beacon/commands/review.py`
   - 已有 `implementation-summary-*`、`technical-implementation-*`
   - 已有 spec review / quality review / artifact_updates / traceability

4. **Debug 反馈采集与问题/想法收敛**
   - `beacon/commands/debug.py`
   - `beacon/utils/debug_feedback.py`
   - 已有 debug mode、prompt sync、project-feed、harvest、issue/idea 聚合
   - 已有 `.beacon/debug/runs/`、`.beacon/debug/issues/`、`.beacon/debug/ideas/`

再加上：

5. **Gate / Release 证据硬检查骨架**
   - `beacon/commands/gate.py`
   - 已有大量 `reason_code`
   - 已有 traceability、evidence、coverage、QA9、delivery manifest、prototype contract 等检查点

所以 v1.1.9 的正确方向不是“发明一个全新 Beacon”，而是：

> **把这些已存在能力编织成真正抗失败、抗漂移、抗假完成、能持续学习的闭环。**

---

## v1.1.9 要解决的 4 个核心闭环

### 1. Debug 健壮性闭环

目标不是只“记录失败”，而是形成：

```text
failure signal
→ escalation
→ strategy switch
→ evidence check
→ recover / resume
→ issue / idea harvest
→ next version input
```

现有基础：
- `debug enable / sync-prompts / project-feed / harvest`
- `workflow_memory` 的 stage / attempt / checkpoint 事件
- `resume` / `workflow continue`
- `gate` reason codes

v1.1.9 补强点：
- failure streak / escalation state
- 方法论切换（debug / research / delivery / refactor）
- 结构化失败边界
- checkpoint 恢复时自动带回已排除路径 / 下一假设 / 证据缺口

### 2. QA 验证健壮性闭环

目标不是只“执行一次 QA”，而是形成：

```text
test scope
→ session restore
→ evidence execution
→ review quality
→ gate contract
→ delta rerun
→ release readiness
```

现有基础：
- `beacon qa` 主入口
- QA session manifest
- `review quality`
- `gate check release`
- coverage / evidence / qa9 / compatibility / delivery 检查

v1.1.9 补强点：
- implementation_done 与 evidence_done 拆分
- claim ↔ evidence 绑定更严格
- 需求/实现变更后自动识别增量重跑范围
- QA failure 直接回流 debug / implement / version planning
- `qa run <feature>` 的 feature-aware 入口
- 按 user-story / AC 顺序依次验证，而不只停留在 scope/layer 执行

### 3. 需求到实现健壮性闭环

目标不是只“从 PRD 走到实现”，而是形成：

```text
requirements
→ stage context
→ implement run
→ technical archive
→ spec review
→ quality review
→ coverage/gate
→ writeback
```

现有基础：
- workflow stages + lifecycle memory
- stage context / attempt / writeback
- implement summary + technical archive
- review spec + review quality
- coverage metrics

v1.1.9 补强点：
- 需求项 → 实现项 → 证据项 三层 trace contract 更明确
- implement 输出必须声明 artifact_updates / known_risks / rollback_notes
- review 结果要能反向驱动 PRD / user-story / test-case 修订，而不是只生成报告

### 4. 技术实现反哺清晰闭环

目标不是只“归档实现结果”，而是形成：

```text
implementation raw
→ technical archive
→ review recommendations
→ debug ideas/issues
→ version research
→ next requirement rewrite
```

现有基础：
- `.beacon/implement/<run_id>/request|result|stdout|stderr`
- `technical-implementation-*.md/json`
- `artifact_updates`
- `debug harvest` / `export-ideas`

v1.1.9 补强点：
- 技术归档到需求修订的正式桥接
- 从“有归档”升级到“归档可直接生成下一轮输入”
- 将高频 friction / workaround / rollback pattern 升级为 execution baseline

---

## 当前代码级现实判断（新增）

本轮已基于当前仓库代码补充一个更明确的现实判断：

### 已经比较强的部分
- 正式交付主链（workflow → freeze/reopen → implement → review → gate → release）已经比较强闭环
- spec fingerprint / baseline snapshot / coverage / delivery manifest 已具备正式检查

### 尚未完全闭环的部分
- anti-drift 还没有覆盖“所有生命周期 + 所有端口”
- baseline / fingerprint / snapshot 仍存在多中心语义
- README / skill / CLI 在 QA 心智上仍有 feature-oriented vs scope-oriented 偏差
- 置信度仍主要体现为 exhaustiveness / evidence hard-stop，而不是校准后的 closure confidence
- QA 学习面已具备 keep/discard/evo skeleton，但还未进入 QA precision 训练闭环

因此 v1.1.9 的新增 requirement 不只是增强 runtime，还要增强：

```text
lifecycle anti-drift
+ surface anti-drift
+ feature-aware sequential QA
```

---

## v1.1.9 的已落地定位：跨层控制面，而不是再堆功能面

建议把 v1.1.9 定义成 3 层：

### A. Delivery Plane（沿用 v1.1.8）
- `init`
- `prototype`
- `workflow`
- `implement`
- `qa`
- `review`
- `gate`
- `release`

### B. Control Plane（v1.1.9 已落地重点）
- exhaustiveness escalation
- evidence hard-stop
- execution mode router
- checkpoint / resume contract
- recoverable loop contract

### C. Learning Plane（v1.1.9 已落地重点）
- debug harvest → issue / idea
- technical archive → requirement rewrite
- version research → keep/discard
- evo harness → 小范围、固定预算、自进化试验

---

## 最小闭环图

```text
think / user-story / prd / test-case
→ implement
→ technical-implementation archive
→ qa / verify
→ review quality / gate
→ debug harvest / issue / idea
→ version research / closure blueprint
→ next requirement update
```

如果更具体一点：

```text
需求变更
→ workflow_memory 记录上下文与 attempt
→ implement 产出 runtime raw + technical archive
→ qa 使用 session 与 evidence 执行验收
→ review/gate 判断是否真闭环
→ debug 收集失败/摩擦/高成本 workaround
→ version 形成下一轮 keep/discard 与 baseline 提升
```

---

## v1.1.9 建议优先级

### P0
1. Evidence Hard-Stop
2. Exhaustiveness Escalation
3. Checkpoint / Resume Contract
4. Requirement → Implementation → Evidence Trace Contract

### P1
5. Execution Mode Router
6. QA Delta Rerun / Drift-aware Verification
7. Technical Archive → Requirement Rewrite Bridge

### P2
8. Evo Harness（极小可编辑面 + 固定预算 + keep/discard）

---

## 本轮新增物料

- `execution/index.md`
- `execution/architecture-blueprint.md`
- `execution/closure-loop-blueprint.md`
- `prd/beacon-closure-control-learning-overlay.md`
- `user-story/beacon-closure-control-learning-overlay.md`
- `qa/test-cases/beacon-closure-control-learning-overlay.md`
- 既有研究输入继续作为上游：
  - `research/beacon-pua-exhaustiveness-layer-analysis.md`
  - `research/beacon-karpathy-autoresearch-evo-analysis.md`
  - `version/beacon-v1.1.9-exhaustiveness-research.md`

---

## 一句话总结

> v1.1.9 已把 v1.1.8 已有能力通过 exhaustiveness、evidence、resume、debug harvest、technical archive writeback 串成 **更抗失败的真闭环**；下一步 v1.1.10 再做 QA precision / confidence / autoresearch training closure。
