---
phase: 02-inventory-management
verified: 2026-09-16T00:00:00Z
status: passed
score: 12/13 must-haves verified
behavior_unverified: 1
overrides_applied: 0
behavior_unverified_items:

  - truth: "Two consume requests arriving at once cannot drive an item below zero: each consume applies its recomputed batches through a single conditional update that matches only the exact capacity and reserved quantity it read, and a losing writer re-reads and re-checks the guard before retrying, exhausting to 409 rather than overwriting (edge: INV-04/concurrency)."
    test: "Run two consume requests against the same item concurrently (e.g. two threads or two overlapping HTTP requests against a real, multi-threaded/multi-process MongoDB, not mongomock) that together exceed capacity, and confirm exactly one succeeds and one gets 409 concurrent_modification, with capacity never going negative."
    expected: "Item capacity never drops below zero; the losing writer receives 409 rather than corrupting the stored batch list."
    why_human: "The plan itself authors this truth with `verification: backstop` because mongomock is single-threaded and cannot exercise a real race. The mitigation (find_one_and_update pinned on the exact capacity read, retried 3x) is present and correct by code inspection, and the WR-02 review fix specifically hardened this exact filter, but no executed concurrency test proves it under contention."
human_verification:

  - test: "Browser click-through: restock 'Oats' 4 units into Pantry via the running UI, confirm it appears with capacity 4/availability 4 without a page reload; restock 3 more and confirm ONE Oats row with capacity 7."
    expected: "Item appears live after submit with no reload; second restock merges into the same row."
    why_human: "Plan 02-01 Task 4's browser <human-check> was deferred to end-of-phase per HUMAN_VERIFY_MODE=end-of-phase. Logged as WINDOWS.md id 1 (open). A live HTTP smoke test against the real Flask dev server was run as partial substitute evidence, but no interactive browser session was recorded."
  - test: "Browser click-through: restock 4 items across Pantry/Fridge/Freezer with best-by/purchase dates chosen to land in each freshness band, and confirm badge wording — 'Fresh'/'Use soon'/'Past best-by' for Pantry/Fridge, 'Good quality'/'Quality declining'/'Freezer burn risk' for Freezer, 'No date' for a batch with no date."
    expected: "Each badge shows the correct location-specific wording with no safety/discard language for Freezer."
    why_human: "Plan 02-02 Task 3's browser <human-check> was deferred to end-of-phase. Logged as WINDOWS.md id 3 (open). Automated wording greps and the build pass, but no interactive browser render was confirmed."
  - test: "Browser click-through: merge 'Milk'/'milk' batches with distinct best-by dates and confirm consumption order on expand; loose-match 'Whole Milk' into 'Milk'; trigger an ambiguous restock ('Skim Milk' + 'Milk' both present, then restock 'Milk') and confirm the notice; confirm Fridge/Freezer location separation; confirm a batch with no best-by date renders a dash."
    expected: "All five scenarios render as specified, including the ambiguity notice text naming the colliding items."
    why_human: "Plan 02-03 Task 3's browser <human-check> was deferred to end-of-phase. Logged as WINDOWS.md id 4 (open). Automated build/grep/pytest checks pass, but no interactive browser session was recorded."
  - test: "Browser click-through: consume drains the soonest-expiring batch; an over-consume shows the on-hand count and keeps the typed quantity; reserving shows the claimant's name and drops availability; another member's consume still succeeds on a fully-reserved item; the release button is hidden for non-owners and works for the owner; two reservations by the same member are each independently releasable."
    expected: "All six scenarios behave exactly as specified, with reserved quantities worded as a claim, never as a lock."
    why_human: "Plan 02-04 Task 3's 6-step browser <human-check> was deferred to end-of-phase. Logged as WINDOWS.md id 5 (open). Automated build/grep/pytest checks pass, but no interactive browser session was recorded."
---

# Phase 2: Inventory Management Verification Report

