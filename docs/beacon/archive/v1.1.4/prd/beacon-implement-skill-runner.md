# PRD: Beacon implement 子命令与自定义实现 Skill 适配（v1.1.4）

## 1. 目标

在 v1.1.4 为 Beacon 正式补齐 implementation stage 的产品动作，新增顶层 `implement` 子命令组，使 Beacon 能够：

1. 用统一命令承接 implementation，而不再只依赖 `--implementation-command` 占位；
2. 通过配置接入用户自定义实现 Skill / Runner（例如 OMX）；
3. 把需求物料（User Story / PRD / Test Case / Prototype / execution context）打包为可执行实现输入；
4. 在实现完成后写回结构化证据，并驱动 `review spec / review quality` 继续闭环；
5. 保持 Beacon 的产品边界：需求交付闭环内核，而不是调度器 / 编码 orchestrator。

## 2. 背景

v1.1.3 已经明确：

- Beacon 的 canonical workflow 为：
  `think -> user-story -> prd -> [prototype] -> test-case -> implementation -> verify -> gate`
- `implementation` 是 **外部执行对齐点**；
- `review spec` 与 `review quality` 是实现阶段的正式回写动作；
- Beacon 不应直接膨胀为通用 scheduler / team orchestrator。

当前实现虽然已有：

- workflow 中的 `implementation` 阶段；
- `--implementation-command` 与 `BEACON_IMPLEMENTATION_COMMAND`；
- 顶层 `review spec` / `review quality`；
- bridge/omx 模板字符串；

但仍存在关键缺口：

1. implementation 还不是正式命令面，而只是 workflow 内部参数；
2. 没有统一的 implementation Runner/Skill 配置模型；
3. 没有 request/result 契约，外部实现结果难以被 Beacon 结构化消费；
4. 没有正式的 implementation summary / runtime evidence / review writeback 链路；
5. 对 OMX 之类个人实现 Skill 的接入还停留在 ad-hoc 模板，不是产品能力。

## 3. 第一性原则

### 3.1 用户真正需要的不是“再加一种 bridge”

用户真正需要的是：

- 在 Beacon 主链里有一个正式的“开始实现”动作；
- 这个动作能调用自己偏好的实现 Skill / Runner；
- 实现结果能被 Beacon 记录、复核、回写，而不是散落在外部工具里；
- 若实现引发规格偏差，Beacon 能正式提示要回填哪些物料。

### 3.2 Beacon 不直接做什么

Beacon 不直接负责：

- 成为通用编码平台；
- 成为 agent scheduler / team orchestrator；
- 替代 OMX / OMC / Codex / Claude 等外部执行器；
- 在 `implement` 命令内内置复杂多代理 runtime。

### 3.3 Beacon 负责什么

Beacon 负责：

- 为外部实现器提供统一 contract；
- 生成 request / 接收 result；
- 写 implementation evidence；
- 创建 implementation marker；
- 触发 review spec / review quality；
- 把长期真相沉淀到 `docs/beacon/<version>/execution/`。

## 4. 产品定位

> `implement` 是 Beacon implementation stage 的正式适配器命令。  
> 它负责把 Beacon 需求物料转译为外部实现任务，把外部实现结果转译为 Beacon 可追溯证据与回写动作。

它不是：
- `bridge` 的简单重命名；
- 外部 skill 的包装噪音层；
- 另一个 team/orchestrator 产品。

## 5. 范围

### In Scope

1. 顶层 `implement` 子命令组；
2. Runner 配置模型；
3. request/result/runtime evidence 契约；
4. OMX 作为首个 Runner 示例；
5. workflow implementation 阶段接入 `implement run`；
6. `review spec / review quality` 的后置触发；
7. execution 层实现摘要物料。

### Out of Scope

1. 不在 v1.1.4 内实现复杂多代理编排；
2. 不把 `implement` 变成通用 CI/CD 平台；
3. 不把所有 external tools 都做成内置一等功能；
4. 不在本版强制实现自动 patch PRD/User Story 全文；
5. 不替代现有 `bridge` 的实验性运行时能力。

## 6. 用户与场景

### Persona A — 个人 AI 工程师（OMX 用户）

