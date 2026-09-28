---
phase: 02-inventory-management
reviewed: 2026-09-16T00:00:00Z
depth: standard
files_reviewed: 28
files_reviewed_list:
  - server/itemIdentity.py
  - server/requirements.txt
  - server/tests/conftest.py
  - server/tests/test_inventory_tracer.py
  - client/package.json
  - client/vite.config.js
  - client/index.html
  - client/src/api/inventory.js
  - client/src/components/RestockForm.js
  - .gitignore
  - server/freshness.py
  - server/tests/test_freshness.py
  - server/tests/test_inventory_freshness.py
  - client/src/components/FreshnessBadge.js
  - server/tests/test_item_identity.py
  - server/tests/test_restock_matching.py
  - client/src/components/BatchList.js
  - server/tests/test_consume.py
  - server/tests/test_reserve.py
  - server/hardwareDatabase.py
  - server/projectsDatabase.py
  - server/app.py
  - server/usersDatabase.py
  - client/src/index.js
  - client/src/index.css
  - client/src/App.js
  - client/src/App.css
  - client/src/components/Project.js
  - client/src/components/Checkout.js
findings:
  critical: 1
  warning: 3
  info: 2
  total: 6
status: fixed
fix_report: 02-REVIEW-FIX.md
---

# Phase 02: Code Review Report

**Reviewed:** 2026-09-16T00:00:00Z
**Depth:** standard
**Files Reviewed:** 28
**Status:** issues_found

## Summary

Track B's inventory management feature is built on a coherent design (separate `Items` collection keyed by household + location + itemKey, batch-level FIFO consumption, location-specific freshness rules, unenforced "dibs" reservations) and the four plans' threat models correctly identify and test the household-membership boundary using string-typed request parameters. Most of the claimed mitigations hold up under direct code inspection: `itemName` is safely coerced through `normalizeItemName` before ever reaching a Mongo filter, `location` is checked against a fixed tuple, `quantity` is validated as a real (non-bool) `int`, and the FIFO drain / overbooking-guard logic in `consumeFromItem` matches D-02/D-06/D-07 exactly, including the batches-left-untouched-on-rejection property the tests assert.

However, one boundary the threat model treats as closed is not actually closed: **`householdId` (and the other identifier fields carried in JSON request bodies — `userId`, `userName`, `reservationId`) are never type-checked before being embedded directly into MongoDB filter/update documents.** Because Flask's `request.get_json()` parses arbitrary JSON structures (not just strings), a POST body can supply a MongoDB query operator object (e.g. `{"$ne": "..."}"`) in place of a plain string `householdId`. This defeats `assertHouseholdMember` and every downstream `collection.find`/`find_one_and_update` filter that trusts `householdId` to be an opaque string, breaking the household-isolation guarantee that T-02-01, T-02-11, and T-02-12 all claim to provide. I reproduced this live against the real Flask route (not just the internal function) and drained another household's stock through `/api/inventory/consume` as a user with no relationship to that household — see CR-01 below for the reproduction and fix.

