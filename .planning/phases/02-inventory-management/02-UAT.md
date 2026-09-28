---
status: complete
phase: 02-inventory-management
source: [02-VERIFICATION.md]
started: 2026-09-16T02:00:00Z
updated: 2026-09-22T20:20:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Restock tracer browser click-through
expected: Item appears live after submit with no reload; second restock merges into the same row (capacity 7).
result: pass

### 2. Freshness badge wording browser click-through
expected: |
  Pantry/Fridge use "Fresh"/"Use soon"/"Past best-by"; Freezer uses "Good quality"/"Quality declining"/
  "Freezer burn risk" (no safety/discard language); a batch with no date shows "No date".
result: pass

### 3. Batch matching and detail browser click-through
expected: |
  Merge same-name batches, loose-match a superstring name, ambiguous restock creates a new item with
  a notice naming the colliding items, Fridge/Freezer location separation, no-best-by renders a dash.
result: pass

### 4. Consume/reserve/release browser click-through
expected: |
  Consume drains soonest-expiring batch first; over-consume shows on-hand count and keeps typed
  quantity; reserve shows claimant name and drops availability (not capacity); another member's
  consume still succeeds on a fully-reserved item; release hidden for non-owners, works for owner;
  two reservations by the same member are independently releasable.
result: pass

### 5. Concurrent-consume race
expected: |
  Two genuinely concurrent consume requests against a real multi-threaded MongoDB (not mongomock)
  that together exceed capacity: exactly one succeeds, the other gets 409, capacity never negative.
result: pass

## Summary

total: 5
passed: 5
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

None.

## Test Environment Notes

All 5 tests were run against a real local MongoDB (installed via `brew install mongodb-community`,
not mongomock) with the Flask backend (threaded) and Vite dev server both running locally, driven
via Chrome browser automation for tests 1-4 and a genuine two-thread HTTP race (with a
`threading.Barrier` to force simultaneity) against the live server for test 5.

One test-construction correction worth recording: the original test 3 script (from 02-VERIFICATION.md)
assumed restocking "Whole Milk" would create a separate "whole milk" item to later collide with
"Skim Milk". In fact "Whole Milk" correctly loose-matches into the existing "milk" key (D-03's
substring rule), so no separate "whole milk" item is ever created — this is correct product behavior,
not a bug. The ambiguity scenario was re-verified with an equivalent, genuinely ambiguous case
("Almond Butter" + "Peanut Butter", then restock "Butter") and passed, correctly creating a new item
and showing the notice: `"Butter" wasn't merged into an existing item because it could match more
than one: almond butter, peanut butter. A separate item was created instead.`
