# Beacon v1.2.0 Project Skill / QA Evolution Blueprint

## Goal

Translate the v1.2.0 project-skill workstream into one bounded execution plan that still serves the mainline:

```text
PRD
→ user-story
→ QA
→ implementation evidence
→ review / gate / release
```

This blueprint exists to stop `beacon skill discover` from being treated as a tiny command patch or a generic project analyzer.

---

## 1. Why this blueprint is required

The shipped repo now has:

- `beacon/commands/skill.py` for adapter registry / bind / doctor
- `beacon/utils/project_skills.py` for project profile, orchestration, and evidence gates
- `beacon/commands/help.py` + `beacon/utils/help_support.py` for stage-aware navigation
- `beacon/commands/profile.py` for profile create/show
- `beacon/commands/doctor.py` for package verification

What `v1.2.0` now adds as one coherent requirement-to-implementation contract is:

1. project feature detection
2. template loading
3. recommendation scoring and explanation
4. preview/apply semantics
5. shared result consumption by help / doctor / profile

This blueprint exists so `discover` stays bounded instead of drifting into scattered utils and ambiguous UX.

---

## 2. Product role of `beacon skill discover`

`beacon skill discover` is a **project onboarding and binding command**.

Its value is not “more analysis”.
Its value is:

```text
analyze project
→ recommend skill/profile/template
→ preview the proposed config
→ explicitly apply
→ validate and route into the mainline
```

This means it must remain subordinate to project adaptation, not become a new product center.

---

## 3. Canonical operator contract

Recommended command surface:

```bash
beacon skill discover   --project-root .   --template <name>   --from-memory   --apply-recommended   --dry-run   --json
```

### Required behavior

1. **detect** project features statically
2. **recommend** bounded skill/profile/template outputs
3. **preview** the diff/result by default
4. **apply** only on explicit opt-in
5. **explain** every recommendation with evidence and reasons
6. **persist** the recommendation artifact for later help/doctor/profile consumption

### Forbidden behavior

- executing arbitrary project code as part of discovery
- writing config by default without preview/apply intent
- returning a generic narrative project report without binding semantics

---

## 4. Artifact contract

### 4.1 Human-visible artifacts

- existing requirement docs under `docs/beacon/v1.2.0/`
- this blueprint
- release note describing the frozen requirement package

### 4.2 Machine/state artifacts

Recommended discovery state path:

```text
.beacon/state/skill-discovery/<project-or-feature>.json
```

Recommended fields:

- `project_features`
- `recommended_templates`
- `recommended_skills`
- `recommendation_scores`
- `recommendation_reasons`
- `source_evidence`
- `config_diff`
- `applied`
- `applied_at`

### 4.3 Config contract

Recommended additive config surface in `beacon.config.yaml`:

```yaml
project_skills:
  discovery:
    preferred_templates:
      - web-fullstack
    recommendation_policy: auto
    memory_enabled: true
    template_dirs:
      - beacon/templates/skill_profiles
```

This surface must stay additive and merge-friendly.

---

## 5. Source touchpoints

### Existing modules to reuse

- `beacon/commands/skill.py`
- `beacon/utils/project_skills.py`
- `beacon/commands/help.py`
- `beacon/utils/help_support.py`
- `beacon/commands/profile.py`
- `beacon/commands/doctor.py`
- `beacon/utils/implement_adapters.py`
- `beacon/commands/test_case.py` / machine QA bundle generation
- `beacon/utils/story_state.py` / frozen machine story baseline

### Landed new modules for v1.2.0 implementation

- `beacon/utils/project_analyzer.py`
- `beacon/utils/skill_templates.py`
- `beacon/utils/skill_discovery.py`

The new modules exist to keep `project_skills.py` from becoming an unbounded kitchen sink.

---

## 6. Shared-linkage requirements

### Help
If a project needs project-skill onboarding and no valid profile binding exists, `help` should be able to recommend:

```text
beacon skill discover --project-root .
```

### Profile
`profile` must be able to consume or review discovery-produced profile data without creating a second configuration model.

### Skill doctor
`skill doctor` must validate discovery-produced templates / registry entries / capability contracts using the same source of truth.

---

## 7. Relationship to story-QA baseline bundle

Project-skill discovery is not separate from the mainline bundle.
It should improve how projects enter the same bundle:

- PRD
- user-story
- `.machine/user-story/<feature>.json`
- QA markdown
- `.machine/qa/<feature>.ac-test-matrix.json`
- `.machine/qa/<feature>.story-scenario-map.json`
- `.machine/qa/<feature>.qa9-matrix.json`
- coverage / evidence scorecard

The output of discovery must make this bundle easier to execute, not replace it.

---

## 8. Suggested implementation order

1. add explicit `skill discover` requirement contract to the docs line
2. add machine baseline bundle for the frozen feature line
3. implement static project analyzer + template loader + recommendation engine
4. connect help / profile / skill doctor to the shared discovery result
5. only then consider richer memory-aware recommendation refinements

---

## 9. Freeze criteria for this workstream

The workstream is requirement-closed when:

1. `skill discover` is documented as preview-first and explainable
2. state/config artifacts are explicitly defined
3. code touchpoints are mapped
4. help/profile/doctor linkage is explicit
5. the v1.2.0 runtime line can generate its machine baseline bundle, implementation closure, and release artifacts cleanly

---

## 10. Imported additions from the deep project-skill analysis

### 10.1 Template-library direction

The deeper analysis recommends starter-pack families such as:

- `web-fullstack`
- `mobile-app`
- `api-service`
- `data-pipeline`
- `ml-model`
- domain second-development packs (ERP / CMS variants)

These families are directional requirements for v1.2.0, even if not all templates are implemented yet.

### 10.2 Memory-aware recommendation direction

The deep analysis also justifies a bounded optimization layer for discovery based on:

- project features
- historical skill success patterns
- prior issue / pain-point memory

This belongs to the discovery surface, not to a separate product center.

### 10.3 Prototype-anchor link

The project-skill research reinforces that `skill discover` and prototype anchoring are related only through the same mainline:

```text
project onboarding
→ requirement bundle
→ prototype anchor checks
→ QA / gate / release
```

Project-skill discovery should therefore improve the same bundle execution, not fork a second workflow.

### 10.4 Deferred generic discover

The broader codebase-analysis `beacon discover` idea is intentionally deferred from the v1.2.0 core requirement package.
If it ever lands, it should do so as a future advanced/labs surface.
