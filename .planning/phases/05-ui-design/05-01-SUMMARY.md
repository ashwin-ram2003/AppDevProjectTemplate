---
phase: 05-ui-design
plan: 01
subsystem: ui
tags: [css-custom-properties, design-tokens, react, responsive, accessibility]

# Dependency graph
requires:
  - phase: 02-inventory-management
    provides: InventoryView/Project.js, BatchList.js, Checkout.js/ItemActions, FreshnessBadge.js, RestockForm.js — the working presentational components this plan restyles
provides:
  - "A :root design-token system (color/spacing/typography/radius/motion) in client/src/index.css"
  - "Token-driven, location-striped item-card and batch-card markup replacing <table> in Project.js and BatchList.js"
  - "The project's first responsive breakpoint (599px) with no-horizontal-scroll phone layout"
  - "Designed hover/focus-visible/disabled button states with a named-property transition and reduced-motion fallback"
  - "InventoryView session-identity JSDoc contract and App.js call-site comment"
  - ".planning/phases/05-ui-design/05-DESIGN.md — canonical token reference and session-identity contract, read by Track A and Track C"
affects: [05-02-ui-design, track-a-account-household, track-c-data-integration]

# Actuals (#2632)
actuals:
  tokens: 6469
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CSS custom properties in a single :root block, extended (not duplicated), consumed via var() throughout App.css"
    - "Table-to-card responsive restructure preserving <details>/<summary> disclosure and stopPropagation click-containment"
    - "BEM-style modifier naming (.item-card--{pantry|fridge|freezer}) extending the existing .freshness-badge--{state} convention"
    - "Shared comma-selector interactive-state rule set (resting/hover/focus-visible/disabled) with a named-property transition and prefers-reduced-motion fallback"

key-files:
  created:
    - .planning/phases/05-ui-design/05-DESIGN.md
  modified:
    - client/src/index.css
    - client/src/App.css
    - client/src/App.js
    - client/src/components/Project.js
    - client/src/components/BatchList.js

key-decisions:
  - "Ambiguity-notice keeps its amber (expiring) border and text color but its background becomes the neutral parchment surface token, per Task 2's explicit surfaces instruction — this reads as a paper panel with an amber accent rather than a fully-amber-tinted box."
  - "No new CSS custom properties were needed for Task 2's sweep — every remaining px/rem/hex value in App.css mapped exactly onto a token already declared in Task 1, confirming the spacing/typography scale audited in RESEARCH.md was complete."

patterns-established:
  - "Design-token :root block in index.css is the single source of truth; any future component styling must reference existing var(--*) names before introducing a new literal."
  - "Card-list markup (<ul class=\"item-card-list\">/<ul class=\"batch-card-list\">) is the established mobile-safe pattern for any future tabular data in this client."

requirements-completed: [DESIGN]

coverage:
  - id: D1
    description: "Design-token :root system in index.css extends (not duplicates) the existing font/color declarations; App.css references tokens exclusively with zero hex literals"
    requirement: "DESIGN"
    verification:
      - kind: unit
        ref: "grep -c ':root' client/src/index.css == 1; grep -oE '#[0-9a-fA-F]{3,8}' client/src/App.css | wc -l == 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "Item rows in all three storage locations render as location-striped shelf cards (no <table>), with expand/collapse and Consume/Reserve click-containment behavior unchanged"
    requirement: "DESIGN"
    verification:
      - kind: unit
        ref: "grep -cE '<table|colSpan' client/src/components/Project.js == 0; grep -c 'item-disclosure' client/src/components/Project.js == 1"
        status: pass
    human_judgment: true
    rationale: "Click-to-expand and click-containment behavior and the visual rendering of the location stripe can only be confirmed by driving the running app in a browser; the backend was unreachable in this sandboxed worktree so the Task 1/2/3 <human-check> blocks were not executed this session."
  - id: D3
    description: "Batch history renders as a labelled card list at every width, preserving its render-order contract; batch fields and item-action rows stack vertically below 599px with no horizontal overflow"
    requirement: "DESIGN"
    verification:
      - kind: unit
        ref: "grep -cE '<table|<thead|<tbody' client/src/components/BatchList.js == 0; grep -c 'sort(' client/src/components/BatchList.js == 0; grep -c '@media' client/src/App.css == 2"
        status: pass
    human_judgment: true
    rationale: "Visual stacking at 375px and 1200px, and batch-order-matches-server-response, require a running browser session against a live backend, which was unavailable in this sandboxed worktree."
  - id: D4
    description: "Every interactive button has a designed resting/hover/focus-visible/disabled state with a named-property transition and a prefers-reduced-motion fallback"
    requirement: "DESIGN"
    verification:
      - kind: unit
        ref: "grep -c 'focus-visible' client/src/App.css == 3; grep -c 'prefers-reduced-motion' client/src/App.css == 1; grep -cE 'transition:[^;]*\\ball\\b' client/src/App.css == 0"
        status: pass
    human_judgment: true
    rationale: "Whether the focus ring is visibly brown, the hover border-darken reads correctly, and no layout shifts on hover requires visual confirmation in a browser, deferred per this task's precondition."

