# Beacon Automation Retired

The historical Beacon queue/job/launchd automation assets are retired.

Use the native long-loop runner instead:

```bash
beacon-loop goal "<goal>"
```

Operator guide: `docs/beacon/v1.6.0/execution/beacon-loop-usage.md`

This directory is retained only as a tombstone for older checkouts. It must not
contain runnable queue, scheduler, repair window, or QA automation business
assets.
