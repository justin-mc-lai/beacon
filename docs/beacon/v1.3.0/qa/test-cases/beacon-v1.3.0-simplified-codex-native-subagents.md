# QA Test Cases: Beacon v1.3.0 Simplified Codex Native Subagents

**Feature**: Beacon v1.3.0 - Simplified Codex Native Subagents  
**Version**: v1.3.0  
**Date**: 2026-04-10  
**Status**: planning line

## TC-001 Planning prompts should route to planning, not QA

- Given a prompt containing `下一版本`, `演进`, or `subagent`
- When `beacon ask` or `beacon prompt optimize` is called
- Then the routed intent should prefer planning-oriented surfaces

## TC-002 Stage subagent mode should be explicit

- Given a stage command without `subagent_mode`
- When it runs
- Then it should stay on the single-surface path

## TC-003 Invalid stage role should block

- Given an unregistered role for a stage
- When Beacon attempts delegation
- Then Beacon should stop before writeback

## TC-004 Subagent evidence must exist before canonical artifact update

- Given a delegated stage
- When worker output is missing or malformed
- Then Beacon must mark the stage blocked

## TC-005 `implement run` should keep existing runners valid

- Given `native-single` and `native-team`
- When `v1.3.0` subagent work lands
- Then existing runners should remain supported

## TC-006 QA subagent outputs must produce repair handoff when blocked

- Given `qa` subagent verification finds critical blockers
- When evidence is compiled
- Then the canonical QA output should contain blocker summary and repair handoff