**Phase Goal:** Within a household, a member can see what food is on hand across pantry/fridge/freezer and reserve, consume, or restock items without ever over-committing what's available.
**Verified:** 2026-09-16
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | A user can view all food items in a household's inventory grouped by location (Pantry/Fridge/Freezer), each showing capacity and availability | ✓ VERIFIED | `server/hardwareDatabase.py:getItemsByLocation` returns all 3 location keys always present, each item carrying `capacity`/`availability`; `client/src/components/Project.js` renders three `LocationSection`s in fixed order from live `fetchInventory()` data (`grep fetchInventory` in Project.js → present, no literal item objects). 114/114 backend tests pass including `test_empty_household_returns_all_three_location_keys_empty`. |
| 2 | A user can restock an item — quantity + purchase date + best-by date ("check-in") | ✓ VERIFIED | `POST /api/inventory/restock` registered in `server/app.py`; `hardwareDatabase.addBatch` validates and appends a batch, incrementing `capacity`; `RestockForm.js` submits all four fields. `test_restock_then_read_shows_item_under_pantry` and 8 sibling tests pass. |
| 3 | A user can reserve/claim a quantity for themselves without removing it from shared inventory ("request") | ✓ VERIFIED | `POST /api/inventory/reserve` → `hardwareDatabase.addReservation` appends via `$push`/`$inc reservedQuantity`, never touches `capacity`/`batches`; `test_reserve_more_than_capacity_succeeds_availability_floored_at_zero` confirms no capacity check on reserve (D-07). `ItemActions` in `Checkout.js` renders reserve control and reservation list. |
| 4 | A user can consume/remove a quantity ("checkout"), rejected if it would exceed what's available | ✓ VERIFIED | `POST /api/inventory/consume` → `hardwareDatabase.consumeFromItem` compares requested quantity against `capacity` (D-06), raises `InsufficientStockError` → 409 with `onHand`/`requested`, batches left byte-identical on rejection. `test_consume_capacity_plus_one_is_rejected_and_leaves_batches_unchanged` and `test_consume_exactly_capacity_succeeds_and_leaves_zero` pass. |
| 5 | Every item displays a freshness flag (fresh/expiring soon/expired) from its best-by date vs today | ✓ VERIFIED | `server/freshness.py` computes 3 distinct location rule-sets (Pantry no-warning, Fridge 3-day, Freezer purchase-date-driven); `getItemsByLocation` annotates every item/batch; `FreshnessBadge.js` renders location-worded labels. 33 freshness-specific tests pass including all 4 exact-boundary cases. |

**Score:** 5/5 roadmap success criteria verified by passing automated tests + direct code inspection.

### Plan-Level Must-Haves (selected, beyond roadmap SCs)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 6 | A request for inventory from a non-member is rejected 403, no data | ✓ VERIFIED | `assertHouseholdMember` raises `NotAHouseholdMemberError`; live exploit reproduction (below) confirms this holds even against a NoSQL-operator-injection attempt. |
| 7 | Item identity: normalization + substring/prefix matching, ambiguity creates a new item rather than guessing | ✓ VERIFIED | `itemIdentity.findMatchingItemKey` implements exact→loose→ambiguous→none resolution; 18 unit tests + 9 restock-integration tests pass, including two-household and cross-location isolation. |
| 8 | A rejected consume never partially applies | ✓ VERIFIED | `consumeFromItem` computes the full replacement batch list before any write and applies it via a single pinned `find_one_and_update`; `test_consume_capacity_plus_one_is_rejected_and_leaves_batches_unchanged` confirms byte-identical state after rejection. |
| 9 | A member cannot release another member's reservation | ✓ VERIFIED | `removeReservation` matches on `reservationId` AND `userId`; mismatch raises `ReservationNotOwnedError` → 403, entry survives. `test_different_member_cannot_release_reservation` passes. |
| 10 | The interface never describes a reserved quantity with locking/denial wording, and consume is never disabled by reservation presence | ✓ VERIFIED | `grep -ciE 'disabled=\{[^}]*reserv'` on `Checkout.js` = 0; wording is "Reserved by {name}: {quantity}"; consume `disabled` only bound to its own in-flight state. |
| 11 | No literal MongoDB connection string in tracked source; MONGODB_URI required | ✓ VERIFIED | `server/app.py:getMongoClient()` reads `MONGODB_URI`, raises `RuntimeError` if unset; `grep -c your_mongodb_connection_string_here server/app.py` = 0. |
| 12 | NoSQL-operator injection via unvalidated `householdId`/`userId`/`reservationId` (CR-01, code review) does not bypass household isolation | ✓ VERIFIED (independently reproduced) | See "Security Fix Verification" below — the review's exact exploit reproduction now returns 403 with the target household's stock untouched. |
| 13 | Two concurrent consumes cannot drive an item below zero | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Structural mitigation present and correct by code inspection (pinned `find_one_and_update` on `capacity`, retried 3x, WR-02-hardened) but the plan itself marks this `verification: backstop` — mongomock is single-threaded, so no executed race test exists. See Human Verification. |

