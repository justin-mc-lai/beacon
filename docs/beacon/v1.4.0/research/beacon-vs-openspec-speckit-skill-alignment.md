# Beacon vs OpenSpec / Spec Kit — Skill 设计对齐与 LLM 能力释放分析

> 日期：2026-05-08
> 范围：Beacon `v1.4.0` skill 包 vs `github/spec-kit`、`dceoy/speckit-agent-skills`、`compnew2006/Spec-Kit-Antigravity-Skills`、`arunt14/spec-kit-qa`
> 已有底稿：`@/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.4.0/research/beacon-openspec-speckit-comparison-and-deliverable-design.md`、
> `@/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.4.0/research/beacon-agent-surface-speckit-trae-alignment.md`
> 注：用户提供的微信文档（`mp.weixin.qq.com`）抓取时被风控页拦截，本报告基于上述仓库内已沉淀的对比研究 + 当前 Beacon 实测代码量做对齐。

---

## 1. 量化对齐：Skill 厚度 vs 后台代码厚度

| 项目 | Skill 文档层 | 后台代码层 | 形态 |
|---|---:|---:|---|
| **Beacon `beacon-qa`** | `SKILL.md` 77 行 | `beacon/commands/qa.py` **1936** + `utils/qa_feature.py` **1425** + `utils/qa9.py` 406 + `qa_precision.py` 193 + `qa_runtime.py` 124 ≈ **~4 084** 行 Python | 强代码契约 |
| **Spec Kit 系（spec-kit / speckit-agent-skills / Antigravity / spec-kit-qa）** | 单一 `SKILL.md` 几十行 + 可选 bash helper | 几乎没有；决策权全交 LLM | 零代码契约 |
| **OpenSpec** | 各 slash 命令模板 | 中等：`openspec validate` 等少量 Node 工具 | 弱代码 + 目录协议 |

→ Beacon 一个子 skill 的 SKILL.md 看起来克制，但被它"路由"的 Python 实现是 Spec Kit 系总和的几十倍。这是**用户感受到的"Beacon QA 写了非常多代码"的根因**。

## 2. 三种路线的本质权衡

| 维度 | Beacon（强契约） | Spec Kit 系（零契约） | OpenSpec（中等） |
|---|---|---|---|
| **真相归属** | markdown truth + compiled contract（机器可验证） | LLM 即时推理；artifact 漂移依赖人审 | `openspec/changes/` 目录协议 |
| **决策稳定性** | 同输入 → 同输出（确定性优先） | 同输入 → 不同 LLM/版本会漂 | 中等：validate 拦截结构错 |
| **门禁能力** | `gate / release check / scorecard` 可阻断 | 无机器门禁；release 由 LLM 自述 | `validate` 仅校验目录结构 |
| **LLM 能力释放** | **被显著约束**：prompt-boundary、host-bridge、only frozen truth feeds implement | **充分释放**：LLM 直接生成 plan/tasks/qa report | 中等 |
| **维护成本** | 高：Python contract / projection / kernel 演进 | 低：改 SKILL.md prompt 即可 | 中 |
| **跨 host 一致性** | 高（contract 是单点） | 低（不同 LLM 行为差异大） | 中 |
| **新功能上线速度** | 慢（要走 PRD/story/test-case/implement/qa/release 全链） | 极快（写 prompt 就行） | 快 |
| **可审计性** | 强（evidence-first，每步留 JSON） | 弱（聊天记录） | 中 |
| **垂类深度** | 深（QA 能做 runner admission / SSO 检测 / Acceptance Kit v1 四层 verdict） | 浅（依赖 LLM 现场判断） | 中 |

**结论**：两条路线不是优劣关系，是**不同产品定位**。Beacon 自我定位是"evidence-first 交付内核"，Spec Kit 系是"LLM-first SDD 脚手架"。混用 → 出事。

## 3. Beacon 是否"职能限制过于严格、没释放 LLM 能力"

短答：**部分场景是的**。具体盘点：

### 3.1 严格但合理（应保留）

