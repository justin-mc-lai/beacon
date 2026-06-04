# Change: Beacon Design Human Subskills Closure Contract

**Feature**: `beacon-design-human-subskills-closure-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## 1. Change Reason

v1.4.11 已经把旧 prototype 能力重构为 Beacon design 能力，并在 PRD 中承诺了 `beacon-design-*` 子入口。

当前缺口是：CLI route 和 PRD 承诺已经有 7 条，但 host-visible human skill 只安装了 `beacon-design` 和 `beacon-design-review`。

这会让 AI 每次使用 design 能力时重新理解 intent，降低稳定性，也容易把 reference、bootstrap、review、polish、system 等边界混在一起。

## 2. Accepted Change

冻结一个小 feature，要求 Beacon 补齐 design 人类面子 skill 闭环：

1. 保留 `beacon-design` 作为总入口和分流入口。
2. 新增或对齐 7 个 host-visible 子 skill：
   - `beacon-design-explore`
   - `beacon-design-extract`
   - `beacon-design-system`
   - `beacon-design-review`
   - `beacon-design-polish`
   - `beacon-design-library`
   - `beacon-design-bootstrap`
3. 每个子 skill 必须绑定到现有 `beacon design route <intent>`，不新增 runtime route。
4. 每个子 skill 必须声明 `support_only=true`、`truth_source=false`、`gate_source=false`、`lifecycle_stage=false`。
5. `beacon-design-library` 必须明确 `awesome-design-md` 是 reference-only。
6. `beacon-design-bootstrap` 必须明确只做 capability admission，不是 release / gate 证据。
7. accepted design facts 仍必须通过 Beacon truth binding、prototype adapter 或 change/refreeze 进入主链。

## 3. Scope

### In Scope

- `.agents/skills/beacon-design-*` host-visible skill 文件。
- `skills/beacon/beacon-design-*` packaged skill 文件。
- `beacon-design-review` 与 v1.4.11 design route 语义对齐。
- Skill discoverability / route contract / boundary tests。
- Documentation references that describe the design subskill family.

### Out Of Scope

- No new design CLI route.
- No change to `beacon design route` runtime contract.
- No prototype adapter behavior change.
- No PRODUCT.md / DESIGN.md truth content change.
- No release verdict change.
- No new lifecycle stage.
- No upstream design skill becoming Beacon truth source.

## 4. Source Evidence

- Brainstorm: `docs/brainstorms/2026-05-27-beacon-brainstorm-分析-v1.4.11-design-人类面子-skill-是否应从单一-beacon-design-拆成-beacon-design-子-skill-并给出闭环.md`
- Existing design PRD: `docs/beacon/archive/v1.4.11/prd/beacon-design-product-prototype-rebuild-contract.md`
- Existing design user story: `docs/beacon/archive/v1.4.11/user-story/beacon-design-product-prototype-rebuild-contract.md`
- Existing design route CLI: `beacon design contract "beacon-design-product-prototype-rebuild-contract" --project . --version v1.4.11 --json`
- Current skills: `.agents/skills/beacon-design/SKILL.md`, `.agents/skills/beacon-design-review/SKILL.md`

## 5. Route Decision

This feature is a post-release-check aggregate truth correction for v1.4.11 design human surface completeness.

It reopens v1.4.11 scope intentionally and requires implementation, QA, aggregate change refresh, and release check after freeze.

## 6. Freeze Deliverables

- `docs/beacon/archive/v1.4.11/research/beacon-design-human-subskills-closure-contract.md`
- `docs/beacon/archive/v1.4.11/change/beacon-design-human-subskills-closure-contract.md`
- `docs/beacon/archive/v1.4.11/prd/beacon-design-human-subskills-closure-contract.md`
- `docs/beacon/archive/v1.4.11/user-story/beacon-design-human-subskills-closure-contract.md`
- `docs/beacon/archive/v1.4.11/qa/test-cases/beacon-design-human-subskills-closure-contract.md`

## 7. Boundary

This feature freezes requirement truth for host-visible Beacon design subskills only.
