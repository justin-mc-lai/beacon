# Beacon v1.1.8 Architecture Blueprint

## 定位

Beacon v1.1.8 是一个面向**项目接管 + 需求交付 + 技术归档 + QA 验收 + 反馈回流**的 CLI 工作流内核。

## 分层结构

```text
User / Agent
  -> Beacon CLI surface
    -> init / prototype / implement / qa / debug / review / gate / release
      -> docs/beacon/<version>/ human primary
      -> docs/beacon/<version>/.machine/ machine secondary
      -> .beacon/ runtime internal state
```

## 五条设计线

1. `init-progressive-architecture-blueprint`
2. `prototype-baseline`
3. `implement-technical-architecture-archive`
4. `qa-command-browser-acceptance`
5. `debug-runtime-feedback-loop`

## 关键工件面

### Human
- `SUMMARY.md`
- `execution/index.md`
- `execution/boundaries.md`
- `execution/architecture-blueprint.md`
- `execution/version-evolution-blueprint.md`
- `execution/project-lifecycle-onboarding.md`
- `execution/implementation-archive-index.md`

### Machine
- `.machine/execution/design-line-map.json`
- `.machine/execution/review-spec-v118-design-lines.json`
- `.machine/execution/gstack-capability-gap-matrix.json`
- `.machine/execution/*-gap-audit.json`
- `.machine/execution/technical-implementation-*.json`

### Runtime
- `.beacon/qa/status.json`
- `.beacon/qa/sessions/`
- `.beacon/debug/runs/`
- `.beacon/debug/issues/`
- `.beacon/debug/ideas/`
- `.beacon/implement/<run_id>/`
- `.beacon/state/project-onboarding.json`

## 接管链

```text
init
→ project onboarding
→ prototype baseline
→ implement + technical archive
→ qa + browser evidence + session
→ gate / release
→ debug feedback
→ next version planning
```
