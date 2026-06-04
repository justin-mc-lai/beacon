# Beacon v1.1.9 Closure Loop Blueprint

## 目标

回答一个具体问题：

> 如何基于 **现有 Beacon 功能特性**，把 v1.1.9 做成真正的闭环，并覆盖：
> - debug 健壮性
> - qa 验证健壮性
> - 需求到实现健壮性
> - 技术实现反哺清晰

---

## 总体策略

不是新增一条“v1.1.9 专属主链”，而是把现有能力编成 4 个子闭环：

| 闭环 | 当前基础 | v1.1.9 补强 | 结果 |
| --- | --- | --- | --- |
| Debug 健壮性 | `debug` + `workflow_memory` + `resume` | exhaustion / checkpoint / mode switch | 失败可恢复、不会重复踩坑 |
| QA 健壮性 | `qa` + session + `review quality` + `gate` | evidence hard-stop / delta rerun | 验证不流于“跑过一次” |
| 需求到实现健壮性 | `workflow` + `implement` + `review spec` + coverage | trace contract / writeback discipline | 需求、实现、证据三层不漂移 |
| 技术实现反哺清晰 | technical archive + debug ideas + version research | archive→requirement bridge / baseline uplift | 技术事实能直接反哺下一轮版本 |

## 当前代码级现实判断（补充）

这份蓝图现在不仅基于设计目标，也基于当前实现现实：

### 已经成立
- 正式 release-line 主链是强闭环的
- freeze / reopen / review / gate / release 已有正式治理
- coverage / spec fingerprint / baseline snapshot 已进入正式检查面

### 仍未完全成立
- anti-drift 还没有覆盖全部入口端口（README / root skill / packaged skill / CLI / installed copies / managed blocks）
- baseline 语义还分散在 `revision_state`、`story_state`、`v110_baseline`
- calibrated confidence 仍未落地
- closure outcome taxonomy 仍未落地

所以这份蓝图里的“闭环增强”现在要被理解成两部分：

1. **把已有强主链继续做严**
2. **把当前仍松散的入口/QA/恢复层正式收口**

---

## 1. Debug 健壮性闭环

### 当前 Beacon 已有基础

#### A. 反馈采集
- `beacon debug enable`
- `beacon debug sync-prompts`
- `beacon debug project-feed`
- `beacon debug harvest`
- `beacon/utils/debug_feedback.py`

#### B. 生命周期记忆
- `beacon/utils/workflow_memory.py`
- 已有 stage_started / stage_failed / memory_writeback / checkpoint 类事件

#### C. 恢复能力
- `beacon resume`
- `beacon workflow continue`

### 当前断点

当前 debug 更像“采集器”，还不是“控制器”：

1. 没有 failure streak / escalation level
2. 没有“必须切换策略”的正式语义
3. checkpoint 恢复时还缺少：
   - 已尝试路径
   - 已排除原因
   - 下一假设
   - 当前 evidence gap

### v1.1.9 补强建议

#### 1) 增加 Exhaustion State
建议新增：

```text
.beacon/state/exhaustion.json
```

最小字段：
- `failure_streak`
- `escalation_level`
- `last_failed_stage`
- `attempted_strategies[]`
- `excluded_causes[]`
- `next_hypothesis`
- `evidence_gap[]`

#### 2) 增加 Escalation Contract

- `E1`: 必须换本质不同方案
- `E2`: 必须补一手文档 / 源码 / 假设验证
- `E3`: 必须提交 exhaustiveness checklist
- `E4`: 只能进入 recoverable loop 或结构化失败边界

#### 3) Debug → Version 回流

把 `debug harvest` 产出的：
- 高频 reason_code
- 高频 workaround
- 高频 friction_summary

直接写入下一轮：
- version research
- execution baseline
- evo benchmark corpus

### 形成的闭环

```text
runtime failure
→ debug feedback
→ escalation
→ strategy switch
→ resume/continue
→ harvest
→ version input
```

---

## 2. QA 验证健壮性闭环

### 当前 Beacon 已有基础

#### A. QA 主入口
- `beacon qa run`
- `beacon qa status`
- `beacon qa session save|list|use|show`

#### B. QA 状态面
- `.beacon/qa/status.json`
- `.beacon/qa/sessions/<session_id>/manifest.json`

#### C. 质量与门禁
- `beacon review quality`
- `beacon gate check release`
- `beacon/commands/gate.py` 中的大量 evidence / coverage / qa9 / compatibility 检查

### 当前断点

1. “实现完成”与“证据完成”还没有明确拆层
2. QA rerun 还缺少 requirement delta 驱动
3. QA failure 与 implement/debug 的回流还不够正式
4. `qa run` 当前不是 feature-aware
5. QA 当前并不会按 user-story / AC 顺序逐项推进

### v1.1.9 补强建议

#### 1) Completion Contract 拆层

至少拆成：
- `implementation_done`
- `evidence_done`

只有同时满足，才能进入：
- `review quality`
- `gate-ready`
- `release-ready`

#### 2) QA Delta Rerun

基于：
- `workflow_memory` 的 stage context
- `technical-implementation-*` 的 changed_files / api_changes / db_changes
- `coverage` 的 story/ac/tc 缺口

