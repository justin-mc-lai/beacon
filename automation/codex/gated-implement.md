# Codex Automation Spec: Gated Implement

Type: `standalone`

Schedule suggestion:

- Low frequency only
- Example custom cron: `0 13 * * 1-5`

Workspace mode:

- Prefer `worktree`

Prompt:

```text
Use $beacon:beacon and $beacon:beacon-implement for this run.

Project root: /Users/apple/Developer/Personal/products/beacon
Queue file: /Users/apple/Developer/Personal/products/beacon/automation/beacon-automation-queue.json

Goal:
Run a gated implementation window for explicitly queued features only. Never choose a feature opportunistically. Never reopen or rewrite requirement truth. Use Beacon gates to decide whether implementation may proceed.

Steps:
1. Run the host wrapper:
   /Users/apple/Developer/Personal/products/beacon/automation/jobs/beacon-gated-implement-job.sh \
     --project-root /Users/apple/Developer/Personal/products/beacon \
     --queue /Users/apple/Developer/Personal/products/beacon/automation/beacon-automation-queue.json \
     --host-runtime codex \
     --workspace-mode worktree \
     --output-dir /Users/apple/Developer/Personal/products/beacon/.beacon/automation-runs/implement
2. Read the generated artifacts.
3. Report:
   - executed candidates
   - skipped candidates with reasons
   - evidence refs
   - whether QA should run next

Constraints:
- do not force execution when gates fail
- do not edit the queue file during the run
- do not run release write actions
```
