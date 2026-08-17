# External Lifecycle Mapping

This is a non-canonical support reference for humans.

It explains how external skill systems map into Beacon without changing Beacon's own mainline.

## One-line positioning

- `agent-skills` = engineering skill library
- `gstack` = specialist software factory
- Beacon = truth / evidence / governance kernel

## Mapping

`agent-skills` phase model:

```text
define -> plan -> build -> verify -> review -> ship
```

Beacon mapping:

```text
prd -> user-story -> test-case -> implement -> qa -> release
```

`gstack` specialist sprint model:

```text
think -> plan -> build -> review -> test -> ship -> reflect
```

Beacon mapping:

- `think` / challenge / specialist overlays -> Beacon support surfaces
- `plan` -> `prd`, `user-story`, `test-case`
- `build` -> `implement`
- `test` / verification -> `qa`
- `ship` -> `release`

## Boundary

These mappings improve readability and adoption only.

They do not:

- create new Beacon lifecycle stages
- turn support surfaces into truth surfaces
- replace Beacon's canonical truth or fail-closed gate model
