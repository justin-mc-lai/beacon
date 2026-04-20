# 组件契约清单：beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor

| Component ID | Page | Name | State Refs | AC Refs | TC Refs |
|---|---|---|---|---|---|
| `management-overview-component-01` | `management-overview` | 筛选与排序条 | ready, filtered, empty, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `management-overview-component-02` | `management-overview` | 项目注册表 | ready, filtered, empty, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `management-overview-component-03` | `management-overview` | 阶段分布摘要 | ready, filtered, empty, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `management-overview-component-04` | `management-overview` | 风险与调试摘要 | ready, filtered, empty, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `management-overview-component-05` | `management-overview` | 推荐 skill 区 | ready, filtered, empty, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-01` | `runtime-center` | 运行态摘要头部 | single-active, team-active, ralph-active, idle, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-02` | `runtime-center` | single / team / ralph 模式切换 | single-active, team-active, ralph-active, idle, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-03` | `runtime-center` | agent/session 引用 | single-active, team-active, ralph-active, idle, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-04` | `runtime-center` | artifact 与 linked run | single-active, team-active, ralph-active, idle, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-05` | `runtime-center` | 最近结果与 blocker | single-active, team-active, ralph-active, idle, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-viewer-component-01` | `material-viewer` | 版本树 | ready, document-open, source-missing, loading, empty, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-viewer-component-02` | `material-viewer` | 文档类型列表 | ready, document-open, source-missing, loading, empty, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-viewer-component-03` | `material-viewer` | feature 目录 | ready, document-open, source-missing, loading, empty, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-viewer-component-04` | `material-viewer` | 文档阅读面板 | ready, document-open, source-missing, loading, empty, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-viewer-component-05` | `material-viewer` | 来源路径信息 | ready, document-open, source-missing, loading, empty, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-01` | `material-document-detail` | 文档头部信息 | ready, sibling-switch, version-switch, source-missing | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-02` | `material-document-detail` | 版本 / 类型 / feature 面包屑 | ready, sibling-switch, version-switch, source-missing | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-03` | `material-document-detail` | Markdown 正文区 | ready, sibling-switch, version-switch, source-missing | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-04` | `material-document-detail` | 同类文档切换 | ready, sibling-switch, version-switch, source-missing | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-05` | `material-document-detail` | 来源路径与只读说明 | ready, sibling-switch, version-switch, source-missing | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |

## 说明
- 组件契约用于 requirement freeze，不是最终前端组件实现规范。
- 实现阶段需要保持 component -> state -> AC/TC 的可追踪关系。
