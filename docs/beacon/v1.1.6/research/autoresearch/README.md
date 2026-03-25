# Research: autoresearch — 固定时间盒、自主实验循环与单目标优化

> 来源：`oss-sync/automation/autoresearch/karpathy-autoresearch/`
> 复核时间：2026-03-24
> 证据等级：A
> 研究目标：为 Beacon v1.1.6 提供 **timebox、自主循环边界、单文件修改、指令文件设计** 的源码级借鉴

---

## 1. 先给结论

autoresearch 不是通用产品工作流框架，而是一个非常纯粹的自主实验系统。

它的核心价值在于：

1. **把任务压缩为单目标优化问题**
2. **给每轮实验一个固定 wall-clock 预算**
3. **严格限制可修改边界**
4. **把 human instructions 与 agent-editable code 分开**

它对 Beacon 的启发不在“无限自治”，而在：

- 高成本任务应如何 timebox
- agent 应该被允许改什么、不允许改什么
- 单轮迭代的成功标准如何被压缩成一个清晰指标

---

## 2. 从源码复核到的关键事实

### 2.1 只有一个主要可编辑目标：`train.py`

`program.md` 明确写明：

- `prepare.py`：只读，不允许改
- `train.py`：唯一允许 agent 修改的核心文件
- `program.md`：human 编辑的 agent instructions

这意味着 autoresearch 的运行边界非常清晰：

- 人类修改指令系统
- agent 修改实验实现
- 评估 harness 保持稳定

### 2.2 固定 5 分钟 wall-clock 预算是硬约束

`program.md` 明确规定每轮实验：

- 训练预算固定为 5 分钟
- 以 wall clock 计时
- 超时到 10 分钟视为失败

`prepare.py` 里也有 `TIME_BUDGET = 300` 的实现。

这不是“建议值”，而是整个系统的实验公平性前提。

### 2.3 评估目标被压缩成单一指标：`val_bpb`

`program.md` 与 README 都强调：

- 核心目标是把 `val_bpb` 做低
- 结果记录到 `results.tsv`
- 更好就保留 commit，更差就 reset 回去

这类设计的关键不是训练本身，而是：

> **agent 每一轮都面对一个明确、可回滚、可比较的 objective function。**

### 2.4 `program.md` 扮演 lightweight skill / instruction file

README 与 `program.md` 都把它描述成一种超轻量的“skill”/instructions 文件：

- human 通过改 `program.md` 调整 agent 行为
- agent 不直接改 instructions
- 这样可以把行为治理与实现修改分开

### 2.5 这个系统是高度自治的，但自治建立在强约束上

`program.md` 中的 loop 逻辑明确要求：

- 建分支
- 改 `train.py`
- git commit
- 跑实验
- 解析指标
- 记录结果
- improved 就保留，不 improved 就回滚

也就是说，自主循环并不是“想怎么试就怎么试”，而是：

- 修改边界固定
- 预算固定
- 评估指标固定
- 保留/丢弃规则固定

### 2.6 `NEVER STOP` 是该项目的实验姿态，不适合直接迁移到通用产品任务

`program.md` 明确写了实验一旦开始，agent 不要停下来问人。

这对训练实验场景合理，但对 Beacon 这类通用 workflow 系统来说，不能直接照搬。

Beacon 更适合借的是：

- 固定时间盒
- stop/review gate
- 边界清晰的单轮任务

而不是“永远继续”。

---

## 3. 本次修正了哪些旧口径

### 旧口径 1：autoresearch = 自主研究框架，可直接类比 Beacon workflow

**修正后：不成立。**

autoresearch 更准确的定位是：

- 单目标实验优化系统
- 高约束、自主循环、可回滚实验框架

而不是面向复杂产品需求编排的通用 workflow 系统。

### 旧口径 2：它的主要借鉴点是 self-modification

**修正后：不应这样表述。**

更值得借鉴的是：

- timebox
- 单文件/单目标聚焦
- 评估指标清晰
- 保留/回滚规则清晰

### 旧口径 3：无限自治本身值得迁移

**修正后：风险过高。**

Beacon 应借它的约束结构，不应直接借它的无限循环策略。

---

## 4. 与 Beacon 的真实可比维度

| 维度 | autoresearch 的强项 | Beacon 可借鉴点 |
|------|---------------------|-----------------|
| Timebox | 强 | 高成本执行任务固定预算 |
| Single-target loop | 强 | 单轮任务目标压缩与明确验收 |
| Edit boundary | 强 | 显式声明哪些文件/区域可改 |
| Instruction file design | 强 | 类 `program.md` 的轻量行为约束文件 |
| Multi-artifact workflow | 弱 | 不是其强项 |
| Runtime generality | 弱 | 只适合实验场景 |

---

## 5. 对 Beacon 的具体借鉴建议

### 适合吸收

1. **为高成本执行加固定时间盒**
2. **明确 agent 的可修改边界**
3. **将复杂任务压缩成单轮可比较目标**
4. **引入轻量 instruction file 作为行为约束层**

### 不适合现在就吸收

1. **`NEVER STOP` 式无限自治**
2. **把所有任务都抽象成单指标优化问题**
3. **把训练实验的 keep/discard 逻辑生搬到产品 workflow**

---

## 6. 关键证据文件

- `oss-sync/automation/autoresearch/karpathy-autoresearch/program.md`
- `oss-sync/automation/autoresearch/karpathy-autoresearch/README.md`
- `oss-sync/automation/autoresearch/karpathy-autoresearch/prepare.py`
- `oss-sync/automation/autoresearch/karpathy-autoresearch/train.py`

---

## 7. 一句话总结

autoresearch 对 Beacon 的真正启发是：

> **把自主循环建立在明确的时间预算、修改边界和评估指标之上，而不是单纯放大自治程度。**
