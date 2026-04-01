# Beacon v1.1.11 Architecture Blueprint

## Intent

`v1.1.11` 是将 Beacon Prototype 从“单页 archetype 壳子生成器”升级为“story-driven 高保真实现参考包编译器”的规划线。

它不是新的 workflow kernel。

它是对现有 prototype surface 的产品模型重定义。

## System Shape

目标系统形态：

```text
story / prd / route source / code source / baseline source
→ contract compiler
→ prototype plan
→ page inventory + page specs + state matrix
→ multi-page high-fidelity reference pack
→ strict review / freeze / gate semantics
→ implementation / qa consumers
```

## Primary layers

### Requirement layers

- `SUMMARY.md`
- `user-story/`
- `prd/`
- `qa/test-cases/`
- `execution/`
- `release/`

### Machine layers

- `.machine/user-story/`
- `.machine/qa/`
- `.machine/execution/`

### Runtime prototype layers

- `docs/beacon/<version>/prototype/<feature>/prototype-plan.json`
- `docs/beacon/<version>/prototype/<feature>/page-specs/`
- `docs/beacon/<version>/prototype/<feature>/pages/`
- `docs/beacon/<version>/prototype/<feature>/states/`
- `docs/beacon/<version>/prototype/<feature>/coverage-report.json`
- `docs/beacon/<version>/prototype/<feature>/prototype-review.json`

## Architectural delta relative to v1.1.10

Compared with `v1.1.10`, the new delta is:

- input parsing moves from flat field extraction to contract compilation
- the render unit moves from `prototype_archetype` to required page inventory
- baseline protection becomes a first-class contract instead of an informal note
- review/freeze/status become artifact-consistency-aware instead of file-existence-oriented
- implementation and QA consumers can read page-level prototype artifacts instead of only top-level navigation/interaction shells

## Directive

Do not describe `v1.1.11` as “better templates”.

It is only successful if Beacon can truthfully answer:

- which pages are required
- which states are required
- which route-producing controls must close
- which baseline expressions must not regress
- which artifacts downstream tools should consume
