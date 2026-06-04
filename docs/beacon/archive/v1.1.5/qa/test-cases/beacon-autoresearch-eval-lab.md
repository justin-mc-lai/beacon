# Test Cases: Beacon autoresearch-inspired Eval Lab

**Feature**: beacon-autoresearch-eval-lab  
**Version**: v1.1.5

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | contract | Fixed benchmark surface defined | 固定 benchmark 面清晰存在 |
| TC-002 | contract | Editable surface is small and explicit | 仅规则层/提示词层/漂移规则层可编辑 |
| TC-003 | contract | Hard gate discard rules defined | verify/gate/report/status 失败即 discard |
| TC-004 | contract | Soft scoring dimensions defined | 有 human load / drift / confidence / repair / complexity 评分 |
| TC-005 | contract | Drift auditor minimum loop defined | requirement->db->api->ui 闭环清晰 |
| TC-006 | contract | Evidence ledger defined | keep/discard 账本路径和字段明确 |
| TC-007 | review | Non-goal excludes full self-modification | 不允许一开始自改整仓 |
| TC-008 | review | Delivery-kernel positioning preserved | 不漂移成 runtime agent lab |
