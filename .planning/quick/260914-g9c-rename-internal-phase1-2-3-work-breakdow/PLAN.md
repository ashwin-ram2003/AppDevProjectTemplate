---
quick_id: 260914-g9c
slug: rename-internal-phase1-2-3-work-breakdow
date: 2026-09-14
---

Rename our internal 3-part work-breakdown structure from "Phase 1/2/3" to "Track A/B/C" across
planning docs, to eliminate collision with the assignment PDF's own grading "Phase 1" (5pts,
docs-only) / "Phase 2" (10pts, working app). "Phase" is reserved exclusively for those two
assignment-defined grading milestones going forward.

## Tasks

1. `.planning/ROADMAP.md` — rename "Phase 1/2/3" headings/body text to "Track A/B/C"; drop the
   redundant "Phase N /" prefix already paired with Track labels; repurpose or remove the
   "Phase Numbering" (integer/decimal) explanatory note since it doesn't apply to tracks.
2. `.planning/WORK-ITEMS.md` — same rename in each section header ("Phase 1 / Track A" → "Track A").
3. `.planning/STATE.md` — update "Current focus", "Current Position", and "Decisions" prose from
   Phase to Track terminology. Leave GSD's own structural frontmatter keys (`total_phases`, etc.)
   untouched — this is a prose/label rename only, not a schema change.
4. `.planning/PROJECT.md` and `.planning/REQUIREMENTS.md` — rename any references to our own
   Phase 1/2/3 numbering to Track A/B/C. Do NOT touch correct references to the PDF's real
   "Phase 1"/"Phase 2" grading milestones.
5. Add the two untracked files (`.planning/.gsd-allow-shrink`, `Team Project_Fa26.pdf`) to this
   commit — both belong in the repo (gsd config marker; assignment source doc).

## Acceptance

- No planning doc uses "Phase" to refer to our own 3-part breakdown; all such references say
  "Track A/B/C" instead.
- References to the assignment's actual Phase 1 / Phase 2 grading milestones are unchanged.
- Docs remain internally consistent (no leftover "Phase 1 of 3" style progress counters using the
  old numbering).
