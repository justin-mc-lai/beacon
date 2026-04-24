# 状态流冻结图：Beacon v1.3.7 implement frozen-truth verification and canonical delivery baseline envelope

| From | To | Event | Guard | Fallback |
|---|---|---|---|---|
| `recovery-diagnostics:ready` | `runtime-center:ready` | 点击运行态关联 | route_allowed | recovery-diagnostics:ready |

## 说明
- 状态流与导航图共同定义 prototype 冻结语义。
- 每条边都应可追溯到 test-case 场景。
