# Test Cases: prototype-design-intelligence-and-governed-rendering-separation

## Overview

**Feature**: prototype-design-intelligence-and-governed-rendering-separation
**Test Type**: ALL
**Version**: v1.3.11
**Generated**: 2026-05-02 21:23
**Requested Mode**: auto
**Effective Mode**: rule
**Fallback Reason**: llm_unavailable
**Memory Context**: N/A
**AC Matrix JSON**: docs/beacon/archive/v1.3.11/.machine/qa/prototype-design-intelligence-and-governed-rendering-separation.ac-test-matrix.json
**QA9 Matrix JSON**: docs/beacon/archive/v1.3.11/.machine/qa/prototype-design-intelligence-and-governed-rendering-separation.qa9-matrix.json
**Story Scenario Map JSON**: docs/beacon/archive/v1.3.11/.machine/qa/prototype-design-intelligence-and-governed-rendering-separation.story-scenario-map.json
**Prototype Plan Present**: False
**Prototype Coverage Present**: False
**Prototype Navigation Contract**: False
**Prototype Interaction Contract**: False

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-001 | TC-001 | unit | `python3 -m pytest -q -k unit --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | All unit assertions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-001.json` |
| AC-002 | TC-002 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Structured design artifact contract and projection outputs remain deterministic | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-002.json` |
| AC-003 | TC-003 | unit | `python3 -m pytest -q -k unit --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | All unit assertions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-003.json` |
| AC-004 | TC-004 | unit | `python3 -m pytest -q -k unit --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | All unit assertions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-004.json` |
| AC-101 | TC-005 | ui | `npx playwright test` | Web UI assertions and key actions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-005.json` |
| AC-102 | TC-006 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Design-role boundaries remain explicit and do not leak into render truth | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-006.json` |
| AC-103 | TC-007 | unit | `python3 -m pytest -q -k unit --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | All unit assertions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-007.json` |
| AC-104 | TC-008 | ui | `npx playwright test` | Web UI assertions and key actions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-008.json` |
| AC-201 | TC-009 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Unapproved design-skill output remains blocked from implementation render surfaces | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-009.json` |
| AC-202 | TC-010 | unit | `python3 -m pytest -q -k unit --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | All unit assertions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-010.json` |
| AC-203 | TC-011 | ui | `npx playwright test` | Web UI assertions and key actions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-011.json` |
| AC-204 | TC-012 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Production-visible copy remains the only content allowed into default render surfaces | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-012.json` |
| AC-301 | TC-013 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Preview and page outputs stay free of governance explanation leakage by default | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-013.json` |
| AC-302 | TC-014 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Review-only human-readable materials remain demoted from the implementation surface | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-014.json` |
| AC-303 | TC-015 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Production UI copy projection remains explicit and traceable | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-015.json` |
| AC-304 | TC-016 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Default UI copy remains single-semantic and page-action oriented | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-016.json` |
| AC-401 | TC-017 | unit | `python3 -m pytest -q -k unit --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | All unit assertions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-017.json` |
| AC-402 | TC-018 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Exception-surface guidance remains conditional and constrained to recovery diagnostics | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-018.json` |
| AC-403 | TC-019 | unit | `python3 -m pytest -q -k unit --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | All unit assertions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-019.json` |
| AC-404 | TC-020 | unit | `python3 -m pytest -q -k unit --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | All unit assertions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-020.json` |
| AC-501 | TC-021 | ui | `npx playwright test` | Web UI assertions and key actions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-021.json` |
| AC-502 | TC-022 | unit | `python3 -m pytest -q -k unit --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | All unit assertions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-022.json` |
| AC-503 | TC-023 | unit | `python3 -m pytest -q -k unit --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | All unit assertions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-023.json` |
| AC-504 | TC-024 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Implement renderer allowed inputs remain limited to approved implementation artifacts | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-024.json` |
| AC-005 | TC-025 | unit | `python3 -m pytest -q -k unit --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | All unit assertions pass | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-025.json` |
| AC-205 | TC-026 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Review-only human-readable materials are not treated as implementation inputs | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-026.json` |
| AC-405 | TC-027 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Implementation closure remains possible without reading design explanation prose | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-027.json` |
| AC-505 | TC-028 | unit | `python3 -m pytest -q tests/test_v135_prototype_projection_consistency.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Implement default consumption entry is limited to machine-view and implementation artifacts | `.beacon/evidence/test-results/prototype-design-intelligence-and-governed-rendering-separation/TC-028.json` |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | from AC-001 |
| TC-002 | Pending | from AC-002 |
| TC-003 | Pending | from AC-003 |
| TC-004 | Pending | from AC-004 |
| TC-005 | Pending | from AC-101 |
| TC-006 | Pending | from AC-102 |
| TC-007 | Pending | from AC-103 |
| TC-008 | Pending | from AC-104 |
| TC-009 | Pending | from AC-201 |
| TC-010 | Pending | from AC-202 |
| TC-011 | Pending | from AC-203 |
| TC-012 | Pending | from AC-204 |
| TC-013 | Pending | from AC-301 |
| TC-014 | Pending | from AC-302 |
| TC-015 | Pending | from AC-303 |
| TC-016 | Pending | from AC-304 |
| TC-017 | Pending | from AC-401 |
| TC-018 | Pending | from AC-402 |
| TC-019 | Pending | from AC-403 |
| TC-020 | Pending | from AC-404 |
| TC-021 | Pending | from AC-501 |
| TC-022 | Pending | from AC-502 |
| TC-023 | Pending | from AC-503 |
| TC-024 | Pending | from AC-504 |
| TC-025 | Pending | from AC-005 |
| TC-026 | Pending | from AC-205 |
| TC-027 | Pending | from AC-405 |
| TC-028 | Pending | from AC-505 |

---

## Delta Focus For Reopened Change

本轮 `beacon-change` 仅新增三类强约束验收：

1. `four-layer artifact topology`
   - 校验 prototype bundle 是否显式区分 `authoring / review / projection / implementation`
   - 校验 implement 不会跨层回读 review-only materials
2. `default consumption entry tightening`
   - 校验实现层默认读取入口是否只包含 `machine-view / design-artifacts / implementation-map / projection contracts`
   - 校验 `ux-prd.md / DESIGN.md / prototype-review.md / pages/*.md` 不再被默认读取
3. `review-only surface downgrade`
   - 校验 human-readable explanation materials 仍可用于审阅
   - 校验这些材料不能再被视为正式实现输入 truth
