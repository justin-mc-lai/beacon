# Beacon v1.3.8 Post-Freeze Team-Ralph Sequencing and Host Prompt Trace Analysis

**Date**: 2026-04-24  
**Method**: 基于 Rolo 真实项目 `memory-friction-evolution-v1.3.3-partner-rule-adjustment-team-ralph-sequencing-20260424` 报告、当前 `implement` runtime 面与 `v1.3.7` delivery contract 做收敛分析  
**Purpose**: 判断 Beacon 是否应把冻结后的 `team -> ralph` 顺序正式产品化，并把宿主提示词到执行命令的映射纳入 formal evidence。

---

## 1. Summary

这条调研的核心结论是：

- 在真实多服务交付中，`team first, ralph second` 已经是稳定可复现的工作模式。
- Beacon 现在有这些能力碎片：
  - `implement team-plan`
  - `implement team-run`
  - `implement run --mode ralph`
  - `implement ralph-status`
- 但它仍没有把这条顺序做成一条显式的 public execution contract。
- 同时，真正驱动用户工作的并不是裸命令，而是宿主提示词。
- 如果 Beacon 只记录执行命令，不记录 `host prompt -> mapped command -> produced artifact`，就会丢掉最有价值的演进信号。

一句话：

> `v1.3.8` 应该把“冻结后多服务快速推进，再做主审收口”的真实序列正式产品化，并把宿主调用链变成结构化证据。

---

## 2. Problem Statement

这条 friction 不是“有没有 team/ralph 模式”，而是三件事没有闭环：

1. 执行顺序没有产品化  
2. 宿主提示词没有留证  
3. plan 质量不足以支撑 team 和 Ralph 两阶段闭环

这会导致：

- 用户每次都要重复表达“先 team 再 ralph”
- Ralph 的语义仍被误解成 team reviewer 的重复物
- memory/friction 只能看到低层 CLI，学不到用户真实工作路径

---

## 3. Current Baseline

### 3.1 已有能力

- 冻结前：
  - requirement clarity
  - technical review contract
- 冻结后：
  - implementation plan
  - team-plan
  - team-run
  - ralph run
  - ralph status
  - branch check

### 3.2 现状缺口

- 顺序关系不是 contract，只是人工习惯
- host prompt trace 没有正式 artifact
- plan 对多服务 feature 仍可能退化为占位任务
- branch preflight 更像“报错器”，不是“操作建议器”

---

## 4. Direct Evidence

来自 Rolo report 的直接信号：

1. 先冻结，再开发  
2. 多服务交付优先 `implement team`  
3. `ralph` 不是替代 `team`，而是 team 之后的第二阶段总审  
4. 发布前必须收口到规范分支  

对应直接证据：

- `.beacon/state/requirement-clarity-partner-rule-adjustment.json`
- `.beacon/state/technical-review-contract-partner-rule-adjustment.json`
- `docs/beacon/v1.3.3/.machine/execution/implementation-plan-partner-rule-adjustment.json`
- `docs/beacon/v1.3.3/.machine/execution/git-workflow-partner-rule-adjustment.json`
- `.beacon/raw-command-log.jsonl`

---

## 5. Host Prompt Trace Signal

这次最强的产品信号来自宿主提示词序列，而不是命令本身：

1. `beacon-prd-bootstrap`
2. `beacon-toolkit-lighthouse`
3. `beacon-brainstorm`
4. `beacon status`
5. `beacon-implement mode=team`
6. `beacon-implement mode=ralph`
7. `beacon implement check-branch`

说明：

- 对人类来说，这是一条自然工作流
- 对 Beacon 来说，这条链还没有进入 formal runtime evidence

所以 `v1.3.8` 的关键不是再加一个 mode，而是把真实宿主驱动面纳入 writeback。

---

## 6. Research Direction

### 6.1 方向 A: 保持现状，只在文档里建议 `team -> ralph`

优点：

- 实现简单

缺点：

- 仍然依赖人工解释
- status / HUD 无法读出顺序状态
- memory/friction 仍缺少 formal host trace

结论：

- 不够。

### 6.2 方向 B: 把 `team -> ralph` 做成显式顺序合同

优点：

- 更贴近真实交付心智
- status / HUD 可以直接展示 phase
- release 前的 closure 路径更清晰

缺点：

- 需要对 implement runtime、status、maybe HUD 做状态建模

结论：

- 推荐。

### 6.3 方向 C: 只做 prompt trace，不做顺序合同

优点：

- 能改善学习面

缺点：

- 用户执行心智仍然没有产品化
- 解决不了 phase 可视化和 branch closure 问题

结论：

- 不够。

---

## 7. Proposed v1.3.8 Scope

### 7.1 Explicit Post-Freeze Execution Sequence

推荐公开表达：

```text
freeze pass
-> implement team-plan
-> implement team-run
-> implement ralph
-> qa
-> release
```

推荐命令形态：

```bash
beacon implement run "<feature>" --mode team --post-review ralph --json
```

### 7.2 Host Prompt Trace Artifact

推荐记录：

- original host prompt
- inferred surface
- mapped command
- generated artifacts
- route success or blocked

### 7.3 Phase Projection

让 `status` / HUD 至少显示：

- freeze status
- team phase
- team done or blocked
- ralph pending or active
- ralph stop_state
- ralph next_action

### 7.4 Actionable Branch Preflight

推荐输出：

- affected service
- current branch
- expected branch
- dirty worktree state
- recommended safe relocation action

---

## 8. Boundaries

`v1.3.8` 不应：

- 新增新的公开主生命周期 stage
- 让 `team`、`ralph` 使用不同 requirement truth
- 用 prompt trace 替代 formal execution evidence

`v1.3.8` 应：

- 把真实顺序变成 contract
- 把宿主驱动面变成 evidence
- 保持 frozen truth 不变

---

## 9. Preliminary Conclusion

这条演进是值得做的，而且适合定义成 Beacon 的一条正式 feature：

- `team -> ralph` 是执行合同增强
- `host_prompt_trace` 是证据合同增强

两者合在一起，Beacon 才能既服务真实交付，又学习真实用法。

## 10. Recommended Next Step

基于这份调研，下一步适合起一条正式 feature：

- `beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace`

## Source Refs

- `/Users/apple/Developer/Company/rolo/.beacon/analysis/memory-friction-evolution-v1.3.3-partner-rule-adjustment-team-ralph-sequencing-20260424.md`
- `beacon/commands/implement.py`
- `skills/beacon/beacon-implement/SKILL.md`
- `docs/beacon/v1.3.7/execution/architecture-blueprint.md`
- `docs/beacon/v1.3.7/execution/boundaries.md`
