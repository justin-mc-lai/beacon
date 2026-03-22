# Beacon vs OpenSpec / GSD / GSD-2 对比与功能固化

> 目的：基于本地已拉取的开源项目快照，对 Beacon 的定位、边界和后续应固化的能力做一次正式收口。

---

## 1. 对比对象与依据

本次对比基于本地 `agent-skills/` 下的仓库快照：

| 项目 | 本地路径 | 参考快照 |
| --- | --- | --- |
| Beacon | `beacon/` | 当前工作树 |
| OpenSpec | `agent-skills/OpenSpec` | `afdca0d` |
| Get Shit Done | `agent-skills/get-shit-done` | `f12a400` |
| GSD-2 | `agent-skills/gsd-2` | `eeb35202` |

说明：
- 本文以项目 README / docs 的公开定位与当前本地快照为依据；
- 目标不是评判“谁更强”，而是明确 **Beacon 应该固化什么，不应该变成什么**。

---

## 2. 四个项目的核心定位

## 2.1 Beacon

Beacon 当前定位：

> **evidence-first delivery kernel**

核心特点：
- requirement materials 主链：think / user-story / prd / test-case
- implementation adapter：skill / implement
- review / verify / gate / release 闭环
- `docs/beacon/<version>/` 作为正式事实源

Beacon 的强项不在“自动跑一切”，而在：

> **把需求、实现证据、验收和版本交付收拢成一个可审计闭环。**

## 2.2 OpenSpec

OpenSpec 当前定位：

> **artifact-guided spec framework**

核心特点：
- change folder 驱动：proposal / specs / design / tasks
- `/opsx:propose -> /opsx:apply -> /opsx:archive`
- 适合“先达成变更共识，再进入实现”
- 非常强调 spec 变化、archive、delta spec 合并

它的核心价值是：

> **规范 change-level 规格化过程。**

## 2.3 GSD（Get Shit Done）

Get Shit Done v1 方向更像：

> **prompt-framework + context engineering + spec-driven development**

核心特点：
- 通过 prompts / skills / slash commands 驱动
- 强调 roadmap / requirements / state / verify
- 强调 context rot 问题
- 本质仍偏“prompt orchestration system”

它的核心价值是：

> **通过 prompt 体系和计划/验证机制提高 AI 编码稳定性。**

## 2.4 GSD-2

GSD-2 明确升级成：

> **真正的 coding-agent application**

核心特点：
- standalone CLI
- fresh session per task
- context injection
- state machine auto mode
- git worktree isolation
- cost / dashboard / crash recovery / stuck detection
- milestone / slice / task hierarchy

它的核心价值是：

> **把 agent runtime 本身产品化。**

---

## 3. 关键能力矩阵

| 维度 | Beacon | OpenSpec | GSD | GSD-2 |
| --- | --- | --- | --- | --- |
| 主抽象 | version delivery package | change artifact package | project/phase workflow | milestone/slice/task runtime |
| 核心单位 | feature / slice / release | proposal/spec/design/tasks | project / phase / plan | milestone / slice / task |
| 实现执行 | adapter-based (`implement`) | `/opsx:apply` | prompt-driven commands | full runtime-controlled automation |
| review / gate / release | 强 | 中 | 中 | 强，但偏 runtime 完成态 |
| 正式交付工件 | 很强 | 中 | 中 | 中 |
| 自动执行/runtime 控制 | 轻 | 轻 | 中 | 很强 |
| context/window 控制 | 弱 | 弱 | 中 | 很强 |
| git/worktree 自动化 | 弱 | 弱 | 中 | 很强 |
| Brownfield 支持 | 中 | 强 | 中 | 中 |
| 标准 skill 包 | 已补齐 | 多工具命令/skill 分发强 | 多 runtime prompt/skill 分发强 | CLI 为主 |
| 多服务 workspace 需求治理 | 强 | 中 | 中 | 中 |

---

## 4. Beacon 相对三者的真正优势

## 4.1 相对 OpenSpec

Beacon 更强的是：
- requirement + execution + review + gate + release 一体化
- 更像“版本交付包”，而不只是“change 包”
- 有 formal execution artifacts

OpenSpec 更强的是：
- 变更提案与 archive 流程非常清晰
- proposal/spec/design/tasks 的 artifact 心智更强
- brownfield change flow 更成熟

### 结论
Beacon 不该照搬 OpenSpec 的整套 change/archive 体系，
但应该吸收：

1. **artifact 明确命名**
2. **change/slice 级变更单元心智**
3. **用户先看清楚“要改什么”，再 implement**

## 4.2 相对 GSD（v1）

Beacon 更强的是：
- formal docs / delivery 结构更清晰
- execution / release / audit 语义更稳定

GSD 更强的是：
- 计划、验证、上下文工程的“操作感”
- 更重视 agent 行为一致性

