# Phase 2: Inventory Management (Track B) - Context

**Gathered:** 2026-09-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Track B delivers household inventory management: viewing food stock by location (Pantry/Fridge/Freezer), restocking items, reserving items (visible-only dibs, not enforced), consuming items, and freshness flags per item — satisfying INV-01 through INV-05 and this track's rubric ownership (R1-2: the feature board itself; R2-1: food-item resources stored in DB with an API). This CONTEXT.md also directly informs completion of the board's `TD-DOC-B` item ("Define the household item-stock schema and write Track B's initial user stories").

</domain>

<decisions>
## Implementation Decisions

### Item & batch model
- **D-01:** Each restock creates its own **batch** (own purchase date + best-by date) rather than overwriting a single aggregate record. An item's total capacity/availability = sum across its batches. — **Reversibility:** costly — collapsing batches into an aggregate later requires a data migration and loses per-batch history.
- **D-02:** Reserve and consume draw from batches **FIFO by best-by date** (soonest-expiring batch first).
- **D-03:** Item identity for batch-merging purposes = same **location** + name matched via **case/whitespace normalization + simple substring/prefix matching** (not exact-string-only, not full fuzzy/NLP matching). E.g. "Milk" and "milk " merge; "Milk" and "Whole Milk" may merge via substring match; "Milk" in Fridge is a distinct item from "Milk" in Freezer.

### Reserve vs. consume
- **D-04:** Reserve and consume are **independent actions**, not a sequential pipeline — consuming never requires reserving first. Reserve represents "dibs" / planning-ahead intent (e.g. claiming the last yogurt for tomorrow); routine partial use (e.g. drinking a cup of milk) is a direct one-time consume.
- **D-05:** Reserve is an **unenforced flag** — it marks a quantity with the reserving user's name/id, visible on the inventory view, but does **not** subtract from what other household members can consume. — **Reversibility:** reversible — can be upgraded to an enforced hold later without breaking existing data (batches/quantities are unaffected).
- **D-06:** Consume always draws directly from total available stock (via the FIFO-by-batch rule above), regardless of any existing reservations.
- **D-07:** TD-04's overbooking guard applies **only to consume** — rejecting a consume that would exceed available stock. It does not apply to reserve, since reserve was never a real claim on the physical pool.
- **D-08:** A reservation can be released/cleared by the user who created it.

### Freshness flag (INV-05) — location-specific, not one flat rule
- **D-09:** **Pantry:** fresh until the best-by date passes, then expired. No early "expiring soon" warning window (dry staples don't need one).
- **D-10:** **Fridge:** expiring soon at ≤3 days before best-by date; expired after best-by passes.
- **D-11:** **Freezer:** explicitly **not** a food-safety expiration model — frozen food doesn't spoil the way fridge/pantry food does. Reframed as a **freezer-burn-risk quality signal** computed from purchase/freeze date (not a user-entered best-by date): fresh <6 months, expiring soon 6–12 months, "expired" (meaning likely freezer-burned/quality-degraded, still safe to eat) >12 months. — **Reversibility:** costly — if a literal best-by-date model is wanted later for Freezer, batches would need a schema change (freeze-date-based computation vs. stored best-by field).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & rubric mapping
- `.planning/REQUIREMENTS.md` — INV-01..05 (Inventory requirement group), Rubric Item Ownership table (Track B owns R1-2, R2-1)
- `.planning/ROADMAP.md` §"Phase 2 (Track B): Inventory Management" — Goal, Depends on, Success Criteria (this phase's roadmap entry; note the "Phase N" prefix here is GSD's own internal tracking ID, not the assignment's Phase 1/2 — see the note at the top of ROADMAP.md's Phases section)
- `.planning/WORK-ITEMS.md` §"3. Inventory Management — Track B" — existing board items to expand (TD-DOC-B, US-R1-B, US-06..US-10, TD-04) per the user's explicit instruction: expand these rather than create new ones unless scope can't be covered
- `Team Project_Fa26.pdf` — Figure 3 "Resource Management" mockup (Capacity/Available/Request/Checkin/Checkout UI) — the original assignment shape this track's schema reframes onto food

### Coordination point
- `.planning/ROADMAP.md` — "Explicit coordination point" section: Track B owns item-quantity updates (reserve, consume/checkout, restock/check-in) within `server/projectsDatabase.py`'s household document; Track A owns household CRUD/membership within the same document.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None yet — `server/hardwareDatabase.py` and `server/projectsDatabase.py` are stub files (function signatures + `pass` bodies only, no logic). `client/src/components/Checkout.js` and `client/src/components/Project.js` are empty (0 bytes) — the frontend has no code, and `client/` has **no `package.json`** at all (React tooling isn't even installed yet). Track B implementation starts from a genuinely blank slate on both ends.

### Established Patterns
- The scaffold's original `hardwareDatabase.py` docstring shows the pre-existing (unimplemented) shape: `HardwareSet = {'hwName': ..., 'capacity': ..., 'availability': ...}` — flat, no location, no batches, no dates. This CONTEXT.md's decisions supersede that shape; the new schema needs `location`, `batches[]` (each with quantity/purchaseDate/bestByDate), and derived `capacity`/`availability` per item+location.
- `projectsDatabase.py`'s docstring shows the household document shape: `hwSets: {HW1: 0, HW2: 10, ...}` — also flat, predates this track's schema decisions. Needs redesign to nest item→location→batches under the household document per the coordination point above.

### Integration Points
- `server/app.py` has stubbed routes (`/get_all_hw_names`, `/get_hw_info`, `/check_out`, `/check_in`, `/create_hardware_set`, `/api/inventory`) that Track B's backend logic will wire up — currently all `pass`/empty `jsonify({})`.

</code_context>

<specifics>
## Specific Ideas

- The user framed "reserve" conceptually themselves during discussion: it's a **coordination signal among trusted housemates** ("calling dibs"), not an access-control mechanism — this shaped D-04/D-05 directly and should guide any UI copy/wording later (e.g. show "reserved by [name]" rather than blocking language).
- The user identified that Freezer freshness is fundamentally different in kind from Fridge/Pantry freshness (quality decay vs. food safety) — this is a domain insight worth preserving verbatim for anyone implementing INV-05, since it's not obvious from the requirement text alone.

</specifics>

<deferred>
## Deferred Ideas

- **Partial/fractional quantity tracking within a unit** (e.g. "half the milk carton is left") — raised by the user as a "later on" idea. Track B's v1 schema uses whole-unit integer quantities only. Should be added to `REQUIREMENTS.md`'s v2 backlog.

</deferred>

---

*Phase: 2-inventory-management*
*Context gathered: 2026-09-15*
