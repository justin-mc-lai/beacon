# Test Cases: beacon-implement-skill-runner

## Overview

**Feature**: beacon-implement-skill-runner
**Test Type**: ALL
**Version**: v1.1.4
**Generated**: 2026-03-20 12:00
**Memory Context**: N/A
**AC Matrix JSON**: docs/beacon/v1.1.4/qa/test-cases/beacon-implement-skill-runner.ac-test-matrix.json
**QA9 Matrix JSON**: docs/beacon/v1.1.4/qa/test-cases/beacon-implement-skill-runner.qa9-matrix.json
**Prototype Navigation Contract**: False
**Prototype Interaction Contract**: False

---

## Gate Summary

- Gate0 输入完整性: Pass（已有 User Story + PRD）
- Gate1 冲突/未决项: Pass（当前需求稿未声明阻塞级 unresolved conflict）
- Gate2 AC→TC 映射: Pass（26/26 AC 已映射）

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-001 | TC-001 | unit | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Beacon exposes top-level implement command group | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-001.json` |
| AC-002 | TC-002 | smoke | `python3 -m beacon.main implement list-runners` | Implement group exposes run/status/list-runners subcommands | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-002.json` |
| AC-003 | TC-003 | unit | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | implement run accepts --runner and does not hardcode OMX | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-003.json` |
| AC-004 | TC-004 | contract | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Runner resolution follows CLI > project > global > default priority | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-004.json` |
| AC-005 | TC-005 | contract | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Project config can register custom implementation runners/skills | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-005.json` |
| AC-006 | TC-006 | integration | `python3 -m pytest -q tests/test_v114_workflow_implement_integration.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | OMX runner assembles Beacon artifacts into executable implementation task input | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-006.json` |
| AC-007 | TC-007 | contract | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | implement run writes structured request.json with source-of-truth and artifact paths | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-007.json` |
| AC-008 | TC-008 | contract | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Beacon validates structured result.json from external runner | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-008.json` |
| AC-009 | TC-009 | integration | `python3 -m pytest -q tests/test_v114_workflow_implement_integration.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | implement runtime emits stdout/stderr/command/request/result evidence | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-009.json` |
| AC-010 | TC-010 | integration | `python3 -m pytest -q tests/test_v114_workflow_implement_integration.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Successful implement run writes .beacon/state/implementation-<feature>.json | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-010.json` |
| AC-011 | TC-011 | integration | `python3 -m pytest -q tests/test_v114_workflow_implement_integration.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Beacon writes implementation-summary JSON and Markdown under execution/ | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-011.json` |
| AC-012 | TC-012 | integration | `python3 -m pytest -q tests/test_v114_workflow_implement_integration.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Workflow implementation stage can delegate to beacon implement run | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-012.json` |
| AC-013 | TC-013 | regression | `python3 -m pytest -q -k implement --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Missing runner config preserves legacy implementation_command path and Blocked fallback | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-013.json` |
| AC-014 | TC-014 | integration | `python3 -m pytest -q tests/test_v114_workflow_implement_integration.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | implement completion can trigger review spec for artifact update assessment | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-014.json` |
| AC-015 | TC-015 | integration | `python3 -m pytest -q tests/test_v114_workflow_implement_integration.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | implement completion can trigger review quality for gate-ready assessment | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-015.json` |
| AC-016 | TC-016 | contract | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Runner result supports artifact_updates for user-story/prd/test-case/prototype | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-016.json` |
| AC-017 | TC-017 | unit | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | docs/beacon remains long-term truth source while .beacon/implement is runtime only | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-017.json` |
| AC-018 | TC-018 | exception | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Implement stays adapter-scoped and does not expand into scheduler/orchestrator behavior | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-018.json` |
| AC-019 | TC-019 | unit | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Runner registry supports at least command and command-skill types | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-019.json` |
| AC-020 | TC-020 | functional | `python3 -m beacon.main implement run beacon-implement-skill-runner --runner omx --project . --version v1.1.4 --dry-run` | Beacon assembles feature artifact context into runner task prompt payload | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-020.json` |
| AC-021 | TC-021 | exception | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Missing or invalid runner result fails with explicit reason codes | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-021.json` |
| AC-022 | TC-022 | smoke | `python3 -m beacon.main implement list-runners` | implement status shows runner/run/request/result/marker/review state | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-022.json` |
| AC-023 | TC-023 | contract | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | implementation.runners.<id> schema includes type/command/args/env/timeout/result_file | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-023.json` |
| AC-024 | TC-024 | integration | `python3 -m pytest -q tests/test_v114_workflow_implement_integration.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | OMX runner supports configured skill prefix and task template binding | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-024.json` |
| AC-025 | TC-025 | exception | `python3 -m pytest -q tests/test_v114_implement_command.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Runner failure paths emit stable reason codes | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-025.json` |
| AC-026 | TC-026 | regression | `python3 -m pytest -q -k implement --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | v1.1.4 materials explicitly describe draft-stage semantics for implement capability | `.beacon/evidence/test-results/beacon-implement-skill-runner/TC-026.json` |

