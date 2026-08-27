# Research: Beacon 优化方向提案（2026-08-27）—— X 方法论 × 第三方 spec 最新能力 × 现有能力盘点

**日期**：2026-08-27
**目的**：在移除 Trellis、回归 beacon 自身子迭代之后，把三类输入交叉成一组**新的、beacon 原生口径**的优化方向：
1. **X 方法论**（Cursor 工程师 Lauren Tan @poteto 的一线 agent coding 工作法）：`docs/beacon/research/beacon-agent-coding-methodology-cursor-poteto-2026-08.md`
2. **第三方 spec 开源库最新能力**（本日 oss-sync 同步提取）：`docs/beacon/research/beacon-oss-reference-sync-2026-08-26.md`
3. **beacon 现有能力盘点与既有缺口**：`beacon-maturity-remediation-roadmap.md`、`beacon-loopx-capability-analysis-2026-08.md`、`beacon-longrun-stability-analysis-2026-08.md`

**边界**：所有方向必须满足 global-boundaries——主链（prd→user-story→test-case→implement→qa→release）不扩张；support surface 有界；evidence-first / fail-closed；不新增命令面；learning 不定义 truth。

---

## 1. 现状锚点（一句话盘点）

- **beacon 强项**：requirement kernel、evidence kernel、QA/gate 逻辑、versioned docs package、多 surface 材质化。
- **既有缺口**（此前研究已识别）：
  - 长程 S4 预算/spend、S7 并发所有权（longrun-stability）
  - LoopX P0 借入清单：quota should-run、todo 所有权、user gate 投影、spend-once、ready-score（loopx-capability-analysis）
  - 成熟度路线图 P0：PRD→story→QA anchor contract、story-QA baseline bundle、coverage scorecard
  - 方法论 M2 feature map、M3 失败模式 skill 化回归（agent-coding-methodology）

## 2. 交叉后出现的「新」优化方向

### D1 验证能力前置 + 功能地图（Feature Map）
- **来源**：X 方法论 M2（agent 自己运行产品/读 trace/开模拟器，靠 feature map 把模糊 bug 路由到复现入口）+ deer-flow sandbox:execute 授权 + mempalace stale-library write guard。
- **方案**：把 `.beacon/code2truth/` 的 system map 资产演进为**机器可查询的 feature map**——每个功能带「位置、进入路径、验证入口（怎么运行、观察什么信号、复现命令）」；`beacon-plan`/`eval-real-project` 消费它，让"一张截图/一句 bug 描述"直接路由到复现，人不再当唯一 verifier。
- **载体**：`eval-real-project` + `beacon-gen-implement` 引用层；`.beacon/code2truth/` 扩展 schema。
- **优先级**：P1（复用现有 code2truth，不新开系统）。

### D2 预算/配额内核（S4 缺口闭合）
- **来源**：LoopX quota should-run + spend 账本（本次同步又看到 1055 条 quota 加固：fail-closed without scheduler receipt、spend artifact paths、settlement causality）+ gstack content binding / evidence ledger + ralphex spend-limit 检测 + longrun-pi-agent-evolution P0-3 spend-after-validated-writeback。
- **方案**：goal driver 增加 **spend ledger**：决策顺序固定为 健康门禁 → operator gate → 证据等待 → 配额；**只在校验后的 writeback 后 spend 一次**，quiet skip/dry-run 不 spend；交接文本限 16 行/1800 字符（handoff budget）。
- **载体**：`beacon-goal` / program lake driver；AC 落 tests。
- **优先级**：P0（既有 P0-3 研究已指向，本轮第三方同步确认可行性）。

### D3 失败模式 → skill 回归库（含异构审查）
- **来源**：X 方法论 M3（失败模式写 skill + 多 sub-agent + coordinator rubric + 跨模型打分）+ bmad claims falsification pass（边角猎手）+ ECC council-multi-model（异构 Codex review）+ spec-kit switch-case 校验硬化。
- **方案**：把 `beacon-plan`/`beacon-qa` eval 运行中**反复出现的 agent 失败模式**固化成可回归测试的 skill 用例（协调者 rubric + 交叉模型打分），作为 QA/release 前的对抗式审查输入——直接对齐 global-boundaries「对抗式审查（v1.6.4+）强制」。
- **载体**：`beacon-qa` skill eval kit 扩展 + `beacon-plan` evals/ 回归库；release 前强制加载。
- **优先级**：P0（对抗式审查已是 gate，缺的是机制化回归源）。

