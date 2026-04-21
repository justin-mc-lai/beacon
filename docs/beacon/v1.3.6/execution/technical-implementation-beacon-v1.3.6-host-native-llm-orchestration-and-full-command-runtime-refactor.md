# Beacon v1.3.6 Technical Implementation

## Feature

- `beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor`

## Scope

- Promote `v1.3.6` to the current runtime release line.
- Align package truth, root docs, packaged host skills, and release evidence.
- Preserve the existing public command surface while making release-facing wording and evidence coherent.

## Key Implementation Areas

- Version truth
  - `beacon/__init__.py`
  - `pyproject.toml`
  - `beacon/version-truth.json`
- Host-native runtime modules
  - `beacon/utils/semantic_runtime.py`
  - `beacon/utils/delivery_kernel.py`
- Public docs and packaging
  - `README.md`
  - `SKILL.md`
  - `CLAUDE.md`
  - `.claude-plugin/plugin.json`
  - `skills/beacon/`
  - `skills/beacon-iteration-governance/`
- Release evidence
  - `docs/beacon/v1.3.6/release/`
  - `docs/beacon/v1.3.6/change/`
  - `docs/beacon/v1.3.6/.machine/change/`

## Verification

- Runtime regression suite executed for the promoted line.
- Docs/skill regression suite queued for rerun after promotion fixes.
- Release version-change evidence generated through `beacon release create`.
