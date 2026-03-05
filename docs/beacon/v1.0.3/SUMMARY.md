# Beacon v1.0.3 版本摘要

## 版本目标

v1.0.3 聚焦 **工作流闭环热修复（迭代一版）**：

1. 修复 `workflow --auto --skip` 假闭环问题
2. 修复失败阶段不可恢复问题（支持失败后重试成功）
3. 将 `gate` 纳入 workflow 主状态机形成完整闭环
4. 统一 `dry-run` 语义为“不阻断、可演练”
5. 发布核查切换为真实工件校验（非模拟）

## 本版本核心文档

- `version/热修复迭代一版版本.md`
- `research/workflow-closure-hotfix-iteration-1.md`
- `execution/v1.0.3-beacon-memory-v1-redesign.md`
- `execution/v1.0.3-beacon-version-evolution-blueprint.md`
- `execution/v1.0.3-workflow-interactive-hud-design.md`
- `prd/beacon-memory-v1-redesign.md`
- `user-story/beacon-memory-v1-redesign.md`
- `qa/test-cases/beacon-memory-v1-redesign.md`
- `qa/test-cases/beacon-memory-v1-redesign.ac-test-matrix.json`
- `qa/test-cases/workflow-interactive-hud.md`
- `qa/test-cases/workflow-interactive-hud.ac-test-matrix.json`

## 状态

- 交付状态：Implemented（代码+测试已完成）
- 核心验收：
  - Memory v1 已落地：`memory-v1.json` + `status/content_hash/reason_codes/revision_of/superseded_by`
  - remember/recall 已支持 `--mode/--layer/--ids` 分层召回契约
  - feedback 已支持 `extract/apply/sync`，并产出 candidates/apply-report 工件
  - lifecycle 已支持 `attempt_id/attempt_seq/supersedes_event_id`，失败后可恢复
  - workflow 已支持交互式 HUD + next-step 确认（含 `workflow hud`）
  - 主状态机已纳入 `gate`，completed 需满足 `closure_complete && gate_pass`
  - `resume` 已支持 flat + action 契约（`resume <run_id>` / `resume continue <run_id>|--run-id`）
  - `release check` 已切换为真实工件校验（auto-test/gate-report/evidence/coverage）
  - `gate --mode dry-run` 已统一为非阻断语义（exit 0）
- 自动化测试：`python3 -m pytest -q` → **222 passed**（2026-03-05）
- 更新时间：2026-03-05
