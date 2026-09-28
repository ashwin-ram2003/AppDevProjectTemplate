# Phase 5 (Track E): UI Design — Canonical Design Document

This document is the canonical reference for PantryTrack's shared design-token system and
`InventoryView`'s session-identity prop contract. **Track A** and **Track C** are its
readers: Track A wires real session values into `InventoryView`'s call site without
touching its internals, and Track C audits DATA-01/DATA-03 against the prop contracts
documented here and in each component's own JSDoc block. Any new UI work in Track A or
Track C should reference the same token names below rather than introducing new
color/spacing/typography/radius literals.

## Design Tokens

All tokens are CSS custom properties declared in a single `:root` block in
`client/src/index.css` and consumed via `var(--token-name)` from `client/src/App.css`
(and any future stylesheet). Track A and Track C adopt these by referencing the same
names rather than introducing new literals.

### Colour

| Token | Value | Purpose |
|-------|-------|---------|
| `--color-page` | `#F5F1E8` | Page background — warm parchment base |
| `--color-surface` | `#FCFAF5` | Card/panel surface — paper-like, distinct from page |
| `--color-ink` | `#2B2622` | Primary text colour |
| `--color-ink-muted` | `#6E655B` | Secondary/muted text (hints, notes, labels) |
| `--color-rule` | `#DDD5C7` | Default hairline border colour |
| `--color-rule-soft` | `#E7E0D3` | Softer hairline border (nested/inner dividers) |
| `--color-accent` | `#5C4433` | Deep pantry-shelf brown accent — hover/focus emphasis |
| `--color-danger` | `#8C2F22` | Error text colour |
| `--color-loc-pantry` | `#8A6A4B` | Pantry location stripe — shelf wood |
| `--color-loc-fridge` | `#5F8A7D` | Fridge location stripe — cool larder |
| `--color-loc-freezer` | `#5C7796` | Freezer location stripe — cold store |
| `--color-fresh-bg` | `#DCEFD8` | Freshness badge "fresh" background |
| `--color-fresh-fg` | `#2F5D2A` | Freshness badge "fresh" text |
| `--color-fresh-border` | `#A8CFA0` | Freshness badge "fresh" border |
| `--color-expiring-bg` | `#FAEBC8` | Freshness badge "expiring_soon" background |
| `--color-expiring-fg` | `#7A5310` | Freshness badge "expiring_soon" text |
| `--color-expiring-border` | `#E4C273` | Freshness badge "expiring_soon" border |
| `--color-expired-bg` | `#F7DFD8` | Freshness badge "expired" background |
| `--color-expired-fg` | `#8C2F22` | Freshness badge "expired" text |
| `--color-expired-border` | `#E0A99C` | Freshness badge "expired" border |
| `--color-unknown-bg` | `#EDE7DC` | Freshness badge "unknown" background |
| `--color-unknown-fg` | `#4A443C` | Freshness badge "unknown" text |
| `--color-unknown-border` | `#D4CBBC` | Freshness badge "unknown" border |
| `--color-claim-own-bg` | `#E4EBDF` | Reservation entry background — reserved by the current user |
| `--color-claim-own-fg` | `#3C5233` | Reservation entry text — reserved by the current user |
| `--color-claim-own-border` | `#B9C9AC` | Reservation entry border — reserved by the current user |
| `--color-claim-other-bg` | `#F2EDE2` | Reservation entry background — reserved by someone else |
| `--color-claim-other-fg` | `#6E655B` | Reservation entry text — reserved by someone else |
| `--color-claim-other-border` | `#E7E0D3` | Reservation entry border — reserved by someone else |

### Spacing

| Token | Value | Purpose |
|-------|-------|---------|
| `--space-3xs` | `2px` | Smallest gap — tight inline spacing |
| `--space-2xs` | `4px` | Compact gaps (labels, small notes) |
| `--space-xs` | `6px` | Small internal padding |
| `--space-sm` | `8px` | Default small padding/gap |
| `--space-md` | `10px` | Medium internal padding |
| `--space-lg` | `12px` | Larger internal padding (item-actions rows) |
| `--space-xl` | `16px` | Standard component padding/gap |
| `--space-2xl` | `24px` | Section spacing (indents, margins) |
| `--space-3xl` | `32px` | Large section spacing |
| `--space-4xl` | `64px` | Page-level bottom padding |

