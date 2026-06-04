# PRD：Prototype 命令业务语义化改造

**Feature**: `prototype-business-semantic-refactor`  
**Version**: `v1.3.5`  
**Date**: `2026-04-20`  
**Status**: `draft`  
**Priority**: `P0`  
**参考文档**: 
- `docs/analysis/beacon-prototype-设计分析与改进方案.md`
- `docs/analysis/cc-design-借鉴分析.md`

---

## 1. 问题陈述

### 1.1 核心问题

当前 Beacon Prototype 命令存在以下关键问题：

1. **技术实现细节泄漏到产品语言层**
   - 输出中混杂技术术语（如 `management-overview`, `runtime`）
   - 页面定义使用技术 ID 而非业务名称
   - 用户看到的是技术实现而非业务价值

2. **线框图缺乏业务语义**
   - ASCII 图只展示布局结构，没有业务含义
   - 缺少数据来源、业务规则、异常处理说明
   - 设计师无法直接理解业务意图

3. **定位不清晰**
   - 不明确是低保真线框图还是高保真原型
   - 混合了业务语义、技术实现、视觉设计
   - 与设计工作流的衔接不清晰

### 1.2 影响

- **产品经理**：看到技术术语，需要翻译才能理解
- **设计师**：线框图太抽象，需要猜测业务含义
- **开发者**：不理解为什么要做，只知道做什么
- **QA**：不知道如何验证业务价值

### 1.3 为什么现在做

- v1.3.6 已引入 prototype 命令，但输出质量不符合预期
- 需要在 v1.3.5 中完成核心改造，为后续版本奠定基础
- 避免错误的设计模式在更多项目中传播

---

## 2. 目标

### 2.1 主要目标

将 Beacon Prototype 命令从**技术实现导向**改造为**业务语义优先**的线框图生成器：

1. **明确定位**：Beacon Prototype = Wireframe Generator（低保真线框图生成器）
2. **业务语义优先**：所有用户可见内容使用纯业务语言，禁止技术术语
3. **场景驱动设计**：从用户场景出发，而不是技术结构
4. **分层隔离**：业务层、设计规范层、技术映射层严格分离

### 2.2 非目标

- 不生成高保真视觉稿（Mockup）
- 不生成可交互原型（Interactive Prototype）
- 不直接生成前端代码
- 不替代设计师的工作

---

## 3. 设计原则

### 3.1 业务语义优先原则

**原则**：所有用户可见的内容必须使用业务语言，禁止技术术语。

**实施规则**：
- 页面名称：使用业务场景名称（✅ "经营驾驶舱首页" ❌ "home"）
- 功能描述：使用用户目标（✅ "帮助管理者快速识别需要介入的项目" ❌ "展示项目数、阻塞数"）
- 交互说明：使用业务动作（✅ "查看项目详细健康报告" ❌ "点击进入 project-detail 页面"）

### 3.2 场景驱动设计原则

**原则**：从用户场景出发，而不是从技术结构出发。

**设计流程**：
```
识别用户角色 → 定义使用场景 → 明确用户目标 → 设计信息架构 → 生成线框图
```

### 3.3 分层隔离原则

**原则**：业务层、产品层、技术层严格分离。

```
业务语义层 (Business Semantics)  ← 用户看到的
    ↓
设计规范层 (Design Specs)        ← 设计师使用的
    ↓
技术映射层 (Technical Mapping)   ← 开发者实现的
```

### 3.4 三阶段设计流程

参考 cc-design 项目的设计阶段划分：

| 阶段 | 名称 | 保真度 | 关注点 | Beacon 负责 |
|------|------|--------|--------|------------|
| 1 | Wireframe (线框图) | 低保真 | 布局和信息架构 | ✅ 是 |
| 2 | Mockup (视觉稿) | 高保真 | 完整的视觉设计 | ❌ 否（设计师负责） |
| 3 | Prototype (交互原型) | 可交互 | 用户流程 | ❌ 否（设计师负责） |

---

## 4. 功能需求

### FR-001 业务语义模型

**需求**：建立业务语义模型，替代当前的技术导向 PAGE_CATALOG。

**实现要点**：
- 创建 `beacon/models/business_semantics.py`
- 定义 `BUSINESS_SEMANTIC_MODEL` 结构
- 包含：业务场景、用户目标、关键问题、信息架构、用户动作、异常处理

**验收标准**：
- 所有页面定义都有完整的业务场景描述
- 无技术术语泄漏到业务层
- 通过业务语义验证测试

### FR-002 业务语义线框图生成

**需求**：重构线框图生成逻辑，生成包含业务语义的线框图。

**实现要点**：
- 重构 `prototype_utils.py` 中的线框图生成函数
- 实现 `generate_business_wireframe()`
- 线框图包含：使用场景、用户目标、关键问题、信息架构、业务价值、数据说明

**验收标准**：
- 生成的线框图完全使用业务语言
- 包含业务价值和数据说明
- 包含异常处理说明
- 设计师可以直接理解并转化为高保真设计

