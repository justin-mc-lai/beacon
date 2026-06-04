# Beacon Human Skill Reference (v1.4.7)

这份文档面向人类操作者。

目标只有一个：当你准备在宿主里直接调用 Beacon skill 时，能快速判断：

- 什么时候用
- 什么时候不该用
- 一句提示词应该怎么写

## 使用原则

- 先按决策面选 skill，不按名字熟不熟来选。
- 要改承诺、范围、acceptance，回 truth 主链。
- support surface 只负责 challenge、收敛、诊断、补锚定、补说明，不直接替代 `implement`、`qa`、`release`。
- 如果 support 结论改变了冻结 truth，必须回 `beacon-change`。

## 快速路由

| 你现在的真实诉求 | 应优先用 |
| --- | --- |
| 需求、范围、承诺、acceptance 还没收口 | `beacon-prd` / `beacon-user-story` / `beacon-test-case` / `beacon-change` |
| 已有冻结 truth，准备动实现 | `beacon-implement` |
| 已实现，准备验证、验收、放行 | `beacon-qa` / `beacon-release` |
| 只是想 challenge、诊断、补锚定、补说明、整理上下文 | support skills |

## 主链 skills

| Skill | 何时用 | 不该何时用 | 推荐提示词模板 |
| --- | --- | --- | --- |
| `beacon-prd` | 问题定义、目标、边界、承诺面还不清楚 | 已经只是代码修复或 QA 问题 | `$beacon:beacon-prd 把这个需求收成 PRD，明确目标、边界、非目标和承诺面。` |
| `beacon-user-story` | 已有 PRD，但角色目标、场景、AC 不够可执行 | 你要改实现，不是补 acceptance | `$beacon:beacon-user-story 基于当前 PRD 收敛 user stories 和 acceptance criteria。` |
| `beacon-test-case` | 需要把 acceptance 编译成测试场景和 coverage contract | 只是做自由探索，不是测试闭环 | `$beacon:beacon-test-case 把当前 acceptance 展开成 test cases，并标出覆盖缺口。` |
| `beacon-prototype` | 这条功能需要先出交互/页面/原型闭环 | 已经确认不用原型，直接进入实现 | `$beacon:beacon-prototype 先给这条需求产出原型与交互闭环，保持和 frozen truth 对齐。` |
| `beacon-change` | 冻结后要改 scope、承诺、acceptance、truth package | 只是 challenge 或说明，不是真的改 truth | `$beacon:beacon-change 这轮需要正式改冻结 truth，请承认 drift 并回填 requirement package。` |
| `beacon-implement` | truth 已稳定，进入正式实现 | 需求还没冻结，或只是 support 诊断 | `$beacon:beacon-implement 基于当前 frozen truth 开始实现，保持改动外科手术式。` |
| `beacon-qa` | 需要正式验收 feature、补证据、判断是否 pass | 只是做 support 级 challenge，不是正式 QA | `$beacon:beacon-qa 对这条 feature 做正式 QA 验收，按 acceptance 和 test-case 出结论。` |
| `beacon-release` | 需要 release verdict、放行材料、release 风险判断 | 还没完成 QA，就想直接放行 | `$beacon:beacon-release 对这条版本线做 release readiness 判断，给出 verdict 和 blocker。` |

## 常用 support skills

