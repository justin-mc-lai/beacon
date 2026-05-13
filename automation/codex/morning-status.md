# Codex Automation Spec: Morning Status

Type: `standalone`

Schedule suggestion:

- Weekdays at `09:00`
- Or custom cron: `0 9 * * 1-5`

Workspace mode:

- Prefer `worktree`

Prompt:

```text
Use $beacon:beacon for this run.

Project root: /Users/apple/Developer/Personal/products/beacon
Queue file: /Users/apple/Developer/Personal/products/beacon/automation/beacon-automation-queue.json

Goal:
Run a low-risk morning Beacon status pass. Read current workflow state, active execution surfaces, QA status, implementation next tasks, and release-facing blockers. Do not modify requirement truth. Do not start implementation. Do not run release write actions.

Steps:
1. Run the host wrapper:
   /Users/apple/Developer/Personal/products/beacon/automation/jobs/beacon-status-job.sh \
     --project-root /Users/apple/Developer/Personal/products/beacon \
     --queue /Users/apple/Developer/Personal/products/beacon/automation/beacon-automation-queue.json \
     --output-dir /Users/apple/Developer/Personal/products/beacon/.beacon/automation-runs/status
2. Read the generated artifact and summarize:
   - active features
   - blocked features
   - QA status and evidence gaps
   - implementation next task / blocked task signals
   - release-prep risks
3. Report only actionable findings. If there is nothing important, say so briefly.

Output:
- concise human summary
- artifact path
- recommended next route: status, qa, implement, change, or release-prep
```
