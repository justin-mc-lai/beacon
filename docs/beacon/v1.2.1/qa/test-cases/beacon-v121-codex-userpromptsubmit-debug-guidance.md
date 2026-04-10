# Beacon v1.2.1 Test Cases: Codex UserPromptSubmit Debug Guidance

**Feature**: Beacon v1.2.1 - Codex UserPromptSubmit Debug Guidance  
**Version**: v1.2.1  
**Date**: 2026-04-10  
**Status**: Drafted supplement line

---

## TC-001: UserPromptSubmit payload should be accepted

**Priority**: P0  
**Expected**:

- Beacon accepts a JSON payload with `hook_event_name = UserPromptSubmit`
- prompt text is extracted from supported fields

## TC-002: Hook output should include model-facing guidance

**Priority**: P0  
**Expected**:

- output contains `hookSpecificOutput.additionalContext`
- context includes recommended Beacon command
- context includes a normalized prompt suggestion

## TC-003: Mixed-boundary prompt should trigger split guidance

**Priority**: P0  
**Expected**:

- boundary state becomes `mixed_need_confirm`
- output asks for prompt splitting

## TC-004: Debug evidence should persist to all required layers

**Priority**: P0  
**Expected**:

- prompt router history updated
- debug feedback file updated
- run snapshot file updated

## TC-005: Non-UserPromptSubmit hook events should be ignored safely

**Priority**: P1  
**Expected**:

- command returns `status=ignored`
- no misleading hook-specific guidance is emitted
