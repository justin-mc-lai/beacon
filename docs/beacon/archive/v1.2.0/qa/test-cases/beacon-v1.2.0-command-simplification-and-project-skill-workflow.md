# Beacon v1.2.0 测试用例：主链简化、项目适配与需求锚定增强

**Feature**: Beacon v1.2.0 - Command Simplification and Project-Skill Workflow Enhancement  
**Version**: v1.2.0  
**Date**: 2026-04-08  
**Status**: Frozen

---

## 1. 测试目标

`v1.2.0` 的测试不能只验证“功能有没有”，而要验证：

```text
PRD
→ user-story
→ QA
→ implementation evidence
→ review / gate / release
```

是否因为这轮增强而变得：

- 更清晰
- 更可追溯
- 更少漂移

---

## 2. 测试范围

### 2.1 主链锚点合同

需要验证：

- PRD-to-story traceability
- story-to-AC traceability
- AC-to-test-case traceability
- scenario-family coverage
- evidence closure expectations

### 2.2 命令简化与智能路由

需要验证：

- 默认命令面是否更聚焦主链
- `help/status` 是否更像主链路由器
- backward compatibility 是否仍成立

### 2.3 项目级 skill workflow

需要验证：

- project-skill discovery/binding 是否降低了项目接入难度
- 是否继续保持 capability / evidence / stage boundary

### 2.4 Prototype requirement anchoring

需要验证：

- prototype 是否继续被 PRD/story 双向约束
- drift 是否能被显式检测

### 2.5 QA auto harness

需要验证：

- `qa auto harness` 是否被清晰限制在 story-native QA 范围内
- harness 是否只消费 baseline bundle 而不自行发明 benchmark target
- harness 是否只修改 bounded QA policy surfaces
- harness 输出是否足以被 review/gate 消费

---

## 3. 核心测试维度

| 维度 | 指标 | 目标 |
|------|------|------|
| 主链清晰度 | mainline discoverability | 用户更容易进入 `PRD/story/QA` 链 |
| 追溯性 | PRD-story-QA traceability | 必须显式可验证 |
| 覆盖率 | story/AC/scenario coverage | 不低于当前能力，且更可解释 |
| 适配性 | project-skill onboarding friction | 降低项目接入成本 |
| 防漂移 | requirement/prototype drift detection | 原型偏移必须被显式报告 |

---

## 4. 关键测试用例

### TC-001: 主链锚点合同存在且可读

**优先级**: P0  
**类型**: contract

**目标**:

- 验证 `v1.2.0` 文档显式声明 `PRD → story → QA` 为主链锚点

**预期结果**:

- `SUMMARY / think / user-story / prd / execution/index` 至少一处明确表达主链锚点
- subordinate workstreams 没有与主链并列抢占产品中心

---

### TC-002: Story-QA baseline bundle 可构建

**优先级**: P0  
**类型**: contract

**目标**:

- 验证 `PRD + story + AC matrix + scenario map + QA9 matrix + coverage scorecard` 可以被视为一个固定 bundle

**预期结果**:

- bundle 所需 artifact 列表明确
- bundle 结构固定
- 能用于后续项目适配或评估

---

### TC-003: Command simplification 不破坏主链

**优先级**: P0  
**类型**: functional

**目标**:

- 验证命令简化后主链命令仍稳定

**预期结果**:

- `think / user-story / prd / test-case / implement / qa / gate / release` 仍然清晰可达
- 默认命令面更聚焦，而不是更模糊

---

### TC-004: `help` 成为主链路由器

**优先级**: P0  
**类型**: functional

**目标**:

- 验证 `help` 能根据阶段正确推荐主链下一步

**预期结果**:

- 推荐应围绕当前主链阶段
- 推荐理由应明确
- 不应优先推荐边缘能力

---

### TC-004A: `ask / help` 作为智能入口成立

**优先级**: P0  
**类型**: functional

**目标**:

