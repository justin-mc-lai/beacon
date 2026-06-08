# Code2Truth Intake: code2truth-project-intake

- version: `v1.5.2`
- target_project: `/Users/apple/Developer/Personal/products/justin-mc-lai-skills`
- authority: `support_evidence_only`
- generated_at: `2026-06-05T10:11:56.708603+00:00`

## Boundary

Code and provider graphs can propose candidate truth. User-confirmed Beacon package Markdown is formal truth.

## Source Inventory

- files_scanned: `112`
- source_files: `66`
- skill_files: `42`
- test_files: `0`
- doc_files: `4`

### Entry Points

- `scripts/install_reasonix_extras.py`
- `scripts/install_skills.py`
- `scripts/install_ui_ux_oss_skills.py`
- `scripts/publish_skills.py`
- `scripts/skill_sync_gate.py`
- `skills/awesome-design-md/SKILL.md`
- `skills/cli-anything/SKILL.md`
- `skills/cli-anything/scripts/install.sh`
- `skills/manage-oss-sync/SKILL.md`
- `skills/manage-oss-sync/scripts/dedupe_oss_sync_report.py`
- `skills/manage-oss-sync/scripts/generate_oss_sync_index.py`
- `skills/manage-oss-sync/scripts/import_oss_sync_repo.py`
- `skills/manage-oss-sync/scripts/manage_oss_sync.py`
- `skills/manage-oss-sync/scripts/oss_sync_lib.py`
- `skills/manage-oss-sync/scripts/sync_oss_sync_repos.py`
- `skills/manage-oss-sync-runtime/SKILL.md`
- `skills/qi-dev/SKILL.md`
- `skills/qi-dev/qi-dev-bmtop-local/SKILL.md`
- `skills/qi-dev/qi-dev-bmtop-miniapp/SKILL.md`
- `skills/qi-dev/qi-dev-bmtop-prod/SKILL.md`

## Provider Evidence

- understand_anything_available: `False`
- provider_authority: `support_advisory`
- truth_authority: `false`

## Candidate Truth

- `CLAIM-001` confidence=`medium` authority=`candidate_only`: Project behavior can be reconstructed from detected entry points.
  - refs: `scripts/install_reasonix_extras.py`, `scripts/install_skills.py`, `scripts/install_ui_ux_oss_skills.py`, `scripts/publish_skills.py`, `scripts/skill_sync_gate.py`
- `CLAIM-002` confidence=`high` authority=`candidate_only`: Skill files provide strong workflow evidence for candidate truth reconstruction.
  - refs: `skills/awesome-design-md/SKILL.md`, `skills/cli-anything/SKILL.md`, `skills/manage-oss-sync/SKILL.md`, `skills/manage-oss-sync-runtime/SKILL.md`, `skills/qi-dev/SKILL.md`

## Ambiguity

- `AMB-002` No tests were detected in the intake scope. route=`Keep coverage claims low-confidence until QA evidence is added.`

## Promotion Route

Candidate truth can be promoted only through user confirmation and Beacon truth/change/refreeze routing.
