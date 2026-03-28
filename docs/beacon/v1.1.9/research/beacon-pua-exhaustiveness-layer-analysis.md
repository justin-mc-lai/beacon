# 调研：Beacon v1.1.9 借鉴 PUA 的穷尽执行层

**日期**：2026-03-26  
**范围**：`tanweai/pua` 本地源码实现（skill / hooks / loop / evals / state）  
**目标**：提炼 Beacon v1.1.9 可吸收的“穷尽一切但证据优先”的执行机制，而不是照搬 PUA 话术层。

---

## 1. 调研对象与第一性原理结论

本次分析基于本地源码：

- `~/.codex/pua/codex/pua/SKILL.md`
- `~/.codex/pua/skills/pua/SKILL.md`
- `~/.codex/pua/skills/pua/references/*`
- `~/.codex/pua/hooks/hooks.json`
- `~/.codex/pua/hooks/failure-detector.sh`
- `~/.codex/pua/hooks/frustration-trigger.sh`
- `~/.codex/pua/hooks/session-restore.sh`
- `~/.codex/pua/hooks/pua-loop-hook.sh`
- `~/.codex/pua/scripts/setup-pua-loop.sh`
- `~/.codex/pua/evals/*`

第一性原理结论：

> PUA 的核心价值不是“骂得凶”，而是它把 **不许草率放弃、不许空口完成、不许重复试错** 变成了一套可触发、可升级、可恢复、可验证的执行控制层。

对 Beacon 最值得借鉴的不是语气，而是下面这条链：

```text
failure signal
→ escalation state
→ methodology switch
→ evidence hard-stop
→ recoverable loop / checkpoint
→ structured failure boundary
```

---

## 2. PUA 源码实现的真实结构

PUA 不是单一 prompt，而是五层结构：

1. **核心行为协议**
   - `skills/pua/SKILL.md`
   - 定义红线、主动性、检查清单、失败升级、完成条件
2. **命令与角色路由**
   - `commands/*.md`
   - `skills/p7|p9|p10|pro|pua-loop`
3. **Hook 自动注入**
   - `hooks/hooks.json`
   - 在用户不耐烦、Bash 连续失败、SessionStart、Stop、PreCompact 时自动触发
4. **本地状态持久化**
   - `~/.pua/.failure_count`
   - `~/.pua/builder-journal.md`
   - `~/.pua/evolution.md`
   - `.claude/pua-loop.local.md`
5. **行为验证**
   - `evals/test-behavior.sh`
   - `evals/run-trigger-test.sh`

换句话说，PUA 是一个 **behavioral runtime overlay**，不是一个普通 skill 文档。

---

## 3. Beacon v1.1.9 最值得吸收的 8 个机制

## 3.1 连续失败升级状态机

PUA 用 `failure-detector.sh` 把 Bash 连续失败转换成：

- L1：换本质不同方案
- L2：强制搜索 / 读源码 / 列假设
- L3：强制走完整检查清单
- L4：进入最后边界 / 体面失败

### Beacon 借鉴建议

在 v1.1.9 增加：

- `.beacon/state/exhaustion.json`

建议字段：

```json
{
  "failure_streak": 0,
  "escalation_level": "none",
  "last_failed_step": "",
  "attempted_strategies": [],
  "required_next_action": ""
}
```

建议升级语义：

- `E1`：要求切换本质不同策略
- `E2`：要求补官方文档 / 源码 / 假设验证
- `E3`：要求输出 exhaustiveness checklist
- `E4`：只能进入“结构化失败边界”或“恢复型循环”

---

## 3.2 Evidence-before-done 硬门禁

PUA 最重要的红线是：

> 没有 build/test/curl 等验证输出，不允许说 done。

### Beacon 借鉴建议

把 v1.1.9 的“完成”拆成两层：

1. `implementation_done`
2. `evidence_done`

只有以下条件同时满足，才能进入 completion / gate-ready：

- 已执行验证命令
- 已读取命令输出
- 关键 claim 有 evidence
- 已声明剩余风险

这比“有测试”更严格，要求 **claim 与 evidence 绑定**。

---

## 3.3 Exhaustiveness Checklist

PUA 的 7 项检查清单本质是在阻止以下问题：

- 重复试错
- 不搜就猜
- 没看上下文就改
- 没做最小复现就扩大修改面

### Beacon 借鉴建议

v1.1.9 新增标准清单：

1. 是否逐字读失败信号
2. 是否查官方文档 / 一手来源
3. 是否读出错上下文
4. 是否验证前置假设
5. 是否尝试反向假设
6. 是否做最小复现 / 最小隔离
7. 是否切换过工具 / 方法 / 路径

建议落盘：

- `docs/beacon/v1.1.9/execution/exhaustiveness-policy.md`
- `docs/beacon/v1.1.9/execution/exhaustiveness-report.md`

---

## 3.4 任务类型 → 方法论路由

PUA 的真正进步不只是“施压”，而是：