**Score:** 12/13 must-haves verified; 1 present-but-behavior-unverified (backstop, routed to human verification).

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `server/itemIdentity.py` | `normalizeItemName`, `findMatchingItemKey`, `AmbiguousItemMatch` | ✓ VERIFIED | All exports present, imports nothing beyond `re`, no fuzzy-matching library. |
| `server/freshness.py` | Pure freshness rules, 4 constants + `SEVERITY_RANK` + 3 thresholds + 2 functions | ✓ VERIFIED | All exports present; no pymongo/flask import. |
| `server/hardwareDatabase.py` | Items collection CRUD, batch/reservation logic, exceptions | ✓ VERIFIED | All 14 required exports present; `find_one_and_update` used for both consume (3x) and release (pinned). |
| `server/projectsDatabase.py` | Household-scoped actions + membership guard | ✓ VERIFIED | All 8 required exports present; Track A's `queryProject`/`createProject`/`addUser`/`updateUsage` untouched (still stubs, correctly out of this phase's scope). |
| `server/app.py` | 5 REST routes | ✓ VERIFIED | `GET /api/inventory`, `POST /api/inventory/{restock,consume,reserve,release}` all registered; `/check_in`, `/check_out`, `/get_all_hw_names`, `/get_hw_info`, `/create_hardware_set` all removed. |
| `client/src/components/Project.js` (InventoryView) | Renders live inventory grouped by location | ✓ VERIFIED | Calls `fetchInventory`, no hardcoded item literals, renders `FreshnessBadge`/`BatchList`/`ItemActions`. |
| `client/src/components/RestockForm.js` | Restock form | ✓ VERIFIED | All 5 fields present, forwards response including `matchAmbiguity`. |
| `client/src/components/FreshnessBadge.js` | Location-worded freshness badge | ✓ VERIFIED | Distinct Freezer quality wording confirmed ("Freezer burn risk", no discard/safety language). |
| `client/src/components/BatchList.js` | Per-item batch detail, no re-sort | ✓ VERIFIED | `grep -c '.sort(' BatchList.js` = 0; dash rendered for missing best-by date. |
| `client/src/components/Checkout.js` (ItemActions) | Consume/reserve/release controls | ✓ VERIFIED | Consume never gated on reservation presence; release button only for own entries. |
| `client/src/api/inventory.js` | 5 API functions | ✓ VERIFIED | `fetchInventory`, `restockItem`, `consumeItem`, `reserveItem`, `releaseReservation` all exported. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `client/src/components/Project.js` | `client/src/api/inventory.js` | `fetchInventory()` in `useEffect` | ✓ WIRED | Confirmed by direct read + grep. |
| `client/src/api/inventory.js` | `server/app.py` | `fetch` of `/api/inventory*` | ✓ WIRED | All 5 endpoint paths match exactly. |
| `server/app.py` | `server/projectsDatabase.py` | `projectsDB.{restockItem,getHouseholdInventory,consumeItem,reserveItem,releaseReservation}` | ✓ WIRED | Confirmed by direct read of each route handler. |
| `server/projectsDatabase.py` | `server/hardwareDatabase.py` | `hardwareDB.{addBatch,getItemsByLocation,consumeFromItem,addReservation,removeReservation}` | ✓ WIRED | Confirmed by direct read. |
| `server/hardwareDatabase.py` | `server/freshness.py` | `computeBatchFreshness`/`computeItemFreshness` inside `getItemsByLocation` | ✓ WIRED | Confirmed by direct read; annotation never persisted (test confirms raw collection has no `freshness` field). |
| `server/hardwareDatabase.py` | `server/itemIdentity.py` | `findMatchingItemKey` in `addBatch`/`_resolveExistingItemKey` | ✓ WIRED | Confirmed by direct read. |
| `client/src/components/Project.js` | `client/src/components/{FreshnessBadge,BatchList,Checkout}.js` | Item row renders all three | ✓ WIRED | Confirmed by direct read of `Project.js`. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `InventoryView` (Project.js) | `inventory.locations` | `fetchInventory()` → `GET /api/inventory` → `getHouseholdInventory` → real mongomock/Mongo query | Yes | ✓ FLOWING |
| Item row `capacity`/`availability` | `item.capacity`, `item.availability` | Server-computed sum of batch quantities minus reserved, from the live document | Yes | ✓ FLOWING |
| `FreshnessBadge` | `item.freshness`, `batch.freshness` | Server-computed per-request from `freshness.py`, never a static default | Yes | ✓ FLOWING |

