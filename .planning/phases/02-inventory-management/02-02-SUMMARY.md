---
phase: 02-inventory-management
plan: 02
subsystem: api
tags: [flask, freshness, react, food-safety-rules]

# Dependency graph
requires:
  - phase: 02-inventory-management (plan 01)
    provides: "Items collection document shape (batches[] with purchaseDate/bestByDate), GET /api/inventory + POST /api/inventory/restock REST contract, InventoryView (Project.js)"
provides:
  - "server/freshness.py: pure, database-free location-specific freshness rules (Pantry/Fridge/Freezer) with FRESH/EXPIRING_SOON/EXPIRED/UNKNOWN constants and SEVERITY_RANK total order"
  - "item.freshness and item.batches[].freshness computed on every GET /api/inventory response, never persisted"
  - "FreshnessBadge React component rendering location-worded labels (food-safety wording for Pantry/Fridge, quality-decay wording for Freezer)"
affects: [02-03-item-identity-matching, 02-04-reserve-consume, track-d-testing]

# Actuals (#2632)
actuals:
  tokens: 6191
  tasks: 3
  commits: 5

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pure computation modules (freshness.py) take no DB/network args and are annotated onto already-serialized read-path dicts, never written back to Mongo -- the same pattern any future derived/computed field in this codebase should follow"
    - "Server always computes 'today' itself (date.today()) inside the read path; no request parameter may ever supply the current date"

key-files:
  created:
    - server/freshness.py
    - server/tests/test_freshness.py
    - server/tests/test_inventory_freshness.py
    - client/src/components/FreshnessBadge.js
  modified:
    - server/hardwareDatabase.py
    - client/src/components/Project.js
    - client/src/App.css

key-decisions:
  - "Freezer 'months elapsed' defined as whole calendar months (month difference, decremented by one if today's day-of-month hasn't reached purchaseDate's day-of-month) -- documented in freshness.py's module docstring so the boundary math is traceable, not incidental."
  - "computeItemFreshness recomputes each batch's freshness internally from purchaseDate/bestByDate rather than trusting a pre-annotated 'freshness' key on the batch dict -- keeps the roll-up correct regardless of call order in hardwareDatabase.py."
  - "Freshness annotation happens only inside getItemsByLocation (the GET read path); addBatch's own return value (used by the restock response) is untouched, keeping the restock POST response contract from 02-01 unchanged -- avoids an undocumented scope expansion into a response shape the plan didn't ask for."

patterns-established:
  - "Location-specific business rules stay as separate, non-unified functions even when they share a shape -- the freshness.py docstring explicitly warns against later 'simplifying' the three rule-sets into one, because they model different physical processes."

requirements-completed: [INV-05]

coverage:
  - id: D1
    description: "Every item and batch in GET /api/inventory carries a freshness flag (fresh/expiring_soon/expired/unknown) computed from its own dates against today, with no sensor or model input (INV-05)"
    requirement: "INV-05"
    verification:
      - kind: unit
        ref: "server/tests/test_inventory_freshness.py (7 tests: Pantry expired, Fridge expiring_soon, Freezer expired-regardless-of-best-by, mixed-batch roll-up, unknown, empty location, non-persistence)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Pantry has no early warning window (fresh until best-by passes, then expired) -- D-09, including the exact-best-by-date edge case"
    requirement: "INV-05"
    verification:
      - kind: unit
        ref: "server/tests/test_freshness.py#test_pantry_best_by_today_is_fresh, #test_pantry_best_by_yesterday_is_expired, #test_pantry_best_by_five_days_away_is_fresh"
        status: pass
    human_judgment: false
  - id: D3
    description: "Fridge shows expiring_soon within 3 days of best-by and expired after, including the exact-3-days edge case -- D-10"
    requirement: "INV-05"
    verification:
      - kind: unit
        ref: "server/tests/test_freshness.py#test_fridge_best_by_exactly_three_days_away_is_expiring_soon, #test_fridge_best_by_four_days_away_is_fresh, #test_fridge_best_by_yesterday_is_expired"
        status: pass
    human_judgment: false
  - id: D4
    description: "Freezer freshness is computed only from purchase/freeze date (best-by ignored entirely): fresh under 6 months, expiring_soon 6-12 months inclusive, expired beyond 12 months -- D-11, including both exact-boundary edge cases"
    requirement: "INV-05"
    verification:
      - kind: unit
        ref: "server/tests/test_freshness.py#test_freezer_frozen_exactly_six_months_ago_is_expiring_soon, #test_freezer_frozen_exactly_twelve_months_ago_is_expiring_soon, #test_freezer_frozen_thirteen_months_ago_is_expired, #test_freezer_best_by_supplied_alongside_purchase_date_changes_nothing"
        status: pass
    human_judgment: false
  - id: D5
    description: "An item's freshness is the worst freshness among its batches (expired > expiring_soon > fresh > unknown), order-independent; no batches or missing relevant date yields unknown, never fresh or expired"
    verification:
      - kind: unit
        ref: "server/tests/test_freshness.py#test_item_with_one_fresh_and_one_expired_batch_is_expired, #test_item_roll_up_does_not_depend_on_batch_order, #test_item_with_no_batches_is_unknown, #test_pantry_best_by_absent_is_unknown"
        status: pass
    human_judgment: false
  - id: D6
    description: "Freshness is computed on every GET, never persisted to the Items collection, and the server -- never the client -- decides what 'today' is"
    verification:
      - kind: unit
        ref: "server/tests/test_inventory_freshness.py#test_freshness_is_never_persisted_on_the_raw_items_document"
        status: pass
      - kind: other
        ref: "grep -n 'request\\.\\(args\\|get_json\\)' server/app.py shows only householdId/userId (GET) and the restock body fields (POST) -- no today/now/asOf parameter is read anywhere in the inventory path"
        status: pass
    human_judgment: false
  - id: D7
    description: "FreshnessBadge renders a location-worded label: Pantry/Fridge use 'Fresh'/'Use soon'/'Past best-by'; Freezer uses 'Good quality'/'Quality declining'/'Freezer burn risk' with no discard or safety wording; unknown renders 'No date' neutrally for every location; badge wired into the item row with no client-side date arithmetic"
    requirement: "INV-05"
    verification:
      - kind: other
        ref: "grep -c 'Freezer burn risk' client/src/components/FreshnessBadge.js (2), grep -c FreshnessBadge client/src/components/Project.js (2), grep for date-library import/date arithmetic in Project.js (0 matches)"
        status: pass
      - kind: other
        ref: "npm --prefix client run build (vite v5.4.21, exits 0, dist/ emitted)"
        status: pass
    human_judgment: true
    rationale: "The plan's Task 3 <verify> includes a <human-check> requiring a running backend + frontend and manual browser interaction across four restocked items (Pantry/Fridge fresh-window/Freezer quality-decline/Freezer burn-risk/no-date). Per HUMAN_VERIFY_MODE=end-of-phase (project config) and auto_advance=false, this was not run interactively during plan execution -- consistent with plan 02-01's handling of its own Task 4 human-check. Deferred to end-of-phase and logged in .planning/WINDOWS.md as an unrun-verify entry."

