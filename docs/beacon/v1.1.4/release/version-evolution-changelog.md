# Beacon Version Evolution Changelog (to v1.1.4)

## Summary

This changelog summarizes the product and implementation evolution that led to v1.1.4.

## Version timeline

| Version | Theme | Key increment |
| --- | --- | --- |
| v1.0.0 | Baseline workflow kernel | Established think / story / PRD / test-case / gate backbone |
| v1.0.1 | Reliability hardening | Reduced false-pass behavior and strengthened state handling |
| v1.0.2 | QA9 closure | Connected test-case, auto-test, gate, release evidence |
| v1.0.3 | Memory + recovery | Improved workflow lifecycle, memory semantics, release checking |
| v1.1.0 | Governance tightening | Strengthened config, gate, docs, and execution governance |
| v1.1.1 | Source-of-truth consolidation | Moved Beacon to `docs/beacon/<version>/` as the formal delivery root |
| v1.1.2 | Prototype lifecycle | Added prototype create / review / freeze contracts |
| v1.1.3 | Boundary consolidation | Clarified Beacon core boundary and command layering |
| v1.1.4 | Skill / implement execution adapters | Added `beacon skill`, `beacon implement`, workflow delegation, and standard skill packaging |

## v1.1.4 focus

Compared with v1.1.3, v1.1.4 adds:

1. explicit implementation adapter execution
2. runner / skill adapter registry
3. implementation request/result contracts
4. implementation summary + review surfaced writeback
5. standard `skills/beacon/` package layout aligned to `docs/skill-development-standards.md`

## Notes

- v1.1.4 is the first version where Beacon not only documents implementation adapters, but actually ships them.
- v1.1.4 also closes the gap between root compatibility `SKILL.md` and standard `skills/<name>/SKILL.md` packaging.
