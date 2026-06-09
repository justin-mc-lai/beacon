# Boundaries v1.6.0

## Skill Harness Boundary

Beacon v1.6.0 classifies host-visible skills by harness responsibility:

- `planner`: rough prompt decomposition, lake/ocean sizing, source/truth/evidence reading, gap discovery, and route recommendation.
- `generator`: authority-bound truth, implementation, prototype, design, or delivery artifact generation.
- `evaluator`: evidence verification, drift detection, no-fake-delivery enforcement, QA, release, and route/block decisions.
- `governor`: context, archive, hooks, automation, memory, metadata, status, and diagnostics.

## Lifecycle Boundary

The v1.6.0 human-facing lifecycle is:

```text
plan -> truth -> generate -> evaluate -> release
```

The canonical truth model is unchanged from the v1.5.2 cutover:

```text
truth-map resolver -> features/<slug>/{truth,tests,tasks,evidence}.md
```

## Hard Gates

- Planner skills do not implement, write frozen truth, or issue QA/release verdicts.
- Generator skills do not self-certify completion and cannot use placeholder/docs-only/fake evidence as closure.
- Evaluator skills do not rewrite truth or repair implementation as part of verdict generation.
- Governor skills do not become a human mainline stage.

## No Compatibility Alias Rule

v1.6.0 host-visible skill names are intentionally breaking and use:

```text
beacon-<harness-code>-<function>
```

Harness codes are `pln`, `gen`, `eval`, and `gov`.

Old host-visible skill aliases are not part of the v1.6.0 skill package.
