# 版本默认（无提示词版本）

## Normal

```
default_target_version():
  runtime = current_runtime_release_line
  if any docs/planning > runtime: return min(higher)
  else: return bump_patch(runtime)  # v1.6.8 → v1.6.9
```

## Hotfix

- baseline = `current_runtime_release_line`
- **never** patch-bump as first production fix target

## Explicit

- `vX.Y.Z` / `vA\vB` dual-track → 用用户写的
