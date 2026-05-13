# Beacon Skill Example: Compatibility Implementation

This example shows how **v1.4.5** treats external runners such as OMX: useful for compatibility, but not part of the default human main path.

Read first:

- [`../../../docs/beacon/v1.4.5/SUMMARY.md`](../../../docs/beacon/v1.4.5/SUMMARY.md)
- [`../../../docs/beacon/v1.4.5/execution/index.md`](../../../docs/beacon/v1.4.5/execution/index.md)
- [`../../../docs/beacon/v1.4.5/execution/architecture-blueprint.md`](../../../docs/beacon/v1.4.5/execution/architecture-blueprint.md)

```bash
# 1) Inspect optional adapters and preferred runner
beacon skill list
beacon skill detect --project-root . --json
# skill prefer omx only when compatibility is explicit
beacon implement list-runners --json

# 2) Keep default implementation host-native unless compatibility is explicit
beacon implement plan \
  "Beacon v1.4.5 release line" \
  --project . \
  --version v1.4.5 \
  --json

# 3) Explicit compatibility-plane runner usage
beacon implement run \
  "Beacon v1.4.5 release line" \
  --project . \
  --version v1.4.5 \
  --runner omx \
  --dry-run \
  --json

# 4) Inspect implementation status / plan progress
# review spec before escalating to compatibility-plane execution
beacon implement status \
  "Beacon v1.4.5 release line" \
  --project-root . \
  --version v1.4.5

# 5) After implementation, run QA and release checks through Beacon core
beacon qa run \
  "Beacon v1.4.5 release line" \
  --project . \
  --version v1.4.5 \
  --json
beacon gate check release \
  --project-root . \
  --version v1.4.5 \
  --json
```
