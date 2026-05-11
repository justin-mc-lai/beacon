# Test Cases: beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation

## Overview

**Feature**: `beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation`  
**Test Type**: `contract + integration + regression`  
**Version**: `v1.4.3`  
**Status**: `freeze-ready`  
**Primary Truth**: `docs/beacon/v1.4.3/prd/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`  
**Upstream User Story**: `docs/beacon/v1.4.3/user-story/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`  
**Global Boundary Truth**: `docs/beacon/global-boundaries.md`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-US001-001 | contract | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "ceo_subfeature_acceptance_passed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | CEO review subfeature acceptance is passed and projected into runtime acceptance artifacts | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US001-001.json` |
| AC-002 | TC-US002-001 | contract | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "ceo_subfeature_acceptance_passed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | CEO review subfeature acceptance includes explicit strategic judgment support inside the accepted closure | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US002-001.json` |
| AC-003 | TC-US003-001 | regression | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "ceo_subfeature_acceptance_passed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | CEO review subfeature acceptance proves truth-safe routing without direct truth freeze | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US003-001.json` |
| AC-004 | TC-US004-001 | contract | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "design_subfeature_acceptance_passed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Design review subfeature acceptance is passed and projected into runtime acceptance artifacts | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US004-001.json` |
| AC-005 | TC-US005-001 | integration | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "design_subfeature_acceptance_passed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Design review subfeature acceptance proves `design-review -> prototype -> implement` layering when triggered | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US005-001.json` |
| AC-006 | TC-US006-001 | regression | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "design_subfeature_acceptance_passed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Design review subfeature acceptance proves prototype de-overloading is part of accepted closure | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US006-001.json` |
| AC-007 | TC-US007-001 | contract | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "learn_subfeature_acceptance_passed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Governed learning subfeature acceptance is passed and projected into runtime acceptance artifacts | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US007-001.json` |
| AC-008 | TC-US008-001 | integration | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "learn_subfeature_acceptance_passed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Governed learning subfeature acceptance proves default learning injection is part of accepted closure | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US008-001.json` |
| AC-009 | TC-US009-001 | integration | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "learn_subfeature_acceptance_passed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Governed learning subfeature acceptance proves applied learning remains visible with staleness/conflict context | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US009-001.json` |
| AC-010 | TC-US010-001 | regression | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "learn_subfeature_acceptance_passed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Governed learning subfeature acceptance proves stale/conflicting learning is downgraded or pruned | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US010-001.json` |
| AC-011 | TC-US011-001 | integration | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "learn_subfeature_acceptance_passed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Governed learning subfeature acceptance proves route explainability is part of accepted closure | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US011-001.json` |
| AC-012 | TC-US012-001 | regression | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "version_line_preserves_boundary_contract" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | The umbrella version line keeps the public lifecycle unchanged and keeps review surfaces as support surfaces | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US012-001.json` |
| AC-013 | TC-US013-001 | contract | `python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k "umbrella_subfeatures_are_qa_closed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | v1.4.3 aggregates 3 freeze-ready subfeatures whose implementation is QA-accepted as umbrella evidence | `.beacon/evidence/test-results/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation/TC-US013-001.json` |

## Execution Results

| Test ID | Result | Notes |
| --- | --- | --- |
| TC-US001-001 | Passed | Aggregated CEO subfeature acceptance artifacts are present and projected into runtime acceptance evidence |
| TC-US002-001 | Passed | Aggregated CEO subfeature acceptance proves explicit strategic judgment support is in accepted closure |
| TC-US003-001 | Passed | Aggregated CEO subfeature acceptance proves truth-safe routing without direct truth freeze |
| TC-US004-001 | Passed | Aggregated design subfeature acceptance artifacts are present and projected into runtime acceptance evidence |
| TC-US005-001 | Passed | Aggregated design subfeature acceptance preserves `design-review -> prototype -> implement` layering when triggered |
| TC-US006-001 | Passed | Aggregated design subfeature acceptance proves prototype de-overloading is part of accepted closure |
| TC-US007-001 | Passed | Aggregated learn subfeature acceptance artifacts are present and projected into runtime acceptance evidence |
| TC-US008-001 | Passed | Aggregated learn subfeature acceptance proves default learning injection is part of accepted closure |
| TC-US009-001 | Passed | Aggregated learn subfeature acceptance proves applied learning remains visible with staleness/conflict context |
| TC-US010-001 | Passed | Aggregated learn subfeature acceptance proves stale/conflicting learning is downgraded or pruned |
| TC-US011-001 | Passed | Aggregated learn subfeature acceptance proves route explainability is part of accepted closure |
| TC-US012-001 | Passed | Umbrella execution boundary contract preserves support-surface role and avoids a second implementation surface |
| TC-US013-001 | Passed | All 3 subfeatures remain QA-accepted and available as umbrella aggregation evidence |

## Freeze Gate Notes

- Current test-case package defines umbrella QA as an aggregation contract over the 3 implemented subfeatures.
- The matrix validates acceptance transactions, scorecards, and execution boundary truth instead of introducing a second independent implementation surface.
- Release-facing umbrella claims require all 3 subfeatures to remain QA-accepted and material-sync clean.

## Diagram Truth

- `branch-flow`
  - `problem signal -> ceo-review -> prd/story/case truth -> design-review -> prototype? -> implement -> qa -> release`
  - `learning record -> learn surface -> default injection -> support-surface explanation -> next run`
- `decision-priority`
  - `global boundaries > frozen truth > gate > review outputs > learning hints`
  - `design-review challenge > prototype packaging`
  - `visible learning recall > hidden heuristic reuse`
- `state-machine`
  - `latent_learning -> readable -> injected -> audited`
  - `overloaded_prototype -> clarified -> handoff_only`
  - `thin_support_surface -> explainable_support_surface`
