# Execution Index (v1.1.8)

## Human Primary Surface

- `../SUMMARY.md`
- `../version/beacon-v1.1.8-prototype-baseline.md`
- `../research/gstack-gap-analysis.md`
- `../research/three-track-closure-audit.md`
- `../prd/beacon-prototype-baseline.md`
- `../prd/beacon-debug-runtime-feedback-loop.md`
- `../prd/beacon-qa-command-browser-acceptance.md`
- `../prd/beacon-implement-technical-architecture-archive.md`
- `../prd/beacon-init-progressive-architecture-blueprint.md`
- `../user-story/beacon-prototype-baseline.md`
- `../user-story/beacon-debug-runtime-feedback-loop.md`
- `../user-story/beacon-qa-command-browser-acceptance.md`
- `../user-story/beacon-implement-technical-architecture-archive.md`
- `../user-story/beacon-init-progressive-architecture-blueprint.md`
- `../qa/test-cases/beacon-prototype-baseline.md`
- `../qa/test-cases/beacon-debug-runtime-feedback-loop.md`
- `../qa/test-cases/beacon-qa-command-browser-acceptance.md`
- `../qa/test-cases/beacon-implement-technical-architecture-archive.md`
- `../qa/test-cases/beacon-init-progressive-architecture-blueprint.md`
- `../release/v1.1.8.md`
- `./boundaries.md`
- `./architecture-blueprint.md`
- `./version-evolution-blueprint.md`
- `./project-lifecycle-onboarding.md`
- `./implementation-archive-index.md`
- `./technical-implementation-archive-blueprint.md`
- `./init-architecture-blueprint-main-doc.md`

## 推荐阅读顺序（按角色）

### 技术负责人 / 架构负责人
1. `../SUMMARY.md`
2. `../version/beacon-v1.1.8-prototype-baseline.md`
3. `../research/gstack-gap-analysis.md`
4. `./architecture-blueprint.md`
5. `./version-evolution-blueprint.md`
6. `./init-architecture-blueprint-main-doc.md`
7. `./technical-implementation-archive-blueprint.md`
8. 五条 PRD

### 接手开发 / 二开同学
1. `../SUMMARY.md`
2. `../research/three-track-closure-audit.md`
3. `./project-lifecycle-onboarding.md`
4. `./architecture-blueprint.md`
5. `../prd/beacon-init-progressive-architecture-blueprint.md`
6. `../prd/beacon-implement-technical-architecture-archive.md`
7. `../prd/beacon-qa-command-browser-acceptance.md`

### Agent / 自动化消费者
1. `../SUMMARY.md`
2. `./index.md`
3. `.machine/execution/*revision.json`
4. `.machine/user-story/*.json`
5. `.machine/qa/*.ac-test-matrix.json`
6. gap audit / capability matrix / design-line map
7. `terminal.json`

## 五线依赖地图

```text
init-progressive-architecture-blueprint
  -> establishes project onboarding, architecture blueprint, and reading order

prototype-baseline
  -> defines UI / implementation baseline

implement-technical-architecture-archive
  -> turns implementation result into technical archive

qa-command-browser-acceptance
  -> verifies real behavior with browser/session evidence

debug-runtime-feedback-loop
  -> harvests real usage friction and feeds next version planning
```

更具体地说：

```text
init
→ prototype
→ implement
→ qa
→ gate/release
→ debug feedback
→ next version
```

## Machine Secondary Surface

- `docs/beacon/archive/v1.1.8/.machine/execution/`
- `docs/beacon/archive/v1.1.8/.machine/execution/design-line-map.json`
- `docs/beacon/archive/v1.1.8/.machine/execution/review-spec-v118-design-lines.json`
- `docs/beacon/archive/v1.1.8/.machine/qa/`
- `docs/beacon/archive/v1.1.8/.machine/user-story/`
- `docs/beacon/archive/v1.1.8/.machine/execution/prototype-ui-audit.json`
- `docs/beacon/archive/v1.1.8/.machine/execution/debug-runtime-gap-audit.json`
- `docs/beacon/archive/v1.1.8/.machine/execution/qa-command-gap-audit.json`
- `docs/beacon/archive/v1.1.8/.machine/execution/implement-archive-gap-audit.json`
- `docs/beacon/archive/v1.1.8/.machine/execution/init-architecture-gap-audit.json`
- `docs/beacon/archive/v1.1.8/.machine/execution/gstack-capability-gap-matrix.json`
- `docs/beacon/archive/v1.1.8/.machine/execution/terminal.json`

## Machine 读取顺序建议

1. `beacon-*-revision.json`
2. `beacon-*.ac-test-matrix.json`
3. `beacon-*.json`（user-story）
4. `*-gap-audit.json`
5. `gstack-capability-gap-matrix.json`
6. `design-line-map.json`
7. `review-spec-v118-design-lines.json`
8. `terminal.json`

## Notes

- v1.1.8 当前已作为正式 release line。
- 本版聚焦五条并行设计线：prototype baseline、runtime debug feedback、qa/browser acceptance、implement 技术归档、init 架构主入口。
- 五条线不是平铺功能清单，而是共同组成“Beacon 生命周期接管项目开发”的主干。
- `milemon` 作为真实样板提供验证边界，但设计必须保持通用。
- `.machine` 已补齐 revision / user-story / ac-test-matrix / gap audit / design-line map / spec review 汇总。
- 已通过 `beacon review spec --version v1.1.8` 对五条设计线完成 formal spec review；当前 machine 汇总结果为 `5/5 pass`。
- release 文档、architecture blueprint、version evolution blueprint、project lifecycle onboarding、implementation archive index 已生成并纳入当前线。
