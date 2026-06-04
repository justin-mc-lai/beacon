# Beacon v1.2.0 QA Autoresearch 使用指南

> 这份文档专门回答一个问题：  
> **如何稳定触发 Beacon 的 QA 演进 / autoresearch 风格自迭代，而不是把它误用成“无限自治修 bug 平台”？**

---

## 1. 先说结论

在当前 `v1.2.0` 中，**QA autoresearch 不是一个单独的稳定子命令**。

要稳定触发 “`PRD / Story / QA → QA 演进 → keep/review/discard → 下一轮 QA`” 这条链，推荐固定用下面这组命令：

```text
1. beacon qa run
2. beacon qa evolve
3. beacon qa audit label
4. beacon version experiment
```

也就是：

```text
固定 baseline bundle
→ 跑一次 QA
→ 计算 delta-aware rerun plan
→ 写入人工 audit truth
→ 刷新 calibration / benchmark / keep-discard
→ 跑 fixed-budget evo experiment
→ 再决定 keep / review / discard
→ 下一轮 QA
```

这才是当前 Beacon 最接近 `autoresearch` 的、同时又**符合 v1.2.0 边界**的稳定做法。

---

## 2. 它不是什么

`v1.2.0` 明确禁止把 QA autoresearch 理解成下面这种模式：

```text
一个命令
→ 自动自改整个仓库
→ 自动修代码
→ 自动直到 release 通过
```

原因很简单：

1. 这会绕开 `PRD → user-story → QA` 主链
2. 这会把 project-specific execution logic 拉回 Beacon core
3. 这会让 keep/discard 失去可比较的固定预算
4. 这会把 learning plane 变成泛化自治平台，而不是判断系统优化面

所以在 `v1.2.0` 的定义里：

> QA autoresearch 只能优化 **bounded QA policy surfaces**，不能直接接管项目执行系统或 release verdict。

---

## 3. QA autoresearch 的正式输入

`v1.2.0` 已经把 QA autoresearch 的必需输入固定为 **story-native QA baseline bundle**：

1. `PRD`
2. `user-story`
3. `AC matrix`
4. `story-scenario-map`
5. `QA9 matrix`
6. `coverage / evidence scorecard`

也就是说，任何 autoresearch 风格的 QA 演进，都必须建立在：

```text
需求真相
→ 测试真相
→ 证据真相
```

这三个层之上。

如果这些东西都没齐，就不应该直接谈 QA autoresearch。

---

## 4. 最稳定的触发方式

### 4.1 面向普通用户：自然语言入口

如果用户记不住太多命令，最稳的是：

```bash
beacon ask "帮我对「<feature>」做 QA 验收" --project-root . --version v1.2.0 --plan-only --json
```

或者：

```bash
beacon ask "帮我为「<feature>」生成 QA 演进计划" --project-root . --version v1.2.0 --plan-only --json
```

这两句最适合：

- 想让 Beacon 先给出路由建议
- 想确认下一步应该跑 QA、QA evolve、还是 release gate
- 想避免误执行

### 4.2 面向稳定执行：直接命令链

如果你已经明确要跑 QA autoresearch 闭环，推荐直接用下面这条顺序：

```bash
beacon qa run "<feature>" --project . --version v1.2.0 --mode story-exhaustive --json
beacon qa evolve "<feature>" --project . --version v1.2.0 --mode story-exhaustive --json
beacon qa audit label <run_id> <scenario_id> --label <label> --project . --json
beacon version experiment "QA autoresearch for <feature>" --version v1.2.0 --project . --json
```

---

## 5. 推荐的标准操作顺序

下面这条，是我建议你在团队里固化成 SOP 的版本。

---

### Step 0：先确认当前 feature 已具备 baseline bundle

至少应存在：

- `docs/beacon/archive/v1.2.0/prd/<feature>.md`
- `docs/beacon/archive/v1.2.0/user-story/<feature>.md`
- `docs/beacon/archive/v1.2.0/qa/test-cases/<feature>.md`
- `docs/beacon/archive/v1.2.0/.machine/qa/<feature>.ac-test-matrix.json`
- `docs/beacon/archive/v1.2.0/.machine/qa/<feature>.story-scenario-map.json`
- `docs/beacon/archive/v1.2.0/.machine/qa/<feature>.qa9-matrix.json`

如果不确定当前 feature 是否已经具备这些，先跑：

```bash
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
```

---

### Step 1：跑第一轮 QA

#### 推荐命令

```bash
beacon qa run "<feature>" --project . --version v1.2.0 --mode story-exhaustive --json
```

#### 为什么优先 `story-exhaustive`

因为如果你要做 autoresearch 风格自迭代，最好一开始就用更强的 story-native 穷尽视图，而不是只看粗粒度 pass/fail。

#### 你要重点看这些字段

- `status`
- `feature_scorecard.continue_decision`
- `feature_scorecard.coverage_gap`
- `feature_scorecard.stop_reasons`
- `feature_scorecard.repair_handoff`
- `scenario_results_v2`

#### 典型分支

##### 分支 A：已经足够好

```text
continue_decision = ready_for_release
```

说明这轮 QA 已经足够进入后续 `review / gate / release`。

##### 分支 B：需要修复

```text
continue_decision = stop_for_repair
```

说明当前结果不适合直接接受，需要进入修复或下一轮演进。

---

### Step 2：生成 QA 演进计划

#### 推荐命令

```bash
beacon qa evolve "<feature>" --project . --version v1.2.0 --mode story-exhaustive --json
```

#### 这一步做什么

这一步**不会直接跑测试**。  
它做的是：

```text
根据上一轮 QA 结果
→ 识别哪些 AC / TC / scenario 需要 rerun
→ 生成 targeted delta plan
→ 物化 feature QA matrix
```

