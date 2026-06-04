# Test Cases: beacon-v1.3.3-minimal-hud-scenarios-and-implementation

## Overview

**Feature**: beacon-v1.3.3-minimal-hud-scenarios-and-implementation  
**Test Type**: ALL  
**Version**: v1.3.3  
**Generated**: 2026-04-17 11:53  
**Memory Context**: codex fixed hud hook alignment  
**AC Matrix JSON**: docs/beacon/archive/v1.3.3/.machine/qa/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.ac-test-matrix.json  
**QA9 Matrix JSON**: docs/beacon/archive/v1.3.3/.machine/qa/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.qa9-matrix.json  
**Story Scenario Map JSON**: docs/beacon/archive/v1.3.3/.machine/qa/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.story-scenario-map.json

---

## Scenario Test Set

### TC-001 (AC-001): `help/status` 覆盖 S1-S6 场景

- Given：构造 S1-S6 输入状态
- When：调用 `minimal_hud` 渲染并经 `help/status` 输出
- Then：六类场景均命中预期分支，且文案稳定

### TC-002 (AC-002): HUD 行数预算受控

- Given：正常场景与 warn/blocked 场景
- When：渲染 HUD
- Then：常态 <=2 行；仅 warn/blocked 为 3 行

### TC-003 (AC-003): 最小决策字段完整

- Given：stage + execution + blocker + next_action 输入
- When：生成 HUD payload 与文本
- Then：必须能稳定读出当前阶段、进度摘要、下一步命令与阻断推荐命令

### TC-004 (AC-004): Ralph 可观测字段稳定

- Given：ralph round/stop/blocker/streak 数据
- When：调用 `help/status --json`
- Then：`phase/round_count/stop_state/next_action/current_blocker/failure_streak/no_delta_streak` 均可读

### TC-005 (AC-005): Team 可观测字段稳定

- Given：team 执行汇总与角色输出
- When：读取 team HUD JSON/HTML + `status --json`
- Then：`team_state/terminal_status/review_gates/fix_loops/roles[*]` 摘要存在且结构稳定

### TC-006 (AC-006): 命令面不扩张且 JSON 兼容

- Given：v1.3.3 HUD 增强后 CLI
- When：检查公开一级命令与 `help/status --json` 字段
- Then：无新增公开一级命令；JSON 仅增不删

### TC-007 (AC-007): compatibility 阻断统一推荐 doctor

- Given：compatibility 阻断场景
- When：输出 `next_step` 与 HUD 第三行
- Then：推荐命令统一指向 `beacon doctor migrate-compat ...`

### TC-008 (AC-008): UserPromptSubmit 固定 HUD 注入

- Given：Codex `UserPromptSubmit` hook payload
- When：执行 Beacon hook 适配
- Then：`hookSpecificOutput.additionalContext` 返回 `[beacon-hud]` 前缀 + 1-3 行 HUD

### TC-009 (AC-009): 会话刷新固定 HUD 注入

- Given：`SessionStart/SessionResume/SessionRefresh` 任一事件 payload
- When：执行 Beacon hook 适配
- Then：返回固定 HUD 文本并与 `minimal_hud` 输出同源

### TC-010 (AC-010): Hook 异常降级不阻断

- Given：hook 输入异常或状态读取失败
- When：执行 hook
- Then：输入提交流程不被阻断；降级为空 HUD；写入 debug 证据事件；`doctor verify-codex-hud-hook` 在未捕获运行态激活证据前返回 warning，捕获 doctor-managed dispatch 证据后返回 pass

---

## Suggested Commands

- `python3 -m pytest -q tests/utils/test_minimal_hud.py`
- `python3 -m pytest -q tests/test_v121_codex_user_prompt_submit.py`
- `python3 -m beacon.main help --project-root . --feature "beacon-v1.3.3-minimal-hud-scenarios-and-implementation" --json`
- `python3 -m beacon.main status --board --project-root .`

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | from AC-001 |
| TC-002 | Pending | from AC-002 |
| TC-003 | Pending | from AC-003 |
| TC-004 | Pending | from AC-004 |
| TC-005 | Pending | from AC-005 |
| TC-006 | Pending | from AC-006 |
| TC-007 | Pending | from AC-007 |
| TC-008 | Pending | from AC-008 |
| TC-009 | Pending | from AC-009 |
| TC-010 | Pending | from AC-010 |