duration: ~15min active tool-call work (includes one-time worktree environment setup -- server/.venv and client/node_modules did not exist in this fresh worktree and had to be created/installed before any test could run)
completed: 2026-09-16
status: complete
---

# Phase 2 Plan 2: Location-Specific Freshness Rules Summary

**Three genuinely different freshness rule-sets (Pantry: no early warning; Fridge: 3-day window; Freezer: purchase-date-driven quality band) computed server-side and rendered as location-worded badges, test-first.**

## Performance

- **Duration:** ~15 min active work (environment setup for a fresh worktree -- server/.venv and client/node_modules -- plus TDD RED/GREEN cycles for two tasks and one styling task)
- **Tasks:** 3/3 complete
- **Files modified/created:** 7 (2 new Python modules, 1 new React component, 4 modified)

## Accomplishments
- `server/freshness.py`: pure, standard-library-only module exporting the four freshness constants, `SEVERITY_RANK`, the three named thresholds, `computeBatchFreshness`, and `computeItemFreshness` -- Pantry has no early-warning window (D-09), Fridge warns within 3 days (D-10), Freezer is computed entirely from purchase date and never consults best-by (D-11)
- 26 boundary tests in `server/tests/test_freshness.py`, written first and confirmed failing (`ModuleNotFoundError`) before `freshness.py` existed, covering every exact boundary named in the plan (Pantry on best-by date, Fridge at exactly 3 days, Freezer at exactly 6 and exactly 12 months) plus item-level roll-up order-independence and invalid-input (`ValueError`) paths
- `server/hardwareDatabase.py`'s `getItemsByLocation` now computes `today` once per call from the server's own clock and annotates every batch and item with `freshness`, never writing it back to MongoDB
- 7 integration tests in `server/tests/test_inventory_freshness.py`, written first and confirmed failing (`KeyError: 'freshness'`), proving the annotation on the live Flask+mongomock read path, including a direct read of the raw `Items` collection confirming no `freshness` field is ever persisted
- `client/src/components/FreshnessBadge.js`: renders a label that depends on both `freshness` and `location` -- Freezer's expired band reads "Freezer burn risk" with no discard or safety instruction, per the user's explicit quality-vs-safety distinction in CONTEXT.md
- `client/src/components/Project.js` and `client/src/App.css` wire the badge into each item row with four data-driven, high-contrast badge styles, each pairing color with a text label
- Full backend suite (46 tests: 13 tracer + 26 freshness + 7 inventory-freshness) passes with no regression to plan 02-01's tracer tests; `npm --prefix client run build` succeeds

## Task Commits

Each task was committed atomically (TDD RED then GREEN):

1. **Task 1: Freshness rules, test-first** - `ebdd32a` (test, RED) then `7ab5917` (feat, GREEN)
2. **Task 2: Annotate the inventory read with freshness** - `ea7b325` (test, RED) then `d3abff7` (feat, GREEN)
3. **Task 3: Freshness badge in the inventory view** - `6c99636` (feat)

