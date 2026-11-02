---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 7
total_count: 8
last_updated: 2026-09-24T23:18:47.673Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 02 | unrun-verify | .planning/phases/02-inventory-management/02-01-PLAN.md |  | Task 4's <human-check> browser click-through steps (start backend+frontend, manually restock Oats via the UI, confirm capacity/availability update without reload) were not run interactively; deferred to end-of-phase per HUMAN_VERIFY_MODE=end-of-phase. A live HTTP smoke test against the real Flask dev server (not just the Flask test client) was run as partial substitute evidence. | fixed |  | 2026-09-16T06:10:16.842Z | 2026-09-22T20:19:15.975Z |
| 2 | 02 | stub | client/src/App.js | 11 | HOUSEHOLD_ID/USER_ID are hardcoded placeholders (not fetched via a login/session flow) because Track A's auth/session layer (ACCT-04) has not landed yet; Track A wires real session values in once it lands. | open |  | 2026-09-16T06:10:22.438Z |  |
| 3 | 02 | unrun-verify | client/src/components/FreshnessBadge.js |  | Task 3 human-check (browser click-through confirming badge wording for Pantry/Fridge/Freezer at each freshness value) deferred per HUMAN_VERIFY_MODE=end-of-phase; automated checks (build, grep wording checks) passed. | fixed |  | 2026-09-16T06:19:14.794Z | 2026-09-22T20:19:16.134Z |
| 4 | 02 | unrun-verify | client/src/components/BatchList.js |  | Task 3 human-check (5-step browser click-through: merge Milk/milk batches with distinct best-by dates and confirm consumption order, loose-match merge (Whole Milk), ambiguous restock notice (Skim Milk then Milk), Freezer/Fridge location separation, no-best-by-date dash rendering) deferred per HUMAN_VERIFY_MODE=end-of-phase; automated checks (npm run build, no-sort grep, BatchList-wired grep, full pytest suite) all passed. | fixed |  | 2026-09-16T06:27:16.165Z | 2026-09-22T20:19:16.225Z |
| 5 | 02 | unrun-verify | client/src/components/Checkout.js |  | Task 3 human-check (6-step browser click-through: consume drains soonest-expiring batch, insufficient-stock message retains typed quantity, reserve shows claimant name and drops availability, another member's consume still succeeds on a fully-reserved item, release button hidden for non-owners and works for owner, two reservations by same member each independently releasable) deferred per HUMAN_VERIFY_MODE=end-of-phase; automated checks (npm run build, ItemActions-wired grep, releaseReservation grep, no-disabled-on-reservation grep, full pytest suite) all passed. | fixed |  | 2026-09-16T06:37:42.061Z | 2026-09-22T20:19:16.306Z |
| 6 | 05 | unrun-verify | client/src/components/Project.js |  | Task 1 human-check deferred: backend unreachable in sandboxed worktree — visual card-striping, expand/collapse, and click-containment not confirmed in a live browser | fixed |  | 2026-09-24T19:10:51.851Z | 2026-09-24T23:18:47.508Z |
| 7 | 05 | unrun-verify | client/src/App.css |  | Task 2 human-check deferred: backend unreachable in sandboxed worktree — button focus-ring visibility, hover border-darken, and disabled-state rendering not confirmed in a live browser | fixed |  | 2026-09-24T19:10:56.997Z | 2026-09-24T23:18:47.591Z |
| 8 | 05 | unrun-verify | client/src/components/BatchList.js |  | Task 3 human-check deferred: backend unreachable in sandboxed worktree — batch-card stacking at 375px, batch order matching server response, and item-actions row wrapping not confirmed in a live browser | fixed |  | 2026-09-24T19:11:01.674Z | 2026-09-24T23:18:47.673Z |

````json
[
  {
    "id": 1,
    "kind": "unrun-verify",
    "phase": "02",
    "file": ".planning/phases/02-inventory-management/02-01-PLAN.md",
    "line": null,
    "description": "Task 4's <human-check> browser click-through steps (start backend+frontend, manually restock Oats via the UI, confirm capacity/availability update without reload) were not run interactively; deferred to end-of-phase per HUMAN_VERIFY_MODE=end-of-phase. A live HTTP smoke test against the real Flask dev server (not just the Flask test client) was run as partial substitute evidence.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-09-16T06:10:16.842Z",
    "resolved_at": "2026-09-22T20:19:15.975Z"
  },
  {
    "id": 2,
    "kind": "stub",
    "phase": "02",
    "file": "client/src/App.js",
    "line": 11,
    "description": "HOUSEHOLD_ID/USER_ID are hardcoded placeholders (not fetched via a login/session flow) because Track A's auth/session layer (ACCT-04) has not landed yet; Track A wires real session values in once it lands.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-16T06:10:22.438Z",
    "resolved_at": null
  },
  {
    "id": 3,
    "kind": "unrun-verify",
    "phase": "02",
    "file": "client/src/components/FreshnessBadge.js",
    "line": null,
    "description": "Task 3 human-check (browser click-through confirming badge wording for Pantry/Fridge/Freezer at each freshness value) deferred per HUMAN_VERIFY_MODE=end-of-phase; automated checks (build, grep wording checks) passed.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-09-16T06:19:14.794Z",
    "resolved_at": "2026-09-22T20:19:16.134Z"
  },
  {
    "id": 4,
    "kind": "unrun-verify",
    "phase": "02",
    "file": "client/src/components/BatchList.js",
    "line": null,
    "description": "Task 3 human-check (5-step browser click-through: merge Milk/milk batches with distinct best-by dates and confirm consumption order, loose-match merge (Whole Milk), ambiguous restock notice (Skim Milk then Milk), Freezer/Fridge location separation, no-best-by-date dash rendering) deferred per HUMAN_VERIFY_MODE=end-of-phase; automated checks (npm run build, no-sort grep, BatchList-wired grep, full pytest suite) all passed.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-09-16T06:27:16.165Z",
    "resolved_at": "2026-09-22T20:19:16.225Z"
  },
  {
    "id": 5,
    "kind": "unrun-verify",
    "phase": "02",
    "file": "client/src/components/Checkout.js",
    "line": null,
    "description": "Task 3 human-check (6-step browser click-through: consume drains soonest-expiring batch, insufficient-stock message retains typed quantity, reserve shows claimant name and drops availability, another member's consume still succeeds on a fully-reserved item, release button hidden for non-owners and works for owner, two reservations by same member each independently releasable) deferred per HUMAN_VERIFY_MODE=end-of-phase; automated checks (npm run build, ItemActions-wired grep, releaseReservation grep, no-disabled-on-reservation grep, full pytest suite) all passed.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-09-16T06:37:42.061Z",
    "resolved_at": "2026-09-22T20:19:16.306Z"
  },
  {
    "id": 6,
    "kind": "unrun-verify",
    "phase": "05",
    "file": "client/src/components/Project.js",
    "line": null,
    "description": "Task 1 human-check deferred: backend unreachable in sandboxed worktree — visual card-striping, expand/collapse, and click-containment not confirmed in a live browser",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-09-24T19:10:51.851Z",
    "resolved_at": "2026-09-24T23:18:47.508Z"
  },
  {
    "id": 7,
    "kind": "unrun-verify",
    "phase": "05",
    "file": "client/src/App.css",
    "line": null,
    "description": "Task 2 human-check deferred: backend unreachable in sandboxed worktree — button focus-ring visibility, hover border-darken, and disabled-state rendering not confirmed in a live browser",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-09-24T19:10:56.997Z",
    "resolved_at": "2026-09-24T23:18:47.591Z"
  },
  {
    "id": 8,
    "kind": "unrun-verify",
    "phase": "05",
    "file": "client/src/components/BatchList.js",
    "line": null,
    "description": "Task 3 human-check deferred: backend unreachable in sandboxed worktree — batch-card stacking at 375px, batch order matching server response, and item-actions row wrapping not confirmed in a live browser",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-09-24T19:11:01.674Z",
    "resolved_at": "2026-09-24T23:18:47.673Z"
  }
]
````
