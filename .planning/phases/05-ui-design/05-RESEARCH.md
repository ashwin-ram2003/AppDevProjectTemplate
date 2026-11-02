# Phase 5: UI Design - Research

**Researched:** 2026-09-24
**Domain:** React presentational component restyling — CSS custom-property design tokens, mobile card layout restructure, in-source prop-contract documentation
**Confidence:** HIGH

## Summary

This phase is a pure presentation-layer restructure of five already-built, already-working React components (`InventoryView`/`Project.js`, `FreshnessBadge`, `BatchList`, `RestockForm`, `Checkout`/`ItemActions`) plus their shared stylesheet (`App.css`/`index.css`). No new npm packages, no new data flow, no new backend surface. Everything needed to execute this phase — the design direction (D-05..D-08), the token scope (D-03), the mobile-layout mechanism (D-01/D-02), and the documentation split (D-04) — is already locked in `05-CONTEXT.md`. Research therefore focuses on *how* to implement those locked decisions correctly given the codebase's actual current state (read directly, not assumed) and on well-established, low-risk CSS/React patterns rather than library evaluation — there is no library to evaluate, since the client has zero styling dependencies (`client/package.json` lists only `react`, `react-dom`, `@vitejs/plugin-react`, `vite`) and the project's own CLAUDE.md/CONTEXT.md direction is to keep it that way.

The three technical mechanisms this phase needs are all native-CSS, zero-dependency techniques: CSS custom properties in `:root` for the token system (D-03), a `display: block`-based media-query table→card transform for the two `<table>` elements that need restructuring (D-01/D-02), and JSDoc block comments above each component's function signature for the in-source half of the prop-contract documentation (D-04). All three are current, stable, framework-agnostic patterns with no version-currency risk — this is not a fast-moving ecosystem area.

**Primary recommendation:** Implement CSS custom properties in `index.css`'s existing `:root` block (extending, not duplicating, the font/color already set there), restructure `Project.js`'s `<table>`/`<tr>`/`<td>` and `BatchList.js`'s `<table>` to a card layout below a `max-width: 599px` media query using `display: block` on table elements (preserving the `<details>` disclosure wrapper), and add one JSDoc block per component documenting its data-only prop contract — writing the canonical version into a new `05-DESIGN.md` in the phase directory per D-04.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Visual layout / responsive breakpoint | Browser / Client (CSS) | — | Pure presentation; no data or business logic involved |
| Freshness color coding | Browser / Client (CSS + `FreshnessBadge.js`) | — | Server already computes the `freshness` enum value (INV-05); this phase only maps it to color/label, unchanged from today |
| Design token definitions | Browser / Client (`index.css` `:root`) | — | CSS custom properties are a browser-native mechanism; no build step needed |
| Component prop-contract documentation | Browser / Client (source JSDoc) + Docs (`05-DESIGN.md`) | — | Contract lives both in-source (D-04, so editors see it) and in a canonical phase doc (D-04, so Track A/C can read it without opening every file) |
| Session-identity prop wiring (`householdId`/`userId`/`userName`) | Frontend Server / Client (`App.js` call site) | — | Out of scope for *implementation* this phase (Track A owns that) — this phase only documents the existing contract at the existing call site |
| Data fetching / API contracts | API / Backend (`client/src/api/inventory.js`, Flask routes) | — | Explicitly untouched this phase — CONTEXT.md D-02/D-04 restrict scope to markup + CSS |

## Package Legitimacy Audit

**Not applicable — this phase installs no new packages.** `client/package.json` currently has zero styling-related dependencies (`react`, `react-dom` as runtime deps; `@vitejs/plugin-react`, `vite` as dev deps) `[VERIFIED: client/package.json — read this session]`. CONTEXT.md's Established Patterns section confirms: "no CSS Modules or styled-components — all styling is global classes in `App.css`/`index.css`." The recommended implementation (CSS custom properties, media queries) requires no library. If the planner considers introducing any CSS tooling (PostCSS, a CSS-in-JS library, a component library), that would be a scope deviation from CONTEXT.md's decisions and should be flagged, not silently added.

**Packages removed due to [SLOP] verdict:** none — no packages evaluated.
**Packages flagged as suspicious [SUS]:** none.