- 已有自己的 OMX/技能体系；
- 希望继续用 OMX 编码实现；
- 但希望 Beacon 能记住本次实现与哪一版需求物料对应，并驱动 review/writeback。

### Persona B — 团队内标准化使用者

- 不关心 OMX，关心是否有统一的 implementation contract；
- 希望项目级配置里指定默认实现器；
- 希望 workflow 到 implementation 不再依赖手工拼 shell 命令。

## 7. 核心设计

## 7.1 顶层命令

MVP：

```bash
beacon implement run <feature>
beacon implement status <feature|run_id>
beacon implement list-runners
```

后续可扩展：

```bash
beacon implement show-runner <id>
beacon implement doctor
```

## 7.2 Runner Model

`implement` 不得写死为 OMX。

命令必须支持：

```bash
beacon implement run <feature> --runner omx
```

Runner 为配置驱动对象，而非硬编码分支。

### 推荐 Runner 类型

1. `command`
   - 直接执行一个外部命令模板
2. `command-skill`
   - 执行一个外部命令，同时带 skill/task prompt 约定

## 7.3 配置优先级

1. CLI 参数
2. 项目配置：`beacon.config.yaml`
3. 全局配置：`~/.config/beacon/config.yaml`
4. 默认 Runner

## 7.4 配置结构

```yaml
implementation:
  default_runner: omx
  auto_review_spec: true
  auto_review_quality: false

  runners:
    omx:
      type: command-skill
      command: omx
      args:
        - run
        - --project-root
        - "{project_root}"
        - --task
        - "{task_prompt}"
      timeout_sec: 3600
      env_passthrough:
        - OPENAI_API_KEY
        - ANTHROPIC_API_KEY
      skill_prefix: "$workflows-work"
      result_file: ".beacon/implement/{run_id}/result.json"
```

## 7.5 Beacon 组装给 Runner 的任务输入

Beacon 必须能从以下物料组装实现任务：

- `docs/beacon/<version>/user-story/<feature>.md`
- `docs/beacon/<version>/prd/<feature>.md`
- `docs/beacon/<version>/qa/test-cases/<feature>.md`
- `docs/beacon/<version>/prototype/<feature>/`（若存在）
- `docs/beacon/<version>/execution/` 上下文

并写入：

```text
.beacon/implement/<run_id>/request.json
```

### Request Schema（建议）

```json
{
  "schema_version": "1.0",
  "run_id": "run-xxx",
  "feature": "beacon-implement-skill-runner",
  "version": "v1.1.4",
  "source_of_truth_root": "docs/beacon/v1.1.4",
  "artifacts": {
    "user_story": "...",
    "prd": "...",
    "test_case": "...",
    "prototype": "..."
  },
  "runner": {
    "id": "omx",
    "skill": "workflows-work"
  },
  "goals": [
    "implement code",
    "run verification",
    "write structured result"
  ]
}
```

## 7.6 Runner 返回结果契约

外部实现器完成后，应写入：

```text
.beacon/implement/<run_id>/result.json
```

### Result Schema（建议）

```json
{
  "schema_version": "1.0",
  "run_id": "run-xxx",
  "status": "completed",
  "summary": "Implemented runner registry and OMX adapter",
  "changed_files": [
    "beacon/commands/implement.py",
    "beacon/utils/implement_runner.py"
  ],
  "verification": [
    {
      "command": "python3 -m pytest -q tests/test_v114_implement_command.py",
      "status": "passed"
    }
  ],
  "artifact_updates": {
    "user_story": { "required": false },
    "prd": { "required": true, "reason": "Implementation contract changed" },
    "test_case": { "required": true, "reason": "Need runner coverage tests" },
    "prototype": { "required": false }
  }
}
```

## 7.7 Runtime Evidence

`implement run` 至少产出：

```text
.beacon/implement/<run_id>/
├── request.json
├── result.json
├── stdout.log
├── stderr.log
└── command.txt
```

## 7.8 Formal Writeback

Beacon 在实现完成后必须自动生成：

```text
docs/beacon/<version>/execution/
├── implementation-summary-<feature>.json
└── implementation-summary-<feature>.md
```

并创建：

```text
.beacon/state/implementation-<feature>.json
```

