---
phase: 02-inventory-management
plan: 03
subsystem: api
tags: [flask, pymongo, react, item-identity, matching]

# Dependency graph
requires:
  - phase: 02-inventory-management (plan 01)
    provides: "Items collection document shape, GET /api/inventory + POST /api/inventory/restock REST contract, itemIdentity.normalizeItemName (D-03 normalization half)"
  - phase: 02-inventory-management (plan 02)
    provides: "item.freshness and item.batches[].freshness computed on every GET /api/inventory response"
provides:
  - "itemIdentity.findMatchingItemKey + AmbiguousItemMatch: the full D-03 resolution order (exact, loose substring/prefix single-candidate, ambiguous-raises, none)"
  - "hardwareDatabase.addBatch resolves its target item through the matcher, scoped to exactly one householdId + one location"
  - "item.matchAmbiguity response field -- transient, present only on a restock response where an ambiguous match forced a new item"
  - "BatchList React component: per-item batch detail (quantity/purchaseDate/bestByDate/freshness) rendered in server-supplied consumption order"
affects: [02-04-reserve-consume]

# Actuals (#2632)
actuals:
  tokens: 6881
  tasks: 3
  commits: 5

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "findMatchingItemKey is a pure function over (normalizedName, existingKeys) -- no DB access, no I/O -- making its resolution order exhaustively unit-testable independent of the Mongo-backed caller"
    - "Ambiguity is a deterministic no-guess OUTCOME (create a new item + report candidates), not an error path -- callers must catch AmbiguousItemMatch and treat it as a successful create, never let it propagate as a 500"
    - "Transient, non-persisted response metadata (matchAmbiguity) is attached to the already-serialized item dict just before return, the same pattern plan 02-02 established for freshness -- never written back to Mongo"

key-files:
  created:
    - server/tests/test_item_identity.py
    - server/tests/test_restock_matching.py
    - client/src/components/BatchList.js
  modified:
    - server/itemIdentity.py
    - server/hardwareDatabase.py
    - client/src/components/Project.js
    - client/src/components/RestockForm.js
    - client/src/App.css

key-decisions:
  - "matchAmbiguity carries the sorted colliding itemKeys (not raw display names) -- itemKeys are already the normalized, lowercase, human-legible form (e.g. 'whole milk'), so no separate lookup was needed to report what the restock could have merged into."
  - "The ambiguity notice in the UI is single-slot state (one notice at a time, cleared/replaced on the next restock) scoped by location+itemKey -- matches the plan's 'a short line near the newly created item' framing rather than an accumulating notification list."
  - "RestockForm.js needed a small change (not in the plan's files_modified list) to forward the restock response's item -- including matchAmbiguity -- up to InventoryView instead of discarding it; without this, Task 3's UI-surfacing requirement (matchAmbiguity reaching the client) would have been unimplementable. See Deviations."

patterns-established:
  - "A location-scoped, household-scoped Mongo find() feeding a pure matching function is the template for any future item-identity lookup (e.g. plan 02-04's reserve/consume, which resolves its target item the same way per this plan's Next Phase Readiness note)."

requirements-completed: [INV-01, INV-02]

