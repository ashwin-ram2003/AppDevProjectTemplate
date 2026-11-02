# Phase 5: UI Design - Context

**Gathered:** 2026-09-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Track E (Aaron's dual duty alongside Track B) delivers visual/UX polish and a documented component contract over Track B's already-built inventory UI (`InventoryView`/`Project.js`, `RestockForm`, `FreshnessBadge`, `BatchList`, `Checkout`/`ItemActions`): clear visual grouping and phone-width usability for the inventory view, consistent freshness-badge color coding, a documented session-identity prop contract at `InventoryView`'s call site, documented data-only prop contracts for every presentational component, and a small shared style-token set — satisfying this phase's 5 success criteria (`DESIGN` board items, no REQUIREMENTS.md ID). No new inventory *behavior* is in scope — data fetching, mutation logic, and API contracts are untouched.

</domain>

<decisions>
## Implementation Decisions

### Mobile layout
- **D-01:** Below a phone-width breakpoint (~600px), the item table and the nested batch table both switch to a stacked-card layout — one card per item/batch with labeled fields stacked vertically, rather than horizontal scroll or column-hiding. — **Reversibility:** reversible — a later redesign can swap card CSS/markup back to a table without touching data flow.
- **D-02:** Achieving the card layout requires restructuring the render markup in `Project.js` (`LocationSection`/row rendering) and `BatchList.js` — the `<table><tr>` structure cannot become a real card layout via CSS alone. `Checkout.js`/`ItemActions` markup may also need adjustment where it renders inline with the table row. Data-fetching, event handlers, and props stay untouched — this is a presentation-layer restructure only.

### Style tokens
- **D-03:** The shared token set is a full system: color (including the existing freshness palette — fresh/expiring_soon/expired/unknown — currently hardcoded hex in `App.css`), spacing scale (replacing the ad-hoc 8/16/24/32px values scattered through selectors), typography (font sizes/weights in use), and border-radius. Implemented as CSS custom properties (e.g. `--color-fresh`, `--space-sm`, `--radius-md`) so Track A and Track C's own UI work can adopt the same values instead of re-inventing them.

### Documentation
- **D-04:** Component prop-contract documentation lives in two places: a canonical `DESIGN.md` (in the phase directory) listing every presentational component's data-only prop contract plus `InventoryView`'s session-identity props (`householdId`, `userId`, `userName`) documented at its call site — this is what Track A/Track C read before wiring in their own UI or auditing DATA-01/DATA-03 — AND short JSDoc comments directly above each component's function signature in the source files, so the contract stays visible to anyone editing the component without needing to remember to check `DESIGN.md`.

### Visual identity (frontend-design skill applied)
- **D-05:** Design direction is **warm domestic/kitchen**, chosen explicitly to avoid the generic AI-template look (warm-cream+terracotta, or SaaS-card-kit identical-rounded-shadow cards) that `frontend-design` skill guidance flags as a tell. Palette grounded in real kitchen materials — butter/parchment neutrals, a deep pantry-shelf brown or sage-green accent (NOT terracotta near #D97757 — explicitly flagged as an overused AI-generated tell). Surfaces read as soft/paper-like, not glossy SaaS panels.
- **D-06:** Item/batch cards (from D-01/D-02's mobile restructure) read as labeled shelf/bin cards, not SaaS dashboard tiles: flat or minimal shadow, a colored left-edge stripe per location (Pantry/Fridge/Freezer) rather than identical rounded boxes with the same grey shadow on every card.
- **D-07:** One clean humanist sans-serif typeface for both UI labels and data (item names, quantities, dates) — this is a utility tool, not an editorial piece, so no separate display/body typeface pairing is needed. Avoid the generic tracked-out ALL-CAPS eyebrow-label pattern and mid-dot-joined meta strings the skill flags as template chrome.
- **D-08:** The existing freshness badge palette (green/amber/red/gray, D-03) stays functionally as-is — it is already accessible-contrast and not part of the "generic AI palette" problem — but its exact hex values may be adjusted to sit harmoniously against the new warm-kitchen base palette rather than the current cool-neutral (`#f8f9fa`) background.

### Claude's Discretion
- Exact breakpoint value (~600px suggested by the user during discussion; planner/executor may tune based on actual phone-width testing).
- Exact token names/values within the agreed categories (color/spacing/typography/radius) — user approved the *scope* and D-05..D-08's direction, not specific hex/px values.
- Whether `Checkout.js`/`ItemActions` needs markup changes beyond what the card restructure forces — determined during implementation.
- Specific humanist sans-serif typeface choice (e.g. system font stack vs. a specific webfont) — deliberate but not user-specified.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & rubric mapping
- `.planning/ROADMAP.md` §"Phase 5 (Track E): UI Design" — Goal, Depends on, Success Criteria (this phase's roadmap entry)
- `.planning/PROJECT.md` §Key Decisions — records Track B's prior UI/schema decisions this phase builds on top of

### Source of truth for existing UI (this phase's starting point)
- `client/src/components/Project.js` — `InventoryView` (default export), `LocationSection`, `AmbiguityNotice` — the component whose session-identity props (`householdId`, `userId`, `userName`) must be documented at its call site
- `client/src/components/FreshnessBadge.js` — existing location-aware label/title logic; do NOT change its freshness-computation behavior, only its visual styling and prop documentation
- `client/src/components/BatchList.js` — batch table; ordering contract in its own doc comment ("batches MUST be rendered in the order received") must be preserved through any markup restructure
- `client/src/components/RestockForm.js` — form component, in scope for token/spacing polish
- `client/src/components/Checkout.js` — exports `ItemActions`, renders reservation/consume UI inline per item row
- `client/src/App.css` — all current hardcoded colors/spacing to be replaced with tokens; `client/src/index.css` — root font/color already set, tokens should compose with it not duplicate it

### Prior track decisions this phase must respect
- `.planning/phases/02-inventory-management/02-CONTEXT.md` — D-09/D-10/D-11 (location-specific freshness rules) and the "reserve is dibs, not a hold" framing (D-04/D-05) — freshness badge color-coding and any UI copy changes must stay consistent with this framing, not contradict it

### Design methodology
- `frontend-design` skill (Claude Code plugin, `frontend-design:frontend-design`) — applied during this discussion to derive D-05..D-08's visual direction and avoid generic AI-template tells. The planner/executor should re-invoke this skill when producing the actual token values and component markup, following its two-pass process (design plan → review against brief → build) rather than treating D-05..D-08 as the finished token values.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `FreshnessBadge`'s existing `freshness-badge--{fresh|expiring_soon|expired|unknown}` CSS class naming convention — extend this pattern for token variable naming rather than inventing a new naming scheme.
- `App.css`'s existing freshness palette (`#dcfce7`/`#166534` green, `#fef3c7`/`#92400e` amber, `#fee2e2`/`#991b1b` red, `#f3f4f6`/`#374151` gray) is already a reasonable, accessible-contrast palette — tokenize these values rather than redesigning the palette from scratch.

### Established Patterns
- `client/src/components/` has no CSS Modules or styled-components — all styling is global classes in `App.css`/`index.css`. Token implementation should follow this existing convention (CSS custom properties in `:root`, likely in `index.css`), not introduce a new styling paradigm.
- No `@media` queries exist anywhere in the client yet — this phase introduces the project's first responsive breakpoint.
- Current markup nests item rows in a single `<table>` with `<details>` disclosure per item (`item-disclosure`/`item-summary`) containing the batch table and item actions. The card restructure needs to preserve the expand/collapse (disclosure) behavior in whatever new markup replaces the table row.

### Integration Points
- `InventoryView` (`Project.js`) is the component Track A will call with real `householdId`/`userId`/`userName` once its own session/auth work lands — this is the exact call site the session-identity prop contract documents.
- Every component in `client/src/components/` is presentational + data-fetching only (no hard-coded fallback data) — Track C will audit DATA-01/DATA-03 against the documented prop contracts.

</code_context>

<specifics>
## Specific Ideas

- User confirmed the freshness badge existing hex palette is a good starting point to tokenize rather than redesign.
- User explicitly chose to allow markup restructuring (not CSS-only) once cards were chosen for mobile — recognizing a `<table>` cannot become a real card layout with CSS alone.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 5-ui-design*
*Context gathered: 2026-09-24*
