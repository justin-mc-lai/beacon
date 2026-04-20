# cc-design 项目借鉴分析

**分析日期**: 2026-04-20  
**目标**: 为 Beacon Prototype 命令改进提供参考  
**分析对象**: ~/Developer/Personal/oss-sync/cc-design/

---

## 一、cc-design 项目概览

### 1.1 项目定位

cc-design 是一个**设计系统与原型管理项目**，为开发团队提供统一的设计语言和协作平台。

### 1.2 核心目录结构

```
cc-design/
├── design/
│   ├── prototypes/     # 原型设计文件
│   ├── assets/         # 设计资源（图标、图片等）
│   ├── specs/          # 设计规范文档
│   └── README.md
└── README.md
```

### 1.3 设计原则

1. **一致性**: 保持设计语言的统一性
2. **可访问性**: 遵循无障碍设计标准
3. **可维护性**: 设计系统易于更新和扩展
4. **协作性**: 设计与开发紧密配合

---

## 二、可借鉴的核心理念

### 2.1 三层分离架构

cc-design 明确区分了三个层次：

```
┌─────────────────────────────────────┐
│ prototypes/ - 原型设计文件           │  ← 设计师工作层
│ - Wireframe (线框图)                │
│ - Mockup (视觉稿)                   │
│ - Prototype (交互原型)              │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ specs/ - 设计规范文档                │  ← 规范定义层
│ - 设计系统                           │
│ - 组件规范                           │
│ - 交互规范                           │
│ - 无障碍设计指南                     │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ assets/ - 设计资源                   │  ← 资源交付层
│ - 图标库                             │
│ - 插图                               │
│ - 组件导出                           │
└─────────────────────────────────────┘
```

**对 Beacon 的启示：**
- Beacon 也应该分离 **业务语义层**、**设计规范层**、**技术实现层**
- 当前 Beacon 的问题是三层混在一起

### 2.2 设计阶段明确划分

cc-design 定义了三个清晰的设计阶段：

| 阶段 | 名称 | 保真度 | 关注点 |
|------|------|--------|--------|
| 1 | Wireframe (线框图) | 低保真 | 布局和信息架构 |
| 2 | Mockup (视觉稿) | 高保真 | 完整的视觉设计 |
| 3 | Prototype (交互原型) | 可交互 | 用户流程 |

**对 Beacon 的启示：**
- Beacon 当前的 prototype 命令应该专注于 **Wireframe 阶段**
- 明确定位：**低保真原型，关注布局和信息架构**
- 不应该混入视觉设计或技术实现细节

### 2.3 工作流程清晰

cc-design 定义了完整的工作流程：

```
1. 需求分析 → specs/ 中创建需求文档
2. 原型设计 → prototypes/ 中创建设计文件
3. 设计评审 → 记录评审意见和修改历史
4. 资源导出 → 将最终资源导出到 assets/
5. 开发交付 → 提供设计规范和切图资源
```

**对 Beacon 的启示：**
- Beacon 的 prototype 命令应该在 **需求分析** 和 **原型设计** 之间
- 输入：PRD、User Story（需求文档）
- 输出：Wireframe（原型设计）
- 下游：设计师基于 Wireframe 创建高保真设计

### 2.4 命名规范严格

cc-design 对文件命名有严格规范：

```
[模块名]-[类型]-[版本号]-[日期].[扩展名]

示例：
- dashboard-wireframe-v1.0-20260420.fig
- user-profile-mockup-v2.1-20260420.sketch
- checkout-flow-prototype-v1.0-20260420.xd
```

**对 Beacon 的启示：**
- Beacon 的 prototype 输出应该包含 **类型标识**：`wireframe`
- 明确版本号和日期
- 建议格式：`[feature-name]-wireframe-[version]-[date]/`

### 2.5 规范文档结构化

cc-design 的 specs/ 目录有清晰的文档结构：

```markdown
# 组件名称

## 概述
简要描述组件的用途和使用场景

## 变体
列出所有变体和状态

## 规格
- 尺寸
- 间距
- 颜色
- 字体

## 交互
描述交互行为和状态变化

## 无障碍
无障碍相关的注意事项

## 示例
提供使用示例和代码片段
```

**对 Beacon 的启示：**
- Beacon 的 wireframe 输出应该包含类似的结构化信息
- 每个页面/组件应该有：
  - 概述（使用场景）
  - 变体（不同状态）
  - 规格（布局规格）
  - 交互（用户动作）
  - 示例（业务场景示例）

---

## 三、具体借鉴点

### 3.1 借鉴点 1：三阶段设计流程

**cc-design 的做法：**
```
Wireframe (低保真) → Mockup (高保真) → Prototype (可交互)
```

**应用到 Beacon：**
```python
# beacon/models/design_stages.py
class DesignStage(Enum):
    WIREFRAME = "wireframe"      # 低保真线框图（Beacon 负责）
    MOCKUP = "mockup"            # 高保真视觉稿（设计师负责）
    PROTOTYPE = "prototype"      # 可交互原型（设计师负责）

# beacon prototype 命令只负责生成 WIREFRAME
# 输出明确标注为 "wireframe"，避免混淆
```