---

## QA9 Coverage Mapping

| TC ID | QA Type | Title | Priority |
|------|---------|-------|----------|
| TC-001 | unit | beacon-implement-skill-runner unit :: Command Surface | P0 |
| TC-002 | smoke | beacon-implement-skill-runner smoke :: Subcommands | P0 |
| TC-003 | unit | beacon-implement-skill-runner unit :: Runner Model | P0 |
| TC-004 | contract | beacon-implement-skill-runner contract :: Config Priority | P0 |
| TC-005 | contract | beacon-implement-skill-runner contract :: User-defined Skill | P0 |
| TC-006 | integration | beacon-implement-skill-runner integration :: OMX Example | P0 |
| TC-007 | contract | beacon-implement-skill-runner contract :: Request Contract | P0 |
| TC-008 | contract | beacon-implement-skill-runner contract :: Result Contract | P0 |
| TC-009 | integration | beacon-implement-skill-runner integration :: Runtime Evidence | P0 |
| TC-010 | integration | beacon-implement-skill-runner integration :: Implementation Marker | P0 |
| TC-011 | integration | beacon-implement-skill-runner integration :: Execution Summary | P0 |
| TC-012 | integration | beacon-implement-skill-runner integration :: Workflow Integration | P0 |
| TC-013 | regression | beacon-implement-skill-runner regression :: Backward Compatibility | P1 |
| TC-014 | integration | beacon-implement-skill-runner integration :: Spec Writeback | P0 |
| TC-015 | integration | beacon-implement-skill-runner integration :: Quality Writeback | P0 |
| TC-016 | contract | beacon-implement-skill-runner contract :: Artifact Update Semantics | P0 |
| TC-017 | unit | beacon-implement-skill-runner unit :: Source of Truth | P0 |
| TC-018 | exception | beacon-implement-skill-runner exception :: Boundary | P1 |
| TC-019 | unit | beacon-implement-skill-runner unit :: Runner Types | P0 |
| TC-020 | functional | beacon-implement-skill-runner functional :: Task Prompt Assembly | P1 |
| TC-021 | exception | beacon-implement-skill-runner exception :: Result Validation | P1 |
| TC-022 | smoke | beacon-implement-skill-runner smoke :: Reviewability | P0 |
| TC-023 | contract | beacon-implement-skill-runner contract :: Config Model | P0 |
| TC-024 | integration | beacon-implement-skill-runner integration :: OMX Skill Binding | P0 |
| TC-025 | exception | beacon-implement-skill-runner exception :: Reason Codes | P1 |
| TC-026 | regression | beacon-implement-skill-runner regression :: Draft Stage | P1 |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | from AC-001 |
| TC-002 | Pending | from AC-002 |
| TC-003 | Pending | from AC-003 |
| TC-004 | Pending | from AC-004 |
| TC-005 | Pending | from AC-005 |
| TC-006 | Pending | from AC-006 |
| TC-007 | Pending | from AC-007 |
| TC-008 | Pending | from AC-008 |
| TC-009 | Pending | from AC-009 |
| TC-010 | Pending | from AC-010 |
| TC-011 | Pending | from AC-011 |
| TC-012 | Pending | from AC-012 |
| TC-013 | Pending | from AC-013 |
| TC-014 | Pending | from AC-014 |
| TC-015 | Pending | from AC-015 |
| TC-016 | Pending | from AC-016 |
| TC-017 | Pending | from AC-017 |
| TC-018 | Pending | from AC-018 |
| TC-019 | Pending | from AC-019 |
| TC-020 | Pending | from AC-020 |
| TC-021 | Pending | from AC-021 |
| TC-022 | Pending | from AC-022 |
| TC-023 | Pending | from AC-023 |
| TC-024 | Pending | from AC-024 |
| TC-025 | Pending | from AC-025 |
| TC-026 | Pending | from AC-026 |

---

## Recommended Verification Commands

- `python3 -m pytest -q tests/test_v114_implement_command.py`
- `python3 -m pytest -q tests/test_v114_implement_command.py`
- `python3 -m pytest -q tests/test_v114_workflow_implement_integration.py`
- `python3 -m beacon.main implement list-runners`
- `python3 -m beacon.main implement status beacon-implement-skill-runner --project . --version v1.1.4`

## Risk Notes

- 重点风险：Runner 配置优先级、OMX skill 绑定、request/result 契约漂移、需求物料回填一致性。
- Draft 阶段允许当前实现尚未全部存在；Blocked 条件应以 Runner 缺失、结果契约缺失、回填失效等显式 reason code 表达。
