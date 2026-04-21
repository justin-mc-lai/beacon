# 状态流冻结图：beacon-v1.3.6-visual-management-console-and-material-viewer

| From | To | Event | Guard | Fallback |
|---|---|---|---|---|
| `home:loading` | `home:ready` | data_loaded | data_fetch_success | - |
| `home:ready` | `home:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `management-overview:loading` | `management-overview:ready` | data_loaded | data_fetch_success | - |
| `management-overview:ready` | `management-overview:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `project-detail:loading` | `project-detail:ready` | data_loaded | data_fetch_success | - |
| `project-detail:ready` | `project-detail:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `material-viewer:loading` | `material-viewer:ready` | data_loaded | data_fetch_success | - |
| `material-viewer:ready` | `material-viewer:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `home:ready` | `management-overview:ready` | 点击项目组合入口 | route_allowed | home:ready |
| `home:ready` | `project-detail:ready` | 点击重点项目卡片 | route_allowed | home:ready |
| `management-overview:ready` | `project-detail:ready` | 点击项目行/卡片 | route_allowed | management-overview:ready |
| `management-overview:ready` | `home:ready` | 点击首页导航 | route_allowed | management-overview:ready |
| `project-detail:ready` | `runtime-center:ready` | 点击运行态摘要 | route_allowed | project-detail:ready |
| `project-detail:ready` | `recovery-diagnostics:ready` | 点击恢复诊断入口 | route_allowed | project-detail:ready |
| `project-detail:ready` | `material-viewer:ready` | 点击文档查看入口 | route_allowed | project-detail:ready |
| `project-detail:ready` | `management-overview:ready` | 点击返回 | route_allowed | project-detail:ready |
| `runtime-center:ready` | `project-detail:ready` | 点击返回 | route_allowed | runtime-center:ready |
| `runtime-center:ready` | `management-overview:ready` | 点击面包屑 | route_allowed | runtime-center:ready |
| `recovery-diagnostics:ready` | `project-detail:ready` | 点击返回 | route_allowed | recovery-diagnostics:ready |
| `recovery-diagnostics:ready` | `runtime-center:ready` | 点击运行态关联 | route_allowed | recovery-diagnostics:ready |
| `material-viewer:ready` | `project-detail:ready` | 点击返回 | route_allowed | material-viewer:ready |
| `material-viewer:ready` | `material-document-detail:ready` | 点击文档列表项 | route_allowed | material-viewer:ready |
| `material-document-detail:ready` | `material-viewer:ready` | 点击返回 | route_allowed | material-document-detail:ready |

## 说明
- 状态流与导航图共同定义 prototype 冻结语义。
- 每条边都应可追溯到 test-case 场景。
