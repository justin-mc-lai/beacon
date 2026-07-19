---
slug: loom-skill-score-corpus-v1
version: v2.0.0
status: frozen
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/loom-skill-score-corpus-v1/truth.md
---

# Tests: loom-skill-score-corpus-v1

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-169 | TC-W5-001 | contract | `loom skill-score --corpus skill-score-corpus.v1` | fields |
| AC-169 | TC-W5-002 | negative | `score without corpus` | skill_score_corpus_missing |

## Legal / Illegal

| TC ID | Path | Assertion |
|-------|------|-----------|
| TC-W5-LEGAL-01 | legal walk | happy path satisfies AC |
| TC-W5-ILLEGAL-01 | illegal | fail-closed reason_code |
