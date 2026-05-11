# PRD: Beacon v1.4.2 Contract-Aligned Test Evolution and Skill Delivery Governance

**Feature**: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`  
**Version**: `v1.4.2`  
**Date**: `2026-05-11`  
**Status**: `freeze-ready`  
**Track**: `test-governance + skill-delivery + release-contract + browser-qa-admission`  
**Scenario**: `beacon-self-iteration + contract-lane-classification + skill-surface-guidance + protected-browser-surface-governance`  
**Template**: `main PRD / next-version planning`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Current runtime architecture: `docs/beacon/v1.4.0/execution/architecture-blueprint.md`
- Previous planning line: `docs/beacon/v1.4.1/SUMMARY.md`
- Deep support surface PRD: `docs/beacon/v1.4.1/prd/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- Deep test delta sample: `docs/beacon/v1.4.1/deep/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure/deep-test-delta.md`
- Skill QA order rule: `skills/beacon/references/usage-rules.md`
- Browser QA runtime guidance: `skills/beacon/beacon-qa/SKILL.md`
- External browser-skill research synthesis: `docs/beacon/v1.4.0/research/beacon-vs-openspec-speckit-skill-alignment.md`

## 1. 问题

Beacon 自迭代已经具备 frozen truth、QA、release、deep delta、version surface governance 等能力，但测试集合在持续演进时仍可能混合当前功能验收、当前 runtime 契约、generated surface 同步、兼容承诺、历史快照与过期假设。缺少契约 lane 会让 full-suite 输出无法解释为明确的交付状态。

与此同时，Beacon 的 browser-capable QA 还存在第二层治理缺口：skill 和 research 已经知道 protected live surface 应优先走 attached-session / CDP / real-browser 路径，但默认运行时和 adapter 仍可能落到 placeholder runner、transcript-only evidence 或 bare Playwright fallback。结果是“知道正确策略”与“能稳定执行正确策略”之间出现断层。

## 2. 目标

本需求目标是在不扩张主生命周期的边界下，为 Beacon 建立契约对齐的测试演进治理模型：以 frozen truth 为源头，以 Test Contract Index 为投影，以 QA evidence 和 release gate 为验收闭环，使测试增量、skill 指引、风险缓解和恢复路径都可审计；同时把 browser-native QA admission、runner 选择、session bridge、evidence 真实性与 learning loop 纳入正式 requirement，而不是停留在经验说明或 skill 提示词。

## 3. 设计原则

### 3.1 边界优先

- `Test Contract Index` 只能作为 machine projection，不能成为第二 truth root。
- `doctor / qa / release / deep` 承担既有表面内的治理职责，不新增公开主阶段。
- planning line 不能污染 current runtime release line。

### 3.2 分层优先

- 分层保持为 markdown truth -> compiled contract -> test contract index -> browser admission truth -> QA evidence -> release scorecard -> skill delivery guidance。
- skill 文案只能提供交付指引，不能直接定义 release verdict。
- runtime projection 只能消费契约，不能反向改写 frozen truth。

### 3.3 恢复优先

- 失败必须有 reason code、repair route 和 `beacon help` resume route。
- severe blocker 必须 `stop_for_repair`，修复后再进入下一轮 QA backfill。
- legacy snapshot drift 默认进入 test evolution backlog，除非被明确提升为 compatibility contract。

### 3.4 风险缓解优先

- generated surface drift、feature release lane failure、planning/runtime conflict 必须被识别为 release-facing 风险。
- 风险缓解方式必须显式记录为 repair、waiver、backlog、compatibility promotion 或 reject。
- unclassified full-suite output 不能被用作 release pass 或 release blocker 的唯一依据。

### 3.5 真实浏览器优先

- 对 protected live surface，runner admission 必须优先判断 session bridge 与 attached browser truth，而不是默认从 bare Playwright 开始撞墙。
- transcript、task echo、静态 artifact 占位件不能单独充当 browser QA 完成证据。
- 无 session bridge 时，正式结果应为 `skip` / `blocked` + machine-readable reason，而不是把环境/认证失败记成产品失败。

## 4. 范围

In scope:

- Define `Test Contract Index` as a machine-readable delivery governance projection.
- Define canonical test lanes for Beacon self-iteration.
- Define AC/TC/pytest/evidence mapping expectations.
- Define doctor build/verify ownership for test contract governance.
- Define QA and release consumption of lane status.
- Define skill delivery guidance so agent surfaces route test work by contract lane.
- Define release reason codes for missing, stale, failed, or unclassified test contract evidence.
- Define how `deep` test deltas are adopted without letting deep execute QA or rewrite frozen truth.
- Define protected browser surface admission, runner priority, session-backed evidence requirements, and runner-learning writeback.

