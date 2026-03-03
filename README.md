# Beacon CLI

> AI Product Workflow Toolkit — 需求澄清、用户故事、PRD、测试用例的完整工作流

[![PyPI version](https://img.shields.io/pypi/v/beacon-cli)](https://pypi.org/project/beacon-cli/)
[![Python](https://img.shields.io/python/pyversions/beacon-cli)](https://pypi.org/project/beacon-cli/)
[![License](https://img.shields.io/pypi/l/beacon-cli)](./LICENSE)

---

## 1. Beacon 是什么

Beacon 是面向 AI 时代的智能产品工作流工具，帮助团队将「需求想法」稳定地转化为「可交付证据」。

### 核心价值

| 价值 | 说明 |
|------|------|
| **效率提升** | 一键生成 US/PRD/TC 产物链，减少手工切换 |
| **范围保障** | 越界检测与预警，避免范围漂移 |
| **交付确定性** | 明确的终态判定（Pass / Blocked / Cancelled） |
| **证据可信** | 完整证据链，支持审计与复盘 |

### 与历史 PTK 的关系（背景）

Beacon 从 product-toolkit（历史 PTK）升级而来。当前命令口径已统一到 Beacon：仅保留 `beacon` 命令入口，历史 PTK 仅作背景说明。

- **CLI**: 统一使用 `beacon-<subcommand>`（兼容 `beacon <subcommand>`）
- **文档**: `docs/beacon/` 为主，`docs/product/` 为历史 PTK 兼容
- **状态**: `.beacon/` 目录（原有 `.ptk/` 别名兼容）
- **兼容策略**: 仅保留目录兼容（`.ptk`、`docs/product`），命令口径统一为 `beacon`
- **Skill**: 默认使用 `beacon-<subcommand>` 触发（`/beacon:` 仅在支持该语法的平台可用）

### v1.0.0 功能特性（命令口径统一为 Beacon）

1. **三层防线**：Gate 门控 + 证据驱动 + 记忆体约束，默认 strict-by-default。
2. **扁平命令体验**：保留 `auto-test`、`work`、`report --machine` 等常见用法，统一通过 Beacon 命令执行。
3. **工作流记忆闭环**：阶段开始/结束自动沉淀 memory，支持 recall 注入与 feedback 反哺。
4. **UI 防假通过强校验（auto-test）**：
   - `expectation=success` 且 `origin != target` -> `failed`
   - `expectation=error` 命中重定向/错误证据 -> `passed`
   - strict 下无显式 UI assertion -> `blocked`
5. **可审计交付**：运行态/报告/终态产物可追溯，支持 Gate reason code 级别定位。

### v1.0.1 最小补齐（MVP 不失真）

1. **Verify 终态硬条件**：`verify` 仅在 `.beacon/auto-test-status.json.status=passed` 时闭环，否则 workflow 直接 `blocked`。
2. **UI 无真实执行默认阻断**：非 debug（`BEACON_DEBUG` 未开启）下，`expectation=unknown` 不再放行，统一 `blocked(ui_real_execution_required)`。
3. **版本落盘统一**：`think/user-story/prd/test-case/report` 全链路支持 `--version`，并同步写入 `docs/beacon/<version>`（兼容镜像到 `docs/product/<version>`）。
4. **Coverage 强校验接入 gate**：输出 `story/ac/tc` 覆盖指标，strict/debug 在 `test-case/release` 阶段未满覆盖直接 `coverage_incomplete`。
5. **Workflow 终态下一步选择器**：完成/阻断后固定输出 OMC / OMX / Beacon Team 三选一路径，避免“结束后无下一步”。

### 对齐增强（2026-03-03）

1. **Workflow ↔ Gate strict 一致性修复**：终态自动补齐 release-profile memory、implementation marker、manifest 同步，`workflow start --auto` 与 strict gate 结果一致。
2. **CLI/Skill 单一事实源**：`SKILL.md` 命令表由 `beacon/prefixed.py::SUPPORTED_SUBCOMMANDS` 自动同步（`scripts/sync_skill_commands.py`）。
3. **版本治理增强**：`beacon version create` 支持 `--base-version + --bump`，并自动写入版本元数据用于追溯。
4. **演进总结真实化**：`beacon evolution-summary create` 汇总真实 run/memory/coverage/evidence 差异，不再输出模板 TBD。
5. **可选真实 LLM 编排**：设置 `BEACON_LLM_MODE=real` + `BEACON_LLM_API_KEY` 后，next-stage 推理可走真实模型；失败自动回退规则模式。
6. **Visual 回归能力**：`auto-test` 新增 `visual` 层与目录哈希对比能力，支持阈值判定。

📘 详细说明见：[Beacon 功能说明与闭环流程（v1.0.1）](./docs/beacon/v1.0.1/execution/beacon-feature-closure-guide.md)

---

## 2. 快速开始

### 2.1 安装

```bash
# 通过 pip 安装
pip install beacon-cli

# 或从源码安装
cd beacon
pip install -e .
```

### 2.2 5 个核心命令速览

> 命令规则定案：统一采用 `beacon-<subcommand>`，例如 `beacon-think`、`beacon-workflow`。

```bash
# 1. 启动完整工作流
beacon-workflow start "用户登录功能"

# 2. 产品思考
beacon-think start "用户登录优化"
beacon-think confirm "用户需要社交登录"
beacon-think question "是否需要支持企业SSO?" --priority high --blocking

# 3. 生成用户故事
beacon-user-story create "用户登录"

# 4. 生成 PRD
beacon-prd create "用户登录"

# 5. 生成测试用例
beacon-test-case create "用户登录"
```

### 2.3 完整示例：做一个"用户登录"功能

```bash
# === 步骤 1: 产品思考 ===
# 启动思考会话，探索需求细节
beacon-think start "用户登录功能"
beacon-think confirm "用户需要账号密码登录"
beacon-think confirm "用户需要社交账号登录（Google/GitHub）"
beacon-think question "是否需要支持企业 SSO?" --priority high --blocking
beacon-think question "登录会话有效期多长?" --priority medium

# 查看思考进度
beacon-think status

# 生成思考总结
beacon-think summarize

# === 步骤 2: 生成用户故事 ===
beacon-user-story create "用户登录"

# === 步骤 3: 生成 PRD ===
beacon-prd create "用户登录"

# === 步骤 4: 生成测试用例 ===
beacon-test-case create "用户登录" --type all

# === 步骤 5: 检查工作流状态 ===
beacon-workflow status

# === 步骤 6: 运行门控检查 ===
beacon-workflow gate
```

---

## 3. 核心概念

### 3.1 工作流阶段

```
┌─────────┐   ┌────────────┐   ┌──────┐   ┌───────────┐   ┌────────────────┐   ┌────────┐   ┌──────┐
│  Think  │ → │ User Story │ → │ PRD  │ → │ Test Case │ → │ Implementation │ → │ Verify │ → │ Gate │
└─────────┘   └────────────┘   └──────┘   └───────────┘   └────────────────┘   └────────┘   └──────┘
   需求澄清    用户故事        需求文档     测试矩阵         对齐实现开发编码        多层测试     交付门控
```

| 阶段 | 命令 | 产出 |
|------|------|------|
| Think | `beacon-think *` | 确认事实、开放问题、冲突记录 |
| User Story | `beacon-user-story *` | 用户故事文档 |
| PRD | `beacon-prd *` | 产品需求文档 |
| Test Case | `beacon-test-case *` | 测试用例文档 + AC 可执行矩阵 |
| Implementation | `beacon-workflow start --auto` | 实现阶段执行记录 |
| Verify | `beacon-auto-test create *` | 多层真实执行证据 |
| Gate | `beacon-workflow gate` | Pass / Blocked / Cancelled |

### 3.1.1 工作流生命周期（Lifecycle）与记忆体

Beacon 的 workflow 生命周期主链为 6 阶段：

`think → user-story → prd → test-case → implementation → verify`

每个阶段在记忆体中会写入 4 类事件（完成态闭环）：

1. `stage_started`
2. `stage_context_injected`（recall 注入）
3. `stage_finished`
4. `memory_writeback`（写回 insight/decision）

阶段状态判定：

- `not_started`：无事件
- `in_progress`：仅有部分事件
- `completed`：4 类事件齐全
- `failed`：存在 `stage_failed`

> v1.0.1 起，`beacon-workflow start --auto=false` 只写 `workflow_planned`，不再提前写阶段 started/context，避免“未执行却显示已开始”的失真。

### 3.2 文档输出结构

```
项目根目录/
├── docs/
│   ├── beacon/                    # Beacon 专用
│   │   └── v1.0.0/
│   │       ├── prd/
│   │       ├── user-story/
│   │       └── qa/test-cases/
│   └── product/                   # 历史 PTK 兼容
│       └── v1.0.0/
│           └── ...
├── .beacon/                      # 状态目录
│   ├── state/
│   │   └── think-progress.json
│   └── memory/
└── beacon (CLI 入口)
```

### 3.3 门控检查

| 阶段 | 门控项 | 判定标准 |
|------|--------|---------|
| Think | 收敛门 | 无 `blocking=true` 的未决项 |
| User Story | AC门 | 七维 AC 完整 |
| PRD | 风险门 | critical/high 冲突已解决 |
| Test Case | 覆盖门 | AC→TC 覆盖矩阵完整且可执行 |
| Verify | 执行门 | UI/API/Unit/Smoke 真实执行，关键动作证据完整 |
| Release | 测试门 | 冒烟测试 100% 通过 |

---

## 4. 命令参考

### 4.1 工作流命令

#### `beacon-workflow`

完整产品工作流管理。

```bash
# 启动工作流
beacon-workflow start <feature>
beacon-workflow start "用户登录" --auto          # 自动执行所有阶段
beacon-workflow start "用户登录" --skip think    # 跳过 think 阶段

# 基于记忆体进度续跑（v1.0.1）
beacon-workflow continue --version v1.0.1               # 自动定位 next_stage，执行一步
beacon-workflow continue --version v1.0.1 --auto        # 从 next_stage 一路补齐到 verify
beacon-workflow continue --run-id run-xxxx --auto       # 指定 run_id 续跑

# 自动模式（新增 implementation / verify 阶段）
beacon-workflow start "用户登录" --auto \
  --implementation-command "python -m pytest -q tests/test_login_flow.py" \
  --verify-scope all \
  --verify-ui-command "python -m pytest -q -k ui" \
  --verify-api-curl-command "bash -lc 'curl -fsS http://127.0.0.1:8000/health'" \
  --verify-unit-command "python -m pytest -q -k unit" \
  --verify-smoke-command "python -m pytest -q -m smoke"

# 仅计划，不执行阶段（manual）
beacon-workflow start "用户登录" --version v1.0.1
# 说明：manual 模式只写 workflow_planned，不写 stage_started/context

# 查看状态
beacon-workflow status
beacon-workflow status --version v1.0.0
beacon-workflow status --version v1.0.1 --feature "用户登录"

# 门控检查
beacon-workflow gate
beacon-workflow gate think        # 只检查 think 阶段

# 运行任意子命令
beacon-workflow run kano "功能A"
beacon-workflow run analyze
```

| 子命令 | 说明 |
|--------|------|
| `start` | 启动完整产品工作流 |
| `continue` | 按记忆体生命周期自动续跑下一阶段（或全链路补齐） |
| `status` | 显示工作流各阶段状态 |
| `gate` | 运行阶段门控检查 |
| `run` | 运行任意 beacon 子命令 |

说明：
- `verify` 阶段会执行“终态硬校验”：缺失状态文件、JSON 非法、或 `status!=passed` 均判定失败。
- workflow 完成/阻断时会输出 `NEXT STEP SELECTOR`（OMC / OMX / Beacon Team + 继续命令）。

#### `beacon-gate`

门控检查工具。

```bash
# 检查所有阶段
beacon-gate

# 检查指定阶段
beacon-gate think
beacon-gate user-story
beacon-gate prd
beacon-gate test-case
beacon-gate release

# strict/debug 模式下会阻断以下测试可信性问题：
# - 未执行即失败（test_execution_missing）
# - 关键动作缺失即失败（test_key_actions_missing）
# - AC→TC→执行证据链断裂即失败（ac_tc_evidence_chain_broken）
# - 覆盖不完整即失败（coverage_incomplete）
```

---

### 4.2 思考命令

#### `beacon-think`

产品思考 vNext — 使用苏格拉底式提问探索需求。

```bash
# 启动思考会话
beacon-think start "用户登录优化"

# 查看状态
beacon-think status

# 确认事实
beacon-think confirm "用户需要社交登录"

# 添加问题
beacon-think question "是否需要企业SSO?" --priority high --blocking
beacon-think question "会话有效期?" --priority medium

# 记录冲突
beacon-think conflict semantic "安全和易用性冲突"
beacon-think conflict boundary "边界条件定义不清"

# 生成总结
beacon-think summarize
```

| 子命令 | 说明 | 参数 |
|--------|------|------|
| `start` | 启动新思考会话 | `<topic>` |
| `status` | 显示思考状态 | - |
| `confirm` | 确认一个事实 | `<fact>` |
| `question` | 添加开放问题 | `<question>` |
| `conflict` | 记录冲突 | `<type> <description>` |
| `summarize` | 生成思考总结 | - |

---

### 4.3 文档命令

#### `beacon-user-story`

用户故事生成与管理。

```bash
# 生成用户故事
beacon-user-story create "用户登录"

# 列出已有用户故事
beacon-user-story list
```

#### `beacon-prd`

PRD（产品需求文档）生成与管理。

```bash
# 生成 PRD
beacon-prd create "用户登录"

# 列出已有 PRD
beacon-prd list
```

#### `beacon-test-case`

测试用例生成与管理。

```bash
# 生成测试用例
beacon-test-case create "用户登录"
beacon-test-case create "用户登录" --type smoke   # 只生成冒烟测试
beacon-test-case create "用户登录" --type new     # 新功能测试
beacon-test-case create "用户登录" --type all     # 全部测试

# 产出包含：
# 1) docs/product/<version>/qa/test-cases/<feature>.md
# 2) docs/product/<version>/qa/test-cases/<feature>.ac-test-matrix.json
#    每条包含 layer / command / assertion / evidence_path（AC->TC 可执行矩阵）

# 列出已有测试用例
beacon-test-case list

# 门控检查
beacon-test-case gate "用户登录"
```

---

### 4.4 分析命令

#### `beacon-analyze`

需求分析。

```bash
beacon-analyze
beacon-analyze --feature "用户登录"
```

#### `beacon-brainstorm`

头脑风暴模式。

```bash
beacon-brainstorm "用户登录"
beacon-brainstorm "用户登录" --mode creative
```

#### `beacon-design`

设计阶段。

```bash
beacon-design "用户登录"
beacon-design "用户登录" --type ui
```

#### `beacon-jtbd`

Jobs-to-be-Done 分析。

```bash
beacon-jtbd "用户登录"
```

#### `beacon-kano`

KANO 模型分析 — 需求分类（基本型、期望型、兴奋型）。

```bash
beacon-kano "用户登录"
beacon-kano "用户登录" --add "社交登录"
beacon-kano "用户登录" --list
```

#### `beacon-moscow`

MoSCoW 优先级划分 — Must/Should/Could/Won't。

```bash
beacon-moscow "用户登录"
beacon-moscow "用户登录" --add "账号密码" must
beacon-moscow "用户登录" --add "社交登录" should
```

#### `beacon-roadmap`

路线图规划。

```bash
beacon-roadmap
beacon-roadmap v2.0.0
beacon-roadmap --timeline 2026-Q1,2026-Q2
```

#### `beacon-persona`

用户画像。

```bash
beacon-persona "用户登录"
beacon-persona list
```

#### `beacon-version`

版本管理。

```bash
# 自动沿用当前最大语义版本
beacon-version create "用户登录"

# 从指定基线 bump（推荐）
beacon-version create "用户登录" --base-version v1.0.1 --bump minor

# 手动指定目标版本
beacon-version create "用户登录" --version v2.0.0
beacon-version list
```

#### `beacon-evolution-summary`

版本演进总结。

```bash
beacon-evolution-summary create v1.0.1 --previous v1.0.0
beacon-evolution-summary create auto --json
```

---

### 4.5 运维命令

#### `beacon-doctor`

环境诊断与修复。

```bash
beacon-doctor
beacon-doctor --fix
```

#### `beacon-status`

状态面板。

```bash
beacon-status
beacon-status --verbose
beacon-status --board --version v1.0.1 --feature "用户登录"
```

#### `beacon-report`

生成报告。

```bash
beacon-report
beacon-report --machine
beacon-report --machine --version v1.0.0
beacon-report --machine --version v1.0.1 --feature "用户登录"
```

#### `beacon-debug`

调试模式。

```bash
beacon-debug
beacon-debug --trace
```

#### `beacon-feedback`

测试反馈同步。

```bash
beacon-feedback
beacon-feedback --sync
```

#### `beacon-resume`

恢复会话。

```bash
beacon-resume
beacon-resume session-123
```

#### `beacon-init`

项目初始化。

```bash
beacon-init
beacon-init --template minimal
```

---

### 4.6 测试与发布命令

#### `beacon-auto-test`

自动化测试。

```bash
# 启动一次自动测试（写入 .beacon/auto-test-status.json）
beacon-auto-test create ui --project .

# 多层真实执行（ui/api-curl/unit/smoke）
beacon-auto-test create all --project . \
  --ui-command "python -m pytest -q -k ui" \
  --api-curl-command "bash -lc 'curl -fsS http://127.0.0.1:8000/health'" \
  --unit-command "python -m pytest -q -k unit" \
  --smoke-command "python -m pytest -q -m smoke"

# Visual 回归（目录哈希比对）
beacon-auto-test create visual --project . \
  --visual-baseline-dir .beacon/visual/baseline \
  --visual-current-dir .beacon/visual/current \
  --visual-threshold 0.02

# UI 防假通过校验（继承历史规则）
beacon-auto-test create ui \
  --project . \
  --expectation success \
  --target-url /admin/dashboard \
  --origin-url /admin/login \
  --ui-assertion "url_contains:/admin/dashboard"

# strict 下无断言直接 blocked
beacon-auto-test create ui \
  --project . \
  --expectation success \
  --target-url /admin/dashboard \
  --origin-url /admin/dashboard \
  --strict-ui-assertion

# 非 debug 下，UI expectation=unknown 默认 blocked（防假通过）
beacon-auto-test create ui --project . --expectation unknown
# 若仅调试启发式行为，可显式开启：
BEACON_DEBUG=1 beacon-auto-test create ui --project . --expectation unknown

# 关键动作证据校验（缺任一项即失败）
beacon-auto-test create ui \
  --project . \
  --expectation success \
  --target-url /dashboard \
  --origin-url /dashboard \
  --require-ui-actions \
  --ui-action-evidence "login=.beacon/evidence/ui/login.json" \
  --ui-action-evidence "register=.beacon/evidence/ui/register.json" \
  --ui-action-evidence "browse=.beacon/evidence/ui/browse.json" \
  --ui-action-evidence "submit-form=.beacon/evidence/ui/submit-form.json"

# 结合 AC 矩阵回写执行证据（生成 evidence_path 文件）
beacon-auto-test create all \
  --project . \
  --matrix-path docs/product/v1.0.1/qa/test-cases/用户登录.ac-test-matrix.json \
  --layer-command "ui=python -m pytest -q -k ui" \
  --layer-command "api-curl=bash -lc 'curl -fsS http://127.0.0.1:8000/health'" \
  --layer-command "unit=python -m pytest -q -k unit" \
  --layer-command "smoke=python -m pytest -q -m smoke"

# 查看测试状态
beacon-auto-test status --project .
beacon-auto-test status --project . --json
```

常见 `ui_guard.reason_code`：
- `ui_expectation_success_mismatch`
- `ui_expectation_error_redirect`
- `ui_origin_target_unknown`
- `ui_assertion_missing_strict`

新增与交付可信相关的 gate reason_code（strict/debug）：
- `test_execution_missing`
- `test_key_actions_missing`
- `ac_tc_evidence_chain_broken`
- `coverage_incomplete`

#### `beacon-test-progress`

测试进度跟踪。

```bash
beacon-test-progress
beacon-test-progress --verbose
```

#### `beacon-release`

发布流程。

```bash
beacon-release v1.0.0
beacon-release v1.0.0 --dry-run
```

---

### 4.7 技术设计命令

#### `beacon-api-design`

API 设计。

```bash
beacon-api-design "用户登录"
beacon-api-design "用户登录" --format openapi
```

#### `beacon-data-dictionary`

数据字典。

```bash
beacon-data-dictionary
beacon-data-dictionary "用户"
```

---

### 4.8 设计协作命令

#### `beacon-ui-spec`

UI 规范。

```bash
beacon-ui-spec "用户登录"
beacon-ui-spec "用户登录" --theme dark
```

#### `beacon-wireframe`

线框图。

```bash
beacon-wireframe "登录页面"
beacon-wireframe "登录页面" --export png
```

---

### 4.9 记忆系统命令

#### `beacon-save`

保存上下文。

```bash
beacon-save "当前思考"
beacon-save "当前思考" --tags work,login
```

#### `beacon-recall`

召回上下文。

```bash
beacon-recall
beacon-recall "当前思考"
beacon-recall --tag work
```

#### `beacon-remember`

长期记忆。

```bash
beacon-remember "用户偏好"
beacon-remember list
```

---

### 4.10 协作命令

#### `beacon-team`

团队模式。

```bash
beacon-team start
beacon-team status
beacon-team status
```

#### `beacon-ralph-bridge`

Ralph 桥接。

```bash
beacon-ralph-bridge connect
beacon-ralph-bridge status
```

---

## 5. 使用示例

### 5.1 完整产品工作流

```bash
# 方式一：手动分步执行
beacon-think start "点赞功能"
beacon-think confirm "用户需要对内容点赞"
beacon-think summarize
beacon-user-story create "点赞功能"
beacon-prd create "点赞功能"
beacon-test-case create "点赞功能"
beacon-workflow gate

# 方式二：自动执行
beacon-workflow start "点赞功能" --auto
```

### 5.2 KANO 需求优先级

```bash
# 1. 启动 KANO 分析
beacon-kano "用户登录"

# 2. 添加需求并分类
beacon-kano "用户登录" --add "账号密码" must
beacon-kano "用户登录" --add "社交登录" should
beacon-kano "用户登录" --add "生物识别" could
beacon-kano "用户登录" --add "语音登录" wont

# 3. 查看分析结果
beacon-kano "用户登录" --list

# 4. 生成报告
beacon-kano "用户登录" --report
```

### 5.3 团队协作

```bash
# 1. 启动团队会话
beacon-team start "登录功能评审"

# 2. 推进团队评审状态
beacon-team status
beacon-team review spec pass --reviewer pm
beacon-team review quality pass --reviewer qa

# 3. 记录讨论
beacon-save "登录功能评审结论" --tags team,login

# 4. 生成会议纪要
beacon-team report --format both
```

---

## 6. 配置说明

### 6.1 .beacon 目录

```
.beacon/
├── runs/
│   └── run-*/state.json               # 每次 workflow run 的状态（feature/version/mode/events）
├── state/
│   ├── think-progress.json    # 思考会话状态
│   └── workflow-memory/<run_id>/      # 阶段 recall 注入上下文
├── memory/
│   ├── workflow-lifecycle.json        # 生命周期事件主文件
│   ├── workflow-lifecycle.index.json  # 去重索引
│   ├── workflow-lifecycle.schema.json # schema
│   ├── project-insights.json          # insight 写回
│   └── decisions.json                 # decision 写回
└── config.yaml               # 配置文件
```

### 6.4 记忆体使用（workflow + memory）

推荐路径：

1. `beacon-workflow start "<feature>" --version <vX.Y.Z>`（manual 仅计划）
2. `beacon-workflow continue --version <vX.Y.Z>`（执行 next_stage）
3. `beacon-workflow continue --version <vX.Y.Z> --auto`（补齐到 verify）
4. `beacon-status --board --version <vX.Y.Z>` 查看 `next_stage/closure_complete`
5. `beacon-report --machine --version <vX.Y.Z>` 导出可审计进度

定位口径：

- 优先按 `run_id`
- 否则按 `version + feature` 定位 workflow run
- 再回退到最新 workflow run

### 6.2 配置文件

```yaml
# .beacon/config.yaml
version: "1.0.0"

# 文档输出目录
docs:
  primary: "docs/beacon"      # 主要目录
  compatibility: "docs/product"  # 历史 PTK 兼容

# 工作流配置
workflow:
  auto_gate: true            # 自动门控
  strict_mode: false         # 严格模式

# 输出格式
output:
  format: "markdown"
  template: "default"
```

### 6.3 环境变量

```bash
# 指定项目根目录
BEACON_PROJECT=/path/to/project

# 指定版本
BEACON_VERSION=v1.0.0

# 调试模式
BEACON_DEBUG=1
```

---

## 7. 目录结构

### 7.1 项目文件组织

```
beacon/
├── beacon/                    # CLI 源码
│   ├── main.py               # 入口
│   ├── commands/             # 命令模块
│   │   ├── workflow.py
│   │   ├── think.py
│   │   ├── user_story.py
│   │   ├── prd.py
│   │   ├── test_case.py
│   │   └── ... (37 个命令)
│   └── utils/
├── docs/
│   ├── beacon/               # Beacon 文档
│   └── product/             # 历史 PTK 兼容
├── references/               # 参考文档
│   ├── socratic-questioning.md
│   └── acceptance-criteria.md
├── scripts/                  # 脚本
├── SKILL.md                 # Skill 定义
└── pyproject.toml           # 项目配置
```

### 7.2 文档输出示例

```
项目根目录/
├── docs/
│   └── beacon/
│       └── v1.0.0/
│           ├── prd/
│           │   └── 用户登录.md
│           ├── user-story/
│           │   └── 用户登录.md
│           ├── qa/
│           │   └── test-cases/
│           │       └── 用户登录.md
│           └── execution/
│               ├── boundaries.md
│               └── terminal.json
└── .beacon/
    └── state/
        └── think-progress.json
```

---

## 8. 常见问题

### Q1: 如何升级 Beacon？

```bash
pip install --upgrade beacon-cli
```

### Q2: 如何查看版本？

```bash
beacon --version
# 或
beacon-version list
```

### Q3: 如何迁移历史 PTK 数据？

Beacon 保留历史 PTK 目录兼容（仅目录层）。如需迁移：

```bash
# 历史 PTK 数据位于 .ptk/，Beacon 使用 .beacon/
# 两者自动兼容，无需手动迁移
```

### Q4: 如何自定义文档模板？

在项目中创建 `references/` 目录，Beacon 会优先使用项目本地的模板。

### Q5: 如何获取帮助？

```bash
# 查看帮助
beacon --help

# 查看子命令帮助
beacon-workflow --help
beacon-think --help

# 运行环境诊断
beacon-doctor
```

---

## 9. 相关链接

- **文档入口（v1.0.1）**: [docs/beacon/v1.0.1/](./docs/beacon/v1.0.1/)
- **功能与闭环说明**: [Beacon 功能说明与闭环流程](./docs/beacon/v1.0.1/execution/beacon-feature-closure-guide.md)
- **命令-产物-证据速查表**: [beacon-command-artifact-evidence-cheatsheet.md](./docs/beacon/v1.0.1/execution/beacon-command-artifact-evidence-cheatsheet.md)
- **研究方案（MVS）**: [beacon-fidelity-mvp-solution.md](./docs/beacon/v1.0.1/research/beacon-fidelity-mvp-solution.md)
- **反过度设计规范**: [anti-overdesign-min-spec.md](./docs/beacon/v1.0.1/research/anti-overdesign-min-spec.md)
- **生命周期调整**: [workflow-memory-lifecycle-adjustment.md](./docs/beacon/v1.0.1/execution/workflow-memory-lifecycle-adjustment.md)

---

**版本**: v1.0.1
**最后更新**: 2026-03-03