## Standard Stack

### Core
No new libraries. This phase uses only what's already installed: React 18.3.1 function components + plain CSS via `App.css`/`index.css` `[VERIFIED: client/package.json — read this session]`.

### Supporting
| Technique | Purpose | Why Standard |
|-----------|---------|---------------|
| CSS Custom Properties (`--token-name`) | Design tokens (D-03) | Native browser feature since ~2017, zero build tooling, works with the project's existing global-CSS convention `[CITED: penpot.app/blog/the-developers-guide-to-design-tokens-and-css-variables]` |
| `display: block` table→card media query | Mobile card layout (D-01/D-02) | Standard responsive-table pattern requiring no JS; widely documented, framework-agnostic `[CITED: web search — reintech.io/blog/creating-responsive-table-css, codeburst.io/undo-tables-to-make-them-responsive]` |
| JSDoc `@component`/`@param` block comments | In-source prop contract (D-04) | Standard convention for documenting React props without TypeScript/PropTypes; IDE-readable via hover tooltips `[CITED: schof.co/writing-jsdoc-for-react-components, inkoop.io/blog/a-guide-to-js-docs-for-react-js]` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| CSS custom properties | Sass/PostCSS variables | Requires adding a build-time preprocessor dependency the project doesn't have; CSS custom properties need zero new tooling and CONTEXT.md's Established Patterns section directs sticking with the existing global-CSS convention |
| `display: block` table→card CSS | JS-driven conditional rendering (render `<table>` vs `<div class="card">` based on `window.innerWidth`) | Adds React state/resize-listener complexity and a layout-thrash risk for a problem CSS solves natively; also breaks progressive enhancement (works without JS re-render on resize) |
| Flexbox/Grid card layout (new markup entirely) | CSS Grid `display: grid` cards | Both are valid; Grid is slightly more idiomatic for 2-D card layouts (label + value pairs) — recommend Grid for the per-field label/value pairs inside each card, Flexbox for the card list itself. Either satisfies D-01/D-02; no dependency difference. |
| JSDoc comments | PropTypes package | Adds a new runtime dependency (`prop-types` npm package) for a PoC that has zero type-checking anywhere else in the codebase; JSDoc achieves the documentation goal (IDE hover, `05-DESIGN.md` cross-reference) without adding a dependency, consistent with D-04's requirement being *documentation*, not *runtime validation* |

**Installation:**
No installation required — zero new dependencies this phase.

**Version verification:** N/A — no packages to version-check. React 18.3.1 and Vite 5.4.1 confirmed already installed via `client/package.json` `[VERIFIED: client/package.json — read this session]`.

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Browser (React client, client/src/)                         │
│                                                                │
│  App.js (call site — documents session-identity contract)    │
│    │  householdId="H1" userId="alice" userName="Alice"       │
│    │  (placeholder values today; Track A wires real values   │
│    │   in later without touching InventoryView internals)    │
│    ▼                                                          │
│  InventoryView (Project.js)                                  │
│    │  fetches inventory via client/src/api/inventory.js      │
│    │  (UNCHANGED this phase)                                 │
│    ▼                                                          │
│  LocationSection (×3: Pantry/Fridge/Freezer)                 │
│    │  renders item rows — TABLE today, CARD layout <600px    │
│    ├──► FreshnessBadge (color+label from server-computed     │
│    │      `freshness` enum — UNCHANGED logic, styling only)  │
│    ├──► BatchList (nested table — TABLE today, CARD <600px)  │
│    │      └──► FreshnessBadge (per batch)                    │
│    └──► ItemActions (Checkout.js) — reserve/consume/release  │
│           forms rendered inline per item                     │
│  RestockForm — standalone form, token/spacing polish only    │
│                                                                │
│  Styling: index.css (:root — NEW: design tokens added here)  │
│           App.css (component classes — refactored to         │
│                     consume tokens instead of hardcoded hex/px)│
└─────────────────────────────────────────────────────────────┘

