# Beacon ↔ OMX adapter notes（v1.1.4 Draft）

## 1. 目标

定义 Beacon 如何把 `implement` implementation stage 对接到 **OMX / oh-my-codex** 工作流，并保持：

- Beacon 作为需求交付闭环内核；
- OMX 作为外部实现 skill/runtime；
- 实现结果可写回 Beacon execution / review / gate 链路。

---

## 2. 为什么 OMX 是最优先适配对象

相较于一般 shell 命令，OMX 具备以下特征：

1. 有明确的 **skill/workflow** 入口；
2. 有较强的 **长任务 / team / runtime** 能力；
3. 能接受结构化任务提示并执行多步实现；
4. 有状态、恢复、验证与操作员控制；
5. 与 Beacon 的 implementation → review → verify → gate 闭环天然互补。

> 结论：OMX 很适合作为 Beacon 第一个正式 implementation runner 示例。

---

## 3. 概念映射

| Beacon 概念 | OMX 概念 | 说明 |
|---|---|---|
| `implement run` | `omx exec` / `omx team` / skill invocation | Beacon 触发实现动作，OMX 真正执行 |
| source of truth | task prompt 输入 | Beacon 把 `docs/beacon/<version>/` 物料组装给 OMX |
| runner | runtime + skill | OMX 既是运行时也是 skill 承载器 |
| implementation marker | 执行完成后 Beacon 写回 | 不依赖 OMX 内部状态直接替代 |
| execution summary | Beacon formal docs | OMX 输出结果，Beacon 负责 formal summary |
| `review spec` / `review quality` | 后置 Beacon 动作 | 不交给 OMX 直接替代 |

---

## 4. 推荐适配类型

## 4.1 初版推荐：`command-skill`

Beacon 对 OMX 的推荐适配类型是：

```text
command-skill
```

即：
- 通过 CLI 启动 OMX；
- 由 Beacon 拼接 skill/task prompt；
- OMX 执行实现；
- Beacon 读取结构化结果文件。

## 4.2 为什么不是 bridge alias

不建议把 OMX 适配做成：

```bash
beacon bridge omx ...
```

原因：
- `bridge` 是运行时通道；
- `implement` 是 implementation stage 的正式动作；
- Beacon 需要 request/result/review/writeback 语义，而 `bridge` 只提供执行通道不够。

---

## 5. 推荐调用模型

### 5.1 Beacon 侧命令

```bash
beacon implement run <feature> --runner omx --skill workflows-work
```

### 5.2 解析后的 OMX 调用（示意）

```bash
omx exec --full-auto --cd "{project_root}" --skip-git-repo-check "{task_prompt}"
```

说明：
- `omx exec` 是 OMX 当前稳定的非交互执行入口；
- `--cd` 让 Codex 以项目根目录作为工作根；
- `--skip-git-repo-check` 允许 milemon 这类未初始化 git 的工作目录也能执行；
- `--full-auto` 用于提高非交互 implement 场景的实战可用性。

### 5.3 任务提示（示意）

```text
$workflows-work
Read Beacon source of truth:
- docs/beacon/{version}/user-story/{feature_slug}.md
- docs/beacon/{version}/prd/{feature_slug}.md
- docs/beacon/{version}/qa/test-cases/{feature_slug}.md
- docs/beacon/{version}/prototype/{feature_slug}/ (if present)
Implement the scoped feature.
Run relevant verification.
Write structured result to .beacon/implement/{run_id}/result.json
```

---

## 6. Request / Result 合同

## 6.1 Beacon 生成 request

```text
.beacon/implement/{run_id}/request.json
```

至少包括：
- `run_id`
- `feature`
- `version`
- `source_of_truth_root`
- `artifacts`
- `runner.id = omx`
- `runner.skill`
- `task_prompt`
- `expected_result_file`

## 6.2 OMX 返回 result

```text
.beacon/implement/{run_id}/result.json
```

建议最小字段：

```json
{
  "schema_version": "1.0",
  "run_id": "run-xxx",
  "status": "completed",
  "summary": "...",
  "changed_files": [],
  "verification": [],
  "artifact_updates": {}
}
```

---

## 7. Beacon 侧正式写回

OMX 执行完成后，Beacon 必须写：

### runtime
- `.beacon/state/implementation-<feature>.json`
- `.beacon/implement/<run_id>/stdout.log`
- `.beacon/implement/<run_id>/stderr.log`
- `.beacon/implement/<run_id>/command.txt`

### formal docs
- `docs/beacon/<version>/execution/implementation-summary-<feature>.json`
- `docs/beacon/<version>/execution/implementation-summary-<feature>.md`

### 后置动作
- `review spec <feature>`
- `review quality <feature>`（策略可配置）

---

## 8. 与 OMX 边界

## Beacon 负责
- source-of-truth 读取
- request/result schema
- execution summary
- implementation marker
- review/writeback/gate 链接

## OMX 负责
- 真正执行 skill/workflow
- 代码实现
- 局部验证
- 输出结构化结果

## Beacon 不负责
- OMX 的 team mode / tmux / HUD / mailbox
- OMX runtime 内部状态建模
- skill 安装、升级、恢复机制

---

## 9. 失败路径与建议 reason codes

- `runner_not_configured`
- `runner_request_write_failed`
- `runner_execution_failed`
- `runner_result_missing`
- `runner_result_invalid`
- `implement_execution_failed`
- `implement_writeback_failed`
- `implement_review_trigger_failed`

---

## 10. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| Beacon 写死 OMX | 扩展性差 | 用 runner registry + config model |
| OMX 没有标准 result 输出 | Beacon 无法回填 | 强制 result schema |
| Beacon 过度依赖 OMX team/runtime | 边界漂移 | Beacon 只适配 implement 动作，不接管 runtime |
| task prompt 过长/过噪 | skill 执行质量下降 | 统一 request contract + task template 控制 |
| review/writeback 不进入主链 | 变成孤立实现 | implement 结束后强制进入 review spec |

---

## 11. 建议实施顺序

1. 先支持 OMX `command-skill` 适配
2. 打通 request/result/runtime evidence
3. 写 implementation summary + marker
4. 自动触发 `review spec`
5. 再考虑与 `omx team` 的更深层适配，但不进入 MVP

---

## 12. 成功标准

- Beacon 能把 feature 通过 OMX 实现 runner 执行
- Beacon 能消费 OMX 结果并生成 formal execution summary
- Beacon 能把 OMX 实现结果接回 review / verify / gate
- 整体过程中 Beacon 仍然保持闭环内核定位，而不是变成 OMX 的 runtime 管理器
