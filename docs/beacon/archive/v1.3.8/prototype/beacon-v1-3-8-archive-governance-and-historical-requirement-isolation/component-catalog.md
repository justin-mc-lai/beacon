# 组件契约清单：Beacon v1.3.8 archive governance and historical requirement isolation

| Component ID | Page | Name | State Refs | AC Refs | TC Refs |
|---|---|---|---|---|---|
| `runtime-center-component-01` | `runtime-center` | 运行态摘要头部 | single-active, team-active, ralph-active, idle, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-02` | `runtime-center` | single / team / ralph 模式切换 | single-active, team-active, ralph-active, idle, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-03` | `runtime-center` | agent/session 引用 | single-active, team-active, ralph-active, idle, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-04` | `runtime-center` | artifact 与 linked run | single-active, team-active, ralph-active, idle, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-05` | `runtime-center` | 最近结果与 blocker | single-active, team-active, ralph-active, idle, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |

## 说明
- 组件契约用于 requirement freeze，不是最终前端组件实现规范。
- 实现阶段需要保持 component -> state -> AC/TC 的可追踪关系。
