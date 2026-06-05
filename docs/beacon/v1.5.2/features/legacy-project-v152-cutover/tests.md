# Tests: legacy-project-v152-cutover

## Coverage Matrix

| AC ID | TC ID | Layer | Assertion |
|-------|-------|-------|-----------|
| AC-001 | TC-001 | integration | A project with legacy triptych, missing package, missing governance MD, missing projection, or stale agent surface is classified as `legacy_or_mixed_truth_state`. |
| AC-002 | TC-002 | integration | `beacon-change-refreeze` blocks direct refreeze and recommends the cutover route when preflight reports legacy/mixed state. |
| AC-003 | TC-003 | integration | The cutover wrapper emits ordered phases and can run/report inventory, package validation, truth-map verify, governance verify, agent refresh, and resume state. |
| AC-004 | TC-004 | contract | Package validation treats `features/<slug>/truth.md` and `tests.md` as authority; legacy triptych conflicts are reported as drift with package truth winning. |
| AC-005 | TC-005 | integration | `doctor metadata verify` fails closed when governance MD is missing, active version contract is missing, or sqlite projection source hash drifts. |
| AC-006 | TC-006 | contract | Stale skills/rules that describe old triptych as normal v1.5.2 authority are detected and route to agent-surface setup/verify. |
| AC-007 | TC-007 | integration | freeze/refreeze/implement/QA/release cannot pass while any cutover plane is blocked or contradictory. |
| AC-008 | TC-008 | integration | After all cutover phases pass, the transaction returns the original requested route, including `beacon change ... --refreeze-chain` for refreeze intent. |
| AC-001 | TC-009 | unit | Inventory mode is read-only and does not mutate package, governance MD, sqlite projection, or agent surface files. |
| AC-003 | TC-010 | contract | A dry-run cutover report includes exact next commands for every blocked phase. |
| AC-009 | TC-011 | contract | `beacon implement plan` resolves package `tasks.md` and reports task alignment even when technical review blocks execution admission. |
| AC-009 | TC-012 | integration | Implementation progress updates execution plan/progress artifacts and does not write completion state back into `features/<slug>/tasks.md`. |
| AC-010 | TC-013 | contract | No standalone default `beacon-truth-cutover` public skill is required; `beacon truth-cutover --help` is available and legacy/mixed preflight routes existing human surfaces to `beacon-truth-cutover` / `truth-cutover run`. |
| AC-010 | TC-014 | integration | Doctor reports `truth_source_mismatch` with low-cognitive-load explanation and exact repair commands when feature package authority, truth-map projection, machine mirrors, governance, or legacy triptych contradict v1.5.2 authority. |
| AC-010 | TC-015 | regression | `technical_review_contract` and `beacon change` accept relative `--project .` without subpath or version drift; `--version v1.5.2` remains the selected and recommended refreeze version. |

## Validation Note

Coverage truth lives in this package for v1.5.2. Generated QA matrices and runtime JSON may project from it, but they are not requirement authority.
