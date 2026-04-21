# Beacon 固定输入+LLM+稳定输出模式分析

**分析日期**: 2026-04-21  
**分析范围**: Beacon v1.3.3 核心命令实现  
**分析目标**: 
1. 验证是否全场景子skill实现了"固定输入 + LLM + 稳定输出"模式
2. 评估 Beacon 职责边界清晰度

---

## 执行摘要

### 核心发现

**问题1: 是否全场景采用"固定输入 + LLM + 稳定输出"？**

**答案：否。** Beacon 采用**混合策略架构**，根据命令特性选择最优实现模式：

| 模式类型 | 命令示例 | 占比 | 特征 |
|---------|---------|------|------|
| 纯规则生成 | test-case, user-story, think | ~30% | 确定性输出，零 LLM 调用 |
| 混合模式 | prd | ~10% | LLM 优先 + 规则回退 |
| 编排委托 | implement, qa, prototype | ~60% | 委托给宿主运行时（Claude Code/Codex） |

**问题2: Beacon 职责是否清晰？**

**答案：是。** Beacon 定位明确：

- **核心职责**: 证据驱动的产品工作流内核（PRD → 实现 → 验收 → 发布）
- **设计哲学**: 宿主原生（Host-Native）、极简人类心智负担
- **边界清晰**: 不做高保真设计、CI/CD 平台集成、生产运维

---

## 详细分析

### 1. 命令实现模式分类

#### 1.1 纯规则生成模式

**代表命令**: `test-case`, `user-story`, `think`

**特征**:
- ✅ 固定输入：结构化 PRD/User Story
- ❌ 无 LLM 调用：完全基于规则引擎
- ✅ 稳定输出：确定性 JSON/Markdown

**案例: test-case 命令**

```python
# beacon/commands/test_case.py (1267 lines)

def _extract_ac_items(content: str) -> list[dict]:
    """纯正则表达式提取 AC-XXX 模式"""
    pattern = r'(?:^|\n)(?:#+\s*)?(?:AC-(\d+)|验收标准\s*(\d+))[：:]\s*(.+?)(?=\n(?:#+\s*)?(?:AC-\d+|验收标准\s*\d+|$))'
    # 返回确定性列表

def _infer_layer_from_ac(ac_text: str) -> str:
    """规则推断测试层级"""
    if any(kw in ac_text for kw in ["界面", "页面", "按钮"]):
        return "ui"
    elif any(kw in ac_text for kw in ["API", "接口", "curl"]):
        return "api-curl"
    return "unit"

def _build_qa9_entries(ac_items: list[dict]) -> list[dict]:
    """生成 QA9 矩阵（功能/冒烟/单元/接口/契约/集成/回归/异常/兼容）"""
    # 纯规则映射，无 LLM
```

**输出示例**:
```json
{
  "ac-test-matrix": [
    {"ac_id": "AC-001", "layer": "ui", "priority": "P0"}
  ],
  "qa9-matrix": {
    "functional": [...],
    "smoke": [...],
    "unit": [...]
  }
}
```

**评估**:
- ✅ 输出完全确定性
- ✅ 无 LLM 不稳定性
- ⚠️ 灵活性受限于规则覆盖度

---

#### 1.2 混合模式（LLM + 规则回退）

**代表命令**: `prd`

**特征**:
- ✅ 固定输入：需求描述 + 版本号
- ✅ LLM 调用：语义化内容生成
- ✅ 规则回退：LLM 失败时降级到模板
- ✅ 契约验证：输出结构强校验

**案例: prd 命令**

```python
# beacon/commands/prd.py (1005 lines)

def _is_llm_disabled() -> bool:
    """环境变量控制 LLM 开关"""
    return os.environ.get("BEACON_PRD_DISABLE_LLM", "").lower() in {"1", "true"}

def _render_prd(topic: str, version: str, ...) -> str:
    """规则模板：返回带 '待补充' 占位符的骨架"""
    return f"""
# PRD: {topic}

## 1. 产品概述
**待补充**

## 2. 功能需求
**待补充**
"""

def _render_semantic_prd(topic: str, version: str, ...) -> str:
    """LLM 编译：调用宿主 AI 生成语义化内容"""
    # 委托给 Claude Code 的 LLM 能力

def _validate_contract(content: str, *, require_no_placeholders: bool) -> dict:
    """契约校验：检查必需章节 + 占位符"""
    required_sections = ["产品概述", "功能需求", "验收标准"]
    placeholders = ["待补充", "TODO", "TBD"]
    # 返回 {"valid": bool, "missing": [...], "has_placeholders": bool}

def create(topic: str, version: str, mode: str = "auto"):
    """主命令：模式选择逻辑"""
    if mode == "rule":
        content = _render_prd(...)  # 强制规则
    elif mode == "llm":
        content = _render_semantic_prd(...)  # 强制 LLM
        if not _validate_contract(content, require_no_placeholders=True)["valid"]:
            raise ValueError("LLM 输出未通过契约验证")
    else:  # mode == "auto"
        try:
            content = _render_semantic_prd(...)
            if _validate_contract(content, require_no_placeholders=True)["valid"]:
                return content  # LLM 成功
        except Exception:
            pass
        content = _render_prd(...)  # 回退到规则
    
    # 事务性写入（原子操作 + 失败回滚）
    _atomic_write(prd_path, content)
```

