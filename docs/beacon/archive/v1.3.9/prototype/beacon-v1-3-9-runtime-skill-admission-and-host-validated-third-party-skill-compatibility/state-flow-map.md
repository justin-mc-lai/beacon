# 状态流冻结图：Beacon v1.3.9 runtime skill admission and host-validated third-party skill compatibility

| From | To | Event | Guard | Fallback |
|---|---|---|---|---|
| `v1-3-9:loading` | `v1-3-9:ready` | data_loaded | data_fetch_success | - |
| `v1-3-9:ready` | `v1-3-9:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready |

## 说明
- 状态流与导航图共同定义 prototype 冻结语义。
- 每条边都应可追溯到 test-case 场景。
