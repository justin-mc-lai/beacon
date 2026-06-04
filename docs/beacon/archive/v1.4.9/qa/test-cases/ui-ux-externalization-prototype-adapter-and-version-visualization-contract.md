# Test Cases: ui-ux-externalization-prototype-adapter-and-version-visualization-contract

**Feature**: `ui-ux-externalization-prototype-adapter-and-version-visualization-contract`
**Version**: `v1.4.9`
**Status**: `frozen`

## Coverage Matrix

| AC ID | Test ID | Layer | Command / Evidence | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-UXEXT-001 | contract | PRD/source review | Beacon marks internal UI/UX execution as non-core future capability |
| AC-002 | TC-UXEXT-002 | routing | skill routing evidence | UI/UX execution intent maps to `ui-ux-dev` intents |
| AC-003 | TC-UXEXT-003 | gate | missing upstream simulation | Missing `ui-ux-dev` routes to bootstrap, not silent internal fallback |
| AC-004 | TC-UXEXT-004 | contract | prototype skill / command review | `prototype` is adapter, not generator, in v1.4.9 contract |
| AC-005 | TC-UXEXT-005 | implement gate | accepted design result without binding | Implement blocks when adapter truth binding is missing |
| AC-006 | TC-UXEXT-006 | compatibility | historical prototype bundle fixture | Historical prototype remains readable but not v1.4.9 execution truth |
| AC-007 | TC-UXEXT-007 | requirement clarity | business flow projection fixture | Business flow projection exists and avoids implementation detail |
| AC-008 | TC-UXEXT-008 | requirement clarity | state-machine projection fixture | State-machine projection uses stable closure states |
| AC-009 | TC-UXEXT-009 | requirement clarity | three-piece map fixture | PRD / user-story / test-case map explains ownership and links |
| AC-010 | TC-UXEXT-010 | requirement clarity | projection missing truth bindings | Projection without truth bindings is blocked |
| AC-011 | TC-UXEXT-011 | requirement clarity | required visualization missing | Requirement clarity blocks missing visualization bindings |
| AC-012 | TC-UXEXT-012 | support boundary | design-review finding fixture | `beacon-design-review` remains support and routes to `ui-ux-dev` or `beacon-change` |

## Required Verification

The implementation must add or update automated tests for:

- UI/UX intent route classification.
- `prototype` adapter-only behavior.
- accepted design result binding gate.
- version visualization truth binding parser.
- requirement clarity failure when projection bindings are missing.
- historical prototype compatibility.

## Manual Review Checklist

- UI/UX execution is not presented as Beacon core lifecycle.
- `ui-ux-dev` is the named execution owner.
- `prototype` no longer promises design generation for v1.4.9+.
- business flow and state-machine projections are explicitly non-truth.
- every projection has PRD, user-story, and test-case refs.
