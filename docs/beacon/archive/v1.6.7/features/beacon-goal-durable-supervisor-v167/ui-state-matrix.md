# UI State Matrix — Goal Durable Supervisor

schema: ui-state-matrix.v1
bound_to: Domain FSM — GoalRun / SupervisorSession

CLI/status surfaces only (no product marketing UI). Badges map operator-visible run states.

| State | Page | Badge | Primary action |
|-------|------|-------|----------------|
| created | goal status | created | start work |
| running | goal status | running | heartbeat / tick |
| stage_active | goal status | stage_active | continue stage |
| host_interrupted | goal status / resume-pack | interrupted | resume-pack |
| stage_blocked | goal status | blocked | repair then resume |
| awaiting_verifier | goal status | awaiting_verifier | attach-verifier |
| completed | goal status | completed | release human gate |
| blocked | goal status | hard_blocked | human unblock |
| release_pending | goal status | release_pending | human confirm |
| detached | supervise status | detached | goal supervise (opt-in) |
| active | supervise status | active | poll / --once |
| polling | supervise status | polling | heartbeat |
| waiting_host | supervise status | waiting_host | load skill |
| stopped | supervise status | stopped | re-attach opt-in |

## Do
- Bind badges only to GoalRun / SupervisorSession FSM states above
- Show host_interrupted distinctly from stage_blocked
- Never show completed without verifier path

## Don't
- Reuse commerce draft/placed/paid matrix for this CLI feature
- Auto-attach supervise on goal run
