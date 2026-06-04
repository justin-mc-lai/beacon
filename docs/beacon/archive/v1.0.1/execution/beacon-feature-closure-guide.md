# Beacon 功能说明与闭环流程（v1.0.1）

> 目标：让需求→实现→验证→交付全链路不失真，可追溯，可续跑。

## 1. 功能总览

| 模块 | 主要命令 | 作用 | 核心产物 |
|---|---|---|---|
| 需求澄清 | `beacon-think *` | 记录事实/问题/冲突，形成需求输入 | `.beacon/state/think-progress/<version>.json` |
| 用户故事 | `beacon-user-story create` | 产出 Story + AC | `docs/beacon/<version>/user-story/*.md` |
| 需求文档 | `beacon-prd create` | 产出 PRD | `docs/beacon/<version>/prd/*.md` |
| 测试设计 | `beacon-test-case create` | AC→TC 可执行矩阵 | `*.ac-test-matrix.json` |
| 自动测试 | `beacon-auto-test create` | UI/API/Unit/Smoke 真实执行证据 | `.beacon/auto-test-status.json` + evidence |
| 工作流编排 | `beacon-workflow start/continue` | 生命周期执行与续跑 | `.beacon/runs/<run_id>/state.json` |
| 门控校验 | `beacon-gate` / `beacon-workflow gate` | 严格交付判定 | `.beacon/gate-report.json` |
| 状态与报告 | `beacon-status` / `beacon-report` | 输出机器可读+人工可读进度 | `summary.json` / `summary.md` |
| 记忆体 | workflow memory 自动写入 | recall 注入、writeback、闭环统计 | `.beacon/memory/workflow-lifecycle.json` |

---

## 2. 版本规则（已去 latest）

- 默认 `--version auto`：自动扫描 `docs/beacon` + `docs/product`，选择最大语义版本。
- 支持显式版本：`--version vX.Y.Z`。
- 文档输出统一落盘到 `docs/beacon/<version>`（并兼容镜像到 `docs/product/<version>`）。

---

## 3. 闭环流程（MVS）

核心链路：

`Story -> AC -> TC -> Code -> Evidence -> Gate`

### 3.1 生命周期阶段（6 阶段）

`think -> user-story -> prd -> test-case -> implementation -> verify`

每阶段完成判定（必须齐全）：
1. `stage_started`
2. `stage_context_injected`
3. `stage_finished`
4. `memory_writeback`

> 任一缺失 = 非 completed。

### 3.2 续跑机制

- `beacon-workflow continue --version <v>`：只执行 `next_stage`。
- `beacon-workflow continue --version <v> --auto`：从 `next_stage` 一路补齐到 `verify`。
- 支持 `--run-id` 精确恢复。

### 3.3 终态硬条件

- `implementation`：必须有真实 `--implementation-command`。
- `verify`：`.beacon/auto-test-status.json.status` 必须为 `passed`。
- 任一关键条件失败：workflow 直接 `blocked`。

---

## 4. 证据流与交付工件

workflow 终态会自动产出：

- `docs/beacon/<version>/execution/boundaries.md`
- `docs/beacon/<version>/execution/terminal.json`
- `.beacon/gate-report.json`
- `.beacon/raw-command-log.jsonl`
- `.beacon/evidence-manifest.json`

说明：
- 无真实执行证据、evidence 无法校验、或覆盖不足，strict gate 应阻断。

---

## 5. 最小落地推荐操作

```bash
# 1) 自动运行闭环
beacon-workflow start "用户登录" --auto \
  --implementation-command "python3 -m pytest -q tests/test_login.py" \
  --verify-scope all \
  --verify-unit-command "python3 -m pytest -q -k unit" \
  --verify-smoke-command "python3 -m pytest -q -m smoke"

# 2) 查看闭环与覆盖
beacon-status --board --version v1.0.1
beacon-report --machine --version v1.0.1

# 3) gate 判定
beacon-gate check release --mode strict --version v1.0.1
```

---

## 6. 典型阻断原因（用于排查）

- `implementation_command_required`
- `verify_not_passed`
- `ui_real_execution_required`
- `coverage_incomplete`
- `memory_lifecycle_missing`
- `release_memory_profile_invalid`

---

## 7. 关联文档

- 研究方案：`docs/beacon/archive/v1.0.1/research/beacon-fidelity-mvp-solution.md`
- 反过度设计规范：`docs/beacon/archive/v1.0.1/research/anti-overdesign-min-spec.md`
- 生命周期调整：`docs/beacon/archive/v1.0.1/execution/workflow-memory-lifecycle-adjustment.md`
- 命令-产物-证据速查：`docs/beacon/archive/v1.0.1/execution/beacon-command-artifact-evidence-cheatsheet.md`
