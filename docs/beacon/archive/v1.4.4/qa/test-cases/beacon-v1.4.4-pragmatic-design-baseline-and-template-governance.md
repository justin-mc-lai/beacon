# Test Cases: beacon-v1.4.4-pragmatic-design-baseline-and-template-governance

## Overview

**Feature**: `beacon-v1.4.4-pragmatic-design-baseline-and-template-governance`  
**Version**: `v1.4.4`  
**Status**: `freeze-ready`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-DESIGN44-001 | contract | `python3 -m pytest -q tests/test_v144_design_baseline.py -k "anti_ai_contract_exists"` | default anti-AI UI/UX baseline contract exists |
| AC-002 | TC-DESIGN44-002 | contract | `python3 -m pytest -q tests/test_v144_design_baseline.py -k "design_review_consumes_anti_ai_rubric"` | `design-review` consumes hierarchy/state/interaction plus anti-AI baseline checks |
| AC-003 | TC-DESIGN44-003 | contract | `python3 -m pytest -q tests/test_v144_design_templates.py -k "fixed_three_templates_only"` | exactly 3 default templates are exposed |
| AC-004 | TC-DESIGN44-004 | contract | `python3 -m pytest -q tests/test_v144_design_templates.py -k "template_sources_bound_to_apple_vercel"` | templates bind to normalized `apple` / `vercel` sources |
| AC-005 | TC-DESIGN44-005 | integration | `python3 -m pytest -q tests/test_v144_prototype_projection.py -k "prototype_projects_template_truth"` | `prototype` projects template truth and anti-AI contract into design assets |
| AC-006 | TC-DESIGN44-006 | integration | `python3 -m pytest -q tests/test_v144_implement_design_consumption.py -k "implement_consumes_same_design_truth"` | `implement` consumes the same template and interaction baseline truth |
| AC-007 | TC-DESIGN44-007 | regression | `python3 -m pytest -q tests/test_v144_qa_design_drift.py -k "qa_detects_design_drift_and_ai_slop"` | `qa` detects design drift and anti-AI baseline violations |
| AC-008 | TC-DESIGN44-008 | boundary | `python3 -m pytest -q tests/test_v144_design_templates.py -k "external_reference_not_runtime_dependency"` | external reference repositories stay non-runtime dependencies |