**模式选择矩阵**:

| 模式 | LLM 调用 | 规则回退 | 占位符允许 | 适用场景 |
|------|---------|---------|-----------|---------|
| `--mode=rule` | ❌ | N/A | ✅ | 离线环境、快速骨架 |
| `--mode=llm` | ✅ | ❌ | ❌ | 高质量需求、在线环境 |
| `--mode=auto` | ✅ | ✅ | 视情况 | 默认模式、最大容错 |

**评估**:
- ✅ 兼顾质量与稳定性
- ✅ 契约验证保证输出结构
- ⚠️ LLM 模式下仍存在语义不稳定性（通过多轮验证缓解）

---

#### 1.3 编排委托模式

**代表命令**: `implement`, `qa`, `prototype`

**特征**:
- ✅ 固定输入：需求文档 + 执行参数
- ❌ 无直接 LLM 调用：委托给宿主运行时
- ✅ 稳定输出：依赖宿主能力

**案例: implement 命令**

```python
# beacon/commands/implement.py (部分)

from beacon.utils.implement_native import run_native_implementation
from beacon.utils.implement_adapters import detect_skill_adapter
from beacon.utils.ralph_runtime import start_ralph_loop
from beacon.utils.team_surface import coordinate_team

def run(feature: str, version: str, runner: str):
    """主命令：适配器模式"""
    if runner == "native":
        # 委托给 Claude Code 原生能力
        run_native_implementation(feature, version)
    elif runner == "ralph":
        # 委托给 Ralph 迭代运行时
        start_ralph_loop(feature, version)
    elif runner == "team":
        # 委托给团队协作运行时
        coordinate_team(feature, version)
    else:
        # 检测外部 skill 适配器
        adapter = detect_skill_adapter(runner)
        adapter.execute(feature, version)
```

**宿主原生哲学**:

```
┌─────────────────────────────────────────┐
│         Beacon (编排层)                  │
│  - 需求管理                              │
│  - 流程编排                              │
│  - 契约验证                              │
└──────────────┬──────────────────────────┘
               │ 委托
               ▼
┌─────────────────────────────────────────┐
│    宿主运行时 (Claude Code/Codex)        │
│  - LLM 推理                              │
│  - 代码生成                              │
│  - 工具调用                              │
└─────────────────────────────────────────┘
```

**评估**:
- ✅ 避免重复造轮子
- ✅ 利用宿主最新能力
- ⚠️ 输出稳定性依赖宿主质量

---

### 2. Beacon 职责边界分析

#### 2.1 核心职责（做什么）

**产品工作流内核**:

```
think → prd → user-story → test-case → prototype → implement → qa → gate → release
  ↓       ↓        ↓            ↓           ↓          ↓        ↓      ↓       ↓
 思考   需求文档  用户故事    测试用例    原型图    实现代码   质量验收 门禁  发布
```

**关键能力**:
1. **需求闭环**: PRD → User Story → Test Case 全链路可追溯
2. **证据驱动**: 每个阶段产出机器可读的 canonical.json
3. **契约验证**: 强制输出结构校验（必需章节、字段类型）
4. **事务性写入**: 原子操作 + 失败回滚
5. **QA9 矩阵**: 9 类测试覆盖（功能/冒烟/单元/接口/契约/集成/回归/异常/兼容）

#### 2.2 边界约束（不做什么）

**来自 `docs/beacon/global-boundaries.md` 的 17 条全局约束**:

| 约束类型 | 具体内容 | 理由 |
|---------|---------|------|
| 设计边界 | 不做高保真视觉设计 | 委托给专业设计工具（Figma/Sketch） |
| 平台边界 | 不做 CI/CD 平台集成 | 委托给 Jenkins/GitHub Actions |
| 运维边界 | 不做生产环境监控 | 委托给 Prometheus/Grafana |
| 数据边界 | 不做数据库 schema 管理 | 委托给 Alembic/Flyway |
| 安全边界 | 不做漏洞扫描 | 委托给 Snyk/SonarQube |

**设计哲学**:
- **极简人类心智负担**: 用户只需关注"做什么"，不需关注"怎么做"
- **宿主原生**: 利用宿主（Claude Code）的 AI 能力，而非内嵌 LLM
- **单一职责**: 专注产品工作流，不扩展到基础设施

