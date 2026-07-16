# Beacon v2.0.0 Summary

v2.0.0 opens the **Beacon Rust kernel rewrite** line.

Human-facing lifecycle language remains v1.6.0 compatible:

```text
plan -> truth -> generate -> evaluate -> release
```

Package-authoritative truth:

```text
truth-map resolver -> features/<slug>/{truth,tests,tasks,evidence}.md
```

Primary v2.0.0 feature:

- `beacon-v2-rust-kernel-redesign` — Rust core + Python compat layer; global `~/.beacon/beacon.db`; unified orchestrator; Operator Spine API

Source plan (support advisory):

- `docs/plans/beacon-v2-redesign.md`