| 限制点 | 必要性 |
|---|---|
| `markdown truth root` 唯一写权 | 没有这条，evidence-first 不成立 |
| `implement` 唯一实施入口、`qa` 唯一验收入口、`gate` 唯一阻断 | 否则 release_ready 会被 goal/checkbox/board 伪造 |
| `brainstorm` 只读 + 路由 `change` | 否则会出现"AI 自己改自己冻结的真相" |
| `prompt-boundary` 持久化 verdict | 跨会话审计的关键 |
| `compiled minimal machine contract` 单源 | 否则 implement/qa/release 各看各的世界 |

### 3.2 严格但偏紧（值得放松）

| 限制点 | 当前现象 | 建议 |
|---|---|---|
| **`beacon qa` 用 1936 行 Python 编排 runner admission / SSO / 4 层 verdict** | SKILL.md 只是路由壳，几乎所有判断写死在 Python 里 | 把"runner 选择 / SSO 识别 / verdict 综合"等 **判断式逻辑**前移到 SKILL.md prompt 段，Python 只保留 **事实采集 + 结构化落盘 + gate 写入**。让 LLM 看证据自己得 verdict。 |
| **`prd / user-story / test-case` 都有 host-bridge + Python 编译双轨** | host-native LLM 已经能做的事，仍走 Python projection | bridge 已经存在，可以让 SKILL.md 提供更厚的 *prompt-as-code*（输入契约 + 输出 schema），Python 退到"校验 schema + 写 truth"的最小护栏。 |
| **每个子 skill 的 `Operator rule` 强制 `beacon <verb>`** | 宿主 LLM 只能调 CLI，不能直接生成 markdown | 对 *requirement compile* 类操作，可允许 LLM 直接产出符合 schema 的 markdown，再让 `beacon prd freeze --from-stdin` 仅做校验落盘。降低代码层冗余。 |
| **`implement plan` 输出 task ledger + projection + contract 三件套** | 三者都从 markdown 编译，重复信息多 | 收敛为"contract 单文件 + 渲染层"，task ledger 改为 view 而不是 source。 |
| **`beacon qa run` 默认行为重** | 用户体感"小事也要跑全链" | 提供 `qa quick / qa full` 双档；quick 由 LLM 在 prompt 内做静态检查，full 才走当前 1936 行流水线。 |

### 3.3 严格但缺位（应补能力释放点）

| 缺口 | 含义 |
|---|---|
| **没有 `beacon prompt`/`beacon ask` 类 LLM 自由探查面** | 用户想"让 LLM 在已冻结 truth 上自由问答 / 生成方案对比"必须绕道 brainstorm。建议加一个**只读 LLM 沙盒**，输出独立 markdown，不走 7+3。 |
| **`prototype` 仍偏文档化** | wireframe-freeze 阶段用 LLM 生成 HTML 高保真没开放 | 可挂一个 *optional projection*，在不污染 truth 的前提下让 LLM 真生成 HTML/Figma 桥接。 |
| **`qa` 的 4 层 verdict 是 Python 评分** | 每层 verdict 的"why pass/fail"叙事弱 | 让 LLM 在 verdict 落盘后追加叙事段（reason + improvement hint），写入同一 evidence 文件。 |

## 4. Skill 设计规划建议（Beacon 侧）

借 Spec Kit 系的路线，做"**SKILL.md 厚化 + 后台薄化**"分层重构，但**不放弃** Beacon 的契约纪律：

### 4.1 三段式 SKILL.md 模板

每个 skill 文档显式分三段（目前 Beacon SKILL.md 只有"description + Use for + Operator rule"，过薄）：

```markdown
## Inputs Contract        # 输入 schema（LLM 可读）
## Decision Protocol      # 让 LLM 现场决策的步骤、判据、输出格式
## Backstop CLI           # Python 仅做校验、落盘、gate 写入
```

`beacon-qa` 落地示意：

```text
Inputs:    feature_slug, version, evidence dir, runner availability map
Decision:  protected-surface 检测 → runner 优先级 → 4 层 verdict 综合
Backstop:  beacon qa run --feature ... --json   # 不再决策，只采证据 + 写 verdict
```

LLM 在 Decision 段直接产出 verdict JSON；Python 只做 schema 校验 + 写盘 + gate evidence 链接。`qa.py + qa_feature.py` 1936+1425 行可以预期压到 1/3 以下。