| Skill | 何时用 | 不该何时用 | 推荐提示词模板 |
| --- | --- | --- | --- |
| `beacon-brainstorm` | 还在收敛 framing、方向、候选方案 | 把 brainstorm 直接当正式 requirement | `$beacon:beacon-brainstorm 先头暴这个方向，收敛 options、判断框架和关键 tradeoff。` |
| `beacon-ceo-review` | 要从版本方向、产品收敛、边界扩张风险上挑战一轮 | 想把 CEO review 当最终 requirement truth | `$beacon:beacon-ceo-review 挑战下这版演进，重点看方向是否变重、边界是否失控。` |
| `beacon-design-review` | 需要从 UI/UX/交互质量角度挑战或审视 | 你要改 requirement truth，不是做设计 review | `$beacon:beacon-design-review 从 UI、UX、信息密度和交互闭环挑战这条能力。` |
| `beacon-deep` | 需要更重的结构化分析、复杂风险拆解、深度 challenge | 把 deep 当 release gate 本身 | `$beacon:beacon-deep 对这条复杂问题做深度分析，给出结构化风险、约束和下一跳。` |
| `beacon-help` | 不知道下一步该走哪个面 | 已明确该进 implement/qa/release | `$beacon:beacon-help 基于当前状态判断下一步应该走哪个 Beacon surface。` |
| `beacon-status` | 想看当前版本线/材料/状态/阻断概览 | 需要正式修复或改 truth | `$beacon:beacon-status 汇总当前版本线、阻断、下一步和关键材料。` |
| `beacon-doctor` | 上下文、安装、surface、runtime、docs 有漂移或损坏 | 把 doctor 当常驻主流程步骤 | `$beacon:beacon-doctor 检查并修复当前项目的 context / materials / agent surface 漂移。` |
| `beacon-archive` | 需要归档历史 truth、旧版本或完成线 | 当前还在活跃交付，不是归档时机 | `$beacon:beacon-archive 把这条已完成版本线归档，并保持当前线干净。` |

## v1.4.7 新增 support skills

| Skill | 何时用 | 不该何时用 | 推荐提示词模板 |
| --- | --- | --- | --- |
| `beacon-context-engineering` | 材料很多，但本轮真正需要的 working set 不清楚 | 借它偷偷改 frozen truth | `$beacon:beacon-context-engineering 先不要改 truth，把这轮 implement 真正需要保留的 requirement、证据、风险边界收成最小 working set。` |
| `beacon-debug-recovery` | 实现或 QA 卡住了，但不清楚该回需求、修代码、修验证还是修环境 | 直接在这里结案，不回主链 | `$beacon:beacon-debug-recovery 这轮卡住了，先判断 blocker family，并给出最小修复路径和下一跳。` |
| `beacon-documentation-adr` | 架构或交付决策需要一页轻量 ADR/说明层来解释为什么 | 把 supporting doc 误当 canonical truth | `$beacon:beacon-documentation-adr 给这条决策补一页轻量 ADR，重点写 decision、tradeoff、consequence。` |
| `beacon-doubt-review` | 方案太顺了，怀疑已经自我合理化，想找证据缺口 | 用怀疑姿态替代正式 QA/release gate | `$beacon:beacon-doubt-review 对这版方案做逆向挑战，指出 strongest claim、weakest proof、evidence gap 和下一跳。` |
| `beacon-performance-review` | 功能跑在热路径上，担心延迟、吞吐、资源浪费、规模压力 | 还没厘清 workload，就空谈性能 | `$beacon:beacon-performance-review 从 hot path、waste source、scale assumption 挑战这条实现或方案。` |
| `beacon-security-review` | 涉及权限、外部输入、信任边界、敏感数据 | 还没区分暴露面，就把安全问题泛化成“以后再说” | `$beacon:beacon-security-review 先不要放行，帮我明确 trust boundary、exposure surface、validation risk。` |
| `beacon-source-driven` | 怕模型自由发挥，希望强锚定 requirement、代码、接口、测试、运行证据 | source 不足时擅自脑补并当事实写回 | `$beacon:beacon-source-driven 这轮判断必须强锚定 requirement、代码、接口和测试，标出哪些结论有 source，哪些只是推断。` |
| `beacon-toolkit-automation` | 初始化或维护 project-local automation scaffold、queue、summary schema、executor tier | 还没做 automation，就直接跳进 release 讨论 | `$beacon:beacon-toolkit-automation 给这个项目初始化或检查 automation queue、summary schema 和 executor tier。` |

## 一句收敛

> 改 truth 回主链，做实现走 `implement`，做验收走 `qa/release`，其余 challenge、诊断、补锚定、补说明都走 support surface，但 support 不能替代 truth 和 gate。
