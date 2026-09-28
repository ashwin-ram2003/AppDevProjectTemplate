# Proposed update to `WORK-ITEMS.md` § "3. Inventory Management — Track B"

**Produced by:** `/gsd-plan-phase 02` (Track B planning pass), 2026-09-15
**Source of the expansion:** `.planning/phases/02-inventory-management/02-CONTEXT.md` decisions D-01 through D-11
**Status:** proposed — **do not apply automatically.** The orchestrator reviews this and edits the live `WORK-ITEMS.md`.

This file replaces only section 3 of `WORK-ITEMS.md`. Sections 1, 2, 4, 5, the Legend, the Future Vision backlog, and the Totals line are untouched here; see "Knock-on edits" at the bottom for the two lines elsewhere in the file that the orchestrator should adjust.

---

## Rationale — what changed and why

The instruction for this pass was to expand the stories that already exist before inventing new ones, and to add sub-stories where one story can no longer carry the behavior in three sentences. Here is exactly what happened to each of Track B's eight existing items.

### Sub-numbering convention

A sub-story takes its parent's number with a lowercase letter: `US-07a`, `US-07b`. Technical-debt sub-items follow the same shape: `TD-04a`. A sub-story is always a real, separately demonstrable behavior of its parent feature — never a task breakdown. If it cannot be demoed on its own, it belongs in the parent's description instead.

### Expanded in place — no sub-stories needed (2 items)

| Item | What CONTEXT.md added | Why one story still covers it |
|---|---|---|
| **TD-DOC-B** | The schema is now actually decided (D-01 batches, D-03 item identity), so this item can name it concretely instead of pointing at future work. | It is a documentation item; its whole job is to name the artifact, which now exists. |
| **US-R1-B** | Nothing. | The feature-board rubric story is about the board, not about inventory behavior. Per the planning contract, left exactly as-is. |

### Expanded in place AND given sub-stories (5 items, 9 sub-stories)

| Item | Sub-stories added | Why the parent could not absorb them |
|---|---|---|
| **US-06** View inventory | **US-06a** batch detail | "See capacity and availability per location" and "open an item and see which shopping trip each unit came from" are two different screens' worth of behavior. D-01 made per-batch history real data a user can look at, which the original one-line story predates. |
| **US-07** Restock | **US-07a** repeat restock merges · **US-07b** ambiguous name creates a separate item | D-01 and D-03 turned restock from "add a quantity" into three distinct outcomes a user can observe: a new item, a merge into an existing one, and a deliberate refusal to guess between two similar items. Three outcomes will not fit in three sentences. |
| **US-08** Reserve | **US-08a** release a reservation · **US-08b** see a housemate's claim | D-08 added release, which the original story had no room for. D-05 made "unenforced" the defining property of a reservation, and the only way to demonstrate unenforced is from the *other* housemate's point of view — a different actor, so a different story. |
| **US-09** Consume | **US-09a** soonest-expiring batch drains first | D-02's FIFO ordering is observable (the user watches a specific batch shrink) and is the reason batches exist at all, but it is not what the core consume story is about. |
| **US-10** Freshness | **US-10a** Pantry rule · **US-10b** Fridge rule · **US-10c** Freezer rule | D-09, D-10 and D-11 are three different rules, and D-11 is a different *kind* of rule — a quality signal computed from the freeze date, not a food-safety expiry. Three rules cannot share one three-sentence story. |
| **TD-04** Overbooking guard | **TD-04a** concurrent consumes | D-07 narrowed the guard to consume only, which is a correction to the original item's text ("checkout/reserve"). The race-condition half is engineering work with no user-facing story, so it stays technical debt. |

### Considered for a new top-level story — and rejected (3 candidates)

The planning context flagged three things as possible new top-level stories. All three fit under an existing story as a sub-story, so none was created:

1. **Freezer-specific freshness (D-11).** Rejected as a new story. From the household member's side this is still "see freshness at a glance" — the same badge, on the same row, on the same screen. Only the rule behind it differs. It is **US-10c**.
2. **Reservation release (D-08).** Rejected. Releasing is part of a reservation's own lifecycle, not a separate feature. It is **US-08a**.
3. **Item-name matching on restock (D-03).** Rejected. It is what happens *when you restock*, visible only through the restock flow. It is **US-07a** and **US-07b**.

### Genuinely new — 2 technical-debt items, 0 new user stories

