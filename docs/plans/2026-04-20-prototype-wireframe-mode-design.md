# Beacon 原型设计重构：Wireframe Only 线框草图模式

**日期**: 2026-04-20  
**状态**: 设计阶段  
**方案**: 原型重构为 Wireframe Only

---

## 1. 问题分析

### 1.1 当前原型系统的问题

Beacon 当前的 `prototype` 命令仍残留完整 HTML 原型思路，存在以下问题：

1. **输出过于完整** - 生成完整的 HTML/CSS/JS，包含样式和交互细节，超出了早期需求验证阶段的必要性
2. **缺少跨平台支持** - 只生成 Web 页面，无法表达 PC、App、小程序等不同平台的差异
3. **跳转逻辑不够清晰** - 虽然有 `jump_map`，但在 HTML 页面中不够直观
4. **难以对接实现工具** - 完整 HTML 难以被 [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) 等新兴工具消费

### 1.2 核心需求

**目标工作流**：
```
需求文档 → Beacon 生成线框草图 → 人工审核 → 冻结 → 外部工具/后续规范生成设计 → 实现
```

**线框草图应包含**：
- 所有页面的清单和标记
- 页面间的跳转逻辑说明
- 跨平台差异标注（PC/App/小程序/Web）
- 布局结构（Markdown + ASCII 图）
- 可冻结、可版本化

---

## 2. 方案设计

### 2.1 核心思路

重构现有 `prototype` 命令，使其只输出 `wireframe` 线框草图包。

结论：

- Beacon 中不再保留 `html` 高保真原型模式
- `prototype` 的默认规范就是 `wireframe`
- 后续高保真设计交给其他规范或外部工具处理

### 2.2 命令接口

```bash
# 生成线框草图计划
beacon prototype plan <feature>

# 生成线框草图
beacon prototype create <feature>

# 查看线框草图状态
beacon prototype status <feature>  # 自动识别模式

# 冻结线框草图
beacon prototype freeze <feature>

# 审核线框草图
beacon prototype review <feature>
```

### 2.3 输出结构

#### Wireframe 模式输出

```
docs/beacon/<version>/prototype/<feature>/
├── manifest.json                    # 元数据（包含 prototype_mode: "wireframe"）
├── wireframe-summary.md             # 汇总文档（人类可读）
├── wireframe-manifest.json          # 页面清单、跳转关系
├── pages/
│   ├── page-1-overview.md          # 单页线框（Markdown + ASCII）
│   ├── page-2-detail.md
│   └── page-3-form.md
├── platform-variants.json           # 跨平台差异说明
├── navigation-map.json              # 跳转逻辑（结构化）
├── freeze.json                      # 冻结指纹
└── prototype-review.json            # 审核结果
```

---

## 3. 线框草图格式规范

### 3.1 wireframe-summary.md 示例

```markdown
# 线框草图汇总：Beacon v1.3.4 管理看板

**Feature**: beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane  
**Version**: v1.3.4  
**Mode**: wireframe  
**生成时间**: 2026-04-20 10:30:00

---

## 页面清单

| 页面 ID | 页面名称 | 平台 | 优先级 | 状态 |
|---------|----------|------|--------|------|
| portfolio-overview | 项目组合概览 | Web, PC | P0 | 待审核 |
| project-detail | 项目详情 | Web, PC, App | P0 | 待审核 |
| runtime-center | 运行态中心 | Web, PC | P1 | 待审核 |
| recovery-diagnostics | 恢复诊断 | Web, PC | P2 | 待审核 |

---

## 跳转关系图

```
[portfolio-overview] ──点击项目卡片──> [project-detail]
                     └──点击"运行态"──> [runtime-center]

[project-detail] ──点击"恢复诊断"──> [recovery-diagnostics]
                 └──返回──> [portfolio-overview]

[runtime-center] ──返回──> [portfolio-overview]

[recovery-diagnostics] ──返回──> [project-detail]
```

---

## 平台差异说明

### PC vs Web
- PC 端支持更宽的布局（1440px+）
- PC 端显示更多数据列

### App
- 仅 `project-detail` 页面支持 App
- App 端使用底部导航栏
- App 端隐藏侧边栏

### 小程序
- 暂不支持小程序平台

---

## 审核检查点

- [ ] 所有页面已标记平台支持
- [ ] 跳转逻辑完整无死角
- [ ] 布局结构清晰可理解
- [ ] 与 PRD/用户故事对齐
```

### 3.2 单页线框示例（pages/portfolio-overview.md）