Out of scope:

- Creating a new public lifecycle stage.
- Promoting `v1.4.2` to runtime release line.
- Rewriting all historical tests.
- Treating full-suite output as a single release gate without lane classification.
- Letting skill text define release truth independently from machine evidence.
- Letting `Test Contract Index` become a second requirement truth root.
- Treating placeholder runner transcripts as equivalent to real browser evidence.
- Letting protected live surface QA silently degrade to bare Playwright or generic fallback without explicit classification.

## 5. 问题拆解

### 5.1 Feature evolution currently creates mixed test semantics

Beacon's full test suite contains different kinds of obligations:

- current runtime contracts;
- current feature release-facing tests;
- generated surface sync checks;
- compatibility promises;
- historical snapshot checks;
- old assumptions that need test evolution.

When these are run as a flat suite, failures become ambiguous. A single failure may mean a current release blocker, a generated surface drift, a legacy snapshot mismatch, or an obsolete assumption.

### 5.2 Single tests can become orphaned from product truth

A single test that is not mapped to AC/TC, lane, evidence path, and release consumption can pass while the product contract remains incomplete. It can also fail without explaining whether the failure blocks release.

### 5.3 Agent skill delivery can amplify ambiguity

If Beacon skills tell agents to “run tests” or “fix full-suite failures” without lane classification, agents can:

- chase historical snapshot drift before current release blockers;
- treat planning-line docs as runtime release claims;
- claim progress without AC/TC/evidence truth;
- skip the QA first-principles order;
- ask humans to guess the resume path instead of using `beacon help`.

### 5.4 Browser QA currently knows the right policy but cannot always enforce it

Beacon's QA skill already encodes a protected-surface policy:

```text
web-access
-> attached agent-browser
-> playwright attach/CDP
-> bare Playwright last
```

But core runtime wiring can still:

- default `beacon qa` to a placeholder `browser-use` path;
- accept transcript-only runner artifacts as if they were browser evidence;
- miss the distinction between attached-session truth and clean-context retries;
- repeat the same SSO/login failure without learning writeback.

That makes browser-capable QA look stronger in documentation than in execution.

## 6. Goals

### Primary Goals

1. Establish a `Test Contract Index` that maps feature truth to test lanes and evidence.
2. Classify Beacon tests into stable contract lanes.
3. Ensure each release-facing single test is traceable to AC/TC and evidence.
4. Let `doctor` build and verify test contract governance.
5. Let `qa` execute lane-aware evidence capture in AC order.
6. Let `release` consume lane status and block on relevant reason codes.
7. Update skill delivery guidance so Codex, Claude, Cursor, and Windsurf agents use contract-lane test routing.
8. Preserve global boundaries by avoiding new public lifecycle stages.
9. Make protected-surface browser QA attached-session-aware, evidence-authentic, and recoverable.

### Non-Goals

- This feature does not implement a new test runner.
- This feature does not replace pytest.
- This feature does not make deep mandatory for every feature.
- This feature does not rewrite legacy tests automatically.
- This feature does not change current runtime version from `v1.4.0`.
- This feature does not force every QA run to use a browser when the formal test bundle is non-browser.

## 7. Product Model

### Contract Chain

```text
Markdown truth
-> compiled feature contract
-> test contract index
-> browser admission and session truth
-> lane-aware QA evidence
-> release scorecard/gate
-> skill delivery guidance
```

### Canonical Lanes

| Lane | Responsibility | Release Blocking Rule |
| --- | --- | --- |
| `feature_release_facing` | Current feature AC/TC/pytest/evidence closure | Blocks current feature release |
| `current_runtime_contract` | Current runtime version, docs default line, public surface, current docs claims | Blocks runtime/release readiness |
| `generated_surface_sync` | Generated or projected surfaces such as `SKILL.md`, metadata, context files, command tables, agent surfaces | Blocks when drift affects routing, versioning, or delivery truth |
| `compatibility_contract` | Explicitly supported legacy behavior | Blocks only when behavior remains an active support promise |
| `legacy_snapshot` | Historical docs/evidence snapshots | Does not block current feature release by default |
| `browser_runtime_admission` | Protected-surface session bridge, runner priority, and real-browser evidence eligibility | Blocks browser-capable QA when attached-session truth or authentic evidence is missing |

