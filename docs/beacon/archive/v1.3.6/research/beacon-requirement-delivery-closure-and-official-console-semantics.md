# Beacon Requirement Delivery Closure and Official Console Semantics

## 1. Summary

这份调研的核心结论是：

- Beacon 现在缺的不是更多命令，而是更稳定的 `product closure model`。
- 闭环的核心不是“跑完 implement / qa”，而是 `requirement truth -> execution -> verification -> evidence -> release` 是否持续对齐。
- `memory` 应该成为闭环的证据与召回底座。
- `evo` 应该成为闭环的边界探测与复发治理层。
- `team / ralph / subagent` 是内部执行实现，不应该直接成为默认产品语义。
- 最终可视化产品面应该是“官方正式的交付看板”，而不是“技术运行态拼盘”。

## 2. Current Beacon Baseline

### 2.1 Already present

Beacon 当前已经具备以下基础：

- requirement 主链：`prd -> user-story -> test-case -> prototype`
- delivery 主链：`implement -> qa -> release`
- workflow trace：`workflow-memory`
- memory/readback：`memory-v1.json + recall`
- friction/evolution：`memory-friction-evolution`
- execution surfaces：`single / team / ralph`
- support/read model：`status / doctor / report`
- visual console frozen line：`home / management-overview / project-detail / runtime-center / recovery-diagnostics / material-viewer`

### 2.2 Main gap

这些能力已经存在，但还没有被收口成统一的产品闭环：

- requirement 对 implement 的约束还不够显式
- QA 对 test-case 的对齐还不够产品化
- memory/evo 还没有正式成为 requirement/delivery closure 的治理层
- 可视化界面仍容易泄露内部技术语义，而不是官方产品语义

## 3. What Product Closure Means for Beacon

### 3.1 Requirement alignment

Beacon 需要的不是“有 PRD 就可以实现”，而是：

- implement 前必须知道当前冻结 requirement 是什么
- implement 过程中必须知道哪些点已经实现、哪些点还未覆盖
- QA 时必须知道它验证的是哪一组 test-case，而不是临时自由发挥
- release 时必须知道当前证据到底在支持哪条 requirement truth

所以闭环的第一层应该是：

> requirement alignment plane

它回答：

- 当前 feature 的正式 truth 是什么
- 当前实现对齐到了哪里
- 哪些点还缺证据
- 哪些点出现了 requirement drift

### 3.2 QA alignment

Beacon 的 QA 如果不强绑定 test-case，就很容易滑成：

- 一轮“看起来不错”的验证
- 一堆零散 evidence
- 一份很难回链到 requirement 的总结

更稳定的产品定义应该是：

> QA is test-case-aligned verification

这意味着：

- QA 先消费 test-case matrix
- 每条 scenario 都有明确状态：`covered / missing / blocked / failed / stale`
- 每条 verdict 都要能回链 evidence
- QA 输出不能只是 feature 摘要，还要能回答“哪条 test-case 还没有被正式验证”

### 3.3 Boundary exploration

闭环不能只处理“已经写出来的 requirement”，还要处理“边界是不是其实没探明”。

Beacon 当前最适合引入的不是无限自动探索，而是：

- 在 implement/qa/release 中识别 requirement 边界缺口
- 用 memory 保存问题样本和证据
- 用 evo 判断这是：
  - `clarification needed`
  - `spec drift`
  - `test gap`
  - `recurring failure`
  - `new boundary candidate`

所以 boundary exploration 应该是：

> bounded, evidence-backed, requirement-adjacent

而不是：

> open-ended autonomous ideation

## 4. Recommended Product Model

### 4.1 Approach A: Status aggregation

把已有 `status / report / release / team / qa` 结果继续汇总，靠更多字段完成闭环解释。

**Pros**
- 开发成本低
- 与现有实现耦合最少

**Cons**
- 只能得到更大的状态面板
- 对齐问题和语义问题依旧没有被产品化定义

**Best when:** 只追求短期可见性。

### 4.2 Approach B: Alignment-first closure model

新增统一 read model，把下列 5 个面统一起来：

1. requirement alignment
2. qa alignment
3. boundary exploration
4. execution closure
5. official console semantics

**Pros**
- 最符合 Beacon 当前 workflow-native 边界
- 可以把 memory/evo 纳入主闭环，而不是边缘工具
- 最有利于做正式产品语义

**Cons**
- 需要重整现有状态字段和视觉文案
- 需要明确哪些术语属于内部实现，哪些属于官方产品语义

**Best when:** 目标是稳定产品落地。

### 4.3 Approach C: Full autonomous delivery plane

把 boundary probing、repair orchestration、multi-agent runtime、release closure 都高度自治化。

**Pros**
- 自动化潜力高

**Cons**
- 容易让 Beacon 脱离最小主链
- 容易引入过重内部平台语义

**Best when:** 产品目标已经转向自治系统。

### 4.4 Recommendation

推荐采用 **Approach B**。

原因很直接：

- Beacon 已经有足够多的底层能力，不需要再造一套新平台。
- 当前最需要的是把这些能力翻译成稳定的产品闭环与官方语义。

## 5. Closure Layers Beacon Should Formalize

### 5.1 Requirement alignment plane

职责：

- 把 `prd / user-story / test-case / prototype` 编成当前 feature 的 requirement truth
- 显示 implement 对 requirement 的覆盖进度
- 识别 drift、missing、stale evidence

建议官方语义：