### 4.2 双档命令

主流程命令同时提供两档：

| 档位 | 形态 | 谁决策 |
|---|---|---|
| `<verb> quick`（新加） | LLM-only，读 truth → 输出建议 markdown | LLM |
| `<verb> run / freeze / check`（现状） | Python 编排 + LLM bridge + 落盘 | 代码 |

quick 不写 truth、不进 gate；只是给宿主 LLM 一个低摩擦入口，避免被严格主链劝退。

### 4.3 Skill 文档不再隐藏垂类知识

Beacon 当前把"runner admission / SSO 识别 / Acceptance Kit v1"这类**领域知识**埋在 Python 里。
Spec Kit 系的做法是**全部写进 SKILL.md**，让 LLM 看得见。
建议 Beacon 同样把这部分知识抬到 SKILL.md 的 *Decision Protocol* 段，Python 只剩"采集 + 写盘"。

### 4.4 LLM 自由面

加一个新的可选 skill：

| Skill | 定位 |
|---|---|
| `beacon-ask`（建议新增） | 只读 LLM 沙盒；读 truth + compiled contract → 自由生成方案对比 / 风险扫描 / 反事实分析；输出独立 markdown，不进 gate |

这样 Beacon 继续保留主链严格性，同时**释放 LLM 在 truth 之上的自由推理能力**，避免"什么都得走 7+3"的体感。

## 5. 与 OpenSpec / Spec Kit 距离判断

| 维度 | 距离 | 评价 |
|---|---|---|
| 真相纪律 | **领先** | Beacon 的 `frozen truth + change/refreeze + archive + 4 层 verdict` 比两者都严格 |
| 工程化 | **领先** | host-bridge / contract / scorecard / real-project-validation 是两者没有的 |
| LLM 能力释放 | **落后** | Spec Kit 系把决策权交给 LLM；Beacon 写在 Python 里 |
| 上手速度 | **落后** | Spec Kit `specify init` 几分钟可跑；Beacon 主链需要熟悉 7+3 |
| 跨 host 一致性 | **领先** | contract 是单点 |
| 社区生态 | **落后** | Beacon 单仓自治；Spec Kit 已有 plugin marketplace + Antigravity 等分支 |

**总判断**：Beacon **职责能力足够强悍**，问题不在能力，在 **能力释放路径**。当前是"Python 决策 + LLM 仅做语义润色"，应朝"**LLM 决策 + Python 写入护栏**"重心迁移。这与 v1.4.0 主题"lightweight kernel and core surface refactor"是同向的——但 v1.4.0 减重的是 *projection sprawl*，**没动 skill 层 prompt 与 Python 决策的分配**，建议作为 v1.4.x 或 v1.5.0 的下一条主线。

## 6. 落地建议（按风险从低到高）

1. **低风险**：把 `beacon-qa` 的"protected live surfaces / runner admission"小节从 Python 注释抬到 `SKILL.md` 的 *Decision Protocol*，Python 中保留为 fallback 文案。立竿见影减少认知负担。
2. **低风险**：新增 `beacon-ask`（只读 LLM 沙盒 skill），不动主链。
3. **中风险**：为主流程 7 个命令加 `quick` 子命令档（LLM-only，不进 gate）。
4. **中风险**：`prd / user-story / test-case` 的 host-bridge 输出 schema 化，Python 退化为校验器，目标减码 30~50%。
5. **高风险**：QA 4 层 verdict 评分逻辑全面 LLM 化，Python 仅做证据采集 + schema 校验 + gate 写入；需要新增 *trace-scorecard* 上的 LLM-vs-Python 一致性回归测试。

## 7. 主要参考

