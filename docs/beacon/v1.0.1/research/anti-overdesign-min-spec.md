# Beacon 反过度设计最小规范（1页）

> 目标：确保 Skill/Workflow 不失真、不偏移；以真实证据驱动迭代。

## A. 四条设计铁律（MUST）

1. **Truth-first**：真实执行证据 > 文本说明。
2. **Link-first**：Story→AC→TC→Code→Run→Evidence 必须全链路可追溯。
3. **Default-strict**：默认严格；放宽必须显式并记录风险。
4. **Single-source**：事实源唯一；报告/文档由事实自动生成。

---

## B. 最小事实模型（禁止额外抽象）

仅保留三类对象：
- `event`（阶段事件）
- `edge`（追踪关系边）
- `evidence`（可校验工件）

最小字段（必填）：
- `run_id, stage, story_id, ac_id, tc_id, impl_ref, evidence_ref, ts`

> 任意新增字段，需证明能直接提升 gate 判定质量，否则不加。

---

## C. 防失真约束（MUST NOT）

1. **No Silent Pass**：无证据不得 PASS。
2. **No Heuristic Pass**：关键词推断不得替代真实 evidence。
3. **No Multi-Truth**：同一事实不得多处手工维护。
4. **No Orphan Node**：AC/TC/Code 任一断链即 FAIL。

---

## D. Gate 规则（可直接接入）

新增 reason codes：
- `traceability_broken`
- `evidence_not_verifiable`
- `heuristic_pass_detected`
- `multi_source_truth_conflict`

严格模式判定：
1. `story_id/ac_id/tc_id/impl_ref/evidence_ref` 任一缺失 → `traceability_broken`（BLOCK）
2. `evidence_ref` 文件不存在/不可解析 → `evidence_not_verifiable`（BLOCK）
3. PASS 仅由启发式推断得出、无真实执行产物 → `heuristic_pass_detected`（BLOCK）
4. 同一 run 同一对象在多源状态冲突 → `multi_source_truth_conflict`（BLOCK）

---

## E. 最小指标（每轮必须产出）

- `trace_coverage = linked_tc / total_tc`（目标 100%）
- `evidence_valid_rate = valid_evidence / required_evidence`（目标 100%）
- `heuristic_pass_count`（目标 0）
- `orphan_node_count`（目标 0）

---

## F. 反过度设计准入闸门

新增任何流程/字段前，必须同时满足：
1. 直接提升上面 4 个指标之一；
2. 降低人工维护成本；
3. 可被 gate 自动验证。

任一不满足：本版本不纳入。
