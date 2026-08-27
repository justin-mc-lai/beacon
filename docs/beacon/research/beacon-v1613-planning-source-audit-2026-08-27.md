# Research: Beacon v1.6.13 规划源审计（2026-08-27）—— 7 优化方向 × OSS 能力对照 × skill 文案规范

**日期**：2026-08-27
**用途**：v1.6.13 规划输入（planner support_advisory，非 requirement truth）。
**输入**：
- 7 优化方向提案：`docs/beacon/research/beacon-optimization-proposal-2026-08-27.md`
- OSS 能力对照（子代理调研，锚定 oss-sync 源码）：本文件 §2
- beacon skill 文案规范审计（子代理调研，锚定 .claude/skills/beacon-* 源码）：本文件 §3
- 用户原则：beacon 交付第一，frozen truth 必须普通人能看懂（人话/eli5）。
**模式**：`pln-source`（public_id=`plan`）

---

## 1. v1.6.13 七优化方向清单

| # | 方向 | 一句话（人话） | 初始批次 |
|---|---|---|---|
| D1 | 验证前置 + 功能地图 | 让 agent 自己能打开产品、找到功能、复现 bug 并验证修复，人不用盯着每一步 | 2 |
| D2 | 预算/配额内核 | 给长任务记账：钱（回合/花费）花在哪、何时扣一次，防空转烧钱 | 1 |
| D3 | 失败模式 → skill 回归库 | 把 agent 反复犯的错写成可测试的用例，配合多模型交叉打分，做交付前审查输入 | 1 |
| D4 | 审查护栏 | 审阅子 agent 不能再派子 agent（防套娃），跨 skill 调用走单一入口 | 2 |
| D5 | 证据闭环防假完成 | 证据引用带内容指纹，证据一变就 fail-closed，杜绝「文档说完成其实已变」 | 2 |
| D6 | 多宿主 parity | 新 AI 工具（Zed 等）接入时，beacon 的 7 个 skill 保持一致可用 | 3 |
| D7 | auto-merge 边界 | 让 agent 自动合入 PR、人类退到主干复核 —— 与「release 必须人点头」冲突，倾向不采纳 | — |

## 2. OSS 能力对照结果（子代理调研，锚定 oss-sync 源码）

### 证据链最完整（可直接蒸馏）
- **D2 预算内核** ★★★：`loopx` 提供完整事务账本 —— `control_plane/turn_transaction_contract.json`（事务相位：host_execute→validation→durable_writeback→**quota_spend**→scheduler_ack，spend 严格排在校验+写回之后）、`quota/spend_commit.ts`（CAS 幂等 spend，quiet skip 不扣）、`quota/slot_accounting.py:708-726`（not ok / 非 delivery_completion 一律不扣）、`quota/settlement_validation.py`（completion 校验必须先 durably 完成）。→ beacon 可照搬「spend 时序约束 + CAS 幂等」最小内核。
- **D3 失败模式回归** ★★★：`bmad` `claims-check.md`（spec 自述当证词、独立 reviewer 逐条 falsify、kind/confidence 字段）+ `step-04-review.md`（coordinator 重判 severity、triage 到 intent_gap/bad_spec/patch/defer）+ `review-prompts/verification-gap.md`（Never assert what you did not verify）；`ECC` `eval-harness/SKILL.md`（pass@k 能力回归）+ `agent-eval/SKILL.md`（跨模型对照）+ `council-multi-model/SKILL.md`（异构审查、诚实标注 cross-provider）。注意：跨模型打分是批判式意见（user decides），非自动分数——beacon 若做自动打分需自证。

### 证据充分（可参考）
- **D4 审查护栏** ★★☆：`bmad` `core-skills/bmad-review/SKILL.md` 现成约束句「Do not invoke any skill, and do not spawn subagents of your own — you are the reviewer」；`mattpocock-skills` `ask-matt` 单一 router +「router 撒谎即错」验收标准；`ralphex` review 固定 5 叶子、外置循环。语义注意：禁止的是**递归**，不是并行。
- **D6 多宿主 parity** ★★☆：`openspec` 走共享 `.agents/skills` 目录（Zed 通过 `.agents` 接入，`init.ts:772` sharedAgentsTargets），成本最低；`superpowers` 用 action 抽象 + per-host 工具映射表覆盖 11 宿主。→ beacon 走 `.agents` 共享目录路线可免每宿主安装层。

### 证据弱（建议降级或仅参考）
- **D1 功能地图** ★☆☆：enabler 三件套齐全（`deer-flow` sandbox:execute RBAC 授权、checkpoint 持久 run；`mempalace` 内容寻址写保护 sha256 id），但**「feature map 路由」在所列镜像中零实现，需自研**。
- **D5 证据闭环** ★☆☆：`gstack` 只有散点范式（`diagram-render-drift.test.ts` 内容 hash 绑定、`staging-guard.ts` fail-closed、`egress-receipt.ts` ledger、`tracker-guard.ts` 信封），无完整「evidence ref=path+指纹」账本。→ 建议降级为「先做最小绑定：evidence ref 落盘记 sha256、读取时校验」。

