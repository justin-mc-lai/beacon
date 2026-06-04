# Beacon 中的 Autoresearch：模块演进与使用地图

> 这份文档回答两个问题：  
> 1. Beacon 里的 `autoresearch` 到底分散在哪些模块？  
> 2. 从 `v1.1.5` 到 `v1.2.0`，它是怎么一步步演化成现在这套 bounded QA/evo 体系的？

---

## 1. 一句话定位

Beacon 的 `autoresearch` 从来都不是“整仓自治 agent”。

它在 Beacon 中的真实含义一直是：

```text
固定 benchmark 面
→ 极小可编辑面
→ keep/discard
→ 实验账本
→ 下一轮 policy 改进
```

也就是说，它优化的是：

- QA judgement system
- design/prototype judgement system
- debug / recovery policy

而不是：

- 项目业务代码本身
- 项目部署系统
- release 最终裁决

---

## 2. 按版本看它是怎么演进的

---

### 2.1 v1.1.5：先有 eval-lab skeleton

这一版的核心不是 QA 本身，而是：

> 先把 Beacon 的自我评估和 keep/discard 机制搭出来。

#### 代表文档

- `docs/beacon/v1.1.5/prd/beacon-autoresearch-eval-lab.md`
- `docs/beacon/v1.1.5/user-story/beacon-autoresearch-eval-lab.md`

#### 这版解决的问题

1. 定义固定 benchmark 面
2. 定义最小可编辑面
3. 定义 keep/discard
4. 定义实验账本

#### 这版还没有什么

- 还没有真正以 feature-aware QA 为核心
- 还没有把 `qa run <feature>` 变成主线训练对象
- 还没有 calibration / closure outcome / release scorecard 这套 QA 精准度闭环

#### 这版的角色

> 它是 Beacon autoresearch 的实验地基。

---

### 2.2 v1.1.9 / v1.1.10：把 QA 变成训练对象

到了 `v1.1.9 / v1.1.10`，重点变成：

> 让 `qa run <feature>` 进入正式主链，并让 QA precision 成为可学习面。

#### 代表文档

- `docs/beacon/v1.1.10/prd/beacon-qa-confidence-autoresearch-closure.md`
- `docs/beacon/v1.1.10/execution/qa-confidence-data-contract.md`
- `docs/beacon/v1.1.10/execution/qa-confidence-implementation-phasing.md`

#### 新增了什么概念

1. feature-aware QA
2. `qa evolve`
3. story-exhaustive execution
4. closure outcome
5. calibrated confidence
6. browser evidence pack
7. release scorecard
8. keep/discard precision loop

#### 这版的关键提升

从：

```text
有没有 benchmark skeleton
```

变成：

```text
QA 自己就是 benchmark 主体
```

#### 这版的意义

> Autoresearch 第一次从“抽象研究闭环”变成“围绕 QA 主链的可执行闭环”。

---

### 2.3 v1.1.12：把 learning plane 和边界治理类型化

`v1.1.12` 最重要的事情不是“让 autoresearch 更强”，而是：

> 让 autoresearch 不再乱长。

#### 代表文档

- `docs/beacon/v1.1.12/prd/beacon-version-truth-profile-boundary-governance.md`
- `docs/beacon/v1.1.12/prd/beacon-prototype-design-governance-loop.md`
- `docs/beacon/v1.1.12/execution/evo-harness-contract.md`
- `docs/beacon/v1.1.12/execution/evo-scorecard-contract.md`

#### 这一版明确了什么

##### A. typed learning plane

把 learning surface 拆成：

- `qa_policy`
- `design_policy`
- `contract_policy`
- `rewrite_policy`
- `debug_policy`
- `benchmark_policy`

##### B. forbidden surfaces

明确 autoresearch 不能碰：

- project ops command
- repository code mutation
- release verdict override
- secret state
- takeover architecture truth

##### C. fixed-budget evo

把 experiment contract 固定成：

- budget
- scorecard
- ledger
- decision engine

##### D. prototype/design autoresearch

把 design / prototype 这条线也纳入 bounded autoresearch，而不是只做 QA。

#### 这版的意义

> 从“QA 学习面存在”升级成“所有学习面都必须按类型和边界受控”。

---

### 2.4 v1.2.0：把 story-native QA baseline bundle 固定下来

`v1.2.0` 不是新增无限自迭代平台，而是做了两件更重要的事：

1. 把 **story-native QA baseline bundle** 固定成正式输入
2. 把 `qa auto harness` 限制在 **bounded QA policy surfaces**

#### 代表文档

- `docs/beacon/v1.2.0/prd/beacon-v1.2.0-command-simplification-and-project-skill-workflow.md`
- `docs/beacon/v1.2.0/execution/project-skill-qa-evolution-blueprint.md`
- `docs/beacon/v1.2.0/execution/evo-harness-contract.md`
- `docs/beacon/v1.2.0/execution/evo-scorecard-contract.md`

#### 这版的关键点

##### A. baseline bundle 必须先齐

```text
PRD
→ user-story
→ AC matrix
→ story-scenario-map
→ QA9 matrix
→ coverage/evidence scorecard
```

##### B. QA autoresearch 的地位被明确定义

它是：

```text
story-native QA quality improver
```

不是：

```text
通用自迭代平台
```

##### C. `skill discover` 与 QA 演进的关系被讲清楚