- 现有底稿：`@/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.4.0/research/beacon-openspec-speckit-comparison-and-deliverable-design.md`
- 表面对齐：`@/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.4.0/research/beacon-agent-surface-speckit-trae-alignment.md`
- 归档对比：`@/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.4.0/research/openspec-archive-vs-beacon-version-evolution.md`
- 上游对照：`github/spec-kit`、`dceoy/speckit-agent-skills`、`compnew2006/Spec-Kit-Antigravity-Skills`、`arunt14/spec-kit-qa`
- Beacon 当前 QA 代码量：`@/Users/apple/Developer/Personal/products/beacon/beacon/commands/qa.py` (1936) + `@/Users/apple/Developer/Personal/products/beacon/beacon/utils/qa_feature.py` (1425) + `@/Users/apple/Developer/Personal/products/beacon/beacon/utils/qa9.py` (406) + `@/Users/apple/Developer/Personal/products/beacon/beacon/utils/qa_precision.py` (193) + `@/Users/apple/Developer/Personal/products/beacon/beacon/utils/qa_runtime.py` (124)
- 关联分析：`@/Users/apple/Developer/Personal/products/beacon/docs/analysis/beacon-v1.4.0-agent-skill-能力特性分析.md`

> 已通过 `playwright-cli` CDP 模式重新拉取微信原文与 `arunt14/spec-kit-qa` 仓库，数据补齐见下方 §8 §9 §10。

---

## 8. spec-kit-qa 事实核对（已 clone 实测）

仓库：`arunt14/spec-kit-qa`（v1.0.0, MIT, 2026-04-01）。**全部交付物**：

| 文件 | 行数 | 角色 |
|---|---:|---|
| `commands/run.md` | **199** | skill prompt：QA 决策协议 |
| `commands/qa-template.md` | **91** | QA 报告模板 |
| `extension.yml` | 32 | 扩展清单（hook `after_implement`） |
| `README.md` | 42 | 安装与定位 |
| **合计** | **364 行 markdown** | **0 行代码** |

`run.md` 把 QA 决策完全写成 LLM 能直接执行的 10 步协议：

1. 读 `spec.md` / `tasks.md` / `plan.md` 计划；
2. 检测应用是否运行；
3. 选择 QA 模式（Browser / CLI / Hybrid）；
4. 派生测试场景；
5. 设置环境；
6. 浏览器 QA：导航、填表、UI 校验、截图、记 ✅/❌/⚠️/🔵；
7. CLI QA：跑命令、抓 stdout/stderr/exit、API 校验；
8. 跑既有 test suite 并区分"既有失败 vs 新失败"；
9. 用 `templates/qa-template.md` 生成报告（QA Summary / Test Results Table / AC Coverage Matrix / Failures Detail / Environment / Metrics）；
10. 给三种 verdict（ALL PASSED / PARTIAL PASS / FAILURES FOUND）+ 后置动作建议（`/speckit.ship` 或重跑）。

**关键观察**：

- **零 Python**。spec-kit-qa 依赖宿主 LLM 的 browser/CLI 工具能力 + spec-kit 主框架的 hook executor。
- **决策完全在 prompt 里**：runner 选择、verdict 综合、报告结构、AC 覆盖矩阵、scenario id 命名，全在 markdown 中文字描述。
- **hook 通过 YAML 注册**：`hooks.after_implement.optional=true` + `prompt`，由 spec-kit 框架的 HookExecutor 执行，扩展不评估 condition。
- **没有 contract / scorecard / gate**。verdict 是 LLM 现场叙事；release_ready 由 `/speckit.ship` 后续阶段判定。

vs Beacon `beacon-qa`：

| 项 | spec-kit-qa | Beacon `beacon-qa` |
|---|---:|---:|
| Skill 文档 | 364 行 markdown | 77 行 SKILL.md |
| 后台代码 | **0 行** | **~4 084 行 Python**（qa.py 1936 + qa_feature 1425 + qa9 406 + qa_precision 193 + qa_runtime 124） |
| Verdict 决策 | LLM 现场综合，3 档 | Acceptance Kit v1 四层（skill-contract / scenario-suite / trace-scorecard / real-project-proof），Python 评分 |
| Runner admission | 让 LLM 选 Browser/CLI/Hybrid | Python 内置 protected-surface / SSO / 4 级优先级表 |
| AC 覆盖 | LLM 生成矩阵 markdown | Python 编译 + projection |
| 报告格式 | 单一模板 markdown | JSON evidence + scorecard + gate 写入 |

→ **同一职能（QA），spec-kit-qa 用 364 行纯 markdown 完成；Beacon 用 77 行 SKILL.md + 4084 行 Python 完成**。
后者更可审计、更稳定，但前者更易释放 LLM 智能、迭代成本低 1~2 个数量级。

