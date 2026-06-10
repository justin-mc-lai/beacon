# Beacon Automation Retired

The historical Beacon queue/job/launchd automation assets are retired.

Use the native long-loop runner instead:

```bash
beacon-loop goal "<goal>"
```

This directory is retained only as a tombstone for older checkouts. It must not
contain runnable queue, scheduler, repair window, or QA automation business
assets.
