# Beacon v1.2.0 Command Surface Simplification Blueprint

## Goal

Convert the command simplification research into a bounded requirement blueprint for the v1.2.0 line.

The purpose is not “fewer commands at any cost”.
The purpose is:

```text
protect mainline commands
→ lower operator friction
→ route intent through ask/help
→ hide complexity by default
→ preserve backward compatibility
```

---

## 1. Imported research decisions

The command simplification plan contributes four concrete decisions to the requirement package:

1. the mainline command chain stays stable
2. `ask` and `help` become the primary smart-entry surfaces
3. advanced and labs surfaces should be progressively disclosed, not shown by default
4. compatibility aliases / migration guidance should absorb any future renames or merges

---

## 2. Requirement-level command posture

### 2.1 Protected mainline

The stable visible chain remains:

- `think`
- `user-story`
- `prd`
- `test-case`
- `implement`
- `qa`
- `gate`
- `release`

### 2.2 Smart-entry surfaces

`ask` and `help` should carry more of the operator burden:

- intent-to-command recommendation
- stage-aware next-step routing
- clearer distinction between current stage and advanced side paths

### 2.3 Disclosure policy

The requirement line should assume three visibility bands:

1. **core** — mainline and essential operator surfaces
2. **advanced** — specialist/project surfaces such as `skill`, `verify`, `prototype`, `debug`, `revision`, `report`
3. **labs** — experimental or product-toolkit style surfaces that must not crowd the default help surface

The freeze does **not** require the entire rename/merge program to ship now.
It does require the policy direction to be explicit.

---

## 3. Compatibility and migration policy

The research plan also implies these constraints:

- mainline semantics must not drift
- compatibility aliases may absorb future command consolidation
- deprecation should be staged and explainable
- docs/help output must make the disclosure policy obvious

This means v1.2.0 should freeze the **operator contract**, not only an implementation wish list.

---

## 4. Explicit non-goals

This workstream does not require v1.2.0 to:

- immediately rewrite every command family
- remove all legacy/bridge surfaces at once
- solve cross-project tooling by expanding Beacon core
- let labs or toolchain-heavy commands compete with the mainline by default

---

## 5. Expected source touchpoints

The blueprint primarily points at:

- `beacon/command_catalog.py`
- `beacon/cli_factory.py`
- `beacon/commands/help.py`
- `beacon/utils/help_support.py`
- `beacon/commands/ask.py`
- docs/help surfaces (`README`, `SKILL.md`, `skills/beacon/SKILL.md`)

---

## 6. Freeze criteria for this workstream

The command-surface workstream is requirement-closed when:

1. core/mainline command protection is explicit
2. smart routing expectations for `ask` / `help` are explicit
3. advanced/labs disclosure policy is explicit
4. compatibility/deprecation intent is explicit
5. the rest of the v1.2.0 package still orbits the same `PRD → user-story → QA` anchor
