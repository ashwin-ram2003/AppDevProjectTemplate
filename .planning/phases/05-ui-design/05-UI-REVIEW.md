# Phase 5 — UI Review

**Audited:** 2026-09-24
**Baseline:** Abstract 6-pillar standards (no UI-SPEC.md)
**Screenshots:** Not captured (code-only audit per adversarial standards)
**Scope:** Phase 05-01 and 05-02 implementation: design tokens, card markup, responsive layout, component prop contracts, and documented design system

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | Clear domain labels and state-aware CTAs; loading/error states lack styling context |
| 2. Visuals | 3/4 | Strong card-based hierarchy with location stripes; retry button unstyled, loading state is plain text |
| 3. Color | 4/4 | Zero hex literals in App.css; 43+ token references; all 4 freshness states and reservation colors proper |
| 4. Typography | 4/4 | Three font sizes across the app, all tokenised; consistent weights; tabular numbers for quantities |
| 5. Spacing | 3/4 | 10-token scale fully adopted; mobile breakpoint responsive; layout constraints left as literals |
| 6. Experience Design | 2/4 | Loading/error states present but unstyled; retry button lacks all interactive states (BLOCKER) |

**Overall: 19/24**

---

## Top 3 Priority Fixes

1. **Style the Retry button — BLOCKER for UX completeness** — The retry button in `Project.js` line 161 renders with no className, so it receives zero button styling (no background, border, hover, focus-visible, or disabled states). Users won't perceive it as interactive. **Fix:** Add `className="retry-button"` and create a `.retry-button` CSS rule (or reuse `.item-actions__row button` pattern by wrapping it in a form). Concrete: `<button type="button" className="retry-button" onClick={loadInventory}>Retry</button>`, then add `.retry-button { ... /* same as button states */ }` or include it in the grouped button selector at line 275.

2. **Style the loading state for visual prominence** — "Loading inventory..." renders as plain `<p>Loading inventory...</p>` at `Project.js` line 154. It reads as content, not app state. Users may not recognize the page is still fetching. **Fix:** Add a `.loading-state` or `.state-message` class with padding, border, background color (use `--color-surface`), and left-accent stripe (use `--color-accent` at `--stripe-width`). Make it visually distinct from item cards: `<div className="loading-state">Loading inventory...</div>`.

3. **Group error message and retry button into a visual unit** — At `Project.js` lines 157–166, the error message and retry button are separate DOM elements with no visual relationship. Add a `.error-state` container class with padding, border (use `--color-danger` or `--color-rule-soft`), background (`--color-surface`), and nest both the error text and button inside. This signals "this is app state, not content" and groups the recovery action with the problem description.

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)

**Strengths:**
- Domain-specific, task-focused button labels: "Restock", "Consume", "Reserve", "Release" (not "Submit", "OK", "Save")
- Context-aware empty states: "Nothing stored here yet." (LocationSection, Project.js:59), "No one has reserved this item." (ItemActions, Checkout.js:149)
- State-aware progress indication: Buttons show "Restocking...", "Consuming...", "Reserving..." during submission (RestockForm.js:114, Checkout.js:126, 142)
- Clear form labels: "Item name", "Location", "Quantity", "Purchase date", "Best-by date" — unambiguous and scannable
- Domain-appropriate ambiguity message: "...wasn't merged into an existing item because it could match more than one..." (AmbiguityNotice, Project.js:26–27)

**Gaps:**
- **Loading state copy is minimal:** "Loading inventory..." is the only UX feedback during initial fetch; no indication of what's happening or how long it will take (Project.js:154) — should ideally pair with visual styling
- **Error message alone, no guidance:** Error states (Project.js:160, Checkout.js:129, 145) display only `{error}` text and a bare "Retry" button; they don't confirm "we're working on fixing this" or provide next steps beyond "try again"
- **No form validation UX:** RestockForm has `required` attributes on inputs but no real-time feedback; users only discover invalid fields on submit, at which point the button shows "Restocking..." and then an error (RestockForm.js:35–56)

