# Real Project Command Matrix

Use these placeholders:

- `ROOT` = real project root
- `VERSION` = docs line such as `v1.0.0`
- `FEATURE` = one existing feature such as `friend-match`

## Preflight

```bash
git -C ROOT status --short
beacon doctor --json --project-root ROOT
beacon help --project-root ROOT --version VERSION --feature FEATURE --json
```

## Read-Only Minimal Surface

```bash
beacon status show-status --project-root ROOT --version VERSION --feature FEATURE --board
beacon prd list -p ROOT -v VERSION
beacon user-story list -p ROOT -v VERSION
beacon test-case list -p ROOT -v VERSION
beacon test-case gate FEATURE -p ROOT -v VERSION
beacon implement status FEATURE -p ROOT -v VERSION --json
beacon qa status -p ROOT --json
beacon qa evolve FEATURE -p ROOT -v VERSION --no-write-matrix --json
beacon release check VERSION -p ROOT
beacon release scorecard VERSION -p ROOT --json
```

## How To Interpret Results

- Count the surface as operational when it returns structured output or a clear human-readable status.
- Do not count `qa blocked`, `release_ready=false`, or failed release checks as Beacon defects by themselves.
- Count the surface as defective when it crashes, routes to the wrong version, selects the wrong run, or mutates tracked docs during read-only validation.

## Write-Path Validation In Isolation Only

Run these only in an isolated copy or worktree:

```bash
beacon prd create FEATURE --project ROOT --version VERSION
beacon user-story create FEATURE --project ROOT --version VERSION
beacon test-case create FEATURE --project ROOT --version VERSION
beacon implement plan FEATURE --project ROOT --version VERSION --json
```
