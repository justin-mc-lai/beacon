# User Story: beacon-v1.3.4-structured-prd-generation-and-toolkit-skill-surfacing

## Story

**As a** Beacon requirement author,  
**I want** `prd create` to generate version-aware structured PRD skeletons and already-promised toolkit skills to have host-visible routing,  
**So that** PRD generation no longer starts from an empty generic template and Codex/Claude users can actually reach the toolkit surfaces Beacon documents.

## Story Slices

### US-001: PRD generation must understand Beacon version context

As a requirement author, I want PRD creation to reflect the current version line and feature type instead of emitting one generic template.

### US-002: Mainline and parallel PRDs must be distinguishable

As a maintainer, I want a generated PRD for a main feature and a parallel repair line to start from different skeleton expectations.

### US-003: Toolkit promises must be reachable

As a Codex/Claude operator, I want a toolkit that is documented in Beacon materials to also have a host-visible skill path or equivalent stable route.

### US-004: Debug issues must map into requirement repair

As a maintainer, I want Beacon debug friction to map into parallel PRDs rather than staying only as local notes.

## Acceptance Criteria

- AC-001 Structured PRD skeleton: `prd create` no longer behaves as a purely generic markdown writer for Beacon version packages.
- AC-002 Version awareness: generated PRD skeletons can reflect the active version line and feature class.
- AC-003 Mainline/parallel distinction: generated skeletons can distinguish main PRDs from parallel repair PRDs.
- AC-004 Host-visible toolkit routing: documented optional toolkit surfaces have an explicit skill or stable routing surface for host usage.
- AC-005 Skill/doc alignment: Beacon skill documentation and actual reachable entrypoints do not drift for the frozen toolkit surface.
- AC-006 Debug-to-PRD mapping: requirement/tooling friction can be carried into a formal parallel PRD line with clear issue mapping.

## Metadata

| Field | Value |
|-------|-------|
| Priority | medium |
| Status | ready-for-planning |
| Version | v1.3.4 |
| Feature Slug | beacon-v1.3.4-structured-prd-generation-and-toolkit-skill-surfacing |
