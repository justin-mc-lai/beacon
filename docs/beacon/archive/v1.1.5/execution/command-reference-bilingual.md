# Beacon v1.1.5 Command Guide / 命令指南（双语）

> Bilingual quick guide for external users and operators.

---

## 1. What Beacon is / Beacon 是什么

**EN**  
Beacon is an evidence-first product workflow CLI. It helps teams turn a feature idea into structured requirement materials, implementation requests, verification evidence, and release checks.

**中文**  
Beacon 是一个 evidence-first 的产品工作流 CLI。它帮助团队把一个功能想法收敛成结构化需求文档、实现请求、验证证据和发布检查。

---

## 2. Recommended entrypoint / 推荐入口

**EN**

```bash
beacon <subcommand>
```

**中文**

```bash
beacon <子命令>
```

For v1.1.5, prefer explicit version pinning for release-sensitive work:

```bash
beacon <subcommand> ... --version v1.1.5
```

对 v1.1.5，涉及发布与验收的操作建议显式带上：

```bash
beacon <子命令> ... --version v1.1.5
```

---

## 3. Quick start / 快速开始

### Plan from natural language / 从自然语言开始规划

```bash
beacon ask "Create a release-ready requirement package" \
  --project-root . \
  --version v1.1.5 \
  --plan-only --json
```

```bash
beacon ask "生成一个可发布的需求包" \
  --project-root . \
  --version v1.1.5 \
  --plan-only --json
```

### Start a workflow / 启动工作流

```bash
beacon workflow start "Beacon v1.1.5 layered delivery" --project . --version v1.1.5
```

### Generate the main-chain artifacts / 生成主链文档

```bash
beacon think start "Beacon v1.1.5 layered delivery" --project . --version v1.1.5
beacon user-story create "Beacon v1.1.5 layered delivery" --project . --version v1.1.5
beacon prd create "Beacon v1.1.5 layered delivery" --project . --version v1.1.5
beacon test-case create "Beacon v1.1.5 layered delivery" --project . --version v1.1.5
```

---

## 4. High-frequency commands / 高频命令

| Command | EN | 中文 |
| --- | --- | --- |
| `beacon ask` | Route one natural-language goal into a plan or execution path | 把自然语言目标路由成计划或执行路径 |
| `beacon workflow` | Run the full workflow state machine | 运行完整工作流状态机 |
| `beacon think` | Clarify requirements and capture facts/questions/conflicts | 做需求澄清，记录事实/问题/冲突 |
| `beacon user-story` | Generate user stories | 生成用户故事 |
| `beacon prd` | Generate PRDs | 生成 PRD |
| `beacon test-case` | Generate test cases and AC matrices | 生成测试用例和 AC 矩阵 |
| `beacon implement` | Run implementation through configured adapters | 通过已配置适配器执行实现 |
| `beacon doctor` | Verify or repair package/environment/docs context | 校验或修复包结构、环境与上下文 |
| `beacon gate` | Run gate checks | 执行 gate 检查 |
| `beacon release` | Create or check release readiness | 创建或检查发布准备情况 |

---

## 5. Scenario lookup / 场景速查

### EN: “I only know the goal”
### 中文：“我只知道目标，不知道具体命令”

```bash
beacon ask "<goal>" --project-root . --version v1.1.5 --plan-only --json
```

### EN: “I want to repair an old package to the v1.1.5 layout”
### 中文：“我要把旧包修到 v1.1.5 的分层结构”

```bash
beacon doctor repair-package --project-root . --version v1.1.5 --json
```

### EN: “I need release readiness evidence”
### 中文：“我要看发布就绪证据”

```bash
beacon doctor verify-materials --project-root . --version v1.1.5 --json
beacon doctor verify-delivery --project-root . --version v1.1.5 --json
beacon gate check release --project-root . --version v1.1.5 --json
beacon release check v1.1.5 --project .
```

### EN: “I need implementation via OMX”
### 中文：“我要通过 OMX 执行实现”

```bash
beacon skill list --json
beacon implement list-runners --json
beacon implement run "<feature>" --runner omx --project . --version v1.1.5 --json
```

---

## 6. Human vs machine reading order / 人类与机器的阅读顺序

**EN**

Humans should start with:

1. `SUMMARY.md`
2. `execution/index.md`
3. `command-guide-readme.md`
4. `scenario-quick-reference.md`

Machines should primarily read:

- `.machine/execution/`
- `.machine/qa/`

**中文**

人类建议先看：

1. `SUMMARY.md`
2. `execution/index.md`
3. `command-guide-readme.md`
4. `scenario-quick-reference.md`

机器主要读取：

- `.machine/execution/`
- `.machine/qa/`

---

## 7. Advanced surfaces / 高级命令面

**EN**

- `beacon labs <command>` for PM / analysis templates
- `beacon bridge <command>` for bridge/runtime workflows
- `beacon prompt` for router internals

**中文**

- `beacon labs <command>`：产品/分析模板命令
- `beacon bridge <command>`：bridge/runtime 工作流
- `beacon prompt`：查看路由器内部计划与 contract

Examples / 示例：

```bash
beacon labs analyze create "Beacon vs OpenSpec" --project . --version v1.1.5
beacon bridge team start "Beacon release rollout" --project .
beacon prompt catalog --project-root . --version v1.1.5 --json
```

---

## 8. Recommended next docs / 推荐继续阅读

**EN**

- `command-reference.md`
- `scenario-quick-reference.md`
- `../release/v1.1.5.md`

**中文**

- `command-reference.md`
- `scenario-quick-reference.md`
- `../release/v1.1.5.md`
