# Execution Boundaries v1.5.1

## Truth Map Authority

The truth map center is a deterministic CLI resolver and static schema contract.

`truth-map.md`, `truth-map.json`, and `.machine` files are not truth authority. They are generated views, diagnostics, evidence, or rebuild metadata.

## MD-Only Truth Direction

v1.5.1 removes MD-to-JSON multi-write projection as a goal. Beacon may still generate JSON evidence where useful, but a JSON twin is not required for Markdown truth to be valid.

## Consumer Boundary

New CLI and skill truth reads must go through truth-map resolver first.

Hardcoded direct reads of `prd/`, `user-story/`, and `qa/test-cases/` should not be added. Existing reads become migration targets for v1.5.2 cutover.