### FR-003 结构化规范文档模板

**需求**：为每个页面生成结构化的规范文档。

**实现要点**：
- 参考 cc-design 的组件规范结构
- 包含：概述、信息架构、页面状态、交互设计、布局规格、无障碍、业务规则

**验收标准**：
- 每个页面都有完整的规范文档
- 文档结构统一
- 包含所有必要的业务信息

### FR-004 分层输出目录结构

**需求**：重构输出目录结构，分离业务层、设计规范层、技术映射层。

**当前结构**：
```
docs/beacon/{version}/prototype/{feature}/
├── canonical-envelope.json
├── wireframe-summary.md
├── navigation-map.md
├── pages/
└── page-specs/
```

**改进后结构**：
```
docs/beacon/{version}/prototype/{feature}/
├── metadata.json                    # 元数据
├── CHANGELOG.md                     # 变更历史
├── wireframe/                       # 线框图层（Beacon 生成）
│   ├── business-scenarios.md       # 业务场景定义
│   ├── information-architecture.md # 信息架构
│   ├── pages/                      # 页面线框图
│   └── flows/                      # 流程图
├── specs/                           # 规范层（Beacon 生成）
│   ├── layout-specs.md             # 布局规范
│   ├── interaction-specs.md        # 交互规范
│   └── accessibility-specs.md      # 无障碍规范
└── handoff/                         # 交付层（设计师补充）
    ├── design-file-link.md         # 设计文件链接
    ├── mockups/                    # 高保真视觉稿
    └── assets/                     # 导出资源
```

**验收标准**：
- 目录结构清晰分层
- 每层职责明确
- 支持设计师后续补充

### FR-005 设计阶段标识

**需求**：在所有输出文件中明确标注设计阶段。

**实现要点**：
- 在文档头部添加 frontmatter
- 标注 `design_stage: wireframe`
- 说明下一步由设计师完成

**验收标准**：
- 所有输出文件都有设计阶段标识
- 明确说明这是低保真线框图
- 说明下一步工作

### FR-006 命令接口改进

**需求**：改进命令接口，支持业务语义模式。

**当前命令**：
```bash
beacon prototype create "feature-x" --version v1.3.6
```

**改进后命令**：
```bash
# 方式 1：从需求文档自动提取业务场景
beacon prototype create "feature-x" \
  --version v1.3.6 \
  --mode business-semantic \
  --extract-scenarios-from prd

# 方式 2：指定业务场景
beacon prototype create "feature-x" \
  --version v1.3.6 \
  --scenarios "经营决策场景,项目诊断场景"

# 方式 3：交互式场景定义
beacon prototype create "feature-x" \
  --version v1.3.6 \
  --interactive
```

**验收标准**：
- 支持从 PRD 自动提取业务场景
- 支持交互式场景定义
- 向后兼容现有命令

---

## 5. 技术方案

### 5.1 业务语义模型结构

```python
# beacon/models/business_semantics.py

@dataclass
class BusinessScenario:
    """业务场景定义"""
    scenario_name: str              # 场景名称（如"经营决策场景"）
    user_roles: list[str]           # 用户角色
    usage_timing: str               # 使用时机
    core_goal: str                  # 核心目标
    key_questions: list[str]        # 关键问题
    information_architecture: dict  # 信息架构
    user_actions: list[dict]        # 用户动作
    exception_handling: dict        # 异常处理

@dataclass
class InformationModule:
    """信息模块定义"""
    module_name: str                # 模块名称
    business_value: str             # 业务价值
    key_indicators: list[dict]      # 关键指标
    data_source: str                # 数据来源
    update_frequency: str           # 更新频率
    display_rules: str              # 展示规则

BUSINESS_SEMANTIC_MODEL = {
    "经营决策场景": BusinessScenario(...),
    "项目诊断场景": BusinessScenario(...),
    # ...
}
```

### 5.2 线框图生成逻辑

```python
# beacon/utils/wireframe_generator.py

def generate_business_wireframe(scenario_name: str) -> str:
    """生成业务语义线框图"""
    scenario = BUSINESS_SEMANTIC_MODEL[scenario_name]
    
    wireframe = []
    
    # 1. 场景说明
    wireframe.append(f"# {scenario.scenario_name}\n")
    wireframe.append(f"## 使用场景\n")
    wireframe.append(f"**用户角色**: {', '.join(scenario.user_roles)}\n")
    wireframe.append(f"**使用时机**: {scenario.usage_timing}\n\n")
    
    # 2. 用户目标
    wireframe.append(f"## 用户目标\n")
    wireframe.append(f"{scenario.core_goal}\n\n")
    
    # 3. 关键问题
    wireframe.append(f"## 这个页面帮助用户回答的问题\n")
    for question in scenario.key_questions:
        wireframe.append(f"- {question}\n")
    
    # 4. 信息架构
    wireframe.append(f"\n## 页面信息架构\n\n")
    for module_name, module_data in scenario.information_architecture.items():
        wireframe.append(generate_module_wireframe(module_name, module_data))
    
    # 5. 用户动作
    wireframe.append(f"\n## 用户可以做什么\n")
    for action in scenario.user_actions:
        wireframe.append(f"- **{action['动作']}**\n")
        wireframe.append(f"  - 触发方式：{action['触发条件']}\n")
        wireframe.append(f"  - 进入场景：{action['目标场景']}\n")
    
    return "".join(wireframe)
```

