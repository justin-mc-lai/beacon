# Beacon skill 子命令设计稿（v1.1.4 Draft）

## 1. 目标

新增顶层 `beacon skill` 子命令，用于管理用户偏好的实现类 AI skill 工具与适配器配置，使 Beacon 能够：

1. 检测当前项目/环境可用的 skill 工具；
2. 注册用户自定义 adapter；
3. 设置/查看默认偏好；
4. 为 `beacon implement` 提供稳定的 runner/skill 解析来源。

---

## 2. 为什么需要单独的 `skill` 子命令

如果没有 `beacon skill`：
- 用户偏好无处表达；
- adapter 配置会混入 `implement`，职责过重；
- 难以支持多工具并存（OMX、gstack、未来工具）；
- Beacon 无法形成“检测 / 注册 / 偏好 / doctor”这条独立能力链。

> 结论：`skill` 应独立于 `implement` 存在。

---

## 3. 定位

## `skill`
负责：
- 工具检测
- adapter 注册
- 偏好管理
- 配置校验

## `implement`
负责：
- 真正触发 implementation stage
- 消费 `skill` 解析结果
- 写 implementation evidence / marker / summary / review

---

## 4. 建议命令组

MVP：

```bash
beacon skill detect
beacon skill list
beacon skill show <id>
beacon skill register <id>
beacon skill prefer <id>
beacon skill doctor
```

后续可扩展：

```bash
beacon skill unregister <id>
beacon skill reset-preference
beacon skill export-config
```

---

## 5. 子命令定义

## 5.1 `skill detect`

### 语义
检测当前项目/环境可用的 AI skill 工具。

### 检测来源（建议）
- 项目目录特征
- 已安装 CLI
- 配置文件存在性
- skills 目录存在性

### 示例
```bash
beacon skill detect --project .
```

### 输出建议
| id | detected | evidence |
|---|---|---|
| `omx` | true | `omx` in PATH, `.omx/` found |
| `gstack` | true | `.claude/skills/gstack` found |
| `custom-x` | false | no config |

---

## 5.2 `skill list`

### 语义
列出 Beacon 当前已知/已注册的 skill adapters。

### 输出建议
| id | adapter_type | source | preferred | notes |
|---|---|---|---|---|
| `omx` | `command-skill` | project/global/builtin | yes/no | oh-my-codex adapter |
| `gstack` | `handoff` / `claude-skill` | project/global | yes/no | Claude skill workflow adapter |

---

## 5.3 `skill show <id>`

### 语义
查看某个 adapter 的完整解析结果。

### 应展示
- adapter id
- adapter_type
- command / entry
- request/result contract path templates
- preferred status
- source（CLI/project/global/builtin）
- doctor diagnostics

---

## 5.4 `skill register <id>`

### 语义
注册一个用户自定义 skill adapter。

### 示例
```bash
beacon skill register omx --type command-skill
beacon skill register gstack --type handoff
```

### 设计建议
MVP 阶段不一定直接交互创建完整 YAML；
可先提供：
- scaffold 输出
- 校验现有配置
- 提示用户补全 config block

---

## 5.5 `skill prefer <id>`

### 语义
将某个 adapter 设为当前默认实现偏好。

### 结果
写入：
- 项目配置：`beacon.config.yaml`
- 或全局配置：`~/.config/beacon/config.yaml`

### 示例
```bash
beacon skill prefer omx
beacon skill prefer gstack --scope global
```

---

## 5.6 `skill doctor`

### 语义
校验 skill adapter 是否可用，并输出 failure diagnostics。

### 典型检查
- CLI 是否存在
- skills 目录是否存在
- 配置是否完整
- request/result 路径模板是否合法
- preferred adapter 是否可解析

---

## 6. Adapter 类型建议

建议 `skill` 层支持比 `runner` 稍宽的 adapter family：

1. `command`
2. `command-skill`
3. `claude-skill`
4. `handoff`

### 说明
- `implement` MVP 执行器可先只真正执行 `command` / `command-skill`
- `claude-skill` / `handoff` 先用于 gstack 等非 shell-native 工具

---

## 7. 配置模型建议

```yaml
skill:
  preferred: omx

  adapters:
    omx:
      adapter_type: command-skill
      runtime_family: omx
      command: omx
      args:
        - run
        - --project-root
        - "{project_root}"
        - --task
        - "{task_prompt}"
      result_file: ".beacon/implement/{run_id}/result.json"

    gstack:
      adapter_type: handoff
      runtime_family: claude-code
      request_file: ".beacon/implement/{run_id}/request.md"
      result_file: ".beacon/implement/{run_id}/result.json"
      recommended_flows:
        - /review
        - /qa
        - /ship
```

---

## 8. 与 `implement` 的关系

```text
beacon skill detect/list/show/register/prefer/doctor
  -> manage adapter registry + preference
  -> beacon implement run resolves adapter
  -> implementation executes via resolved adapter
```

也就是说：
- `skill` 是 control/config plane
- `implement` 是 execution plane

---

## 9. 检测策略建议

### OMX 检测
- `omx` 命令存在于 PATH
- 项目中存在 `.omx/` 或 skill/runtime 痕迹
- 可选检测 `agent-skills/oh-my-codex` / 安装路径

### gstack 检测
- 项目或用户环境存在 `.claude/skills/gstack`
- 或已有 gstack slash command / workflow 目录
- 不要求 shell 可执行入口

---

## 10. 失败语义与 reason codes

建议新增：
- `skill_adapter_not_found`
- `skill_adapter_invalid`
- `skill_preference_invalid`
- `skill_runtime_not_detected`
- `skill_config_write_failed`

---

## 11. 成功标准

- 用户能声明自己偏好的实现 skill 工具；
- Beacon 能检测并展示已知适配器；
- `implement` 能稳定消费 `skill` 层配置；
- OMC/OMX 与 gstack 都能以不同 adapter 类型接入；
- Beacon 不因新增 `skill` 子命令而模糊 `implement` / `bridge` 的边界。