## Files Created/Modified
- `server/freshness.py` - `FRESH`/`EXPIRING_SOON`/`EXPIRED`/`UNKNOWN`, `SEVERITY_RANK`, `FRIDGE_EXPIRING_SOON_DAYS`/`FREEZER_EXPIRING_SOON_MONTHS`/`FREEZER_EXPIRED_MONTHS`, `computeBatchFreshness`, `computeItemFreshness`
- `server/tests/test_freshness.py` - 26 boundary tests pinned against a fixed `today` (2026-06-15), documented in the module docstring
- `server/hardwareDatabase.py` - `getItemsByLocation` computes `today` once, annotates every batch/item via a new `_annotateFreshness` helper
- `server/tests/test_inventory_freshness.py` - 7 tests against the `api`/`mongo` fixtures, including a raw-collection non-persistence check
- `client/src/components/FreshnessBadge.js` - `FreshnessBadge` component, location-worded labels and `title` tooltips
- `client/src/components/Project.js` - item row renders `FreshnessBadge` with the item's own `freshness` and section `location`
- `client/src/App.css` - four badge styles (`freshness-badge--fresh/expiring_soon/expired/unknown`)

## Decisions Made
- **Freezer month arithmetic:** defined as whole calendar months elapsed (documented in `freshness.py`'s docstring), so the two exact-boundary tests (6 months, 12 months) are provably consistent with the implementation rather than coincidentally passing.
- **Annotation scope:** `freshness` is added only inside `getItemsByLocation` (the GET read path). `addBatch`'s own returned item (used by the restock POST response) is untouched, keeping 02-01's restock response contract unchanged -- the plan's action text scoped this explicitly to `getItemsByLocation`.
- **Test date strategy:** `test_freshness.py` uses a pinned literal `today` (2026-06-15) with hand-computed ISO dates for every case (per the plan's own guidance to avoid `dateutil`); `test_inventory_freshness.py` uses relative offsets from the real `date.today()` since it only asserts freshness *categories*, not exact boundaries.

## Deviations from Plan

None - plan executed exactly as written. The only unplanned work was one-time environment setup (creating `server/.venv` and installing `client/node_modules`, both gitignored and absent in this fresh worktree) required before any verification command could run; this is infrastructure, not a code deviation, and nothing about it altered the plan's scope.

## Issues Encountered
- Task 3's `<verify>` includes a `<human-check>` requiring a running backend + frontend and manual browser interaction. Per `HUMAN_VERIFY_MODE=end-of-phase` (project config) and `auto_advance=false`, this was not run interactively during this plan's execution, consistent with plan 02-01's handling of its own deferred human-check. All automated checks in the same `<verify>` block (build success, wording greps, badge-wiring grep) passed. Logged in `.planning/WINDOWS.md` as an unrun-verify entry (id 3).

## Known Stubs

None introduced by this plan. (Plan 02-01's pre-existing `HOUSEHOLD_ID`/`USER_ID` hardcoding in `client/src/App.js` remains untouched and is already logged in `.planning/WINDOWS.md`.)

## Threat Flags

None beyond what the plan's own `<threat_model>` already covers (T-02-07, T-02-10, T-02-11) -- no new network endpoint, auth path, or trust-boundary-crossing surface was introduced. T-02-07's mitigation (server-only `today`, no request parameter) was directly verified: `grep -n "request\.\(args\|get_json\)" server/app.py` shows only `householdId`/`userId` (GET) and the restock body fields (POST).

## User Setup Required

None. This plan installs nothing new (no pip/npm packages); it extends `server/hardwareDatabase.py` and adds pure Python/React modules using only what plan 02-01 already installed. Note for any future executor picking up this repo in a fresh git worktree: `server/.venv/` and `client/node_modules/` are both gitignored and were absent here, so they were created/installed before tests or the build could run (`python3 -m venv server/.venv && server/.venv/bin/pip install -r server/requirements.txt`; `npm install --prefix client`).

## Next Phase Readiness
- `item.freshness` and `item.batches[].freshness` are now live on every `GET /api/inventory` response and are load-bearing for plan 02-03 (item identity matching, which merges batches across possibly-differently-worded names and must preserve per-batch freshness) and plan 02-04 (reserve/consume, which draws FIFO by best-by date -- freshness gives a human-readable signal for that same ordering).
- The deferred Task 3 browser human-check is logged in `.planning/WINDOWS.md` (id 3) for end-of-phase/ship-gate visibility, alongside plan 02-01's already-logged deferred checks.
- `server/freshness.py`'s constants (`FRESH`, `EXPIRING_SOON`, `EXPIRED`, `UNKNOWN`, `SEVERITY_RANK`) are the canonical vocabulary any future plan should reuse rather than redefine (e.g. plan 02-04's reserve/consume UI, if it wants to show freshness alongside quantity).

---
*Phase: 02-inventory-management*
*Completed: 2026-09-16*

## Self-Check: PASSED

All 7 claimed files verified present on disk, and all 5 claimed commit hashes (`ebdd32a`, `7ab5917`, `ea7b325`, `d3abff7`, `6c99636`) confirmed present in git log.