- 验证命令简化不是静态瘦身，而是通过 `ask / help` 强化主链导航

**预期结果**:

- `ask` 能基于意图推荐主链命令
- `help` 能基于当前阶段推荐下一步
- 推荐不会优先把用户导向 labs/边缘 surface

---

### TC-004B: Progressive disclosure 与兼容策略清晰

**优先级**: P1  
**类型**: contract

**目标**:

- 验证默认命令面、advanced surface、labs surface 之间有明确 disclosure policy

**预期结果**:

- 默认可见命令面优先主链
- advanced/labs surface 通过显式 disclosure 暴露
- 兼容别名 / staged migration 被明确定义，而不是隐含假设

---

### TC-005: Project-skill workflow 继续保持边界

**优先级**: P0  
**类型**: contract

**目标**:

- 验证项目 skill workflow 强化不会把项目执行逻辑并回 Beacon core

**预期结果**:

- 仍有显式 capability/stage/evidence boundary
- 仍是 project adapter，而不是 core runtime expansion

---

### TC-006: Project skill discovery 降低接入成本

**优先级**: P1  
**类型**: functional

**目标**:

- 验证 skill discover / templates / memory-aware recommendation 能帮助项目更快进入主链

**预期结果**:

- skill/profile 推荐更低摩擦
- 配置更少手工拼接
- 项目 verify/delivery 绑定更可解释

---

### TC-006A: `skill discover` 默认先 preview，不直接写回

**优先级**: P0  
**类型**: contract

**目标**:

- 验证 project-skill discovery 不会未经确认直接改配置

**预期结果**:

- 默认行为停在 preview / dry-run
- 只有显式 apply 才允许合并 `beacon.config.yaml`
- discovery state artifact 会保留推荐结果与 config diff

---

### TC-006B: `skill discover` 推荐必须可解释且面向主链

**优先级**: P0  
**类型**: functional

**目标**:

- 验证 discovery 返回的是可绑定的主链建议，而不是泛化分析报告

**预期结果**:

- 推荐包含项目特征、模板/skill/profile 建议、评分、理由、证据
- 推荐结果能回指 verify / delivery / debug / pipeline 等执行面
- 不会把项目私有执行逻辑描述成 Beacon core 能力

---

### TC-006C: `help / profile / doctor` 必须消费 discovery 结果

**优先级**: P1  
**类型**: integration

**目标**:

- 验证 discovery 不会形成孤立子流程

**预期结果**:

- 当项目尚未完成 project-skill onboarding 时，`help` 能推荐 `beacon skill discover --project-root .`
- `profile` 能显示或消费 discovery 生成的 profile 数据
- `skill doctor` 能验证 discovery 结果对应的模板、registry、capability、evidence contract

---

### TC-006D: 泛化 `beacon discover` 不进入当前主链冻结中心

**优先级**: P1  
**类型**: scope-contract

**目标**:

- 验证 project-skill research 中更宽的 codebase discover 想法没有挤占 v1.2.0 的主链中心

**预期结果**:

- requirement docs 明确以 `beacon skill discover` 为 v1.2.0 onboarding surface
- 泛化 `beacon discover` 仅作为 future advanced/labs direction 被记录
- 不会与 `PRD → story → QA` 主链并列抢占产品中心

---

### TC-007: Prototype 正向锚定

**优先级**: P1  
**类型**: functional

**目标**:

- 验证 PRD/story 中的需求点能映射到 prototype 页面或状态

**预期结果**:

- 未覆盖 requirement 被显式列出
- prototype 覆盖报告可追溯到 PRD/story

---

### TC-008: Prototype 反向锚定

**优先级**: P1  
**类型**: functional

**目标**:

- 验证 prototype 页面/状态若缺少 PRD/story 支撑，会被报告

**预期结果**:

- orphan prototype 被显式发现
- UI 模块信息缺失时能生成补充模板

---

### TC-009: Coverage scorecard 能表达正确维度

**优先级**: P0  
**类型**: contract

