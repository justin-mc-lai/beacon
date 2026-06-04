# 页面线框：物料文档详情

**页面 ID**: `material-document-detail`
**平台**: `Web, PC`
**优先级**: `P2`

## 页面职责
- 冻结文档阅读状态，包括来源路径、版本切换和同类文档切换。

## 关联 Requirement
- `user-story`: docs/beacon/archive/v1.3.5/user-story/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md
- `prd`: docs/beacon/archive/v1.3.5/prd/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md
- `test-case`: docs/beacon/archive/v1.3.5/qa/test-cases/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md

## 布局草图
```text
+---------------------------------------------------------------+
| 面包屑：version / document type / feature                    |
+---------------------------------------------------------------+
| Markdown 正文区                                               |
+---------------------------------------------------------------+
| 同类文档切换 | 来源路径 | 只读说明                            |
+---------------------------------------------------------------+
```

## 关键模块
- 文档头部信息
- 版本 / 类型 / feature 面包屑
- Markdown 正文区
- 同类文档切换
- 来源路径与只读说明

## 用户动作
- `返回物料查看器`: 点击返回 -> `material-viewer`
- `切换同版本文档`: 点击侧栏文档 -> `material-document-detail`

## 状态说明
- `ready` / 文档已打开: 显示文档正文与来源路径。
- `sibling-switch` / 切换同类文档: 在阅读区切换相邻文档。
- `version-switch` / 切换版本: 切换到同类型的其他版本文档。
- `source-missing` / 来源缺失: 文档不存在或来源路径不可达。

## 实现接力备注
- 当前页面是 requirement freeze wireframe，不是高保真视觉稿。
- 实现阶段必须回链本页与 navigation-map / wireframe-summary。
