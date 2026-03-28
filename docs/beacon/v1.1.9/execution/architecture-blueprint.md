# Beacon v1.1.9 Architecture Blueprint

## 定位

Beacon v1.1.8 已经具备项目接管与交付闭环主干：

```text
init / prototype / implement / qa / debug / review / gate / release
```

Beacon v1.1.9 的职责不是取代这条主干，而是作为一个 **跨层控制面 + 学习面** 覆盖其上。

---

## 三层结构

### 1. Delivery Plane（交付面）

这是 v1.1.8 已经存在的能力面：

- `beacon/commands/workflow.py`
- `beacon/commands/implement.py`
- `beacon/commands/qa.py`
- `beacon/commands/review.py`
- `beacon/commands/gate.py`
- `beacon/commands/release.py`
- `beacon/commands/debug.py`

其职责是把需求转成：

```text
requirements
→ implementation
→ verification
→ gate
→ release evidence
```

### 2. Control Plane（控制面）

这是 v1.1.9 应新增/强化的部分：

- evidence hard-stop
- exhaustiveness escalation
- execution mode router
- checkpoint / resume contract
- recoverable loop contract

它不负责生成需求文档，而负责在执行过程中回答：

- 现在到底能不能宣称 done？
- 失败是继续当前策略，还是必须切换方法？
- 压缩/中断恢复后，哪些路线已经排除？
- 当前任务应该走 debug / research / delivery / refactor 哪种方法论？

### 3. Learning Plane（学习面）

这是 v1.1.9 的另一条新增重点：

- debug events → issue/idea harvest
- technical archive → requirement rewrite input
- version research → keep/discard policy
- evo harness → 小范围受控试验台

它负责把运行摩擦与实现事实重新变成下一轮版本输入，而不是让这些信息散落在 stdout / 对话上下文里。

## 当前现实判断（架构视角）

### 已经比较稳的部分
- Delivery plane 已经有较强的正式闭环
- `workflow / freeze / reopen / implement / review / gate / release` 已构成 release-line 主干
- coverage、spec fingerprint、baseline snapshot、delivery manifest 已进入正式检查面

### 仍需后续版本继续收口的部分
- anti-drift 仍未覆盖所有 operator surfaces
- baseline / fingerprint / snapshot 语义仍存在多中心
- calibrated confidence 仍未进入正式 contract
- QA precision learning 仍未进入 autoresearch 主闭环

所以从架构上说，v1.1.9 的职责不是“再加一个子系统”，而是把：

```text
main lifecycle
+ operator surfaces
+ qa orchestration
+ recovery semantics
```

编成一个更统一的 anti-drift control plane。

---

## 关键状态面

### Human Primary

- `docs/beacon/<version>/SUMMARY.md`
- `docs/beacon/<version>/execution/*.md`
- `docs/beacon/<version>/version/*.md`
- `docs/beacon/<version>/research/*.md`

### Runtime Internal

- `.beacon/qa/`
- `.beacon/debug/`
- `.beacon/implement/`
- `.beacon/state/`
- `.beacon/memory/`

### Machine-backed Truth

目前 v1.1.8 已有：
- workflow lifecycle memory
- technical implementation archive
- QA session manifest
- gate report / evidence manifest

v1.1.9 建议新增：
- `.beacon/state/exhaustion.json`
- `.beacon/state/checkpoints/<run_id>/`
- `.beacon/state/execution-baseline.json`
- `.beacon/state/evo/ledger.jsonl`

---

## 闭环主路径

### 主交付闭环

```text
think / user-story / prd / test-case
→ implement run
→ technical archive
→ qa / verify
→ review quality
→ gate / release
```

### 主恢复闭环

```text
failure / friction / ambiguity
→ debug feedback event
→ escalation level
→ strategy switch / evidence补齐
→ resume / continue
→ 新一轮验证
```

### 主学习闭环

```text
technical archive + debug harvest + gate reason codes
→ version research
→ keep/discard decision
→ next version requirement rewrite
```

---

## 为什么这比“继续加命令”更重要

如果没有 v1.1.9 这层控制与学习面，Beacon 虽然有很多能力，但仍然容易出现：

1. **假完成**
   - 有 implementation summary，但 claim 与证据未严格绑定
2. **重复试错**
   - resume 后丢失已排除路径与下一假设
3. **QA 与需求脱节**
   - QA 执行了，但不能清晰指出是哪个 requirement delta 导致必须重跑
4. **技术实现事实没有反哺到产品材料**
   - technical archive 只是归档，不形成下一轮输入

v1.1.9 的价值就在于：

> 把这些“已有能力之间的缝”变成正式 contract。

---

## 边界

### In Scope
- 强化执行时的证据门禁
- 强化失败后的恢复与升级策略
- 强化 debug / qa / implement / gate 之间的回流
- 强化 version research 对真实 runtime fact 的吸收

### Out of Scope
- 直接把 Beacon 变成整仓自治 agent
- 引入人格化高压提示系统
- 在没有固定预算与 scorecard 前开启大规模自改代码
- 用新的命令面替代 v1.1.8 已稳定的主链命令面

---

## 一句话总结

> Beacon v1.1.9 的架构本质，是给 v1.1.8 的交付内核加上一层“失败不乱、完成不虚、恢复不失忆、经验能沉淀”的控制与学习框架；v1.1.10 再在其上补 QA confidence / closure outcome / training feedback loop。