coverage:
  - id: D1
    description: "A case/whitespace-only variant of an existing item's name merges into that item in the same location rather than creating a duplicate (D-03)"
    requirement: "INV-02"
    verification:
      - kind: unit
        ref: "server/tests/test_restock_matching.py#test_case_and_whitespace_variant_merges_into_one_item"
        status: pass
    human_judgment: false
  - id: D2
    description: "A loosely-matching name (substring/prefix, exactly one candidate) merges into the existing item and the item's displayed name stays the first-used spelling (D-03)"
    requirement: "INV-02"
    verification:
      - kind: unit
        ref: "server/tests/test_restock_matching.py#test_loose_match_merges_and_keeps_original_display_name"
        status: pass
    human_judgment: false
  - id: D3
    description: "Matching never crosses locations or households -- the same name in two locations, or two households restocking the same name, stay fully separate items"
    verification:
      - kind: unit
        ref: "server/tests/test_restock_matching.py#test_same_name_different_location_never_merges, #test_two_households_restocking_same_name_stay_separate"
        status: pass
    human_judgment: false
  - id: D4
    description: "A name that loosely matches two or more existing items creates a new item (deterministic no-guess outcome) and the restock response reports the colliding candidates; both existing items keep their original quantities"
    requirement: "INV-02"
    verification:
      - kind: unit
        ref: "server/tests/test_restock_matching.py#test_ambiguous_restock_creates_a_third_item_and_reports_candidates"
        status: pass
    human_judgment: false
  - id: D5
    description: "Matching is substring/prefix only -- no edit-distance ('mlk' vs 'milk'), no synonyms ('dairy' vs 'milk'); exact match relies on caller-side normalization"
    verification:
      - kind: unit
        ref: "server/tests/test_item_identity.py#test_edit_distance_does_not_match, #test_synonyms_do_not_match, #test_milks_does_match_because_milk_is_a_substring_of_milks"
        status: pass
      - kind: other
        ref: "grep -cE '^(import|from) *(difflib|rapidfuzz|fuzzywuzzy|Levenshtein)' server/itemIdentity.py (0)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The matcher's result is deterministic regardless of the order existingKeys are supplied in, for both a resolved match and an ambiguity's candidate list"
    verification:
      - kind: unit
        ref: "server/tests/test_item_identity.py#test_result_does_not_depend_on_existing_keys_order, #test_ambiguity_candidates_do_not_depend_on_existing_keys_order"
        status: pass
    human_judgment: false
  - id: D7
    description: "Restocking a blank/whitespace-only name, or matching against a location with no items, is handled correctly -- 400 for blank, silent new-item creation for empty-location (neither guesses nor errors wrongly)"
    requirement: "INV-02"
    verification:
      - kind: unit
        ref: "server/tests/test_restock_matching.py#test_restock_with_only_spaces_name_returns_400_and_writes_nothing, #test_restock_into_empty_location_creates_new_item_without_error"
        status: pass
    human_judgment: false
  - id: D8
    description: "Batches inside a merged item are returned in consumption order (soonest best-by first for Fridge, oldest purchase date first for Freezer) even when the batches came from differently-worded restocks"
    requirement: "INV-01"
    verification:
      - kind: unit
        ref: "server/tests/test_restock_matching.py#test_merged_batches_returned_in_fridge_consumption_order, #test_merged_batches_returned_in_freezer_consumption_order"
        status: pass
    human_judgment: false
  - id: D9
    description: "A household member can expand any item and see each batch's own quantity, purchase date, best-by date, and freshness, in the order the server returned them (no client-side re-sort); a batch with no best-by date renders an explicit dash"
    requirement: "INV-01"
    verification:
      - kind: other
        ref: "grep -c 'BatchList' client/src/components/Project.js (2), grep -c '.sort(' client/src/components/BatchList.js (0), npm --prefix client run build (exit 0)"
        status: pass
    human_judgment: true
    rationale: "Task 3's <human-check> requires a running backend + frontend and manual browser interaction across 5 scenarios (merge with dates, loose match, ambiguity notice, location separation, no-best-by dash). Per HUMAN_VERIFY_MODE=end-of-phase and auto_advance=false, this was not run interactively during plan execution, consistent with plans 02-01 and 02-02's handling of their own deferred human-checks. Deferred to end-of-phase and logged in .planning/WINDOWS.md (id 4)."

duration: ~20min active tool-call work (includes one-time worktree environment setup -- server/.venv and client/node_modules did not exist in this fresh worktree)
completed: 2026-09-16
status: complete
---

# Phase 2 Plan 3: Item Identity Matching and Batch Detail Summary

**D-03's full item-matcher (exact, loose substring/prefix, deterministic ambiguity) wired into restock, plus a per-item batch history view built test-first.**

## Performance

- **Duration:** ~20 min active work (one-time worktree environment setup -- `server/.venv` and `client/node_modules` were absent in this fresh worktree and had to be created/installed first -- plus TDD RED/GREEN cycles for two tasks and one presentation task)
- **Tasks:** 3/3 complete
- **Files modified/created:** 8 (3 new, 5 modified)