Data flow direction: App.js → InventoryView → api/inventory.js → Flask
backend (unchanged). This phase's changes flow the OTHER direction:
index.css tokens → App.css component styles → JSX markup restructure
(table → card below breakpoint). No arrow crosses into API/data layer.
```

### Recommended Project Structure
No new files/folders needed beyond the phase's documentation artifact:
```
client/src/
├── index.css              # :root — ADD design tokens here (extends existing font/color)
├── App.css                 # component styles — REFACTOR to consume tokens, ADD card-layout media query
└── components/
    ├── Project.js           # ADD JSDoc above InventoryView + LocationSection; RESTRUCTURE item-row markup for card layout
    ├── FreshnessBadge.js     # ADD JSDoc; styling-only changes (palette harmonization per D-08)
    ├── BatchList.js          # ADD JSDoc; RESTRUCTURE batch-table markup for card layout
    ├── RestockForm.js        # ADD JSDoc; token/spacing polish only, no markup restructure
    └── Checkout.js            # ADD JSDoc; markup adjustment only if card restructure forces it (Claude's Discretion per CONTEXT.md)

.planning/phases/05-ui-design/
└── 05-DESIGN.md             # NEW — canonical prop-contract doc (D-04), planner/executor artifact
```

### Pattern 1: CSS Custom Properties as Design Tokens
**What:** Define token variables in `:root`, reference them via `var(--token-name)` throughout component CSS instead of hardcoded hex/px values.
**When to use:** Every color, spacing, typography, and radius value currently hardcoded in `App.css` (D-03 requires this — "replacing the ad-hoc 8/16/24/32px values scattered through selectors").
**Example:**
```css
/* Source: pattern per CITED penpot.app/blog/the-developers-guide-to-design-tokens-and-css-variables;
   token names extend existing FreshnessBadge CSS class convention
   (freshness-badge--{fresh|expiring_soon|expired|unknown}) per CONTEXT.md Reusable Assets */
:root {
  /* existing index.css declarations (font-family, color, background-color) stay as-is;
     tokens ADD to this block, they do not replace what's already there */

  /* color — freshness palette tokenized from current App.css values verbatim
     (values pending D-08 harmonization pass against the new warm-kitchen base) */
  --color-fresh-bg: #dcfce7;
  --color-fresh-fg: #166534;
  --color-fresh-border: #86efac;
  --color-expiring-bg: #fef3c7;
  --color-expiring-fg: #92400e;
  --color-expiring-border: #fcd34d;
  --color-expired-bg: #fee2e2;
  --color-expired-fg: #991b1b;
  --color-expired-border: #fca5a5;
  --color-unknown-bg: #f3f4f6;
  --color-unknown-fg: #374151;
  --color-unknown-border: #d1d5db;

  /* spacing scale — replaces the 8/16/24/32px values already in App.css */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* radius */
  --radius-sm: 4px;
  --radius-pill: 999px; /* freshness-badge's existing border-radius */
}

.freshness-badge--fresh {
  background-color: var(--color-fresh-bg);
  color: var(--color-fresh-fg);
  border-color: var(--color-fresh-border);
}
```
Note: the exact token *names* and final hex/px *values* are Claude's Discretion per CONTEXT.md — the example above shows the mechanism (token declaration → `var()` consumption) grounded in the verbatim current values from `App.css`, not a prescribed final palette.

### Pattern 2: Table-to-Card Responsive Transform
**What:** Below a breakpoint, table elements switch `display` to `block`/`grid`, so each row renders as a standalone card; labels that were column headers become inline labels per field.
**When to use:** `Project.js`'s item table and `BatchList.js`'s batch table (D-01/D-02 — both explicitly named as needing markup restructure, not CSS-only).
**Example:**
```css
/* Source: pattern per CITED reintech.io/blog/creating-responsive-table-css,
   codeburst.io/undo-tables-to-make-them-responsive (display:block technique) */
