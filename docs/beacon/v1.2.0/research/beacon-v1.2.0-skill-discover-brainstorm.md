# Brainstorm: Beacon v1.2.0 `skill discover` from requirement to implementable plan

**Date**: 2026-04-08  
**Feature context**: `beacon skill discover`  
**Primary reference**: `.research/beacon-project-skill-workflow-deep-analysis-2026-04-08.md`  
**Method**: 7-dimension brainstorm  
**Question**: 从当前需求推到可实现阶段，`discover` 是否应该有独立的技术落地方案与 implement plan？

---

## 1. 一句话结论

**应该有，而且必须有。**

`beacon skill discover` 不是一个“小命令增强”，而是一条跨越以下几个面的功能线：

- 项目特征检测
- memory-aware 推荐
- skill 模板库
- project profile / skill 配置生成
- 与现有 `help / profile / skill bind / verify` 的协作

因此它如果没有独立的技术落地方案，会出现三个问题：

1. 需求看起来合理，但代码实现会散落在多个命令和 util 中
2. `discover` 很容易从“项目 skill 发现器”漂成“通用项目分析器”
3. 后续 implement plan 无法回答具体到文件、字段、状态产物的落地边界

所以结论不是“要不要做文档”，而是：

> `discover` 这条线必须有一份从需求到代码触点的独立技术落地方案，并且应有配套 implement plan。

---

## 2. 七维发散

## 2.1 用户维度

### 核心用户

1. **项目负责人**
   - 想快速让 Beacon 适配当前项目的 verify/delivery/debug workflow
2. **开发者**
   - 不想手工写很长的 `beacon.config.yaml`
3. **QA / 平台维护者**
   - 希望推荐结果是可验证、可追溯、可边界化的

### 结论

这类用户不需要一个“分析报告生成器”。
他们需要的是：

- 发现
- 推荐
- 生成
- 验证

所以 `discover` 是一个**配置引导与绑定命令**，不是泛化分析命令。

---

## 2.2 场景维度

### 典型场景

#### 场景 A：新项目接入

- 项目刚接入 Beacon
- 不知道该配哪些 skill/profile
- 希望 Beacon 自动分析项目并给出推荐

#### 场景 B：已有项目增强

- 项目已经在用 Beacon
- 但 verify/delivery 还比较手工
- 想补项目级 skill workflow

#### 场景 C：团队模板复用

- 团队已有多个类似项目
- 希望通过 memory 或模板快速复用配置

### 结论

这些场景都不是一次性的“看一眼项目”。
而是：

```text
analyze project
→ recommend skill/profile template
→ generate config
→ validate
→ bind into workflow
```

所以它天然需要 implement plan，而不是只要 PRD 就够。

---

## 2.3 业务维度

`discover` 对 Beacon 的价值，不在新命令数量，而在降低项目接入主链的摩擦。

### 直接价值

- 项目更容易进入 `verify / gate / release`
- 项目级 skill/profile 不再完全手工配置
- Beacon 的 project-aware 路线更可用

### 更深层价值

它能把 Beacon 从：

- “你得先理解一堆 profile/skill/orchestration 配置”

变成：

- “你先让 Beacon 理解项目，再确认推荐结果”

### 结论

这是明显影响 adoption 的功能面，值得有专门技术落地方案。

---

## 2.4 技术维度

这是最关键的一维。

### 当前代码基线

从现有实现看：

- `beacon/commands/skill.py`
  - 已有 `detect / list / show / register / bind / prefer / doctor / sync-check`
  - **没有** `discover`
- `beacon/utils/project_skills.py`
  - 已有：
    - skill registry
    - project profile create/load
    - feature-profile binding
    - orchestration validation / execution
    - contract drift detection
  - **没有**：
    - project feature analyzer
    - template loader
    - recommendation engine
    - discovery state persistence
- `beacon/commands/profile.py`
  - 当前只负责 create/show
  - 不负责 discovery result 的 review/apply
- `beacon/commands/help.py`
  - 当前是阶段路由器
  - 还不能把“项目还没 discover/bind”作为明确下一步提示

### 技术判断

这说明 `discover` 不应该作为一个小 patch 塞进 `skill.py` 就算完成。
它至少涉及四类新增能力：

1. **项目分析器**
2. **模板库加载器**
3. **推荐与排序器**
4. **discovery 结果状态/产物**

### 结论

从技术复杂度上，它已经满足“必须有独立技术方案”的阈值。

---

## 2.5 体验维度

### 用户期望的体验

用户真正想要的是：

```text
beacon skill discover --project-root .
```

然后得到：

1. 项目类型判断
2. 技术栈摘要
3. 推荐 skill/profile/template
4. 推荐理由
5. apply / dry-run / export

### 不应该变成的体验

- 一大段模糊 JSON
- 只给检测结果，不给下一步
- 生成配置但不验证
- 推荐结果无法回溯

### 结论

如果没有技术方案，体验很容易做成“半成品”。

---

## 2.6 价值维度

`discover` 的核心价值是：

- 降低 Beacon 项目接入门槛
- 提高 project-skill 路线的可用性
- 增强 `help/status` 的主链导航质量

但它的价值必须继续服务于：

```text
PRD
→ story
→ QA
→ verify / gate / release
```

换句话说：

`discover` 的价值不是“会分析项目”。
而是“让项目更容易进入 Beacon 主链”。

---

## 2.7 风险维度

