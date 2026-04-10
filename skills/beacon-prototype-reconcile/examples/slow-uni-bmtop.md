# Example: slow_uni_bmtop

Use this sequence for the first pass against:

- project root: `/Users/apple/Developer/Personal/products/slow_uni_bmtop`
- docs version: `v1.0.0`

## Pass 1: `miniapp-full-pages-prototype`

### Review inputs

- `docs/beacon/v1.0.0/user-story/miniapp-full-pages-prototype.md`
- `docs/beacon/v1.0.0/prd/miniapp-full-pages-prototype.md`
- `docs/beacon/v1.0.0/prototype/miniapp-full-pages-prototype/*`
- `tournament_miniapp/src/pages/**`
- `tournament_miniapp/src/subPages/**`
- `tournament_miniapp/pages.config.ts`
- `tournament_miniapp/src/components/**`
- `tournament_miniapp/src/App.vue`

### Expected execution outputs

- `docs/beacon/v1.0.0/execution/implementation-truth-miniapp-full-pages-prototype.json`
- `docs/beacon/v1.0.0/execution/route-closure-audit-miniapp-full-pages-prototype.json`
- `docs/beacon/v1.0.0/execution/prototype-gap-list-miniapp-full-pages-prototype.md`
- `docs/beacon/v1.0.0/execution/prototype-patch-report-miniapp-full-pages-prototype.md`

### Priority checks

1. 38-page inventory closure
2. route closure for:
   - `home -> scenario-selection`
   - `scenario-selection -> mode-selection`
   - `mode-selection -> add-participants`
   - `add-participants -> preview-matchups`
   - `preview-matchups -> game-detail`
   - `game-detail -> batch-score-entry`
   - `game-detail -> awards / bracket / spectator / team-stats / team-management`
   - `home-side-drawer -> club-list`
3. parameter consumption for:
   - `scenario`
   - `tournamentId`
   - `stageId`
   - `tab`
4. current-user truth for `my-honors`
5. implementation-map drift vs real route targets

## Pass 2: `miniapp-ui-visual-refresh`

### Review inputs

- `docs/beacon/v1.0.0/user-story/miniapp-ui-visual-refresh.md`
- `docs/beacon/v1.0.0/prd/miniapp-ui-visual-refresh.md`
- `docs/beacon/v1.0.0/prototype/miniapp-ui-visual-refresh/*`
- `tournament_miniapp/src/App.vue`
- `tournament_miniapp/src/theme.json`
- shared components such as:
  - `AppNavbar.vue`
  - `SideDrawer.vue`
  - `QuickScorer.vue`
  - `PowerSlider.vue`
  - `TournamentCard.vue`
  - `MatchCard.vue`

### Priority checks

1. token/theme alignment
2. shared component alignment
3. page-spec visual structure alignment
4. key page fidelity for:
   - `home`
   - `mode-selection`
   - `add-participants`
   - `game-detail`
   - `spectator`
   - `fee-calculator`

## Hand back to Beacon

After each pass:

```bash
beacon prototype review "miniapp-full-pages-prototype" --project /Users/apple/Developer/Personal/products/slow_uni_bmtop --version v1.0.0
beacon review design "miniapp-full-pages-prototype" --project /Users/apple/Developer/Personal/products/slow_uni_bmtop --version v1.0.0
```

Repeat for `miniapp-ui-visual-refresh`.