Two things surfaced during planning that no existing Track B item covers, and neither is user-facing, so neither is a user story:

- **TD-11 — bootstrap the React client.** `client/` has no `package.json` and every `.js` file under `client/src/` is 0 bytes. No track currently owns standing the React application up, and Track A, Track C and Track D all need it to exist. Track B hits the wall first (its inventory view is the first screen), so Track B does it and the other tracks build into the same shell. **This is a cross-track coordination item — Track A must not create a second application shell.**
- **TD-12 — make the Flask app importable and runnable.** `server/app.py` currently does `import usersDB`, `import projectsDB`, `import hardwareDB`, and no module by any of those names exists — the app cannot start. There is also no `requirements.txt` and no virtual environment anywhere in the repository. This blocks every backend track, not just Track B.

Numbering check: the highest user story currently on the board is US-14 and the highest technical-debt item is TD-10, so the next free top-level IDs are US-15 and TD-11. No user story reached US-15, which is the intended outcome of the expand-first instruction.

### Deliberately NOT added

- **Fractional / partial quantity tracking** ("half the carton is left") is in CONTEXT.md's Deferred Ideas. It does not appear anywhere below. CONTEXT.md notes it should be added to `REQUIREMENTS.md`'s v2 backlog — that is a separate edit to `REQUIREMENTS.md`, outside this section, and is flagged in Knock-on edits below.
- **Cross-household access control** is not a Track B board item. It is handled as a threat-model mitigation inside the phase plans (the household-membership guard) and as Track A's session work (ACCT-04).

---

## Replacement text for § "3. Inventory Management — Track B"

## 3. Inventory Management — Track B

**Goal:** A household member can see what food is on hand and move it through reserve → consume, or add new stock.

**Rubric ownership:** R1-2 (Feature board) · R2-1 (food-item resources in DB + API)

**Schema note:** Track B's item-stock shape is settled in `.planning/phases/02-inventory-management/02-CONTEXT.md` (decisions D-01 through D-11). Each restock is its own batch with its own purchase and best-by dates; an item's capacity is the sum of its batch quantities; item identity is a normalized name within a single location.