---

## 9. 微信《Web Access：一个 Skill，拉满 Agent 联网和浏览器能力》要点提炼

来源：`mp.weixin.qq.com/s/rps5YVB6TchT9npAaIWKCw`，作者关联仓库 `eze-is/web-access`。
**核心命题**：

> **Skill = Agent 策略哲学 + 最小完备工具集 + 必要的事实说明**

作者在 Web Access skill 设计中给出以下可复用的设计原则：

### 9.1 模型惯性 / 用词即隐性规则

- 用词本身就是隐性规则，会限制 Agent 判断空间。
- 例：主 Agent 即使在主 prompt 写"调研"，自动派给子 Agent 时也会改写成"搜索"，把子 Agent 锚定到 WebSearch 而非浏览器；而小红书是反爬平台，搜索/fetch 不可行。
- 设计意涵：**Skill prompt 必须显式纠正高频误锚词**，并补充事实边界。

### 9.2 通用 > 预设

- 预设方法（每站一个适配器）不可持续；通用 CDP / browser → "任何能打开的网站 Agent 都能用"。
- 以激发 *Agent Native 能力* 为核心，覆盖面"几乎没有上限"。

### 9.3 惰性知识补充

- 模型知识广，但任务中**未必第一时间被调用**。
- Skill 设计要找出"容易重复遗忘的边界"，针对必要信息直接补充事实说明。
- 对有最优路径的事情：直接指定（最小化必要提示 + 巧用 script/脚本文件）。
- 显式强调安全风险边界（CDP 可能交叉/关闭用户原有标签）。

### 9.4 Sub-agent 分治：写目标，不写步骤

- 联网任务常含多个独立目标（同时查 5 竞品、调研 50 网页）。
- 主 Agent 串行 → 中间内容涌入主上下文，token 膨胀，推理质量下降。
- 用宿主框架的 sub-agent 机制，**写目标不写步骤**；架构上所有 sub-agent 共享同一个 Chrome + CDP Proxy，各自创建后台 tab，通过不同 targetId 操作，无竞态。
- 关键陷阱：主→子 prompt 时主 Agent 默认会污染用词；Skill 要内嵌"对 sub-agent 的事实说明"，避免主自动派单时降级。

### 9.5 经验自动沉淀（Skill 内 learning loop）

- 每次操作完一个站点，Agent **按域名**沉淀访问策略：平台特征、有效 URL 模式、已知陷阱。
- 经验文件标"发现日期"，定位是 *"可能有效的提示"* 而非 *"保证正确的事实"*。
- 失败时自动**回退通用模式**并更新经验文件。
- 受益于 Skill 的**渐进式披露**：未用到的经验不占上下文。
- 作者构想"在线经验共享池"（A2A 社区），暂因法律风险未上线。

### 9.6 设计公式

> 激发 Agent 自主智力 ⇒ **策略哲学（怎么思考）+ 最小完备工具集（能做什么）+ 必要事实说明（容易遗忘的边界）**

---

## 10. 把 §8 §9 灌回 Beacon 的具体修订

将上述事实并入 §3 §4 后，Beacon 的 skill 设计应在原"SKILL.md 厚化 + 后台薄化"路线上再叠加 4 条补强原则：

### 10.1 显式纠正模型惯性

Beacon 各 skill SKILL.md 应内置"**易误锚词清单**"段，例如：

- `beacon-qa` 中 "测试" 容易锚到 *unit test 跑一遍*，应纠正为：先读 `test-case` 真相 → 选 Browser/CLI/Hybrid → 产 Acceptance Kit 四层 verdict。
- `beacon-implement` 中 "实现" 容易锚到 *直接动手写代码*，应纠正为：先读 frozen requirement → 编译 contract → 出 plan → 执行 → handoff QA。
- `beacon-prototype` 中 "原型" 容易锚到 *跑 React/HTML*，应纠正为：wireframe-freeze 闭环。

### 10.2 通用 > 预设

QA `protected-surface / SSO / runner 优先级表`目前是 Python 表驱动，符合 §9.2 反例。
建议：保留 Python 作为**事实补给**（runner 列表、SSO 标识），**判断逻辑搬到 SKILL.md**，让 LLM 拥有"再泛化"的判断权——遇到没在表里的协议（OAuth/OIDC/Cloudflare Access/Tailscale serve）也能照原则推理而非穷举。

