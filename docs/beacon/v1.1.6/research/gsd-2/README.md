# Research: GSD 2 — coding-agent runtime、状态机与声明式 workflow 引擎

> 来源：`oss-sync/automation/autoresearch/gsd-2/`
> 复核时间：2026-03-24
> 证据等级：A
> 研究目标：为 Beacon v1.1.6 提供 **runtime hygiene、dispatch pipeline、隔离边界、声明式 workflow** 的源码级借鉴

---

## 1. 先给结论

GSD 2 是本轮研究中最接近 Beacon “执行控制面”的项目。

它真正解决的是：

1. **agent 如何被稳定调度**
2. **上下文如何按单元重置**
3. **状态如何落盘、恢复、隔离**
4. **workflow 如何从代码/提示升级为可执行定义**

因此，GSD 2 对 Beacon 的价值主要不在“又一个 agent CLI”，而在：

- runtime 约束
- dispatch pipeline
- worktree isolation
- hallucination guard
- definition/graph 驱动的 workflow 引擎

---

## 2. 从源码复核到的关键事实

### 2.1 GSD 2 不是 prompt framework，而是 Pi SDK 上的 agent application

`docs/architecture.md` 直接写明：

- GSD 构建在 Pi SDK 之上
- 它在 SDK 之上扩展 workflow engine、auto mode state machine、project management primitives

这意味着它的设计重点是：

- 运行期控制
- 状态推进
- 会话管理
- 工程化调度

而不是只靠 slash command / prompt 注入来“希望模型按规则做事”。

### 2.2 fresh session per unit 是一等原则

`docs/architecture.md` 与 `docs/auto-mode.md` 都明确强调：

- 每个 task / phase / unit 都使用 fresh agent session
- dispatch prompt 会把所需上下文预内联
- 这样可以避免长会话上下文累积导致质量下降

这对 Beacon 很关键，因为它提供了一个清晰的 runtime 原则：

> **不要让执行单元共享无限增长的上下文。**

### 2.3 state-on-disk 是核心架构，不是附属功能

`docs/architecture.md` 明确写到：`.gsd/` 是 sole source of truth。

这带来的能力包括：

- crash recovery
- multi-terminal steering
- session resumption
- runtime introspection

对 Beacon 来说，这类设计比“再加一个 prompt”更接近基础设施能力。

### 2.4 worktree isolation 是默认执行边界的重要组成部分

`docs/auto-mode.md` 与 `src/worktree-cli.ts` 表明 GSD 2 提供三种隔离模式：

- `worktree`（默认）
- `branch`
- `none`

其中默认推荐 milestone 在独立 worktree 内运行，生命周期由 CLI 管理。

这说明 GSD 2 不只是“支持 git”，而是把 git isolation 作为执行系统的一部分来设计。

### 2.5 stuck detection、doctor、forensics 都属于 runtime hygiene

`docs/auto-mode.md` 提到了：

- sliding-window stuck detection
- doctor integration
- forensics
- timeout supervision

这些能力共同构成的不是 QA，而是：

> **runtime hygiene / execution safety net**

它和 gstack 的 QA 金字塔不同，不应混为同一种“验证机制”。

### 2.6 custom workflow engine 已经是定义即数据的真实实现

`src/resources/extensions/gsd/custom-workflow-engine.ts` 与 `run-manager.ts` 明确显示：

- workflow 定义冻结为 `DEFINITION.yaml`
- 运行图写成 `GRAPH.yaml`
- 每次循环都从 graph state 派生下一步 dispatch
- run 目录在 `.gsd/workflow-runs/<name>/<timestamp>/`

这不是“文档里说支持 YAML”，而是已经形成：

- 定义层
- 运行态图
- reconcile 层
- context injection 层

### 2.7 hallucination guard 是硬代码规则

`src/resources/extensions/gsd/auto/phases.ts` 明确处理：

- execute-task 完成但 0 tool calls
- 视为 hallucinated summary
- 标记失败并重试