| ID | Type | Title | Story / Description | Req | Phase |
|----|------|-------|----------------------|-----|-------|
| TD-DOC-B | Technical debt | Define Track B scope, schema, and initial stories | Define the household item-stock schema — items keyed by Pantry/Fridge/Freezer location, each holding a list of batches with their own quantity, purchase date, and best-by date, with capacity and availability derived as sums — and write Track B's initial user stories for the feature board. Delivered as `02-CONTEXT.md` (decisions D-01..D-11) plus the four phase plans `02-01` through `02-04`. | INV | 1 |
| US-R1-B | User story | Publish the feature board | As the instructor, I want to see every planned feature captured as user stories, technical debt, or research items on a shared board so I can verify the team has scoped its work before implementation begins. | R1-2 | 1 |
| US-06 | User story | View inventory by location | As a household member, I want to see items grouped by Pantry, Fridge, and Freezer with each item's capacity and availability so I know what's on hand at a glance. Availability is what nobody has claimed yet; capacity is what is physically there. A location with nothing in it says so plainly rather than showing a blank space. | INV-01 | 2 |
| US-06a | User story | See an item's batch history | As a household member, I want to open an item and see each shopping trip that went into it — its quantity, purchase date, and best-by date — so I can tell fresh stock apart from older stock of the same food. The batches are listed in the order they will be used up. | INV-01 | 2 |
| US-07 | User story | Restock an item | As a household member, I want to log a new purchase with a quantity, a purchase date, and a best-by date so the inventory reflects what I bought. Each purchase is recorded as its own batch rather than being folded into a running total, so the dates stay attached to the units they belong to. | INV-02 | 2 |
| US-07a | User story | Restock the same food again | As a household member, I want a second purchase of something I already have to add to that item instead of creating a duplicate row, even if I typed the name slightly differently. Matching ignores capitalisation and extra spaces and allows one name to contain the other, but only within the same location — Milk in the Fridge and Milk in the Freezer stay separate. | INV-02 | 2 |
| US-07b | User story | Be told when a name is ambiguous | As a household member, I want the app to create a separate item rather than guess when the name I typed could match two things I already have, and to tell me which two. That way it never silently merges my milk into my milk chocolate. | INV-02 | 2 |
| US-08 | User story | Reserve an item | As a household member, I want to claim a quantity of an item under my name so my housemates know I'm planning to use it. Claiming is a heads-up, not a hold — it never takes the food out of the shared count and never stops anyone else from taking it. | INV-03 | 2 |
| US-08a | User story | Release a claim I made | As a household member, I want to take back a claim I made once I no longer need it, so the item stops showing as spoken for. Only the person who made a claim can release it. | INV-03 | 2 |
| US-08b | User story | See who claimed what | As a household member, I want to see which housemate has claimed a quantity of an item and how much, so I can decide for myself whether to take it anyway or leave it for them. | INV-03 | 2 |
| US-09 | User story | Consume an item | As a household member, I want to log a quantity as used so the inventory count stays accurate. I can do this at any time without claiming it first — grabbing a cup of milk is just a consume. | INV-04 | 2 |
| US-09a | User story | Use the soonest-expiring stock first | As a household member, I want what I consume to come off the batch closest to its date first, spilling into newer stock only when that batch runs out, so the food most likely to go to waste is the food that gets used. | INV-04 | 2 |
| US-10 | User story | See freshness at a glance | As a household member, I want every item to carry a freshness flag worked out from its own dates against today, so I know what to use first. The flag is a plain date comparison — no sensors, no predictions. | INV-05 | 2 |
| US-10a | User story | Pantry freshness | As a household member, I want a pantry item to simply read as fresh until its best-by date passes, with no early warning, because dry staples don't need me chased about them a week out. | INV-05 | 2 |
| US-10b | User story | Fridge freshness | As a household member, I want a fridge item to warn me when it's within three days of its best-by date, and to read as past its date once that day has gone by, so I get a useful window to actually cook it. | INV-05 | 2 |
| US-10c | User story | Freezer quality signal | As a household member, I want a freezer item judged on how long it has been frozen — good under six months, declining from six to twelve, freezer-burn risk beyond that — because frozen food loses quality rather than becoming unsafe. The flag is worked out from the freeze date, and it never tells me to throw food away. | INV-05 | 2 |
| TD-04 | Technical debt | Overbooking guard | Reject a consume that would take more units than the item physically holds, leaving the item completely unchanged when it does — no partial deduction. The guard applies to consume only; a claim is never rejected, because a claim was never a real hold on the food. | INV-04 | 2 |
| TD-04a | Technical debt | Concurrent consumes | Make two simultaneous consumes of the same item unable to drive its count below zero: apply each consume with a conditional update pinned to the exact counts that were read, and have the losing writer re-check the guard before retrying. | INV-04 | 2 |
| TD-11 | Technical debt | Bootstrap the React client | Stand up the React application — `package.json`, build tooling, entry HTML, and root component — since `client/` currently has no package manifest and every source file is empty. **Cross-track coordination point: Track B creates this shell first because its inventory view needs it; Tracks A, C, and D build into the same shell rather than creating a second one.** | — | 2 |
| TD-12 | Technical debt | Make the Flask app runnable | Fix `server/app.py`'s three module imports, which name modules that do not exist and stop the app from starting at all, and add the `requirements.txt` and virtual environment the repository currently lacks. Replace the placeholder connection-string literal with an environment-variable read — the credential half of this overlaps Track C's TD-07, which owns provisioning. | — | 2 |

---

## Knock-on edits elsewhere in `WORK-ITEMS.md`

Two lines outside section 3 go stale once the table above lands. Both are the orchestrator's call:

1. **The Totals line** (currently "5 committed features · 18 user stories · 14 technical debt items (10 Phase 2 + 4 Phase 1 scope/schema/stories items) · 10 research items · 19/19 v1 requirements covered"). After this update Track B carries 9 more user-story rows (all sub-stories of existing stories) and 3 more technical-debt rows (TD-04a, TD-11, TD-12). Whether sub-stories are counted in the headline total or shown as "18 user stories (9 with sub-stories)" is a presentation choice — recommend the latter, so the number still reads as "features scoped", which is what the R1-2 rubric item is asking about.
2. **The Legend** could gain one line defining the sub-story convention, since it is new to the board: *"Sub-story — a separately demonstrable behavior of a parent story, numbered with its parent's ID plus a letter (US-07a)."*

Separately, and outside `WORK-ITEMS.md` entirely: `02-CONTEXT.md` records that **partial/fractional quantity tracking** was deferred and should be added to `REQUIREMENTS.md`'s v2 backlog. That edit has not been made yet and is not part of this file.