## 8. Functional Requirements

- FR-001: Beacon must define a Test Contract Index containing identity, truth refs, runtime/docs line, lane membership, AC/TC/test/evidence mapping, status, and reason codes.
- FR-002: Beacon must verify release-facing lane classification and block unsafe unclassified failures.
- FR-003: Beacon must require release-facing tests to map to AC/TC and evidence or declare an explicit generated-surface contract reason.
- FR-004: Doctor support commands must own build/verify behavior for the test contract index.
- FR-005: QA must preserve AC order, evidence pack, coverage current/gap, continue decision, repair handoff, help resume, and next-round backfill.
- FR-006: Release scorecard and strict gate must consume lane status and expose reason codes.
- FR-007: Beacon skill surfaces must guide agents to classify tests by lane.
- FR-008: Deep-derived test deltas must route to test-case or supplemental QA.
- FR-009: Planning-line safety must preserve runtime/package/docs-current version truth.
- FR-010: Beacon must formalize browser-runtime admission for protected live surfaces, including session bridge truth, runner priority, and explicit skip/blocked semantics.
- FR-011: Beacon must distinguish real browser evidence from placeholder runner artifacts and require authentic browser packs for browser-capable QA closure.
- FR-012: Beacon must persist runner-specific learning notes for protected-surface failures so repeated QA rounds can resume with better admission choices.

### FR-010: Protected Browser Surface Admission

For browser-capable QA that targets protected live surfaces, Beacon must support a formal admission decision before execution:

```text
target classification
-> session bridge present?
-> attached runner available?
-> real browser evidence path available?
-> execute / skip / blocked
```

Runner priority for protected surfaces must align to:

```text
web-access
-> attached agent-browser
-> playwright attach/CDP
-> bare Playwright last
```

If no attached/session-backed path is available, Beacon must record `skip` or `blocked` with a machine-readable reason code rather than disguising the run as a product failure.

### FR-011: Browser Evidence Authenticity

Beacon must distinguish:

- real browser evidence packs produced from an attached or deterministic browser execution path;
- placeholder runner artifacts such as task echoes, static transcripts, or synthetic DOM/network summaries.

Placeholder artifacts may support debugging, but they must not by themselves satisfy browser-capable QA closure for release-facing scenarios.

### FR-012: Runner Learning Loop

Beacon must support a QA learning note path for protected/browser-capable scenarios so repeated failures can be classified and reused:

```text
runner attempted
-> outcome
-> reason code
-> fallback or next preferred runner
-> expiry / staleness
```

The learning note is advisory, not a second truth root, but it must be readable by skill/runtime routing so the same SSO/admission mistake is not repeated indefinitely.

## 9. Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | index-contract | Beacon defines a Test Contract Index with feature identity, truth refs, runtime/docs line, lane membership, AC/TC/test/evidence mapping, status, and reason codes. |
| AC-002 | lane-taxonomy | Beacon defines canonical lanes for feature release-facing tests, current runtime contracts, generated surface sync, compatibility contracts, legacy snapshots, and browser runtime admission. |
| AC-003 | release-facing-mapping | Release-facing single tests must map to AC/TC and evidence or declare a generated-surface contract reason. |
| AC-004 | doctor-ownership | Doctor support commands own building and verifying the test contract index; no new public lifecycle stage is introduced. |
| AC-005 | qa-order | QA guidance and execution preserve AC order, evidence pack, coverage current/gap, continue decision, severe blocker stop, repair handoff, `beacon help` resume, and next-round backfill. |
| AC-006 | release-gating | Release scorecard and strict gate consume lane status and block on missing, stale, failed, or unclassified release-facing evidence. |
| AC-007 | generated-surface-sync | Generated skill, metadata, command, context, and agent surfaces are lane-classified and block delivery when drift affects truth or routing. |
| AC-008 | legacy-classification | Historical snapshot failures are routed to `legacy_snapshot` or test evolution backlog unless explicitly promoted to `compatibility_contract`. |
| AC-009 | skill-delivery | Beacon skills instruct agents to use contract-lane verification and avoid unclassified full-suite release claims. |
| AC-010 | deep-delta-adoption | Deep test deltas are adopted through `test-case` or supplemental `qa`; deep remains a support surface and does not execute QA. |
| AC-011 | planning-line-safety | Freezing v1.4.2 requirements does not change current runtime release line, docs default line, or package version. |
| AC-012 | recovery-routing | When test contract governance blocks delivery, Beacon provides reason codes and repair or resume routes through existing support surfaces. |
| AC-013 | browser-admission | Protected browser surfaces require session/runner admission and prefer attached-session paths before bare Playwright. |
| AC-014 | browser-evidence-authenticity | Browser-capable QA closure requires authentic browser evidence, not transcript-only placeholder artifacts. |
| AC-015 | browser-runner-priority | `web-access -> attached agent-browser -> playwright attach/CDP -> bare Playwright` is represented as the protected-surface runner priority model. |
| AC-016 | blocked-not-false-fail | Missing session bridge on protected live surfaces yields `skip` or `blocked` reasoned outcomes rather than false product failures. |
| AC-017 | runner-learning | QA writes reusable runner/admission learning notes with reason, fallback, and expiry semantics. |
| AC-018 | browser-lane-traceability | Browser-runtime admission and browser evidence obligations are represented in lane/status reasoning alongside AC/TC/evidence mapping. |

