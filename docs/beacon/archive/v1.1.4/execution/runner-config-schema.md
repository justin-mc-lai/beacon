# Beacon implementation runner 配置 schema（v1.1.4 Draft）

## 1. 目标

定义 Beacon `implement` 子命令所依赖的 runner 配置模型，确保：

- runner 可配置
- priority 清晰
- 支持 OMX 等 command-skill 适配
- Beacon 能标准化 request/result 路径

---

## 2. 配置位置

## 2.1 项目配置

```text
beacon.config.yaml
```

## 2.2 全局配置

```text
~/.config/beacon/config.yaml
```

---

## 3. 顶层结构

```yaml
implementation:
  default_runner: omx
  auto_review_spec: true
  auto_review_quality: false
  request_root: ".beacon/implement"
  summary_root: "docs/beacon/{version}/execution"

  runners:
    omx:
      type: command-skill
      command: omx
      args:
        - exec
        - --full-auto
        - --cd
        - "{project_root}"
        - --skip-git-repo-check
        - "{task_prompt}"
      timeout_sec: 3600
      env_passthrough:
        - OPENAI_API_KEY
        - ANTHROPIC_API_KEY
      skill_prefix: "$workflows-work"
      request_file: ".beacon/implement/{run_id}/request.json"
      result_file: ".beacon/implement/{run_id}/result.json"
      stdout_file: ".beacon/implement/{run_id}/stdout.log"
      stderr_file: ".beacon/implement/{run_id}/stderr.log"
      command_file: ".beacon/implement/{run_id}/command.txt"
```

---

## 4. 顶层字段定义

## 4.1 `implementation.default_runner`

- 类型：`string`
- 说明：默认 runner id
- 示例：`omx`

## 4.2 `implementation.auto_review_spec`

- 类型：`boolean`
- 默认：`true`
- 说明：实现完成后是否自动调用 `review spec`

## 4.3 `implementation.auto_review_quality`

- 类型：`boolean`
- 默认：`false`
- 说明：实现完成后是否自动调用 `review quality`

## 4.4 `implementation.request_root`

- 类型：`string`
- 默认：`.beacon/implement`
- 说明：request/result/runtime evidence 的根目录

## 4.5 `implementation.summary_root`

- 类型：`string`
- 默认：`docs/beacon/{version}/execution`
- 说明：implementation summary 的正式落盘目录

---

## 5. Runner 对象结构

## 5.1 最小 schema

```yaml
implementation:
  runners:
    <id>:
      type: command | command-skill
      command: <string>
      args: [<string>...]
```

## 5.2 完整 schema

```yaml
implementation:
  runners:
    <id>:
      type: command | command-skill
      description: <string>
      command: <string>
      args: [<string>...]
      timeout_sec: <int>
      env_passthrough: [<ENV_KEY>...]
      env_overrides:
        KEY: VALUE
      skill_prefix: <string>
      task_template: <string>
      request_file: <string>
      result_file: <string>
      stdout_file: <string>
      stderr_file: <string>
      command_file: <string>
      supports_dry_run: <bool>
      supports_review_writeback: <bool>
```

---

## 6. 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | 是 | `command` 或 `command-skill` |
| `description` | string | 否 | 人类可读说明 |
| `command` | string | 是 | 外部执行命令，如 `omx` |
| `args` | array[string] | 是 | 参数模板，支持变量替换 |
| `timeout_sec` | int | 否 | 执行超时 |
| `env_passthrough` | array[string] | 否 | 透传环境变量白名单 |
| `env_overrides` | map | 否 | 额外环境变量覆盖 |
| `skill_prefix` | string | 否 | skill 前缀，例如 `$workflows-work` |
| `task_template` | string | 否 | 组装给 runner 的任务 prompt 模板 |
| `request_file` | string | 否 | request 输出路径模板 |
| `result_file` | string | 否 | result 读取路径模板 |
| `stdout_file` | string | 否 | stdout 路径模板 |
| `stderr_file` | string | 否 | stderr 路径模板 |
| `command_file` | string | 否 | command 记录路径模板 |
| `supports_dry_run` | bool | 否 | runner 是否支持 dry-run |
| `supports_review_writeback` | bool | 否 | 是否支持更丰富 writeback 协议 |

---

## 7. 模板变量

以下变量建议可在 `args` / `task_template` / 文件路径模板中使用：

- `{project_root}`
- `{workspace_root}`
- `{feature}`
- `{feature_slug}`
- `{version}`
- `{run_id}`
- `{source_of_truth_root}`
- `{task_prompt}`
- `{request_file}`
- `{result_file}`

---

## 8. Runner 类型语义

## 8.1 `command`

适用于：
- 纯外部命令调用
- 不依赖特定 skill 语义

示例：

```yaml
implementation:
  runners:
    local-script:
      type: command
      command: bash
      args:
        - scripts/implement.sh
        - "{request_file}"
      result_file: ".beacon/implement/{run_id}/result.json"
```

## 8.2 `command-skill`

适用于：
- 需要 skill 前缀或 task prompt 约定的运行时
- 如 OMX / OMC 等

示例：

```yaml
implementation:
  runners:
    omx:
      type: command-skill
      command: omx
      args:
        - exec
        - --full-auto
        - --cd
        - "{project_root}"
        - --skip-git-repo-check
        - "{task_prompt}"
      skill_prefix: "$workflows-work"
      result_file: ".beacon/implement/{run_id}/result.json"
```

---

## 9. OMX 推荐配置

```yaml
implementation:
  default_runner: omx
  auto_review_spec: true
  auto_review_quality: false

  runners:
    omx:
      type: command-skill
      description: "Use oh-my-codex workflow skill to perform implementation"
      command: omx
      args:
        - exec
        - --full-auto
        - --cd
        - "{project_root}"
        - --skip-git-repo-check
        - "{task_prompt}"
      timeout_sec: 3600
      env_passthrough:
        - OPENAI_API_KEY
        - ANTHROPIC_API_KEY
      skill_prefix: "$workflows-work"
      task_template: |
        {skill_prefix}
        Read Beacon source of truth:
        - {source_of_truth_root}/user-story/{feature_slug}.md
        - {source_of_truth_root}/prd/{feature_slug}.md
        - {source_of_truth_root}/qa/test-cases/{feature_slug}.md
        Implement the scoped feature, run verification, and write result to {result_file}
      request_file: ".beacon/implement/{run_id}/request.json"
      result_file: ".beacon/implement/{run_id}/result.json"
      stdout_file: ".beacon/implement/{run_id}/stdout.log"
      stderr_file: ".beacon/implement/{run_id}/stderr.log"
      command_file: ".beacon/implement/{run_id}/command.txt"
      supports_dry_run: true
      supports_review_writeback: true
```

---

## 10. 配置校验建议

Beacon 应对 runner 配置做至少这些校验：

1. `default_runner` 必须存在于 `runners` 中
2. 每个 runner 必须有 `type` / `command` / `args`
3. `type` 只能是 `command` 或 `command-skill`
4. `result_file` 必须存在或可推导
5. 模板变量必须可解析
6. 不允许 path template 逃离项目根目录

校验失败建议 reason code：

- `runner_config_invalid`
- `runner_path_invalid`
- `runner_template_invalid`
- `runner_default_missing`

---

## 11. 成功标准

- Runner 配置可被 project/global/default 三层解析；
- OMX 配置可作为标准示例直接使用；
- Beacon 能基于配置生成 request/result/runtime evidence 路径；
- Runner schema 简洁可扩展，不把 Beacon 绑定到单一实现器。
