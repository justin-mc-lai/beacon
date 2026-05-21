# Beacon Support Skill Usage Guide (v1.4.8)

这份文档面向人类操作者。

目标只有一个：把常用 engineering support skills 的调用意图、边界、推荐 prompt，以及 v1.4.8 的 material writeback / gate 规则收成一页稳定参考。

## 使用前先记住

- 这些 skill 都是 support surface。
- 它们可以 `challenge`、`diagnose`、`explain`、`strengthen`、`route`。
- 它们不是 truth source，不是 gate source，也不是新的 lifecycle stage。
- 如果结论改变了冻结的 scope、promise 或 acceptance，必须回 `beacon-change` 或 `beacon-change-refreeze`。
- 如果 support finding 被采纳，必须转成 material update、release blocker 或 artifact update obligation；不能静默通过。

## v1.4.8 Material Closure 规则

v1.4.8 的核心变化是：support skill 的结论不再只停留在口头建议。

- `read_only_route_only`：只读分析，不更新 material，不产生 gate truth。
- `writeback_required`：结论被采纳后，必须写回 PRD、user-story、test-case、execution 或 release 文档。
- `execution_host_update_required`：涉及服务、分支、worktree、交付目录时，必须更新 execution host material。
- `obligation_opened`：暂时不能直接写回时，必须生成 artifact update obligation，并在 gate 阶段阻断到闭环。
- `truth_reopen_required`：改动影响冻结 scope、promise 或 acceptance 时，必须回 change/refreeze。
- `evidence_update_required`：结论影响验证时，必须补 QA evidence。

`beacon-toolkit-branch-governance` 的默认职责是更新交付服务、目标分支、worktree 策略、service branch map、technical review contract 与 git workflow material。

## 推荐调用方式

宿主侧优先按 skill 直接调用：

```text
$beacon:<skill-name> <your prompt>
```

例如：

```text
$beacon:beacon-source-driven 这轮判断必须强锚定 requirement、代码、接口和测试，标出哪些结论有 source，哪些只是推断。
```

## Skill 用法

| Skill | 什么时候用 | 不该什么时候用 | 推荐调用 / 推荐 prompt |
| --- | --- | --- | --- |
| `beacon-ceo-review` | 要从版本方向、promise 大小、scope 收缩/扩张、埋雷风险上挑战一轮 | 想把 review 结果直接当正式 truth writeback 或 release verdict | `$beacon:beacon-ceo-review 挑战下这版方案，重点看 promise 是否过大、scope 是否失控、有没有 buried landmine，以及是否会冲击 truth freeze 和 stage boundary。` |
| `beacon-context-engineering` | frozen truth 已有，但 working set 太大、太乱、互相打架，想先压缩最小上下文 | 借整理上下文偷偷改 frozen truth，或把它当正式 implement / qa | `$beacon:beacon-context-engineering 先不要改 truth，把这轮 implement/qa 真正需要保留的 requirement、evidence、风险边界收成最小 working set，并说明 keep / discard 理由。` |
| `beacon-source-driven` | 怕模型自由发挥，希望判断强锚定 requirement、代码、接口、测试、运行证据 | source 不足时脑补结论，并把 support review 当正式 QA/release | `$beacon:beacon-source-driven 这轮判断必须强锚定 requirement、代码、接口和测试，标出哪些结论有 source，哪些只是推断，并指出 source 不支持的 claim。` |
| `beacon-doubt-review` | 方案太顺了，怀疑已经自我合理化，想专门找 contradiction 和 evidence gap | 用怀疑姿态代替正式 QA/release，或在这里直接改 canonical truth | `$beacon:beacon-doubt-review 对这版方案做逆向挑战，指出 strongest claim、weakest proof、主要 contradiction、evidence gap 和下一跳。` |
| `beacon-security-review` | 涉及权限、外部输入、信任边界、敏感数据，想先看 trust boundary 和暴露面 | 还没说明暴露面就泛化成“以后再补”，或把它当 release gate verdict | `$beacon:beacon-security-review 先不要放行，帮我明确这条功能的 trust boundary、exposure surface、permission risk、input validation risk 和 data-handling 风险。` |
| `beacon-performance-review` | 功能处在 hot path、I/O 路径、循环重路径或规模敏感路径，想先看 latency / throughput / waste | 还没厘清 workload 就空谈性能，或把它当正式 QA 结论 | `$beacon:beacon-performance-review 从 hot path、waste source、latency risk、scale assumption 挑战这条方案或实现，指出不能忽略的成本和下一跳。` |
| `beacon-documentation-adr` | 某条架构/交付决策缺少“为什么”，需要轻量 ADR 或说明层补清楚 | 把 supporting doc 误当 canonical truth，或只复述实现不写 tradeoff | `$beacon:beacon-documentation-adr 给这条决策补一页轻量 ADR，重点写 decision、tradeoff、consequence，以及它给实现、维护、交付带来的实际含义。` |
| `beacon-debug-recovery` | implement / qa / release 卡住了，但不清楚该回需求、修代码、修验证还是修环境 | 把它直接当 `doctor` 或在 support 面结案，不回主链 | `$beacon:beacon-debug-recovery 这轮卡住了，先判断 blocker family 是 truth drift、execution gap、verification gap、environment issue 还是 mixed context，并给出最小修复路径和下一跳。` |