### Typography

| Token | Value | Purpose |
|-------|-------|---------|
| `--font-sans` | `system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif` | One humanist sans for both UI labels and data (D-07) |
| `--text-xs` | `0.8rem` | Smallest text (badges, fine print) |
| `--text-sm` | `0.85rem` | Small text (batch cards, notes) |
| `--text-md` | `0.9rem` | Medium text (item summary fields) |
| `--text-base` | `1rem` | Base body text size |
| `--weight-regular` | `400` | Regular font weight |
| `--weight-semibold` | `600` | Semibold font weight (names, badges) |
| `--leading-body` | `1.55` | Body line-height |

### Radius & structure

| Token | Value | Purpose |
|-------|-------|---------|
| `--radius-sm` | `4px` | Standard corner radius (cards, forms, buttons) |
| `--radius-pill` | `999px` | Pill shape (freshness badge) |
| `--rule-width` | `1px` | Standard hairline border width |
| `--stripe-width` | `4px` | Location-stripe left-border width on item cards |
| `--motion-fast` | `150ms` | Standard transition duration |
| `--ease-out` | `cubic-bezier(0.2, 0, 0, 1)` | Standard transition easing |

## InventoryView Session-Identity Contract

`InventoryView` (default export of `client/src/components/Project.js`) accepts three
session-identity props. It reads no global auth state and fetches only inventory data
(via `client/src/api/inventory.js`) — session identity must always be supplied by the
caller.

| Prop | Type | Used for |
|------|------|----------|
| `householdId` | `string` | The household whose inventory to load. Passed to `fetchInventory` and to every mutation call (`restock`, `consume`, `reserve`, `release`). |
| `userId` | `string` | The acting user's id. Used for reserve/consume/release calls and to distinguish "your own" reservations in the UI (`ItemActions`). |
| `userName` | `string` | Display name shown on reservation entries this user creates. |

None of these props has a default value or fallback. `InventoryView` does not read any
global auth/session state — the values must be supplied by its caller.

The current values in `client/src/App.js` (`HOUSEHOLD_ID = 'H1'`, `USER_ID = 'alice'`,
`USER_NAME = 'Alice'`) are development placeholders for this tracer slice only. Track A
replaces them with real session values sourced from its own auth/session layer once that
work lands, without editing `InventoryView` internals.

## Component Prop Contracts

This section and the JSDoc blocks in `client/src/components/` are the same contract
recorded twice per decision D-04. The source is authoritative if the two ever disagree.
No component in this tree holds hard-coded fallback data — every prop below has a
Fallback of `none`, and that is the fact Track C audits DATA-01 and DATA-03 against.

### InventoryView

**Source:** `client/src/components/Project.js` (default export)
Data source: fetches via client/src/api/inventory.js

| Prop | Type | Required | Fallback | Purpose |
|------|------|----------|----------|---------|
| `householdId` | `string` | yes | none | The household whose inventory to load; passed to `fetchInventory` and every mutation call. |
| `userId` | `string` | yes | none | The acting user's id; used for reserve/consume/release calls and to distinguish "your own" reservations. |
| `userName` | `string` | yes | none | Display name shown on reservation entries this user creates. |

### LocationSection

**Source:** `client/src/components/Project.js`
Data source: props only

| Prop | Type | Required | Fallback | Purpose |
|------|------|----------|----------|---------|
| `location` | `string` | yes | none | One of Pantry, Fridge, or Freezer; also selects the item card's location-stripe modifier class. |
| `items` | `Array` | yes | none | The already-fetched item array for this location, rendered in the order received. |
| `ambiguityNotice` | `Object` | no | none | Nullable; the ambiguity notice to show alongside the matching item, if any. |
| `userId` | `string` | yes | none | Pass-through session identity; never read or defaulted here, only forwarded to `ItemActions`. |
| `userName` | `string` | yes | none | Pass-through session identity; never read or defaulted here, only forwarded to `ItemActions`. |
| `onChanged` | `Function` | yes | none | The reload callback forwarded to `ItemActions`. |