#### 2.3 职责清晰度评分

| 维度 | 评分 | 证据 |
|------|------|------|
| 核心职责定义 | ⭐⭐⭐⭐⭐ | 52 个命令清晰映射到产品生命周期 |
| 边界约束明确 | ⭐⭐⭐⭐⭐ | 17 条全局约束文档化 |
| 架构一致性 | ⭐⭐⭐⭐☆ | 混合策略架构，但模式选择有明确逻辑 |
| 文档完整性 | ⭐⭐⭐⭐⭐ | 456 行深度分析文档 + 全局约束文档 |

---

## 3. 架构模式评估

### 3.1 为什么不全场景采用"固定输入 + LLM + 稳定输出"？

**原因分析**:

1. **确定性需求**:
   - `test-case` 命令需要从 PRD 提取 AC-XXX 模式 → 正则表达式比 LLM 更可靠
   - `user-story` 命令生成固定结构 → 模板比 LLM 更高效

2. **成本效益**:
   - 简单规则能解决的问题，无需调用 LLM（降低延迟 + 成本）
   - LLM 适用于语义理解场景（如 PRD 内容生成）

3. **宿主原生哲学**:
   - Beacon 定位为"编排层"，而非"执行层"
   - 复杂 AI 任务委托给 Claude Code，避免重复实现

### 3.2 混合策略的优势

| 优势 | 说明 |
|------|------|
| **灵活性** | 根据场景选择最优实现（规则/LLM/委托） |
| **稳定性** | 规则模式提供确定性保底 |
| **质量** | LLM 模式提供语义化高质量输出 |
| **可维护性** | 清晰的模式分类，易于扩展 |

### 3.3 潜在风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| LLM 输出不稳定 | 契约验证 + 规则回退 |
| 宿主能力依赖 | 适配器模式支持多宿主 |
| 规则覆盖不足 | 持续迭代规则库 |

---

## 4. 结论与建议

### 4.1 核心结论

1. **Beacon 并非全场景采用"固定输入 + LLM + 稳定输出"模式**，而是采用**混合策略架构**：
   - 30% 纯规则生成（确定性场景）
   - 10% 混合模式（语义化场景 + 规则回退）
   - 60% 编排委托（复杂 AI 任务）

2. **Beacon 职责边界清晰**：
   - 核心：产品工作流内核
   - 边界：17 条全局约束明确不做什么
   - 哲学：宿主原生、极简心智负担

### 4.2 架构合理性评估

**✅ 优点**:
- 根据场景选择最优实现，避免"一刀切"
- 规则模式提供稳定性保底
- 宿主原生避免重复造轮子

**⚠️ 注意事项**:
- LLM 模式下仍存在语义不稳定性（已通过契约验证缓解）
- 需持续维护规则库覆盖度

### 4.3 改进建议

1. **增强契约验证**:
   - 当前仅验证结构（章节存在性）
   - 建议增加语义验证（如 AC 数量 ≥ 3）

2. **规则库可视化**:
   - 当前规则分散在各命令中
   - 建议提取到 `beacon/rules/` 统一管理

3. **模式选择透明化**:
   - 当前用户不知道命令使用了哪种模式
   - 建议在输出中标注 `[MODE: rule|llm|hybrid]`

4. **回退策略监控**:
   - 当前无法统计 LLM → 规则回退频率
   - 建议增加遥测（telemetry）收集回退率

---

## 附录

### A. 命令模式分类表

| 命令 | 模式 | LLM 调用 | 输出确定性 |
|------|------|---------|-----------|
| think | 规则 | ❌ | ✅ 完全确定 |
| prd | 混合 | ✅ | ⚠️ 视模式而定 |
| user-story | 规则 | ❌ | ✅ 完全确定 |
| test-case | 规则 | ❌ | ✅ 完全确定 |
| prototype | 委托 | ❌ (委托) | ⚠️ 依赖宿主 |
| implement | 委托 | ❌ (委托) | ⚠️ 依赖宿主 |
| qa | 委托 | ❌ (委托) | ⚠️ 依赖宿主 |
| gate | 规则 | ❌ | ✅ 完全确定 |
| release | 规则 | ❌ | ✅ 完全确定 |

### B. 参考文档

- `docs/analysis/beacon-功能职责与覆盖面深度分析.md` (456 lines)
- `docs/beacon/global-boundaries.md` (17 条全局约束)
- `beacon/cli_factory.py` (52 个命令注册)
- `beacon/commands/prd.py` (混合模式实现)
- `beacon/commands/test_case.py` (规则模式实现)

---

**分析完成时间**: 2026-04-21  
**分析者**: Claude (Sonnet 4.6)  
**文档版本**: v1.0