**改进建议：**
```bash
# 当前命令
beacon prototype create "feature-x" --version v1.3.6

# 改进后命令（明确阶段）
beacon prototype wireframe "feature-x" --version v1.3.6
# 或
beacon prototype create "feature-x" --stage wireframe --version v1.3.6
```

### 3.2 借鉴点 2：规范文档模板

**cc-design 的做法：**
每个组件都有结构化的规范文档，包含：概述、变体、规格、交互、无障碍、示例。

**应用到 Beacon：**
```python
# beacon/templates/wireframe_page_template.py
WIREFRAME_PAGE_TEMPLATE = """
# {page_name}

## 使用场景
**用户角色**: {user_roles}
**使用时机**: {usage_timing}
**核心目标**: {core_goal}

## 关键问题
这个页面帮助用户回答以下问题：
{key_questions}

## 信息架构
{information_architecture}

## 页面状态
- **默认状态**: {default_state}
- **加载状态**: {loading_state}
- **空状态**: {empty_state}
- **错误状态**: {error_state}

## 用户动作
{user_actions}

## 布局规格
- **布局类型**: {layout_type}
- **响应式**: {responsive_breakpoints}
- **关键间距**: {spacing_specs}

## 无障碍考虑
{accessibility_notes}

## 业务规则
{business_rules}
"""
```

### 3.3 借鉴点 3：资源分类管理

**cc-design 的做法：**
```
assets/
├── icons/          # 图标库
├── images/         # 图片资源
├── illustrations/  # 插图
├── logos/          # Logo 和品牌标识
└── components/     # 设计系统组件导出
```

**应用到 Beacon：**
```
docs/beacon/{version}/prototype/{feature}/
├── wireframe/              # 线框图（Beacon 生成）
│   ├── pages/             # 页面线框图
│   ├── components/        # 组件线框图
│   └── flows/             # 流程图
├── specs/                  # 规范文档（Beacon 生成）
│   ├── business-scenarios.md
│   ├── information-architecture.md
│   └── interaction-map.md
└── assets/                 # 资源（设计师补充）
    ├── mockups/           # 高保真视觉稿
    └── prototypes/        # 可交互原型
```

### 3.4 借鉴点 4：版本管理策略

**cc-design 的做法：**
- 使用 Git 管理设计文档和规范
- 大型设计文件使用云端链接（Figma/Sketch Cloud）
- 保持设计版本与代码版本的对应关系

**应用到 Beacon：**
```python
# beacon/models/wireframe_metadata.py
@dataclass
class WireframeMetadata:
    feature_name: str
    version: str                    # 对应 Beacon 版本
    stage: DesignStage              # wireframe/mockup/prototype
    created_at: datetime
    prd_version: str                # 关联的 PRD 版本
    user_story_ids: list[str]       # 关联的 User Story
    design_tool: Optional[str]      # Figma/Sketch/None
    design_file_url: Optional[str]  # 云端设计文件链接
    status: str                     # draft/review/approved/archived
```

### 3.5 借鉴点 5：协作规范

**cc-design 的做法：**
- 设计文件命名清晰，包含版本号和日期
- 重要变更记录在 CHANGELOG 中
- 设计评审意见记录在对应的 issue 中
- 定期同步设计系统与代码实现

**应用到 Beacon：**
```markdown
# docs/beacon/{version}/prototype/{feature}/CHANGELOG.md

## [v1.0.0] - 2026-04-20

### Added
- 初始线框图生成
- 业务场景定义
- 信息架构设计

### Changed
- 调整首页布局，优化信息层级

### Review Comments
- [@reviewer] 建议增加空状态设计
- [@pm] 确认业务场景描述准确

### Design Handoff
- Figma 文件: [链接]
- 交付日期: 2026-04-25
- 负责设计师: @designer
```

---

## 四、对 Beacon Prototype 的具体改进建议

### 4.1 重新定位 Beacon Prototype 命令

**当前定位（模糊）：**
- 生成"原型"，但不清楚是什么阶段的原型
- 混合了业务语义、技术实现、视觉设计

**改进后定位（清晰）：**
```
Beacon Prototype = Wireframe Generator
- 阶段：低保真线框图
- 输入：PRD + User Story（业务需求）
- 输出：业务语义线框图（纯业务语言）
- 下游：设计师基于线框图创建高保真设计
```

### 4.2 采用 cc-design 的三层架构

```python
# beacon/models/wireframe_architecture.py

# 第一层：业务语义层（用户可见）
class BusinessSemantics:
    scenarios: list[BusinessScenario]      # 业务场景
    user_goals: list[str]                  # 用户目标
    key_questions: list[str]               # 关键问题
    information_needs: list[str]           # 信息需求

# 第二层：设计规范层（设计师使用）
class DesignSpecs:
    layout_type: str                       # 布局类型
    sections: list[Section]                # 页面区块
    states: dict[str, StateSpec]           # 页面状态
    interactions: list[Interaction]        # 交互定义

# 第三层：技术映射层（开发者使用）
class TechnicalMapping:
    page_id: str                           # 技术 ID
    route: str                             # 路由
    component: str                         # 组件名
    api_endpoints: list[str]               # API 端点
```

