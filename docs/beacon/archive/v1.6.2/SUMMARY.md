# Beacon v1.6.2 Summary

v1.6.2 closes the **host vs CLI git governance gap**: a version-scoped **workspace admission** surface, **dedicated worktree** as the default collaboration lane, and **defense-in-depth** (skill soft + CLI hard + hook hardening where hosts support it).

Lifecycle language unchanged:

```text
plan -> truth -> generate -> evaluate -> release
```

Package-authoritative truth:

```text
truth-map resolver -> features/<slug>/{truth,tests,tasks,evidence}.md
```

Governance anchor:

```text
docs/beacon/governance/project-version-governance.md
```

Primary v1.6.2 features (change loop):

- `beacon-global-workspace-git-admission-v162` — **Must:** slash/skill `GIT_ADMISSION` Step 0 + `beacon workspace admit` + CLI fail-closed + dirty-only invalidation; **Should:** hook Write deny; **no TTL** (**change draft R2**)

Upstream dependencies:

- v1.1.12 `beacon-implement-branch-gate` (CLI preflight intent)
- v1.4.10 explicit-version canonical branch/worktree preflight
- v1.5.2 `markdown-only-project-version-governance` (governance MD authority)
- v1.6.0 skill harness taxonomy (shared preamble pattern)
- v1.6.1 agent-eval / loop worktree harness patterns (reference only)
