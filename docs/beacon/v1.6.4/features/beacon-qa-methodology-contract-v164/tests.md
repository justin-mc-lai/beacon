---
slug: beacon-qa-methodology-contract-v164
version: v1.6.4
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.4/features/beacon-qa-methodology-contract-v164/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：QA Methodology Contract v1.6.4

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-MC-001 | contract | `python3 -m pytest tests/test_v164_qa_methodology_contract.py::test_first_principles_clause -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `global-boundaries.md §5` 含「第一性原理」条款（动手前回到根本 + 最小可验证单元 + 为什么）；§5 既有 4 条条款未被修改（纯增量校验） |
| AC-002 | TC-MC-002 | contract | `python3 -m pytest tests/test_v164_qa_methodology_contract.py::test_adversarial_clause -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `global-boundaries.md §5` 含「对抗式审查」条款（最挑剔审查 + 3-5 翻车点 + 验证证据 + 不接受看起来没问题）；纯增量校验 |
| AC-003 | TC-MC-003 | contract | `python3 -m pytest tests/test_v164_qa_methodology_contract.py::test_qa_skill_contract_mandatory -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `beacon-eval-qa` SKILL.md 含"交付前对抗式审查"强制契约；缺失翻车点/验证证据 → block（reason_code `adversarial_review_missing`） |
| AC-004 | TC-MC-004 | contract | `python3 -m pytest tests/test_v164_qa_methodology_contract.py::test_adversarial_lane_mandatory -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `planner_review_runtime` adversarial lane 在 qa release 前强制触发（非仅信号触发）；输出含 3-5 翻车点 + 验证证据形状；缺失 → block |

## 验证说明

- TC 文件 `tests/test_v164_qa_methodology_contract.py` 由 implement 阶段创建；实现前 tasks 允许标注 `BLOCKED:implement`。
- TC-001/002 为 contract 层（读 global-boundaries.md §5 文本断言新条款存在 + 既有条款未改）。
- TC-003/004 为 contract 层（读 SKILL.md / 调用 planner_review_runtime 断言强制触发 + block）。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..004 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
