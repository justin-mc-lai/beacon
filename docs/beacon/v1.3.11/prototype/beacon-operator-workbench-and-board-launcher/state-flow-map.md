# 状态流冻结图：Beacon Operator Workbench And Board Launcher

| From | To | Event | Guard | Fallback | AC Refs | TC Refs |
|---|---|---|---|---|---|---|
| `recovery-diagnostics:ready` | `recovery-diagnostics:healthy-warning` | enter_healthy_warning | business_condition_detected | recovery-diagnostics:ready | - | - |
| `recovery-diagnostics:ready` | `recovery-diagnostics:degraded` | enter_degraded | business_condition_detected | recovery-diagnostics:ready | - | - |
| `recovery-diagnostics:ready` | `recovery-diagnostics:rebuild-suggested` | enter_rebuild_suggested | business_condition_detected | recovery-diagnostics:ready | - | - |
| `recovery-diagnostics:ready` | `recovery-diagnostics:doctor-suggested` | enter_doctor_suggested | business_condition_detected | recovery-diagnostics:ready | - | - |
| `portfolio-board:loading` | `portfolio-board:ready` | data_loaded | data_fetch_success | - | - | TC-001, TC-002 |
| `portfolio-board:ready` | `portfolio-board:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready | - | TC-001, TC-002 |
| `portfolio-board:ready` | `portfolio-board:blocked` | enter_blocked | business_condition_detected | portfolio-board:ready | - | - |
| `portfolio-board:ready` | `portfolio-board:needs-review` | enter_needs_review | business_condition_detected | portfolio-board:ready | - | - |
| `execution-board:loading` | `execution-board:ready` | data_loaded | data_fetch_success | - | - | TC-001, TC-002 |
| `execution-board:ready` | `execution-board:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready | - | TC-001, TC-002 |
| `execution-board:ready` | `execution-board:blocked` | enter_blocked | business_condition_detected | execution-board:ready | - | - |
| `execution-board:ready` | `execution-board:needs-review` | enter_needs_review | business_condition_detected | execution-board:ready | - | - |
| `execution-board:ready` | `execution-board:retry-scheduled` | enter_retry_scheduled | business_condition_detected | execution-board:ready | - | - |
| `feature-detail:ready` | `feature-detail:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready | - | TC-001, TC-002 |
| `feature-detail:ready` | `feature-detail:blocked` | enter_blocked | business_condition_detected | feature-detail:ready | - | - |
| `feature-detail:ready` | `feature-detail:needs-review` | enter_needs_review | business_condition_detected | feature-detail:ready | - | - |
| `run-detail:ready` | `run-detail:running` | enter_running | business_condition_detected | run-detail:ready | - | - |
| `run-detail:ready` | `run-detail:blocked` | enter_blocked | business_condition_detected | run-detail:ready | - | - |
| `run-detail:ready` | `run-detail:needs-review` | enter_needs_review | business_condition_detected | run-detail:ready | - | - |
| `run-detail:ready` | `run-detail:retry-scheduled` | enter_retry_scheduled | business_condition_detected | run-detail:ready | - | - |
| `review-surface:ready` | `review-surface:error` | data_failure | runtime_or_projection_error | recovery-diagnostics:ready | - | TC-001, TC-002 |
| `review-surface:ready` | `review-surface:needs-evidence` | enter_needs_evidence | business_condition_detected | review-surface:ready | - | - |
| `review-surface:ready` | `review-surface:blocked` | enter_blocked | business_condition_detected | review-surface:ready | - | - |
| `recovery-diagnostics:ready` | `portfolio-board:ready` | 点击跳转 | route_allowed | recovery-diagnostics:ready | AC-001 | TC-001 |
| `portfolio-board:ready` | `execution-board:ready` | 点击跳转 | route_allowed | portfolio-board:ready | AC-001 | TC-001 |
| `execution-board:ready` | `feature-detail:ready` | 点击跳转 | route_allowed | execution-board:ready | AC-001 | TC-001 |
| `feature-detail:ready` | `run-detail:ready` | 点击跳转 | route_allowed | feature-detail:ready | AC-001 | TC-001 |
| `run-detail:ready` | `review-surface:ready` | 点击跳转 | route_allowed | run-detail:ready | AC-001 | TC-001 |

## 说明
- 状态流与导航图共同定义 prototype 冻结语义。
- 每条边都应可追溯到 test-case 场景。
