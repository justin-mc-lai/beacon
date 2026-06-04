# Gstack 源码对照分析：Beacon v1.1.8 差距清单

## 分析范围

本分析直接基于本地 gstack 源码：

- `oss-sync/agents/agent-skills/gstack/README.md`
- `ARCHITECTURE.md`
- `BROWSER.md`
- `SKILL.md`
- `qa/SKILL.md`
- `setup-browser-cookies/SKILL.md`
- `browse/src/server.ts`
- `browse/src/browser-manager.ts`
- `browse/src/commands.ts`
- `browse/src/cookie-import-browser.ts`
- `browse/src/cookie-picker-routes.ts`
- `scripts/eval-watch.ts`
- `scripts/analytics.ts`

## 结论摘要

gstack 最值得 Beacon v1.1.8 借鉴的不是某一个命令，而是三层组合：

1. **持久化浏览器运行时**
2. **状态化 QA / 登录态治理**
3. **真实使用反馈回流工具自身迭代**

Beacon 当前在需求治理、生命周期和 machine-backed 交付真相方面更强；
gstack 当前在浏览器运行时、状态化验收和工具自反馈方面更成熟。

最优方向不是照搬，而是：

> 用 Beacon 的生命周期/物料治理能力，吸收 gstack 的浏览器、session、QA、反馈闭环设计。

---

## 差距矩阵

| 维度 | gstack 源码体现 | Beacon 当前现状 | 差距结论 | v1.1.8 建议 |
| --- | --- | --- | --- | --- |
| 持久化浏览器 daemon | `browse/src/server.ts`, `browse/src/browser-manager.ts`, `ARCHITECTURE.md` | Beacon 目前只有 runner 概念与 adapter，缺少正式持久浏览器运行时 | **高差距** | QA 设计线需要把“状态化浏览器面”定义成正式能力 |
| 命令/文档/校验同源 | `browse/src/commands.ts` 同时服务 runtime/doc/test | Beacon 有 command catalog，但 `auto-test/qa`、skill docs、执行语义仍未完全同源 | **中差距** | `qa` 命令迁移需统一 command catalog / skill docs / tests |
| `qa` 主入口心智 | `qa/SKILL.md` 把 QA 当成主工作流 | Beacon 仍以 `auto-test` 为主命令面 | **高差距** | `qa` 作为主入口，`auto-test` 做 alias |
| QA = 测试 + 修复 + 再验 | `qa/SKILL.md` 明确 test→fix→verify | Beacon 的 auto-test 更偏执行器/状态汇总 | **高差距** | v1.1.8 QA 设计应继续往 workflow-aware 闭环走 |
| 登录态导入/治理 | `setup-browser-cookies/SKILL.md`, `cookie-import-browser.ts`, `cookie-picker-routes.ts` | Beacon 尚无正式 session/login-state schema | **高差距** | 引入 `.beacon/qa/sessions/` 与 session manifest |
| 浏览器 runner 一等公民 | gstack 的 `/browse` 是基础设施，不是附属 runner | Beacon 只是把 browser-use / agent-browser 当 runner 选项 | **高差距** | 正式定义 `agent-browser` / `browser-use` runner 语义与证据输出 |
| 用户接管 handoff/resume | `handoff`, `resume`, `BROWSER.md` | Beacon 还没有正式定义这类人工接管恢复闭环 | **中差距** | 后续可在 QA/debug 设计中加 handoff/recover 语义 |
| snapshot/diff/annotated evidence | `snapshot -D/-a`, `diff`, `responsive` | Beacon prototype / qa 还未把这类浏览器证据变成一等物料 | **中差距** | prototype verify-impl 与 QA 证据应吸收 diff/screenshot/responsive 思路 |
| 实时反馈回流工具本身 | contributor mode / field report in `SKILL.md` | Beacon debug 目前还偏 prompt/run 事件 | **高差距** | 扩展 `.beacon/debug/` 作为产品迭代输入面 |
| feedback target 分类 | gstack 用 field report 区分工具问题 vs 用户项目问题 | Beacon 当前 debug 事件没有正式 target 分类 | **高差距** | 增加 `feedback_target` schema |
| issue/idea harvest | `scripts/analytics.ts`, eval/watch + contributor flow | Beacon 当前还没有从 debug 自动汇总 issue/idea | **高差距** | 新增 debug issue / idea harvest 设计 |
| 实时观测与评估 | `scripts/eval-watch.ts`, `scripts/analytics.ts` | Beacon 有 report/scoring，但缺少 agent 工具层的实时观测面 | **中差距** | debug/report 可吸收 eval/watch/analytics 思路 |
| 多角色 skill 软件工厂 | README + docs/skills.md | Beacon 已有生命周期与 team/native-team，但 skill 角色产品感偏弱 | **中差距** | help/doctor/skill routing 可以继续产品化 |
| 设计审计与 AI slop 控制 | `/design-review`, `/plan-design-review` | Beacon prototype 已开始补 aesthetic baseline，但还未形成默认强基线 | **中差距** | 保持 v1.1.8 原型审计线继续增强 |