### 10.3 引入 Skill 内经验沉淀（per-feature learning loop）

参考 §9.5，给 Beacon 各主流程 skill 加 *learning notes* 区：

- **存放位置**：`docs/beacon/<version>/.machine/learning/<skill>/<key>.md`，已存在 `Learning Plane Kernel`，对接现成内核即可。
- **写入触发**：QA 失败 / runner 切换 / change refreeze 完成时，由 LLM 输出"本次发现"短笔记，标注日期 + verdict。
- **读取**：下次 skill 加载时按 key 渐进披露（feature_slug / domain / runner）。
- **回退**：笔记失效时自动 fallback 通用流程并 mark stale。

这正好填补 §2 中"Beacon 的 *Learning Plane Kernel* 已经存在但默认没被各 skill SKILL.md 主动使用"的缺口。

### 10.4 子 Agent 分治写法（写目标不写步骤）

Beacon 当前 `implement` / `qa` 内部已有 team runtime / subagent / Ralph lane（被显式 *internal*），但**对外 SKILL.md 没有教用户/宿主 LLM 如何把任务分治**。建议：

- `using-beacon` 路由 skill 加一段 *Sub-task division pattern*：**写目标，不写步骤**；多 feature 并行 QA 时让宿主 LLM 自己开 sub-agent 而不是 Beacon Python 调度。
- 配套提供"主→子 prompt 防降级清单"：禁止改写动词（"调研→搜索"、"实现→编辑文件"、"验证→跑测试"）。

---

## 11. 重新校准的判断（结合两份外部资料）

| 维度 | 修订前判断 | 修订后判断 |
|---|---|---|
| LLM 能力释放 | "落后" | **"显著落后"**：spec-kit-qa 364 行纯 markdown vs Beacon ~4084 行 Python，量化差距 11×；Web Access skill 范式更激进（策略哲学 + 最小工具 + 事实说明） |
| 真相纪律 | "领先" | **"领先且必要"**：spec-kit-qa 把 verdict 完全交给 LLM 现场叙事，长期可审计性弱，Beacon 的 contract / scorecard / gate 不能放弃 |
| 工程化 | "领先" | **"领先但偏重"**：当前的偏重正是 Skill 内 learning loop + 子 Agent 分治可替代的层 |
| 上手速度 | "落后" | **"落后且可补"**：加 `quick` 双档 + `beacon-ask` + learning loop 即可大幅缓解 |
| 社区生态 | "落后" | 维持判断（Beacon 单仓自治；Spec Kit 已有 plugin marketplace + Antigravity 分支） |

**结论不变但论据加强**：Beacon 能力强悍 ✅，但 *能力释放路径* 当前确实压制了 LLM 的自主智力。修订路线应在"SKILL.md 厚化 + 后台薄化"基础上，叠加（10.1）反惯性词清单 +（10.2）通用判断原则 +（10.3）per-skill learning loop +（10.4）子 Agent 分治 prompt 范式。

---

## 12. 再加一条具体落地建议

为 §10.3 补充最小起步动作：

```bash
# 提议：给 beacon-qa 落地 learning loop 示意（不动 Python）
docs/beacon/<version>/.machine/learning/qa/<feature_slug>.md
docs/beacon/<version>/.machine/learning/qa/__index.md
```

`<feature_slug>.md` 内容契约（由 LLM 写、Python 仅校验 schema）：

```yaml
discovered_at: 2026-05-08
runner_attempted: playwright-cli (bare)
outcome: skip
reason: vercel_sso_redirect_no_session_bridge
fallback: web-access via attached chrome
verdict_layer_impact:
  - real-project-proof: blocked
note: "*.vercel.app 命中 SSO 拦截；下次直接走 attached chrome 优先级 1"
expires_after_n_days: 30
```

宿主 LLM 在下次加载 `beacon-qa` 时按 feature_slug / target host 渐进披露这条经验，避免再吃同一坑。完全符合 §9.5 的"经验作为可能有效的提示，而不是保证事实"。