@media (max-width: 599px) {
  .item-table,
  .item-table thead,
  .item-table tbody,
  .item-table tr,
  .item-table td {
    display: block;
    width: 100%;
  }
  .item-table thead {
    display: none; /* labels move inline instead, see markup note below */
  }
  .item-table tr {
    margin-bottom: var(--space-md);
    border: 1px solid var(--color-unknown-border);
    border-radius: var(--radius-sm);
    /* D-06: colored left-edge stripe per location instead of uniform shadow */
    border-left-width: 4px;
  }
}
```
Because `Project.js`'s current markup already collapses each item row into a single `colSpan={4}` cell containing a `<details>` disclosure (not four separate `<td>`s with column data), the "inject column headers via `::before`" sub-pattern doesn't directly apply here — the existing `item-summary__name`/`item-summary__capacity`/`item-summary__availability` spans already carry their own inline text, not raw table-cell values. The restructure work is therefore markup-level (turn the row into a `<div class="item-card">` with the `<details>` inside it, dropping `<table>`/`<tr>`/`<td>` entirely below the breakpoint or unconditionally) rather than a pure CSS toggle — this matches CONTEXT.md D-02's explicit call that "the `<table><tr>` structure cannot become a real card layout via CSS alone."

### Pattern 3: JSDoc Prop-Contract Documentation
**What:** A `/** ... */` block above each component's function declaration, using `@component`, `@param`, and prose describing what the prop *is not* (D-04's "data-only, no internal fetch, no hard-coded fallback" contract).
**When to use:** Every presentational component (`InventoryView`, `LocationSection`, `FreshnessBadge`, `BatchList`, `RestockForm`, `ItemActions`) — D-04 requires this at every component, mirroring `BatchList.js`'s and `Checkout.js`'s existing doc-comment style (both already have prose block comments today, just not in `@param` JSDoc form).
**Example:**
```javascript
// Source: pattern per CITED schof.co/writing-jsdoc-for-react-components
/**
 * InventoryView is the top-level presentational component for a household's
 * inventory. It fetches its own data (via client/src/api/inventory.js) but
 * accepts session identity as props rather than reading it from any global
 * auth state -- Track A's session/auth layer wires real values in here.
 *
 * @component
 * @param {Object} props
 * @param {string} props.householdId - The household whose inventory to load.
 *   No fallback/default; a real session must supply this.
 * @param {string} props.userId - The acting user's id, used for reserve/
 *   consume/release calls and to distinguish "your own" reservations in the
 *   UI (see ItemActions). No fallback/default.
 * @param {string} props.userName - Display name shown on reservation entries
 *   this user creates. No fallback/default.
 */
