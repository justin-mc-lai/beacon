# Beacon Implementation Plan

- plan_id: `plan-beacon-prototype-design-governance-loop-r1`
- feature: `beacon-prototype-design-governance-loop`
- version: `v1.1.12`
- revision_id: `R1`
- baseline_hash: `sha256:a8562a43eab6f43ff71f45f5bd64249e82efac0c50468d85f03c13e984b585b1`
- plan_hash: `sha256:c9c453f975161727e5a7739005e18a31b504d9eb314ec310d66c98c728498c31`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.1.12/user-story/beacon-prototype-design-governance-loop.md`
- prd: `docs/beacon/archive/v1.1.12/prd/beacon-prototype-design-governance-loop.md`
- test_case: `docs/beacon/archive/v1.1.12/qa/test-cases/beacon-prototype-design-governance-loop.md`
- ac_matrix: `docs/beacon/archive/v1.1.12/.machine/qa/beacon-prototype-design-governance-loop.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.1.12/.machine/qa/beacon-prototype-design-governance-loop.story-scenario-map.json`

## Tasks

### ITASK-001 — FR-001 新增 Design Brief 编译层
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-002
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 新增 Design System Contract
- status: `completed`
- mapped_ac_ids: AC-005A
- mapped_test_ids: TEST-008
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 `frontend-design` 进入 generation 面
- status: `completed`
- mapped_ac_ids: AC-002A
- mapped_test_ids: TEST-003
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 `web-design-guidelines` 进入 review 面
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-011
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 Review 输出继续决策
- status: `completed`
- mapped_ac_ids: AC-008, AC-009
- mapped_test_ids: TEST-012, TEST-013
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 Bounded Autoresearch Loop
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — FR-007 Keep / Discard Ledger
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TEST-014
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — FR-008 Freeze / Gate 需要设计真值
- status: `completed`
- mapped_ac_ids: AC-011
- mapped_test_ids: TEST-015
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- target_modules: -

### ITASK-009 — FR-009 单一版本真相源
- status: `completed`
- mapped_ac_ids: AC-013
- mapped_test_ids: TEST-018
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- target_modules: -

### ITASK-010 — FR-010 navigator 必须 profile-aware first
- status: `completed`
- mapped_ac_ids: AC-014
- mapped_test_ids: TEST-019
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- target_modules: -

### ITASK-011 — FR-011 Project Execution Adapter Capability Boundary
- status: `completed`
- mapped_ac_ids: AC-015
- mapped_test_ids: TEST-020
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- target_modules: -

### ITASK-012 — FR-012 Typed Learning Plane Surfaces
- status: `completed`
- mapped_ac_ids: AC-016
- mapped_test_ids: TEST-021
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- target_modules: -

### ITASK-013 — FR-013 Takeover Baseline Runtime Gate
- status: `completed`
- mapped_ac_ids: AC-017
- mapped_test_ids: TEST-022
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- target_modules: -

### ITASK-014 — FR-014 Project Docs 只作为只读 Contract Inputs
- status: `completed`
- mapped_ac_ids: AC-018, AC-003, AC-004, AC-004A, AC-005, AC-006, AC-006A, AC-011A, AC-012
- mapped_test_ids: TEST-023, TEST-004, TEST-005, TEST-006, TEST-007, TEST-009, TEST-010, TEST-016, TEST-017
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- target_modules: -
