# 调研：Beacon v1.1.9 从 karpathy-autoresearch 借鉴自进化（evo）机制

**日期**：2026-03-26  
**来源**：`oss-sync/automation/autoresearch/karpathy-autoresearch/README.md`  
**目标**：把 `autoresearch` README 里的核心设计思想转译成 Beacon v1.1.9 可落地的自进化（evo）机制，而不是停留在“自动研究”概念层。

---

## 1. 调研对象的第一性原理

`karpathy/autoresearch` README 的关键不是“让 agent 自己改代码”，而是它把研究问题收缩成了一个极简可比较闭环：

1. **真实但小的目标系统**
2. **极小可编辑面**
3. **固定时间预算**
4. **单一主指标**
5. **保留 / 丢弃（keep/discard）**
6. **实验日志**
7. **人类改组织说明，不直接下场改主体代码**

README 里最重要的结构是：

- `prepare.py`：固定常量与准备逻辑，不改
- `train.py`：唯一允许 agent 迭代的文件
- `program.md`：人类修改的“研究组织代码”

第一性原理结论：

> autoresearch 成功的关键不是“让 AI 自由发挥”，而是 **把自由收缩到一个极小、真实、可比较、可回滚的试验面**。

---

## 2. README 里最值得 Beacon 注意的设计点

## 2.1 主体代码与组织代码分离

在 autoresearch 里：

- agent 主要改 `train.py`
- 人类主要改 `program.md`

这意味着：

- **研究对象本身** 与 **驱动研究的组织规则** 分离
- 不会把“改代码”和“改 agent 协议”混成同一个面

### 对 Beacon 的启发

Beacon 的自进化也应分成两层：

1. **subject surface**
   - 被评估的 Beacon 规则/策略面
2. **org/program surface**
   - 驱动 Beacon 评估与 keep/discard 的组织说明面

也就是：

> 不要让 Beacon 一上来“自改整仓”，而要先区分“被优化对象”和“优化协议”。

---

## 2.2 极小可编辑面

autoresearch README 明确强调：

- repo 很小
- 只有一个核心文件让 agent 改
- 单文件可让 diff 易审阅

### 对 Beacon 的启发

Beacon v1.1.9 的 evo 面不能是整个仓库，而必须是极小可编辑面。

候选面应优先是：

- prompt / policy 层
- doctor 规则层
- review/gate 严格度规则层
- drift extractor / comparator 层
- execution policy 层

不应先纳入：

- CLI 全量代码树
- runtime orchestration 本体
- 外部 runner 复杂实现

这和 v1.1.5 `autoresearch-inspired Eval Lab` 的方向一致，但 v1.1.9 需要再向前推进一层：  
从“定义可编辑面”推进到“定义如何做可比较 evo 实验”。

---

## 2.3 固定时间预算

README 的关键设计之一是：

- 每次训练固定 **5 分钟 wall clock**
- 不因 agent 改了模型结构、batch size 等而改变评估预算

这样做的价值是：

1. 结果可比
2. agent 不能靠“偷偷加预算”伪造改进
3. 同一平台上可以稳定累积实验

### 对 Beacon 的启发

Beacon 的 evo 不一定是“5 分钟训练”，但应借这个原则：

> 每次自进化试验必须在固定预算下运行。

可以固定：

- 最大迭代轮数
- 最大 wall-clock 时间
- 最大验证命令数
- 最大 token / model budget

否则 Beacon 的 evo 会退化成：

- 试验不公平
- 成本不可比
- 改进无法归因

---

## 2.4 单一主指标

autoresearch README 选择：

- `val_bpb`
- lower is better
- 且 metric 与 vocab-size 无关，减少架构变化带来的比较失真

这说明它非常重视：

> **指标必须足够稳定、足够单一、足够能代表进步**。

### 对 Beacon 的启发

Beacon 的 evo 不能只靠“感觉更好”。

v1.1.9 应至少定义：

### 核心主指标（建议）
- completion evidence reliability
- false-complete rate
- repeated-failure recovery success
- claim/evidence mismatch rate

### 次级指标（建议）
- human cognitive load
- drift detection quality
- repair success
- cost / latency

也就是：

> 自进化必须有 **一个主 KPI + 若干防作弊副指标**，不能只有 narrative judgement。

---

## 2.5 keep/discard 纪律

README 里的核心闭环是：

- 改动
- 运行
- 看是否更好
- keep 或 discard
- 重复

这和 Beacon v1.1.5 里的 Eval Lab 理念完全同向，但 autoresearch 更强调：

> 不是持续堆 patch，而是每次实验都必须接受留下还是丢弃的裁决。

### 对 Beacon 的启发

Beacon v1.1.9 的 evo 应从“研究账本”继续推进到：

- 一次实验只能有一个有限改动面
- 每次实验必须有 keep/discard verdict
- discard 不是失败，而是正常输出

建议显式物料：

- `execution/evo-keep-discard-policy.md`
- `.beacon/state/evo/ledger.jsonl`

---

## 2.6 真实但小，而不是玩具 Demo

README 不是 toy prompt，它让 agent 在一个真正会训练、真正有 metric、真正会产生成本的系统上实验。

### 对 Beacon 的启发

Beacon 的 evo 也不应该只在“模拟文本样例”里打转。

应至少挂住一个真实工作闭环，例如：

