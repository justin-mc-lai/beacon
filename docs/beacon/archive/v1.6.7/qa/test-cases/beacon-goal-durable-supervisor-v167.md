# QA Test Cases: beacon-goal-durable-supervisor-v167

Authority: `features/beacon-goal-durable-supervisor-v167/tests.md`

| AC | TC | Type | Note |
|----|-----|------|------|
| AC-DGS-001..014 | TC-DGS-001..014 | contract/unit | primary matrix |
| legal walks | TC-DGS-LEGAL-01..03 | legal walk | domain FSM |
| illegal | TC-DGS-ILLEGAL-01..04 | illegal | fail-closed |

Command root:

```bash
python3 -m pytest tests/test_v167_goal_durable_supervisor.py -q
```