export default function InventoryView({ householdId, userId, userName }) {
```

### Anti-Patterns to Avoid
- **Hardcoding new hex/px values instead of extending the token set:** Defeats D-03's purpose. Every new value introduced by the card-layout restructure (e.g., a left-edge stripe width, a card border color) should be a token reference, not a fresh magic number.
- **CSS-only card "layout" that keeps the `<table>` DOM structure:** CONTEXT.md D-02 explicitly rules this out — screen readers and real card semantics both suffer if the underlying markup is still `<table><tr><td>` with `display:block` slapped on and nothing else; the recommended approach replaces the row markup with `<div>`-based cards below (or at all widths for) the breakpoint.
- **A new "design system" package or component library:** D-03 calls for "a small shared set of style tokens," explicitly not a full design system; CONTEXT.md's Established Patterns confirms no CSS Modules/styled-components exist today. Introducing one would contradict both the locked decision and the project's zero-dependency styling convention.
- **Terracotta near `#D97757` in the palette:** Explicitly named and ruled out in D-05 as a generic-AI-template tell.
- **Identical-rounded-shadow "SaaS card kit" styling:** D-06 explicitly rules this out for item/batch cards in favor of flat/minimal shadow + colored left-edge stripe per location.
- **Re-sorting batches in the browser:** `BatchList.js`'s existing doc comment (lines 4-12) states batches "MUST be rendered in the order it is received" — the card restructure must preserve render order, not introduce a client-side sort.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Design token management | A custom JS theme object imported into every component | CSS custom properties in `:root` | Native browser cascade means every component's existing global CSS class automatically picks up token changes with zero JS wiring; matches the project's current all-global-CSS convention |
| Prop type/shape validation for a documentation-only need | The `prop-types` npm package + runtime `.propTypes` blocks on every component | JSDoc `@param` comments | D-04's contract requirement is about *documentation* for other tracks to read, not runtime validation; adding `prop-types` would be a new dependency the phase doesn't need |
| Responsive table transform | A JS `matchMedia`/resize-listener that swaps between two separate JSX trees (table vs. card) | CSS `@media` query + `display: block` markup restructure | CSS media queries are declarative, work before React hydrates, and don't risk layout thrash or duplicate-state bugs from maintaining two parallel render paths for the same data |

**Key insight:** Every problem this phase touches (tokens, responsive layout, prop docs) has a native, zero-dependency solution that fits the existing codebase's plain-global-CSS, no-TypeScript convention. There is no library gap to fill — the risk in this phase is scope creep toward adding tooling the codebase doesn't have and CONTEXT.md doesn't call for, not a missing-library problem.

## Common Pitfalls

### Pitfall 1: Card restructure silently breaks the `<details>` disclosure behavior
**What goes wrong:** `Project.js`'s current item row nests a `<details>`/`<summary>` disclosure inside the table row (`item-disclosure`/`item-summary` classes) for expand/collapse. If the card restructure replaces the row markup without preserving this element, click-to-expand behavior for batches/actions silently disappears with no console error.
**Why it happens:** The restructure work naturally focuses on the outer row→card wrapper; it's easy to flatten the inner `<details>` while moving markup around.
**How to avoid:** Keep `<details className="item-disclosure">` and `<summary className="item-summary">` as the inner structure of the new card `<div>`, only replacing the outer `<table><tr><td colSpan={4}>` wrapper. CONTEXT.md's Established Patterns section flags this explicitly: "The card restructure needs to preserve the expand/collapse (disclosure) behavior in whatever new markup replaces the table row."
**Warning signs:** Clicking an item name/row no longer reveals the batch list and item actions; batch list and actions render always-visible instead of collapsed.

### Pitfall 2: `ItemActions`'s click-stop-propagation breaks inside new card markup
**What goes wrong:** `Checkout.js`'s `ItemActions` wraps its root `<div>` in `onClick={(event) => event.stopPropagation()}` specifically so clicking inside the reserve/consume forms doesn't toggle the surrounding `<details>`. If the card restructure changes how `ItemActions` is nested relative to the `<details>`/`<summary>`, this stopPropagation call may become a no-op or (worse) block a click handler it wasn't meant to block.
**Why it happens:** The comment explaining *why* this exists (lines 96-97 of `Checkout.js`) is easy to miss if only the outer card wrapper is being edited, not `Checkout.js` itself.
**How to avoid:** Preserve `ItemActions`'s position as a descendant of the same `<details>` element it's inside today; test that clicking a Consume/Reserve button does not collapse the card.
**Warning signs:** Clicking "Consume" or "Reserve" also collapses the item card before or during the action.

### Pitfall 3: Token refactor changes computed values, not just variable syntax
**What goes wrong:** Swapping `padding: 8px` for `padding: var(--space-sm)` is safe only if `--space-sm` is defined as exactly `8px`. A hasty tokenization pass that "rounds" values to a cleaner scale (e.g., collapsing `4px`/`8px`/`16px`/`24px`/`32px` into a stricter `4/8/16/32` scale) will visually shift every element still using the dropped value, in a phase whose CONTEXT.md doesn't ask for spacing *redesign* — only *tokenization* of what's there.
**Why it happens:** It's tempting to "clean up" values while touching every selector anyway.
**How to avoid:** First pass: define tokens matching current values exactly (audit `App.css` for every distinct px value used — 4, 8, 16, 24, 32 are the confirmed ones `[VERIFIED: client/src/App.css — read this session]`, see verbatim values below). Second pass (if desired, separately): adjust scale deliberately.
**Warning signs:** Visual diff shows spacing changes in areas the plan didn't intend to touch.

### Pitfall 4: Color-only freshness coding without text fails accessibility even though the badge is "recognizable"
**What goes wrong:** Success Criterion 2 asks for color coding "a household member can recognize without reading the label text" — read literally, a plan might strip the text label to rely on color alone, which fails WCAG 1.4.1 (Use of Color) for colorblind users.
**Why it happens:** Over-literal interpretation of "without reading the label text" as "the label text doesn't need to be there," rather than "color should be *fast to recognize*, in addition to the text that's already there."
**How to avoid:** Keep `FreshnessBadge`'s existing text label (`Fresh`/`Use soon`/`Past best-by`/etc.) and `title` tooltip — both already present in `FreshnessBadge.js` — and treat color as a *reinforcing*, not sole, signal. The current implementation already does this correctly; the pitfall is regressing it during the D-08 palette-harmonization pass.
**Warning signs:** A design mock or PR shows freshness communicated only via a colored dot/stripe with no adjacent text.

## Code Examples

### Verified current freshness-badge palette (pre-harmonization, tokenize these values)
```css
/* Source: client/src/App.css lines 74-96 — read this session, quoted verbatim */
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
`[VERIFIED: client/src/App.css:74-96]`

### Verified WCAG contrast ratios of the current palette (computed this session)
Computed via the standard WCAG relative-luminance contrast formula against the hex pairs above:
- fresh (bg `#dcfce7` / fg `#166534`): **6.49:1**
- expiring_soon (bg `#fef3c7` / fg `#92400e`): **6.37:1**
- expired (bg `#fee2e2` / fg `#991b1b`): **6.80:1**
- unknown (bg `#f3f4f6` / fg `#374151`): **9.37:1**

All four exceed the WCAG AA minimum of 4.5:1 for normal text `[VERIFIED: computed this session via WCAG relative-luminance formula against client/src/App.css:74-96 hex values]`. This confirms CONTEXT.md's Reusable Assets claim that the existing palette is "already a reasonable, accessible-contrast palette" — D-08's harmonization pass against the new warm-kitchen background should re-verify contrast if background hex values change, since this computation is only valid for the current `#f8f9fa`-adjacent surface colors.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Sass/LESS variables for design tokens | CSS custom properties (`var(--token)`) | Broad browser support since ~2017 (all evergreen browsers) | No build-step dependency needed; directly usable in the project's existing plain-CSS files |
| `column-hiding`/horizontal-scroll responsive tables | `display:block` card-transform or CSS Grid-based responsive tables | Long-established (not a recent shift) | Chosen explicitly over both alternatives by D-01 — stacked cards, not scroll or hidden columns |

**Deprecated/outdated:** Nothing in this phase's domain is deprecated — CSS custom properties and media-query table transforms remain the current, non-superseded approach as of this research date.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `599px` (below `600px`) is the exact breakpoint boundary to use in code examples | Pattern 2 (Architecture Patterns) | Low — CONTEXT.md marks the exact value as Claude's Discretion ("~600px suggested... planner/executor may tune based on actual phone-width testing"); using `max-width: 599px` is a reasonable interpretation of "below ~600px" but the planner should confirm the final value during implementation, not treat 599 as locked |
| A2 | CSS Grid is preferable to Flexbox for the internal label/value layout inside each card | Alternatives Considered table | Low — purely a technique preference for D-01/D-02's implementation; either satisfies the locked decision, no functional risk either way |

**Assumption A1 and A2 carry low risk and don't require a discuss-phase loop** — both are within CONTEXT.md's explicitly stated "Claude's Discretion" scope, not areas the user locked.

## Open Questions

1. **Should `RestockForm.js` and `Checkout.js` also get a mobile-width layout pass, or only the item/batch tables?**
   - What we know: D-01/D-02 name `Project.js`'s item table and `BatchList.js`'s batch table explicitly as needing markup restructure. `RestockForm.js` is a `display:grid` form (not a table) that likely already stacks reasonably on narrow screens with minor `max-width` adjustment. `Checkout.js`'s `ItemActions` renders inline forms per row.
   - What's unclear: Whether `ItemActions`'s `.item-actions__row` (a flex row of label+input+button) needs its own narrow-screen stacking treatment, or whether it naturally reflows once its containing card is narrow.
   - Recommendation: CONTEXT.md already flags this as Claude's Discretion ("Whether `Checkout.js`/`ItemActions` needs markup changes beyond what the card restructure forces — determined during implementation"). Planner should schedule a phone-width visual check as a verification step rather than pre-committing to specific `ItemActions` markup changes now.

2. **Exact final hex values for the D-05 warm-kitchen palette and D-08 harmonized freshness badge colors**
   - What we know: Direction is locked (butter/parchment neutrals, deep pantry-shelf brown or sage-green accent, NOT terracotta near `#D97757`; freshness badges stay functionally green/amber/red/gray but hex may shift to harmonize).
   - What's unclear: Specific hex values — CONTEXT.md explicitly reserves this ("user approved the *scope* and D-05..D-08's direction, not specific hex/px values").
   - Recommendation: CONTEXT.md's canonical_refs section directs re-invoking the `frontend-design` skill during planning/execution to derive final values via its two-pass process (design plan → review against brief → build), rather than this research agent proposing final hex values now.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None detected — `client/package.json` has no test runner, no `*.test.*`/`*.spec.*` files exist anywhere under `client/` `[VERIFIED: find command, this session — zero results]` |
| Config file | none — see Wave 0 |
| Quick run command | N/A — no framework installed |
| Full suite command | N/A — no framework installed |

### Phase Requirements → Test Map
No `REQUIREMENTS.md` IDs apply to this phase (board items use `DESIGN` in place of a requirement ID, per ROADMAP.md). Mapping instead to the phase's 5 Success Criteria (SC):

| SC ID | Behavior | Test Type | Automated Command | File Exists? |
|-------|----------|-----------|-------------------|-------------|
| SC-1 | Inventory view has clear visual grouping/spacing, usable at phone width | manual-only (visual) | N/A — resize browser / DevTools device toolbar to ≤599px width, confirm card layout renders, no horizontal scroll | ❌ Wave 0 — no visual regression tooling exists |
| SC-2 | Freshness badges use consistent, recognizable color coding | manual-only (visual) | N/A — visual inspection against the documented token palette in `05-DESIGN.md` | ❌ Wave 0 |
| SC-3 | `InventoryView`'s session-identity props documented at call site | manual-only (doc review) | N/A — confirm `App.js` has an inline comment/JSDoc referencing `05-DESIGN.md`, and `05-DESIGN.md` documents `householdId`/`userId`/`userName` | ❌ Wave 0 — no automated doc-presence check exists |
| SC-4 | Every presentational component's data-only prop contract documented | manual-only (doc review) | N/A — confirm JSDoc block exists above each of the 6 components' function signatures | ❌ Wave 0 |
| SC-5 | Shared style-token set exists and is documented | manual-only (doc review + visual) | N/A — confirm `:root` custom properties exist in `index.css` and are referenced in `05-DESIGN.md` | ❌ Wave 0 |

**Automated command note:** All 5 criteria are visual/documentation checks with no meaningful automated assertion available without adding new tooling (e.g., a visual-regression framework like Percy/Chromatic, or a JSDoc-linter). Given this is a small PoC and CONTEXT.md doesn't call for such tooling, the plan should treat this phase's verification as **manual UAT-driven**, consistent with `checkpoint:human-verify`-style gates rather than automated test assertions.

### Sampling Rate
- **Per task commit:** N/A — no automated quick-run command exists for this phase's domain (visual/doc changes)
- **Per wave merge:** Manual visual check at ≤599px and ≥600px viewport widths; manual doc-presence check against the 5 Success Criteria
- **Phase gate:** All 5 Success Criteria manually verified true before `/gsd-verify-work`

### Wave 0 Gaps
- No client-side test framework exists at all (no Jest/Vitest/Testing Library configured). Installing one is out of scope for this phase's locked decisions (D-01–D-08 don't call for test infrastructure) — flagging as a gap for awareness, not a blocker, since this phase's success criteria are inherently visual/documentation-based rather than logic-based.
- `.planning/phases/05-ui-design/05-DESIGN.md` does not yet exist — it is this phase's primary documentation deliverable per D-04, to be created during planning/execution, not by this research pass.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Phase does not touch auth; `App.js`'s hardcoded placeholder session values are explicitly documented as Track A's future concern, not this phase's to implement |
| V3 Session Management | No | Same as above — this phase only *documents* the existing session-identity prop contract, does not implement session handling |
| V4 Access Control | No | No access-control logic changes; `ItemActions`' reserve/consume/release calls and their authorization are unchanged |
| V5 Input Validation | No | No new user inputs introduced; `RestockForm`'s existing inputs (`type="date"`, `type="number" min="1"`) are unchanged by a styling pass |
| V6 Cryptography | No | Not applicable to this phase's scope |