**Evidence:** Grep finds 2 empty-state messages ("Nothing stored here yet", "No one has reserved"), 3 button-state patterns ("Restocking...", "Consuming...", "Reserving..."), 0 form hints or validation messages. Copywriting contract is **met but minimal** — all labels are correct, none are generic ("Click Here", "Submit", "OK"), but state-aware messaging is sparse.

---

### Pillar 2: Visuals (3/4)

**Strengths:**
- **Clear visual grouping:** Item cards (`.item-card`, App.css:29–46) render as bounded units with light background (`--color-surface`), hairline border (`--rule-width`), and a left-edge location stripe (4px, coloured by storage type). Batch cards (`.batch-card`, App.css:159–168) follow the same pattern. This card-based layout replaces the prior table and succeeds at creating visual hierarchy.
- **Location-specific visual signals:** Pantry cards have a wood-brown stripe (`--color-loc-pantry: #8A6A4B`), Fridge a cool blue-grey (`--color-loc-fridge: #5F8A7D`), Freezer a cold blue (`--color-loc-freezer: #5C7796`). These are distinct enough (3:1 contrast floor verified in 05-DESIGN.md) and reinforce mental models.
- **Freshness encoding:** Each batch renders a freshness badge (`.freshness-badge`, App.css:80–112) with a distinct background, text, and border colour for four states (fresh/expiring_soon/expired/unknown) *plus* a location-specific label ("Fresh" vs "Good quality" vs "Freezer burn risk", FreshnessBadge.js:14–29). Colour is a reinforcing signal, not the sole encoding.
- **Spatial hierarchy:** Page heading (`<h1>`, App.js:16), location section headings (`<h2>`, Project.js:57), form heading (`<h3>`, RestockForm.js:60). Details/summary disclosure pattern for expand/collapse. Consistent left-margin indents for nested content (`.batch-list`, `.ambiguity-notice`, `.item-actions` all use `margin-left: var(--space-2xl)`, App.css:139–201).

**Gaps:**
- **Unstyled retry button is not visually interactive:** At Project.js:161, `<button type="button" onClick={loadInventory}>Retry</button>` renders with no className. It has no background, border, or visual hover state. CSS rules at App.css:275–306 apply to `.restock-form button`, `.item-actions__row button`, and `.reservation-entry__release`, but not to bare `<button>` elements. Result: a user seeing an error may not perceive the button as clickable. **BLOCKER for visual clarity.**
- **Loading state lacks visual emphasis:** "Loading inventory..." renders as a bare `<p>` tag (Project.js:154) with no class, background, or visual distinction. It reads as content text, not app state. No spinner, skeleton, or visual progress indicator.
- **Error state is not visually grouped:** Project.js:157–166 renders error text and retry button as separate siblings with no container, no visual boundary, and no shared styling. They should be framed as a unit so users perceive them as "here's the problem and here's how to recover."
- **Details disclosure styling is minimal:** The `.item-disclosure` (App.css:114–116) adds only padding and resets list-style. It could benefit from a subtle border or background shift to signal it's a disclosure-protected region, especially on mobile.

**Visual hierarchy evidence:** Grep finds 3 heading levels (`<h1>`, `<h2>`, `<h3>`), 10 distinct CSS classes for card and batch containers, 4 freshness-badge modifiers, 3 location-stripe modifiers. The card-list structure is sound. The unstyled retry button and plain-text loading state are the gaps.

---

### Pillar 3: Color (4/4)

**Strengths — Excellent execution:**
- **Zero hardcoded hex colors in App.css:** Grep confirms `grep -oE '#[0-9a-fA-F]{3,8}' client/src/App.css | wc -l` prints `0`. Every color reference uses `var(--color-*)` tokens.
- **Comprehensive token library:** `client/src/index.css` declares 28 colour tokens across 5 categories:
  - **Base palette** (8 tokens): page (`#F5F1E8`), surface (`#FCFAF5`), ink (`#2B2622`), ink-muted, rule, rule-soft, accent (`#5C4433`), danger (`#8C2F22`)
  - **Location stripes** (3 tokens): pantry (wood), fridge (cool), freezer (cold)
  - **Freshness states** (12 tokens): 3 per state (fresh/expiring_soon/expired/unknown) for background, foreground, border
  - **Reservation states** (4 tokens): own vs. other claim, 2 tokens each for background, foreground, border