`skill discover` 不是 autoresearch 的一部分，  
它只是帮助项目更容易进入同一条 QA 主链。

#### 这版的意义

> Beacon 终于把 autoresearch 的输入、边界、输出和主线关系都固定成了可交付合同。

---

## 3. 现在 Beacon 里有哪些关键模块在参与 autoresearch

下面按“职责”来拆。

---

### 3.1 `beacon/commands/qa.py`

这是**QA 主入口**。

它负责：

- `qa run`
- `qa evolve`
- `qa status`
- `qa audit label`

#### 它在 autoresearch 中的角色

```text
第一轮执行
→ delta plan
→ 审计真值写入
```

是整个自迭代链最核心的入口。

---

### 3.2 `beacon/utils/qa_feature.py`

这是**feature-aware QA 计划器和产物生成器**。

它负责：

- feature QA plan
- feature matrix materialization
- verification writeback
- scorecard 相关辅助

#### 它在 autoresearch 中的角色

```text
把 PRD/story/QA bundle 转成可执行 feature QA artifact
```

没有它，就没有稳定的 feature-aware baseline。

---

### 3.3 `beacon/utils/qa_precision.py`

这是**QA 精准度层**。

它负责：

- audit labels
- calibration model
- feature scorecard / AC closure 等精度产物

#### 它在 autoresearch 中的角色

```text
把“这轮 QA 看起来通过”转换成：
→ 可信度
→ 审计真值
→ calibration
```

它是“从 pass/fail 到 judgement system”的关键桥梁。

---

### 3.4 `beacon/utils/learning_loop.py`

这是当前 Beacon 中最接近 **autoresearch kernel** 的模块。

它负责：

- benchmark corpus
- keep/discard engine
- scorecard
- ledger
- evo experiments
- execution baseline

#### 关键函数

- `refresh_benchmark_corpus`
- `refresh_keep_discard_engine`
- `run_evo_experiment`
- `refresh_learning_loop`
- `write_evo_contract_docs`

#### 它在 autoresearch 中的角色

```text
audit truth / technical archive / debug inputs
→ benchmark corpus
→ candidate scoring
→ keep/review/discard
→ experiment log
```

如果说 `qa.py` 是“执行入口”，  
那 `learning_loop.py` 就是 “autoresearch 的实验账本与决策引擎”。

---

### 3.5 `beacon/commands/version.py`

这个模块不是版本规划而已。  
它还承接了：

```bash
beacon version experiment ...
```

#### 它在 autoresearch 中的角色

它是**固定预算实验的用户入口**。

也就是：

> 不是随便跑学习循环，而是明确启动一次受预算约束的 evo experiment。

---

### 3.6 `beacon/commands/auto_test.py`

这是底层测试执行层。

它负责：

- 执行 QA9 matrix
- 收集 evidence
- 写 auto-test status
- 写 spec fingerprint

#### 它在 autoresearch 中的角色

```text
没有真实测试执行和证据，
autoresearch 就没有真实 benchmark truth。
```

所以它不是“学习模块”，但它是学习链的证据底座。

---

### 3.7 `beacon/commands/gate.py`

这是最终治理层。

#### 它在 autoresearch 中的角色

它告诉你：

> 即使 learning/evo 看起来不错，也不能绕过 gate。

也就是说，autoresearch 的输出只能成为：

- review 输入
- gate 输入增强

不能替代最终 release verdict。

---

### 3.8 `beacon/utils/project_skills.py`

这个模块本身不是 autoresearch 核心，但它很关键。

因为它决定：

```text
项目的 verify/delivery/debug 执行真相
```

而 `v1.2.0` 明确规定：

> autoresearch 不能直接学习项目私有执行面，只能学习 Beacon 的判断面。

所以它在整个体系中的角色更像：

- boundary provider
- execution truth boundary

---

## 4. 当前最推荐的完整调用链

如果你要在 Beacon 里做 **autoresearch 风格 QA 演进**，当前最稳的顺序就是：

### Step 1
```bash
beacon qa run "<feature>" --project . --version v1.2.0 --mode story-exhaustive --json
```

### Step 2
```bash
beacon qa evolve "<feature>" --project . --version v1.2.0 --mode story-exhaustive --json
```

### Step 3
```bash
beacon qa audit label <run_id> <scenario_id> --label false_pass --project . --json
```

### Step 4
```bash
beacon version experiment "QA autoresearch for <feature>" --version v1.2.0 --project . --json
```

### Step 5
```bash
beacon qa run "<feature>" --project . --version v1.2.0 --mode story-exhaustive --json
```

这就是当前最可靠的“agent 自迭代”近似实现。

---

## 5. 现在还没做到什么

`v1.2.0` 仍然**没有**做这些事：

1. 没有一个叫 `qa autoresearch` 的单命令总入口
2. 没有自动无限循环直到 release pass
3. 没有自动修改任意项目代码
4. 没有把 keep/discard 结果直接强行写回 release verdict
5. 没有把 project-specific execution logic 纳入 learning surface

这些都不是缺陷，而是当前版本的**有意边界**。

---

## 6. 最适合写进教程的一句话

如果你要对外解释 Beacon 里的 autoresearch，我建议统一用这句：

> Beacon 的 autoresearch 不是“自动改仓库直到通过”，而是“围绕 PRD / Story / QA baseline bundle，对 QA judgement policy 做 fixed-budget、keep/discard-governed 的受控演进”。  

这句话最不容易把用户带偏。
