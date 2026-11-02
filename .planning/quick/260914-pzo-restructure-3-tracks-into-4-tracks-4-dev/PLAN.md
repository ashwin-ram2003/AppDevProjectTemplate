---
quick_id: 260914-pzo
slug: restructure-3-tracks-into-4-tracks-4-dev
date: 2026-09-14
---

Restructure the project from 3 tracks to 4 tracks (the team confirmed it has 4 developers), give
each track exactly one Phase 1 rubric item (R1-1..R1-4) and one Phase 2 rubric item (R2-1..R2-3)
— except one track, since there are only 3 Phase-2 rubric items for 4 tracks, which instead owns a
promoted set of backlog items as its own committed Phase 2 scope. Write actual board stories for
each of the four Phase 1 rubric items (previously there were no items directly representing
R1-1/R1-2/R1-3/R1-4 — only generic per-track "define scope" placeholders, which must be KEPT, not
replaced).

## Locked decisions (already confirmed with the user — do not re-litigate)

**New track structure** (split the old Track C, which combined two feature-groups, into two
tracks — giving exactly 4 domain tracks):
- **Track A** — Account & Authentication + Household Management (unchanged from before)
- **Track B** — Inventory Management (unchanged from before)
- **Track C** — Data Integration & API (was half of old Track C — keep TD-DOC-C, US-11, TD-05,
  TD-06, TD-07 exactly as they are, just confirm Track label stays "Track C")
- **Track D** — Deployment & Quality (was the other half of old Track C — its existing items
  US-12, TD-08, TD-09, TD-10 must be RELABELED from Track C to Track D; nothing else about them
  changes)

**Rubric item → track assignment** (final, confirmed with user):
- Track A: **R1-1** (Project Plan) + **R2-2** (user/household info live, no hard-coded data)
- Track B: **R1-2** (Feature board) + **R2-1** (food-item/hardware resources in DB + API)
- Track C: **R1-4** (Tool choice & approach) + no R2 item (promoted backlog scope instead, below)
- Track D: **R1-3** (High-level sketch) + **R2-3** (Cloud deployment)

## Tasks

### 1. `.planning/WORK-ITEMS.md` — add 4 new rubric-story items (one per track, Phase 1)

Add these as new rows in each track's existing primary table (Item Type: User story). Use these
IDs and exact wording:

| ID | Track table to insert into | Title | Story | Req | Phase |
|----|----|----|----|----|----|
| US-R1-A | "1. Account & Authentication" (Track A) | Document the project plan | As the instructor, I want a documented project plan covering team members, sprint velocity, collaboration tools, and implementation methodology so I can assess how the team is organized and working together. | R1-1 | 1 |
| US-R1-B | "3. Inventory Management" (Track B) | Publish the feature board | As the instructor, I want to see every planned feature captured as user stories, technical debt, or research items on a shared board so I can verify the team has scoped its work before implementation begins. | R1-2 | 1 |
| US-R1-C | "4. Data Integration & API" (Track C) | Document tool choice & approach | As the instructor, I want a written explanation of the team's chosen tech stack and technical approach so I can evaluate whether the decisions fit the project's needs. | R1-4 | 1 |
| US-R1-D | "5. Deployment & Quality" (Track D) | Sketch the application architecture | As the instructor, I want a high-level sketch of the application's architecture and user flow so I can quickly understand the system's design before reviewing the code. | R1-3 | 1 |

### 2. `.planning/WORK-ITEMS.md` — relabel section 5 from Track C to Track D