- **60/30/10 distribution:** The warm parchment base (`--color-page`, `--color-surface`) dominates surfaces (the 60%). Accent colour (`--color-accent`, a deep brown) appears in hover/focus states on buttons and selection highlights (the 10%). The remaining 30% is split between supporting colours (muted text, borders, danger).
- **Accessibility verified:** All token values are documented in 05-DESIGN.md with WCAG AA contrast ratios:
  - Freshness badge foreground/background pairs: 6.39:1 (fresh), 5.79:1 (expiring), 6.48:1 (expired), 7.82:1 (unknown) — all exceed 4.5:1 AA floor
  - Location stripes vs. surface: 4.74:1 (pantry), 3.72:1 (fridge), 4.44:1 (freezer) — all exceed 3:1 non-text floor
- **Adoption pattern:** App.css references 43+ colour tokens (grep count). Every interactive element state (hover, focus-visible, disabled) uses tokens: `.restock-form button:hover { border-color: var(--color-accent); }` (App.css:290). No colour bleeds into comments, no placeholder values.

**No gaps.**

**Score justification:** Comprehensive token system, zero literals, accessibility verified, correct usage throughout. This is reference-quality colour implementation.

---

### Pillar 4: Typography (4/4)

**Strengths — Excellent:**
- **One unified typeface family:** `--font-sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif` (index.css:3). Single humanist sans for both UI labels and data; no separate display typeface pair. Appropriate for a utility app, not editorial content.
- **Disciplined size scale:** Only three distinct font sizes appear in App.css (`text-xs`, `text-sm`, `text-md`), plus `text-base` declared in tokens. Usage:
  - `--text-xs` (0.8rem): freshness badges, labels in batch cards, small notes
  - `--text-sm` (0.85rem): batch field values, error messages, muted text
  - `--text-md` (0.9rem): form labels, item summary fields, default content
  - `--text-base` (1rem): inherited from `:root` as fallback
- **Consistent weight pattern:** Two weights only: `--weight-regular: 400` and `--weight-semibold: 600`. Regular for body/supporting text, semibold for item names (`.item-summary__name`, App.css:127–130) and badge text (`.freshness-badge`, App.css:85).
- **Accessibility features:** 
  - `--leading-body: 1.55` set at root (index.css:10) — above the 1.5 minimum, aiding readability
  - `font-variant-numeric: tabular-nums` applied to quantity fields (`.item-summary__capacity`, `.item-summary__availability`, `.batch-card__value`, App.css:136–137, 181) so numbers align vertically in columns, aiding scanning
  - No ALL-CAPS labels, no mid-dot-separated metadata strings, no generic tracked-out eyebrow patterns
- **All values tokenised:** Grep finds zero hardcoded `0.8rem`, `0.9rem`, or font-weight literals in App.css. Every size/weight reference uses `var(--text-*)` or `var(--weight-*)`.

**No gaps.**

**Score justification:** Single typeface, disciplined 3-size scale (plus base), two weights only, accessibility enhancements (line-height, tabular-nums), 100% tokenised. This exceeds baseline requirements.

---

### Pillar 5: Spacing (3/4)