No hardcoded/static fallback data found in any inventory-rendering component (verified via grep for `itemName: '` and array literals — zero matches).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full backend test suite passes | `server/.venv/bin/python -m pytest server/tests -q` | `114 passed` | ✓ PASS |
| Production client build succeeds | `npm --prefix client run build` | `✓ built in 238ms`, emits `dist/index.html` | ✓ PASS |
| All required Python module exports present | inline `hasattr` check across `hardwareDatabase`, `projectsDatabase`, `itemIdentity`, `freshness` | `ALL EXPORTS PRESENT` | ✓ PASS |
| CR-01 exploit reproduction (NoSQL-operator injection) | Live Flask test-client POST with `{"householdId": {"$ne": "nope"}}` against a seeded cross-household item | `403 not_a_household_member`, target item's capacity unchanged (10) | ✓ PASS (exploit closed) |

### Security Fix Verification (CR-01, WR-01, WR-02, WR-03)

The 02-REVIEW.md flagged one Critical and three Warning findings; 02-REVIEW-FIX.md claims all four were fixed in commits `46db52e`/`5db239d`/`8e40df2`/`b506c21`. Independently verified against the current `main` HEAD (not just the fix report's narrative):

- **CR-01 (Critical, NoSQL-operator injection bypassing household isolation):** Reproduced the review's exact exploit live against the running Flask app (mongomock-backed) — a POST body with `householdId: {"$ne": "nope"}` previously drained another household's stock. Current code returns `403 {"error": "not_a_household_member"}` and leaves the target household's item capacity unchanged. `assertHouseholdMember` (projectsDatabase.py:88-89) and `removeReservation` (hardwareDatabase.py:428-429) both type-check their string inputs before any Mongo filter is built, exactly as the fix report claims. **Confirmed closed, not just claimed.**
- **WR-01 (double-decrement on racing release):** `removeReservation`'s final `find_one_and_update` is now pinned on `{"_id": doc["_id"], "reservations.reservationId": reservationId}` (hardwareDatabase.py:464), not just `_id`. **Confirmed present.**
- **WR-02 (spurious 409s from over-pinned concurrency filter):** `consumeFromItem`'s conditional write filter now only pins `capacity` (hardwareDatabase.py:344-346), `reservedQuantity` removed. **Confirmed present.**
- **WR-03 (racy upsert for brand-new item names):** Unique compound index `(householdId, location, itemKey)` created via `_ensureItemUniqueIndex` (hardwareDatabase.py:123-138), called at the top of `addBatch`, with a `DuplicateKeyError`-triggered retry (hardwareDatabase.py:226-238). **Confirmed present.**

10 new regression tests in `server/tests/test_type_validation.py` (dict/list-typed identifiers rejected) all pass, part of the 114-test suite total.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| INV-01 | 02-01, 02-03 | View inventory by location with capacity/availability | ✓ SATISFIED | See truths 1, 7 above. |
| INV-02 | 02-01, 02-03 | Restock with quantity/purchase date/best-by date | ✓ SATISFIED | See truth 2 above. |
| INV-03 | 02-04 | Reserve/claim without removing from inventory | ✓ SATISFIED | See truth 3 above. |
| INV-04 | 02-04 | Consume, rejected if exceeding availability | ✓ SATISFIED | See truth 4 above; concurrency sub-case is behavior-unverified (item 13). |
| INV-05 | 02-02 | Freshness flag from best-by date vs today | ✓ SATISFIED | See truth 5 above. |

All 5 requirement IDs declared across the phase's 4 plans (`requirements:` frontmatter) are accounted for and match REQUIREMENTS.md's INV-01..05 definitions. No orphaned requirements found for this phase.

**Note (documentation hygiene, non-blocking):** REQUIREMENTS.md's v1-requirements checklist still shows `[ ]` (unchecked) for INV-01, INV-02, and INV-05 despite this phase satisfying them (only INV-03/INV-04 show `[x]`), and the Traceability table's Status column still reads "Pending" for INV-01, INV-02, INV-05 vs. "Complete" for INV-03, INV-04. This is a stale-documentation gap, not a functional one — every plan's own frontmatter records `requirements-completed` correctly, and the underlying code/tests satisfy all 5. Flagged as an info-level item for the orchestrator's REQUIREMENTS.md update pass, not a phase-goal blocker.

### Anti-Patterns Found

None blocking. `grep` for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` (case-insensitive) across all phase-modified `server/*.py` and `client/src/**/*.js` files found one match: `client/src/App.js:6` uses the word "placeholder" in a comment describing the intentionally-deferred `HOUSEHOLD_ID`/`USER_ID`/`USER_NAME` constants awaiting Track A's session layer (ACCT-04). This is documented, tracked as an open stub in `.planning/WINDOWS.md` (id 2), and explicitly out of this phase's scope per the plans' own cross-track coordination notes — not an unresolved debt marker.

No empty implementations, no hardcoded inventory data rendered to the UI, no `dangerouslySetInnerHTML`, no secrets in tracked source.

### Human Verification Required

5 items need human testing (4 deferred end-of-phase browser click-throughs, already logged as open items in `.planning/WINDOWS.md`, plus 1 present-but-behavior-unverified concurrency truth):

1. **Restock tracer browser click-through** — restock "Oats" via the live UI twice and confirm live capacity/availability update with no reload. (WINDOWS.md id 1)
2. **Freshness badge wording browser click-through** — confirm all badge labels render correctly for each location/freshness combination. (WINDOWS.md id 3)
3. **Batch matching and detail browser click-through** — confirm merge, loose-match, ambiguity notice, and location separation all render correctly. (WINDOWS.md id 4)
4. **Consume/reserve/release browser click-through** — confirm the full 6-step reserve-is-not-a-lock scenario. (WINDOWS.md id 5)
5. **Concurrent-consume race** — run two genuinely concurrent consume requests against a real multi-threaded MongoDB (not mongomock) and confirm capacity never goes negative. No executed test exists for this; the plan itself marks it `verification: backstop`.

### Gaps Summary

No blocking gaps. All 5 roadmap success criteria and all but one plan-level must-have are verified by passing automated tests, direct code inspection, and (for the Critical security finding) an independently-reproduced exploit confirmation. The phase's own code-review cycle (02-REVIEW.md → 02-REVIEW-FIX.md) is not merely claimed complete — the CR-01 exploit was re-run against current `main` and confirmed closed, and all three Warning-severity concurrency fixes were located and read in the current source.

The only items preventing a clean `passed` status are: (a) 4 human-check browser click-throughs that were legitimately deferred to end-of-phase per the project's `HUMAN_VERIFY_MODE=end-of-phase` configuration and are already tracked as open items in the Broken Windows Ledger, and (b) one concurrency truth the plan itself authored as `verification: backstop` because the test harness (mongomock) cannot exercise a real race — the structural mitigation is present and correct by inspection, but unproven by an executed test. Neither represents a discovered functional defect; both are pre-declared, tracked deferrals surfaced here per the verification protocol.

---

*Verified: 2026-09-16*
*Verifier: Claude (gsd-verifier)*
