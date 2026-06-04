# Test Cases: beacon-memory-v1-redesign

## Overview

**Feature**: beacon-memory-v1-redesign  
**Version**: v1.0.3  
**Generated**: 2026-03-05  
**AC Matrix JSON**: `docs/beacon/archive/v1.0.3/qa/test-cases/beacon-memory-v1-redesign.ac-test-matrix.json`

---

## Executable AC→TC Matrix（As Implemented）

| AC ID | TC ID | Layer | Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-001 | unit | `python3 -m pytest -q tests/test_v103_memory_revision_contract.py::test_memory_revision_should_mark_previous_as_superseded` | revision/supersede 字段语义正确 |
| AC-001 | TC-002 | unit | `python3 -m pytest -q tests/test_v103_memory_revision_contract.py::test_memory_upsert_should_dedupe_by_content_hash` | upsert 按 content_hash 去重 |
| AC-002 | TC-003 | unit | `python3 -m pytest -q tests/test_v103_memory_revision_contract.py::test_remember_search_should_support_mode_and_layer` | remember search 支持 mode/layer |
| AC-002 | TC-004 | integration | `python3 -m pytest -q tests/test_v103_memory_revision_contract.py::test_recall_memory_should_support_layer_and_ids` | recall memory 支持 layer/ids |
| AC-003 | TC-005 | integration | `python3 -m pytest -q tests/test_v103_feedback_pipeline_contract.py::test_feedback_extract_should_collect_reason_codes` | extract 产出 reason_code 候选 |
| AC-003 | TC-006 | integration | `python3 -m pytest -q tests/test_v103_feedback_pipeline_contract.py::test_feedback_apply_should_write_feedback_memory_and_report` | apply 写回 memory/report |
| AC-004 | TC-007 | unit | `python3 -m pytest -q tests/test_v103_workflow_attempt_contract.py::test_lifecycle_attempt_metadata_should_increment_and_link_superseded` | lifecycle attempt 元数据完整 |
| AC-004 | TC-008 | integration | `python3 -m pytest -q tests/test_v103_workflow_attempt_contract.py::test_latest_attempt_status_should_win_over_previous_failure` | 失败可恢复，最新 attempt 生效 |
| AC-005 | TC-009 | integration | `python3 -m pytest -q tests/test_v103_workflow_interactive_and_closure.py::test_workflow_auto_skip_should_not_mark_completed_without_closure` | skip 不误报 completed |
| AC-005 | TC-010 | unit | `python3 -m pytest -q tests/test_v103_workflow_attempt_contract.py::test_stage_skipped_should_be_reported_and_gate_stage_should_exist` | gate 入主状态机 + skipped 状态 |
| AC-006 | TC-011 | integration | `python3 -m pytest -q tests/test_v103_workflow_interactive_and_closure.py::test_resume_continue_should_match_workflow_continue_non_interactive` | resume continue 推进执行 |
| AC-006 | TC-012 | integration | `python3 -m pytest -q tests/test_report_memory_metrics.py::test_report_status_resume_should_expose_memory_metrics` | resume 输出 memory_metrics |
| AC-007 | TC-013 | integration | `python3 -m pytest -q tests/test_v103_release_gate_contract.py::test_release_check_should_require_real_artifacts` | release check 读取真实工件 |
| AC-008 | TC-014 | unit | `python3 -m pytest -q tests/test_v103_release_gate_contract.py::test_gate_dry_run_should_never_block_exit_code` | dry-run 非阻断，exit 0 |

---

## Pass / Fail / Blocked

- **Pass**：AC-001~AC-008 全通过
- **Fail**：任一 Must AC 对应 TC 失败
- **Blocked**：缺少关键工件导致 release/gate 无法判定