### D7 证据与 beacon 判断一致（不采纳）
`gstack` `land-and-deploy` merge 前人类显式三选；`loopx` 把 merge 定义为 `user_gate` todo（`pr_gate_reconcile.py:29-40`，`write_performed: False`）；`deer-flow` 到「创建 PR」为止。**第三方无「agent 自动合入、人类退到 main」实现**——与 beacon「release 人类 gate 不可覆盖」一致。

## 3. beacon skill 文案规范审计（子代理调研，锚定 .claude/skills/beacon-* 源码）

### 汇总：骨架统一（A/D 过），边界哲学基本守住（B 除 1 处），人话只达标 1 个（C），术语有漂移（E）

| skill | A 结构 | B 边界优先 | C 人话 | D 渐进披露 | E 术语一致 |
|---|:---:|:---:|:---:|:---:|:---:|
| design | ✓ | ✓ | △ | ✓ | △ |
| goal | ✓ | ✗ | △ | ✓ | ✓ |
| implement | ✓ | ✓ | △ | ✓ | ✓ |
| plan | ✓ | ✓ | △ | ✓ | ✓ |
| qa | ✓ | ✓ | △ | ✓ | ✓ |
| release | ✓ | ✓ | △ | ✓ | ✓ |
| truth | ✓ | ✓ | ✓ | ✓ | ✗ |

### 高价值发现（F1-F5）
- **F1 loop-goal 是唯一「操作剧本」式主体**（`beacon-goal/references/modes/loop-goal.md`）：把实现级子步骤写成模型指令。属 §6.1 强 gate 可豁免场景，但豁免理由未写。改法：正文只保留「怎么判断 route 到哪个 stage」，子步骤交给 runtime。
- **F2 mode 文件版本锚点陈旧且自相矛盾**：多个 mode 写「v1.5.2 / v1.4.3」，运行时目标 v1.6.12。→ 版本锚点抽到单一 source，mode 里留相对引用。
- **F3 mode_id 前缀体系断裂**：`truth-review` 无 `eval-` 前缀（plan 有 `pln-*`、qa/release 有 `eval-*`）；`gen-prototype` 游离于 `gen-design-*`。
- **F4 人话交付只约束 truth，其余 6 个 skill 无对应契约**：truth 有 L0 `## 人话`/`## Plain language` 硬契约（`gen-truth.md:123,131,406`）+ humanizer 边界，但 7 个 SKILL.md 的 Output contract 全无「普通人能看懂」要求——**AGENTS.md 用户规则在非 truth skill 未落地**。改法：共享 Output contract 加必填「plain-language delivery summary」。
- **F5 共享块靠复制粘贴，已出现复制式 bug**：`pln-brainstorm.md:33` 三个同名 `beacon-gen-truth`；`gen-truth.md:44` 旧版自指残留。→ 共享 preamble/GIT_ADMISSION 抽单文件由 mode 引用。

### 做得好、应推广（3 条）
1. truth 的 L0 人话契约 + Humanizer 边界（普通用户可读 + 不改机器字段）。
2. `eval-qa.md:151-181` protected live surface 判断（先判环境/鉴权 vs 产品回归，stop early 用 skip/blocked 而非 timeout 掩成 fail）。
3. plan 的 Underspec still emit（缺 OSS/version 仍强制输出契约 + 澄清问题）。

## 4. 综合结论与 v1.6.13 路由建议

1. **批次 1（P0）**：D2 预算内核（loopx 可整块蒸馏）+ D3 失败模式回归库（bmad×ECC 拼装）+ **skill 文案规范化**（F2/F4/F5 复制维护 bug + F4 人话契约推广——直接兑现「truth 必须人话」用户原则，成本低、收益全局）。
2. **批次 2（P1）**：D1 功能地图（自研，enabler 借鉴 deer-flow/mempalace）+ D5 证据闭环（最小 sha256 绑定版）+ D4 审查护栏（bmad-review 约束句直接入 rubric）。
3. **批次 3（P2）**：D6 多宿主 parity（走 `.agents` 共享目录）。
4. **D7 不采纳**（第三方证据 + beacon 边界双重确认）。
5. **F1/F3** 随 skill 文案规范批次一并处理（loop-goal 补豁免理由、mode_id 前缀统一）。

**recommended_next_harness**：`plan`（进入 pln-program 模式，把批次 1 拆成 v1.6.13 的 program/lake 计划）。
