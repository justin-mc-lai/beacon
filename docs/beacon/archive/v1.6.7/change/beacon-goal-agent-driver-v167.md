# Change: beacon-goal-agent-driver-v167

- **version**: v1.6.7
- **kind**: new lake (Python AgentDriver)
- **depends_on**: beacon-goal-durable-supervisor-v167
- **date**: 2026-07-18
- **user**: GO Path C — parallel v1 Driver + v2 parity

## Intent

Auto re-launch host agent turns after each exit/context full without typing「继续」.

## Downstream

freeze → implement → qa → release human gate  
v2: `beacon-v2-goal-durable-longrun` already holds parity contract
