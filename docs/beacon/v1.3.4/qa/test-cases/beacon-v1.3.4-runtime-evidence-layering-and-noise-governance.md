# Test Cases: beacon-v1.3.4-runtime-evidence-layering-and-noise-governance

## Overview

**Feature**: `beacon-v1.3.4-runtime-evidence-layering-and-noise-governance`  
**Version**: `v1.3.4`

## Scenario Test Set

### TC-001 (AC-001, AC-002): Formal evidence and runtime cache are split

- Given: the `v1.3.4` release package
- When: reviewing docs and managed machine artifact directories
- Then: formal machine evidence and ephemeral runtime cache have separate documented classifications

### TC-002 (AC-003): Git boundary remains bounded

- Given: Beacon runtime/cache files and formal `.machine` files both exist
- When: applying release/governance rules
- Then: only formal machine evidence is required for package closure

### TC-003 (AC-004, AC-005): Stale runtime cannot override truth

- Given: runtime state is present but stale or conflicting with current revision
- When: status/qa/release evaluate it
- Then: Beacon marks runtime as advisory/partial/stale rather than authoritative

### TC-004 (AC-006): Missing runtime can rebuild from requirement materials

- Given: runtime cache is absent
- When: Beacon performs release/status/doctor flow
- Then: Beacon can continue from docs + formal machine evidence and recommend rebuild/revalidation

### TC-005 (AC-007): Human output is lifecycle-first

- Given: a human-facing status/help/release view
- When: runtime internals exist
- Then: the default output still prioritizes stage, blocker, and next step

### TC-006 (AC-008): Delivery drift can be recorded formally

- Given: a PRD promise exceeds current delivery surface
- When: Beacon records the issue
- Then: the drift can be represented as a formal requirement repair line rather than only local noise