---

## A. Beacon 已经比 gstack 更强的地方

### A1. 生命周期治理更强
Beacon 已有：
- draft / freeze / reopen / revision / accept
- machine-backed user-story / qa / execution
- item writeback / review gate / evidence gate

gstack 更像 workflow skill factory，但在正式 requirements lifecycle / revision truth 上不如 Beacon 系统化。

### A2. docs/beacon/<version>/ 的版本化交付面更强
Beacon 能把：
- PRD
- User Story
- QA
- Execution
- .machine

固定在版本线下管理，这比 gstack 更适合产品需求闭环。

### A3. profile / skill / orchestration 抽象更适合多项目交付
Beacon v1.1.7 已开始补：
- project profile
- project skill binding
- orchestration
- evidence gate

这让 Beacon 比 gstack 更容易成为“项目级交付中枢”。

---

## B. Beacon 当前最该补的高优先级缺口

### B1. `qa` 主入口迁移
优先级：P0

问题：
- 当前 `auto-test` 更像内部执行器名
- 用户真实心智是“做 QA / 做验收”

借鉴：
- gstack `/qa` 的产品心智

建议：
- `beacon qa` 主入口
- `beacon auto-test` alias

### B2. session / login-state 治理
优先级：P0

问题：
- 当前 Beacon 无法正式管理登录态
- 浏览器验收难以连续复用

借鉴：
- gstack `setup-browser-cookies`
- `cookie-import-browser.ts`
- `cookie-picker-routes.ts`

建议：
- `.beacon/qa/sessions/`
- cookies/storage-state/profile/session manifest

### B3. runtime debug 反馈回流 Beacon 本体
优先级：P0

问题：
- 当前 Beacon debug 偏路由/执行面
- 不足以作为版本迭代输入

借鉴：
- gstack contributor mode / field report

建议：
- `.beacon/debug/`
- `feedback_target`
- issue/idea harvest

### B4. 持久浏览器验收基础设施
优先级：P1

问题：
- 当前 Beacon runner 只是概念层组合
- 尚无正式 persistent browser surface

借鉴：
- gstack daemon model
- `browse/src/server.ts`
- `browse/src/browser-manager.ts`

建议：
- Beacon QA 设计上先定义 persistent browser runtime 抽象
- 代码实现可分阶段，不必 v1.1.8 一次做完

### B5. browser evidence 成为正式 gate input
优先级：P1

问题：
- Beacon 现有浏览器能力和 gate/evidence 之间还不够强绑定

借鉴：
- gstack 的 screenshot/diff/responsive/handoff/resume

建议：
- screenshot/video/network/session refs 都可正式回写 review/gate

---

## C. 不建议直接照搬的部分

### C1. 不建议把 Beacon 变成纯 skill factory
Beacon 的优势在 requirements lifecycle / versioned materials / machine truth。
不应为了像 gstack 一样“技能丰富”而弱化 versioned requirements 面。

### C2. 不建议把 Beacon Debug 退化成 contributor markdown 手工报告
gstack 的 field report 很有启发，但 Beacon 更适合：
- 结构化事件
- machine aggregation
- issue/idea auto-harvest

### C3. 不建议在 v1.1.8 直接承诺完整 daemon 实现
gstack 的浏览器 daemon 很成熟，但 Beacon v1.1.8 当前还是 design-only。
应先冻结：
- runtime 抽象
- session schema
- evidence contract
- workflow 语义

而不是过度承诺实现完成度。

---

## D. 对 v1.1.8 三条线的直接影响

### D1. 对 `prototype-baseline`
直接影响：
- 引入 browser diff / responsive / annotated screenshot 思路
- baseline evidence 不应只有静态工件，还应考虑可视对比证据

### D2. 对 `debug-runtime-feedback-loop`
直接影响：
- 明确 `.beacon/debug/` 目录
- 明确 `feedback_target`
- 明确高摩擦成功也要采集
- 明确 issue / idea harvest

### D3. 对 `qa-command-browser-acceptance`
直接影响：
- `qa` 主入口
- `auto-test` alias
- session/login-state schema
- `agent-browser` / `browser-use` 一等执行面
- requirement-delta-driven QA evolution

---

## 最终建议

如果按收益/风险排序，Beacon 应优先吸收 gstack 的能力顺序是：

1. **`qa` 主入口 + auto-test alias**
2. **登录态 / session 治理**
3. **runtime debug 反馈回流产品迭代**
4. **browser evidence → gate/review 正式证据**
5. **persistent browser runtime 抽象**
6. **prototype verify-impl 吸收 diff/responsive 视觉证据思路**

一句话总结：

> gstack 给 Beacon 的最大启发，不是多几个 skill，而是把“状态化执行”和“反馈回流自身”做成正式基础设施。