### AmbiguityNotice

**Source:** `client/src/components/Project.js`
Data source: props only

| Prop | Type | Required | Fallback | Purpose |
|------|------|----------|----------|---------|
| `notice` | `Object` | yes | none | Carries `itemName`, `itemKey`, `location`, and `candidates` describing the restock that could not be merged into an existing item. |

### FreshnessBadge

**Source:** `client/src/components/FreshnessBadge.js`
Data source: props only

| Prop | Type | Required | Fallback | Purpose |
|------|------|----------|----------|---------|
| `freshness` | `string` | yes | none | The server-computed enum: `fresh`, `expiring_soon`, `expired`, or `unknown`. No date arithmetic is performed here. |
| `location` | `string` | yes | none | One of Pantry, Fridge, or Freezer; selects the label/title wording. |

### BatchList

**Source:** `client/src/components/BatchList.js`
Data source: props only

| Prop | Type | Required | Fallback | Purpose |
|------|------|----------|----------|---------|
| `batches` | `Array` | yes | none | The item's batch history, rendered in the order it is received (server-ordered; never re-sorted client-side). |
| `location` | `string` | yes | none | One of Pantry, Fridge, or Freezer; forwarded to `FreshnessBadge` to word each batch's freshness correctly. |

### ItemActions

**Source:** `client/src/components/Checkout.js` (default export)
Data source: mutates via client/src/api/inventory.js

| Prop | Type | Required | Fallback | Purpose |
|------|------|----------|----------|---------|
| `item` | `Object` | yes | none | The already-fetched item object. |
| `userId` | `string` | yes | none | The acting member's identity. |
| `userName` | `string` | yes | none | The acting member's display name. |
| `onChanged` | `Function` | yes | none | Async reload callback, awaited after every successful mutation. |

`item` is read for `householdId`, `location`, `itemName`, `capacity`, `reservations`, and `reservedQuantity`.

### RestockForm

**Source:** `client/src/components/RestockForm.js`
Data source: mutates via client/src/api/inventory.js

| Prop | Type | Required | Fallback | Purpose |
|------|------|----------|----------|---------|
| `householdId` | `string` | yes | none | The household this restock belongs to. |
| `userId` | `string` | yes | none | The acting user's id. |
| `onRestocked` | `Function` | yes | none | Called with the restocked item after a successful submit, including its `matchAmbiguity` field when the server could not disambiguate. |

## Adopting These Tokens in Track A and Track C UI

- Reference token names from `client/src/index.css` (e.g. `var(--color-surface)`, `var(--space-md)`) rather than introducing new color/spacing/typography/radius literals.
- Reuse the established `block--modifier` class naming the codebase already uses for `freshness-badge--fresh` and `item-card--pantry` rather than inventing a new naming scheme.
- The elevation language is hairline borders on flat fills — add no drop shadow and no fade/gradient between two colours.
- The single responsive breakpoint is 599px; a new breakpoint should be justified before being added.

## Accessibility Notes

- Freshness is encoded by colour, a text label, and a title tooltip together. The text label must never be removed in favour of colour alone (WCAG 1.4.1).
- The four freshness background/foreground token pairs were contrast-checked against the parchment surface at 6.39:1 (fresh), 5.79:1 (expiring_soon), 6.48:1 (expired), and 7.82:1 (unknown), all above the 4.5:1 AA floor.
- The three location stripe colours clear the 3:1 non-text floor against `--color-surface` at 4.74:1 (pantry), 3.72:1 (fridge), and 4.44:1 (freezer).
- Batch card field labels stay visible at every width because they are the accessible replacement for the deleted table column headers.

## What This Phase Did Not Change

No data-fetching, mutation, API contract, or freshness computation was altered by Phase 5. `client/src/api/inventory.js` and everything under `server/` are untouched. The placeholder `HOUSEHOLD_ID` / `USER_ID` / `USER_NAME` constants in `client/src/App.js` remain Track A's to remove under ACCT-04.
