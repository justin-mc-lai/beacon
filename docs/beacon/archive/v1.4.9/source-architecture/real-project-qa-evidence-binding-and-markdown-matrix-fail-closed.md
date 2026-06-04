# Source Architecture: Real Project QA Evidence Binding and Markdown Matrix Fail-Closed

**Feature**: `real-project-qa-evidence-binding-and-markdown-matrix-fail-closed`  
**Version**: `v1.4.9`

## 1. Runtime Surfaces

```text
beacon implement
  -> implementation run state
  -> implementation summary
  -> evidence marker

beacon implement import-evidence
  -> controlled evidence intake
  -> source refs + changed files + approver

beacon test-case
  -> reads Markdown QA tables
  -> compiles .machine/qa/*.ac-test-matrix.json
  -> fail closed on parser failure

beacon qa
  -> reads implementation evidence
  -> reads machine matrix
  -> selects project runner profile
  -> classifies outcomes
```

## 2. Source Files To Inspect During Implementation

- `beacon/commands/implement.py`
- `beacon/commands/qa.py`
- `beacon/commands/test_case.py`
- `beacon/utils/qa_feature.py`
- `beacon/utils/requirement_parsing.py`
- `beacon/utils/test_contract_governance.py`
- `beacon/utils/material_sync.py`
- `beacon/utils/artifact_paths.py`

## 3. Required Data Contracts

### 3.1 Implementation Evidence Marker

The marker must identify:

- feature
- version
- run_id or import_id
- source refs
- changed files or service directories
- summary ref
- created_at
- imported flag
- approved_by when imported

### 3.2 Markdown Matrix Compile Diagnostics

The compiler must expose:

- source markdown path
- parsed row count
- AC ids
- TC ids
- parser diagnostics
- fallback_used flag
- blocked reason when fallback would be required

### 3.3 Project Runner Profile

Initial profile support must cover Go + UniApp:

```json
{
  "backend": "go",
  "frontend": "uniapp",
  "commands": {
    "backend_target": "cd tournament-service && go test ./internal/module/rules ./internal/admin/handler ./internal/admin ./internal/admin/middleware",
    "frontend_typecheck": "cd tournament_miniapp && pnpm type-check",
    "frontend_build": "cd tournament_miniapp && pnpm build:mp-weixin",
    "route_check": "cd tournament_miniapp && pnpm check:routes"
  }
}
```

### 3.4 Admission Taxonomy

Supported classes:

- `product_failed`
- `test_failed`
- `runner_admission_blocked`
- `environment_blocked`
- `auth_session_blocked`
- `evidence_binding_missing`
- `coverage_gap`
- `truth_projection_gap`

## 4. Boundary

This source architecture only describes runtime repair surfaces. It does not create a new lifecycle stage and does not authorize QA or release verdicts.
