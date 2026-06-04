# Beacon 命令-产物-证据路径速查表（v1.0.1）

> 适用版本：v1.0.1（默认建议 `--version auto` 或显式 `--version vX.Y.Z`）

## 1) 核心闭环命令

| 阶段 | 命令示例 | 主要产物 | 核心证据路径 |
|---|---|---|---|
| Think | `beacon-think start "用户登录" --version v1.0.1` | 思考进度文件 | `.beacon/state/think-progress/v1.0.1.json` |
| User Story | `beacon-user-story create "用户登录" --version v1.0.1` | 用户故事文档 | `docs/beacon/archive/v1.0.1/user-story/用户登录.md` |
| PRD | `beacon-prd create "用户登录" --version v1.0.1` | PRD 文档 | `docs/beacon/archive/v1.0.1/prd/用户登录.md` |
| Test Case | `beacon-test-case create "用户登录" --version v1.0.1` | 用例文档 + AC/TC 矩阵 | `docs/beacon/archive/v1.0.1/qa/test-cases/用户登录.md` / `*.ac-test-matrix.json` |
| Implementation | `beacon-workflow start "用户登录" --auto --implementation-command "<real cmd>" --version v1.0.1` | 实施阶段执行记录 | `.beacon/raw-command-log.jsonl` |
| Verify | `beacon-auto-test create all --project . --matrix-path <matrix>` | 自动化测试状态 +分层证据 | `.beacon/auto-test-status.json` / `.beacon/evidence/auto-test/<run_id>/` |
| Gate | `beacon-gate check release --mode strict --version v1.0.1` | Gate 判定结果 | `.beacon/gate-report.json` |
| Report | `beacon-report --machine --version v1.0.1` | 机器可读 + 人读摘要 | `docs/beacon/archive/v1.0.1/execution/summary.json` / `summary.md` |

---

## 2) 工作流编排与续跑

| 场景 | 命令示例 | 关键状态/证据 |
|---|---|---|
| 手动计划（不执行阶段） | `beacon-workflow start "用户登录" --version v1.0.1` | `.beacon/runs/<run_id>/state.json`（`status=planned`） |
| 执行下一阶段 | `beacon-workflow continue --version v1.0.1` | 生命周期中 `next_stage` 被推进 |
| 自动补齐到 verify | `beacon-workflow continue --version v1.0.1 --auto --implementation-command "<real cmd>"` | 6 阶段 closure 完整 |
| 指定 run 恢复 | `beacon-workflow continue --run-id run-xxxx --auto ...` | 对应 run 生命周期闭环 |
| 看进度面板 | `beacon-status --board --version v1.0.1` | `memory.next_stage / closure_complete / coverage.*` |

---

## 3) 生命周期记忆体（必须看）

| 内容 | 路径 |
|---|---|
| 生命周期主文件 | `.beacon/memory/workflow-lifecycle.json` |
| 生命周期去重索引 | `.beacon/memory/workflow-lifecycle.index.json` |
| 生命周期 schema | `.beacon/memory/workflow-lifecycle.schema.json` |
| 阶段 recall 上下文 | `.beacon/state/workflow-memory/<run_id>/<stage>-context.json` |
| insight/decision 写回 | `.beacon/memory/project-insights.json` / `.beacon/memory/decisions.json` |

阶段 `completed` 判定（四件套）：
- `stage_started`
- `stage_context_injected`
- `stage_finished`
- `memory_writeback`

---

## 4) 交付审计工件（release/gate 常看）

| 工件 | 路径 | 用途 |
|---|---|---|
| 边界文档 | `docs/beacon/<version>/execution/boundaries.md` | 范围与约束声明 |
| 终态文档 | `docs/beacon/<version>/execution/terminal.json` | Pass/Blocked/Cancelled 终态 |
| Gate 报告 | `.beacon/gate-report.json` | reason_code 级阻断定位 |
| 原始命令日志 | `.beacon/raw-command-log.jsonl` | 实际执行证明 |
| 证据清单 | `.beacon/evidence-manifest.json` | 证据完整性/sha256 |

---

## 5) 快速排查（失败时）

| 现象 | 优先检查 |
|---|---|
| workflow 被阻断在 implementation | 是否传了 `--implementation-command`；查看 `.beacon/raw-command-log.jsonl` |
| verify 不通过 | `.beacon/auto-test-status.json.status` 是否为 `passed` |
| gate strict 不通过 | `.beacon/gate-report.json.issues[].reason_code` |
| 覆盖率不足 | `beacon-status --board --version <v>` 中 `coverage.story/ac/tc` |
| 续跑错阶段 | `.beacon/memory/workflow-lifecycle.json` + `beacon-workflow status --version <v>` |

---

## 6) 一条最小可交付命令（参考）

```bash
beacon-workflow start "用户登录" --auto --version v1.0.1 \
  --implementation-command "python3 -m pytest -q tests/test_login.py" \
  --verify-scope all \
  --verify-ui-command "python3 -m pytest -q -k ui" \
  --verify-api-curl-command "bash -lc 'curl -fsS http://127.0.0.1:8000/health'" \
  --verify-unit-command "python3 -m pytest -q -k unit" \
  --verify-smoke-command "python3 -m pytest -q -m smoke"
```

执行后按顺序核对：
1. `beacon-status --board --version v1.0.1`
2. `beacon-report --machine --version v1.0.1`
3. `beacon-gate check release --mode strict --version v1.0.1`