# Metrics
duration: 35min
completed: 2026-09-24
status: complete
---

# Phase 5 Plan 1: Warm-Kitchen Shelf-Card Tokens & Markup Summary

**Full `:root` design-token system plus a table-to-card restructure of `Project.js`/`BatchList.js` giving PantryTrack its first responsive breakpoint and its first designed button interaction states.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-09-24T20:52:00Z (approx, after fast-forwarding worktree onto phase-05 planning commits)
- **Completed:** 2026-09-24T21:27:00Z
- **Tasks:** 3
- **Files modified:** 6 (1 created, 5 modified)

## Accomplishments
- Extended `client/src/index.css`'s existing `:root` block with a ~53-token warm-kitchen design system: colour (base neutrals, three location-stripe colours, four freshness-state triples, two reservation-claim triples), a 10-step spacing scale, typography, radius/structure, and motion tokens — all pre-existing App.css values, none rounded or redesigned.
- Replaced `Project.js`'s `<table className="item-table">` item rows with a `<ul className="item-card-list">` of location-striped `<li className="item-card item-card--{location}">` cards, keeping the `<details>`/`<summary>` disclosure, `BatchList`, `AmbiguityNotice`, and `ItemActions` nesting byte-identical in order.
- Replaced `BatchList.js`'s `<table className="batch-table">` with a `<ul className="batch-card-list">` of labelled `<li className="batch-card">` field rows (Quantity/Purchased/Best-by/Freshness), preserving the file's render-order JSDoc contract verbatim and adding no client-side sort.
- Swept every remaining hex/px/rem literal out of `App.css`, replacing each with its matching token; designed a shared resting/hover/focus-visible/disabled state set for every button (`.restock-form button`, `.item-actions__row button`, `.reservation-entry__release`) with a two-property named transition and a `prefers-reduced-motion` fallback.
- Added the project's first responsive breakpoint (`@media (max-width: 599px)`), extended across all three tasks into a single block, so item summaries, batch cards, and item-action rows stack vertically with no horizontal scroll.
- Documented `InventoryView`'s session-identity prop contract in JSDoc and at the `App.js` call site, and created `.planning/phases/05-ui-design/05-DESIGN.md` — the canonical token reference and session-identity contract that Track A and Track C read.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end "a Pantry item is a shelf card"** — `c1d1221` (feat)
2. **Task 2: Every remaining App.css selector consumes tokens, interactive states designed** — `3a78792` (feat)
3. **Task 3: Batch lists become card lists, action rows stack at phone width** — `dccd5d2` (feat)

_No TDD tasks in this plan — all three are `tdd="false"` presentation-layer restructures._