### 4.3 采用结构化的规范文档模板

参考 cc-design 的组件规范结构，为每个页面生成：

```markdown
# {页面名称}

## 概述
- 使用场景
- 用户角色
- 核心目标

## 信息架构
- 关键信息模块
- 信息层级
- 数据来源

## 页面状态
- 默认状态
- 加载状态
- 空状态
- 错误状态

## 交互设计
- 用户动作
- 触发条件
- 目标页面

## 布局规格
- 布局类型
- 响应式断点
- 关键间距

## 无障碍
- 键盘导航
- 屏幕阅读器
- 色彩对比度

## 业务规则
- 数据规则
- 权限规则
- 异常处理
```

### 4.4 改进输出目录结构

**当前结构（扁平）：**
```
docs/beacon/{version}/prototype/{feature}/
├── canonical-envelope.json
├── wireframe-summary.md
├── navigation-map.md
├── pages/
└── page-specs/
```

**改进后结构（分层）：**
```
docs/beacon/{version}/prototype/{feature}/
├── metadata.json                    # 元数据（版本、状态、关联）
├── CHANGELOG.md                     # 变更历史
├── wireframe/                       # 线框图层（Beacon 生成）
│   ├── business-scenarios.md       # 业务场景定义
│   ├── information-architecture.md # 信息架构
│   ├── pages/                      # 页面线框图
│   │   ├── home.md
│   │   └── management-overview.md
│   └── flows/                      # 流程图
│       └── user-journey.md
├── specs/                           # 规范层（Beacon 生成）
│   ├── layout-specs.md             # 布局规范
│   ├── interaction-specs.md        # 交互规范
│   └── accessibility-specs.md      # 无障碍规范
└── handoff/                         # 交付层（设计师补充）
    ├── design-file-link.md         # 设计文件链接
    ├── mockups/                    # 高保真视觉稿
    └── assets/                     # 导出资源
```

### 4.5 添加设计阶段标识

**在所有输出文件中明确标注设计阶段：**

```markdown
---
design_stage: wireframe
fidelity: low
generated_by: beacon-prototype-v1.3.6
generated_at: 2026-04-20T23:00:00Z
next_stage: mockup (由设计师完成)
---

# 经营驾驶舱首页 - 线框图

> **设计阶段**: 低保真线框图 (Wireframe)  
> **关注点**: 布局和信息架构  
> **下一步**: 设计师基于此线框图创建高保真视觉稿
```

---

## 五、实施优先级

### 高优先级（立即实施）

1. **明确定位为 Wireframe Generator**
   - 在所有输出中标注 "wireframe"
   - 文档中说明这是低保真原型

2. **采用业务语义优先原则**
   - 移除所有技术术语
   - 使用纯业务语言

3. **采用结构化文档模板**
   - 参考 cc-design 的组件规范结构
   - 包含：概述、信息架构、状态、交互、规格

### 中优先级（近期实施）

4. **重构输出目录结构**
   - 分离 wireframe/、specs/、handoff/ 三层
   - 添加 metadata.json 和 CHANGELOG.md

5. **添加版本管理支持**
   - 记录变更历史
   - 关联 PRD 和 User Story 版本

### 低优先级（长期优化）

6. **支持设计工具集成**
   - 支持导出到 Figma/Sketch
   - 记录设计文件链接

7. **建立设计系统**
   - 定义通用组件库
   - 建立设计 Token

---

## 六、总结

### 6.1 cc-design 的核心价值

1. **清晰的阶段划分**: Wireframe → Mockup → Prototype
2. **严格的层次分离**: prototypes/ → specs/ → assets/
3. **结构化的规范文档**: 统一的文档模板
4. **完善的协作流程**: 从需求到交付的完整链路
5. **规范的版本管理**: 设计版本与代码版本对应

### 6.2 对 Beacon 的关键启示

| cc-design 实践 | Beacon 应用 |
|---------------|------------|
| 三阶段设计流程 | Beacon Prototype = Wireframe Generator |
| 三层架构分离 | 业务语义层 / 设计规范层 / 技术映射层 |
| 结构化规范文档 | 统一的页面规范模板 |
| 清晰的命名规范 | `{feature}-wireframe-{version}-{date}/` |
| 版本管理策略 | 关联 PRD/User Story 版本 |

### 6.3 下一步行动

1. **立即行动**: 在 Beacon v1.3.7 中实施高优先级改进
2. **近期规划**: 在 v1.4.0 中完成中优先级改进
3. **长期愿景**: 建立完整的设计系统和工具链

---

**结论**: cc-design 虽然是一个简单的设计系统管理项目，但其**清晰的阶段划分**、**严格的层次分离**和**结构化的规范文档**理念，对 Beacon Prototype 命令的改进具有重要参考价值。核心是要明确 Beacon Prototype 的定位：**低保真线框图生成器**，专注于业务语义和信息架构，而不是技术实现或视觉设计。
