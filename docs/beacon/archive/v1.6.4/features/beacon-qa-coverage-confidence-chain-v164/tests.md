---
slug: beacon-qa-coverage-confidence-chain-v164
version: v1.6.4
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.4/features/beacon-qa-coverage-confidence-chain-v164/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：QA Coverage Confidence Chain v1.6.4

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-CC-001 | contract | `python3 -m pytest tests/test_v164_qa_confidence_chain.py::test_chain_model_bottom_up -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 置信度传递模型自下而上：unit→interface→...→browser_e2e；上层置信度依赖下层覆盖传递（下层缺失时上层置信度降低） |
| AC-002 | TC-CC-002 | contract | `python3 -m pytest tests/test_v164_qa_confidence_chain.py::test_gap_detection -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 下层 skipped/missing/blocked 时，上层标记 `downstream_gap`；gap 来源可追溯（哪一层断） |
| AC-003 | TC-CC-003 | contract | `python3 -m pytest tests/test_v164_qa_confidence_chain.py::test_confidence_chain_field -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `build_qa_profile_completeness` 输出含 `confidence_chain`（每层置信度 + 依赖来源 + gap 标记）；projection JSON 同步该字段 |
| AC-004 | TC-CC-004 | contract | `python3 -m pytest tests/test_v164_qa_confidence_chain.py::test_break_chain_blocks -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 链终点 browser_e2e 缺失 或 任一依赖层 gap → profile `partial`/`blocked`，不显示 `complete`；evidence 不被记为 full pass |
| AC-005 | TC-CC-005 | integration | `python3 -m pytest tests/test_v164_qa_confidence_chain.py::test_browser_e2e_chain_terminal -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | browser_e2e 作为链终点纳入置信度链；e2e 置信度依赖下层 non-browser 覆盖；与 Phase 1 `playwright-extension` runner 注册表共存 |

## 验证说明

- TC 文件 `tests/test_v164_qa_confidence_chain.py` 由 implement 阶段创建；实现前 tasks 允许标注 `BLOCKED:implement`。
- TC-001..004 为 contract 层（构造 layer coverage payload + 调用 `build_qa_profile_completeness` 断言 confidence_chain 形状）。
- TC-005 为 integration 层，需 Phase 1 的 `playwright-extension` runner 注册（import 校验共存）。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..005 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
