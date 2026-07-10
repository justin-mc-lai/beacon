---
slug: beacon-loop-token-budget-v165
version: v1.6.5
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.5/features/beacon-loop-token-budget-v165/truth.md
parser_contract: beacon-feature-package-v2
---

# Evidence Index: Loop Token Budget v1.6.5

## Authority Surface

| surface | authority | artifact |
|---|---|---|
| truth.md | requirement_truth | docs/beacon/v1.6.5/features/beacon-loop-token-budget-v165/truth.md |
| tests.md | test_truth | docs/beacon/v1.6.5/features/beacon-loop-token-budget-v165/tests.md |
| tasks.md | requirement_truth | docs/beacon/v1.6.5/features/beacon-loop-token-budget-v165/tasks.md |

## Source Refs

- Program graph: docs/beacon/v1.6.5/programs/beacon-oss-borrow-hardening-v165/feature-graph.md
- Depends on: docs/beacon/v1.6.5/features/beacon-loop-pattern-registry-v165/truth.md

## Implementation Evidence

| Surface | Authority | Canonical Artifact | Status | Route |
|---|---|---|---|---|
| implementation | implementation_evidence | `beacon/utils/loop_budget.py` | implemented | beacon-gen-implement |
| implementation | implementation_evidence | `beacon/commands/status.py` | implemented | beacon-gen-implement |
| integration | implementation_evidence | `docs/beacon/v1.6.5/loop-patterns/registry.yaml` | implemented | beacon-gen-implement |
| tests | test_evidence | `tests/test_v165_loop_token_budget.py` | passing | beacon-eval-qa |

Focused command: `python3 -m pytest tests/test_v165_loop_token_budget.py -q`
