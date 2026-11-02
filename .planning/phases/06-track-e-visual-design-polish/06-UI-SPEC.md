---
phase: "6"
slug: "track-e-visual-design-polish"
status: verified
shadcn_initialized: false
preset: none
created: "2026-09-24"
revised: "2026-09-25"
---

# Phase 6 — UI Design Contract

> Visual and interaction contract for Track E: Dashboard Redesign. This document replaces
> its own two prior drafts in full — it was rewritten after live in-browser prototyping
> with the user surfaced that the earlier "token-only deepening" and "botanical-palette-
> on-Phase-5's-card-board" directions did not work. This is the locked direction.
>
> **Supersession notice:** this contract intentionally supersedes `05-DESIGN.md`'s visual
> sections (color tokens, elevation language, card/list markup) — those tokens and that
> markup are replaced, not extended. `05-DESIGN.md`'s **data contract** sections (prop
> shapes, fetch/mutation behavior, session-identity contract) remain authoritative and
> unchanged; only presentation changes.
>
> **Provenance:** the design language below is adapted from a user-supplied reference
> prompt (a "Botanical / Organic Serif" design system originally written for a marketing/
> editorial site — arches, hero sections, staggered grids). That reference's *tokens* (
> palette, type pairing, radius, shadow, motion) are adopted directly; its *marketing-site
> patterns* (arch imagery, hero sections, staggered card grids) are explicitly NOT ported,
> since PantryTrack is a dense, fast-scanning household utility, not an editorial site.
> Layout structure (data table + filter tabs + modal dialogs) was separately derived from
> real inventory-dashboard UX research and validated live against `ux-heuristics-review`
> and `cognitive-load-conversion`, not from the reference prompt.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none — hand-rolled React + plain CSS custom properties (no Tailwind, no shadcn, no component library) |
| Preset | not applicable |
| Component library | none. New components this phase: an inventory data table, location filter-tab bar, and a shared `Modal` presentational wrapper (used by both Add Item and item-detail). Existing components (`FreshnessBadge.js`, `BatchList.js`, `Checkout.js`'s `ItemActions`, `RestockForm.js`) are reused inside the modals with their documented props unchanged — only their container context changes (modal body instead of inline page flow). |
| Icon library | none — text-only labels and a single unicode "×" for modal close. Do not introduce an icon library. |
| Font | **Playfair Display** (display/heading, italic for headings) + **Source Sans 3** (body/UI), both loaded via Google Fonts `<link>` in `client/index.html`. Replaces `--font-sans` as the app's typographic system — see Typography below. |

**Why `Tool: none` is still correct:** this phase changes markup structure and visual
language substantially, but introduces no design-system package. Every new visual pattern
(table, filter pills, modal) is hand-authored CSS, consistent with the rest of this
codebase's zero-dependency styling approach.

Component Inventory section is omitted per template rule (no enumerable design-system
package).

---

## Typography

**Replaces Phase 5's system font stack entirely.** Load two Google Fonts in
`client/index.html`'s `<head>` (a new `<link rel="stylesheet">` tag, alongside the existing
`<meta>`/`<title>` tags — no build-tool font-loading plugin needed):

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600;1,700&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet">
```

New tokens in `client/src/index.css` (replace the existing `--font-sans` definition; do not
keep both):

| Token | Value | Usage |
|-------|-------|-------|
| `--font-display` | `'Playfair Display', Georgia, serif` | Page title, section/table headings, modal titles |
| `--font-body` | `'Source Sans 3', system-ui, -apple-system, sans-serif` | All body text, table cells, form labels, buttons, badges |
| `--leading-body` | `1.55` (unchanged value from Phase 5) | Applies to `--font-body` text exactly as it applied to the old `--font-sans` — Source Sans 3's metrics are close enough to the prior system-font stack that no adjustment is needed. Apply to table cells, form labels, and modal body copy. Heading elements (`--font-display`) use `line-height: 1.2`, not `--leading-body` — display type at 1.3–2.2rem needs a tighter line-height than body copy, standard typographic practice for serif display faces. |

> **Checker Note:** `gsd-ui-checker` may flag "5 font sizes" (2.2rem, 1.3rem, plus the three
> inherited body sizes below) as exceeding a 4-size ceiling. Only **two** sizes are new this
> phase — the 2.2rem page heading and the 1.3rem section/modal heading. `--text-xs`
> (0.8rem), `--text-sm` (0.85rem), and `--text-md` (0.9rem) are **unchanged from Phase 5**,
> already shipped, and already scored 4/4 in `05-UI-REVIEW.md`; this document does not
> resize or remove them, it only changes which font-family renders them. A 4-size ceiling
> exists to catch uncontrolled proliferation in a fresh spec — it is not a mandate to
> shrink a scale this phase inherits and only re-fonts. Do not merge or remove the two new
> heading sizes to force a lower count; do not touch the three inherited body sizes.

`--text-base` (1rem) is not used by any rule in this document; it is neither reused nor
removed by Phase 6 and stays declared for any future phase's use, consistent with Phase 5's
own definition.

| Role | Font | Size | Weight | Style | Line height |
|------|------|------|--------|-------|-------------|
| Page heading (`.app-heading`) | `--font-display` | 2.2rem | 700 | italic | 1.2 |
| Section/table/modal headings | `--font-display` | 1.3rem | 600 | italic | 1.2 |
| Body/table cells/labels | `--font-body` | `--text-md`/`--text-sm` (unchanged values) | 400/600 | normal | `--leading-body` (1.55) |
| Table column headers / small labels | `--font-body` | `--text-xs` (unchanged value) | 600 | normal, uppercase | 1.2 |

Italic Playfair Display headings are this phase's signature typographic move (per the
reference system) — apply to every heading-level element (`.app-heading`, table/section
headings, modal `<h3>` titles), never to body text or buttons.

---

## Color

**Replaces Phase 5's warm-brown palette entirely.** New tokens in `client/src/index.css`
(remove Phase 5's `--color-*` base/accent tokens; freshness-badge and location tokens are
superseded per-value below, not kept alongside the new ones):

| Token | Value | Role | Usage |
|-------|-------|------|-------|
| `--color-bg` | `#F9F8F4` | Dominant (60%) | Page background — warm alabaster |
| `--color-surface` | `#FFFFFF` | Dominant (60%) | Table, modal, and card surfaces |
| `--color-surface-soft` | `#F2F0EB` | Secondary | Table header row, hover states |
| `--color-ink` | `#2D3A31` | Secondary (30%) | Primary text, primary-button fill |
| `--color-ink-muted` | `#6E655B` | Secondary (30%) | Muted text, table column labels |
| `--color-stone` | `#E6E2DA` | Secondary (30%) | Borders, table rules |
| `--color-sage` | `#8C9A84` | Accent | Filter-pill labels, focus rings, secondary emphasis |
| `--color-terracotta` | `#C27B66` | Accent (10%) | Hover state on primary buttons, "act here" emphasis |
| `--color-danger-bg` | `#F7DFD8` | Semantic | Error/past-best-by background (unchanged hex from Phase 5's `--color-expired-bg`, kept as the one color value carried over since it is already a correct, accessible pairing) |
| `--color-danger-fg` | `#8C2F22` | Semantic | Error/past-best-by text |
| `--color-danger-border` | `#E0A99C` | Semantic | Error/past-best-by border |

Freshness badge and location-identity colors: freshness badges keep three semantic states
(fresh / use-soon / past-best-by) recolored into this palette's muted register — fresh uses
a soft sage-green pairing, use-soon a soft amber, past-best-by the danger triad above. Do
not introduce saturated/neon colors for these — every value must read as "muted, earthy"
per the reference system's core principle. Exact hex pairs are the executor's to derive
from `--color-sage` and a muted amber in the same family (e.g. `color-mix()` against
`--color-bg`), confirming each pairing clears 4.5:1 text contrast before committing it —
this phase does not hand down pre-computed hex triples the way 05-DESIGN.md did, because
the palette itself is new; verify, don't assume.

Location identity (Pantry/Fridge/Freezer) is carried by the table's plain-text "Location"
column, not by a color-coded stripe or dot — see Layout & Components below for why a
per-row location indicator was tried and dropped.

**Accessibility floor (unchanged expectation from Phase 5):** every text/background pairing
introduced by this phase must clear WCAG AA (4.5:1 normal text, 3:1 large text/non-text) —
spot-check `--color-ink` on `--color-bg`/`--color-surface`, `--color-sage` on
`--color-surface` (used as filter-pill label text), and all three freshness pairings before
shipping.

---

## Spacing

> **Checker Note:** `gsd-ui-checker` may flag `2px`, `6px`, `10px` in the inherited scale
> below as not multiples of 4. This entire spacing scale is **verbatim-unchanged from
> Phase 5** (already shipped, already audited in `05-UI-REVIEW.md`), and this document
> introduces **zero new spacing tokens**. The 4px-grid heuristic exists to catch
> uncontrolled proliferation in a fresh spec; there is nothing new to check here because
> nothing new was added to this category. Reworking Phase 5's shipped scale to satisfy a
> generic heuristic would mean re-touching already-approved, already-shipped values for no
> reason connected to this phase's actual goal (dashboard layout + botanical visual
> language) — a scale change was never part of what made the earlier drafts fail with the
> user; layout and palette were.