- `Requirement Status`
- `Coverage State`
- `Open Requirement Risks`

不要默认展示：

- raw fingerprint internals
- provider / fallback technical details

### 5.2 QA alignment plane

职责：

- 把 QA 绑定到 test-case
- 以 scenario 为单位给出 verdict
- 对缺口给出 `missing / blocked / stale / failed`

建议官方语义：

- `Verification Status`
- `Scenario Coverage`
- `Outstanding Verification Gaps`

不要默认展示：

- raw runner flags
- host runtime internals

### 5.3 Boundary exploration plane

职责：

- 从 implement/qa/release 失败、偏差、debug 中抽取边界候选
- 区分是 requirement 不清、实现偏差，还是新需求候选
- 把可复发问题沉淀到 memory/evo

建议官方语义：

- `Boundary Signals`
- `Clarification Needed`
- `Recurring Delivery Risks`

### 5.4 Execution closure plane

职责：

- 统一 single / team / ralph 的交付证据面
- 不管内部 runtime 怎么跑，输出都回到同一 requirement + QA + release closure

建议官方语义：

- `Execution Mode`
- `Delivery Progress`
- `Closure Readiness`

内部细节只在二级诊断面暴露：

- `team`
- `ralph`
- `subagent_runtime`
- `fallback_reason`

### 5.5 Official console semantics plane

职责：

- 把可视化管理端变成“正式产品看板”
- 优先展示经营、交付、风险、下一步
- 把技术语义收纳到 diagnostics，而不是首页默认面

## 6. Memory + Evo in the Closure Model

### 6.1 Memory role

memory 不是额外知识库，而是闭环的证据底座：

- 保存 requirement / qa / debug / release 的原始证据
- 保存 recurring issue 样本
- 为 implement/qa/release 生成最小 context pack
- 降低 team/ralph 接力成本

### 6.2 Evo role

evo 不是“自动进化秀场”，而是闭环治理器：

- 识别 recurring failures
- 检测 empty cycle / repair loop
- 标记 boundary clarification candidates
- 提醒当前 requirement 或 test-case 可能不完整

### 6.3 Combined effect

`memory + evo` 联合起来，才适合支撑 Beacon 的闭环：

- memory 负责保留证据与上下文
- evo 负责解释趋势与治理动作

没有 memory，evo 会变成无源之水。  
没有 evo，memory 会变成静态仓库。

## 7. Implement / QA / Team / Ralph Alignment

### 7.1 Implement should consume requirement truth

无论 `single / team / ralph` 哪种模式，implement 在产品上都应该被定义为：

- 读取 requirement truth
- 读取 stage context pack
- 写回 implementation evidence
- 产出对 QA 友好的 handoff

### 7.2 QA should consume test-case truth

QA 在产品上应该被定义为：

- 读取 test-case matrix
- 对每条 scenario 执行验证
- 产出 verdict + evidence
- 写回 release-facing scorecard

### 7.3 Team / Ralph should be internal execution families

它们存在的价值是：

- 提高执行效率
- 支持不同 runtime 和编排强度

它们不应该成为默认产品表述。默认界面应该看到的是：

- 当前执行模式是什么
- 当前闭环状态如何
- 当前卡点在哪里
- 下一步建议是什么

## 8. Official Visualization Semantics

### 8.1 Product pages should answer product questions

建议页面语义收口为：

- `Home`
  - 哪些项目在推进
  - 哪些项目需要介入
- `Portfolio Overview`
  - 多项目交付健康度
- `Project Detail`
  - 当前版本、当前 requirement、当前交付状态、下一步
- `Delivery Center`
  - 执行模式、验证状态、闭环 readiness
- `Recovery & Diagnostics`
  - 技术细节、runtime 细节、repair trace
- `Material Viewer`
  - 正式 requirement / QA / release 材料只读查看

### 8.2 Technical terms should be translated

建议的默认翻译：

| Internal term | Official product label |
|---|---|
| `team` | `Coordinated Execution` |
| `ralph` | `Autonomous Repair Loop` |
| `memory-friction-evolution` | `Boundary Learning` |
| `workflow-lifecycle` | `Execution Timeline` |
| `debug issues` | `Delivery Risks` |
| `fallback_reason` | `Execution Constraint` |
| `subagent readiness` | `Execution Readiness` |

原则：

- 首页和项目详情优先用官方产品语义
- 技术原词只保留在 Recovery / Diagnostics

### 8.3 Official visual tone

要正式产品化，就要避免：

- 太多实验性术语
- 太多内部工程状态名
- 首页充满 raw machine fields

应该优先呈现：

- 状态明确
- 责任明确
- 闭环明确
- 下一步明确

## 9. Risks

- 风险 1：把 memory/evo 引入后，UI 反而变得更技术化。
- 风险 2：为了做闭环，产品面暴露过多 `team / ralph / runtime` 细节。
- 风险 3：boundary exploration 失控，变成无限自动扩 scope。

对应缓解：

- UI 默认只展示官方语义
- diagnostics 页面单独承载技术细节
- boundary exploration 只输出 evidence-backed candidates，不自动改 truth

## 10. Recommended Research Outcomes

这轮研究建议先收口为 4 个后续方向：

1. 定义 `requirement alignment read model`
2. 定义 `qa-to-test-case alignment read model`
3. 定义 `memory + evo boundary governance contract`
4. 定义 `official console semantics dictionary`

在这 4 个方向冻结前，不建议直接进入实现。
