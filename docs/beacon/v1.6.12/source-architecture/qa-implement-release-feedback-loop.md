# Beacon v1.6.12 QA, Implement, Release, And Feedback Loop

## Main Modules

- QA: `beacon/commands/qa.py`, `beacon/utils/qa_feature.py`, `beacon/utils/qa_precision.py`
- Implement: `beacon/commands/implement.py`, `beacon/utils/implement_native.py`
- Release/Gate: `beacon/commands/gate.py`, `beacon/commands/release.py`, `beacon/commands/report.py`, `beacon/commands/status.py`
- Learning: `beacon/utils/learning_loop.py`, `beacon/utils/debug_feedback.py`

## Main Loop

```text
qa finding
→ release/gate judgement
→ implement follow-up
→ technical archive
→ requirement rewrite
→ next QA / next version
```

