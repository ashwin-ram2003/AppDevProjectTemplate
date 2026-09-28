---
quick_id: 260914-glw
slug: add-phase-column-to-work-items-md-and-3-
date: 2026-09-14
---

Add a "Phase" column to `.planning/WORK-ITEMS.md` so each item is tagged with the assignment
PDF's grading milestone it belongs to (Phase 1 = docs-only, due now; Phase 2 = working
implementation), orthogonal to the existing Track A/B/C grouping (who/which module owns it).

## Background

The board currently groups items only by Track (A/B/C). All 12 user stories (US-01..US-12) and
10 technical debt items (TD-01..TD-10) are implementation work, which per the assignment rubric
is Phase 2 work (R2-1/R2-2/R2-3: DB+API, live data, cloud deploy). Phase 1 (R1-1..R1-4) is
project-plan/board/sketch/tool-choice — pure planning, no code. There is currently no board item
representing the Phase-1 planning work each track already did (defining that track's scope,
schema, requirements). This plan adds that.

## Tasks

1. Add a "Phase" column to every item table in `.planning/WORK-ITEMS.md` (5 section tables).
   - All existing items (US-01..US-12, TD-01..TD-10) → `Phase 2`.
2. Add one new Phase-1 documentation item per track, as Technical debt type (not User story —
   these aren't user-facing), inserted at the top of each relevant track's table:
   - Track A (Account & Authentication / Household Management): `TD-DOC-A` — "Define Track A
     scope, schema, and initial stories" — e.g. "Define the account/household data model
     (userid/password fields, household document shape with name/description/householdID) and
     write Track A's initial user stories (US-01..US-05) for the feature board." Phase 1.
   - Track B (Inventory Management): `TD-DOC-B` — "Define Track B scope, schema, and initial
     stories" — e.g. "Define the household item-stock schema (capacity/availability per item,
     keyed by Pantry/Fridge/Freezer location) and write Track B's initial user stories
     (US-06..US-10) for the feature board." Phase 1.
   - Track C (Data Integration & API / Deployment & Quality): `TD-DOC-C` — "Define Track C scope,
     schema, and initial stories" — e.g. "Define the REST API surface and deployment/test plan
     covering DATA-01..03 and OPS-01..02, and write Track C's initial user stories
     (US-11..US-12) for the feature board." Phase 1.
   Each new item's Req column can reference the track's requirement group (e.g. "ACCT/HH" for A).
3. Update the board's closing "Totals" line to reflect the 3 new items (12 → 12 user stories
   unchanged, 10 → 13 technical debt items, note Phase 1 vs Phase 2 split).
4. Update `.planning/STATE.md`'s "Quick Tasks Completed" table with this task.

## Acceptance

- Every row in every WORK-ITEMS.md table has a Phase value (1 or 2).
- Exactly 3 new Phase-1 items exist, one per track, correctly typed as Technical debt.
- Totals line at the bottom of WORK-ITEMS.md is updated and accurate.
- No existing item's Track, Type, or Req mapping is altered — this is additive only.