```markdown
# 页面线框：项目组合概览

**页面 ID**: portfolio-overview  
**页面名称**: 项目组合概览  
**平台**: Web, PC  
**优先级**: P0

---

## 布局结构

```
+------------------------------------------------------------------+
|  [Logo]  Beacon 管理看板              [用户头像] [设置] [退出]  |
+------------------------------------------------------------------+
|                                                                  |
|  项目组合概览                                    [+ 新建项目]    |
|  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  |
|                                                                  |
|  +------------------+  +------------------+  +------------------+|
|  | 项目 A           |  | 项目 B           |  | 项目 C           ||
|  | 状态: 进行中     |  | 状态: 已完成     |  | 状态: 暂停       ||
|  | 进度: 75%        |  | 进度: 100%       |  | 进度: 30%        ||
|  | [查看详情]       |  | [查看详情]       |  | [查看详情]       ||
|  +------------------+  +------------------+  +------------------+|
|                                                                  |
|  +------------------+  +------------------+                      |
|  | 项目 D           |  | 项目 E           |                      |
|  | 状态: 计划中     |  | 状态: 进行中     |                      |
|  | 进度: 0%         |  | 进度: 50%        |                      |
|  | [查看详情]       |  | [查看详情]       |                      |
|  +------------------+  +------------------+                      |
|                                                                  |
+------------------------------------------------------------------+
|  第 1 页 / 共 3 页                          [上一页] [下一页]   |
+------------------------------------------------------------------+
```

---

## 元素清单

### 头部区域
- Logo（左上角）
- 页面标题："Beacon 管理看板"
- 用户头像（右上角）
- 设置按钮
- 退出按钮

### 主内容区域
- 页面标题："项目组合概览"
- 新建项目按钮（右上角）
- 项目卡片网格（响应式，PC 端 3 列，Web 端 2 列）

### 项目卡片
- 项目名称
- 状态标签（进行中/已完成/暂停/计划中）
- 进度条 + 百分比
- "查看详情"按钮

### 底部区域
- 分页信息
- 上一页/下一页按钮

---

## 交互说明

| 元素 | 交互 | 目标 |
|------|------|------|
| 项目卡片 | 点击 | 跳转到 `project-detail` 页面 |
| [查看详情] 按钮 | 点击 | 跳转到 `project-detail` 页面 |
| [+ 新建项目] 按钮 | 点击 | 打开新建项目表单（模态框） |
| [设置] 按钮 | 点击 | 打开设置页面 |
| [退出] 按钮 | 点击 | 退出登录 |
| [上一页]/[下一页] | 点击 | 切换分页 |

---

## 状态变化

### 加载中
- 显示骨架屏（项目卡片位置显示占位符）

### 空状态
- 显示"暂无项目"提示
- 显示"新建项目"引导按钮

### 错误状态
- 显示错误提示："加载失败，请重试"
- 显示"重试"按钮

---

## 平台差异

### PC 端
- 项目卡片网格：3 列
- 最大宽度：1440px

### Web 端
- 项目卡片网格：2 列
- 最大宽度：1200px

### 移动端（不支持）
- 此页面不支持移动端访问
```

### 3.3 wireframe-manifest.json 示例

```json
{
  "schema_version": "1.0",
  "feature": "beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane",
  "version": "v1.3.4",
  "prototype_mode": "wireframe",
  "generated_at": "2026-04-20T10:30:00Z",
  "pages": [
    {
      "id": "portfolio-overview",
      "name": "项目组合概览",
      "platforms": ["web", "pc"],
      "priority": "P0",
      "file": "pages/portfolio-overview.md",
      "status": "draft"
    },
    {
      "id": "project-detail",
      "name": "项目详情",
      "platforms": ["web", "pc", "app"],
      "priority": "P0",
      "file": "pages/project-detail.md",
      "status": "draft"
    },
    {
      "id": "runtime-center",
      "name": "运行态中心",
      "platforms": ["web", "pc"],
      "priority": "P1",
      "file": "pages/runtime-center.md",
      "status": "draft"
    },
    {
      "id": "recovery-diagnostics",
      "name": "恢复诊断",
      "platforms": ["web", "pc"],
      "priority": "P2",
      "file": "pages/recovery-diagnostics.md",
      "status": "draft"
    }
  ],
  "navigation": {
    "entry_page": "portfolio-overview",
    "jumps": [
      {
        "from": "portfolio-overview",
        "to": "project-detail",
        "trigger": "点击项目卡片",
        "type": "navigation"
      },
      {
        "from": "portfolio-overview",
        "to": "runtime-center",
        "trigger": "点击运行态按钮",
        "type": "navigation"
      },
      {
        "from": "project-detail",
        "to": "recovery-diagnostics",
        "trigger": "点击恢复诊断",
        "type": "navigation"
      },
      {
        "from": "project-detail",
        "to": "portfolio-overview",
        "trigger": "点击返回",
        "type": "back"
      }
    ]
  },
  "platform_variants": {
    "pc": {
      "max_width": "1440px",
      "grid_columns": 3,
      "notes": "支持更宽的布局和更多数据列"
    },
    "web": {
      "max_width": "1200px",
      "grid_columns": 2,
      "notes": "标准 Web 布局"
    },
    "app": {
      "supported_pages": ["project-detail"],
      "navigation_style": "bottom-tab",
      "notes": "仅项目详情页支持 App"
    }
  },
  "source_refs": [
    "docs/beacon/v1.3.4/user-story/beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane.md",
    "docs/beacon/v1.3.4/prd/beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane.md"
  ]
}
```