- doctor / gate / review 的真实输入样本
- 真实的 docs/beacon version package
- 真实的 claim/evidence mismatch case
- 真实的 drift extraction case

也就是：

> Beacon evo 的 benchmark 必须来自真实交付场景，而不是纯 synthetic prompt。

---

## 2.7 自进化的是“研究组织代码”

README 有一句很关键：

> 你真正编程的，不只是 Python，而是 `program.md` 里的研究组织。

这对 Beacon 的启发特别大。

Beacon 如果做 evo，真正应该迭代的不只是：

- doctor heuristics
- prompt policies

还包括：

- 哪些角色参与
- 哪个阶段先跑
- 失败后如何切换策略
- 哪些检查是 mandatory
- 哪些证据才算 completion

也就是：

> Beacon 的 evo 不只是 rule tuning，还应该包括 **workflow org code**。

---

## 3. Beacon v1.1.9 最值得吸收的 7 个 evo 借鉴点

## 3.1 Subject Surface / Program Surface 分离

建议分层：

### Subject Surface
- execution policies
- doctor rules
- review/gate heuristics
- drift comparators

### Program Surface
- evo harness instructions
- benchmark routing
- keep/discard policy
- experiment scheduling / budget policy

不要把这两层混在一个文件里。

---

## 3.2 极小可编辑面 + 单次单变量

建议 v1.1.9 的 evo 实验规则：

- 一次实验只允许改一个小面
- 例如只改：
  - 一组 doctor 规则
  - 一段 completion contract
  - 一段 execution-mode routing

这样才能让改进归因清晰。

---

## 3.3 固定预算实验

建议在 Beacon evo 中冻结：

- max runtime
- max iterations
- max command count
- max evidence budget

让不同实验之间保持可比。

---

## 3.4 单一主 KPI

建议 v1.1.9 定义一个核心主指标，例如：

- `false_complete_rate`

配套次级指标：

- `evidence_coverage`
- `recovery_success_rate`
- `operator_load`
- `cost_per_trial`

这比“好多了 / 稍微稳一些”更适合 keep/discard。

---

## 3.5 正式 Evo Ledger

README 强调 morning log / experiment trail。  
Beacon 应把 evo 实验账本正式化：

建议：

```text
.beacon/state/evo/
├── experiments/
├── ledgers/
├── scorecards/
└── keep-discard-log.jsonl
```

每次实验记录：

- change surface
- benchmark set
- budget
- score delta
- keep/discard
- reason

---

## 3.6 “真实输入样本”驱动，而不是纯 prompt 幻觉

建议 v1.1.9 把 evo benchmark 明确挂到真实样本上：

- 历史 gate blocked case
- 历史 false-complete case
- 历史 drift mismatch case
- 历史 doctor misdiagnosis case

也就是让 Beacon evo 像 autoresearch 一样：

> 在一个真实但被压缩过的小世界里反复进化。

---

## 3.7 人类调组织，不直接调主体

对应到 Beacon：

- 人类优先改 benchmark / program / policy
- 不直接让 agent 放开改所有生产代码

这能保持：

- 可控性
- 审计性
- 版本边界清晰

---

## 4. v1.1.9 可新增的正式设计线（Evo 向）

如果把这次调研纳入 v1.1.9，建议新增一条正式 evo 线：

### 线 G：Self-Evolution / Evo Harness

目标：

1. 定义 Beacon evo 的 subject surface 与 program surface
2. 定义固定预算实验协议
3. 定义单一主 KPI + scorecard
4. 定义 keep/discard ledger
5. 定义真实 benchmark corpus

候选输出：

- `execution/evo-harness-contract.md`
- `execution/evo-scorecard-contract.md`
- `execution/evo-program-surface.md`
- `.beacon/state/evo/`

---

## 5. 不应照搬的部分

## 5.1 不把 Beacon 做成“自改整仓”

autoresearch 能让 agent 改 `train.py`，是因为：

- 问题面非常小
- 指标非常清晰
- 预算非常固定

Beacon 仓库远比它复杂，因此不能直接套“自动改代码”心智。

## 5.2 不把 evo 做成无限 agent swarm

README 的重点不是 swarm 数量，而是：

- 问题面足够小
- 每轮能比较
- 实验可丢弃

Beacon v1.1.9 也应坚持小闭环，而不是先追求复杂并行。

## 5.3 不把 README 的训练思路误译成“全自动自治”

autoresearch 的真正约束很多：

- 单文件
- 固定预算
- 单一 metric
- 人类控制组织代码

Beacon 借的是这些约束，不是“无限自治”幻觉。

---

## 6. 结论

对 Beacon v1.1.9 来说，`karpathy/autoresearch` README 最值得借鉴的一句话可以转译成：

> Beacon 不应该先学会“自己改一切”，而应该先学会“在极小、真实、固定预算、可比较的试验面上演进自己”。

更直接地说：

> 如果 PUA 给 Beacon 带来的是“穷尽执行层”，那么 autoresearch 给 Beacon 带来的是“受控自进化试验台”。

两者组合后，Beacon v1.1.9 的自然方向就是：

```text
evidence-first kernel
+ exhaustiveness-controlled execution
+ constrained evo harness
```

---

**落盘位置**：`docs/beacon/archive/v1.1.9/research/`
