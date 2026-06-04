# Beacon ↔ gstack adapter notes（v1.1.4 Draft）

## 1. 目标

定义 Beacon 如何与 **gstack** 兼容，用于 implementation / review / QA / ship 等工作流协作，同时保持：

- Beacon 负责需求与交付闭环；
- gstack 负责 Claude Code 环境中的 skill / slash-command 工作流；
- 两者通过明确的 handoff / result contract 连接。

---

## 2. 为什么 gstack 不能按 OMX 的方式直接接入

gstack 与 OMX 的关键差异：

1. gstack 更像 **Claude Code 内的 skill / slash-command 工作流集合**；
2. 它天然更强调 `/office-hours`、`/review`、`/qa`、`/ship` 这类工作流动作；
3. 它不一定提供稳定的 shell-native 通用 runner contract；
4. 因此，Beacon 不能假设 gstack 等于“一个可直接 shell 调用的 command runner”。

> 结论：gstack 更适合作为 **`claude-skill` adapter** 或 **`handoff` adapter**，而不是普通 `command-skill` adapter。

---

## 3. 推荐适配类型

## 3.1 首选：`claude-skill`

适用于：
- Beacon 生成 skill request package；
- Claude Code / gstack 环境消费该 request；
- 外部运行后写回结构化 result。

## 3.2 备选：`handoff`

适用于：
- Beacon 本身不执行 gstack；
- Beacon 只生成 handoff package 和推荐动作；
- 用户在 Claude Code 中执行对应 gstack skill；
- Beacon 后续读取 result 完成闭环。

---

## 4. 建议的兼容路径

## 路径 A：handoff-first（推荐 MVP）

```text
Beacon
  -> write request.md / request.json
  -> recommend gstack skill/action
  -> user/agent in Claude Code executes gstack workflow
  -> write result.json back to Beacon
  -> Beacon performs review/writeback/gate continuation
```

优点：
- 最稳妥
- 不依赖 gstack 暴露稳定 CLI
- 不破坏 Beacon 与 gstack 边界

## 路径 B：future claude-skill adapter

若后续能确认稳定调用入口，可演化为：
- Beacon 直接触发 Claude Code / gstack skill
- 但仍要求结构化 result contract

---

## 5. gstack 适合承接的动作类型

gstack 不是只适合 coding，还适合：

- 需求挑战 / 方案挑战
- 设计/实现 review
- QA 验证
- ship/release 协助

因此 Beacon 与 gstack 的协作不应只限于 `implement`，还可以后续扩展到：

- `review spec`
- `review quality`
- `verify`
- `release`

但 MVP 阶段应先限定在 implementation / writeback handoff。

---

## 6. Handoff Contract 建议

Beacon 应生成：

```text
.beacon/implement/{run_id}/request.json
.beacon/implement/{run_id}/request.md
```

其中 `request.md` 应面向 Claude/gstack 交互式使用，示例：

```markdown
# Beacon Implementation Handoff

Feature: beacon-implement-skill-runner
Version: v1.1.4

Read Beacon source of truth:
- docs/beacon/archive/v1.1.4/user-story/beacon-implement-skill-runner.md
- docs/beacon/archive/v1.1.4/prd/beacon-implement-skill-runner.md
- docs/beacon/archive/v1.1.4/qa/test-cases/beacon-implement-skill-runner.md

Recommended gstack workflow:
- /review   (if validating design/implementation alignment)
- /qa       (if validating execution)
- /ship     (if preparing release)

Required output:
Write structured result to .beacon/implement/{run_id}/result.json
```

---

## 7. Result Contract

无论是否自动执行，Beacon 对 gstack 的要求必须是统一的：

```text
.beacon/implement/{run_id}/result.json
```

建议字段：

```json
{
  "schema_version": "1.0",
  "run_id": "run-xxx",
  "status": "completed",
  "summary": "Implemented with gstack-assisted Claude workflow",
  "changed_files": [],
  "verification": [],
  "artifact_updates": {},
  "source_runtime": "gstack"
}
```

---

## 8. Beacon 侧写回

gstack 完成后，Beacon 仍然负责：

- implementation marker
- implementation summary
- `review spec`
- `review quality`
- verify / gate continuation

也就是说，gstack 只是外部 skill workflow，**不替代 Beacon 的 formal writeback**。

---

## 9. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| 误把 gstack 当通用 CLI runner | 实现不稳定 | MVP 用 handoff/claude-skill 模式 |
| gstack slash command 变化 | Beacon 兼容性脆弱 | 不写死具体 slash command，保留 adapter notes + mapping |
| 无结构化结果输出 | Beacon 无法回填 | 强制 result.json contract |
| Beacon 与 gstack 职责重叠 | 产品边界混乱 | Beacon 负责闭环物料，gstack 负责 Claude workflow |

---

## 10. 建议实施顺序

1. 先支持 gstack `handoff` adapter
2. 只要求 request package + result contract
3. 让 Beacon 负责 review/writeback/gate
4. 等确认 gstack 稳定调用面后，再考虑 `claude-skill` 直接适配

---

## 11. 成功标准

- Beacon 能为 gstack 生成明确 handoff package
- gstack 结果能被 Beacon 读回并进入 formal writeback
- Beacon 不需要依赖 gstack 内部实现细节即可维持闭环
- gstack 兼容路径不破坏 Beacon 的 source-of-truth 模型
