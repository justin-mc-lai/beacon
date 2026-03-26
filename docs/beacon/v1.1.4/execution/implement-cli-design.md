# Beacon implement CLI 设计稿（v1.1.4 Draft）

## 1. 目标

为 Beacon 提供正式的 implementation 命令面，使 implementation stage 不再只依赖：

- `--implementation-command`
- `BEACON_IMPLEMENTATION_COMMAND`

而是升级为：

```bash
beacon implement ...
```

该命令面必须支持：
- 可配置 runner / skill adapter
- 与 workflow implementation 阶段打通
- 将实现结果转为 Beacon 的 evidence / marker / summary / review 回路

---

## 2. 设计原则

1. **动作化**：implementation 必须是显式命令，而不是隐藏参数。
2. **Runner 化**：Beacon 不直接实现编码，只适配外部实现器。
3. **配置驱动**：Runner 通过 project/global config 解析。
4. **闭环优先**：实现之后必须进入 review / verify / gate，而不是只返回 shell exit code。
5. **边界清晰**：`implement` 不替代 `bridge`，不做 team runtime。

---

## 3. 顶层命令组

## 3.1 MVP 命令

```bash
beacon implement run <feature>
beacon implement status <feature|run_id>
beacon implement list-runners
```

## 3.2 后续增强命令

```bash
beacon implement show-runner <id>
beacon implement doctor
beacon implement retry <run_id>
beacon implement cancel <run_id>
```

---

## 4. 子命令定义

## 4.1 `implement run`

### 语义

触发 implementation stage 的正式执行动作：
- 解析目标 feature/version
- 读取 source-of-truth artifacts
- 解析 runner 配置
- 生成 request contract
- 调用外部 runner / skill
- 校验 result contract
- 写 implementation marker / execution summary
- 可选触发 `review spec` / `review quality`

### 建议 CLI

```bash
beacon implement run <feature> \
  --project . \
  --version v1.1.4 \
  --runner omx \
  --skill workflows-work \
  --dry-run \
  --json
```

### 参数建议

| 参数 | 必填 | 说明 |
|------|------|------|
| `feature` | 是 | 目标 feature 名称 |
| `--project` / `--project-root` | 否 | 项目根目录 |
| `--version` | 否 | 目标 docs 版本 |
| `--runner` | 否 | 指定 runner id |
| `--skill` | 否 | 覆盖 runner 绑定 skill |
| `--task-template` | 否 | 覆盖 task prompt 模板 |
| `--request-file` | 否 | request.json 输出路径覆盖 |
| `--result-file` | 否 | result.json 读取路径覆盖 |
| `--timeout-sec` | 否 | 执行超时覆盖 |
| `--auto-review-spec/--no-auto-review-spec` | 否 | 是否自动触发 review spec |
| `--auto-review-quality/--no-auto-review-quality` | 否 | 是否自动触发 review quality |
| `--dry-run` | 否 | 只生成 request，不执行 runner |
| `--json` | 否 | 输出 machine-readable payload |

### 返回状态

- `0`：执行完成，且 result 合法
- `2`：配置缺失/runner 失败/result 缺失或非法

---

## 4.2 `implement status`

### 语义

查看 implementation run 的当前状态与关联物料。

### 建议 CLI

```bash
beacon implement status beacon-implement-skill-runner --project . --version v1.1.4
```

或：

```bash
beacon implement status --run-id run-20260320T120000Z-impl
```

### 输出建议

- `feature`
- `run_id`
- `version`
- `runner`
- `skill`
- `request_path`
- `result_path`
- `implementation_marker`
- `execution_summary`
- `review_spec_status`
- `review_quality_status`
- `verify_status`
- `gate_ready`

---

## 4.3 `implement list-runners`

### 语义

列出当前 Beacon 可解析的 implementation runners。

### 输出建议

| id | type | source | default | notes |
|----|------|--------|---------|-------|
| `omx` | `command-skill` | project/global | yes/no | Uses OMX `exec` non-interactive entry + skill contract |
| `custom-x` | `command` | project/global | yes/no | User-defined runner |

### 使用场景

- 验证当前配置是否生效
- 查看有哪些 runner 可选
- 调试 project/global config 优先级问题

---

## 5. Runner 解析顺序

`implement run` 的 runner 解析顺序建议：

1. CLI `--runner`
2. CLI `--skill` / `--task-template` overrides
3. 项目配置 `beacon.config.yaml`
4. 全局配置 `~/.config/beacon/config.yaml`
5. 默认 runner
6. 若仍为空：`runner_not_configured`

---

## 6. 与 workflow 的集成

## 6.1 workflow implementation 阶段优先级

当前 workflow implementation 阶段应按以下顺序解析：

1. `--implementation-command`
2. `--implementation-runner`
3. 配置中的 `implementation.default_runner`
4. 若全无，Blocked

## 6.2 委托关系

当 workflow 解析到 runner 时：

```text
workflow implementation -> implement run -> review spec -> verify -> review quality -> gate
```

其中：
- workflow 负责主链推进
- implement 负责 implementation 承接
- review 负责需求与质量回写判断

---

## 7. 与 bridge 的边界

## `implement`
- implementation stage 的正式动作
- 有 request/result/evidence/writeback 语义
- 面向交付闭环

## `bridge`
- 实验性 runtime 通道
- 面向 OMC/OMX/team 等运行时桥接
- 不承载正式 implementation summary / writeback contract

> 结论：`implement` 不应是 `bridge run omx ...` 的别名。

---

## 8. 与 OMX 的接入建议

OMX 建议作为首个 runner example：

```bash
beacon implement run <feature> --runner omx --skill workflows-work
```

Beacon 给 OMX 的责任边界：
- Beacon 生成 request
- Beacon 拼 task prompt
- OMX 执行 skill
- OMX 产出结构化 result
- Beacon 负责落 implementation marker / summary / review

Beacon 不负责：
- OMX team mode / tmux / mailbox / HUD
- OMX runtime 生命周期管理
- OMX 自身 skill 安装与维护

---

## 9. 错误语义

建议 MVP 原生 reason codes：

- `runner_not_configured`
- `runner_config_invalid`
- `runner_request_write_failed`
- `runner_execution_failed`
- `runner_result_missing`
- `runner_result_invalid`
- `implement_execution_failed`
- `implement_writeback_failed`
- `implement_review_trigger_failed`

---

## 10. 成功标准

- `implement` 成为 Beacon 一等命令面；
- 可以列出 runner、执行 runner、查看状态；
- workflow implementation 可委托给 implement；
- 输出 implementation marker、execution summary、review 状态；
- CLI 面不引入 scheduler / team runtime 语义污染。
