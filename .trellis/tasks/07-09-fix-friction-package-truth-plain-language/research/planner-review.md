# Planner Review: package truth projection and plain-language friction

## Intent Snapshot

The user asked to analyze and fix two queued frictions:

- Stop default generation of old `prd/user-story/test-case` split surfaces.
- Fix `friction:eb4495db0020` by making requirement docs understandable in plain language.

The requested outcome is a runtime behavior change, not only documentation.

## Evidence

- `friction:ab595fdee485` is queued, queue-only, P3 improvement, occurrence count 2.
- `friction:eb4495db0020` is queued, queue-only, P3 improvement, occurrence count 1.
- Target project evidence lives under `/Users/apple/Developer/Personal/products/selfmedia-sync-ai/.beacon/debug/friction-captures/`.
- Beacon source code currently has a split:
  - `feature_package_authoritative(version)` is semver-based and returns false for target product versions like `v0.0.12`.
  - `feature_package_authoritative_feature(project_root, version, feature)` also checks physical package readiness and returns true for package-ready target features.

## Findings

1. `manifest.compute_feature_paths()` uses version-only authority, so product versions below `v1.5.2` keep legacy path outputs even when package truth exists.
2. `prd_bootstrap` targets only split docs, so it can generate duplicate-looking truth in package-ready projects.
3. `user_story` and `test_case` command readers use version-only checks and should use feature-aware package authority when a concrete feature is known.
4. Generated package truth lacks a dedicated plain-language human layer; the result is technically useful but hard for operators to read.

## Recommendation

Implement a feature-aware package-authority path policy:

- Package-ready feature -> package paths by default.
- No package -> legacy paths remain for compatibility.
- Explicit compat flag may generate split surfaces when needed.
- Plain-language sections belong in package truth generation and should not replace technical binding.
