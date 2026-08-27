# Beacon Research Index

**Purpose**: provide a stable entrypoint for Beacon research materials that remain useful across versions, plus a map into version-bound research packs.

---

## 1. How to use this directory

Use `docs/beacon/research/` for research that is expected to stay useful across multiple release lines.

For local source lookup of external references, start with:

- [Beacon Open-Source Reference Source Map](./beacon-open-source-reference-source-map.md)

Good fit:

- external reference studies
- method / pattern analysis
- knowledge-plane design notes
- schema / governance concepts
- cross-version product reasoning

Not a good fit:

- single-release delivery notes
- one-off implementation closure artifacts
- version-specific bug or gate investigations that belong under `docs/beacon/<version>/research/`

Rule of thumb:

- if the note is mainly about a specific release line, put it under that version
- if the note describes a reusable pattern Beacon may keep citing later, put it here

---

## 2. Cross-version research

### Active long-lived notes

1. [Beacon Open-Source Reference Source Map](./beacon-open-source-reference-source-map.md)
   - Why it matters:
     freezes the mapping from Beacon research references to canonical `oss-sync` source directories, so future version evolution can read local source code from a known path instead of guessing old `.research/` locations.

2. [Karpathy `LLM Wiki` pattern analysis](./beacon-karpathy-llm-wiki-pattern-analysis.md)
   - Why it matters:
     gives Beacon a reusable frame for compiled knowledge layers, `ingest/query/lint`, query-to-doc writeback, and schema-as-maintainer governance.

3. [Beacon multi-project isolation and learning brainstorm](./beacon-multi-project-isolation-and-learning-brainstorm.md)
   - Why it matters:
     proposes a `kernel / project capsule / distill plane` model for strict project isolation, human-thinking/agent-execution split, and reusable but controlled cross-project experience distillation.

4. [Beacon manager strong doc sync brainstorm](./beacon-manager-strong-doc-sync-brainstorm.md)
   - Why it matters:
     defines a separate `beacon-manager` tool/skill for binding multiple project `docs/beacon` trees into one personal GitHub knowledge repo with git-like `bind/pull/sync/status/reconcile/doctor` workflows and strong consistency rules.

5. [Beacon self-iteration and story-QA coverage study from awesome-design-md and autoagent](./beacon-self-iteration-and-story-qa-coverage-study-awesome-design-md-autoagent.md)
   - Why it matters:
     proposes a dual structure for Beacon: an asset plane for reusable QA baseline bundles and a bounded eval plane for policy-level self-iteration driven by story/AC coverage and false-complete reduction.

6. [Beacon memory and knowledge-plane study from mempalace](./beacon-memory-asset-eval-plane-study-mempalace.md)
   - Why it matters:
     argues for a raw-plus-structured memory model for Beacon, where important reasoning is preserved verbatim, organized into a navigable knowledge plane, and benchmarked for recall value rather than summarized away too early.

7. [Beacon completeness and maturity matrix](./beacon-completeness-maturity-matrix.md)
   - Why it matters:
     provides a concrete score-based assessment of Beacon's current product surfaces, skill/operator design, architecture responsibilities, and risk concentration, anchored explicitly on the `PRD → story → QA` mainline.

8. [Beacon maturity remediation roadmap](./beacon-maturity-remediation-roadmap.md)
   - Why it matters:
     translates the maturity matrix into an execution order, prioritizing mainline hardening, complexity reduction, asset packaging, and only then bounded self-iteration.

9. [Beacon codex-native subagent direction from `gstack`, `superpowers`, and the v1.3.0 seed note](./beacon-codex-native-subagent-direction-gstack-superpowers.md)
   - Why it matters:
     promotes subagent governance out of a single release line and freezes the cross-version position that Beacon should use bounded subagents only on selected surfaces, with stage-owner truth, fresh context packaging, and explicit review ladders.

10. [Beacon Ralph / Subagent norms and long-task delivery brainstorm](./beacon-ralph-subagent-long-task-delivery-brainstorm.md)
   - Why it matters:
     freezes a cross-version judgment that Ralph should be the closure controller, subagents should remain bounded execution units, and long tasks should be modeled as a requirement-to-release loop rather than open-ended agent expansion.

11. [Open SaaS Base from `@zyailive` + `ItusiAI/get-saas`](./open-saas-base-from-zyailive-get-saas.md)
   - Why it matters:
     freezes the dual-source direction for a self-owned open SaaS kernel: low-cost/edge stack and data-sovereign auth from the zyailive note, product-surface parity checklist from get-saas, plus first-class plugin products and agent skills for later in-house products.
   - Linked product project:
     `/Users/apple/Developer/Personal/products/open-saas-base/`
12. [Intent decomposition hardening (2026-07-21)](./intent-decomposition-hardening-2026-07-21.md)
   - Why it matters:
     prevents ocean goals from auto-ticking past plan without journey freeze; multi-signal plan_subintent + host 子代理 gate.
