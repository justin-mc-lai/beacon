# Research: gstack — browser harness、模板化 skills 与分层 QA 体系

> 来源：`oss-sync/agents/agent-skills/gstack/`
> 复核时间：2026-03-24
> 证据等级：A
> 研究目标：为 Beacon v1.1.6 提供 **skill 交付、浏览器执行面、验证金字塔、自调节 QA** 的源码级借鉴

---

## 1. 先给结论

gstack 最值得 Beacon 学的，不是“它是 Playwright 项目”，而是三件事：

1. **模板生成的 skill 交付链路**
2. **可分层定价的验证体系**
3. **带 stop heuristic 的 QA / 修复闭环**

它更像一个：

- browser harness
- AI workflow skill system
- QA / review / design audit 工具箱

而不是一个通用 coding-agent runtime。

---

## 2. 从源码复核到的关键事实

### 2.1 browser harness 的核心是 ref-based selection，不是 DOM 注入

`BROWSER.md` 明确说明：

- 通过 `page.locator(scope).ariaSnapshot()` 取 accessibility tree
- 解析后分配 `@e1`, `@e2` 等 ref
- 再把 ref 映射回 Playwright `Locator`
- 后续 `click @e3` 等命令通过 ref 找回 locator 执行

这套机制的特点是：

- 不依赖往 DOM 注入属性
- 对 AI 来说可读性强
- 能基于 accessibility tree 构造稳定引用

同时 `BROWSER.md` 还明确写了 **ref staleness detection**：页面 DOM 变化后，旧 ref 会先做 `count()` 检查，失效就要求重新 `snapshot`。

### 2.2 gstack 的 skill 文档是模板生成产物，不是手工维护最终态

`ARCHITECTURE.md` 与 `scripts/gen-skill-docs.ts` 共同说明：

- `SKILL.md.tmpl` 是人工维护源
- `SKILL.md` 是生成产物
- CI / 测试会检查模板与生成结果是否同步

这意味着 gstack 对“skill 文档本身”也做了工程化治理：

- 模板可复用
- 文档产物可校验
- skill 升级不会完全依赖人工同步

### 2.3 验证不是单层，而是 3-tier 结构

`ARCHITECTURE.md` 的 template test tiers 明确给出：

- **Tier 1 — Static validation**：免费、快速，校验命令和模板结构
- **Tier 2 — E2E**：真实会话运行技能流程
- **Tier 3 — LLM-as-judge**：让模型评估文档质量、清晰度、完整度

这说明 gstack 真正的强项不是“有测试”，而是：

> **把验证成本做了层次化管理**

先跑便宜检查，再在必要时跑昂贵验证。

### 2.4 `/qa` 不是无上限修 bug，而是带自调节 stop heuristic

`qa/SKILL.md` 中的 `WTF-likelihood` 明确规定：

- revert 增加风险分
- 一次 fix 触及文件过多增加风险分
- fix 数量过多增加风险分
- 触碰无关文件大幅增加风险分
- 超过阈值时必须停下来向用户汇报

这说明 gstack 的 QA/fix loop 不是“无限自治”，而是：

- 有量化中止条件
- 有 hard cap
- 有自我约束机制

### 2.5 diff-aware QA 与 health score 是 workflow 设计的一部分

`qa/SKILL.md`、`qa-only/SKILL.md`、`CHANGELOG.md` 都显示：

- 支持 diff-aware mode
- 以 health score 汇总质量状态
- 可以根据改动范围缩小测试面

这类机制对于 Beacon 很重要，因为它回答了两个问题：

1. 昂贵验证何时值得跑？
2. 验证结果如何被压缩成可决策信号？

### 2.6 gstack 还包含 proactive suggestions，但这不是其主要借鉴点

根 `SKILL.md` 与多个子 skill 文档中都有 `proactive` 开关逻辑。

这说明 gstack 也在做：

- 根据当前阶段主动推荐技能
- 允许用户关闭主动建议

但相较于模板化交付、browser harness 和验证金字塔，这一层对 Beacon 的优先级更低。

---

## 3. 本次修正了哪些旧口径

### 旧口径 1：gstack 只是一个 QA 框架

**修正后：过窄。**

更准确的说法是：

- 它当然有 QA 核心能力
- 但它还包含 skill delivery、browser harness、review/design/ship 等 workflow skills
- 它是一个围绕浏览器执行面与技能工作流组织起来的系统

### 旧口径 2：gstack 的关键价值主要是 skill 数量

**修正后：不成立。**

真正有借鉴价值的是：

- 模板到产物的工程化链路
- 分层验证
- QA stop heuristic
- diff-aware 选择

### 旧口径 3：gstack 可以直接提供 Beacon 的实现 runtime

**修正后：不应这样理解。**

它更像 Beacon 的：

- 浏览器执行与验证参考
- 技能模板化交付参考
- QA 质量治理参考

而不是 Beacon 全栈 runtime 的直接蓝图。

---

## 4. 与 Beacon 的真实可比维度

| 维度 | gstack 的强项 | Beacon 可借鉴点 |
|------|---------------|-----------------|
| Skill delivery | 强 | `tmpl -> generated docs` |
| Browser execution | 强 | 如果 Beacon 要做浏览器执行面，可借 ref/snapshot 设计 |
| QA / verification | 强 | 分层验证、health score、diff-aware、stop heuristic |
| Runtime orchestration | 弱到中 | 只覆盖浏览器执行面，不是通用 agent runtime |
| Artifact workflow | 弱 | 不是它的主轴 |

---

## 5. 对 Beacon 的具体借鉴建议

### 适合吸收

1. **模板化 skill 文档生成**
2. **静态检查 → E2E → LLM judge 的分层验证顺序**
3. **diff-aware 的昂贵验证触发策略**
4. **QA stop heuristic / self-regulation**
5. **health score 作为汇总质量信号**

### 不适合现在就吸收

1. **完整 browser daemon 与 ref 系统**（除非 Beacon 明确下探浏览器执行层）
2. **围绕 live-site QA 的大量特定流程**
3. **所有 review/design/ship skill 细节一比一迁移**

---

## 6. 关键证据文件

- `oss-sync/agents/agent-skills/gstack/BROWSER.md`
- `oss-sync/agents/agent-skills/gstack/ARCHITECTURE.md`
- `oss-sync/agents/agent-skills/gstack/qa/SKILL.md`
- `oss-sync/agents/agent-skills/gstack/qa-only/SKILL.md`
- `oss-sync/agents/agent-skills/gstack/scripts/gen-skill-docs.ts`
- `oss-sync/agents/agent-skills/gstack/CHANGELOG.md`

---

## 7. 一句话总结

gstack 对 Beacon 的最大启发不是“用 Playwright”，而是：

> **把 skill 文档、浏览器执行、以及高成本 QA 验证做成一套可生成、可分层、可自我刹车的工作流系统。**
