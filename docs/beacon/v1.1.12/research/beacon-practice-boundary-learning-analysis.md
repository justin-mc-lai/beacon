# 调研：Beacon v1.1.12 在 rolo / slow_uni_bmtop 实践下暴露的边界与 learning-plane 问题

**日期**：2026-04-01
**调研方式**：Beacon runtime + skill + cross-project docs 交叉复核
**目标**：把真实项目运用中暴露的版本真相、执行面路由、project skill 边界、learning-plane typed surface、takeover gate 等问题，转译成 Beacon `v1.1.12` 的正式需求输入。

---

## 1. 结论摘要

这轮实践复核说明，Beacon `v1.1.12` 不应只被定义成“prototype design governance”线。
它还必须补上一个更底层的治理层：

- 单一版本真相
- profile-aware execution routing
- capability-bounded project execution adapters
- typed learning-plane surfaces
- takeover baseline runtime gate

否则 design governance 即使文档定义得再漂亮，也会在真实项目里被以下问题持续打穿：

1. skill / CLI / docs 对“当前真实版本线”给出矛盾信号
2. navigator 仍默认把用户推回 Beacon native 通用执行面
3. project skill orchestration 实际上可以退化成任意 shell 编排器
4. autoresearch 文档上写 bounded，runtime 却没有 typed mutation surface
5. takeover 项目的 current-state baseline 仍主要靠“建议”，不是强门禁

一句话：

> `v1.1.12` 要真正稳住，不只要治理 prototype 的设计质量，还要治理 Beacon 自己的版本真相、执行边界和学习边界。

---

## 2. 已核实的关键证据

## 2.1 版本真相当前不是单源

Beacon 当前三处口径彼此打架：

- `SKILL.md:53-62`
  - 仍声明当前发布线 / 包版本 / 已落地实现线是 `v1.1.11`
- `beacon/__init__.py:4-5`
  - runtime 版本仍是 `1.1.11` / `v1.1.11`
- `docs/beacon/v1.1.12/release/v1.1.12.md:3-37`
  - 现在已经把 `Planning line only` 与 `Existing runtime facts informing this line` 分开表述
  - 这正说明 planning/runtime split 需要单独 machine-readable 建模，而不能继续靠文案暗示

这意味着 Beacon 当前缺少 machine-readable 的单一版本真相源。
结果是：

- help 可能读 `v1.1.11`
- docs 又提示 `v1.1.12`
- runtime 补丁事实和版本线 closure claim 混在一起

对 `v1.1.12` 的翻译结论：

> 版本真相必须成为正式 requirement，不然 skill / navigator / autoresearch / docs current-line 选择都会漂移。

## 2.2 navigator 仍然是“通用 Beacon 路径优先”

`beacon/utils/help_support.py` 的 `_next_step()` 里，几个关键分支仍直接返回 Beacon native 路径：

- `beacon/utils/help_support.py:99-104`
  - QA stop reason 命中 implementation blocker 时，直接推荐 `beacon implement run ... --runner native-single`
- `beacon/utils/help_support.py:177-181`
  - verify failed 时，直接推荐 `beacon review quality ...`
- `beacon/utils/help_support.py:189-198` 与后续实现分支
  - 文档冻结后默认走 `implement run ... --runner native-single`

也就是说，profile / stage binding 虽然存在，但 navigator 不是 profile-aware first，而是 native path first。

这与 Rolo 的实践边界相冲突：

- `/Users/apple/Developer/Company/rolo/docs/beacon/v1.3.0/execution/boundaries.md:39-40`
  - 明确要求 Beacon 只做 requirement-material + service-slice + delivery-evidence kernel
  - `rolo-dev` 才是 implementation / gateway / UAT / delivery operation surface

对 `v1.1.12` 的翻译结论：

> navigator 不应再把 Beacon native implementation 当默认真相，而应先解析 version truth、project mode、profile binding、stage-local execution surface，再决定下一步。

## 2.3 project_skills 目前边界过宽

`beacon/utils/project_skills.py` 里的 `run_profile_orchestration()` 目前做法过于宽泛：

