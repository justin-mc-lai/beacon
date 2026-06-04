# Beacon v1.1.4 最新特性使用指南

> 目标：给 Beacon v1.1.4 的实际使用者一份**从安装、配置、dry-run、正式执行、review、delivery**的一站式操作说明。

---

## 1. 这份指南解决什么问题

Beacon v1.1.4 相比旧版本，真正新增并稳定交付了三类能力：

1. **正式实现适配层**
   - `beacon skill`
   - `beacon implement`
2. **标准 Skill 包**
   - `skills/beacon/`
   - `skills/beacon/scripts/run_beacon.sh`
3. **implementation 闭环写回**
   - request/result/runtime evidence
   - implementation marker
   - execution summary
   - `review spec` / `review quality`

如果你之前只把 Beacon 当成“写 PRD / User Story / Test Case 的工具”，那么从 v1.1.4 开始，它已经可以承担：

> **需求物料 → 实现适配 → review 写回 → verify / gate / release 交付闭环**

---

## 2. 先记住 Beacon v1.1.4 的角色

### Beacon 负责

- requirement materials
- implementation request/result contract
- execution evidence
- review / verify / gate / release 链路

### Beacon 不负责

- 替代外部 runtime 做多代理编排器
- 替代 IDE / tmux / scheduler
- 替代具体业务项目的部署平台

### 正确心智模型

```text
Beacon = delivery kernel
Runner / Skill = execution surface
```

---

## 3. v1.1.4 的最新特性总览

## 3.1 `beacon skill`

用于管理实现 Runner / Skill adapter：

```bash
beacon skill detect
beacon skill list
beacon skill show omx
beacon skill register <id> ...
beacon skill prefer <id>
beacon skill doctor
```

适合：
- 查看本机可用 runner
- 注册自定义 adapter
- 设定默认 runner

## 3.2 `beacon implement`

用于正式承接 implementation stage：

```bash
beacon implement list-runners
beacon implement run <feature>
beacon implement status <feature|run_id>
```

适合：
- 在 requirement materials 已准备好的前提下触发实现
- dry-run 检查 request / task prompt / command 拼装
- 查看 implementation summary / marker / review 状态

## 3.3 标准 skill 包

Beacon 现在同时提供：

### 兼容入口
- 根目录 `SKILL.md`

### 标准 skill 包
- `skills/beacon/SKILL.md`
- `skills/beacon/references/`
- `skills/beacon/scripts/run_beacon.sh`

标准 wrapper 用法：

```bash
bash skills/beacon/scripts/run_beacon.sh --version
bash skills/beacon/scripts/run_beacon.sh skill list
bash skills/beacon/scripts/run_beacon.sh implement list-runners --json
```

---

## 4. 典型工作流（最新推荐）

## 4.1 第一步：先准备主链物料

至少准备：

```text
docs/beacon/<version>/
├── user-story/<feature>.md
├── prd/<feature>.md
└── qa/test-cases/<feature>.md
```

如果还没写，可以先用：

```bash
beacon think start "<feature>" --project . --version v1.1.4
beacon user-story create "<feature>" --project . --version v1.1.4
beacon prd create "<feature>" --project . --version v1.1.4
beacon test-case create "<feature>" --project . --version v1.1.4
```

## 4.2 第二步：检查 runner

```bash
beacon skill detect --json
beacon skill list --json
beacon implement list-runners --json
```

重点看：
- `preferred`
- `detected`
- `adapter_type`

## 4.3 第三步：先 dry-run

这是 v1.1.4 最推荐的实践。

```bash
beacon implement run "<feature>" \
  --project-root . \
  --version v1.1.4 \
  --runner omx \
  --dry-run \
  --json
```

dry-run 要检查三件事：

1. `request.json` 是否正确生成
2. `task_prompt` 是否引用了正确的 user-story / prd / test-case
3. `command` 是否是你预期的 runner 调用方式

## 4.4 第四步：正式执行

```bash
beacon implement run "<feature>" \
  --project-root . \
  --version v1.1.4 \
  --runner omx \
  --json
```

执行成功后，Beacon 会尝试生成：

```text
.beacon/implement/<run_id>/request.json
.beacon/implement/<run_id>/result.json
.beacon/state/implementation-<feature>.json
docs/beacon/<version>/execution/implementation-summary-<feature>.json
docs/beacon/<version>/execution/implementation-summary-<feature>.md
docs/beacon/<version>/execution/review-spec-<feature>.json
```

