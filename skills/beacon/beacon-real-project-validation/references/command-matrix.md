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

## Modern Runtime Prechecks

```bash
beacon doctor verify-subagent-runtime --project-root ROOT --host-runtime codex --json
beacon doctor verify-subagent-runtime --project-root ROOT --host-runtime claude --json
beacon doctor verify-subagent-delegation FEATURE --project-root ROOT --version VERSION --json
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

## Team / Ralph Dry-Run Surface

Run these only when the Beacon version under validation already supports `team` / `ralph` on the public `implement` surface:

```bash
beacon implement run FEATURE --project ROOT --version VERSION --mode team --runner codex-subagents --host-runtime codex --dry-run --json
beacon implement run FEATURE --project ROOT --version VERSION --mode team --runner gstack --host-runtime claude --dry-run --json
beacon implement run FEATURE --project ROOT --version VERSION --mode ralph --runner codex-subagents --host-runtime codex --dry-run --json
beacon implement run FEATURE --project ROOT --version VERSION --mode ralph --runner gstack --host-runtime claude --dry-run --json
beacon implement ralph-status FEATURE --project-root ROOT --json
```

## Browser QA / Session Surface

Use these when validating Beacon versions that include formal browser QA and session/profile support:

```bash
beacon qa session list -p ROOT --json
beacon qa status -p ROOT --json
beacon qa run FEATURE -p ROOT -v VERSION --json
beacon qa team-run FEATURE -p ROOT -v VERSION --host-runtime codex --json
beacon qa team-run FEATURE -p ROOT -v VERSION --host-runtime claude --json
```

Interpret carefully:

- If the feature's formal QA bundle only declares `unit`, then no browser execution should be expected.
- If the formal QA bundle declares browser-capable layers, verify that Beacon produces browser-task / browser evidence artifacts rather than silently falling back to unrelated default layers.

## How To Interpret Results

- Count the surface as operational when it returns structured output or a clear human-readable status.
- Do not count `qa blocked`, `release_ready=false`, or failed release checks as Beacon defects by themselves.
- Do not count version-line package closure gaps as Beacon defects when current-feature closure is already ready.
- Count the surface as defective when it crashes, routes to the wrong version, selects the wrong run, or mutates tracked docs during read-only validation.

## Write-Path Validation In Isolation Only

Run these only in an isolated copy or worktree:

```bash
beacon prd create FEATURE --project ROOT --version VERSION
beacon user-story create FEATURE --project ROOT --version VERSION
beacon test-case create FEATURE --project ROOT --version VERSION
beacon implement plan FEATURE --project ROOT --version VERSION --json
```

For modern Beacon lines, isolated write-path validation may also include:

```bash
beacon doctor setup-context --project-root ROOT
beacon freeze FEATURE --project-root ROOT --version VERSION
beacon doctor sync-technical-review-contract FEATURE --project-root ROOT --version VERSION --revision-id R1 --review-status approved --approved-by validator --reviewed-at 2026-01-01T00:00:00Z --json
beacon qa session save qa-local -p ROOT --origin http://127.0.0.1:3000 --runner-type agent-browser --scope http://127.0.0.1:3000 --json
beacon qa session use qa-local -p ROOT --json
beacon qa team-run FEATURE -p ROOT -v VERSION --host-runtime codex --json
```
