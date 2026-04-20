# 页面线框：项目物料查看器

**页面 ID**: `material-viewer`
**平台**: `Web, PC`
**优先级**: `P1`

## 页面职责
- 按 version -> document type -> feature 提供只读 Markdown 浏览。

## 关联 Requirement
- `user-story`: docs/beacon/v1.3.5/user-story/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md
- `prd`: docs/beacon/v1.3.5/prd/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md
- `test-case`: docs/beacon/v1.3.5/qa/test-cases/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md

## 布局草图
```text
+----------------------------------------------------------------+
| 版本树 | 文档类型 | feature 列表 | 文档阅读区                |
+----------------------------------------------------------------+
| 来源路径 | 只读说明 | 版本切换                                 |
+----------------------------------------------------------------+
```

## 关键模块
- 版本树
- 文档类型列表
- feature 目录
- 文档阅读面板
- 来源路径信息

## 用户动作
- `打开文档`: 点击文档列表项 -> `material-document-detail`
- `返回项目详情`: 点击返回 -> `project-detail`

## 状态说明
- `ready` / 可浏览: 版本树和文档列表已加载。
- `document-open` / 文档已打开: 右侧阅读区显示当前文档正文。
- `source-missing` / 来源缺失: 目标文档不存在或暂不可读。
- `loading` / 加载中: 文档列表或内容仍在加载。
- `empty` / 空状态: 该版本或类型下没有可读文档。
- `error` / 错误: 文档读取失败。

## 实现接力备注
- 当前页面是 requirement freeze wireframe，不是高保真视觉稿。
- 实现阶段必须回链本页与 navigation-map / wireframe-summary。