- `beacon/utils/project_skills.py:401-414`
  - node 直接拿 `skill` / `command_template` 拼装命令
- `beacon/utils/project_skills.py:438-445`
  - 使用 `subprocess.run(..., shell=True)` 直接执行
- `beacon/utils/project_skills.py:415-425`
  - 运行前只记录 `produces_evidence` / `produces_cases`
  - 没有先校验 `supported_stages` / `capabilities` / `evidence_contract`

而 `v1.1.7` 的 PRD 原本说得很清楚：

- `docs/beacon/v1.1.7/prd/beacon-project-skill-orchestration.md:35-46`
  - Beacon 应定义需求、evidence contract、orchestration 抽象
  - Beacon 不应复制项目自己的全部运行时平台
  - Beacon 不应把 `rolo-dev` 之类项目技能的每个命令都直接内嵌进 core
- `docs/beacon/v1.1.7/prd/beacon-project-skill-orchestration.md:72-80`
  - Skill Registry 需要 `capabilities[]`、`supported_stages[]`、`evidence_contract`

对 `v1.1.12` 的翻译结论：

> project execution adapter 必须有 capability boundary；否则 Beacon core 会滑向任意 shell orchestrator，反而失去 product boundary。

## 2.4 learning plane 文档上 bounded，runtime 上还没 typed

Beacon 早就知道 autoresearch 的关键是：

- 固定时间盒
- 严格限制可修改边界
- 单一可比较目标

证据：

- `docs/beacon/v1.1.6/research/autoresearch/README.md:12-25`
  - 明确把 autoresearch 定义成单目标、固定预算、严格边界的实验系统
- `docs/beacon/v1.1.10/prd/beacon-qa-confidence-autoresearch-closure.md:55-72`
  - 已经把 QA closure 分成 requirement / evidence / judgement / closure / learning 五层

但 runtime 里的 learning plane subject surface 仍过于粗：

- `beacon/utils/learning_loop.py:137-146`
  - 只有 `execution_baseline`
  - `requirement_rewrite`
  - `debug_recovery_policy`

这和 `v1.1.12` 当前边界定义也不一致：

- `docs/beacon/v1.1.12/execution/boundaries.md:21-25`
  - 只说了 bounded、不可无限 HTML/CSS rewrite
  - 但没有把 `design_brief_extractor`、`guideline_severity_mapping`、`review_thresholds` 等 subject surface typed 化

对 `v1.1.12` 的翻译结论：

> bounded autoresearch 不能只停在口号，必须显式拆成 typed policy surfaces，否则 keep/discard 只能对模糊 requirement rewrite 生效，边界天然漂。

## 2.5 takeover baseline 仍主要靠文档约定，不是 runtime gate

`slow_uni_bmtop` 的 takeover 文档已经给出了很清楚的进入顺序：

- `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/execution/boundaries.md:94-103`
  - 先补齐 `architecture-blueprint`
  - `current-state-service-map`
  - `refactor-boundaries`
  - `version-evolution-blueprint`
  - `project-lifecycle-onboarding`
- `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/execution/project-lifecycle-onboarding.md:49-60`
  - agent 先确认 `docs_version` / `runtime_version`
  - 再读 architecture + service map + boundaries
  - 未冻结当前版本基线前不要扩张实现范围
  - next stage 应先是 `freeze`

这说明 takeover 模式的真实顺序应是：

```text
current-state truth
→ baseline freeze
→ feature workflow
→ implementation
```

而不是：

```text
init
→ feature / implement
→ 之后再补 current-state
```

对 `v1.1.12` 的翻译结论：

> Beacon core 需要 takeover-baseline-required 这一类 runtime gate，而不只是文档里“建议先这样做”。

---

## 3. 应冻结的四层边界模型

结合 Beacon core、Rolo、slow_uni_bmtop 的实践，最稳的产品边界应该是四层：

## Layer 1: Requirement kernel

负责：

- think
- user-story
- prd
- test-case
- architecture / boundaries / source materials