### 结论
Beacon 应该吸收：

1. **计划与验证的流程刚性**
2. **context hygiene / dispatch hygiene**
3. **对“需求完成 ≠ 可交付”的明确提醒**

## 4.3 相对 GSD-2

Beacon 更强的是：
- requirement materials 与版本交付物料天然更清晰
- 对多服务 workspace 的 docs/governance 更友好
- 对 review / verify / gate / release 的正式语义更明确

GSD-2 更强的是：
- 真正的 runtime 产品化
- auto mode / crash recovery / stuck detection / worktree
- token / cost / dashboard / orchestration

### 结论
Beacon **不要**试图变成 GSD-2。

Beacon 应该承认：

> **GSD-2 是 runtime application；Beacon 是 delivery kernel。**

---

## 5. Beacon 现在最应该固化的能力

基于对比，Beacon 当前最该固化的是以下 7 个点。

## 5.1 固化一：Delivery Kernel 定位

必须持续明确：

```text
Beacon = requirement + implement contract + review + gate + release
```

而不是：

```text
Beacon = 通用 agent runtime / scheduler / tmux orchestrator
```

## 5.2 固化二：`skill` + `implement` 正式双命令面

v1.1.4 已经引入：
- `beacon skill`
- `beacon implement`

这必须被认为是正式主线，不再退回“implementation-command 占位参数时代”。

## 5.3 固化三：service-slice / implement-ready slice 模式

Beacon 后续必须明确支持：

- 单仓项目 → feature 直接 implement
- 多服务项目 → service-slice implement
- 非 git 内容项目 → content/theme slice implement

这点在 `slow-wp` / `rolo` 中已经验证有效。

## 5.4 固化四：execution / release 标准件

以下 execution 工件应视为 Beacon 最新交付标准核心：

```text
execution/
├── boundaries.md
├── config.json
├── source.json
├── git-alignment.json
├── change-impact.json
├── delivery-manifest.json
└── terminal.json
```

这正是 Beacon 区别于 OpenSpec / GSD 的关键资产。

## 5.5 固化五：标准 skill 包 + compatibility mirror

当前双层模型必须保留：

- `skills/beacon/` = canonical standard package
- 根 `SKILL.md` = compatibility mirror

这让 Beacon 同时满足：
- 标准 skill 开发规范
- 当前生态兼容

## 5.6 固化六：Cookbook + FAQ 支持层

已经补好的这三类文档，应视为 Beacon 的正式支持层：

- `latest-feature-usage-guide.md`
- `real-project-recipes.md`
- `faq-and-troubleshooting.md`

这让 Beacon 从“有能力”升级成“可被稳定使用”。

## 5.7 固化七：Runner 的实战化校准

已验证：
- OMX 需要走 `omx exec`
- 非 git 项目需要 `--skip-git-repo-check`

因此 Beacon 的 runner 不应停留在“概念设计”，而应持续维护为：

> **与真实外部工具 CLI 一致的 adapter。**

---

## 6. Beacon 不应该固化什么

## 6.1 不要固化为 GSD-2 式 runtime

不建议让 Beacon 内建：
- session runtime state machine
- token/cost dashboard
- worktree orchestration
- crash recovery supervisor
- parallel worker fleet

这些更像 GSD-2 的问题域。

## 6.2 不要把 OpenSpec 的 archive/change 流原样照搬

Beacon 当然可以学习 OpenSpec 的 artifact discipline，
但不应让自己被重构成：

```text
proposal/spec/design/tasks/archive first
```

Beacon 的主心智仍应是：

```text
version / feature / execution / release
```

## 6.3 不要把外部实现工具写死

现在虽然 OMX 是最佳默认，
但 Beacon 必须继续保留：

- adapter registry
- custom runner
- handoff runner

---

## 7. 对 Beacon 的功能固化建议

## P0（应立即视为正式）

1. `skill` / `implement` 主命令面
2. implementation marker / summary / review-spec 链路
3. OMX 内置 adapter 的 `exec` 模式
4. execution / release 工件标准
5. 标准 `skills/beacon/` 包

## P1（下一步可以继续增强）

1. `review spec --apply-writeback`
2. runner/project profile（single-repo / workspace / content-site）
3. delivery upgrade helper（把旧版本包补到最新 execution 标准）
4. implement-ready slice scaffolding

## P2（谨慎进入）

1. migration guide
2. richer OMC / gstack adapters
3. delivery / release report automation

---

## 8. 一句话总判断

### OpenSpec 更像
> **change-spec framework**

### GSD 更像
> **prompt-driven workflow system**

### GSD-2 更像
> **coding-agent runtime application**

### Beacon 最应该固化为
> **evidence-first delivery kernel with implementation adapters**

这就是 Beacon 最值得坚持的方向，也是它与这三个项目最有区分度、最该继续放大的能力。

