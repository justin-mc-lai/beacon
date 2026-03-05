# Beacon v1.0.3 热修复迭代一版调研结论

Date: 2026-03-05

## 0) 总结结论

- v1.0.2 功能完成度：约 **80%**（可用）
- 闭环程度：约 **62/100**（存在关键断点）
- 工程健康度：较好（`python3 -m pytest -q` = **198 passed**）

## 1) 已完成（核心能力）

1. 命令体系完整：`beacon` + `beacon-*` 前缀命令齐全（`beacon/main.py`, `beacon/prefixed.py`）。
2. QA9 主链已打通：`think -> test-case(.qa9-matrix) -> auto-test -> gate`（`beacon/commands/think.py`, `test_case.py`, `auto_test.py`, `gate.py`）。
3. verify 有硬条件：`auto-test-status.json.status` 必须为 `passed`（`beacon/commands/workflow.py:575-597`）。
4. 命令同步机制可用：`scripts/sync_skill_commands.py --check` 通过。
5. v1.0.2 契约/回归测试覆盖较全（`tests/test_v102_*`, `tests/test_qa9_v102_contract.py` 等）。

## 2) 闭环关键问题（高优先级）

1. `--auto --skip` 可跳过阶段后仍写 `completed`（假闭环风险）
   - 证据：`workflow.py:739-742, 793-810`
2. 阶段失败后难恢复（`stage_failed` 优先，重跑可能仍判失败）
   - 证据：`workflow_memory.py:434-437`；事件去重：`workflow_memory.py:153-164`
3. workflow 主状态机不含 gate（只到 verify）
   - 证据：`workflow.py:32-39`; `workflow_memory.py:20`; `gate.py:95`
4. `resume` 仅查看，不推进执行
   - 证据：`resume.py:22-31`
5. `gate --mode dry-run` 仍可能 Blocked + exit 2
   - 证据：`gate.py:1640-1643, 1695-1723, 1792`

## 3) 迭代建议

### P0（立即处理）

1. `workflow start --auto` 完成前强制 `compute_workflow_progress().closure_complete` 校验。
2. 调整失败可恢复语义：允许后续成功覆盖失败，同时保留重试轨迹。
3. 将 `gate` 纳入 workflow 主状态机（升级为 7 阶段闭环）。
4. `release check` 从“模拟检查”切换为读取真实工件（`auto-test-status` / `gate-report` / `coverage`）。

### P1（下一迭代）

1. 统一 `reason_code` 注册源（当前 gate 62 个，`reason_fix_helper` 仅 22 个）。
2. `status/report` 增加运营视角：Top reason_code、事件完整性、失败趋势。
3. 统一 dry-run 语义为“不阻断 + exit 0”。

### P2（中期）

1. 接入 `pytest-cov` 与覆盖率门槛。
2. 增强外部契约测试（OpenAPI / Pact / CDC）。
3. 清理文档与入口口径偏差（README“仅 beacon” vs `pyproject.toml` 仍有 ptk）。

## 4) 额外发现（半成品信号）

1. `docs/beacon/v1.0.2/SUMMARY.md` 仍为 Draft。
2. `qa9.py` 引用 `scripts/midscene-*.mjs`，仓库中缺失对应脚本。
3. `beacon/__init__.py` 注册命令少于 `beacon/main.py`，存在维护一致性风险。

## 5) v1.0.3 建议验收标准（Hotfix Done）

- `workflow start --auto` 在跳过阶段场景不再误报 completed。
- 失败阶段可通过重跑恢复，生命周期正确记录“失败→重试→成功”。
- workflow 生命周期包含 `gate`，最终闭环状态可追溯。
- `gate --mode dry-run` 不阻断主流程且退出码为 0。
- 发布检查读取真实工件并输出可审计证据。
