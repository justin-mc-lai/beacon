# Beacon v1.5.2 Summary

v1.5.2 completes the truth-source cutover.

Normal Beacon production and consumption must use:

```text
truth-map resolver -> features/<slug>/{truth,tests,tasks,evidence}.md
```

Legacy `prd/`, `user-story/`, and `qa/test-cases/` are no longer canonical truth surfaces. They are only rebuild/absorb artifacts owned by `doctor` and `change`.