**目标**:

- 验证 coverage 不再只是“有没有测试”，而是主链可追溯性与证据性

**预期结果**:

- scorecard 至少包含：
  - PRD-to-story traceability
  - story coverage
  - AC coverage
  - scenario-family coverage
  - evidence completeness
  - false-complete sensitivity

---

### TC-010: v1.2.0 不扩成宽而散的 enhancement bundle

**优先级**: P0  
**类型**: product-contract

**目标**:

- 验证 `v1.2.0` 文档表达仍然是一个主目标 + 三个 subordinate workstreams

**预期结果**:

- command simplification、project-skill workflow、prototype anchoring 都被表达为 support workstreams
- 主产品叙事仍然围绕 `PRD/story/QA`

---

### TC-011: QA auto harness 的输入必须锚定 baseline bundle

**优先级**: P0  
**类型**: contract

**目标**:

- 验证 `qa auto harness` 被定义为消费 `PRD/story/QA baseline bundle`

**预期结果**:

- harness 输入明确要求：
  - PRD
  - story
  - AC matrix
  - scenario map
  - QA9 matrix
  - coverage/evidence scorecard
- harness 不允许自建 benchmark target

---

### TC-012: QA auto harness 的 subject surface 必须受限

**优先级**: P0  
**类型**: contract

**目标**:

- 验证 harness 只允许修改 bounded QA policy surfaces

**预期结果**:

- 允许面只包括 story-QA policy 类别
- 明确禁止：
  - project execution commands
  - release override
  - arbitrary repo-wide product mutation
  - memory/knowledge plane 独立扩张

---

### TC-013: QA auto harness 输出必须支持 keep/discard

**优先级**: P0  
**类型**: contract

**目标**:

- 验证 harness 每次运行都能形成可比较的迭代记录

**预期结果**:

- 输出包含：
  - changed policy surface
  - affected stories / ACs
  - coverage delta
  - evidence closure delta
  - false-complete delta
  - keep/discard verdict

---

### TC-014: QA auto harness 不能绕过 review / gate

**优先级**: P1  
**类型**: governance

**目标**:

- 验证 harness 只是 QA 政策迭代器，而不是新的放行中心

**预期结果**:

- harness 的产出被定义为 review/gate 输入
- harness 自身不能直接决定 release / accept

---

### TC-014A: 研究结论已被 versioned 物料吸收

**优先级**: P0  
**类型**: closure

**目标**:

- 验证 April 8 的 architecture / command / project-skill 三份深度调研已经进入 v1.2.0 正式需求包

**预期结果**:

- versioned research/execution docs 能追溯三份调研的关键结论
- think / prd / user-story / test-cases 中存在对应的 requirement deltas
- 这些研究不会只停留在 `.research/` 内部文件中

---

### TC-015: Requirement package 可冻结并生成 machine baseline bundle

**优先级**: P0  
**类型**: closure

**目标**:

- 验证 v1.2.0 需求物料已经达到可闭环、可冻结状态

**预期结果**:

- `SUMMARY / think / user-story / prd / qa / execution / release` 均存在且语义一致
- `execution/project-skill-qa-evolution-blueprint.md` 与 `source-architecture/index.md` 存在
- `.machine/user-story/<feature>.json` 可生成并冻结
- `.machine/qa/<feature>.ac-test-matrix.json`、`.story-scenario-map.json`、`.qa9-matrix.json` 可生成
- freeze 后的 release note 能明确说明：已冻结的是需求包，不是已实现代码

---

## 5. 验收口径

`v1.2.0` 的测试通过，不应只意味着“这些功能存在”，而应意味着：

1. 主链更容易被理解和执行
2. 主链追溯性更强
3. 项目适配更低摩擦
4. prototype 更不容易漂移
5. 整个版本线仍然围绕 `PRD/story/QA` 组织

如果只做到了局部功能增强，而没有做到这五点，那么 `v1.2.0` 仍然是不完整的。