## 4.5 第五步：查看状态

```bash
beacon implement status <feature> --project-root . --version v1.1.4 --json
```

重点看：
- `summary_exists`
- `review_spec_exists`
- `review_quality_exists`
- `implementation_marker_exists`

## 4.6 第六步：review / verify / gate

```bash
beacon review spec <feature> --project . --version v1.1.4 --json
beacon review quality <feature> --project . --version v1.1.4 --json
beacon gate check release --project-root . --version v1.1.4 --json
```

---

## 5. runner 真实推荐顺序

## 5.1 OMX：当前最推荐

Beacon 当前内置的 **OMX** 是最推荐的直接实现 runner。

### 当前内置命令模型

```bash
omx exec --full-auto --cd "{project_root}" --skip-git-repo-check "{task_prompt}"
```

### 为什么推荐 OMX

- 有稳定非交互入口：`omx exec`
- 支持 skill/workflow 风格任务提示
- 能适配非 git workspace（通过 `--skip-git-repo-check`）
- 已在 Beacon v1.1.4 内置与测试

## 5.2 gstack：handoff-first

`gstack` 当前更适合作为：

- `handoff`
- 或人工接续型执行面

它不是 Beacon v1.1.4 当前最推荐的自动执行 runner。

## 5.3 OMC：建议先项目内显式覆盖

Beacon 内置有 `omc` adapter，但实战上：

- 请先核实你本机的 OMC CLI 实际可用命令
- 若你项目要长期使用 OMC，建议在项目 `beacon.config.yaml` 里显式定义 args，而不要只依赖内置默认值

---

## 6. `beacon.config.yaml` 最新推荐写法

## 6.1 最小 omx 配置

```yaml
skill:
  preferred: omx

implementation:
  default_runner: omx
  auto_review_spec: true
  auto_review_quality: false
```

## 6.2 自定义 omx 配置

```yaml
skill:
  preferred: omx

implementation:
  default_runner: omx
  auto_review_spec: true
  auto_review_quality: false
  runners:
    omx:
      adapter_type: command-skill
      runtime_family: omx
      command: omx
      args:
        - exec
        - --full-auto
        - --cd
        - "{project_root}"
        - --skip-git-repo-check
        - "{task_prompt}"
      skill_prefix: "$workflows-work"
      timeout_sec: 3600
      result_file: ".beacon/implement/{run_id}/result.json"
```

---

## 7. 三种实战项目用法

## 7.1 单仓项目

适合：
- 一个 repo
- 一个 feature 对应一组 `user-story/prd/test-case`

推荐：
- 直接用 `beacon implement run <feature> --runner omx`

## 7.2 非 git / 内容型项目

例如：
- WordPress 目录
- 主题目录
- 站点工程目录

推荐：
- 先把 feature 切成 implement-ready slices
- 使用内置 omx，因为已包含 `--skip-git-repo-check`

## 7.3 多服务 workspace 项目

例如：
- 根目录是 workspace
- 子目录才是真正服务 repo

推荐：
- Beacon 负责 feature / service-slice / release / delivery evidence
- 真实代码实现进入服务 repo 执行
- 不建议直接把 workspace 根目录当成单服务实现目录

---

## 8. 失败时怎么看

常见 `reason_code`：

- `runner_not_configured`
- `runner_command_not_found`
- `runner_execution_timeout`
- `runner_execution_failed`
- `runner_result_missing`
- `runner_result_invalid`
- `implement_execution_failed`

### 推荐排查顺序

1. `beacon implement run ... --dry-run --json`
2. 看 `.beacon/implement/<run_id>/request.json`
3. 看 `.beacon/implement/<run_id>/command.txt`
4. 看 `.beacon/implement/<run_id>/stdout.log`
5. 看 `.beacon/implement/<run_id>/stderr.log`
6. 跑 `beacon implement status <feature> --json`

---

## 9. 最新版 Beacon 的最佳实践

1. **先写主链，再 implement**
2. **先 dry-run，再正式执行**
3. **feature 粒度不合适时，先切 slice**
4. **把 Beacon 当 delivery kernel，不是通用调度器**
5. **对多服务项目，用 Beacon 管需求闭环，用项目自身开发规范管实现**

---

## 10. 一句话总结

如果你之前把 Beacon 理解成：

> “一个写 PRD / User Story / Test Case 的工具”

那么从 v1.1.4 开始，更准确的理解应该是：

> **一个带 implementation adapter、review 写回和标准 skill 包的 delivery kernel。**

