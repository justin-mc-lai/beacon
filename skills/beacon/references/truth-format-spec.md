# Truth Format Specification (v1.4.12+)

When writing or editing truth documents for v1.4.12+, follow these format rules.

## PRD Format

### Mandatory sections (in order)
Overview → Outline → Problem → Goals → Scope → Functional Requirements → Acceptance Criteria → Non-Goals → Success Metrics

### Optional sections (insertable at designated points)
- Context (after Outline)
- Design Principles (after Goals)
- Source Contract (after Functional Requirements)
- State Axes (after Functional Requirements)
- Runtime Behavior Contract (after Functional Requirements)
- Evidence Contract (before Acceptance Criteria)
- Diagram Truth Layer (after Success Metrics)

### Rules
- Section titles: pure English names, **no numbering** (`## Problem`, not `## 1. Problem`)
- Front matter: **Feature**, **Version**, **Status**, **Date**, **Language**
- **Language** must be `en` or `zh`; content language must match
- Scope subsections: only `### In Scope` and `### Out of Scope`
- **Status** != `template`: no `<!-- FILL: ... -->` placeholders allowed
- FR table: `| FR ID | Related AC | Requirement |`
- State Axes table: `| Axis | States | Meaning |`
- **Outline** must contain a ` ```mermaid ` code block

## User Story Format

### Mandatory sections (in order)
Story → Outline → Acceptance Criteria → Test Story Map → References

### Optional sections
- State Axis Coverage (after Acceptance Criteria)

### Rules
- AC table: `| AC ID | Theme | Description |`
- Test Story Map: `| Test ID | Covers | Scenario |`
- References: at least 3 paths (research, PRD, test cases)
- **Outline** must contain a ` ```mermaid ` code block

## Test Cases Format

### Mandatory sections (in order)
Outline → Coverage Matrix → Explicit Non Coverage

### Optional sections
- Branch Coverage Mapping (after Coverage Matrix)

### Rules
- Coverage Matrix: `| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |`
- **Outline** must contain a ` ```mermaid ` code block

## Universal Rules

- Section titles and table column names are always English
- No numbering prefixes on section titles (no `## 1.`, `### 1.1`, etc.)
- No extra sections outside the white list
- Mermaid diagrams use `flowchart TD`, `flowchart LR`, `stateDiagram-v2`, or `sequenceDiagram`
- `beacon truth verify --strict` enforces all these rules