---

## 4. 实现计划

### 4.1 代码改动范围

#### 修改文件
- `beacon/commands/prototype.py` - 增加 `--mode` 参数
- `beacon/utils/prototype_utils.py` - 增加 wireframe 生成逻辑

#### 新增函数（在 prototype_utils.py 中）
- `write_wireframe_bundle()` - 生成线框草图包
- `compile_wireframe_plan()` - 编译线框草图计划
- `generate_wireframe_summary()` - 生成汇总文档
- `generate_wireframe_page()` - 生成单页线框
- `generate_ascii_layout()` - 生成 ASCII 布局图
- `extract_platform_variants()` - 提取平台差异

### 4.2 实现阶段

#### Phase 1: 基础框架（1-2 天）
- [ ] 增加 `--mode` 参数到 `prototype plan/create` 命令
- [ ] 实现 `write_wireframe_bundle()` 基础逻辑
- [ ] 生成 `wireframe-manifest.json`
- [ ] 生成 `wireframe-summary.md` 骨架

#### Phase 2: 线框生成（2-3 天）
- [ ] 实现单页线框生成（Markdown 格式）
- [ ] 实现 ASCII 布局图生成
- [ ] 提取跳转逻辑到 `navigation-map.json`
- [ ] 提取平台差异到 `platform-variants.json`

#### Phase 3: 集成与测试（1-2 天）
- [ ] 集成到现有 `freeze`/`review` 流程
- [ ] 编写单元测试
- [ ] 更新文档和示例

#### Phase 4: 工具对接（可选，后续迭代）
- [ ] 定义标准化 schema 供外部工具消费
- [ ] 提供 `export` 命令支持多格式导出
- [ ] 对接 awesome-design-md 等工具

---

## 5. 风险与挑战

### 5.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| prototype_utils.py 已经很大（81k tokens） | 代码维护困难 | 考虑拆分为 `wireframe_utils.py` |
| ASCII 图生成复杂度高 | 开发时间增加 | 先实现简单布局，复杂布局后续迭代 |
| 跨平台差异表达不够灵活 | 无法覆盖所有场景 | 提供扩展字段，允许自定义 |

### 5.2 产品风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 用户习惯了完整 HTML 原型 | 切换成本高 | 保持 HTML 模式为默认，wireframe 为可选 |
| 线框草图不够直观 | 审核效率低 | 提供清晰的示例和模板 |
| 外部工具对接不顺畅 | 工作流断裂 | 先验证 awesome-design-md 的消费能力 |

---

## 6. 成功标准

### 6.1 功能完整性
- [ ] 支持 `--mode wireframe` 生成线框草图
- [ ] 输出包含页面清单、跳转逻辑、平台差异
- [ ] 支持 Markdown + ASCII 图格式
- [ ] 集成到 freeze/review 流程

### 6.2 可用性
- [ ] 线框草图人类可读性强
- [ ] 跳转逻辑清晰无歧义
- [ ] 平台差异标注完整

### 6.3 可扩展性
- [ ] 输出格式可被外部工具消费
- [ ] 支持自定义平台类型
- [ ] 支持自定义布局模板

---

## 7. 后续演进方向

### 7.1 短期（1-2 个月）
- 完善 ASCII 图生成算法
- 增加更多布局模板（列表页、表单页、详情页等）
- 对接 awesome-design-md 工具

### 7.2 中期（3-6 个月）
- 支持交互式线框编辑（CLI 交互模式）
- 支持从线框草图生成测试用例
- 支持线框草图版本对比

### 7.3 长期（6-12 个月）
- 支持可视化线框编辑器（Web UI）
- 支持从设计工具（Figma/Sketch）导入
- 支持 AI 辅助线框生成

---

## 8. 参考资料

- [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) - Markdown 驱动的设计工具
- Beacon 现有原型系统：`beacon/commands/prototype.py`
- Beacon 线框命令：`beacon/commands/wireframe.py`（现有，但功能简单）
- Beacon 版本化机制：`docs/beacon/<version>/` 目录结构

---

## 9. 决策记录

| 日期 | 决策 | 理由 |
|------|------|------|
| 2026-04-20 | 选择方案 2（原型模式切换） | 复用现有基础设施，减少代码重复 |
| 2026-04-20 | 输出格式：Markdown + ASCII + JSON | 人类可读 + 机器可消费 |
| 2026-04-20 | 工作流：Beacon → 审核 → 外部工具 | 保持 Beacon 作为需求-设计桥梁 |

---

**文档版本**: 1.0  
**最后更新**: 2026-04-20  
**作者**: Claude (Beacon 设计分析)
