# Test Cases: workflow-interactive-hud

## Overview

**Feature**: workflow-interactive-hud  
**Version**: v1.0.3  
**Generated**: 2026-03-05  
**AC Matrix JSON**: `docs/beacon/archive/v1.0.3/qa/test-cases/workflow-interactive-hud.ac-test-matrix.json`

---

## Executable AC→TC Matrix（As Implemented）

| AC ID | TC ID | Layer | Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-001 | integration | `python3 -m pytest -q tests/test_v103_workflow_hud_contract.py::test_start_interactive_should_render_hud_before_prompt` | start interactive 先 HUD 后 prompt |
| AC-001 | TC-002 | integration | `python3 -m pytest -q tests/test_v103_workflow_hud_contract.py::test_continue_interactive_should_render_hud_before_prompt` | continue interactive 先 HUD 后 prompt |
| AC-002 | TC-003 | integration | `python3 -m pytest -q tests/test_v103_workflow_interactive_and_closure.py::test_workflow_hud_command_should_emit_required_sections_and_snapshot` | HUD 字段完整并落盘 snapshot |
| AC-003 | TC-004 | unit | `python3 -m pytest -q tests/test_v103_workflow_interactive_timeout_contract.py::test_interactive_menu_should_list_six_actions` | next-step 菜单 1~6 完整 |
| AC-004 | TC-005 | integration | `python3 -m pytest -q tests/test_v103_workflow_interactive_and_closure.py::test_interactive_reject_then_pause_should_record_lifecycle` | 执行类动作拒绝后不推进 |
| AC-005 | TC-006 | integration | `python3 -m pytest -q tests/test_v103_workflow_hud_contract.py::test_no_interactive_should_not_prompt_next_step_menu` | no-interactive 无阻塞 prompt |
| AC-006 | TC-007 | integration | `python3 -m pytest -q tests/test_v103_workflow_interactive_and_closure.py::test_interactive_reject_then_pause_should_record_lifecycle` | 交互决策写 lifecycle |
| AC-006 | TC-008 | integration | `python3 -m pytest -q tests/test_v103_workflow_hud_contract.py::test_interactive_decision_should_write_memory_entry` | 交互决策写 memory decision |
| AC-007 | TC-009 | integration | `python3 -m pytest -q tests/test_v103_workflow_hud_contract.py::test_feedback_apply_action_should_record_event_and_return_hud` | feedback apply 后返回 HUD loop |
| AC-008 | TC-010 | integration | `python3 -m pytest -q tests/test_v103_workflow_interactive_and_closure.py::test_resume_continue_should_match_workflow_continue_non_interactive` | resume continue 与 workflow continue 一致 |
| AC-009 | TC-011 | unit | `python3 -m pytest -q tests/test_v103_workflow_interactive_timeout_contract.py::test_timeout_should_default_to_pause_and_record_event` | 超时默认 pause 并写事件 |
| AC-009 | TC-012 | unit | `python3 -m pytest -q tests/test_v103_workflow_interactive_timeout_contract.py::test_timeout_continue_should_resolve_single_step` | on-timeout=continue 生效 |
| AC-010 | TC-013 | integration | `python3 -m pytest -q tests/test_v103_workflow_interactive_and_closure.py::test_workflow_auto_skip_should_not_mark_completed_without_closure` | 未闭环不得 completed |
| AC-010 | TC-014 | integration | `python3 -m pytest -q tests/test_workflow_continue_progress.py::test_workflow_continue_auto_should_close_remaining_stages` | 闭环完成后可进入 complete 路径 |

---

## Pass / Fail / Blocked

- **Pass**：AC-001~AC-010 全通过
- **Fail**：任一 Must AC 对应 TC 失败
- **Blocked**：交互工件缺失或生命周期状态不一致导致无法判定
