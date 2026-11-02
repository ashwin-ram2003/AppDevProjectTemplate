# Phase 5: UI Design - Pattern Map

**Mapped:** 2026-09-24
**Files analyzed:** 9 (8 modified in place + 1 new doc)
**Analogs found:** 9 / 9 (self-referential — this phase restyles existing files; each file's own current structure and `BatchList.js`'s existing JSDoc are the analogs)

## Note on analog strategy

This phase has no "new feature, existing precedent elsewhere" shape — it modifies 8 already-built, already-working files in place (tokens, card markup, JSDoc). There is no other component library or design-token system anywhere else in this repo to borrow from (`client/src/components/` is the entire component tree; no CSS Modules/styled-components exist per RESEARCH.md). Accordingly, analogs below are:
1. **`BatchList.js`'s existing JSDoc block** (lines 3-12) — the one component that already has prose-doc-comment style close to what D-04 wants everywhere; use it as the template for the other 5 components' JSDoc.
2. **`Checkout.js`'s existing inline explanatory comments** (lines 4-13, 96-97) — the pattern for *why*-comments near behavior that must survive the restructure (stopPropagation, dibs-not-lock framing).
3. **Each file's own current CSS/JSX** — the literal values/structure to tokenize or restructure, since D-03's rule is "tokenize what's there," not invent new values.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `client/src/index.css` | config (style tokens) | transform | itself — existing `:root` block (lines 1-5) | exact (extend, don't replace) |
| `client/src/App.css` | config (component styles) | transform | itself — existing selectors (lines 1-240) | exact (refactor to consume tokens + add breakpoint) |
| `client/src/components/Project.js` | component | request-response (fetch) + transform (markup) | itself, `LocationSection`/`InventoryView` (lines 19-67, 69-144) | exact |
| `client/src/components/BatchList.js` | component | transform (render) | itself — already has target JSDoc style (lines 3-12) | exact — also serves as JSDoc template for others |
| `client/src/components/FreshnessBadge.js` | component | transform (render) | itself — already has JSDoc (lines 1-11) | exact — also serves as JSDoc template |
| `client/src/components/Checkout.js` (exports `ItemActions`) | component | request-response (mutations) | itself — has inline comments, lacks JSDoc block (lines 4-13, 96-97) | role-match (needs JSDoc added, comment style already present) |
| `client/src/components/RestockForm.js` | component | request-response (mutation) | itself — no JSDoc yet (lines 1-10) | role-match (needs JSDoc added) |
| `client/src/App.js` | component (call site) | request-response | itself — placeholder session constants (lines 4-11, 17) | exact (add JSDoc/comment documenting session-identity contract) |
| `.planning/phases/05-ui-design/05-DESIGN.md` | config/doc (new file) | N/A | `BatchList.js` JSDoc content + this PATTERNS.md's classification table, restructured as canonical prop-contract doc | new — no direct analog, structure given in RESEARCH.md "Recommended Project Structure" |

## Pattern Assignments

### `client/src/index.css` (config, token declarations)

**Analog:** itself, current `:root` block

**Current state** (lines 1-13, full file):
```css
:root {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #1f2933;
  background-color: #f8f9fa;
}

body {
  margin: 0;
}

* {
  box-sizing: border-box;
}
```

**Pattern to apply:** ADD design tokens into this `:root` block — do not duplicate or replace the existing `font-family`/`color`/`background-color` declarations (D-05 will likely change `background-color`/`color` values themselves as part of the warm-kitchen palette, but the *mechanism* is extending this same block). New tokens needed per D-03: `--color-fresh-{bg,fg,border}`, `--color-expiring-{bg,fg,border}`, `--color-expired-{bg,fg,border}`, `--color-unknown-{bg,fg,border}` (tokenized verbatim from `App.css` lines 74-96 below, then D-08-harmonized), `--space-{xs,sm,md,lg,xl}` (4/8/16/24/32px, the confirmed distinct values already in use), `--radius-sm` (4px) and `--radius-pill` (999px, from `.freshness-badge` line 67).

### `client/src/App.css` (config, component styles + new breakpoint)

**Analog:** itself, current selectors

**Freshness palette to tokenize verbatim** (lines 74-96):
```css
.freshness-badge--fresh {
  background-color: #dcfce7;
  color: #166534;
  border-color: #86efac;
}
.freshness-badge--expiring_soon {
  background-color: #fef3c7;
  color: #92400e;
  border-color: #fcd34d;
}
.freshness-badge--expired {
  background-color: #fee2e2;
  color: #991b1b;
  border-color: #fca5a5;
}
.freshness-badge--unknown {
  background-color: #f3f4f6;
  color: #374151;
  border-color: #d1d5db;
}
```
Rewrite each property as `var(--color-*-bg/fg/border)` — CSS class naming convention `freshness-badge--{fresh|expiring_soon|expired|unknown}` (line 74, 80, 86, 92) is the established naming scheme; extend it for any new location-stripe classes (D-06) rather than inventing new naming.

**Spacing values currently hardcoded** (scattered, confirmed distinct set): `4px` (lines 17, 55, 106, 134, 146, 178, 197...), `8px` (lines 23, 29, 44, 61, 104, 127, 146, 152...), `16px` (lines 46, 47, 110, 161), `24px` (line 4, 12), `32px` (line 12 alt) — map each 1:1 to `--space-xs/sm/md/lg/xl` without rounding (RESEARCH.md Pitfall 3).

**Item table → card restructure target** (lines 20-31, item table; lines 137-148, batch table):
```css
.item-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 8px;
}
.item-table th,
.item-table td {
  text-align: left;
  padding: 8px;
  border: 1px solid #d1d5db;
}
```
Add `@media (max-width: 599px)` block per RESEARCH.md Pattern 2 (display:block transform) — paired with the JSX markup restructure in `Project.js`/`BatchList.js` since CONTEXT.md D-02 rules out CSS-only.

**Disclosure/actions classes that must survive restructure** (lines 103-113, 160-194): `.item-disclosure`, `.item-summary`, `.item-summary__name/__capacity/__availability`, `.item-actions`, `.item-actions__row`, `.item-actions__field` — these class names are referenced directly in `Project.js` and `Checkout.js` JSX; do not rename without updating both files together.

### `client/src/components/Project.js` (component, request-response + markup transform)

**Analog:** itself

**Imports pattern** (lines 1-6):
```javascript
import { useCallback, useEffect, useState } from 'react';
import { fetchInventory } from '../api/inventory.js';
import BatchList from './BatchList.js';
import FreshnessBadge from './FreshnessBadge.js';
import ItemActions from './Checkout.js';
import RestockForm from './RestockForm.js';
```
No import changes needed — this phase is presentation-only.

**Row markup to restructure into cards** (lines 36-61, the `<tr>`→`<td colSpan={4}>`→`<details>` structure):
```jsx
{items.map((item) => (
  <tr key={item.itemKey}>
    <td colSpan={4} className="item-row-cell">
      <details className="item-disclosure">
        <summary className="item-summary">
          <span className="item-summary__name">{item.itemName}</span>
          <span className="item-summary__capacity">Capacity: {item.capacity}</span>
          <span className="item-summary__availability">
            Available: {item.availability}
          </span>
          <FreshnessBadge freshness={item.freshness} location={location} />
        </summary>
        <BatchList batches={item.batches} location={location} />
        {ambiguityNotice && ambiguityNotice.itemKey === item.itemKey && (
          <AmbiguityNotice notice={ambiguityNotice} />
        )}
        <ItemActions item={item} userId={userId} userName={userName} onChanged={onChanged} />
      </details>
    </td>
  </tr>
))}
```
**Critical constraint (RESEARCH.md Pitfall 1):** the `<details className="item-disclosure">`/`<summary className="item-summary">` pair MUST remain intact inside whatever new outer wrapper replaces `<tr><td colSpan={4}>` — only the outer table-row wrapper becomes a `<div className="item-card">` (or similar); the disclosure/summary/BatchList/ItemActions nesting order stays the same.

**No JSDoc yet on `InventoryView` (line 69) or `LocationSection` (line 19)** — add per D-04, using `BatchList.js`'s existing JSDoc as the template (see below). Session-identity prop contract (`householdId`, `userId`, `userName`) documented here per SC-3, cross-referenced at the `App.js` call site (line 17).

### `client/src/components/BatchList.js` (component, JSDoc template + markup transform)

**Analog:** itself — already has the target JSDoc shape

**Existing JSDoc to use as the template for all 6 components** (lines 1-12):
```javascript
import FreshnessBadge from './FreshnessBadge.js';

/**
 * BatchList renders one item's batch history -- one row per shopping trip,
 * each with its own quantity, purchase date, best-by date, and freshness.
 *
 * `batches` MUST be rendered in the order it is received. The server
 * already returns batches in consumption order (soonest best-by first for
 * Pantry/Fridge, oldest purchase date first for Freezer, per D-02/D-11 and
 * hardwareDatabase's _batchSortKey) -- re-sorting here in the browser would
 * show a household the wrong thing about what gets used first.
 */
export default function BatchList({ batches, location }) {
```
This is prose-only, not `@param`-tagged — RESEARCH.md Pattern 3 recommends adding `@component`/`@param` tags while keeping this prose intact (the "batches MUST be rendered in order" constraint must be preserved verbatim through any edit — it's an explicit CONTEXT.md canonical_ref).

**Table markup to restructure** (lines 17-38, `<table className="batch-table">`) — same `display:block` treatment as `Project.js`'s item table, paired with `@media (max-width: 599px)` in `App.css`.

### `client/src/components/FreshnessBadge.js` (component, styling-only + JSDoc extension)

**Analog:** itself — already has JSDoc (lines 1-11)

**Existing JSDoc** (lines 1-11) already documents *why* (location-aware wording, no date arithmetic, D-09/D-10/D-11 framing) — extend with `@param` tags per RESEARCH.md Pattern 3, do not replace the prose (it directly encodes prior-track decisions this phase must respect per CONTEXT.md canonical_refs).

**Class-naming convention to preserve** (line 60):
```jsx
<span className={`freshness-badge freshness-badge--${freshnessClass}`} title={title}>
```
`freshness-badge--{fresh|expiring_soon|expired|unknown}` — do not change class names, only the CSS values those classes resolve to (App.css tokenization). Text label + `title` tooltip must stay (RESEARCH.md Pitfall 4 — color-only encoding fails accessibility).

### `client/src/components/Checkout.js` (component `ItemActions`, request-response mutations)

**Analog:** itself — has explanatory comments but no JSDoc block yet

**Existing inline comment to convert into the JSDoc block** (lines 4-13):
```javascript
// The name "Checkout.js" carries over from the assignment's checkout
// mockup, which maps onto consuming (see plan 02-04). This component also
// renders reserve and release -- everything a household member does to an
// item's own row besides restocking.
//
// A reservation is a coordination signal among housemates ("dibs"), never
// a lock (D-05, D-07). The consume control below is never disabled, hidden,
// or gated by the presence of any reservation, and the reserved display
// below only ever names who claimed what -- it never says "unavailable",
// "locked", or "blocked".
export default function ItemActions({ item, userId, userName, onChanged }) {
```
Convert to `/** ... */` JSDoc with `@param` tags per D-04, preserving all "dibs not lock" framing verbatim (this directly encodes CONTEXT.md canonical_ref to `02-CONTEXT.md` D-04/D-05).

**stopPropagation pattern that must survive card restructure** (lines 96-98, RESEARCH.md Pitfall 2):
```jsx
// Clicking inside these controls must not toggle the surrounding
// <details> disclosure the item row lives in.
<div className="item-actions" onClick={(event) => event.stopPropagation()}>
```
Preserve `ItemActions`'s position as a descendant of the same `<details>` it's inside today — do not move it outside the disclosure during the card restructure.

**Reservation entry class-naming convention** (lines 142-146) to extend if D-06 stripe styling touches reservation entries too:
```jsx
className={
  entry.userId === userId
    ? 'reservation-entry reservation-entry--own'
    : 'reservation-entry reservation-entry--other'
}
```

### `client/src/components/RestockForm.js` (component, request-response mutation, token/spacing polish only)

**Analog:** itself — no JSDoc yet, no markup restructure needed per CONTEXT.md ("token/spacing polish only, no markup restructure")

**Current form structure** (lines 42-45):
```jsx
<form className="restock-form" onSubmit={handleSubmit}>
  <h3>Restock an item</h3>
```
Add JSDoc above `export default function RestockForm({ householdId, userId, onRestocked })` (line 10) per D-04, using the `BatchList.js` template. CSS-only changes here: `.restock-form` (App.css lines 42-62) needs `padding`/`gap`/`border-radius` swapped to `var(--space-*)`/`var(--radius-sm)` tokens — no JSX/markup edits required.

### `client/src/App.js` (call site, session-identity documentation)

**Analog:** itself

**Existing placeholder comment to extend** (lines 4-11):
```javascript
// Track A's session/auth layer (ACCT-04) has not landed yet, so there is no
// login flow to source householdId/userId/userName from. These are
// placeholder identifiers for this tracer slice only; the seeded household
// for local development is documented in the phase SUMMARY. Track A wires
// real session values in here once ACCT-04 lands.
const HOUSEHOLD_ID = 'H1';
const USER_ID = 'alice';
const USER_NAME = 'Alice';
```
This comment already documents *why* the values are placeholders — SC-3 requires this call site to also reference the documented prop contract. Add a line pointing to `05-DESIGN.md` (e.g. `// See .planning/phases/05-ui-design/05-DESIGN.md for InventoryView's full session-identity prop contract.`) near line 17 (`<InventoryView householdId={HOUSEHOLD_ID} userId={USER_ID} userName={USER_NAME} />`).

### `.planning/phases/05-ui-design/05-DESIGN.md` (new canonical doc)

**No direct file analog** — structure per RESEARCH.md's own "Recommended Project Structure" section and D-04's requirement: one section per component with its data-only prop contract, plus a dedicated `InventoryView` session-identity section, plus the token table (colors/spacing/typography/radius with names and values). Source content = the JSDoc blocks written into each component file (single source of truth duplicated for readability, not re-derived).

---

## Shared Patterns

### JSDoc prop-contract block (D-04)
**Source:** `client/src/components/BatchList.js` lines 3-12 (prose style), `FreshnessBadge.js` lines 1-11 (prose style)
**Apply to:** `Project.js` (`InventoryView`, `LocationSection`), `Checkout.js` (`ItemActions`), `RestockForm.js` — the 4 components currently missing a JSDoc block. `BatchList.js` and `FreshnessBadge.js` need `@param` tags added to their existing prose, not a full rewrite.
```javascript
/**
 * <ComponentName> is a data-only presentational component — it does not
 * fetch its own data / has no hard-coded fallback (state which applies).
 *
 * @component
 * @param {Object} props
 * @param {string} props.xyz - description, note "No fallback/default" where true.
 */
```

### Freshness color-coding class convention
**Source:** `client/src/App.css` lines 74-96, `client/src/components/FreshnessBadge.js` line 60
**Apply to:** `App.css` token block, any new D-06 location-stripe classes
```css
.freshness-badge--{fresh|expiring_soon|expired|unknown}
```
Extend this `--` BEM-modifier naming convention for new classes (e.g. `.item-card--{pantry|fridge|freezer}` for D-06 stripes) rather than inventing a new scheme.

### Table→card responsive transform
**Source:** RESEARCH.md Pattern 2 (no existing codebase precedent — first responsive breakpoint in the project)
**Apply to:** `Project.js`'s item table (lines 26-63) and `BatchList.js`'s batch table (lines 17-38)
```css
@media (max-width: 599px) {
  .item-card { /* new markup replacing <table><tr><td colSpan> */
    border: 1px solid var(--color-unknown-border);
    border-radius: var(--radius-sm);
    border-left-width: 4px; /* D-06 location stripe */
    margin-bottom: var(--space-md);
  }
}
```

### stopPropagation / disclosure preservation
**Source:** `client/src/components/Checkout.js` lines 96-98, `client/src/components/Project.js` lines 39-40
**Apply to:** Any card-restructure edit touching `Project.js` row markup or `Checkout.js` root div — verify click-to-expand and click-to-act-without-collapsing both still work after restructure (RESEARCH.md Pitfalls 1 and 2).

## No Analog Found

None — every file in scope is a modification of existing, already-read source; there is no file in this phase without a direct "itself" analog.

## Metadata

**Analog search scope:** `client/src/` (entire client tree — 8 files read in full, no file > 250 lines, no Grep/offset reads needed)
**Files scanned:** `App.css`, `index.css`, `App.js`, `components/Project.js`, `components/BatchList.js`, `components/FreshnessBadge.js`, `components/Checkout.js`, `components/RestockForm.js` (8 files, all git-tracked, verified via `git ls-files`)
**Pattern extraction date:** 2026-09-24
