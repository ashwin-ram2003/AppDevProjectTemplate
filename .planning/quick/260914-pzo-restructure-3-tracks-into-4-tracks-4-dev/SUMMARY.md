---
quick_id: 260914-pzo
slug: restructure-3-tracks-into-4-tracks-4-dev
date: 2026-09-14
status: complete
---

# Quick Task 260914-pzo: Restructure 3 Tracks into 4 Tracks (4 Developers) Summary

Restructured PantryTrack's planning docs from a 3-track to a 4-track structure now that the team
has confirmed 4 developers — split the old Track C (which combined Data Integration & API with
Deployment & Quality) into Track C (Data Integration & API) and a new Track D (Deployment &
Quality), added 4 rubric-story items mapping the actual PDF Phase 1 rubric items (R1-1..R1-4) onto
each track, and promoted 2 backlog items into Track C's Phase 2 scope since only 3 of the 4 tracks
can own one of the 3 real Phase 2 rubric items.

## What Changed

### `.planning/WORK-ITEMS.md`
- Added `US-R1-A` (R1-1, Project Plan) to Track A's table
- Added `US-R1-B` (R1-2, Feature board) to Track B's table
- Added `US-R1-C` (R1-4, Tool choice & approach) to Track C's table
- Relabeled section 5 header from "Deployment & Quality — Track C" to "Deployment & Quality — Track D"
- Added `TD-DOC-D` (Track D scope/schema/stories) and `US-R1-D` (R1-3, architecture sketch) to
  section 5's table; existing `US-12`, `TD-08`, `TD-09`, `TD-10` are unchanged in content, only now
  under the Track D header
- Kept `TD-DOC-A`, `TD-DOC-B`, `TD-DOC-C` exactly as they were (explicitly not touched)
- Added `US-13` (Reset a forgotten password, STRETCH-01) and `US-14` (Manage custom storage
  locations, STRETCH-02) to Track C's table as its Phase 2 scope
- Updated Totals line (12 → 18 user stories, 13 → 14 technical debt items, 17 → 19 v1 requirements
  covered) and replaced the stale "R1-1 owned externally" reminder with a note that R1-1 is now
  represented via US-R1-A / Track A; added a "4 tracks, 4 developers" summary line

### `.planning/REQUIREMENTS.md`
- Added a new "Track C Stretch Features" v1 requirement group with `STRETCH-01` and `STRETCH-02`
- Added a "Rubric Item Ownership" section mapping R1-1..R1-4 and R2-1..R2-3 to their owning tracks,
  noting Track C's Phase 2 contribution is the Stretch Features group instead of a numbered R2 item
- Replaced the stale "R1-1 owned by another team member" note with "R1-1 is now owned by Track A"
- Updated the Traceability table: `OPS-01`/`OPS-02` moved from Track C to Track D; added
  `STRETCH-01`/`STRETCH-02` rows mapped to Track C; updated Coverage counts (17 → 19 total, added
  Track D: 2)
- Annotated `ENH-01`/`ENH-02` in the v2 section as promoted to v1 scope under STRETCH-01/STRETCH-02
  (historical entries kept, not deleted)

### `.planning/ROADMAP.md`
- Updated Overview: Track C description now covers only Data Integration & API; added a new Track D
  description covering Deployment & Quality (moved from the old combined Track C description)
- Updated the Phases checklist to list 4 tracks instead of 3
- Updated Track C's "Phase Details" entry (goal, depends-on, requirements, success criteria) to drop
  deployment/testing content and add the 2 stretch-feature success criteria instead
- Added a new "Track D: Deployment & Quality" Phase Details section (goal, depends-on, requirements
  OPS-01/OPS-02, success criteria, plans placeholder) following the same format as the other tracks
- Updated the Progress table to 4 rows (Track A, B, C, D) and updated Execution Order prose

### `.planning/PROJECT.md`
- Added STRETCH-01 and STRETCH-02 to the Active requirements checklist
- Added a Business Context note documenting the 4-developer / 4-track structure and rubric
  ownership pattern

### `.planning/STATE.md`
- Added a Decisions bullet documenting the 3→4 track restructuring, the Track C/D split, and the
  locked rubric item ownership mapping
- Updated "Current Position" (Phase 1 of 4, not 3) and "Current focus" prose to reference Track D
- Updated frontmatter `total_phases` from 3 to 4
- Added this quick task to the "Quick Tasks Completed" table
- Updated Session Continuity "Stopped at" note

## Rubric Item Ownership (final, locked)

| Rubric Item | Owning Track |
|-------------|--------------|
| R1-1 (Project Plan) | Track A |
| R1-2 (Feature board) | Track B |
| R1-4 (Tool choice & approach) | Track C |
| R1-3 (High-level sketch) | Track D |
| R2-1 (Resources in DB + API) | Track B |
| R2-2 (Live user/household data) | Track A |
| R2-3 (Cloud deployment) | Track D |
| — (Track C's Phase 2 scope) | Track C stretch features (STRETCH-01, STRETCH-02) |

## Deviations from Plan

None — plan executed exactly as written. The only additions beyond the plan's literal file-by-file
task list were: (1) fixing the same stale "R1-1 owned externally" note in WORK-ITEMS.md's "Out of
scope reminder" line (not explicitly listed as a WORK-ITEMS.md task, but directly contradicted the
newly added US-R1-A and mirrors the equivalent REQUIREMENTS.md fix the plan did require), and (2)
adding matching "Last updated" footer date lines to REQUIREMENTS.md, ROADMAP.md, and PROJECT.md for
internal consistency with the existing document convention.

## Self-Check: PASSED

- FOUND: `.planning/WORK-ITEMS.md` (modified, committed)
- FOUND: `.planning/REQUIREMENTS.md` (modified, committed)
- FOUND: `.planning/ROADMAP.md` (modified, committed)
- FOUND: `.planning/PROJECT.md` (modified, committed)
- FOUND: `.planning/STATE.md` (modified, committed)
- FOUND commit `4dc1ca7`: "docs: restructure to 4 tracks (4 developers), assign rubric items and promote stretch features"

## Metrics

- **Duration:** ~15 minutes
- **Files modified:** 5
- **Commits:** 1 (`4dc1ca7`)

---
*Completed: 2026-09-14*
