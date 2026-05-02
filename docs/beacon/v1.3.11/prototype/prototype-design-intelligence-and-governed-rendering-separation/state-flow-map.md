# 状态流冻结图：Prototype Design Intelligence And Governed Rendering Separation

| From | To | Event | Guard | Fallback | AC Refs | TC Refs |
|---|---|---|---|---|---|---|
| `home:loading` | `home:ready` | data_loaded | data_fetch_success | - | - | TC-001, TC-002 |
| `home:ready` | `home:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready | - | TC-001, TC-002 |
| `home:ready` | `home:blocked` | enter_blocked | business_condition_detected | home:ready | - | - |
| `home:ready` | `home:intervention-needed` | enter_intervention_needed | business_condition_detected | home:ready | - | - |
| `home:ready` | `home:empty` | enter_empty | business_condition_detected | home:ready | - | - |
| `management-overview:loading` | `management-overview:ready` | data_loaded | data_fetch_success | - | - | TC-001, TC-002 |
| `management-overview:ready` | `management-overview:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready | - | TC-001, TC-002 |
| `management-overview:ready` | `management-overview:filtered` | enter_filtered | business_condition_detected | management-overview:ready | - | - |
| `management-overview:ready` | `management-overview:empty` | enter_empty | business_condition_detected | management-overview:ready | - | - |
| `project-detail:loading` | `project-detail:ready` | data_loaded | data_fetch_success | - | - | TC-001, TC-002 |
| `project-detail:ready` | `project-detail:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready | - | TC-001, TC-002 |
| `project-detail:ready` | `project-detail:requirement-missing` | enter_requirement_missing | business_condition_detected | project-detail:ready | - | - |
| `project-detail:ready` | `project-detail:draft` | enter_draft | business_condition_detected | project-detail:ready | - | - |
| `project-detail:ready` | `project-detail:frozen` | enter_frozen | business_condition_detected | project-detail:ready | - | - |
| `project-detail:ready` | `project-detail:runtime-active` | enter_runtime_active | business_condition_detected | project-detail:ready | - | - |
| `runtime-center:ready` | `runtime-center:single-active` | enter_single_active | business_condition_detected | runtime-center:ready | - | - |
| `runtime-center:ready` | `runtime-center:team-active` | enter_team_active | business_condition_detected | runtime-center:ready | - | - |
| `runtime-center:ready` | `runtime-center:ralph-active` | enter_ralph_active | business_condition_detected | runtime-center:ready | - | - |
| `runtime-center:ready` | `runtime-center:idle` | enter_idle | business_condition_detected | runtime-center:ready | - | - |
| `recovery-diagnostics:ready` | `recovery-diagnostics:healthy-warning` | enter_healthy_warning | business_condition_detected | recovery-diagnostics:ready | - | - |
| `recovery-diagnostics:ready` | `recovery-diagnostics:degraded` | enter_degraded | business_condition_detected | recovery-diagnostics:ready | - | - |
| `recovery-diagnostics:ready` | `recovery-diagnostics:rebuild-suggested` | enter_rebuild_suggested | business_condition_detected | recovery-diagnostics:ready | - | - |
| `recovery-diagnostics:ready` | `recovery-diagnostics:doctor-suggested` | enter_doctor_suggested | business_condition_detected | recovery-diagnostics:ready | - | - |
| `material-viewer:loading` | `material-viewer:ready` | data_loaded | data_fetch_success | - | - | TC-001, TC-002 |
| `material-viewer:ready` | `material-viewer:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready | - | TC-001, TC-002 |
| `material-viewer:ready` | `material-viewer:document-open` | enter_document_open | business_condition_detected | material-viewer:ready | - | - |
| `material-viewer:ready` | `material-viewer:source-missing` | enter_source_missing | business_condition_detected | material-viewer:ready | - | - |
| `material-viewer:ready` | `material-viewer:empty` | enter_empty | business_condition_detected | material-viewer:ready | - | - |
| `material-document-detail:ready` | `material-document-detail:sibling-switch` | enter_sibling_switch | business_condition_detected | material-document-detail:ready | - | - |
| `material-document-detail:ready` | `material-document-detail:version-switch` | enter_version_switch | business_condition_detected | material-document-detail:ready | - | - |
| `material-document-detail:ready` | `material-document-detail:source-missing` | enter_source_missing | business_condition_detected | material-document-detail:ready | - | - |
| `home:ready` | `management-overview:ready` | 点击项目组合入口 | route_allowed | home:ready | AC-001 | TC-001 |
| `home:ready` | `project-detail:ready` | 点击重点项目卡片 | route_allowed | home:ready | AC-001 | TC-001 |
| `management-overview:ready` | `project-detail:ready` | 点击项目行/卡片 | route_allowed | management-overview:ready | AC-001 | TC-001 |
| `management-overview:ready` | `home:ready` | 点击首页导航 | route_allowed | management-overview:ready | AC-001 | TC-001 |
| `project-detail:ready` | `runtime-center:ready` | 点击运行态摘要 | route_allowed | project-detail:ready | AC-001 | TC-001 |
| `project-detail:ready` | `recovery-diagnostics:ready` | 点击恢复诊断入口 | route_allowed | project-detail:ready | AC-001 | TC-001 |
| `project-detail:ready` | `material-viewer:ready` | 点击文档查看入口 | route_allowed | project-detail:ready | AC-001 | TC-001 |
| `project-detail:ready` | `management-overview:ready` | 点击返回 | route_allowed | project-detail:ready | AC-001 | TC-001 |
| `runtime-center:ready` | `project-detail:ready` | 点击返回 | route_allowed | runtime-center:ready | AC-001 | TC-001 |
| `runtime-center:ready` | `management-overview:ready` | 点击面包屑 | route_allowed | runtime-center:ready | AC-001 | TC-001 |
| `recovery-diagnostics:ready` | `project-detail:ready` | 点击返回 | route_allowed | recovery-diagnostics:ready | AC-001 | TC-001 |
| `recovery-diagnostics:ready` | `runtime-center:ready` | 点击运行态关联 | route_allowed | recovery-diagnostics:ready | AC-001 | TC-001 |
| `material-viewer:ready` | `project-detail:ready` | 点击返回 | route_allowed | material-viewer:ready | AC-001 | TC-001 |
| `material-viewer:ready` | `material-document-detail:ready` | 点击文档列表项 | route_allowed | material-viewer:ready | AC-001 | TC-001 |
| `material-document-detail:ready` | `material-viewer:ready` | 点击返回 | route_allowed | material-document-detail:ready | AC-001 | TC-001 |

## 说明
- 状态流与导航图共同定义 prototype 冻结语义。
- 每条边都应可追溯到 test-case 场景。
