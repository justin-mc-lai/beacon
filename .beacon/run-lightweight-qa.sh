#!/bin/sh
set -eu

export BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1

python3 -m beacon.main qa run \
  "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor" \
  --project . \
  --version v1.4.0 \
  --layer-command "unit=sh .beacon/qa-lightweight-evidence-check.sh" \
  --layer-command "functional=sh .beacon/qa-lightweight-evidence-check.sh" \
  --json
