---
hook_id: beacon-post-release-local-install
hook_code: post_release
project: beacon
enabled: true
trigger_policy: manual_confirmed
skill: beacon-project-hooks
command_template: "beacon hooks run beacon-post-release-local-install --project . --version {version} --feature {feature} --confirm"
produces_evidence:
  - codex_agent_surface_setup
  - codex_agent_surface_verify
  - claude_agent_surface_setup
  - claude_agent_surface_verify
  - global_beacon_cli_version
  - global_beacon_cli_launcher_path
  - macmini_hermes_beacon_sync_default
  - macmini_hermes_beacon_sync_finance
failure_route: release
---

# Beacon Post Release Local Install Hook

## Purpose

After a Beacon source release is accepted, this project-level hook records the local operator follow-up that keeps the Beacon development environment usable:

- materialize Beacon host-visible skills into the local Codex agent surface;
- materialize Beacon host-visible skills into the local Claude agent surface;
- verify those local agent surfaces against the released Beacon line;
- confirm the global `beacon` and `beacon-cli` launchers resolve to the released CLI version.
- sync Beacon skills into Mac mini Hermes Agent profiles (default + finance) via `qi-dev-macmini`.

This hook is project-specific to the Beacon source repository. It is not a default Beacon lifecycle behavior for downstream projects.

## Admission

- The release gate has already passed for the target version.
- The operator is in the Beacon source repository.
- The hook is invoked at the `post_release` boundary.
- The operator manually confirms the side-effect follow-up with `--confirm`.
- The target version is explicit, for example `v1.4.10`.

## Implantation

This hook is implanted into the Beacon source release follow-up after `beacon release check <version>` returns release-ready.

It is invoked manually through the project hook toolkit:

```bash
python3 -m beacon.main hooks plan beacon-post-release-local-install \
  --project-root . \
  --version <version> \
  --feature <feature> \
  --hook-code post_release \
  --json

python3 -m beacon.main hooks run beacon-post-release-local-install \
  --project-root . \
  --version <version> \
  --feature <feature> \
  --hook-code post_release \
  --confirm \
  --json
```

The hook runtime has a restricted built-in follow-up for this hook id. It does not execute arbitrary shell commands from the Markdown contract.

Expected operator commands for the side-effect follow-up are:

```bash
python3 -m beacon.main doctor setup-agent-surface --project-root . --version <version> --agent codex --force --json
python3 -m beacon.main doctor verify-agent-surface --project-root . --version <version> --agent codex --strict --json
python3 -m beacon.main doctor setup-agent-surface --project-root . --version <version> --agent claude --force --json
python3 -m beacon.main doctor verify-agent-surface --project-root . --version <version> --agent claude --strict --json
python3 -m beacon.main doctor setup --force --json
beacon --version
beacon-cli --version

# sync to Mac mini Hermes Agent
qi_dev.sh macmini exec "bash /Users/apple/Developer/Personal/products/hapi-implementation-playbook/tools/hapi-dual-mac-ops/scripts/sync_beacon_dual_machine.sh --peer-only"
qi_dev.sh macmini health
```

## Evidence

The hook evidence must record, or be accompanied by, these release follow-up facts:

- Codex agent surface setup status is `PASS`.
- Codex agent surface verification status is `PASS`.
- Claude agent surface setup status is `PASS`.
- Claude agent surface verification status is `PASS`.
- `beacon --version` prints the target Beacon CLI version.
- `beacon-cli --version` prints the target Beacon CLI version.
- `which beacon` and `which beacon-cli` resolve to launchers on the operator PATH.
- Mac mini Hermes Agent default profile Beacon skill sync status is `PASS`.
- Mac mini Hermes Agent finance profile Beacon skill sync status is `PASS`.

Runtime hook evidence is written under `.beacon/state/hooks/beacon-post-release-local-install/`.

Latest hook read model is written to `docs/beacon/.machine/hooks/beacon-post-release-local-install.latest.json`.

## Failure Route

If any setup or verification command fails, stay in `release` follow-up and repair the local installation. Failed local installation evidence routes back to release follow-up repair.

## Authority Boundary

No authority over PRD truth, user-story truth, test-case truth, QA verdict, release verdict, gate verdict, freeze state, or requirement truth.

Scope is limited to project-level post-release installation and verification evidence for the Beacon source repository.