## 快速选择

- 方向太顺、scope/promise 可能有雷：`beacon-ceo-review`
- 上下文太乱、working set 太大：`beacon-context-engineering`
- 怕自由发挥、要强锚 source：`beacon-source-driven`
- 怀疑已经进入自洽幻觉：`beacon-doubt-review`
- 权限、输入、暴露面、敏感数据：`beacon-security-review`
- 热路径、延迟、吞吐、规模：`beacon-performance-review`
- 缺 ADR、缺 why、缺 tradeoff：`beacon-documentation-adr`
- 卡住了，但还没分清 blocker family：`beacon-debug-recovery`

## 意图路由边界

### 已支持的意图自动路由

以下能力已经明确收成 Beacon 的 host-visible route contract 或 stable human matching：

- `beacon` / `using-beacon`
- 按当前决策面把请求路由到 `truth / execution / verification-gate / support`
- `beacon-change-refreeze`
- 支持 `change 一键冻结`、`change refreeze`、`重新冻结`、`refreeze-chain`、`post-freeze requirement closure`
- 命中后应路由到既有机器路径：`beacon change ... --refreeze-chain`

这只是 route constitution，不等于自动执行完整主链。

### 只支持推荐路由

以下 support skill 当前支持“按意图推荐去哪个 skill”，但本质仍是 advisory/support route，不是自动进入主链执行：

- `beacon-ceo-review`
- `beacon-context-engineering`
- `beacon-source-driven`
- `beacon-doubt-review`
- `beacon-security-review`
- `beacon-performance-review`
- `beacon-documentation-adr`
- `beacon-debug-recovery`

这类 skill 的当前能力边界是：

- 能按意图命中到合适 support surface
- 能输出 route explanation 和下一跳
- 能把问题回送到 `beacon-change`、`beacon-implement`、`beacon-qa`、`beacon-release` 或 `beacon-doctor`
- 不能因为命中了 support intent，就自动替代主链执行

### 明确不自动执行

以下边界在 `v1.4.8` 是明确 fail-closed 的：

- support skill 命中后，不自动执行 `change`
- support skill 命中后，不自动执行 `implement`
- support skill 命中后，不自动执行 `qa`
- support skill 命中后，不自动执行 `release`
- `beacon-change-refreeze` 也不自动继续 `implement / qa / release`
- automation runtime 当前不承诺 autonomous `deep / refreeze / release` end-to-end closure

一句话区分：

> 现在已经支持“按意图路由到 skill”，但还没有把“命中意图后自动替你跑完整主链”升级成默认行为。

## 路由提醒

- challenge 后 scope / acceptance 要改：回 `beacon-change` 或 `beacon-change-refreeze`
- challenge 后只是实现质量问题：回 `beacon-implement`
- challenge 后只是证据闭环不够：回 `beacon-qa`
- challenge 后是 release blocker 判断：回 `beacon-release`
- challenge 后发现是环境或 surface 漂移：回 `beacon-doctor`
- challenge 后涉及服务、分支、worktree、交付目录：回 `beacon-toolkit-branch-governance`

## Gate 影响

v1.4.8 的 release/implement gate 应优先读 Markdown truth，并校验最小 machine state。

- PRD、user-story、test-case、research、execution、release 文档是冻结 truth。
- JSON 是 cache/state，不复制整篇 Markdown。
- implement 前必须显式存在交付服务、开发分支、worktree 策略和 technical review contract。
- strict release gate 只接受当前版本 release event，不允许 fallback 到历史版本 release memory。
- support finding 被接受但没有 material adoption route 时，应阻断为 `accepted_support_finding_not_adopted`。

## Source anchors

这份用法页基于以下 skill 合同收敛：

- `skills/beacon/beacon-ceo-review/SKILL.md`
- `skills/beacon/beacon-context-engineering/SKILL.md`
- `skills/beacon/beacon-source-driven/SKILL.md`
- `skills/beacon/beacon-doubt-review/SKILL.md`
- `skills/beacon/beacon-security-review/SKILL.md`
- `skills/beacon/beacon-performance-review/SKILL.md`
- `skills/beacon/beacon-documentation-adr/SKILL.md`
- `skills/beacon/beacon-debug-recovery/SKILL.md`
