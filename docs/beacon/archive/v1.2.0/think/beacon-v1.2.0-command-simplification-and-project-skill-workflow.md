# Beacon v1.2.0 产品思考：围绕 `PRD → user-story → QA` 主链进行简化、适配与防漂移

**Feature**: Beacon v1.2.0 - Command Simplification and Project-Skill Workflow Enhancement  
**Version**: v1.2.0  
**Date**: 2026-04-08  
**Status**: Frozen

---

## 1. 关键判断

Beacon `v1.2.0` 不应被定义成一个泛化增强版本。

它真正要做的，是让 Beacon 已经存在的核心主链更容易操作、更容易适配项目、更不容易漂移：

```text
PRD
→ user-story
→ QA
→ implementation evidence
→ review / gate / release
```

这意味着：

- 命令简化不是独立目标，而是为了让主链更易学、更易用
- 项目级 skill 工作流不是独立目标，而是为了让主链在不同项目里更好落地
- prototype 锚定不是独立目标，而是为了减少需求到 UI 的偏移

---

## 2. 当前 v1.1.12 已经做对了什么

从现有架构和文档看，Beacon 已经具备：

1. 明确的 requirement kernel
2. 明确的 delivery evidence kernel
3. 项目级 profile / skill / verify / orchestrate 适配路径
4. release / gate / review 的正式证据闭环

所以 `v1.2.0` 不需要重新发明主链。

它需要做的是三件事：

1. **mainline hardening**
2. **operator simplification**
3. **project adaptation packaging**

---

## 3. 当前真正的问题

### 3.1 命令复杂度过高

当前 Beacon 的命令面太宽：

- 新用户不知道该从哪里进入
- `core / support / labs / bridge` 虽然在代码里分层了，但对外感知仍偏复杂
- 某些命令职责相近，增加心智负担

### 3.2 项目级 skill workflow 仍偏手工

虽然已经有：

- `profile`
- `skill bind`
- `verify run`
- `orchestrate run`

但项目方仍然需要自己做较多配置与推断。

### 3.3 Prototype 与需求仍可能漂移

prototype 和设计治理在 `v1.1.12` 已经很强，但：

- prototype 仍可能脱离 PRD/story 独立演化
- UI 模块信息可能在 PRD/story 中不完整
- gate 对“需求-原型一致性”的约束还不够显式

---

## 4. v1.2.0 的正确中心

这轮需求开发最重要的不是列很多 workstream，而是先锁定 hierarchy：

## Main objective

**让 `PRD → story → QA` 这条链更容易被理解、使用、验证和适配。**

## Subordinate workstreams

### A. 命令简化与智能路由

目标：

- 让用户更快进入主链
- 让 `help/status` 更像主链路由器

### B. 项目级 skill workflow 强化

目标：

- 让项目更容易绑定适合自己的 verify/delivery surface

冻结决策：

- `beacon skill discover` 是配置引导与绑定命令，不是通用项目分析器
- 默认先给 preview / dry-run，再允许显式 apply
- discovery 结果必须被 `help / profile / skill doctor` 共用，而不是形成第二套模型

### C. Prototype-PRD-Story 双向锚定

目标：

- 让 prototype 保持在需求主链约束内

---

## 5. 一条必须明确写进 v1.2.0 的原则

`v1.2.0` 的所有增强都必须满足：

> 不能削弱 `PRD → story → QA` 的可追溯性。  
> 只能增强它的可操作性、可适配性和防漂移能力。

这意味着：

- command simplification 不能让主链变模糊
- project skill workflow 不能把项目执行面拉进 Beacon core
- prototype work 不能盖过 requirement/evidence 主链

---

## 6. v1.2.0 最值得做的产物

### P0

1. `PRD-story-QA anchor contract`
2. `story-QA baseline bundle`
3. `coverage scorecard contract`

### P1

4. command surface simplification blueprint
5. project-skill discovery/binding blueprint

### P2

6. prototype requirement anchor contract
7. project adapter starter packs

---

## 7. 对当前版本线物料的要求

因此，`v1.2.0` 的正式文档表达不应继续写成：

- 命令简化 + skill workflow + prototype anchoring 三个并列主题

而应写成：

- 一个主目标
- 三个 subordinate workstreams
- 所有 AC 与 test cases 都回指 `PRD → story → QA`

---

## 8. 来自 2026-04-08 深度调研的补充结论

### 8.1 架构补充结论

- `v1.1.12` 的 requirement/evidence 主链已经足够成熟，`v1.2.0` 应视为 selective hardening line
- 四层架构（Requirement / Evidence / Adapter / Learning）必须继续保留
- 显式 agent 编排层、大模块重构、测试覆盖率平台化是 follow-on work，不是本轮产品中心

### 8.2 命令面补充结论

- 命令简化不只是“减少命令数”，而是要让 `ask / help` 成为主链智能入口
- 默认可见命令面应优先主链，advanced / labs surface 通过显式 disclosure 暴露
- 兼容别名 / staged migration 是 requirement contract 的一部分，而不是实现后再补

### 8.3 项目级 skill 补充结论

- `skill discover` 应吸收模板库、memory-aware recommendation、preview/apply loop 这三类能力方向
- Prototype 锚定应继续吸收 forward + reverse validation 的结论
- 更宽的泛化 `beacon discover` 代码库分析命令应被视为未来 advanced/labs 方向，不进入当前主链冻结中心

## 9. 最终结论

`v1.2.0` 不是“更多功能”的版本。

它应该是：

> Beacon 回到自身根锚点，并把主链做得更易用、更可项目化、更不漂移的版本。