## Layer 2: Delivery evidence kernel

负责：

- implement summary
- technical archive
- qa scorecard
- review / gate / release

## Layer 3: Project execution adapters

负责：

- `rolo-dev`
- gateway / UAT / pipeline
- SQL / Redis / browser profile
- 项目特有 delivery operations

这一层必须保留在项目 execution surface，而不是并回 Beacon core。

## Layer 4: Learning plane

只允许优化：

- policy surface
- compiler surface
- evaluation surface

不允许直接扩成：

- project ops
- arbitrary code mutation
- secrets / cookies / storage state
- final release decision

---

## 4. autoresearch 真正该落在哪些面

## 应允许的落地面

- `qa_policy`
  - scenario expansion heuristics
  - evidence sufficiency thresholds
  - continue decision calibration
  - false-complete reduction
- `design_policy`
  - design brief extractor
  - design-system normalization
  - guideline severity mapping
  - review thresholds
- `contract_policy`
  - profile token / rule matcher
  - cross-artifact drift rules
- `debug_policy`
  - recovery policy
  - escalation mapping
- `rewrite_policy`
  - technical archive / QA outcome -> PRD/test-case/version research writeback
- `benchmark_policy`
  - scorecard weights
  - trial budget
  - keep/discard thresholds

## 不应允许的落地面

- `project_skills` 的 command template 本身
- `rolo-dev` / gateway / UAT / pipeline 的实际命令
- 业务仓任意实现代码
- release / gate 最终裁决逻辑
- cookies / storage state / secrets
- takeover 项目的 current-state truth 本体

一句话：

> autoresearch 应优化 Beacon 的判断系统，不应优化项目的执行系统。

---

## 5. 对 v1.1.12 应新增的 requirement

### RQ-001 单一版本真相源

skill、CLI、release line、docs current line 必须从同一个 machine-readable source 读取。
planning line 与 runtime supplement 必须显式分开。

### RQ-002 navigator 必须 profile-aware first

help / doctor / status 的下一步推荐，必须优先解析：

1. version truth
2. project mode
3. feature/profile binding
4. stage-local execution surface

只有没有 binding 时，才能降级到 Beacon native 通用路径。

### RQ-003 project execution adapter 必须有 capability gate

运行 orchestration 前必须先校验：

- `supported_stages`
- `capabilities`
- `evidence_contract`
- required evidence / cases

不满足就 blocked，而不是直接 shell 执行。

### RQ-004 learning plane subject surface 必须 typed

至少拆成：

- `qa_policy`
- `design_policy`
- `contract_policy`
- `debug_policy`
- `rewrite_policy`
- `benchmark_policy`

### RQ-005 takeover 模式必须有 baseline gate

缺少以下任一项时，不允许进入 `implement`：

- `architecture-blueprint`
- `current-state-service-map`
- `refactor-boundaries`
- current baseline freeze

### RQ-006 项目 service-slice / profile docs 只作为只读 contract inputs

像 Rolo 这样的项目文档，应进入：

- profile gate
- contract drift detection
- verify / review inputs

而不是被误用成 Beacon core 的默认执行脚本来源。

---

## 6. 建议的稳定顺序

实践证明，最稳的 Beacon skill workflow 应按下面的顺序收敛：

```text
single version truth
→ project mode
→ execution surface
→ bounded learning surface
→ help / status / review / gate
```

如果顺序反过来，系统就会出现：

- docs current-line 漂移
- navigator 乱推 native path
- project skill 边界穿透
- autoresearch 学到执行面而不是判断面

---

## 7. 结论

这轮实践对 `v1.1.12` 的真正补充不是“再加几个 design governance artifact”，而是：

> 让 Beacon 自己先具备稳定的版本真相、项目边界真相和 learning-plane 真相，然后 design governance 才不会被错误的执行面和错误的版本线带偏。

因此，`v1.1.12` 应被扩展为：

```text
design governance
+ execution-boundary stabilization
+ typed learning-plane governance
```

---

**落盘位置**：`docs/beacon/v1.1.12/research/`
