# 组件契约清单：beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor

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
| `page-01-d1bbcc5c-component-01` | `page-01-d1bbcc5c` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-01-d1bbcc5c-component-02` | `page-01-d1bbcc5c` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-01-d1bbcc5c-component-03` | `page-01-d1bbcc5c` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-01-d1bbcc5c-component-04` | `page-01-d1bbcc5c` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `beacon-ui-component-01` | `beacon-ui` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `beacon-ui-component-02` | `beacon-ui` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `beacon-ui-component-03` | `beacon-ui` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `beacon-ui-component-04` | `beacon-ui` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-03-93da1608-component-01` | `page-03-93da1608` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-03-93da1608-component-02` | `page-03-93da1608` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-03-93da1608-component-03` | `page-03-93da1608` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-03-93da1608-component-04` | `page-03-93da1608` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-04-56a5749b-component-01` | `page-04-56a5749b` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-04-56a5749b-component-02` | `page-04-56a5749b` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-04-56a5749b-component-03` | `page-04-56a5749b` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-04-56a5749b-component-04` | `page-04-56a5749b` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `demo-component-01` | `demo` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `demo-component-02` | `demo` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `demo-component-03` | `demo` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `demo-component-04` | `demo` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `human-component-01` | `human` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `human-component-02` | `human` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `human-component-03` | `human` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `human-component-04` | `human` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-07-d4c36c95-component-01` | `page-07-d4c36c95` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-07-d4c36c95-component-02` | `page-07-d4c36c95` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-07-d4c36c95-component-03` | `page-07-d4c36c95` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-07-d4c36c95-component-04` | `page-07-d4c36c95` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-08-4a2d79ff-component-01` | `page-08-4a2d79ff` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-08-4a2d79ff-component-02` | `page-08-4a2d79ff` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-08-4a2d79ff-component-03` | `page-08-4a2d79ff` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-08-4a2d79ff-component-04` | `page-08-4a2d79ff` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-09-ece61c61-component-01` | `page-09-ece61c61` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-09-ece61c61-component-02` | `page-09-ece61c61` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-09-ece61c61-component-03` | `page-09-ece61c61` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-09-ece61c61-component-04` | `page-09-ece61c61` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-10-107f06b4-component-01` | `page-10-107f06b4` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-10-107f06b4-component-02` | `page-10-107f06b4` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-10-107f06b4-component-03` | `page-10-107f06b4` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-10-107f06b4-component-04` | `page-10-107f06b4` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `prd-component-01` | `prd` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `prd-component-02` | `prd` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `prd-component-03` | `prd` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `prd-component-04` | `prd` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `user-story-component-01` | `user-story` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `user-story-component-02` | `user-story` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `user-story-component-03` | `user-story` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `user-story-component-04` | `user-story` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-13-1c4ec680-component-01` | `page-13-1c4ec680` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-13-1c4ec680-component-02` | `page-13-1c4ec680` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-13-1c4ec680-component-03` | `page-13-1c4ec680` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-13-1c4ec680-component-04` | `page-13-1c4ec680` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-specs-json-component-01` | `page-specs-json` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-specs-json-component-02` | `page-specs-json` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-specs-json-component-03` | `page-specs-json` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-specs-json-component-04` | `page-specs-json` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `contract-component-01` | `contract` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `contract-component-02` | `contract` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `contract-component-03` | `contract` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `contract-component-04` | `contract` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-spec-component-01` | `page-spec` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-spec-component-02` | `page-spec` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-spec-component-03` | `page-spec` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-spec-component-04` | `page-spec` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-17-860d61fc-component-01` | `page-17-860d61fc` | 页面头部 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-17-860d61fc-component-02` | `page-17-860d61fc` | 关键内容区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-17-860d61fc-component-03` | `page-17-860d61fc` | 主要操作区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `page-17-860d61fc-component-04` | `page-17-860d61fc` | 状态与反馈区 | ready, loading, error | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-01` | `material-document-detail` | 文档头部信息 | ready, sibling-switch, version-switch, source-missing | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-02` | `material-document-detail` | 版本 / 类型 / feature 面包屑 | ready, sibling-switch, version-switch, source-missing | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-03` | `material-document-detail` | Markdown 正文区 | ready, sibling-switch, version-switch, source-missing | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-04` | `material-document-detail` | 同类文档切换 | ready, sibling-switch, version-switch, source-missing | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-05` | `material-document-detail` | 来源路径与只读说明 | ready, sibling-switch, version-switch, source-missing | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |

## 说明
- 组件契约用于 requirement freeze，不是最终前端组件实现规范。
- 实现阶段需要保持 component -> state -> AC/TC 的可追踪关系。