## Accomplishments
- `server/itemIdentity.py`: `findMatchingItemKey(normalizedName, existingKeys)` implements the full D-03 resolution order (exact wins outright; a single loose substring/prefix candidate wins; two or more candidates raise `AmbiguousItemMatch` rather than guessing; no candidates returns `None`), plus `AmbiguousItemMatch` carrying its candidates pre-sorted
- 18 tests in `server/tests/test_item_identity.py`, written first and confirmed failing (`ImportError`) before the matcher existed, covering every case in the plan's behavior block including the explicit out-of-scope cases (no edit distance, no synonyms) and two order-independence tests
- `server/hardwareDatabase.py`'s `addBatch` now resolves its target item through the matcher, scoped to exactly one `householdId` + one `location` (never wider), instead of assuming the normalized name is the itemKey; a matched item's stored `itemName` is left untouched so the household keeps its first-chosen display name
- An ambiguous match creates a new item -- the deterministic no-guess outcome, not an error -- and attaches the sorted colliding candidate keys under `matchAmbiguity` on the returned item dict, propagating unchanged through `projectsDatabase.restockItem` and the `/api/inventory/restock` response
- 9 integration tests in `server/tests/test_restock_matching.py`, written first and confirmed failing (loose-match and ambiguity cases) before `addBatch` was wired in, covering merge-by-normalization, loose-match-with-display-name-preserved, location isolation, household isolation, ambiguity, empty-location restock, blank-name rejection, and consumption order across merged batches for both Fridge and Freezer
- `client/src/components/BatchList.js`: renders one row per batch (quantity, purchase date, best-by date -- an explicit dash when absent -- and a per-batch `FreshnessBadge`) strictly in received order, with no sort call, since the server already computes consumption order
- `client/src/components/Project.js`: each item row now expands via a native `<details>`/`<summary>` disclosure (keyboard accessible, no extra state) showing `BatchList` in the body; when a restock response carries `matchAmbiguity`, a short notice appears under the newly created item naming what it could have merged into
- Full backend suite (73 tests: 46 baseline + 18 item-identity + 9 restock-matching) passes with no regressions to plans 02-01 or 02-02; `npm --prefix client run build` succeeds

## Task Commits

Each task was committed atomically (TDD RED then GREEN):

1. **Task 1: Item matching rules, test-first** - `128f774` (test, RED) then `e94b73b` (feat, GREEN)
2. **Task 2: Restock resolves its target item through the matcher** - `578a590` (test, RED) then `0ed01de` (feat, GREEN)
3. **Task 3: Batch detail in the inventory view** - `582003a` (feat)

## Files Created/Modified
- `server/itemIdentity.py` - adds `AmbiguousItemMatch` (with sorted `candidates`), `findMatchingItemKey(normalizedName, existingKeys)`
- `server/tests/test_item_identity.py` - 18 tests: exact/loose/ambiguous/none, out-of-scope cases, order independence
- `server/hardwareDatabase.py` - `addBatch` resolves its target itemKey through `findMatchingItemKey`, scoped to `householdId`+`location`; attaches `matchAmbiguity` on collision
- `server/tests/test_restock_matching.py` - 9 tests against the `api`/`mongo` fixtures
- `client/src/components/BatchList.js` - `BatchList` component: quantity/purchaseDate/bestByDate/freshness per batch, received order only
- `client/src/components/Project.js` - item rows expand via `<details>`/`<summary>` to render `BatchList`; surfaces `matchAmbiguity` as a notice
- `client/src/components/RestockForm.js` - forwards the restock response's `item` (including `matchAmbiguity`) to `onRestocked` instead of discarding it
- `client/src/App.css` - batch row, disclosure, and ambiguity-notice styles

## Decisions Made
- **Ambiguity candidate representation:** `matchAmbiguity` carries sorted itemKeys (already normalized, lowercase, human-legible) rather than a separate display-name lookup -- simpler and sufficient for the UI notice.
- **UI ambiguity-notice scope:** single most-recent notice, keyed by `location`+`itemKey`, cleared on the next restock -- matches the plan's "a short line near the newly created item," not a persistent notification list.
- **Display-name provenance (reaffirmed from 02-01):** a matched item's `itemName` is never overwritten by a later loosely-matched restock, per D-03's "the display name stays the name first used for it" must-have.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Modified `client/src/components/RestockForm.js` to forward the restock response**
- **Found during:** Task 3, implementing the `matchAmbiguity` UI-surfacing requirement
- **Issue:** `RestockForm.js` is not in the plan's `files_modified` list, but the plan's Task 3 action explicitly requires: "When the restock response carried `matchAmbiguity`, show a short line near the newly created item." `RestockForm` was the only place holding the raw restock POST response; it discarded the response body entirely and called `onRestocked()` with no arguments. Without forwarding the response, `InventoryView` (`Project.js`) would have had no way to learn a restock was ambiguous, and this named requirement of Task 3 would be unimplementable.
- **Fix:** Changed `RestockForm.handleSubmit` to capture `restockItem(...)`'s return value and call `onRestocked(response.item)` instead of `onRestocked()`. `InventoryView`'s `handleRestocked` (new) reads `restockedItem.matchAmbiguity` to set the notice, then reloads inventory as before.
- **Files modified:** `client/src/components/RestockForm.js`, `client/src/components/Project.js`
- **Verification:** `npm --prefix client run build` succeeds; `grep -c BatchList client/src/components/Project.js` and `grep -c matchAmbiguity client/src/components/Project.js` both non-zero.
- **Committed in:** `582003a` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary to complete Task 3's own stated requirement (surfacing `matchAmbiguity` to the household). No scope creep -- the change is a one-line forward of data the response already carried, not new business logic.

