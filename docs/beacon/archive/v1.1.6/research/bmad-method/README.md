# Research: BMAD-METHOD — 分阶段 guided workflow、agent 协作与 next-step 导航

> 来源：`oss-sync/automation/autoresearch/bmad-method/`
> 复核时间：2026-03-24
> 证据等级：B
> 研究目标：为 Beacon v1.1.6 提供 **phase-based workflow、agent 分工、context documents、help navigator** 的源码级借鉴

---

## 1. 先给结论

BMAD-METHOD 最值得 Beacon 学的，不是“agent 很多”，而是：

1. **把工作流拆成明确阶段**
2. **让不同 agent/skill 负责不同阶段与产物**
3. **用 `bmad-help` 这种导航器回答‘下一步做什么’**
4. **用项目文档持续构建共享上下文**

它更像一个：

- guided development framework
- context-building method
- phase + role + deliverable 组合体系

而不是像 GSD 2 那样的 runtime/harness。

---

## 2. 从源码与官方文档复核到的关键事实

### 2.1 默认 BMM 套件是 agent + workflow 双层结构

`docs/reference/agents.md` 明确列出了默认 BMM agents，例如：

- Analyst
- Product Manager
- Architect
- Scrum Master
- Developer
- QA Engineer
- UX Designer
- Technical Writer
- Quick Flow Solo Dev

并且每个 agent 都有：

- skill id
- trigger
- primary workflows

这说明 BMAD 的核心不是“agent persona 好玩”，而是：

> **agent 作为 workflow 入口与职责边界。**

### 2.2 workflow map 是分阶段推进的，而不是平面工具列表

`docs/reference/workflow-map.md` 明确把 BMM 组织为：

- Phase 1: Analysis
- Phase 2: Planning
- Phase 3: Solutioning
- Phase 4: Implementation
- Quick Flow（小任务捷径）

每个阶段都有：

- 目标
- 对应 workflow
- 产出文件

也就是说，BMAD 的主轴是：

- 先形成文档化上下文
- 再让后续 agent/skill 在这些文档上继续推进

### 2.3 `bmad-help` 是导航器，而不只是 FAQ

workflow-map 与 how-to 文档都把 `bmad-help` 放在核心位置：

- 不确定下一步时运行它
- workflow 结束后也会给出下一步建议
- 它会根据已安装模块、项目状态、当前上下文给出建议

这和普通 CLI 的 `help` 很不同。

它更接近 Beacon 应该拥有的一种能力：

> **阶段感知 + 上下文感知的 next-step navigator**

### 2.4 `project-context.md` 体现了 BMAD 对共享上下文文件的重视

`docs/reference/workflow-map.md` 与相关 how-to 文档明确说明：

- `project-context.md` 用来记录实现规则和项目偏好
- 后续 workflow 都可把它作为共享上下文
- 目标是减少不同 agent 在实现阶段做出不一致决策

这说明 BMAD 的一个关键理念是：

- 文档不是交付副产物
- 文档是 agent 之间的共享记忆与约束介质

### 2.5 Quick Flow 与 Full Method 并存，体现复杂度分层

workflow-map 中的 Quick Flow 明确用于：

- 小而清晰的工作
- 跳过完整 phases 1-3
- 直接走更快的实现路径

这说明 BMAD 已经在产品层面承认：

- 不是所有任务都值得走完整重流程
- workflow 深度应该和任务复杂度匹配

### 2.6 BMM 之外还有模块生态，但不应混成单一“agent 数量”叙事

`README.md`、`module-help.csv`、docs 都说明除了 BMM 之外，还有：

- BMad Builder
- Test Architect (TEA)
- Game Dev Studio
- Creative Intelligence Suite

因此更准确的口径是：

- BMM 是默认核心套件
- 其上还有模块生态扩展
- 不能简单归纳成“BMAD 有 12+ agents”就完事

---

## 3. 本次修正了哪些旧口径

### 旧口径 1：BMAD 的核心价值 = 12+ 专家 agents

**修正后：过于表面。**

更准确的说法是：

- agent 只是职责入口
- 真正的核心是 phase-based workflow + document-driven context building

### 旧口径 2：BMAD 可以与 GSD 2、gstack 直接按同一 runtime/QA 维度比较

**修正后：不成立。**

BMAD 更接近：

- methodology
- phase orchestration
- role-based workflow

而不是：

- runtime engine
- browser harness
- benchmark framework

### 旧口径 3：Party Mode 是近期 Beacon 借鉴重点

**修正后：不应优先。**

对 Beacon 更有用的其实是：

- workflow map
- `bmad-help`
- `project-context.md`
- Quick Flow / Full Method 分层

---

## 4. 与 Beacon 的真实可比维度

| 维度 | BMAD 的强项 | Beacon 可借鉴点 |
|------|-------------|-----------------|
| Phase-based workflow | 强 | 分阶段主线与阶段产物 |
| Agent responsibility split | 强 | 按角色拆职责而不是按命令堆功能 |
| Next-step navigation | 强 | `doctor/help` 不只做诊断，还要做引导 |
| Shared context docs | 强 | `project-context.md` 这类共享上下文文件 |
| Runtime control | 弱 | 不是它的强项 |
| QA 金字塔 | 弱到中 | 需要借 TEA/其他模块，非 BMM 核心 |

---

## 5. 对 Beacon 的具体借鉴建议

### 适合吸收

1. **用 phase map 组织主流程**
2. **让不同能力单元绑定到不同阶段与产物**
3. **提供 next-step navigator（类似 `bmad-help`）**
4. **引入共享上下文文件，如 `project-context.md`**
5. **区分 Quick Flow 与 Full Method**

### 不适合现在就吸收

1. **大量 agent persona 命名体系**
2. **完整模块生态与 Party Mode**
3. **把 methodology 层和 runtime 层混合设计**

---

## 6. 关键证据文件

- `oss-sync/automation/autoresearch/bmad-method/docs/reference/agents.md`
- `oss-sync/automation/autoresearch/bmad-method/docs/reference/workflow-map.md`
- `oss-sync/automation/autoresearch/bmad-method/docs/index.md`
- `oss-sync/automation/autoresearch/bmad-method/src/bmm-skills/module-help.csv`
- `oss-sync/automation/autoresearch/bmad-method/src/core-skills/`
- `oss-sync/automation/autoresearch/bmad-method/README.md`

---

## 7. 一句话总结

BMAD-METHOD 对 Beacon 的真正启发是：

> **把 agent 能力、阶段推进、共享文档和“下一步建议”组织成一个可持续导航的工作流方法，而不是只增加更多角色。**
