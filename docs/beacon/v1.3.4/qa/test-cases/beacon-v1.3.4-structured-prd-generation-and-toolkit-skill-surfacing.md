# Test Cases: beacon-v1.3.4-structured-prd-generation-and-toolkit-skill-surfacing

## Overview

**Feature**: `beacon-v1.3.4-structured-prd-generation-and-toolkit-skill-surfacing`  
**Version**: `v1.3.4`

## Scenario Test Set

### TC-001 (AC-001, AC-002): PRD generation is version-aware

- Given: a Beacon version package and a new feature request
- When: `prd create` is used in Beacon context
- Then: the resulting skeleton reflects Beacon-style requirement sections and version context

### TC-002 (AC-003): Mainline and parallel PRD skeletons can differ

- Given: one mainline feature and one debug-driven parallel repair feature
- When: PRD generation runs
- Then: the resulting skeletons can distinguish the two requirement roles

### TC-003 (AC-004, AC-005): Toolkit routing is host-visible and doc-aligned

- Given: a toolkit promised by Beacon docs
- When: a host operator routes through Beacon skills
- Then: the toolkit is reachable through a documented stable entry surface

### TC-004 (AC-006): Debug friction can map into formal PRD repair

- Given: a Beacon debug friction issue
- When: it is lifted into requirement repair flow
- Then: the issue can be attached to a formal parallel PRD line with clear mapping