- Debug → RCA / 蓝军
- Build → 质疑 / 删除 / 简化
- Research → 搜索优先
- Review → 减法优先

### Beacon 借鉴建议

v1.1.9 不需要 flavor，但需要 **execution mode router**：

- `debug_mode`
- `research_mode`
- `refactor_mode`
- `delivery_mode`
- `architecture_mode`

每种 mode 决定：

- 默认检查顺序
- 证据要求
- 失败后的下一跳策略

也就是：

> Beacon 借“方法论切换”，不借“人格扮演”。

---

## 3.5 Compaction Checkpoint / Session Restore

PUA 很清楚一点：

> context compaction 不是失败历史归零。

它通过 journal 把这些状态跨压缩保留：

- 当前压力等级
- 已失败次数
- 已排除方案
- 下一假设
- 关键上下文

### Beacon 借鉴建议

v1.1.9 在 PreCompact / resume 时保存并恢复：

- tried approaches
- excluded causes
- next hypothesis
- current blocker
- evidence gap

避免：

- 压缩后重复试同一路线
- 重新猜已经排除的原因

---

## 3.6 可恢复的自主循环控制

PUA loop 的设计非常有价值：

- `<promise>`：真完成才结束
- `<loop-pause>`：需要人工时暂停
- `<loop-abort>`：明确边界后终止

### Beacon 借鉴建议

v1.1.9 可引入恢复型 loop 协议（命名可后定）：

- done signal
- pause signal
- abort signal

重点不是 XML，而是语义：

- **不能“卡住就退出”**
- **必须区分可恢复暂停与真正终止**
- **必须带完成信号而不是主观感觉**

---

## 3.7 角色级失败协议

PUA 的 P7/P8/P9/P10 不是装饰，而是：

- 不同角色有不同交付物
- 不同角色有不同失败模式
- 不同角色有不同升级动作

### Beacon 借鉴建议

v1.1.9 可把已有角色进一步结构化：

- Planner：边界不清 / 拆解失真
- Executor：证据不足 / 重复试错
- Reviewer：误报 / 漏报 / 只挑格式
- Orchestrator：路由错误 / 并行冲突 / 粒度失控

也就是：

> 不是只定义“谁负责什么”，还要定义“这个角色最常怎么失败”。

---

## 3.8 自进化基线（Baseline Only Up）

PUA 的 `evolution.md` 做的是：

- 某个高质量动作出现 3+ 次
- 就不再算“额外努力”
- 升级为“默认义务”

### Beacon 借鉴建议

v1.1.9 可引入 execution baseline：

例如以下行为一旦稳定出现，就进入默认义务：

- 改代码后跑验证
- claim 前贴 evidence
- 修 1 处后扫同类
- completion 时写风险

这样 Beacon 会从“一次次提醒”进化成“默认交付习惯”。

---

## 4. 不建议照搬的部分

## 4.1 不借 PUA 话术层

Beacon 应保持：

- evidence-first
- neutral but firm
- engineering style

不应引入：

- 羞辱式表达
- 情绪化表演
- 对用户体验有噪音的高压台词

## 4.2 不把远端平台能力当核心

PUA 有：

- 反馈上传
- 排行榜
- 注册
- 支付

这些不是 Beacon v1.1.9 的重点。

应优先借的是：

- escalation state
- checklist
- evidence hard-stop
- checkpoint / resume
- loop control

## 4.3 不只靠关键词触发

PUA 的 frustration regex 对插件很有用，但 Beacon 更适合优先使用：

- tool failure streak
- repeated unchanged strategy
- claim/evidence mismatch
- gate blocked with no remediation
- explicit user dissatisfaction

也就是让触发更多基于 **执行事实**，而不是纯文本情绪词。

---

## 5. 对 Beacon v1.1.9 的建议落地面

如果把本次调研正式纳入 v1.1.9 范围，推荐冻结以下能力：

### 线 A：Exhaustiveness Escalation
- failure streak 状态
- escalation policy
- required next action

### 线 B：Evidence Hard-Stop
- implementation_done / evidence_done 分离
- 无证据 claim 阻断

### 线 C：Execution Mode Router
- task type → execution mode
- failure pattern → next mode

### 线 D：Checkpoint / Resume
- compaction checkpoint
- session restore
- excluded causes persistence

### 线 E：Recoverable Loop
- done / pause / abort 语义
- loop state file
- 可恢复中断

### 线 F：Execution Baseline
- 重复高质量动作 → 默认义务
- baseline only up

---

## 6. 结论

Beacon v1.1.9 如果要吸收 PUA 的价值，最短路径不是“学会 PUA”，而是：

> 把 Beacon 从 evidence-first workflow kernel，推进成 **evidence-first + exhaustiveness-controlled execution kernel**。

一句话说：

> v1.1.9 应该把“要么真完成，要么有边界地失败”变成 Beacon 的正式执行层能力。

---

**落盘位置**：`docs/beacon/v1.1.9/research/`