13. [大厂 AI agent coding 方法论 —— Cursor 工程师 Lauren Tan 工作方法拆解](./beacon-agent-coding-methodology-cursor-poteto-2026-08.md)
   - Why it matters:
     一线实证「验证 > 生成 / feature map / 失败模式 skill 化 / agent 团队工程管理」，映射到 Beacon 的验证优先设计与 S4 预算等缺口。
14. [Beacon 对齐第三方 spec skill 同步更新摘要（2026-08-26）](./beacon-oss-reference-sync-2026-08-26.md)
   - Why it matters:
     记录 oss-sync canonical mirror 与上游的对齐状态及更新要点（loopx quota、review 子 agent 护栏、skill 触发标准化），并修正 source map 的 `awesome-design-md` 路径。
15. [Beacon 优化方向提案（2026-08-27）—— X 方法论 × 第三方 spec 最新能力](./beacon-optimization-proposal-2026-08-27.md)
   - Why it matters:
     把 Cursor 工程师方法论、本日第三方同步能力与既有缺口（S4 预算、feature map、失败模式回归）交叉成 7 个 beacon 原生优化方向，首批锁定预算内核 + 失败模式 skill 回归库。
16. [Beacon v1.6.13 规划源审计（2026-08-27）—— 7 优化方向 × OSS 能力对照 × skill 文案规范](./beacon-v1613-planning-source-audit-2026-08-27.md)
   - Why it matters:
     子代理锚定 oss-sync 源码核实 7 方向的第三方证据链（D2/D3 最强、D1/D5 弱、D7 不采纳），并审计 7 个 skill 文案规范性（F1-F5：共享块复制 bug、人话契约只在 truth、mode_id 前缀断裂），产出 v1.6.13 批次建议。


---
17. [Feature Map 设计（2026-08-27）—— 需求真相 × 代码锚定的功能地图](./beacon-feature-map-design-2026-08-27.md)
   - Why it matters:
     把方法论 M2 的 feature map 与 beacon 需求真相结合：truth 讲"做什么"，feature-map 讲"在哪改/怎么验证/看什么"，agent 固定走「读 truth→读 map→实现→自证」，分三阶段建设（骨架→复现路由→agent 自验证）。


## 3. Version-bound research entrypoints

These directories contain research tied to specific release lines and should be read together with that version's `SUMMARY.md` and execution materials.

### v1.3.2

- [`docs/beacon/v1.3.2/research/`](../v1.3.2/research/)
  - Current notable topic:
    responsibility optimization for `implement / qa / ralph`, clarifying the split between truth owner, execution runtime, closure controller, and learning plane

### v1.3.0

- [`docs/beacon/v1.3.0/research/`](../v1.3.0/research/)
  - Current notable topic:
    this line no longer owns the canonical codex-native subagent direction note; it now consumes [Beacon codex-native subagent direction from `gstack`, `superpowers`, and the v1.3.0 seed note](./beacon-codex-native-subagent-direction-gstack-superpowers.md) and keeps only version-local pointers/adoption materials

### v1.2.0

- [`docs/beacon/v1.2.0/research/`](../v1.2.0/research/)
  - Current notable topic:
    product-manager skills design analysis

### v1.1.12

- [`docs/beacon/v1.1.12/research/`](../v1.1.12/research/)
  - Current notable topics:
    practice boundary and learning-plane governance
    design governance and meta-harness closure
    requirement-anchor divergence closure
    external reference study against StatsClaw and awesome-design-md

### v1.1.9

- [`docs/beacon/v1.1.9/research/`](../v1.1.9/research/)
  - Current notable topic:
    Karpathy autoresearch evo translation for Beacon

### v1.1.8

- [`docs/beacon/v1.1.8/research/`](../v1.1.8/research/)
  - Current notable topics:
    gstack gap analysis
    three-track closure audit

### v1.1.6

- [`docs/beacon/v1.1.6/research/`](../v1.1.6/research/)
  - Current notable topics:
    external framework/reference reading pack
    autoresearch, gstack, openspec, bmad-method, memevolve, deer-flow

### Earlier lines

- [`docs/beacon/v1.1.1/research/`](../v1.1.1/research/)
- [`docs/beacon/v1.1.0/research/`](../v1.1.0/research/)
- [`docs/beacon/v1.0.3/research/`](../v1.0.3/research/)
- [`docs/beacon/v1.0.2/research/`](../v1.0.2/research/)
- [`docs/beacon/v1.0.1/research/`](../v1.0.1/research/)

Use these mainly for historical context, not as the first source for current product truth.

---

## 4. Suggested reading order

If you are trying to understand Beacon's long-horizon research direction:

