# Beacon Skill Example

```bash
# Version
bash skills/beacon/scripts/run_beacon.sh --version

# List adapters
bash skills/beacon/scripts/run_beacon.sh skill list

# Start workflow
bash skills/beacon/scripts/run_beacon.sh workflow start "Beacon v1.1.4 skill standard alignment" --project . --version v1.1.4

# Run implementation with OMX
bash skills/beacon/scripts/run_beacon.sh implement run "Beacon v1.1.4 skill standard alignment" --project . --version v1.1.4 --runner omx --dry-run --json
```