## 7.9 Review Integration

实现完成后，Beacon 至少支持自动触发：

1. `review spec <feature>`
2. `review quality <feature>`（可配置是否自动触发）

其中：
- `review spec` 负责判断哪些需求物料需要回填；
- `review quality` 负责判断 verify / gate-ready。

## 7.10 Workflow Integration

当前 workflow implementation 阶段优先级应改为：

1. `--implementation-command`
2. `--implementation-runner`
3. 配置中的 `implementation.default_runner`
4. 若均缺失，则 Blocked

当 implementation 使用 Runner 时，其行为应等价于：

```bash
beacon implement run <feature> --runner <resolved_runner>
```

## 8. 功能需求

### FR-001 顶层 `implement` 子命令组
必须新增：
- `implement run`
- `implement status`
- `implement list-runners`

### FR-002 Runner 配置驱动
系统必须允许通过配置注册多个 Runner，不得将 OMX 写死为唯一实现器。

### FR-003 OMX Runner 示例
系统必须至少提供 OMX Runner 示例配置，支持通过 `skill_prefix` / `task_prompt` 触发 OMX skill。

### FR-004 Request 契约
`implement run` 必须生成结构化 request 文件，包含 source-of-truth、feature、version、runner、artifact paths。

### FR-005 Result 契约
系统必须消费结构化 result 文件，并将结果映射到 Beacon 的 implementation marker、execution summary 与 review 链路。

### FR-006 实现摘要落盘
系统必须在 execution 目录中生成 implementation summary 文档。

### FR-007 Implementation Marker
成功实现必须写 `.beacon/state/implementation-<feature>.json`。

### FR-008 自动 review 触发
实现完成后必须至少能自动调用 `review spec`，并可选自动调用 `review quality`。

### FR-009 Artifact Update 语义
Runner 返回结果必须支持声明是否需要回填：
- user-story
- prd
- test-case
- prototype

### FR-010 Backward Compatibility
若未配置 Runner，系统保留当前 `--implementation-command` / `BEACON_IMPLEMENTATION_COMMAND` 路径；若都无，则继续 Blocked。

### FR-011 错误语义
下列失败必须具备明确 reason code：
- `runner_not_configured`
- `runner_request_write_failed`
- `runner_execution_failed`
- `runner_result_missing`
- `runner_result_invalid`
- `runner_writeback_failed`

### FR-012 长期事实源不变
长期事实源仍然是 `docs/beacon/<version>/`；`.beacon/implement/` 仅保存 raw runtime 与临时执行状态。

## 9. CLI 草案

```bash
# 使用默认 runner
beacon implement run <feature> --project . --version v1.1.4

# 指定 runner
beacon implement run <feature> --runner omx --project . --version v1.1.4

# 指定 OMX skill
beacon implement run <feature> --runner omx --skill workflows-work --project . --version v1.1.4

# 查看状态
beacon implement status <feature>
beacon implement status --run-id <run_id>

# 查看可用 runner
beacon implement list-runners
```

## 10. 与 bridge 的边界

### `implement`
- Beacon implementation stage 的正式动作；
- 有 request/result/writeback/review 契约；
- 面向交付闭环。

### `bridge`
- 实验性通道；
- 面向 runtime / 外部 orchestrator / 长任务执行；
- 不承担正式物料回填语义。

## 11. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 把 Beacon 做成调度器 | 边界失控 | Runner 只做适配，不做 team/scheduler |
| OMX 写死成唯一实现器 | 难扩展 | 使用 runner registry + config model |
| result 契约过弱 | 无法回填 | 强制 request/result schema |
| 自动回填过度激进 | 污染 PRD/User Story | 先做 review 驱动，后续再引入 `--apply-writeback` |
| workflow 与 implement 双入口打架 | 心智混乱 | workflow implementation 统一委托给 `implement run` |

## 12. 成功标准

- Beacon implementation stage 具有正式命令面；
- 用户可通过配置使用个人实现 Skill（如 OMX）；
- 实现结果能被 Beacon 写回 execution summary 与 implementation marker；
- `review spec / review quality` 成为实现后正式回写链路；
- Beacon 仍保持需求闭环内核定位，而不是膨胀为通用 orchestrator。
