---
phase: 02-inventory-management
review_path: 02-REVIEW.md
fix_scope: critical_warning
fixed: 2026-09-16T01:48:00Z
findings_fixed: 4
findings_skipped: 2
---

# Phase 02: Code Review Fix Report

**Fix scope:** Critical + Warning (Info items IN-01/IN-02 intentionally left unfixed)
**Findings fixed:** 4/4 in scope

> Note: this report was reconstructed by the orchestrator from the gsd-code-fixer agent's
> completion summary after the original `02-REVIEW-FIX.md` (written uncommitted in the fixer's
> isolated worktree) was lost when that worktree was force-removed before the file was checked
> for. The underlying fixes themselves are unaffected — they are safely committed on `main`
> (commits `46db52e`, `5db239d`, `8e40df2`, `b506c21`). Only this narrative report was
> regenerated, not hand-verified line-by-line against the original.

## CR-01 (Critical) — Fixed

**Commit:** `46db52e`

Type-validated `householdId`/`userId` at the shared `assertHouseholdMember` choke point
(`server/projectsDatabase.py`), plus `reservationId` in `removeReservation` and `userName` in
`addReservation` (`server/hardwareDatabase.py`). Added 10 new regression tests in
`server/tests/test_type_validation.py` proving dict/list-typed identifiers are rejected with no
cross-household write — closing the NoSQL-operator injection that let a JSON body like
`{"householdId": {"$ne": "..."}}` bypass household isolation entirely.

## WR-01 (Warning) — Fixed

**Commit:** `5db239d`

Pinned `removeReservation`'s final `find_one_and_update` filter on `reservations.reservationId`
still being present in the array, so a duplicate/racing release call fails to match instead of
unconditionally decrementing `reservedQuantity` a second time.

## WR-02 (Warning) — Fixed

**Commit:** `8e40df2`

Dropped `reservedQuantity` from `consumeFromItem`'s optimistic-concurrency filter — the pinned
condition now checks only `capacity` (the field the overbooking guard and the write both actually
depend on), eliminating spurious `409 ConcurrentModificationError` responses caused by unrelated
concurrent reserve/release activity on the same item.

## WR-03 (Warning) — Fixed

**Commit:** `b506c21`

Added a unique compound index on `Items(householdId, location, itemKey)` and a
`DuplicateKeyError`-triggered retry (read-merge-write) in `addBatch`, closing the race where two
concurrent first-time restocks of the same never-before-seen item name could create two separate
item documents.

## IN-01, IN-02 (Info) — Not fixed (out of scope)

Dead exception handling in `GET /api/inventory` and unused imports (`ObjectId` in `app.py`,
`MongoClient` in `projectsDatabase.py`/`usersDatabase.py`) were intentionally left untouched —
`fix_scope: critical_warning` excludes Info-severity findings by default.

## Verification

- `server/.venv/bin/python -m pytest server/tests -q` → **114 passed** (104 pre-existing + 10 new
  regression tests for CR-01)
- `npm --prefix client run build` → succeeded, no regressions

---
*Fixed: 2026-09-16*
*Fixer: Claude (gsd-code-fixer)*