你要重点看：

- `status`
- `reason_codes`
- `targeted_layers`
- `targeted_tc_ids`
- `targeted_scenario_ids`
- `targeted_scenario_families`

#### 这一步在 autoresearch 中的角色

它相当于：

> 下一轮实验设计器（experiment planner）

---

### Step 3：写入 audit truth

真正的 autoresearch 自迭代，不能只靠模型自评。

所以你需要把**人工确认过的真值**写回系统。

#### 推荐命令

```bash
beacon qa audit label <run_id> <scenario_id> --label false_pass --project . --json
```

#### 常见 label

- `true_pass`
- `true_block`
- `false_pass`
- `false_block`
- `runner_gap`
- `flake`

#### 这一步会触发什么

在当前实现里，这一步会：

1. 写入 `.beacon/state/qa-audits/...`
2. 刷新 `qa calibration model`
3. 刷新 `learning loop`
4. 让后续 keep/discard 实验有真实 benchmark truth

这一步非常关键，因为：

> **没有 audit truth，就只有“模型觉得自己对”，那不叫 autoresearch。**

---

### Step 4：刷新 learning plane

通常在 `qa audit label` 后，系统已经会刷新 learning loop。  
但从概念上你要知道它做了什么：

```text
technical archive inputs
+ debug issue inputs
+ QA audit inputs
→ benchmark corpus
→ keep/discard engine
→ scorecard
→ ledger
```

这里优化的不是项目业务代码，而是 Beacon 的判断系统：

- QA policy
- evidence sufficiency
- false-complete reduction
- continue/stop calibration

---

### Step 5：跑 fixed-budget evo experiment

#### 推荐命令

```bash
beacon version experiment "QA autoresearch for <feature>" --version v1.2.0 --project . --json
```

#### 这是当前最接近 autoresearch agent 的一步

因为它会基于：

- benchmark corpus
- latest scorecard
- keep/discard engine
- fixed budget contract

来跑一轮有界实验。

#### 你要重点看

- `run_id`
- `verdict`
- `main_kpi_score`
- `metrics.false_complete_rate`
- `selected_candidates`
- `score_delta`

#### 判读方式

##### keep
说明本轮选出的 QA policy candidates 值得保留

##### review
说明有一定价值，但还不够稳定，需要人工再审

##### discard
说明这一轮实验没有带来足够可信的提升

---

### Step 6：只改 bounded QA policy surfaces

如果 experiment 给出的是 keep/review，你下一轮应该改的，是这些东西：

- story scenario expansion policy
- coverage threshold policy
- evidence sufficiency policy
- continue / stop-for-repair policy
- false-complete reduction policy

而**不应该**改：

- project-specific execution commands
- release verdict override
- arbitrary repo-wide product surfaces
- memory/knowledge plane 作为独立中心

---

### Step 7：再跑一轮 QA

#### 推荐命令

```bash
beacon qa run "<feature>" --project . --version v1.2.0 --mode story-exhaustive --json
```

然后重复：

```text
qa run
→ qa evolve
→ qa audit label
→ version experiment
→ next qa run
```

这就是当前 Beacon 中最正确的“autoresearch 风格 QA 自迭代”。

---

## 6. 最稳定的命令模板

如果你要在团队里直接复制，用这组就够：

### 模板 A：路由入口

```bash
beacon ask "帮我对「<feature>」做 QA 验收" --project-root . --version v1.2.0 --plan-only --json
```

### 模板 B：跑第一轮 QA

```bash
beacon qa run "<feature>" --project . --version v1.2.0 --mode story-exhaustive --json
```

### 模板 C：生成 QA 演进计划

```bash
beacon qa evolve "<feature>" --project . --version v1.2.0 --mode story-exhaustive --json
```

### 模板 D：写人工审计真值

```bash
beacon qa audit label <run_id> <scenario_id> --label false_pass --project . --json
```

### 模板 E：跑 autoresearch 风格实验

```bash
beacon version experiment "QA autoresearch for <feature>" --version v1.2.0 --project . --json
```

---

## 7. 最适合给普通用户的自然语言触发句

如果用户记不住复杂命令，只给他这几句就够：

1. **帮我对「\<feature\>」做 QA 验收**
2. **帮我为「\<feature\>」生成 QA 演进计划**
3. **帮我检查「\<feature\>」这轮 QA 现在该继续还是停下来修**
4. **帮我检查现在是否满足 release 条件**

都建议先走：

```bash
beacon ask "..." --project-root . --version v1.2.0 --plan-only --json
```

然后再决定是否进入真实执行命令。

---

## 8. 什么时候说明“触发不稳定”

下面这些说法不够稳定：

### 不稳定说法 1

```text
帮我做 qa autoresearch
```

问题：

- `autoresearch` 不是 ask/router 的稳定高频主意图词
- 容易落不到你预期的 QA evolve / version experiment 链

### 不稳定说法 2

```text
帮我自动迭代到 QA 通过
```

问题：

- 听起来像“无限自治”
- 与 `v1.2.0` 的 bounded harness 设计相冲突

### 不稳定说法 3

```text
帮我 QA、修复、发版一条龙
```

问题：

- 一句话里有多个主意图
- 不利于稳定路由

---

## 9. 最后一条建议

如果你只想得到 **稳定、可靠、可解释** 的 QA autoresearch 闭环，请遵守下面这条：

```text
自然语言只负责路由，
真正执行固定用 qa run / qa evolve / qa audit label / version experiment 四段式。
```

这就是当前 Beacon `v1.2.0` 中最接近 `autoresearch`、同时最不容易跑偏的方式。