**Rationale for near-universal "No":** This phase is a presentation-layer-only restructure (markup + CSS + doc comments) with explicit scope boundaries in CONTEXT.md: "No new inventory *behavior* is in scope — data fetching, mutation logic, and API contracts are untouched." There is no new attack surface. The one item worth a passing security-adjacent note: any markup restructure that changes how user-controlled data (`item.itemName`, `entry.userName`, etc.) is rendered should preserve React's default JSX-escaping behavior (no `dangerouslySetInnerHTML` introduced) — none of the current components use it `[VERIFIED: Project.js, FreshnessBadge.js, BatchList.js, RestockForm.js, Checkout.js — read this session, no dangerouslySetInnerHTML present]`, and the restructure should not introduce it.

### Known Threat Patterns for this stack
Not applicable — no new threat surface introduced by a CSS/markup-only restructure of already-reviewed components (Track B's code review already addressed a NoSQL-injection finding in the data layer, per STATE.md; this phase does not touch that layer).

## Project Constraints (from CLAUDE.md)

- Userid and password must be encrypted at rest/in transit (SR3) — not applicable to this phase's scope (no auth work).
- No hard-coded values anywhere in the app — this phase's session-identity prop *documentation* work directly supports auditing this later (SC-3/SC-4 make the "no hard-coded fallback" contract explicit and checkable by Track C), but does not itself remove `App.js`'s current placeholder `HOUSEHOLD_ID`/`USER_ID`/`USER_NAME` constants — that removal is Track A's job when session/auth lands.
- GSD Workflow Enforcement: file edits for this phase must go through `/gsd-execute-phase` once a plan exists — this research output feeds the planner, not direct implementation.
- Flask + MongoDB + React stack, matches existing scaffold — unaffected; this phase is client-CSS/markup only.

## Sources

### Primary (HIGH confidence)
- `client/src/components/Project.js`, `FreshnessBadge.js`, `BatchList.js`, `RestockForm.js`, `Checkout.js` — read directly, this session
- `client/src/App.js`, `client/src/App.css`, `client/src/index.css` — read directly, this session
- `client/package.json`, `client/vite.config.js`, `client/index.html` — read directly, this session
- `.planning/phases/05-ui-design/05-CONTEXT.md` — locked decisions D-01 through D-08
- `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/ROADMAP.md` (Phase 5 section) — read directly, this session
- Computed WCAG contrast ratios — calculated this session from `App.css`'s verbatim hex values

### Secondary (MEDIUM confidence)
- [penpot.app — The developer's guide to design tokens and CSS variables](https://penpot.app/blog/the-developers-guide-to-design-tokens-and-css-variables/)
- [reintech.io — Creating a responsive table with CSS](https://reintech.io/blog/creating-responsive-table-css)
- [codeburst.io — Undo Tables to Make Them Responsive](https://codeburst.io/undo-tables-to-make-them-responsive-5bf6c7510a9d)
- [schof.co — Writing JSDoc for React Components](https://schof.co/writing-jsdoc-for-react-components/)
- [inkoop.io — A Guide to using JSDoc for React.js](https://www.inkoop.io/blog/a-guide-to-js-docs-for-react-js/)

### Tertiary (LOW confidence)
None — all findings above are either directly verified against the codebase, computed this session, or drawn from official/widely-corroborated web references. No unverified WebSearch-only claims are load-bearing in this research.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; existing stack read directly from `package.json`
- Architecture: HIGH — patterns are native-browser, well-established techniques with no ecosystem churn; component structure read directly from source
- Pitfalls: HIGH — all four pitfalls derive from specific behaviors read directly in the current source (disclosure toggle, stopPropagation, exact px values, existing accessible-contrast palette), not speculation

**Research date:** 2026-09-24
**Valid until:** No practical expiry — this phase's techniques (CSS custom properties, media-query responsive tables, JSDoc) are stable, non-versioned browser/language features, not a fast-moving library surface. Re-check only if the client adopts a new build tool or styling dependency before this phase executes.
