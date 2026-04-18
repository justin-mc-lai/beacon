# PRD：Beacon v1.3.4 结构化 PRD 生成与 Toolkit Skill 暴露修复

**Feature**: `beacon-v1.3.4-structured-prd-generation-and-toolkit-skill-surfacing`  
**Version**: `v1.3.4`  
**Date**: `2026-04-18`  
**Status**: `planning line`

## 1. 问题

在本轮 `v1.3.4` requirement 建设过程中，Beacon 自身暴露出两条明确产品摩擦：

### 1.1 `prd create` 仍是通用模板生成器

当前 [prd.py](/Users/apple/Developer/Personal/products/beacon/beacon/commands/prd.py) 的 `prd create` 只是写入一份固定占位模板：

- `Background`
- `Goals`
- `Timeline`
- `API Design`

它不会：

- 读取当前版本包主题
- 根据 feature 场景生成结构化章节
- 自动收敛 boundary / layering / rebuild / acceptance 这些关键骨架
- 区分“主 PRD”和“并行 PRD”的不同定位

结果是：

> `beacon-prd` 表面是正式 requirements 入口，实际生成能力却仍停留在 generic template 阶段。

### 1.2 memory/friction toolkit 有命令，没有子 skill

`v1.3.3` 文档已经正式承诺 memory/friction toolkit：

- PRD
- user story
- test cases
- execution materials

同时 CLI/labs 层也确实存在实现：

- [memory_friction_evolution.py](/Users/apple/Developer/Personal/products/beacon/beacon/commands/memory_friction_evolution.py)
- `beacon labs memory-friction-evolution`

但宿主 skill 面没有对应子 skill：

- `skills/beacon/` 下没有 `beacon-memory-friction-evolution/SKILL.md`
- `skills/beacon/SKILL.md` 只显式暴露了 `beacon-toolkit-lighthouse`

结果是：

> 文档承诺与宿主可见 skill surface 脱节，用户在 Codex/Claude 中无法通过一致的 Beacon skill 路由使用该 toolkit。

## 2. 目标

### 2.1 让 `prd create` 成为正式 requirement bootstrap 入口

`prd create` 必须从“generic template writer”升级为“version-aware / scenario-aware PRD generator”。

### 2.2 让已承诺 toolkit 拥有可达的 host-visible skill surface

当某个 optional toolkit 已经进入正式版本包和 skill 叙事时，必须有与之对应的宿主子 skill 或等价稳定入口。

### 2.3 保持主 `6+3` 边界不扩张

这次修复的目标不是扩张新的人类主流程，而是让 Beacon 自己已经承诺的入口真实可用、语义一致。

## 3. 设计原则

### 3.1 `prd create` 必须服务版本包，不是空白写字板

PRD 生成器的职责不是“生成任何 markdown”，而是：

- 生成当前版本线可用的 requirement 骨架
- 体现当前版本约束
- 体现 feature 类型差异
- 降低后续人工重写成本

### 3.2 文档承诺必须有宿主可达入口

如果一个 feature 已经进入：

- 版本包 `SUMMARY`
- PRD / user-story / QA
- skill 主文案

那么它至少必须满足其一：

- 有明确 host-visible subskill
- 或有明确、稳定、可被 skill 路由消费的等价入口

### 3.3 Optional toolkit 仍保持 optional

memory/friction toolkit 即使补足子 skill，也仍应保持：

- optional
- analysis-oriented
- 不扩张主 `6+3`

### 3.4 修复要最小但要闭环

这条线不追求一次性重写全部 PRD 体系或全部 toolkit surface，而是优先修复已经阻断真实使用的断层。

## 4. 范围

### In scope

- `prd create` 的结构化、版本感知、场景感知生成能力
- PRD 生成器与 `beacon-prd` skill 的一致性
- memory/friction toolkit 的 host-visible skill 补齐
- `skills/beacon/SKILL.md` 的暴露收口

### Out of scope

- 重写全部 requirement 命令
- 把 optional toolkit 升级为主流程入口
- 新增新的公开一级主命令
- 对所有 labs 命令都补子 skill

## 5. 功能需求

### FR-001 `prd create` 必须支持版本感知生成

