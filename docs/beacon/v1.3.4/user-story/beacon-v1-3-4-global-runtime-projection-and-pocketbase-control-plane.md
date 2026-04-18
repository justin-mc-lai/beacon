# User Story: Beacon v1.3.4 管理看板原型补充入口

**Feature**: `beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane`  
**Version**: `v1.3.4`  
**Status**: `prototype-source`

**As a** 一人公司中的 CEO 与项目负责人，  
**I want** Beacon 为 `Beacon Runtime Ledger` 与 `Beacon 管理看板` 提供可审查的生命周期原型，  
**So that** 我可以先用可视化参考包确认首页总览、项目详情、runtime 下钻、恢复诊断的页面结构与状态边界，再决定后续实现。

## Source of Truth

此文件仅作为 `beacon prototype` 的结构化 source envelope。

正式需求与边界说明仍以以下 PRD 为准：

- `docs/beacon/v1.3.4/prd/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`

## Prototype Contract

ui_visualization_required: true
design_governance_required: true
interactive_prototype_required: true
design_generation_mode: description-as-design
prototype_mode: reference-pack-v2
coverage_mode: all-existing-routes
prototype_archetype: admin-workbench
theme_mood: disciplined
theme_primary: #1F6FEB
theme_secondary: #0F172A
surface_style: calm-ops board with lifecycle-first information hierarchy
target_user: one-person-company CEO and project owner
brand_keywords: lifecycle-first, delivery-truth, calm-ops, sober-control
sections: portfolio-overview, project-detail, runtime-center, recovery-diagnostics
navigation: overview, projects, runtime, diagnostics
primary_entry: portfolio-overview
primary_exit: project-detail
primary_cta: 查看项目详情
secondary_cta: 打开运行态
jump_map: portfolio-overview->project-detail: drill into selected project version, parallel PRDs, and lifecycle progress; project-detail->runtime-center: inspect single/team/ralph active runs and agent/session refs; runtime-center->recovery-diagnostics: inspect stale runs, sqlite unavailable state, and rebuild readiness; recovery-diagnostics->portfolio-overview: return to cross-project summary after diagnosis
states: healthy-summary, requirement-incomplete, implement-running, qa-running, release-ready, team-active, ralph-active, blocked, db-offline, partial-rebuild
required_pages:
  - portfolio-overview
  - project-detail
  - runtime-center
  - recovery-diagnostics
required_states:
  - healthy-summary
  - requirement-incomplete
  - implement-running
  - qa-running
  - release-ready
  - team-active
  - ralph-active
  - blocked
  - db-offline
  - partial-rebuild
page_inventory:
  - portfolio-overview
  - project-detail
  - runtime-center
  - recovery-diagnostics
page_inventory_source:
  CEO overview requires project/version/stage/progress/blocker summary.
  Project owner detail requires version line, main/parallel PRDs, material completeness, git/worktree governance, session refs.
  Runtime center requires single/team/ralph focused drilldown.
  Recovery diagnostics requires degraded mode, rebuild contract, and sync-health explanation.
baseline_protection:
  - page: portfolio-overview
    preserve:
      - lifecycle-first summary cards
      - current version, progress, blocker in one scan line
      - runtime only as compressed badge
      - no raw worker transcript exposure
  - page: project-detail
    preserve:
      - main PRD and parallel PRD distinction
      - requirement materials completeness panel
      - git and worktree governance card
      - recommended next skill and next action
  - page: runtime-center
    preserve:
      - single team ralph mode separation
      - active agent count and role status for team
      - round count and next action for ralph
      - host session refs without full transcript disclosure
  - page: recovery-diagnostics
    preserve:
      - projection not truth wording
      - sqlite and pocketbase degraded mode explanation
      - rebuild from docs/beacon and .beacon path
      - omc omx explicitly excluded from managed runtime scope
route_closure_required: true
drift_guardrails: runtime-noise-exposed-on-home, agent-count-misused-as-progress, projection-layer-presented-as-truth, omc-omx-leak-into-board, git-worktree-governance-hidden
design_reference_sources: Beacon v1.3.4 main PRD lifecycle-first board model, Beacon v1.3.4 one-person-company ops board model, PocketBase as control plane, not formal delivery truth, Beacon admin-workbench prototype discipline, human minimal surface with runtime drilldown only
