# Release Checklist v1.4.12

## Truth Package
- [x] version-material-file-map-contract: PRD, user-story, test-case frozen
- [x] unified-truth-template-cli-contract: PRD, user-story, test-case frozen
- [x] freeze-states written with baseline hashes
- [x] SUMMARY.md updated
- [x] global-boundaries.md checked (no boundary violations)

## Implementation
- [x] manifest core module (beacon/utils/manifest.py)
- [x] manifest CLI (beacon/commands/manifest.py)
- [x] truth_template module (beacon/utils/truth_template.py)
- [x] truth_format module (beacon/utils/truth_format.py)
- [x] truth CLI (beacon/commands/truth.py)
- [x] diagram_truth.py updated (no numbering + propagation)
- [x] material_sync._discover_features migrated to manifest
- [x] material_audit._feature_names migrated to manifest
- [x] prd._render_prd delegates to template for v1.4.12+
- [x] prd_bootstrap._minimal_prd_from_downstream delegates to template for v1.4.12+
- [x] gate integration (truth_format_non_compliant)
- [x] CLI registered in cli_factory.py
- [x] Package version bumped to 1.4.12

## QA
- [x] 15/15 ACs verified (PASS)
- [x] 26/26 unit tests passing
- [x] CLI end-to-end verification (manifest verify, truth verify, truth init)
- [x] Negative tests (numbering rejection, missing Outline, missing mermaid)
- [x] Language detection (en/zh) verified
- [x] diagram_truth assertions verified

## Version Surface
- [x] Package version: 1.4.12
- [x] Toolkit version: v1.4.12
- [x] SUMMARY.md: v1.4.12
- [x] freeze-states: v1.4.12 frozen
- [x] Manifest: v1.4.12, 2 features
- [x] Release note generated

## Skill/Hook
- [ ] Agent skill installed locally
- [ ] Global CLI installed
