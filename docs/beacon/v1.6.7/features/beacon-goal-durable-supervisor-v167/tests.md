---
slug: beacon-goal-durable-supervisor-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Goal Durable Supervisor v1.6.7

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-DGS-001 | TC-DGS-001 | contract | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_supervise_is_opt_in -q` | goal run 不自动 attach supervise |
| AC-DGS-002 | TC-DGS-002 | contract | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_heartbeat_default_120s -q` | 默认 interval=120 |
| AC-DGS-003 | TC-DGS-003 | unit | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_execution_jsonl_append -q` | heartbeat/tick append JSONL |
| AC-DGS-004 | TC-DGS-004 | unit | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_checkpoint_and_resume_pack -q` | checkpoint + resume-pack digest only |
| AC-DGS-005 | TC-DGS-005 | unit | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_stall_detects_idle -q` | idle≥interval → host_interrupted/stall |
| AC-DGS-006 | TC-DGS-006 | contract | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_interrupt_ne_stage_blocked -q` | 两类 reason 可区分 |
| AC-DGS-007 | TC-DGS-007 | unit | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_tick_execute_dispatches -q` | --execute 可派发；无 flag 不派发 |
| AC-DGS-008 | TC-DGS-008 | contract | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_no_complete_without_verifier -q` | 无 refs 不可 complete |
| AC-DGS-009 | TC-DGS-009 | contract | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_supervise_never_auto_release -q` | 不自动 release |
| AC-DGS-010 | TC-DGS-010 | contract | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_no_second_public_entry -q` | 文档/示例无第二入口 |
| AC-DGS-011 | TC-DGS-011 | unit | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_log_append_only -q` | 禁止覆写 JSONL |
| AC-DGS-012 | TC-DGS-012 | unit | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_sqlite_fts_non_authoritative -q` | FTS 结果不触发 complete |
| AC-DGS-013 | TC-DGS-013 | contract | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_skill_mentions_resume_pack -q` | SKILL 含 resume-pack/supervise |
| AC-DGS-014 | TC-DGS-014 | contract | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_tests_md_has_legal_and_illegal -q` | tests 含 legal/illegal 行 |

## Legal walk coverage

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-DGS-001 | TC-DGS-LEGAL-01 | legal walk | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_legal_walk_create_to_complete -q` | created→…→completed with verifier |
| AC-DGS-006 | TC-DGS-LEGAL-02 | legal walk | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_legal_walk_host_interrupt_resume -q` | host_interrupted→resume last_substep |
| AC-DGS-001 | TC-DGS-LEGAL-03 | legal walk | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_legal_walk_opt_in_supervise -q` | supervise attach→poll→detach |

## Illegal transition coverage

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-DGS-008 | TC-DGS-ILLEGAL-01 | illegal | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_illegal_interrupt_to_complete -q` | host_interrupted 不能直 complete |
| AC-DGS-001 | TC-DGS-ILLEGAL-02 | illegal | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_illegal_auto_supervise_on_run -q` | goal run 不 auto supervise |
| AC-DGS-011 | TC-DGS-ILLEGAL-03 | illegal | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_illegal_overwrite_jsonl -q` | 禁止覆写日志 |
| AC-DGS-012 | TC-DGS-ILLEGAL-04 | illegal | `python3 -m pytest tests/test_v167_goal_durable_supervisor.py::test_illegal_memory_overrides_verifier -q` | FTS 不能当 verifier |

## Evidence Path

`.beacon/evidence/test-results/beacon-goal-durable-supervisor-v167/`