当用户指定：

- `--version vX.Y.Z`
- feature 名称

时，生成器必须能感知：

- 当前版本包主题
- 当前版本包已有主/并行 PRD 结构
- 当前版本的 global boundaries

### FR-002 `prd create` 必须支持场景感知骨架

至少要能区分：

- 主 PRD
- 并行 PRD
- runtime/control-plane 类 PRD
- requirement/tooling friction 类 PRD

而不是所有场景都写同一份模板。

### FR-003 生成骨架必须包含边界类章节

对于非 trivial feature，生成结果至少应支持以下正式章节，而不是只给占位段落：

- 问题
- 目标
- 设计原则
- 范围
- 功能需求
- 风险与缓解
- 验收标准

### FR-004 生成器必须允许受控覆盖默认模板

应允许后续基于 feature type 或 version package registry 选择不同模板，不要求把所有逻辑都写死在 `prd.py`。

### FR-005 memory/friction toolkit 必须有 host-visible skill

当 `v1.3.3` 仍作为当前 runtime/toolkit 线时，memory/friction toolkit 必须有对应宿主 skill，例如：

- `skills/beacon/beacon-memory-friction-evolution/SKILL.md`

或其他等价、稳定、可发现的 Beacon skill 路由。

### FR-006 skill 文案必须与真实入口一致

`skills/beacon/SKILL.md`、examples、宿主暴露列表必须与真实子 skill / command surface 一致。

不得出现：

- 文档承诺存在 toolkit
- 但 skill routing 不可达

### FR-007 toolkit 仍必须保持非主面

即使补齐子 skill，也必须保持：

- optional
- analysis plane
- 不替代 `prd/user-story/test-case/implement/qa/release`

## 6. 候选实现方向

### Slice A：结构化 PRD 生成器

- 为 `prd create` 建立模板注册层
- 按 version / feature pattern / feature class 选择骨架
- 允许主 PRD 与并行 PRD 用不同模板

### Slice B：Beacon PRD skill 收口

- `beacon-prd` skill 应明确：
  - `prd create` 不是 generic markdown writer
  - 它应生成 Beacon 风格 requirement skeleton

### Slice C：Toolkit Skill 补齐

- 新增 memory/friction toolkit 子 skill
- 在 `skills/beacon/SKILL.md` 中作为 optional supplemental skill 暴露
- 保持其默认不污染主面

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| `prd create` 继续泛化，用户仍要大幅重写 | 高 | 建立最小模板注册机制，先覆盖真实高频场景 |
| toolkit 子 skill 补齐后侵入主面 | 中 | 保持 optional supplemental 定位，不放入主 `6+3` |
| 文档与入口再次漂移 | 高 | 把 skill drift 检查扩到 optional toolkit 子 skill 暴露 |

## 8. 验收标准

### AC-001 `prd create` 不再只是 generic template

真实新建一个版本线 PRD 时，输出结果必须至少包含 Beacon 风格结构化骨架，而不是占位模板。

### AC-002 主/并行 PRD 可区分

生成器必须能支持主 PRD 与并行 PRD 的不同骨架。

### AC-003 memory/friction toolkit 可通过宿主 skill 到达

在 Codex/Claude skill routing 中，memory/friction toolkit 必须存在稳定、可发现的子 skill。

### AC-004 主 `6+3` 不被扩张

补齐子 skill 后，默认主面仍只围绕 `6+3`，optional toolkit 只作为补充面存在。

## 9. 成功指标

- 新建 `v1.3.x` PRD 时，不再需要先删掉 80% 占位模板再重写
- 版本包文档里承诺的 optional toolkit 能通过宿主 skill 真实抵达
- Beacon skill 文案、examples、实际入口三者一致

## 10. 与主 PRD 的关系

本 PRD 是 `v1.3.4` 的并行修复线，服务于主 PRD：

- `beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane`

它解决的是“如何更正确地建立和暴露 v1.3.4 requirement/toolkit surface”，而不是 PocketBase 多项目运行态本身。

---

**Created**: 2026-04-18  
**Version**: v1.3.4  
**Status**: planning line  
**Memory Context**: N/A