自动判断：
- 哪些 test cases 必须重跑
- 哪些 session 仍可复用
- 哪些 evidence 已失效

#### 3) QA Failure 路由

- 需求不清 → 回 `think / user-story / prd`
- 实现漂移 → 回 `implement / review spec`
- 环境/数据问题 → 回 `debug`
- 证据缺失 → 卡在 `gate`

#### 4) Feature-aware 顺序验证

v1.1.9 已从：

```text
qa run qa9
→ matrix/layer execution
```

增强为：

```text
qa run <feature>
→ resolve feature materials
→ load user-story / test-case matrix
→ verify in user-story / AC order
→ write back per item
```

这已经让“实现完毕后根据用户故事依次进行 QA 验证”成为正式实现面；下一步 v1.1.10 再补 calibrated confidence / closure outcome / QA precision training。

### 形成的闭环

```text
qa run
→ evidence capture
→ review quality
→ gate
→ delta detection
→ targeted rerun
→ release readiness
```

---

## 3. 需求到实现健壮性闭环

### 当前 Beacon 已有基础

#### A. 主链与上下文
- `beacon workflow`
- `beacon/utils/workflow_memory.py`
- stage context / attempt / writeback

#### B. 实现归档
- `beacon implement run`
- `implementation-summary-*.md/json`
- `technical-implementation-*.md/json`

#### C. 审查与覆盖
- `beacon review spec`
- `beacon review quality`
- `beacon/utils/coverage.py`

### 当前断点

1. requirement → implementation → evidence 的 contract 还不够显式
2. artifact_updates 虽有，但还没有升级为必须闭环动作
3. spec review / quality review 产出的建议尚未强制进入下一轮写回
4. baseline / fingerprint / snapshot 的 canonical relation 还不够单中心

### v1.1.9 补强建议

#### 1) 三层 Trace Contract

为每个 feature 强制形成三层关系：

- **Requirement layer**
  - user story
  - AC
  - test-case
- **Implementation layer**
  - changed_files
  - modules_touched
  - api/db/config changes
- **Evidence layer**
  - verification
  - QA evidence
  - gate evidence refs

#### 2) Artifact Update Discipline

`artifact_updates` 不应只是提示，而应成为：
- writeback 待办
- gate 关注项
- resume 时的 next action

#### 3) Review 结果回写到材料

建议让 `review spec / quality` 的关键 recommendations 能落到：
- PRD 修订点
- test-case 补强点
- version research 风险项

### 形成的闭环

```text
requirements
→ implement
→ technical archive
→ review spec/quality
→ coverage & gate
→ requirement writeback
```

---

## 4. 技术实现反哺清晰闭环

### 当前 Beacon 已有基础

#### A. Runtime Raw
- `.beacon/implement/<run_id>/request.json`
- `.beacon/implement/<run_id>/result.json`
- `.beacon/implement/<run_id>/stdout.log`
- `.beacon/implement/<run_id>/stderr.log`

#### B. Technical Archive
- `technical-implementation-<feature>.md`
- `technical-implementation-<feature>.json`

#### C. 反馈出口
- `debug harvest`
- `debug export-ideas`
- `docs/beacon/archive/v1.1.9/version/*.md`

### 当前断点

目前更多是“技术事实被保存了”，但还没有完全做到：

```text
技术事实
→ 需求重写输入
→ 下轮基线提升
```

### v1.1.9 补强建议

#### 1) Archive → Requirement Bridge

从技术归档中提取：
- 高频变更模块
- 高频风险类型
- 高频 rollback 注意点
- 高频 artifact_updates

映射回：
- 需求模板需要补什么
- QA 模板需要补什么
- debug baseline 要求补什么

#### 2) Execution Baseline Uplift

把高频成功动作升级成默认义务，例如：
- 改 API 必须写 api_changes
- 改数据必须写 db_changes / rollback_notes
- 改前端必须补受影响 evidence
- claim done 前必须有 verification 列表

#### 3) 形成 Keep / Discard 输入

technical archive 与 debug harvest 一起组成 v1.1.9 evo harness 的真实 benchmark corpus，而不是靠纯 synthetic prompt。

### 形成的闭环

```text
technical archive
→ structured learning
→ requirement/test/debug baseline uplift
→ next version design
```

---

## 推荐实现顺序

### P0
1. `evidence hard-stop`
2. `exhaustiveness escalation`
3. `checkpoint / resume contract`
4. `trace contract (requirement → implementation → evidence)`

### P1
5. `qa delta rerun`
6. `artifact_updates as writeback obligation`
7. `archive → requirement bridge`
8. `feature-aware qa run`
9. `story-sequential qa writeback`

### P2
10. `evo harness`

---

## 最终判断

v1.1.9 最有价值的地方不是“做更多命令”，而是让已有能力之间形成正式约束：

- Debug 不是只收集日志，而是能升级执行强度
- QA 不是只跑测试，而是能判断证据是否真正完成
- Workflow 不是只把文档串起来，而是能把需求、实现、证据压成一条可追溯链
- Technical archive 不是只做归档，而是要反哺下一轮需求、测试、debug baseline

## 一句话总结

> v1.1.9 应把 Beacon 现有能力编织成四个子闭环：**失败可恢复、验证可追责、需求与实现不漂移、技术事实能反哺下一轮版本。**
