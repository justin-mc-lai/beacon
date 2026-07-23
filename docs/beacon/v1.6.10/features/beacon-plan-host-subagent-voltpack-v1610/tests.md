---
slug: beacon-plan-host-subagent-voltpack-v1610
version: v1.6.10
revision_id: R1
materials_status: current
---

# Tests

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-VP-001 | AC-VP-KW-001 | `python3 -c "from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate as e; g=e('实现登录'); assert g['spawn'] is False and g['reason_code']=='subagent_default_off'"` | spawn false |
| TC-VP-002 | AC-VP-KW-002 | `python3 -c "from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate as e; g=e('启用子代理做架构设计与代码审查全面分析'); assert 'pack-review' in g['packs'] and 'architect-reviewer' in g['roles'] and 'code-reviewer' in g['roles']"` | pack-review core |
| TC-VP-003 | AC-VP-KW-003 | `python3 -c "from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate as e; g=e('并行实现多湖'); assert g['host_agents'] is False"` | parallel alone off |
| TC-VP-004 | AC-VP-PK-001 | `python3 -m pytest tests/test_v1610_plan_host_subagent_voltpack.py -q -k plan_review_install` | 10 roles written |
| TC-VP-005 | AC-VP-PK-002 | `python3 -m pytest tests/test_v1610_plan_host_subagent_voltpack.py -q -k hard_constraints` | HARD in files |
| TC-VP-006 | AC-VP-PK-003 | `python3 -m pytest tests/test_v1610_plan_host_subagent_voltpack.py -q -k minimal_pack` | 6 roles |
| TC-VP-007 | AC-VP-GT-001 | `python3 -c "from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate as e, PLAN_REVIEW_CORE_ROLES; g=e('子代理 全面审查'); assert set(PLAN_REVIEW_CORE_ROLES)<=set(g['roles'])"` | core 4 |
| TC-VP-008 | AC-VP-GT-002 | `python3 -c "from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate as e; g=e('不要子代理 但启用子代理'); assert g['spawn'] is False"` | negate wins |
| TC-VP-009 | AC-VP-GT-003 | `python3 -c "from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate as e; g=e('启用子代理'); assert g['packs']==['pack-default']"` | default pack |
| TC-VP-010 | AC-VP-RD-001 | `python3 -m pytest tests/test_v1610_plan_host_subagent_voltpack.py -q -k readiness_flat` | flat skill root |
| TC-VP-011 | AC-VP-BD-001 | `python3 -c "from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate as e; g=e('启用子代理 全面审查'); assert g['cannot_complete_goal'] is True"` | bound |
| TC-VP-012 | AC-VP-BD-002 | `rg -n "第二公共|second public" docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/truth.md` | non-goal entry |
| TC-VP-013 | AC-VP-FB-001 | `python3 -c "from beacon.utils.planner_review_runtime import build_planner_review_runtime_artifact as b; from pathlib import Path; p=b(project_root=Path('.'),feature='x',version='v1.6.10',prompt='t',subagent_runtime_available=False,write=False); assert p['execution_mode']=='single_process_multi_reviewer' and p['fallback_reason']"` | fallback |
| TC-VP-014 | AC-VP-EX-001 | `test -f skills/beacon/examples/subagent-plan-review-architecture-on-30s.md` | example exists |
| TC-VP-015 | AC-VP-DF-001 | `rg -n "全量 VoltAgent|Non-goals" docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/truth.md` | defer dump |
| TC-VP-016 | AC-VP-PK-001 | `python3 -m pytest tests/test_v1610_plan_host_subagent_voltpack.py -q` | suite green |

Primary suite: `tests/test_v1610_plan_host_subagent_voltpack.py`

| TC-VP-017 | AC-VP-CNT-001 | `python3 -c "from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate as e, PLAN_REVIEW_CORE_ROLES; g=e('启用子代理 全面审查'); assert g['spawn_count']==3 and g['roles']==list(PLAN_REVIEW_CORE_ROLES)"` | default 3 |
| TC-VP-018 | AC-VP-CNT-002 | `python3 -c "from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate as e; g=e('启用子代理 全面审查 开5个子代理'); assert g['spawn_count']==5"` | count param |
| TC-VP-019 | AC-VP-CNT-003 | `python3 -c "from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate as e; g=e('启用子代理 全面审查', subagent_count=99); assert g['spawn_count']==10"` | clamp 10 |