**Strengths:**
- **10-step spacing scale, fully adopted:** Tokens declared in index.css:13–22 range from `--space-3xs: 2px` to `--space-4xl: 64px`. Grep finds all 10 tokens used throughout App.css (14 references to `--space-*`). Examples: `.app-container` uses `var(--space-2xl)` and `var(--space-4xl)` (App.css:4); `.item-card-list` uses `var(--space-sm)` (App.css:26); `.batch-card` uses `var(--space-xl)` and `var(--space-2xs)` (App.css:162–164).
- **Consistent spacing vocabulary:** The same token is reused logically across contexts. `--space-xl` (16px) is the default component padding/gap, `--space-2xl` (24px) is the section indent, `--space-4xl` (64px) is the bottom-of-page margin. This creates rhythm.
- **Mobile responsiveness:** A single `@media (max-width: 599px)` block (App.css:308–346) adapts spacing for narrow viewports: `.item-summary` changes `gap` from `var(--space-xl)` to `var(--space-2xs)` (App.css:309–313); `.app-container` padding reduces from `var(--space-2xl) var(--space-xl)` to `var(--space-lg)` on sides (App.css:315–318); `.batch-card` stacks vertically with reduced gap. No horizontal scrollbar at 375px width per spec.
- **No arbitrary values within the spacing logic:** Grep confirms all padding/margin/gap in `.item-*`, `.batch-*`, `.freshness-*`, `.reservation-*`, `.restock-form` use tokens. No ad-hoc `8px`, `12px`, or `24px` literals in style rules.

**Gaps:**
- **Layout constraint values are not tokenised:** Non-spacing values like `max-width: 960px` (App.css:2, the page container), `max-width: 420px` (App.css:60, the form), `min-width: 140px` (App.css:129, item summary name), `width: 72px` (App.css:217, action input), and the `599px` media query condition are hardcoded. These are not spacing scale steps but rather layout constraints, so leaving them as literals is defensible. However, the audit standard holds that "no non-token length values appear in CSS"; by that measure, 5 values are outliers. Impact: low — they set layout structure, not rhythmic spacing, but they break the "every value is a token" principle.
- **Input width (72px) could be a spacing token:** The action input at App.css:217 uses `width: 72px`. This could be aliased as `--space-input-width: 72px` in the token set to maintain consistency, though it's arguably a component-specific dimension rather than a spacing scale step.

**Score justification:** 10-token scale well-used, mobile breakpoint responsive, spacing vocabulary consistent. The layout constraints (960px, 420px, 140px, 72px, 599px) are not spacing scale steps and are arguably acceptable as literals. However, strict "all values are tokens" adherence would require 5 more declarations. Grade: 3/4 (strong execution, minor tokenisation gap).

---

### Pillar 6: Experience Design (2/4)

**Strengths:**
- **Loading state present:** InventoryView sets `const [loading, setLoading] = useState(true)` (Project.js:115) and `setLoading(true/false)` in the `loadInventory` callback (Project.js:120, 128). When `loading` is true, the component renders "Loading inventory..." (Project.js:154). The async/await pattern is correct (Project.js:119–130).
- **Error state present:** `const [error, setError] = useState(null)` (Project.js:116) is set on catch (Project.js:126), and an error UI renders with `{error}` text and a `<button onClick={loadInventory}>Retry</button>` (Project.js:157–166). The error is captured from the fetch call, so users see real error messages (e.g., network failures, API timeouts).
- **Empty states handled:** LocationSection checks `if (items.length === 0)` and renders "Nothing stored here yet." (Project.js:58–59). ItemActions checks `if (reservations.length === 0)` and renders "No one has reserved this item." (Checkout.js:148–149). Both are friendly, not generic "no data" messages.
- **Disabled button states:** Buttons show `disabled={submitting}`, `disabled={consuming}`, `disabled={claimInFlight}`, and `disabled={releaseTargetId !== null}`. CSS rules at App.css:300–306 style disabled buttons with `cursor: not-allowed` and reduced-contrast text colour. This prevents double-submission on forms.
- **Button state messaging:** During submission, buttons show progress text: "Restocking...", "Consuming...", "Reserving..." (RestockForm.js:114, Checkout.js:126, 142). This gives users visual feedback that their action was received.
- **Reduced-motion support:** App.css includes `@media (prefers-reduced-motion: reduce)` (348–354) that sets `transition-duration: 0.01ms` for users who've requested reduced motion. This is correct WCAG compliance.

