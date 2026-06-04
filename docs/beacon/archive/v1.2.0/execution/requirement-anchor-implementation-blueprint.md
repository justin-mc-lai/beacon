# Beacon v1.2.0 Requirement Anchor Implementation Blueprint

This document summarizes how the v1.2.0 requirement package lands in runtime behavior.

## Shipped mapping

1. **Command simplification**
   - `beacon --help` now promotes the mainline before lower-frequency surfaces
   - `labs` / `bridge` require explicit exposure

2. **Mainline routing**
   - `help` returns next-step guidance centered on the current phase
   - skill discovery is suggested when project binding is missing

3. **Project-skill discovery**
   - project features are analyzed from repo signals
   - built-in starter templates generate preview/apply recommendations
   - discovery state is shared with profile and doctor surfaces

4. **QA baseline alignment**
   - v1.2.0 prefers QA9 matrix inputs when present
   - coverage / evidence / scorecard outputs remain tied to the requirement bundle

5. **Closure artifacts**
   - implement / review / accept regenerate execution-governance artifacts
   - release gate reads machine execution artifacts plus `.beacon` evidence truth

## Companion docs

- `./architecture-blueprint.md`
- `./command-surface-simplification-blueprint.md`
- `./project-skill-qa-evolution-blueprint.md`
- `../release/v1.2.0.md`