1. Start with [Karpathy `LLM Wiki` pattern analysis](./beacon-karpathy-llm-wiki-pattern-analysis.md)
2. Then read [Beacon Open-Source Reference Source Map](./beacon-open-source-reference-source-map.md) if you need the local `oss-sync` source directories behind any external reference
3. Then read [Beacon multi-project isolation and learning brainstorm](./beacon-multi-project-isolation-and-learning-brainstorm.md)
4. Then read [Beacon manager strong doc sync brainstorm](./beacon-manager-strong-doc-sync-brainstorm.md) for the independent cross-project doc-sync tool direction
5. Then read [Beacon self-iteration and story-QA coverage study from awesome-design-md and autoagent](./beacon-self-iteration-and-story-qa-coverage-study-awesome-design-md-autoagent.md)
6. Then read [Beacon memory and knowledge-plane study from mempalace](./beacon-memory-asset-eval-plane-study-mempalace.md)
7. Then read [Beacon completeness and maturity matrix](./beacon-completeness-maturity-matrix.md)
8. Then read [Beacon maturity remediation roadmap](./beacon-maturity-remediation-roadmap.md)
9. Then read [Beacon codex-native subagent direction from `gstack`, `superpowers`, and the v1.3.0 seed note](./beacon-codex-native-subagent-direction-gstack-superpowers.md)
10. Then read [Beacon Ralph / Subagent norms and long-task delivery brainstorm](./beacon-ralph-subagent-long-task-delivery-brainstorm.md)
11. Then read [`docs/beacon/v1.1.12/research/`](../v1.1.12/research/) for the most recent governance-heavy release-line studies
12. Then read [`docs/beacon/v1.2.0/research/`](../v1.2.0/research/) for newer product-surface expansion work

If you are trying to solve a concrete versioned task:

1. Start with `docs/beacon/<version>/SUMMARY.md`
2. Read `docs/beacon/<version>/execution/index.md`
3. Only then drill into that version's `research/`

---

## 5. Maintenance rule

When adding a new research note:

1. decide whether it is cross-version or version-bound
2. place it in the correct directory
3. add a one-line entry here if it is cross-version
4. if it materially changes a version line, also update that version's `SUMMARY.md` or execution index as needed
5. if it cites an external open-source project, also update [Beacon Open-Source Reference Source Map](./beacon-open-source-reference-source-map.md)

13. [Beacon Competitor & Open-Source Benchmark Registry](./beacon-competitor-registry.md)
   - Why it matters:
     registers and analyzes key open-source benchmarks (`spec-kit`, `mattpocock-skills`, `everything-claude-code`) for spec-driven workflows, task breakdown, drift/padding interception, and dynamic context updates.
14. [Beacon long-run stability analysis (2026-08-03)](./beacon-longrun-stability-analysis-2026-08.md)
   - Why it matters:
     audits Beacon's long-running task stability across 8 dimensions against four new loop projects (`loopx`, `oh-my-pi`, `kun`, `simple-long-horizon-agent`); identifies the real gaps as S4 quota control and S7 concurrent ownership, with loopx's quota-aware wake and claims/leases as directly adoptable references, plus a Δ-vs-baseline evaluation standard.
15. [Beacon long-run stability mechanisms + pi agent evolution (2026-08-03)](./beacon-longrun-pi-agent-evolution-2026-08.md)
   - Why it matters:
     deep-dives kun's goal-as-thread-object dual-coordinator loop and loopx's deterministic no-LLM control plane (quota slots, should_run gate chain, hard leases, event-sourced state) at source level, produces a 10-item Beacon stability backlog (P0 quota/spend-after-validated-writeback/Δ-eval), and designs the architecture for Beacon truth delivery powered by the pi agent (oh-my-pi) for long-run delivery, creative tasks, and scheduled tasks — with the explicit boundary that truth/state-machine/gates stay in Beacon while execution lives in pi.
16. [Beacon loop capability next steps (2026-08-05)](./beacon-loop-capability-next-2026-08.md)
   - Why it matters:
     re-assesses loop capability after v0.0.4 vision-flywheel shipped and the first heartbeat (search-boundary-curate) went live; the six insights prioritize closing the feedback loop (metrics → analyze → brain-writeback), turning single heartbeat into a heartbeat network (produce-queue + evidence_threshold triggers + hard lease), upgrading should-run to state-aware gates (terminal_no_followup / replan obligation / workspace guard), adding no-progress backoff, event-sourcing the ledger, and adopting a Δ-vs-baseline evaluation standard — with the autonomy ladder L0→L4 as the organizing narrative (triggers and convergence shift to the system, human gates never revoked).
17. [Beacon × ADB role division (2026-08-05)](./beacon-adb-role-division-2026-08.md)
   - Why it matters:
     freezes the division of labor between Beacon (defines correctness, judges completion — truth/FSM/gates/verifier) and agent-delivery-bus (schedules and governs — approvals/idempotent dispatch/heartbeat quota/evidence reconciliation); documents the concrete coupling points (truth_gate adapter = beacon, worker binding embeds beacon skills, dual gates never substitute), the one-line boundary rule (standards/judgment → Beacon; dispatch/approval/quota/ledger → ADB; execution/creation → hermes/pi), and the future allocation of loop improvements across the two projects.

- [QA 验证强度 × 自动合并审核增强](./beacon-qa-strength-auto-merge-2026-08-27.md)
- [Auto-merge 第一性原理（M4 修正）](./beacon-automerge-first-principles-2026-08-27.md)