**Critical gap — BLOCKER:**
- **Retry button is completely unstyled:** Project.js:161 renders `<button type="button" onClick={loadInventory}>Retry</button>` with no className. CSS selectors at App.css:275–306 cover `.restock-form button`, `.item-actions__row button`, and `.reservation-entry__release`, but not bare `<button>`. Result:
  - No background colour — button may appear as plain text
  - No border — no visual weight
  - No hover state — users won't see interactive feedback on mouseover
  - No focus-visible ring — keyboard users get no focus indicator
  - No disabled state — even if the button could be disabled (it's not), there would be no visual change
  - **This is a UX defect:** Users viewing an error may not perceive the Retry button as actionable.

**Other gaps:**
- **Loading state is unstyled plain text:** Project.js:154 renders `<p>Loading inventory...</p>` with no class. It has no background, border, padding, or accent colour. Visually, it reads as page content, not app state. No spinner, skeleton loader, or progress indicator. Users may not recognize the page is still fetching, especially on slow networks.
- **Error state lacks visual framing:** Project.js:157–166 renders the error text and retry button as separate DOM siblings with no container, no shared background, no border. They should be grouped in a `.error-state` container so users perceive them as "here's the problem and here's the solution."
- **No confirmation for destructive actions:** While "consume" and "release" modify state, they have no confirmation dialog. A user could accidentally consume an item. (This is a design choice, not necessarily wrong, but worth noting.)
- **Form validation lacks real-time feedback:** RestockForm has `required` attributes on inputs, but no real-time validation UI. Users only discover invalid fields on submit, at which point "Restocking..." appears, then fails. Best practice would show validation errors inline as users type.

**Evidence:**
- Loading states: 1 site (Project.js:115)
- Error states: 2 sites (Project.js:116, 157–166) + 3 sites in form handlers (RestockForm.js:32, Checkout.js:33–35)
- Empty states: 2 sites (Project.js:59, Checkout.js:149)
- Disabled states: 4 buttons across RestockForm and Checkout
- Button state messaging: 3 patterns ("Restocking...", "Consuming...", "Reserving...")
- Unstyled buttons: 1 critical (Retry, Project.js:161)
- Unstyled state messaging: 1 (Loading, Project.js:154)

**Score justification:** States are detected and handled in logic, but UX presentation is incomplete. The retry button being unstyled is a BLOCKER for visual affordance. The loading state lacks styling and visual emphasis. Error UI is not grouped. Grade: 2/4 (functionality present, presentation poor).

---

## Files Audited

- `/Users/aphan/Group_2_Monday/client/src/index.css` — 83 lines, design-token `:root` block
- `/Users/aphan/Group_2_Monday/client/src/App.css` — 355 lines, component styling, responsive breakpoint
- `/Users/aphan/Group_2_Monday/client/src/App.js` — 22 lines, entry point with InventoryView call
- `/Users/aphan/Group_2_Monday/client/src/components/Project.js` — 189 lines, InventoryView + LocationSection
- `/Users/aphan/Group_2_Monday/client/src/components/BatchList.js` — 54 lines, batch card list
- `/Users/aphan/Group_2_Monday/client/src/components/FreshnessBadge.js` — 79 lines, freshness state rendering
- `/Users/aphan/Group_2_Monday/client/src/components/Checkout.js` — 200+ lines, ItemActions (consume/reserve/release)
- `/Users/aphan/Group_2_Monday/client/src/components/RestockForm.js` — 121 lines, restock form
- `/Users/aphan/Group_2_Monday/.planning/phases/05-ui-design/05-DESIGN.md` — Design token reference and prop contracts

**Summary of implementation:**
Phase 05-01 delivered a complete design-token system (color/spacing/typography/radius), restructured item/batch tables to card markup, and introduced a 599px responsive breakpoint. Phase 05-02 documented all 7 component prop contracts in JSDoc and in the canonical 05-DESIGN.md. The token system is comprehensive and well-adopted; colour and typography are excellent. The gaps are in UX presentation of state (loading, error) and one critical missing button style (Retry), which degrade the experience-design score.