Change "## 5. Deployment & Quality — Track C" to "## 5. Deployment & Quality — Track D", and
update the Phase column for its existing 4 items (US-12, TD-08, TD-09, TD-10) if not already set
(they should already be Phase 2 — leave as-is, just confirm the section header's Track label).

### 3. `.planning/WORK-ITEMS.md` — add `TD-DOC-D` (Track D's scope-definition item, for symmetry)

Insert at the top of section 5's table (Technical debt, Phase 1):
`TD-DOC-D | Technical debt | Define Track D scope, schema, and initial stories | Define the
deployment pipeline and test-coverage plan covering OPS-01/OPS-02, and write Track D's initial
user stories (US-12) for the feature board. | OPS | 1`

KEEP the existing TD-DOC-A, TD-DOC-B, TD-DOC-C items exactly as they are (user explicitly asked
to keep these — they are NOT replaced by the new US-R1-* items, which serve a different purpose:
literal rubric-item stories vs. per-track scope-definition placeholders).

### 4. `.planning/WORK-ITEMS.md` — promote 2 backlog items into Track C's own Phase 2 scope

Track C has no R2 rubric item (only 3 exist for 4 tracks), so it gets its own committed feature
scope instead, built from two backlog items that are realistically buildable in a PoC (not
hardware/ML-dependent, unlike the R-01..R-10 research items). Add these as NEW rows in section 4
("Data Integration & API" / Track C)'s table (Item Type: User story, Phase 2):

| ID | Title | Story | Req |
|----|----|----|----|
| US-13 | Reset a forgotten password | As a user who forgot their password, I want to reset it via the existing Forgot Password flow so I can regain access to my household's inventory without contacting an admin. | STRETCH-01 |
| US-14 | Manage custom storage locations | As a household member, I want to define storage locations beyond the default Pantry/Fridge/Freezer (e.g. a garage freezer or wine fridge) so my household's inventory reflects how we actually store food. | STRETCH-02 |

### 5. `.planning/WORK-ITEMS.md` — update stats, legend, and Totals line

- Stats block: user stories count increases by 6 (US-R1-A/B/C/D + US-13/US-14) → new total.
  Technical debt count increases by 1 (TD-DOC-D) → new total.
- Totals line at bottom: update counts, and add a note that 4 tracks now exist, each owning one
  Phase 1 rubric item and either one Phase 2 rubric item or (Track C) a promoted stretch-feature
  scope.

### 6. `.planning/REQUIREMENTS.md` — add new requirement group + rubric ownership table

- Add a new v1 requirement group (after the "Deployment & Quality" group): "### Track C Stretch
  Features (not from PDF rubric — promoted backlog, Track C's Phase 2 scope)" with:
  - `STRETCH-01`: User can reset a forgotten password via the existing Forgot Password flow
  - `STRETCH-02`: User can define custom storage locations beyond Pantry/Fridge/Freezer
- Add a new section "## Rubric Item Ownership" (after the v1 Requirements section, before v2)
  listing R1-1 through R1-4 and R2-1 through R2-3, each with its owning Track per the locked
  decisions above, and a note that Track C's Phase 2 contribution is the Stretch Features group
  instead of a numbered R2 item.
- Remove the old note "R1-1 ... is a separate deliverable owned by another team member and is
  intentionally out of scope here" — replace with a note that R1-1 is now owned by Track A.
- Update the Traceability table: OPS-01 and OPS-02 move from "Track C" to "Track D". Add STRETCH-01
  and STRETCH-02 rows mapped to Track C. Update the Coverage summary counts accordingly.
- In the v2 Requirements section, remove or annotate ENH-01 and ENH-02 (they list these as
  deferred enhancements) to note they've been promoted to v1 committed scope as STRETCH-01/02
  under Track C — do not delete the historical entries, just annotate them as promoted.

### 7. `.planning/ROADMAP.md` — add Track D as its own section, split from Track C

- In the Overview section, update Track C's description to ONLY cover Data Integration & API
  (drop the "plus... Deployment & Quality" language), and add a new Track D description covering
  Deployment & Quality (cloud deploy, PyTest harness, generic-naming cleanup) — move that content
  from the old Track C description.
- In "Phase Details" (still labeled with our Track terminology, NOT literal PDF phases — these
  headings should already say "Track A/B/C" from a prior rename; add a new "Track D:..." section
  after Track C's, following the same Goal/Depends on/Requirements/Success Criteria/Plans format
  as the others), covering OPS-01, OPS-02, and derived from the current Track C description's
  deployment/testing content.
- Update the Progress table to have 4 rows (Track A, B, C, D) instead of 3.
- Update any "Execution Order" or dependency prose that currently describes 3 tracks to describe 4.

### 8. `.planning/PROJECT.md` — reflect the 4-track structure and stretch features

- Add STRETCH-01 and STRETCH-02 to the "Active" requirements checklist (as new unchecked items).
- Add a short note (near the existing Business Context / Strategy notes) that the team now has 4
  developers on 4 tracks, each owning one Phase 1 rubric item and one Phase 2 rubric item (or,
  for Track C, a promoted stretch-feature scope instead).

### 9. `.planning/STATE.md` — update Decisions and Current Position prose

- Add a Decisions bullet documenting: track count went from 3 to 4 (team confirmed 4 developers);
  Track C split into Track C (Data Integration & API) and Track D (Deployment & Quality); rubric
  item ownership locked per the mapping above; Track C's Phase 2 scope comes from 2 promoted
  backlog items instead of a numbered R2 item.
- Update "Current focus" prose if it references the old 3-track structure.

## Acceptance

- WORK-ITEMS.md has exactly 4 new US-R1-* items (one per track, Phase 1, correctly worded per the
  table above), TD-DOC-A/B/C are unchanged, TD-DOC-D is added, section 5 says "Track D", and 2 new
  Track C stretch-feature stories (US-13, US-14) exist as Phase 2 items.
- REQUIREMENTS.md has STRETCH-01/02, a Rubric Item Ownership section matching the locked mapping,
  an updated Traceability table (OPS items now Track D), and no stale "R1-1 owned externally" note.
- ROADMAP.md has 4 track sections (A, B, C, D) each with their own Goal/Depends on/Success Criteria,
  and a 4-row Progress table.
- PROJECT.md and STATE.md reflect the 4-track / 4-developer structure.
- No existing item's core Track/Type/Req mapping is altered except the explicit relabels above
  (US-12/TD-08/TD-09/TD-10 Track C→Track D; OPS-01/OPS-02 traceability Track C→Track D).