### 5.3 技术映射层（隔离）

```python
# beacon/models/technical_mapping.py

# 技术映射层：仅供开发者使用，不出现在业务文档中
TECHNICAL_MAPPING = {
    "经营驾驶舱首页": {
        "page_id": "home",
        "route": "/",
        "component": "DashboardHome",
        "api_endpoints": ["/api/projects/summary", "/api/projects/blocked"]
    },
    # ...
}
```

---

## 6. 实施计划

### Phase 1: 建立业务语义模型（2-3 天）

**任务**：
1. 创建 `beacon/models/business_semantics.py`
2. 定义 `BUSINESS_SEMANTIC_MODEL` 结构
3. 迁移现有 `PAGE_CATALOG` 到业务语义模型
4. 编写业务语义验证规则

**交付物**：
- 业务语义模型代码
- 单元测试
- 文档

### Phase 2: 重构线框图生成逻辑（2-3 天）

**任务**：
1. 重构 `prototype_utils.py`
2. 实现 `generate_business_wireframe()`
3. 实现 `generate_semantic_wireframe_section()`
4. 添加业务语义线框图模板

**交付物**：
- 重构后的代码
- 单元测试
- 示例输出

### Phase 3: 改进命令接口（1-2 天）

**任务**：
1. 添加 `--mode business-semantic` 选项
2. 实现 `--extract-scenarios-from prd` 功能
3. 实现 `--interactive` 交互式场景定义
4. 更新命令文档

**交付物**：
- 命令接口代码
- 集成测试
- 用户文档

### Phase 4: 重构输出目录结构（1-2 天）

**任务**：
1. 实现新的目录结构
2. 添加 metadata.json 和 CHANGELOG.md
3. 更新相关命令（status, review 等）

**交付物**：
- 目录结构代码
- 迁移脚本
- 文档

### Phase 5: 文档和示例（1 天）

**任务**：
1. 更新 `docs/beacon/archive/v1.3.5/prototype/` 文档
2. 创建业务语义线框图示例
3. 编写最佳实践指南
4. 更新 CHANGELOG

**交付物**：
- 完整文档
- 示例项目
- 最佳实践指南

---

## 7. 验收标准

### AC-001 业务语义优先

- [ ] 所有输出文件完全使用业务语言
- [ ] 无技术术语泄漏到业务层
- [ ] 通过业务语义验证测试

### AC-002 线框图质量

- [ ] 线框图包含使用场景、用户目标、关键问题
- [ ] 线框图包含业务价值和数据说明
- [ ] 线框图包含异常处理说明
- [ ] 设计师可以直接理解并转化为高保真设计

### AC-003 分层隔离

- [ ] 业务层、设计规范层、技术映射层严格分离
- [ ] 技术 ID 不出现在业务文档中
- [ ] 每层职责明确

### AC-004 命令接口

- [ ] 支持从 PRD 自动提取业务场景
- [ ] 支持交互式场景定义
- [ ] 向后兼容现有命令

### AC-005 文档完整性

- [ ] 每个页面都有完整的规范文档
- [ ] 文档结构统一
- [ ] 包含所有必要的业务信息

---

## 8. 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 业务语义模型设计不合理 | 高 | 中 | 参考 cc-design 和行业最佳实践，进行多轮评审 |
| 现有项目迁移成本高 | 中 | 高 | 提供迁移脚本和向后兼容模式 |
| 用户学习成本增加 | 中 | 中 | 提供详细文档和示例，支持交互式模式 |
| 技术债务积累 | 中 | 低 | 分阶段重构，保持代码质量 |

---

## 9. 成功指标

### 主要指标

- **业务语义覆盖率**：100% 的输出文件使用纯业务语言
- **设计师满意度**：设计师可以直接理解线框图，无需额外解释
- **迁移成功率**：现有项目可以顺利迁移到新模式

### 次要指标

- **文档完整性**：每个页面都有完整的规范文档
- **命令使用率**：新命令选项的使用率
- **错误率**：业务语义验证错误率

---

## 10. 参考资料

- [Beacon Prototype 设计分析与改进方案](docs/analysis/beacon-prototype-设计分析与改进方案.md)
- [cc-design 借鉴分析](docs/analysis/cc-design-借鉴分析.md)
- [Beacon Global Boundaries](docs/beacon/global-boundaries.md)

---

**Created**: 2026-04-20  
**Version**: v1.3.5  
**Status**: draft
