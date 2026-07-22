---
slug: trace-lifecycle-binding-v1610
version: v1.6.10
revision_id: R1
materials_status: current
---

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-TRC-001 | AC-TRC-001 | `rg -n "record_lifecycle_stage_trace" beacon/utils/agent_trace.py` | 存在 helper |
| TC-TRC-002 | AC-TRC-002 | `rg -n "record_lifecycle_stage_trace" beacon/commands/truth.py` | truth review 挂钩 |
| TC-TRC-003 | AC-TRC-003 | `rg -n "record_lifecycle_stage_trace" beacon/commands/freeze.py` | freeze 挂钩 |
| TC-TRC-004 | AC-TRC-004 | `rg -n "feature_slug|harness" beacon/utils/agent_trace.py` | 绑定字段 |
| TC-TRC-005 | AC-TRC-005 | `rg -n "record_driver_turn_trace" beacon/utils/goal_agent_driver.py` | driver 调用 |
| TC-TRC-006 | AC-TRC-005 | `rg -n "except Exception" beacon/utils/goal_agent_driver.py -A3 \| rg -n "pass|driver_trace"` | 非静默 pass-only |
| TC-TRC-007 | AC-TRC-006 | `rg -n "full_chat|assert_no_full_chat" beacon/utils/loom_trace.py` | 禁全文权威 |
| TC-TRC-008 | AC-TRC-007 | `rg -n "record_lifecycle_stage_trace" beacon/commands/qa.py` | qa 挂钩 |
| TC-TRC-009 | AC-TRC-008 | `python -m pytest tests/test_v1610_trace_lifecycle_binding.py -q` | 覆盖信号 |
| TC-TRC-010 | AC-TRC-009 | `rg -n "Intent Coverage Matrix|FSM 五元组|人话" docs/beacon/v1.6.10/features/trace-lifecycle-binding-v1610/truth.md` | 金样 shape |
| TC-TRC-011 | AC-TRC-010 | `rg -c "TC-TRC-" docs/beacon/v1.6.10/features/trace-lifecycle-binding-v1610/tests.md` | TC≥10 |
| TC-TRC-012 | AC-TRC-001 | `python -c "from beacon.utils.agent_trace import record_lifecycle_stage_trace"` | import ok |
99:| AC-TRC-006 | payload/汇总禁止 `full_chat` 作为权威；aggregate 继续 strip full_chat |
126:## Illegal transitions
129:- append_failed → silent success (no reason_code)
130:- event with full_chat body as sole evidence | illegal transitions covered |
| TC-TRC-013 | AC-TRC-006 | 126:## Illegal transitions | illegal transitions section present |
| TC-TRC-014 | AC-TRC-004 | 129:- append_failed → silent success (no reason_code) | illegal silent-success forbidden |