## 10. 验收标准

| AC ID | 验收主题 | 验收标准 |
| --- | --- | --- |
| AC-001 | index-contract | Test Contract Index 的身份、truth refs、runtime/docs line、lane、AC/TC/test/evidence、status、reason codes 可被机器校验。 |
| AC-002 | lane-taxonomy | canonical lanes 明确声明并用于测试分类，含 browser runtime admission。 |
| AC-003 | release-facing-mapping | release-facing single tests 未映射 AC/TC/evidence 时必须阻断或声明 generated-surface contract reason。 |
| AC-004 | doctor-ownership | doctor 表面负责 build/verify，不新增主生命周期阶段。 |
| AC-005 | qa-order | QA 顺序保留 AC order、evidence pack、coverage current/gap、continue decision、repair handoff、help resume 和 backfill。 |
| AC-006 | release-gating | release scorecard 和 strict gate 消费 lane status 并输出阻断 reason codes。 |
| AC-007 | generated-surface-sync | generated surfaces 漂移被归入 `generated_surface_sync` 并可在影响交付 truth 时阻断。 |
| AC-008 | legacy-classification | historical snapshot drift 默认不阻断当前 release，除非被提升为 compatibility contract。 |
| AC-009 | skill-delivery | skills 指导 agent 使用 contract-lane verification，不从未分类 full-suite 输出宣称 ready。 |
| AC-010 | deep-delta-adoption | deep delta 经 test-case 或 supplemental QA 采纳，deep 不执行 QA。 |
| AC-011 | planning-line-safety | v1.4.2 freeze 不改变 v1.4.0 runtime/default/current release truth。 |
| AC-012 | recovery-routing | 阻断时必须提供 reason code 和 repair/resume route。 |
| AC-013 | browser-admission | protected browser surfaces 在执行前完成 session/runner admission，并优先 attached-session 路径。 |
| AC-014 | browser-evidence-authenticity | browser-capable QA 关闭条件要求真实浏览器 evidence，transcript-only 占位件不足以过关。 |
| AC-015 | browser-runner-priority | protected-surface runner priority 明确体现 `web-access -> attached agent-browser -> playwright attach/CDP -> bare Playwright`。 |
| AC-016 | blocked-not-false-fail | 缺少 session bridge 时正式结果为 `skip/blocked` 且带 reason code，不伪装成产品失败。 |
| AC-017 | runner-learning | QA 会写入 runner/admission learning note，包含 reason、fallback/next runner 与 expiry。 |
| AC-018 | browser-lane-traceability | browser admission / browser evidence 义务被纳入 lane/status 推理与交付判定。 |

## Freeze Deliverables

- `docs/beacon/v1.4.2/SUMMARY.md`
- `docs/beacon/v1.4.2/execution/index.md`
- `docs/beacon/v1.4.2/execution/architecture-blueprint.md`
- `docs/beacon/v1.4.2/prd/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- `docs/beacon/v1.4.2/user-story/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- `docs/beacon/v1.4.2/qa/test-cases/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`

## Release-Facing Reason Codes

- `test_contract_index_missing`
- `test_contract_index_stale`
- `ac_test_mapping_missing`
- `feature_release_lane_missing`
- `feature_release_lane_failed`
- `generated_surface_sync_drift`
- `planning_line_runtime_conflict`
- `unclassified_test_failure`
- `legacy_snapshot_misclassified_as_release_blocker`
- `protected_surface_session_bridge_missing`
- `protected_surface_runner_priority_unavailable`
- `browser_evidence_placeholder_only`
- `browser_runtime_admission_missing`
- `browser_runner_learning_missing`