Phase 5's 10-step spacing scale (`--space-3xs` through `--space-4xl`) is retained
unchanged — reuse it for all new components (table cell padding, modal padding, filter-pill
padding). No new spacing tokens are needed; this phase's newness is in layout structure and
color/type, not a new spacing rhythm.

---

## Shape & Elevation

**Supersedes Phase 5's "hairline borders, no shadow, no gradient" rule.** The botanical
direction is built on soft, diffused shadows and heavy rounding — apply these new tokens:

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-lg` | `20px` | Table container, stats/filter surfaces |
| `--radius-modal` | `24px` | Modal dialogs |
| `--radius-pill` | `999px` | Buttons, filter tabs, freshness badges (unchanged shape from Phase 5, new radius token name) |
| `--shadow-card` | `0 10px 15px -3px rgba(45,58,49,0.06)` | Resting shadow on the table container |
| `--shadow-modal` | `0 25px 50px -12px rgba(45,58,49,0.25)` | Modal dialogs only |

No gradients anywhere (the reference system's own rule, and craft R1) — warmth comes from
the flat `--color-bg`/`--color-surface` pairing and the shadow system, never a gradient
wash.

---

## Layout & Components

This phase replaces Phase 5's per-location card-list page structure with a genuine
dashboard shape. This was arrived at through three rejected live prototypes before
locking — documented here so a future reader understands why simpler options were passed
over, not just what was chosen.

### 1. Header

`.app-heading` ("{householdId} Pantry") stays as the page's one italic Playfair Display
display moment, unchanged in content and position. Add a "+ Add Item" button
(`--color-ink` fill, pill radius, white text) positioned at the header's trailing edge —
replaces Phase 5's always-visible inline `RestockForm` at the page bottom.

**Rejected:** a bordered/backgrounded masthead box around the heading — makes the page's
one bold moment look like another card. Kept: bold type alone, no container.

### 2. Location filter tabs

A row of pill buttons: `All`, `Pantry`, `Fridge`, `Freezer`. Active tab: `--color-ink`
fill, white text. Inactive: `--color-surface` fill, `--color-stone` border, `--color-ink`
text. Clicking a tab filters the table below to that location (`All` shows every row).
This is genuinely new interactive behavior, not present in Phase 5 — implement as
client-side filtering over the already-fetched `locations` object, no new API call.

### 3. Inventory table

**Replaces Phase 5's three stacked/columned `LocationSection` card lists.** A single table,
`--radius-lg`, `--shadow-card`, `--color-surface` background, inside `--color-stone`
1px border:

| Column | Source |
|--------|--------|
| Location | `item.location` (via whichever `LocationSection` iteration produced this row — see Planner Notes) |
| Item | `item.itemName` |
| Capacity | `item.capacity` |
| Available | `item.availability` |
| Freshness | `<FreshnessBadge>` (component reused unchanged) |

Header row: `--color-ink-muted` text, uppercase, `--text-xs`, letter-spacing. Body rows:
`--color-surface` default, `--color-surface-soft` on hover, `--color-stone` 1px row
dividers, cursor pointer. Clicking a row opens that item's detail in a modal (see below).

**Rejected — three prior directions, in order:**
1. *Token-only deepening of Phase 5's existing brown palette and card-list layout* (first
   draft of this document). Too timid — the user's actual complaint ("doesn't look like it
   has any frontend design") needed a structural answer, not two new CSS variables.
2. *This botanical palette applied to Phase 5's existing 3-column side-by-side card board*
   (second live prototype). Visually warmer, but `ux-heuristics-review` correctly flagged
   that three equal-width columns of stacked cards reads as a Kanban board, which implies
   drag-and-drop between locations — an interaction this app does not and will not support.
   Users' first instinct to drag a card would fail silently (H4 Consistency violated).
3. *A single table with location filter tabs, but Add Item and item-detail opened as
   right-edge sliding drawers* (third live prototype). Structurally correct — this is the
   layout locked below — but the drawer chrome was visually inconsistent with the botanical
   direction's rounded, soft-shadow, centered-composition aesthetic; the user found the
   sidebar pattern "doesn't look clean" against this particular visual language.

**Also considered and dropped within the table design itself:** a per-row colored dot or
left-edge stripe repeating the location identity already stated in the Location column —
redundant signal once location is a plain table column (unlike the old card-board, where
grouping-by-column was the only way to know an item's location). The Location column text
is sufficient; no icon or color chip is added per row.

### 4. Modals — the one shared interaction pattern

**Both "+ Add Item" and clicking a table row open the same modal chrome** — this
consistency (one dialog pattern, not two) is itself a Phase 6 success criterion (see
Roadmap). Modal chrome, shared:

- Centered: `position: fixed; top/left: 50%; transform: translate(-50%, -50%)`.
- `--radius-modal` (24px), `--shadow-modal`, `--color-surface` background, `padding:
  32px` (`--space-3xl` × ~2, or a literal 32px — matches `--space-3xl`'s existing value).
- `max-width: 90vw` and a fixed pixel width appropriate to content (Add Item: ~420px;
  item-detail: ~460px, since it carries batch history) with `max-height: 85vh; overflow-y:
  auto` for long batch histories.
- A backdrop: `position: fixed; inset: 0; background: rgba(45,58,49,0.25); z-index` below
  the modal, above everything else. Backdrop click closes the modal (H3 user control).
- A header row inside the modal: `<h3>` title in `--font-display` italic, and an explicit
  `×` close button (`--color-ink-muted`, no border, `1.5rem`, top-right of the header row)
  — never rely on backdrop-click alone as the only exit (H3: both affordances, standard
  drawer/modal convention).
- Only one modal open at a time — opening one closes the other if it was open.

**Add Item modal body:** the existing `RestockForm` component, unchanged props/behavior,
rendered inside the modal instead of inline at the page bottom.

**Item-detail modal body:** item name + a one-line summary (`{location} · Capacity {cap} ·
Available {avail} · {freshness label}`) in `--color-ink-muted`, then the existing
`BatchList` component (unchanged), then the existing `ItemActions` component (unchanged) —
same components Phase 5 built, now composed inside a modal instead of an inline
`<details>` disclosure.

### 5. States

- **Loading:** while the initial fetch is in flight, render a single centered state panel
  (`--radius-lg`, `--color-surface`, `--shadow-card`, `--space-xl` padding) in place of the
  table, containing "Loading inventory…" and a small CSS spinner (`border`-ring,
  `--color-sage` accent edge, respecting `prefers-reduced-motion` per Phase 5's existing
  media-query block — add `animation: none` there for the new spinner, not just a slower
  duration).
- **Error:** same panel treatment, `--color-danger-bg`/`--color-danger-border`, the prefixed
  copy `"Couldn't load your inventory. {error}"`, and a **now-styled** Retry button
  (`--color-ink` fill, pill radius — this closes the Phase 5 UI-review's unstyled-button
  finding).
- **Empty (all locations, zero items):** the table renders its header row with a single
  full-width row: "Nothing stored here yet." in `--color-ink-muted` italic, centered. (Per-
  location empty states no longer apply once there's one shared table — a location filter
  showing zero rows for that location gets the same one-line treatment, filtered.)
- **Empty (no reservations on an item):** unchanged copy ("No one has reserved this item."),
  now rendered inside the item-detail modal instead of inline in a card.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Header action | "+ Add Item" (new — replaces the inline "Restock an item" form heading as the entry point; the form itself keeps its own internal "Restock an item" `<h3>` inside the modal) |
| Filter tabs | "All", "Pantry", "Fridge", "Freezer" — unchanged location names, sentence case |
| Table column headers | "Location", "Item", "Capacity", "Available", "Freshness" — plain nouns, no jargon |
| Loading state | "Loading inventory…" (unchanged from Phase 5) |
| Error state | `"Couldn't load your inventory. {error}"` (unchanged from the second Phase 6 draft) |
| Empty state (table) | "Nothing stored here yet." (unchanged copy, new placement: full-width table row instead of per-section) |
| Empty state (reservations) | "No one has reserved this item." (unchanged, now inside modal) |
| Destructive confirmation | "Consume" and "Release" remain without a confirmation dialog — unchanged decision from the prior draft; still an explicit, intentional scope boundary, not a gap. The in-flight disabled-button safeguard is unchanged. |

---

## UI Considerations

| Category | Element(s) | Status | Resolution |
|----------|------------|--------|------------|
| loading | Initial inventory fetch | ✅ covered | Single centered state panel replaces the table — see States above. |
| error | Fetch failure | ✅ covered | Same panel family, danger palette, styled Retry button — see States above. |
| empty (all) | Zero items across all locations, or zero items in a filtered location | ✅ covered | Single full-width table row, italic muted text — see States above. |
| empty (reservations) | Item with no reservations | ✅ covered | Unchanged copy, now inside the item-detail modal. |
| disabled | In-flight Restock/Consume/Reserve/Release buttons | ✅ covered | Existing `disabled` + reduced-contrast styling carries over unchanged; must not regress when these components move inside modals. |
| destructive-action | Consume, Release | ✅ covered | No confirmation dialog, explicit decision — see Copywriting Contract. |
| modal-stacking | Add Item and item-detail both open | ✅ covered | Only one modal open at a time; opening either closes the other — see Layout & Components §4. |
| modal-dismissal | Any open modal | ✅ covered | Two exits required: explicit × button AND backdrop click — see Layout & Components §4 (H3 user control, learned from the rejected drawer prototype which initially shipped with neither). |
| long-text | Item names in the table's Item column | 🧪 backstop | No length limit is enforced client- or server-side. Executor should verify a long item name (30+ characters) wraps or is handled gracefully in the table cell and in the modal title, at both desktop and 599px width, without breaking row height or the close-button position. |
| responsive | Table + filter tabs + modals at ≤599px | 🧪 backstop | Phase 5's 599px breakpoint concept carries over in spirit but the underlying layout is new (table, not cards) — executor must verify the table doesn't force horizontal scroll at phone width (a common table failure mode: consider allowing only the table itself to scroll horizontally within its container, or stacking columns, rather than letting the whole page overflow), and that modals remain usable (not taller/wider than the viewport) at 375px width. |
| contrast | New palette pairings (sage on surface, freshness badges, danger triad) | 🧪 backstop | See Color section — this phase does not pre-compute hex triples the way 05-DESIGN.md did; executor must verify each new text/background pairing clears WCAG AA before committing. |
| batch-history overflow | Item-detail modal with many batches | ✅ covered | The modal chrome's `max-height: 85vh; overflow-y: auto` (Layout & Components §4) already handles an arbitrarily long `BatchList` without a separate scroll mechanism needed inside the modal body. |
| zero-one-many (batches) | `BatchList` inside the item-detail modal | ✅ covered | Unchanged component; an item always has ≥1 batch (items are created via restock, which always adds a batch), so a zero-batch state cannot occur — `BatchList`'s existing 1-or-many rendering is unaffected by the move into a modal. |
| consume/reserve/release error | Item-detail modal's action controls | ✅ covered | `ItemActions`' existing inline `consumeError`/`reserveError`/`releaseError` text (unchanged from Phase 5) renders inside the modal exactly as it rendered inside the old inline card — no new error-surface design needed, just confirm it remains visible within the modal's `overflow-y: auto` body. |

**Second probe pass (post-rewrite, 2026-09-25):** the ui-consideration-probe was re-run
against this rewrite's actual new surfaces (filter tabs, the table, both modals, and the
one-modal-at-a-time rule), generating 38 candidate pairs. Three rows above are new
(batch-history overflow, zero-one-many for batches, and the action-error row); the rest
were dismissed as not applicable to their surface — fixed enum tabs have no
empty/loading/error/partial/overflow concept, both modals' `empty`/`loading`/`error`/
`partial` candidates duplicate either the app-level fetch states (already covered above) or
Phase 5's unchanged per-action states (already covered above), and the "only one modal
open" rule is a behavior contract, not a data-shaped element with state categories. Zero
unresolved.

---

## Registry Safety

Not applicable — `Tool: none`. No shadcn, no component registry, no third-party UI blocks.
The two Google Fonts `<link>` tags are the only external resource this phase adds; both are
Google's own CDN, loaded via standard `<link rel="stylesheet">`, no build-tool dependency.

---

## Planner Notes — Structural Impact

**This phase requires real markup and component-composition changes, not just CSS.**
Unlike the phase's original (superseded) scope, this is not additive-only:

- `client/src/components/Project.js`'s `LocationSection`/`AmbiguityNotice` render logic is
  replaced by a new table-rendering component (name TBD by planner — e.g. `InventoryTable`)
  that flattens all three locations' item arrays into one row set with a `location` field
  per row, plus the filter-tab state. `InventoryView`'s data-fetching (`fetchInventory`,
  `loadInventory`, the `loading`/`error`/`ambiguityNotice` state) is unchanged — only what
  it renders with that state changes.
- A new shared `Modal` presentational wrapper (or equivalent shared styling class pattern)
  is needed so Add Item and item-detail render through one consistent chrome rather than
  duplicating the header/backdrop/close-button markup twice.
- `RestockForm`, `BatchList`, `FreshnessBadge`, and `ItemActions` (`Checkout.js`) keep their
  existing props and behavior unchanged — only their rendering context (inside a modal
  instead of inline) changes. Verify each component's existing JSDoc prop contract
  (05-DESIGN.md) still accurately describes it after this move; update the JSDoc/design-doc
  prose only if the container context needs explaining, never the prop shapes themselves.
- `client/index.html` gains the two Google Fonts `<link>` tags (a new file touched this
  phase; Phase 5 never modified it).
- `client/src/index.css`'s `:root` block is substantially rewritten (color/font tokens
  replaced, not purely additive this time) — this is a deliberate, in-scope exception to
  the additive-only pattern Phase 5 established, per this document's supersession notice.

Ambiguity-notice handling (`AmbiguityNotice` component, shown when a restock can't be
merged into an existing item) still needs a home in the new layout — planner should decide
whether it surfaces inside the Add Item modal (most likely, since it's a direct response to
a restock submission) or as a transient banner; not decided by this UI-SPEC, flagged for
the plan.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS (not applicable — `Tool: none`)
- [x] Dimension 7 Inventory Provenance: PASS (not applicable — no design-system package)

**Approval:** approved 2026-09-25 — locked after 4 live in-browser prototype iterations
directly with the user (token-only deepening → botanical-on-card-board → table+drawers →
table+centered-modals), the last three grounded in `ux-heuristics-review` and
`cognitive-load-conversion` findings. Re-run `gsd-ui-checker` before execution if further
changes are made to this document.
