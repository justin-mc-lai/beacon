---
slug: beacon-protected-path-denylist-v165
version: v1.6.5
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.5/features/beacon-protected-path-denylist-v165/truth.md
parser_contract: beacon-feature-package-v2
---

# Evidence Index: Protected Path Denylist v1.6.5

## Authority Surface

| surface | authority | artifact |
|---|---|---|
| truth.md | requirement_truth | docs/beacon/v1.6.5/features/beacon-protected-path-denylist-v165/truth.md |
| tests.md | test_truth | docs/beacon/v1.6.5/features/beacon-protected-path-denylist-v165/tests.md |
| tasks.md | requirement_truth | docs/beacon/v1.6.5/features/beacon-protected-path-denylist-v165/tasks.md |
| global-boundaries.md | requirement_truth | docs/beacon/global-boundaries.md |

## Source Refs

- Program graph: docs/beacon/v1.6.5/programs/beacon-oss-borrow-hardening-v165/feature-graph.md
- User decision: denylist enters global boundaries as cross-version principle.

## Implementation Evidence

| Surface | Authority | Canonical Artifact | Status | Route |
|---|---|---|---|---|
| implementation | implementation_evidence | `docs/beacon/global-boundaries.md` | implemented | beacon-gen-implement |
| implementation | implementation_evidence | `beacon/utils/protected_paths.py` | implemented | beacon-gen-implement |
| integration | implementation_evidence | `beacon/utils/workspace_admission.py` | implemented | beacon-gen-implement |
| tests | test_evidence | `tests/test_v165_protected_path_denylist.py` | passing | beacon-eval-qa |

Focused command: `python3 -m pytest tests/test_v165_protected_path_denylist.py -q`
