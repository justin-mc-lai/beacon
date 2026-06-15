# Beacon v1.6.0 Summary

v1.6.0 opens the Beacon skill harness taxonomy line.

Normal Beacon production and consumption continue to use package-authoritative truth:

```text
truth-map resolver -> features/<slug>/{truth,tests,tasks,evidence}.md
```

The v1.6.0 human-facing lifecycle language is:

```text
plan -> truth -> generate -> evaluate -> release
```

Legacy `prd`, `user-story`, and `test-case` names are not v1.6.0 primary skill categories. They remain migration, rebuild, or absorb concepts under package-authoritative truth.

Primary v1.6.0 features:

- `beacon-skill-harness-taxonomy-v160`
- `beacon-loop-native-runner-and-automation-retirement` (frozen)
- `beacon-loop-goal-closed-loop-orchestrator` (frozen — goal delivery orchestrator, AC-031..AC-039)
