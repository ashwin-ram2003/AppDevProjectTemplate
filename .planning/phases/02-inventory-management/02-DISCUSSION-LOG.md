# Phase 2: Inventory Management (Track B) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-15
**Phase:** 2-inventory-management
**Areas discussed:** Batch tracking vs. aggregate stock, Reservation semantics & ownership, Consume vs. Reserve relationship, Freshness thresholds

---

## Batch tracking vs. aggregate stock

| Option | Description | Selected |
|--------|-------------|----------|
| Separate batches | Each restock creates its own batch/lot with own purchase/best-by date; totals sum across batches | ✓ |
| Single aggregate record | One record per item+location, overwritten on each restock | |

**User's choice:** Separate batches.

| Option | Description | Selected |
|--------|-------------|----------|
| FIFO by best-by date | Reserve/consume draws from the soonest-expiring batch first | ✓ |
| User picks the batch | User explicitly selects which batch to draw from | |
| No batch-level draw — pool only | Batches exist for display only; reserve/consume decrements a pooled total | |

**User's choice:** FIFO by best-by date.

| Option | Description | Selected |
|--------|-------------|----------|
| Exact name match, per location | Batches merge only on exact string match + same location | |
| Fuzzy/normalized matching | Attempt to merge near-duplicate names | ✓ |

**User's choice:** Fuzzy/normalized matching — refined in a follow-up to: case/whitespace normalization + simple substring/prefix matching (not full NLP/synonym matching, which was flagged as likely too much scope for the PoC).

**Notes:** None further; area closed after three questions, user chose "Next area."

---

## Reservation semantics & ownership / Consume vs. Reserve relationship

*(These two areas merged organically — the user interrupted the first scripted question to ask "what is the point of a reservation in a household?", which reframed both areas together.)*

**User's question:** "what is the point of a reservation in a household?"

**Claude's response:** Explained INV-03's wording ("reserve/claim... without removing it from the shared inventory") and framed reservation as a "dibs" coordination mechanism among trusted housemates, not a checkout/possession model.

**User's clarification:** "i think it makes more sense to just have the user 'checkout' the item by using it from the inventory as a one time consumption. i wouldnt call 'dibs' on milk and then use a cup and mark that i only used a cup, i would either use the milk completely or have enough to put it back in stock (although later on we would want to somehow track quantity of stock as well, like half the milk is left"

This established: reserve and consume are **independent** actions (not sequential); routine partial use is a direct consume, not reserve-then-consume. The "half the milk left" idea was captured as a deferred backlog item (partial/fractional quantity tracking).

| Option | Description | Selected |
|--------|-------------|----------|
| Reserved stock is protected | Reserving reduces the shared "available" pool; enforced | |
| Reserved stock is just a visible flag, unenforced | Reserving marks intent only; no enforcement | ✓ (via free-text) |

**User's choice (free text):** "i think putting it as a flag would be a fine use but the concept itself doesn't really make sense" — interpreted as: keep reserve as an unenforced flag, since strict enforcement doesn't fit trust-based household dynamics.

**Claude proposed a full resolution** (reserve = unenforced flag with reserving user's name, visible on inventory view, doesn't block others; consume always draws from total available via FIFO batch order; TD-04's overbooking guard applies only to consume; reservations can be released by their creator) and confirmed it with the user via a yes/adjust check — user confirmed "Yes, that's right — move on."

**Deferred idea confirmed:** Partial/fractional quantity tracking within a unit — user selected "Defer it" when asked directly.

---

## Freshness thresholds

| Option | Description | Selected |
|--------|-------------|----------|
| ≤3 days before best-by | Flat rule, no location variation | |
| ≤7 days before best-by | Wider flat window | |
| Varies by location (freezer gets longer window) | Location-based branching rule | ✓ |

**User's choice:** Varies by location.

**Follow-up on exact per-location numbers** — user gave a free-text answer rather than picking a preset: "nothing for pantry bc its all dry staples (unless its something like bread), fridge is <=3 days, freezer is after a year"

**Claude's follow-up clarifications:**
- Pantry: confirmed via multiple-choice — "no expiring-soon window for Pantry" (fresh until best-by passes, then expired; no early warning).
- Freezer: user rejected Claude's first framing ("expiring soon at 11 months, expired at 12, based on a default best-by date") via "Let me describe it differently," then explained: **"freezer shouldn't be expiration bc freezer food doesn't really expire, but freshness might not be as good because of freezer burn."** This reframed Freezer's freshness flag entirely — from a food-safety/best-by model to a freezer-burn-risk quality-decay model computed from purchase/freeze date rather than a best-by date.

| Option | Description | Selected |
|--------|-------------|----------|
| Fresh <6mo, expiring soon 6-12mo, expired >12mo | Matches common freezer-burn guidance | ✓ |
| Different thresholds | User specifies other cutoffs | |

**User's choice:** Fresh <6mo, expiring soon 6-12mo, expired >12mo (with "expired" here meaning likely freezer-burned/quality-degraded, not unsafe).

---

## Claude's Discretion

None — every gray area reached an explicit user decision; no "you decide" was invoked.

## Deferred Ideas

- **Partial/fractional quantity tracking within a unit** (e.g. "half the milk carton is left") — user raised this as a "later on" idea during the Reserve/Consume discussion; explicitly deferred to the v2 backlog rather than built into Track B's v1 schema.
