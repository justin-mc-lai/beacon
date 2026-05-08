# Beacon 全局约束

## 目标

把以下要求提升为 Beacon 的跨版本全局约束，而不是某个版本或某个 feature 的私有偏好：

> 人类极简心智工作流继续沿袭；对外命令面极度克制；复杂度默认留在机器内部，不让人类承担。

这份文档的地位高于任何单个 `docs/beacon/vX.Y.Z/` 版本包。

## 人类主面约束

### 1. 人类主流程收敛为 6 段主链 + 条件 prototype 层

无论 `team`、`subagent`、`ralph` 或宿主原生能力如何增强，人类主流程都必须保持为：

```text
prd
→ user-story
→ test-case
→ implement
→ qa
→ release
```

其中：

- `prototype` 不是默认必经主链，而是条件触发层
- 只有在 feature 实际存在 UX/UI surface、页面/状态/导航/交互 handoff 需求时，才要求进入：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release
```

- `prototype` 只表示 `requirement-driven wireframe freeze`
- 它仍位于 `test-case` 与 `implement` 之间
- 它不承担高保真视觉稿、最终前端页面或设计系统定稿职责
- 对纯后端、纯契约、纯治理、无实际 UX/UI handoff 的 feature，不应强制插入 `prototype`

这是 Beacon 的人类主心智面，不得因内部能力增强而继续扩张。

### 2. 人类辅助面继续保持极简

辅助命令仍应收敛为：

- `help`
- `status`
- `doctor`
- `archive`

其中：

- `archive` 是 support command，不是新的 lifecycle stage
- 它负责历史 truth 退出当前 delivery plane 的正式治理动作

它们是支持面，不是新主流程。

## 对外命令面约束

### 3. 不新增新的公开一级主命令

Beacon 不得因为原生 team/subagent 能力增强而新增面向人类的公开一级主命令来暴露：

- `team`
- `subagent`
- `runtime-readiness`
- `delegation-readiness`
- 宿主差异选择

### 4. `implement` 与 `qa` 仍是唯一执行入口

对人类而言：

- `implement` 仍是唯一实现入口
- `qa` 仍是唯一验收入口

team/subagent 只能作为内部执行面存在，不应取代这两个主入口。

## 机器内部复杂度约束

### 5. team/subagent/precheck 默认留在机器内部

以下复杂度都必须默认由 Beacon 机器内部消化：

- 宿主原生 team/subagent 调起
- `runtime-readiness precheck`
- `delegation-readiness precheck`
- team lane 拆解
- verifier / repair-handoff-writer / implementation-architect 等内部角色协作
- Ralph 闭环 routing

人类不应被要求长期理解这些细节。

### 6. 预检查必须内嵌到 `implement` / `qa`

两段预检查必须默认作为：

- `implement`
- `qa`

内部前置动作执行。

`doctor` 只作为：

- 显式诊断
- 阻断修复
- 深入排查

而不是人类主流程的新增常驻步骤。

## Requirement Closure 全局约束

### 7. `prd → user-story → test-case → acceptance` 是 Beacon 立项根本

Beacon 的立项根本，不只是存在一条 6 段主流程，而是要求前 3 段形成正式 requirement truth，并支撑后续 acceptance：

```text
prd
→ user-story
→ test-case
→ acceptance
```

全局规则：

- `prd` 定义问题、目标、边界与承诺面
- `user-story` 把 `prd` 编译成可执行的角色目标与 acceptance criteria
- `test-case` 把 `user-story` 编译成可验收场景
- `implement / qa / release` 只能沿这条链闭环，不得反向改写 requirement truth

规则：

> Beacon 的实现、验收、发布，必须回到 `prd / user-story / test-case` 的统一 truth，而不是由 runtime 状态、代理模式或局部完成信号单独定义“算不算完成”。

### 8. 所有 implement lane 都必须绑定同一份 requirement truth

无论后续实现通过：

- `implement single`
- `implement team`
- `implement ralph`

哪一条 lane 推进，它们都必须：

- 绑定同一份 `prd`
- 绑定同一份 `user-story`
- 绑定同一份 `test-case`
- 接受同一套 acceptance / gate 判断

禁止出现：

- `single` 按 PRD 验收
- `team` 按 agent 完成度验收
- `ralph` 按 round 结束验收

规则：

> runtime mode 只能改变执行形态，不能改变 requirement truth。

### 9. requirement traceability 必须能被 review-spec / gate 检查

Beacon 默认必须支持把下列对齐关系做成正式检查对象：

- `PRD promised surfaces`
- `User Story acceptance criteria`
- `Test Case acceptance coverage`
- `Implementation shipped surfaces`
- `QA / release gate verdict`

如果这条链断裂，则必须：

- 阻断
- 或明确 downgrade 并留下批准记录

而不能静默滑过。

### 9A. `prototype` 在被触发时必须是闭环推理产物，不得退化为静态模板说明

当且仅当 feature 具备实际 UX/UI surface、页面/状态/导航/交互 handoff 需求时，`prototype` 才应被触发。

一旦触发，`prototype` 可以保留结构化模板骨架，但页面内容必须基于真实：

- `prd`
- `user-story`
- `test-case`

做闭环推理后生成，至少覆盖：

- 页面状态流转（含异常回退）
- 页面跳转关系
- 页面组件契约（职责/数据来源/交互）
- 与 AC/TC 的映射关系

规则：

> 模板只负责固定结构，语义内容必须由 requirement truth 推导并通过校验，不能只做静态说明填空。

### 9B. Beacon 多写入点必须采用 canonical 驱动与事务一致提交

Beacon 在原型与运行态相关能力中，默认存在多写入点：

1. human-readable sink（面向人类审核）
2. machine-readable sink（面向机器消费）
3. runtime projection sink（SQLite/投影索引）

全局约束：

- canonical envelope 是唯一提交源，不允许多源并写。
- 所有 sink 必须由 canonical 单向投影生成，不允许 human 文档反向驱动 machine 真相。

### 9C. 版本表面治理（Version Surface Governance）

Beacon 源码中的所有版本号变量（Versioned Strings）必须遵循“单真值、多投影”原则：

- `beacon/version-truth.json` 是全仓版本号的唯一真值来源（Canonical Release Manifest）。
- 严禁手动修改 `__init__.py`、`SKILL.md`、`metadata.json` 或 `.trae` 规则文件中的版本号。
- 所有的版本变更必须首先在 Manifest 中修改，然后通过投影机制（如 `sync-version-surfaces`）同步到各受管表面。
- `release check` 和 `gate check release` 必须强制校验版本漂移，并在发现不一致时阻断发布流程（Fail-Closed）。
- 提交流程必须遵循：
  - `prepare -> validate -> commit -> publish -> verify`
- 任一 sink 写入失败：
  - 必须整体回滚
  - 或标记事务失败并阻断 freeze/release

### 9C. 跨面 anti-drift 一致性必须可审计

同一批次跨写入点必须共享一致事务元数据，至少包含：

- `source_hash`
- `projection_seq`
- `transaction_id`
- `committed_at`
- `sink_checksums`

规则：

- `status/review/doctor/gate/release` 必须可检查并报告跨面一致性状态。
- 发现 human/machine/sqlite 任一面不一致时，不得判定 `freeze pass` 或 `release pass`。
- 任何“只在单面修补、未重建全体投影”的行为都视为潜在漂移。

## 宿主约束

### 10. 宿主上下文必须唯一

Beacon 只讨论：

- Beacon 作为 skill 运行在 Codex 中
- Beacon 作为 skill 运行在 Claude 中

不讨论：

- 同一轮执行里在 Codex / Claude / 其他运行时之间做选择
- Beacon 自己桥接多个外部运行时

规则：

> 当前宿主是谁，就只判断当前宿主是否支持原生 subagent/team 能力。

### 11. 外部运行时只可作为调研借鉴，不能默认进入主叙事

像 `omx` 这样的外部运行时，可以作为研究样本，用于借鉴：

- launcher / adapter 检测
- dry-run 优先
- artifact / stdout / stderr / command 可写检查

但不得自动升级为 Beacon 的跨版本正式主叙事。

## 默认行为边界约束

### 12. 外部规范仓库只可借鉴吸收，不形成默认依赖

像 `forrestchang/andrej-karpathy-skills` 这类开源行为规范仓库，只能作为 Beacon 的研究与提炼来源。

正确做法是：

- 借鉴其中可迁移的边界原则
- 吸收到 Beacon 自己的 `global-boundaries`
- 通过 Beacon 自己的 docs / tests / doctor / context setup 落地

禁止做法：

- 要求默认安装外部 skill 仓库
- 要求默认安装外部 plugin
- 要求运行时调用外部 skill 才能满足 Beacon 默认规范
- 把外部规范仓库升级为 Beacon 的正式主依赖

### 13. 默认行为边界必须同时约束 Beacon 自身与目标项目

这份 `global-boundaries` 不只约束 Beacon 源码仓自身，也约束接入 Beacon 的目标项目。

规则：

- Beacon 自身的源码开发、命令设计、文档演进必须遵守这份边界
- 目标项目在接入 Beacon 后，其 `AGENTS.md` / `CLAUDE.md` managed context 也必须继承这份边界
- 目标项目不应绕过这份边界，单独引入更宽的默认主叙事

也就是说：

> Beacon 的极简心智面与默认行为边界，既是 Beacon 自己的开发规范，也是目标项目的默认继承规范。

### 14. 默认行为边界必须包含四类轻量原则

在不扩张人类主流程的前提下，Beacon 默认应吸收以下四类行为边界：

1. **显式假设与歧义管理**
   - 不清楚时不得静默选择一种解释直接执行
   - 多种解释并存时必须显式记录假设、取舍或阻断原因
   - 关键需求不明时，应回到 `prd / user-story` 收口，而不是直接进入实现
2. **简单优先**
   - 默认采用最小正确改动
   - 不为单次需求新增 speculative abstraction、额外配置或未请求的未来扩展
3. **外科手术式改动**
   - 只改与当前请求、冻结材料或当前闭环直接相关的范围
   - 不做 drive-by refactor
   - 不删除无关代码、注释或格式
   - 只清理自己这次改动制造的 orphan
4. **目标驱动验证闭环**
   - 非平凡任务必须绑定成功标准与验证信号
   - bug fix 要有复现或验证证据
   - feature 要有 acceptance/test 映射
   - refactor 要有 before/after 验证

### 15. trivial task 可以轻量处理，但不能越界

Beacon 默认规范允许对低风险 trivial task 做轻量处理，例如：

- 明显 typo
- 单行文案修改
- 明确无歧义的小范围修正

但即使是 trivial task，也仍然必须满足：

- 不触碰无关文件
- 不顺手重构相邻代码
- 不因为“简单”而扩大改动范围

规则：

> 轻量不等于随意；简单任务可以少流程，但不能破坏边界。

## 输出约束

### 16. 人类输出必须极简

对人类的默认输出必须控制为：

- 一句当前状态
- 一句阻断原因
- 一个推荐下一步
- 一个 fallback 或修复命令

### 17. 机器输出必须完整

对机器和审计面必须保留完整输出：

- reason codes
- runtime / delegation 细节
- evidence refs
- diagnostics
- artifact paths

规则：

> 复杂度不能消失，但必须被吸收到机器面，而不是倾倒给人类。

## 禁止事项

以下做法应被视为违背 Beacon 全局约束：

1. 因 subagent 能力增强而新增新的公开一级主命令
2. 让用户手动选择 Codex / Claude / 其他运行时
3. 让用户在主流程中显式操作 precheck
4. 把 team/subagent 细节默认暴露为人类长期心智负担
5. 把 Beacon 演进成多运行时桥接调度器
6. 把外部行为规范仓库或 plugin 变成 Beacon 默认安装前提
7. 让目标项目在接入 Beacon 后默认绕过这份全局边界
8. 在没有 canonical 事务提交的情况下直接多点写入 human/machine/sqlite
9. 允许 human 文档与 machine/runtime 索引出现同批次语义不一致却继续 freeze/release
10. 把 `prototype` 输出退化为只含静态模板说明且缺失状态流/组件契约/AC-TC 映射
