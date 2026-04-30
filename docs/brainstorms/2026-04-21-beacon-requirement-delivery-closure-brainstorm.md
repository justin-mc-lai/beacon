---
date: 2026-04-21
topic: beacon-requirement-delivery-closure
---

# Beacon Requirement Delivery Closure Brainstorm

## What We're Building

Beacon 现在已经有 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release` 主链，也已经有 `memory / workflow-memory / memory-friction-evolution / team / ralph / status` 这些局部能力。真正缺的不是单点功能，而是一层更稳定的产品闭环：

- requirement truth 要能约束 implement
- QA 要明确对齐 test-case，而不是单独形成一套验证叙事
- memory 和 evo 要能持续识别边界漂移、复发问题和闭环缺口
- `single / team / ralph` 这些执行面要共享同一份 requirement + evidence truth
- 可视化产品面要展示官方产品语义，而不是直接暴露内部技术术语

这次 brainstorming 的目标不是写实现方案，而是明确 Beacon 应该形成什么样的闭环产品模型，才能更稳定地落地“需求冻结后的人机协作交付”。

## Why This Approach

### Approach A: 继续堆叠现有命令结果

把 `implement / qa / status / report / release` 的结果继续拼在一起，用更多汇总字段解决闭环问题。

**Pros:**
- 改动最小
- 复用已有命令产物

**Cons:**
- requirement、qa、memory、visual semantics 仍然是分裂的
- 更像“汇总更多状态”，不是“形成统一产品闭环”

**Best when:** 只想补一点状态展示，不想调整产品结构。

### Approach B: Alignment-first 闭环层

新增一层“对齐与闭环语义面”，把 requirement alignment、QA alignment、boundary exploration、execution closure、official console semantics 收到同一 read model 中。

**Pros:**
- 最符合 Beacon 的 workflow-native 产品边界
- 能把 memory/evo 变成闭环治理层，而不是孤立工具

**Cons:**
- 需要统一很多已有内部语义
- 需要重新定义可视化产品默认展示词汇

**Best when:** 目标是让 Beacon 更像正式产品，而不是脚本集合。

### Approach C: 直接做 autonomous delivery brain

把 requirement probing、repair loop、team orchestration、visual control plane 全做成高度自治系统。

**Pros:**
- 自动化上限最高

**Cons:**
- 容易把 Beacon 拉成通用自治平台
- 容易超出当前产品边界

**Best when:** 产品目标已经不是 Beacon 的最小主链，而是独立自治系统。

推荐采用 **Approach B**。它最符合 Beacon 当前形态，也最容易和现有 memory/evo 吸收线对齐。

## Key Decisions

- 决策 1：Beacon 的闭环核心应该是 `alignment`，不是更多 runtime 状态。因为 requirement、qa、release 真相不一致，才是当前最危险的漂移。
- 决策 2：QA 必须被正式定义为 `test-case aligned verification`，而不是自由验证层。否则 release evidence 不稳定。
- 决策 3：memory 应该服务 requirement/delivery closure，而不是变成独立知识库。它的职责是保存证据、帮助召回、降低接力成本。
- 决策 4：evo 应该服务 boundary exploration 和 recurrence governance，而不是独立演化秀场。它要帮助 Beacon 识别“需求边界还不清”“同类问题又回来了”。
- 决策 5：`team / ralph / subagent` 是执行实现，不应该成为人类主界面的默认语义。产品面应优先展示 `执行模式 / 闭环状态 / 风险 / 下一步`。
- 决策 6：官方可视化语义要正式化，避免首页和项目详情出现太多 `ralph / tmux / runtime family / fallback reason` 这类内部术语。

## Open Questions

- requirement boundary probing 的输出是写进 `research/change-candidate`，还是写进 `doctor/status` 的治理面。
- `team` 和 `ralph` 在官方 UI 中是否保留二级技术详情入口，还是只在 Recovery / Diagnostics 页面显式出现。
- QA 对 test-case 的对齐粒度，是否需要达到 `scenario -> evidence -> verdict` 逐条闭环，而不是 feature 级摘要。

## Next Steps

→ 先沉淀到 `docs/beacon/v1.3.6/research/` 做研究线文档  
→ 明确官方可视化语义字典  
→ 再决定是否进入 PRD / user-story / test-case
