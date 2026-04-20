# 状态流冻结图：beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor

| From | To | Event | Guard | Fallback |
|---|---|---|---|---|
| `management-overview:loading` | `management-overview:ready` | data_loaded | data_fetch_success | - |
| `management-overview:ready` | `management-overview:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `material-viewer:loading` | `material-viewer:ready` | data_loaded | data_fetch_success | - |
| `material-viewer:ready` | `material-viewer:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `page-01-d1bbcc5c:loading` | `page-01-d1bbcc5c:ready` | data_loaded | data_fetch_success | - |
| `page-01-d1bbcc5c:ready` | `page-01-d1bbcc5c:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `beacon-ui:loading` | `beacon-ui:ready` | data_loaded | data_fetch_success | - |
| `beacon-ui:ready` | `beacon-ui:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `page-03-93da1608:loading` | `page-03-93da1608:ready` | data_loaded | data_fetch_success | - |
| `page-03-93da1608:ready` | `page-03-93da1608:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `page-04-56a5749b:loading` | `page-04-56a5749b:ready` | data_loaded | data_fetch_success | - |
| `page-04-56a5749b:ready` | `page-04-56a5749b:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `demo:loading` | `demo:ready` | data_loaded | data_fetch_success | - |
| `demo:ready` | `demo:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `human:loading` | `human:ready` | data_loaded | data_fetch_success | - |
| `human:ready` | `human:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `page-07-d4c36c95:loading` | `page-07-d4c36c95:ready` | data_loaded | data_fetch_success | - |
| `page-07-d4c36c95:ready` | `page-07-d4c36c95:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `page-08-4a2d79ff:loading` | `page-08-4a2d79ff:ready` | data_loaded | data_fetch_success | - |
| `page-08-4a2d79ff:ready` | `page-08-4a2d79ff:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `page-09-ece61c61:loading` | `page-09-ece61c61:ready` | data_loaded | data_fetch_success | - |
| `page-09-ece61c61:ready` | `page-09-ece61c61:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `page-10-107f06b4:loading` | `page-10-107f06b4:ready` | data_loaded | data_fetch_success | - |
| `page-10-107f06b4:ready` | `page-10-107f06b4:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `prd:loading` | `prd:ready` | data_loaded | data_fetch_success | - |
| `prd:ready` | `prd:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `user-story:loading` | `user-story:ready` | data_loaded | data_fetch_success | - |
| `user-story:ready` | `user-story:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `page-13-1c4ec680:loading` | `page-13-1c4ec680:ready` | data_loaded | data_fetch_success | - |
| `page-13-1c4ec680:ready` | `page-13-1c4ec680:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `page-specs-json:loading` | `page-specs-json:ready` | data_loaded | data_fetch_success | - |
| `page-specs-json:ready` | `page-specs-json:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `contract:loading` | `contract:ready` | data_loaded | data_fetch_success | - |
| `contract:ready` | `contract:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `page-spec:loading` | `page-spec:ready` | data_loaded | data_fetch_success | - |
| `page-spec:ready` | `page-spec:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `page-17-860d61fc:loading` | `page-17-860d61fc:ready` | data_loaded | data_fetch_success | - |
| `page-17-860d61fc:ready` | `page-17-860d61fc:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |
| `prd:ready` | `user-story:ready` | 点击跳转 | route_allowed | prd:ready |
| `page-03-93da1608:ready` | `prd:ready` | 点击跳转 | route_allowed | page-03-93da1608:ready |
| `material-viewer:ready` | `material-document-detail:ready` | 点击文档列表项 | route_allowed | material-viewer:ready |
| `material-document-detail:ready` | `material-viewer:ready` | 点击返回 | route_allowed | material-document-detail:ready |

## 说明
- 状态流与导航图共同定义 prototype 冻结语义。
- 每条边都应可追溯到 test-case 场景。
