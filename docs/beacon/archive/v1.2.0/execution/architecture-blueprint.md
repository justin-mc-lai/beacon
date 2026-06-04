# Beacon v1.2.0 Architecture Blueprint

`v1.2.0` is the runtime line that keeps Beacon centered on the `PRD → user-story → QA` mainline while making the operator surface easier to use and easier to bind to a real project.

## What this blueprint captures

1. **Mainline-first command surface**
   - the default CLI help surface prioritizes `think / user-story / prd / test-case / implement / qa / gate / release`
   - `help` / `status` act as phase routers instead of static command dumps
   - advanced surfaces remain available through explicit disclosure instead of competing with the mainline by default

2. **Bounded project-skill workflow**
   - `beacon skill discover` follows `detect → recommend → preview → apply`
   - discovery state is written to `.beacon/state/skill-discovery/`
   - only explicit apply merges the recommendation into `beacon.config.yaml`
   - `help` / `profile` / `skill doctor` consume the same discovery model

3. **Requirement-to-prototype anchoring**
   - prototype validation remains subordinate to the mainline
   - prototype drift must be explained in terms of PRD/story expectations, not as a separate product center

4. **Release-truth execution governance**
   - `docs/beacon/archive/v1.2.0/.machine/execution/` contains the machine-readable release contract
   - terminal / delivery-manifest / change-impact / source / config / git-alignment stay in sync with `.beacon` runtime evidence
   - review / accept / gate closure must produce evidence-backed release artifacts

## Primary source docs

- `./command-surface-simplification-blueprint.md`
- `./project-skill-qa-evolution-blueprint.md`
- `./target-project-kernel-blueprint.md`
- `../source-architecture/index.md`
- `../release/v1.2.0.md`
