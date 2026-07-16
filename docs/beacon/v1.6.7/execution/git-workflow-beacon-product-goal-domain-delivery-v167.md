# Git Workflow — Product Goal Domain Delivery Program

- feature: `beacon-product-goal-domain-delivery-v167`
- version: `v1.6.7`
- expected_branch: `beacon/v1.6.7`
- branch_prefix: `beacon/`
- base_branch: `main`
- branch_resolution_mode: `program-level`
- dedicated_worktree_path: `.`
- require_clean_worktree_for_switch: `false`

## Notes

- Program lakes share aggregation branch `beacon/v1.6.7`.
- After merge, truth_canonical `main` is accepted for QA/release admission.
- Do **not** inherit `beacon-git-scope-graph-v167` feature branch for these lakes.