## Files Created/Modified
- `client/src/index.css` - Extended `:root` with the full design-token set (color/spacing/typography/radius/motion), original three declarations rewritten to consume tokens
- `client/src/App.css` - Deleted `.item-table`/`.item-row-cell`/`.batch-table`; added `.item-card-list`/`.item-card`(+3 location modifiers)/`.batch-card-list`/`.batch-card`(+fields); tokenized every remaining literal; added shared button interactive states; added and extended the 599px media block
- `client/src/App.js` - Added a one-line comment at the `InventoryView` call site pointing to `05-DESIGN.md`
- `client/src/components/Project.js` - Restructured `LocationSection`'s item rows from `<table>` to `<ul class="item-card-list">`; added `InventoryView` JSDoc session-identity contract
- `client/src/components/BatchList.js` - Restructured the batch table to a labelled `<ul class="batch-card-list">`, preserving the render-order JSDoc paragraph verbatim
- `.planning/phases/05-ui-design/05-DESIGN.md` - New canonical doc: full token reference table (colour/spacing/typography/radius) and `InventoryView` session-identity contract

## Decisions Made
- `.ambiguity-notice`'s background becomes the neutral `--color-surface` parchment token (per Task 2's explicit surfaces instruction) while its border and text keep the `--color-expiring-*` amber tokens — a paper panel with an amber accent rather than a fully amber-tinted box. Both instructions in the plan text applied cleanly to different properties on the same selector; no conflict in the final CSS.
- No new design tokens were introduced in Task 2's sweep — every remaining literal in `App.css` mapped exactly to a token already declared in Task 1, confirming RESEARCH.md's audited spacing/typography scale was complete.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' automated `<verify>` commands and `<acceptance_criteria>` checks pass; scope boundaries (no edits to `client/src/api/inventory.js`, `server/`, event handlers, props, `FreshnessBadge.js` logic, or `package.json`) were respected throughout.

**Worktree base note (not a plan deviation, but material to reproducibility):** this worktree's branch was created from a commit (`e6206d0`) that predates the phase-05 planning commits (context/research/patterns/plan). Before starting Task 1, the branch was fast-forward merged onto `main` (`git merge main --ff-only`, a strict fast-forward with no rewrite and no conflicts) to bring in `05-01-PLAN.md` and its supporting docs, which otherwise did not exist in the worktree.

## Issues Encountered
- `client/node_modules/` was not present in the worktree (a fresh checkout). Ran `npm install --no-audit --no-fund` against the existing, unmodified `package-lock.json` to restore it for the build-verification step — zero new packages added, `package.json`/`package-lock.json` untouched, consistent with the plan's zero-install scope boundary.
- The Flask backend was not reachable from this sandboxed worktree (no listening server, no `server/` process running), so the `<human-check>` portions of all three tasks' `<verify>` blocks — visual confirmation of card striping, expand/collapse, click-containment, phone-width stacking, and button focus/hover states — were deferred per each task's `<precondition>` instruction ("If the backend is unreachable, run the automated checks, record the human-check as deferred to the end-of-phase verification, and continue"). All automated checks and acceptance criteria ran and passed. The deferred visual checks are recorded in the `coverage:` block above as `human_judgment: true` and should be run as part of end-of-phase verification once a live dev server + backend is available.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `05-DESIGN.md` is in place with the full token table and `InventoryView` session-identity contract; plan 05-02 can proceed to add per-component prop contracts and any remaining component-level token/spacing polish (`RestockForm.js`, `Checkout.js`, `FreshnessBadge.js`) referencing the same token names.
- The card-list markup pattern (`item-card-list`/`batch-card-list`) and the 599px breakpoint are established precedents for 05-02.
- **Blocker for full sign-off:** the deferred human-check visual passes (Tasks 1–3) must be run against a live `npm --prefix client run dev` + reachable Flask/MongoDB backend before this phase's SC-1/SC-2 success criteria can be marked fully verified, not just code-verified.

---
*Phase: 05-ui-design*
*Completed: 2026-09-24*

## Self-Check: PASSED

- FOUND: client/src/index.css
- FOUND: client/src/App.css
- FOUND: client/src/App.js
- FOUND: client/src/components/Project.js
- FOUND: client/src/components/BatchList.js
- FOUND: .planning/phases/05-ui-design/05-DESIGN.md
- FOUND: .planning/phases/05-ui-design/05-01-SUMMARY.md
- FOUND commit: c1d1221 (Task 1)
- FOUND commit: 3a78792 (Task 2)
- FOUND commit: dccd5d2 (Task 3)
