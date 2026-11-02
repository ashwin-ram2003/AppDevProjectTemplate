---
quick_id: 260914-rco
slug: add-r2-rubric-item-ownership-labels-to-e
date: 2026-09-14
---

Add explicit R2-x rubric ownership labels to each track section in `.planning/WORK-ITEMS.md`,
mirroring how R1-x is already visible via the US-R1-* story cards. Currently Phase 2 items show
only their domain requirement code (e.g. DATA-01, INV-01) — nothing states which R2-1/R2-2/R2-3
rubric item a track's Phase 2 work collectively satisfies, even though `REQUIREMENTS.md`'s Rubric
Item Ownership table already has this mapping.

## Tasks

1. In `.planning/WORK-ITEMS.md`, add a "**Rubric ownership:**" line directly under each track
   section's **Goal:** line, stating both rubric items that track owns:
   - Track A (section 1, "Account & Authentication"): `**Rubric ownership:** R1-1 (Project Plan) ·
     R2-2 (live user/household data, no hard-coding)`
   - Track B (section 3, "Inventory Management"): `**Rubric ownership:** R1-2 (Feature board) ·
     R2-1 (food-item resources in DB + API)`
   - Track C (section 4, "Data Integration & API"): `**Rubric ownership:** R1-4 (Tool choice &
     approach) · Stretch Features (US-13, US-14) in place of a numbered R2 item`
   - Track D (section 5, "Deployment & Quality"): `**Rubric ownership:** R1-3 (High-level sketch)
     · R2-3 (Cloud deployment)`
   (Section 2, "Household Management", is also Track A but doesn't need a duplicate line since
   section 1 already states Track A's ownership — add a one-line cross-reference instead: `**Part
   of:** Track A — see Rubric ownership in section 1.`)
2. Update the artifact HTML at `/Users/aphan/.claude/jobs/ab0bf1a4/tmp/board/board.html` the same
   way: add a small rubric-ownership line under each `.feature-goal` paragraph in each of the 4
   numbered feature sections (1, 3, 4, 5) using the same wording as above; section 2 gets the
   "Part of Track A" cross-reference.
3. Commit the WORK-ITEMS.md change (message like "docs: add R2 rubric ownership labels to each
   track section on the feature board"). The artifact HTML file is outside the git repo (lives in
   a job scratch directory) — do not attempt to commit it.

## Acceptance

- Every track section states which R1 and R2 (or stretch-feature) rubric item it owns, visible at
  a glance without cross-referencing REQUIREMENTS.md.
- No existing item rows, IDs, or Req columns are altered — this is additive only.