Three further concurrency/robustness gaps exist in `hardwareDatabase.py` around reservation release and the consume optimistic-concurrency guard, plus two minor dead-code items. None of the frontend components introduce XSS (React's default escaping is relied on correctly, no `dangerouslySetInnerHTML`), and no hardcoded secrets or debug artifacts were found in any reviewed file.

## Critical Issues

### CR-01: Unvalidated `householdId`/`userId`/`reservationId` types allow NoSQL-operator injection that bypasses household isolation

**File:** `server/projectsDatabase.py:76-99` (`assertHouseholdMember`, and every function that calls it: `restockItem`, `getHouseholdInventory`, `consumeItem`, `reserveItem`, `releaseReservation`), `server/hardwareDatabase.py:167-172, 230-235, 354-361, 381-383` (raw Mongo filters built from these values), `server/app.py:166-316` (`restock_inventory`, `consume_inventory`, `reserve_inventory`, `release_inventory` — all read these fields via `body.get(...)` with no type check)

**Issue:** Every mutating inventory route pulls `householdId` (and `userId`, `userName`, `reservationId`) straight out of `request.get_json()` and passes it, unvalidated, into MongoDB filter documents:

```python
# projectsDatabase.py
def assertHouseholdMember(client, householdId, userId):
    household = db[hardwareDB.HOUSEHOLDS_COLLECTION].find_one({"householdId": householdId})
    if household is None or userId not in household.get("users", []):
        raise NotAHouseholdMemberError(userId)
```

`request.get_json()` decodes arbitrary JSON, so `householdId` is not guaranteed to be a string — a client can send `{"householdId": {"$ne": "bogus"}, ...}`. Mongo then interprets the value as a query operator instead of an equality match, so `find_one({"householdId": {"$ne": "bogus"}})` returns an *arbitrary other household's* document, and the same injected value flows on into `hardwareDB.addBatch` / `consumeFromItem` / `addReservation` / `removeReservation`'s own filters (`server/hardwareDatabase.py:167-172`, `230-235`, `354-361`), which then match/mutate items across households instead of scoping to one.

I reproduced this against the real Flask app (mongomock-backed test client, same fixtures the test suite uses):

```python
# Household H2 ("carol") owns a Pantry item "SecretStash" with 10 units.
# Attacker is "alice", a member of H1 only, with no relationship to H2.
resp = api.post('/api/inventory/consume', json={
    'householdId': {'$ne': 'nope'},
    'userId': 'alice',
    'location': 'Pantry',
    'itemName': 'SecretStash',
    'quantity': 10,
})
# -> 200 {'item': {'availability': 0, 'batches': [], 'capacity': 0,
#          'householdId': 'H2', 'itemKey': 'secretstash', ...}}
# H2's SecretStash item is now fully drained by a user who is not a
# member of H2 and never should have been able to see or touch it.
```

This is a full authorization-bypass / cross-tenant data-corruption vulnerability reachable on every POST inventory route (`restock`, `consume`, `reserve`, `release`), directly contradicting T-02-01 ("a userId absent from the household's `users` array raises `NotAHouseholdMemberError`") and T-02-12 ("scoped to one householdId and one location ... neither household's restock merges into or reveals the other's items") — those mitigations assume `householdId` is already a trustworthy string, which nothing in the code enforces. The GET route (`/api/inventory`) is not exploitable this way because Flask's query-string parsing (`request.args.get`) can only ever produce a plain string, but all four POST routes are.

**Fix:** Validate that every identifier pulled from a JSON body is a plain `str` before it reaches any Mongo filter — cheapest is a single guard at the top of `assertHouseholdMember` (closes the shared boundary for every caller) plus explicit checks on `reservationId`/`userName` where they're used directly:

```python
# projectsDatabase.py
def assertHouseholdMember(client, householdId, userId):
    if not isinstance(householdId, str) or not isinstance(userId, str):
        raise NotAHouseholdMemberError(userId)
    db = client[hardwareDB.DB_NAME]
    household = db[hardwareDB.HOUSEHOLDS_COLLECTION].find_one({"householdId": householdId})
    if household is None or userId not in household.get("users", []):
        raise NotAHouseholdMemberError(userId)
```

```python
# hardwareDatabase.py — removeReservation, before the first find_one
if not isinstance(reservationId, str):
    raise ReservationNotFoundError(reservationId)
```

Add a regression test that POSTs a dict/list in place of `householdId` (and `reservationId`) to each of the four mutating routes and asserts 403/404/400 with no write, mirroring the existing membership-guard tests in `test_consume.py`/`test_reserve.py`.

## Warnings

### WR-01: `removeReservation` can double-decrement `reservedQuantity` under a duplicate/concurrent release

**File:** `server/hardwareDatabase.py:369-414`
**Issue:** The final write is filtered only on `_id`, not on the reservation still being present:

```python
updated = collection.find_one_and_update(
    {"_id": doc["_id"]},
    {
        "$pull": {"reservations": {"reservationId": reservationId}},
        "$inc": {"reservedQuantity": -entry.get("quantity", 0)},
    },
    return_document=ReturnDocument.AFTER,
)
```

If two `release` requests for the same `reservationId` race (e.g. a second browser tab, or a client-side retry after a dropped response), both can pass the earlier ownership check (each reads the entry via its own `find_one` before either writes), and both then execute this `find_one_and_update`. The `$pull` is idempotent (a second pull matching nothing is a no-op on the array), but the `$inc` is **not** conditioned on the pull actually having removed anything — it always fires, so `reservedQuantity` is decremented twice for one logical release, and can go negative. `availability` is floored at 0 so it won't visibly break, but `reservedQuantity` itself (rendered directly in `client/src/components/Checkout.js:92,168` as "`{reservedTotal} reserved`") can show a negative or otherwise wrong number, and the corruption persists in the stored document.

**Fix:** Pin the update on the reservation still being present, so a losing duplicate call fails to match and can be treated as an idempotent no-op instead of an unconditional decrement:

```python
updated = collection.find_one_and_update(
    {"_id": doc["_id"], "reservations.reservationId": reservationId},
    {
        "$pull": {"reservations": {"reservationId": reservationId}},
        "$inc": {"reservedQuantity": -entry.get("quantity", 0)},
    },
    return_document=ReturnDocument.AFTER,
)
if updated is None:
    raise ReservationNotFoundError(reservationId)
```

### WR-02: `consumeFromItem`'s optimistic-concurrency filter over-pins on `reservedQuantity`, causing spurious 409s

**File:** `server/hardwareDatabase.py:305-315`
**Issue:** The conditional write that implements the consume race-guard pins on both fields read at the top of the loop:

```python
updated = collection.find_one_and_update(
    {
        "_id": doc["_id"],
        "capacity": capacity,
        "reservedQuantity": reservedQuantity,
    },
    {"$set": {"batches": newBatches, "capacity": capacity - quantity}},
    return_document=ReturnDocument.AFTER,
)
```

Per D-06/D-07 (also documented in this function's own docstring), consume never reads or writes `reservedQuantity` — the overbooking guard and the write both operate on `capacity`/`batches` alone. Pinning the conditional update on the exact `reservedQuantity` value read means any concurrent, unrelated reserve or release on the *same item* (a very plausible household scenario: one member reserving while another consumes) will cause this consume's conditional update to spuriously fail and retry, even though nothing about the consume's own precondition (`capacity`) actually changed. Under realistic concurrent household use this can exhaust `_MAX_CONCURRENCY_ATTEMPTS` (3) and surface `ConcurrentModificationError` (409) for a consume that had no real conflict — the exact scenario T-02-09's mitigation claims to prevent, undermined by an unrelated field.

**Fix:** Drop `reservedQuantity` from the pinned filter — only `capacity` (the field the guard and the write both depend on) needs to match:

```python
updated = collection.find_one_and_update(
    {"_id": doc["_id"], "capacity": capacity},
    {"$set": {"batches": newBatches, "capacity": capacity - quantity}},
    return_document=ReturnDocument.AFTER,
)
```

### WR-03: `addBatch`'s upsert for a brand-new item name is racy without a unique index

**File:** `server/hardwareDatabase.py:191-207`
**Issue:** When two concurrent restocks both resolve to `matchedKey = None` for the same never-before-seen item name (e.g. two members restocking "Rice" in Pantry for the first time at the same moment), both calls target the identical upsert filter `{"householdId": householdId, "location": location, "itemKey": targetKey}` with `upsert=True`. MongoDB does not serialize two concurrent upserts against a filter that isn't backed by a unique index — this is a documented MongoDB race (two upserts can both observe "no matching document" and both insert), which would silently create two separate `Items` documents with the same `itemKey`, splitting that item's batch history across two records that `getItemsByLocation` would then render as two separate rows for what the household believes is one item.

**Fix:** Add a unique compound index on `Items` for `(householdId, location, itemKey)` at startup/migration time, and catch the resulting `DuplicateKeyError` in `addBatch` to retry the read-merge-write instead of assuming the upsert is race-free.

## Info

### IN-01: Dead exception handling in `GET /api/inventory`

**File:** `server/app.py:152-157`
**Issue:** The route catches `hardwareDB.ItemNotFoundError` and `hardwareDB.InvalidInventoryInput` around `projectsDB.getHouseholdInventory`, but that call chain (`assertHouseholdMember` + `hardwareDB.getItemsByLocation`) never raises either exception — `getItemsByLocation` takes no user-suppliable `location`/`itemName`/`quantity` to validate. This is harmless today but misleads a future reader into believing GET can 404/400.
**Fix:** Remove the two dead `except` clauses, or add a comment noting they're defensive/forward-looking if that's intentional.

### IN-02: Unused imports left over from the scaffold rewrite

**File:** `server/app.py:4` (`from bson.objectid import ObjectId`, unused anywhere in the file), `server/projectsDatabase.py:2` (`from pymongo import MongoClient`, unused — `projectsDatabase` only ever receives an already-constructed `client`), `server/usersDatabase.py:2` (same unused `MongoClient` import)
**Issue:** Dead imports carried through this phase's rewrite of `app.py` and extension of `projectsDatabase.py`.
**Fix:** Remove the unused imports.

---

_Reviewed: 2026-09-16T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
