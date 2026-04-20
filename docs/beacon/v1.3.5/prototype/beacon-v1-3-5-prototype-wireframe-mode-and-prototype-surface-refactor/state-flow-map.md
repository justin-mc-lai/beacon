# 状态流冻结图：beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor

| From | To | Event | Guard | Fallback |
|---|---|---|---|---|
| `management-overview:loading` | `management-overview:ready` | data_loaded | data_fetch_success | - |
| `management-overview:ready` | `management-overview:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `material-viewer:loading` | `material-viewer:ready` | data_loaded | data_fetch_success | - |
| `material-viewer:ready` | `material-viewer:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `material-viewer:ready` | `material-document-detail:ready` | 点击文档列表项 | route_allowed | material-viewer:ready |
| `material-document-detail:ready` | `material-viewer:ready` | 点击返回 | route_allowed | material-document-detail:ready |

## 说明
- 状态流与导航图共同定义 prototype 冻结语义。
- 每条边都应可追溯到 test-case 场景。
