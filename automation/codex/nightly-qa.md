# Automation Spec: Nightly QA

Type: `standalone`

Schedule suggestion:

- Daily at `23:00`
- Or custom cron: `0 23 * * *`

Workspace mode:

- Prefer `worktree`
- executor: `codex`
- tier: `native`

Prompt:

```text
Use $beacon:beacon and $beacon:beacon-qa for this run.

Project root: /Users/apple/Developer/Personal/products/beacon
Queue file: /Users/apple/Developer/Personal/products/beacon/automation/beacon-automation-queue.json

Goal:
Run nightly Beacon QA for queued candidate features. Respect Beacon truth/gate boundaries. Do not rewrite frozen truth. Do not perform release write actions.

Steps:
1. Run the host wrapper:
   /Users/apple/Developer/Personal/products/beacon/automation/jobs/beacon-qa-job.sh \
     --project-root /Users/apple/Developer/Personal/products/beacon \
     --queue /Users/apple/Developer/Personal/products/beacon/automation/beacon-automation-queue.json \
     --host-runtime codex \
     --output-dir /Users/apple/Developer/Personal/products/beacon/.beacon/automation-runs/qa
2. Read the generated artifacts.
3. For each feature, report:
   - layered verdict summary
   - blockers
   - repair handoff needed or not
   - evidence paths
4. If a protected live surface blocks execution because session admission is missing, record it explicitly as blocked or skipped, not as product failure.
5. Capability note:
   - Run through a Beacon-supported runtime.

Output:
- one section per feature
- pass / blocked / repair-needed summary
- evidence refs
- recommended next route
```