## Issues Encountered
- Task 3's `<verify>` includes a `<human-check>` requiring a running backend + frontend and manual browser interaction across 5 scenarios. Per `HUMAN_VERIFY_MODE=end-of-phase` (project config) and `auto_advance=false`, this was not run interactively during this plan's execution, consistent with plans 02-01 and 02-02's handling of their own deferred human-checks. All automated checks in the same `<verify>` block (build success, no-sort grep, BatchList-wired grep) passed. Logged in `.planning/WINDOWS.md` as an unrun-verify entry (id 4).
- This repo's worktree gotcha (noted by 02-02's run) recurred: `server/.venv` and `client/node_modules` are gitignored and did not exist in this fresh worktree. Recreated with `python3 -m venv server/.venv && server/.venv/bin/pip install -r server/requirements.txt` and `npm install --prefix client` before any test or build could run. Infrastructure only -- no code deviation.

## Known Stubs

None introduced by this plan. (Plan 02-01's pre-existing `HOUSEHOLD_ID`/`USER_ID` hardcoding in `client/src/App.js` remains untouched and is already logged in `.planning/WINDOWS.md`, id 2.)

## Threat Flags

None beyond what the plan's own `<threat_model>` already covers (T-02-02, T-02-12, T-02-13). No new network endpoint, auth path, or trust-boundary-crossing surface was introduced. T-02-02 and T-02-12's mitigations were directly verified: the candidate-key query inside `addBatch` filters on `householdId` + `location` only, both validated first, and `itemName` is coerced through `normalizeItemName` before any comparison -- confirmed by `test_two_households_restocking_same_name_stay_separate` and `test_same_name_different_location_never_merges`.

## User Setup Required

None. This plan installs nothing new. Note for any future executor picking up this repo in a fresh git worktree: `server/.venv/` and `client/node_modules/` are both gitignored and must be recreated (`python3 -m venv server/.venv && server/.venv/bin/pip install -r server/requirements.txt`; `npm install --prefix client`) before tests or the build can run -- now the third plan in a row to hit this, worth noting for Track C/D's environment setup.

## Next Phase Readiness
- `itemIdentity.findMatchingItemKey` and `AmbiguousItemMatch` are the canonical, load-bearing item-resolution primitives for plan 02-04's reserve and consume actions, which per this plan's own `<output>` instruction should resolve their target item through this same matcher rather than reinventing lookup logic.
- The `matchAmbiguity` response-field pattern (transient, attached only to the triggering response, never persisted) is a template for any future non-persisted response metadata.
- The deferred Task 3 browser human-check is logged in `.planning/WINDOWS.md` (id 4) for end-of-phase/ship-gate visibility, alongside plans 02-01 and 02-02's already-logged deferred checks.
- The recurring fresh-worktree environment-setup gotcha (`server/.venv`, `client/node_modules` gitignored) should be called out explicitly to Track C (deployment/CI) and Track D (testing infrastructure), since three plans in a row in this phase have had to redo the same one-time setup.

---
*Phase: 02-inventory-management*
*Completed: 2026-09-16*

## Self-Check: PASSED

All 8 claimed source files plus `.planning/WINDOWS.md` verified present on disk, and all 5 claimed commit hashes (`128f774`, `e94b73b`, `578a590`, `0ed01de`, `582003a`) confirmed present in `git log`.