### D4 审查护栏：review 子 agent 禁止再 spawn + 单一 Skill 调用
- **来源**：ralphex / bmad-method 不约而同禁止 review agent 派发自身子 agent（detached dispatch）；mattpocock「跨 skill 调用单一化，禁止 skill 调用其他 user-invoked skill」+ ECC skill 激活触发声明进 description。
- **方案**：beacon 的 review/qa sub-agent 契约显式加「不得 spawn 子 agent」护栏（曾经 trellis-check 有此自豁免，随 trellis 移除后需在 beacon skill 层补回）；beacon-* skill 的触发词/激活声明统一元数据化。
- **载体**：beacon skill 文档与 sub-agent prompt 契约。
- **优先级**：P1（低成本、防递归失控）。

### D5 证据闭环保真：content-bound evidence ledger
- **来源**：gstack content binding（evidence ledger、tracker trust envelope、fail-closed hooks）+ mempalace 缓存/写入守卫 + loopx 证据生命周期（IP-012 external evidence observation）。
- **方案**：beacon evidence ref 增加**内容绑定**——证据引用不再只是路径，而是「路径 + 内容指纹/签名」，内容漂移时 fail-closed（不判 pass），杜绝「文档说完成但证据已变」的假闭环保真。
- **载体**：gate/evidence 校验层；AC 落 tests。
- **优先级**：P1（直接强化现有 evidence-first，不新增命令）。

### D6 Host surface 扩张与 parity 校验
- **来源**：openspec 加 Zed、superpowers v6.3 加 Devin/Hermes、bmad 加 Grok——第三方 skill 普遍多宿主化。
- **方案**：`beacon doctor setup-agent-surface` 扩展新宿主（Zed 等），并保持 beacon-* 在各 surface 的 parity；把「remove trellis 后 7 surface 手工清理」的经验固化为 `doctor verify-agent-surface` 的残留检测（本次实战证明官方卸载不覆盖全部 surface，beacon 自身需提供可靠清理/校验面）。
- **载体**：`beacon doctor`。
- **优先级**：P2（支撑面，不扩张主链）。

### D7 Auto-merge 边界（有意不采纳）
- **来源**：X 方法论 M4（agent 自动合入，人类退到 main 上复核）。
- **判定**：与 global-boundaries AC-027「release 永远不可 auto 覆盖」冲突，**不采纳**；仅记录为候选——若未来推进，只考虑 QA 通过后到非 release 中间阶段的自动合入，release 人类 gate 保持。
- **优先级**：记录，不实施。

## 3. 优先级排序与落地批次

| 批次 | 方向 | 落地载体 | 判据 |
|---|---|---|---|
| 批次 1（P0） | D2 预算内核、D3 失败模式回归库 | beacon-goal + beacon-qa eval | 闭合 S4/对抗式审查既有 gate 缺口 |
| 批次 2（P1） | D1 feature map、D5 证据闭环、D4 审查护栏 | code2truth + gate + skill 契约 | 强化 verification-first 与 evidence-first |
| 批次 3（P2） | D6 host parity、doctor 残留检测 | beacon doctor | 支撑面，低风险 |

## 4. 不建议做的（延续成熟度路线图的红线）

- 不扩张命令面（D 系列全部走现有 skill/命令内部能力）。
- 不把 memory 当新中心（D2-D5 都以主链 truth 为锚）。
- 不采纳 auto-merge 越过 release gate（D7）。
- 不重建被移除的 trellis 式任务运行时——beacon 自身 skill + program lake 已覆盖同等职责。

## 5. 结论

把 X 方法论、第三方最新能力与 beacon 现有缺口交叉后，**最值得先做的两条**：
1. **D2 预算/配额内核**（三方证据链最完整：方法论「有界回合」× loopx quota 加固 × gstack spend 账本）；
2. **D3 失败模式 skill 回归库**（方法论 M3 × bmad/ECC 异构审查 × beacon 既有对抗式审查 gate）。

两者都落在既有载体上、不扩张主链、可直接纳入下一条版本线的 program/truth 冻结流程。
