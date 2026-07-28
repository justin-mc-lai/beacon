---
slug: design-craft-absorption-v1611
version: v1.6.11
revision_id: R1
materials_status: current
---

# Tests: design-craft-absorption-v1611

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-CRAFT-001 | AC-CRAFT-001 | `python3 -m pytest -q tests/test_design_craft_absorption_v1611.py -k public_surface_no_new_lifecycle --tb=no` | craft stays under beacon-design; no new 1+6 public skill or lifecycle stage |
| TC-CRAFT-002 | AC-CRAFT-002 | `python3 -m pytest -q tests/test_design_craft_absorption_v1611.py -k craft_refs_selectable --tb=no` | baseline/a11y/motion/improve progressive refs exist and are router-selectable |
| TC-CRAFT-003 | AC-CRAFT-003 | `python3 -m pytest -q tests/test_design_craft_absorption_v1611.py -k support_only_schema --tb=no` | payload missing support_only=true or truth_source=false fails closed |
| TC-CRAFT-004 | AC-CRAFT-004 | `python3 -m pytest -q tests/test_design_craft_absorption_v1611.py -k improve_write_guard --tb=no` | improve product-source write is rejected; plans only under craft plan root |
| TC-CRAFT-005 | AC-CRAFT-005 | `python3 -m pytest -q tests/test_design_craft_absorption_v1611.py -k improve_proof_gate --tb=no` | findings lacking contract/runtime/correction never enter plans |
| TC-CRAFT-006 | AC-CRAFT-006 | `python3 -m pytest -q tests/test_design_craft_absorption_v1611.py -k binding_routes --tb=no` | promise-changing findings only recommend prototype_adapt or change_refreeze |
| TC-CRAFT-007 | AC-CRAFT-007 | `python3 -m pytest -q tests/test_design_craft_absorption_v1611.py -k router_max_modules --tb=no` | auto router selects <=2 modules by default and never silent-all-four |
| TC-CRAFT-008 | AC-CRAFT-008 | `python3 -m pytest -q tests/test_design_craft_absorption_v1611.py -k metadata_deferred --tb=no` | SEO/metadata and registry long-tail are explicit non-goals |
| TC-CRAFT-ILLEGAL | AC-CRAFT-001 | `python3 -m pytest -q tests/test_design_craft_absorption_v1611.py -k craft_illegal_transition --tb=no` | craft→truth_freeze / craft→release_go / improve→product_write are rejected |
