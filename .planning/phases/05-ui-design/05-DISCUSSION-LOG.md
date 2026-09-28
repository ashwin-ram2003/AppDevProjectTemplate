# Phase 5: UI Design - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-24
**Phase:** 5-ui-design
**Areas discussed:** Mobile table strategy, Style token scope & values, Visual redesign depth, Contract documentation format, Visual identity direction

---

## Mobile table strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Stack into cards | Each item/batch row becomes a small card with labeled stacked fields below ~600px. Touches row-rendering markup, not just CSS. | ✓ |
| Horizontal scroll | Keep `<table>` markup as-is, wrap in `overflow-x:auto` below the breakpoint. | |
| Collapse to fewer columns | Hide less-critical columns via CSS at narrow widths. | |

**User's choice:** Stack into cards.
**Notes:** Recommended option; accepted without further discussion.

---

## Style token scope & values

| Option | Description | Selected |
|--------|-------------|----------|
| Color + spacing | Custom properties for freshness palette + a small spacing scale. | |
| Color only | Just formalize the freshness/status color palette. | |
| Full system (color, spacing, typography, radius) | Also standardize font sizes, border-radius, shadow values. | ✓ |

**User's choice:** Full system.
**Notes:** User opted for the more complete token system over the "recommended" narrower option.

---

## Visual redesign depth

| Option | Description | Selected |
|--------|-------------|----------|
| Restructure render markup as needed | Rework row/table JSX into card-friendly structure since cards were chosen for mobile. | ✓ |
| CSS-only, keep markup | Keep `<table>`/`<tr>` markup, fake card look with CSS. | |

**User's choice:** Restructure render markup as needed.
**Notes:** Follows directly from the mobile card-layout decision — CSS alone can't turn a table into a real card layout.

---

## Contract documentation format

| Option | Description | Selected |
|--------|-------------|----------|
| Both: DESIGN.md + JSDoc | Canonical DESIGN.md plus JSDoc comments above each component signature. | ✓ |
| DESIGN.md only | Single canonical markdown doc. | |
| JSDoc only | Documented directly above each component's signature. | |

**User's choice:** Both: DESIGN.md + JSDoc.
**Notes:** Recommended option; accepted.

---

## Visual identity direction (frontend-design skill applied)

| Option | Description | Selected |
|--------|-------------|----------|
| Warm domestic/kitchen | Butter/parchment neutrals, pantry-shelf brown or sage-green accent (not terracotta), flat/low-shadow shelf-card look with colored left-edge stripe per location, one humanist sans typeface. | ✓ |
| Cool utilitarian/inventory-system | Slate/graphite neutrals with a functional blue/teal accent, monospace data accents, denser layout. | |
| Minimal, let structure carry it | Near-white/near-black neutrals only, no added accent beyond functional freshness badges. | |

**User's choice:** Warm domestic/kitchen.
**Notes:** Applied the `frontend-design` skill's guidance to avoid generic AI-template tells (warm-cream+terracotta, SaaS-card-kit identical-shadow cards) by grounding the palette/layout in the household kitchen/pantry subject matter instead.

---

## Claude's Discretion

- Exact breakpoint value (~600px suggested during discussion; may be tuned during implementation).
- Exact token names/values within the agreed categories (color/spacing/typography/radius) and within the warm-kitchen direction.
- Whether `Checkout.js`/`ItemActions` needs markup changes beyond what the card restructure forces.
- Specific humanist sans-serif typeface choice (system stack vs. a specific webfont).

## Deferred Ideas

None — discussion stayed within phase scope.