这是 GSD 2 对 Beacon 最有参考价值的 guard 之一，因为它把“无实际产出”从模糊感觉变成了**明确执行规则**。

### 2.8 GSD 2 的 YAML workflow 不是配置文件堆砌，而是受 schema 和 engine 约束

`create-workflow` 相关技能与 `definition-loader.ts`、`custom-workflow-engine.ts` 表明：

- workflow 定义是 `.gsd/workflow-defs/<name>.yaml`
- 会经过解析与 schema 校验
- engine 会根据 GRAPH/DEFINITION 的状态推进流程

所以 GSD 2 的“声明式 workflow”是一个真实的执行面，而不只是写 YAML 作为说明文档。

---

## 3. 本次修正了哪些旧口径

### 旧口径 1：GSD 2 = Pi SDK + YAML workflow

**修正后：太浅。**

更准确的说法是：

- GSD 2 是一个 state-on-disk 的 coding-agent runtime
- Pi SDK 只是其 runtime 基础
- YAML workflow 只是其执行系统扩展出的一个能力面

### 旧口径 2：health checks = 三层验证

**修正后：不成立。**

GSD 2 的强项是：

- doctor
- stuck detection
- timeout supervision
- hallucination guard
- worktree lifecycle checks

这是 runtime diagnostics，不是 gstack 意义上的 QA 金字塔。

### 旧口径 3：GSD 2 最值得借鉴的是 web UI / 完整自动化产品形态

**修正后：不应优先聚焦。**

Beacon 短期真正该借的是：

- fresh session per unit
- state-on-disk
- hallucination guard
- worktree/branch/none 执行边界
- definition + graph 的 workflow 执行模式

---

## 4. 与 Beacon 的真实可比维度

| 维度 | GSD 2 的强项 | Beacon 可借鉴点 |
|------|--------------|-----------------|
| Runtime hygiene | 强 | fresh session、state-on-disk、stuck detection、timeouts |
| Git isolation | 强 | `worktree / branch / none` 三档边界 |
| Dispatch pipeline | 强 | unit 化执行、prompt 预内联、reconcile 循环 |
| Declarative workflow | 强 | `DEFINITION.yaml + GRAPH.yaml` |
| QA 金字塔 | 弱到中 | 不是主战场 |
| Artifact planning | 中 | 有，但不是其最独特的部分 |

---

## 5. 对 Beacon 的具体借鉴建议

### 适合吸收

1. **fresh session per execution unit**
2. **state-on-disk 作为恢复与审计基础**
3. **0-tool-call / 0-output guard**
4. **可配置隔离边界：worktree / branch / none**
5. **定义与运行态分离的 workflow engine**

### 不适合现在就吸收

1. **完整 web UI、forensics、parallel milestone orchestration**
2. **直接复制 Pi SDK 依赖与 GSD 的全部扩展生态**
3. **在 v1.1.6 一次性把所有 workflow 全部 YAML 化**

---

## 6. 关键证据文件

- `oss-sync/automation/autoresearch/gsd-2/docs/architecture.md`
- `oss-sync/automation/autoresearch/gsd-2/docs/auto-mode.md`
- `oss-sync/automation/autoresearch/gsd-2/docs/commands.md`
- `oss-sync/automation/autoresearch/gsd-2/src/resources/extensions/gsd/custom-workflow-engine.ts`
- `oss-sync/automation/autoresearch/gsd-2/src/resources/extensions/gsd/run-manager.ts`
- `oss-sync/automation/autoresearch/gsd-2/src/resources/extensions/gsd/auto/phases.ts`
- `oss-sync/automation/autoresearch/gsd-2/src/worktree-cli.ts`

---

## 7. 一句话总结

GSD 2 对 Beacon 的真正启发是：

> **把 agent 执行变成一个有状态、可恢复、可隔离、可声明式驱动的 runtime 系统，而不是只靠 prompt 约束。**
