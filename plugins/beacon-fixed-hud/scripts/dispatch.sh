#!/usr/bin/env bash
# beacon-doctor-managed: true
# beacon-doctor-project-root: /Users/apple/Developer/Personal/products/beacon
# beacon-doctor-version: v1.6.8
set -euo pipefail
export BEACON_CODEX_HUD_ACTIVATION_SOURCE="doctor-managed-dispatch"
exec bash /Users/apple/Developer/Personal/products/beacon/skills/beacon/scripts/run_beacon.sh debug codex-fixed-hud --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.8 --json