| 风险 | 影响 | 结论 |
|------|------|------|
| discover 变成通用项目分析器 | 高 | 必须限制 scope |
| discover 直接改配置且不可回滚 | 高 | 必须先 dry-run / preview |
| 推荐算法不可解释 | 高 | 必须给推荐理由与证据 |
| 模板库和 profile schema 漂移 | 中 | 必须有固定 contract |
| discover 与 help/status 不联动 | 中 | 会降低产品价值 |

---

## 3. 收敛判断

## 3.1 是否需要技术落地方案？

**是。**

原因：

1. 涉及多个命令/模块
2. 涉及配置 schema
3. 涉及产物与状态写回
4. 涉及主链导航联动

## 3.2 是否需要 implement plan？

**是。**

而且 implement plan 不能只有“加一个命令”这种粒度。
它应该至少拆成：

- 分析
- 推荐
- 模板
- 状态写回
- 命令集成
- 测试

---

## 4. 推荐技术落地结构

## 4.1 命令层

### 新增命令

`beacon skill discover`

建议签名：

```bash
beacon skill discover \
  --project-root . \
  --interactive \
  --template <name> \
  --from-memory \
  --apply-recommended \
  --dry-run \
  --json
```

### 命令职责

- 分析项目特征
- 加载模板与 memory
- 生成推荐
- 预览配置
- 可选写回配置

---

## 4.2 util 层

建议新增：

- `beacon/utils/project_analyzer.py`
  - 技术栈、目录、依赖、规模、成熟度分析
- `beacon/utils/skill_templates.py`
  - 模板加载、校验、合并
- `beacon/utils/skill_discovery.py`
  - 推荐算法、评分、结果对象、dry-run payload

不建议把全部逻辑继续塞进：

- `project_skills.py`

否则会进一步放大已有 util 的职责体积。

---

## 4.3 配置/状态面

这里没有数据库，不涉及表结构新增。
但应明确有哪些**配置字段**和**状态文件**新增。

### A. 配置字段

建议在 `beacon.config.yaml` 中新增可选区块：

```yaml
project_skills:
  discovery:
    preferred_templates:
      - web-fullstack
    recommendation_policy: auto
    memory_enabled: true
    template_dirs:
      - beacon/templates/skill_profiles
```

### B. 状态产物

建议新增：

```text
.beacon/state/skill-discovery/<feature-or-project>.json
```

内容包括：

- project features
- recommended templates
- recommended skills
- recommendation scores
- recommendation reasons
- whether applied

### C. 产物写回

如应用配置，写回：

- `beacon.config.yaml`

如只预览，不写回配置，只产出 discovery artifact。

---

## 4.4 模板面

建议新增：

```text
beacon/templates/skill_profiles/
  web-fullstack.yaml
  mobile-app.yaml
  api-service.yaml
  data-pipeline.yaml
  ml-model.yaml
  二开-erp.yaml
  二开-cms.yaml
```

每个模板至少包含：

- registry
- profiles
- required_evidence
- required_cases
- orchestration nodes

---

## 4.5 主链联动面

这是很多方案容易漏掉的部分。

`discover` 的产品价值不在命令本身，而在它和主链的联动。

需要联动：

### A. `help`

如果项目缺 profile/skill 绑定，且处于需要 verify/project execution 的场景，`help` 应能推荐：

```text
beacon skill discover --project-root .
```

### B. `doctor`

`skill doctor` 应能消费 discovery 写回结果并检查：

- 模板是否完整
- skill entry 是否存在
- capability 是否满足 stage

### C. `profile`

`profile create/show` 应与 discover 结果兼容，不应形成两套模型。

---

## 5. 推荐 implement plan（草案）

## ITASK-001 — 命令入口与 payload 合同

改动：

- `beacon/commands/skill.py`

目标：

- 新增 `discover` 子命令
- 输出统一 JSON payload

边界：

- 不改现有 `bind / prefer / doctor`

## ITASK-002 — 项目特征分析器

改动：

- 新增 `beacon/utils/project_analyzer.py`

目标：

- 检测技术栈
- 检测目录结构
- 检测依赖文件
- 估算项目规模/成熟度

边界：

- 只做静态分析
- 不执行项目代码

## ITASK-003 — 模板加载与推荐引擎

改动：

- 新增 `beacon/utils/skill_templates.py`
- 新增 `beacon/utils/skill_discovery.py`

目标：

- 模板加载
- 推荐打分
- memory-aware 推荐
- dry-run 结果生成

边界：

- 先做规则型推荐
- 不引入复杂在线学习

## ITASK-004 — 配置写回与状态持久化

改动：

- `beacon.config.yaml` schema 扩展
- `.beacon/state/skill-discovery/*.json`

目标：

- 支持预览与应用
- 支持推荐结果落盘

边界：

- 不覆盖用户已有配置，优先 merge

## ITASK-005 — help / doctor / profile 联动

改动：

- `beacon/commands/help.py`
- `beacon/commands/profile.py`
- `beacon/commands/skill.py`

目标：

- 让 discover 进入主链导航
- 让 doctor 能校验 discover 结果
- 让 profile 面能消费 discover 结果

## ITASK-006 — 测试与版本文档闭环

改动：

- `tests/test_v120_skill_discover_*.py`
- `docs/beacon/v1.2.0/...`

目标：

- contract tests
- integration tests
- docs 同步

---

## 6. 最终建议

`discover` 不应再被看成“顺手加个命令”。

它更准确的定位是：

> Beacon `v1.2.0` 中让项目更容易进入主链的 project-skill onboarding surface。

因此它必须有：

1. 独立技术落地方案
2. 独立 implement plan
3. 明确字段/状态产物
4. 清楚的改动边界

否则需求会停留在“方向对，但无法可靠实施”的状态。

