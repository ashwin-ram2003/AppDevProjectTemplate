---
phase: "05"
slug: "ui-design"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-24"
---

# Phase 05 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None detected — `client/package.json` has no test runner, no `*.test.*`/`*.spec.*` files exist anywhere under `client/` |
| **Config file** | none — Wave 0 N/A, no framework installed for this phase (out of scope) |
| **Quick run command** | N/A — no framework installed |
| **Full suite command** | N/A — no framework installed |
| **Estimated runtime** | N/A |

---

## Sampling Rate

- **After every task commit:** `npm --prefix client run build` (grounded in Phase 02 Task 4; ~5s) plus that task's grep gates. No behavioural test suite exists, so these confirm the artifact shape and that the client still compiles — they do not assert rendered behaviour, which stays manual.
- **After every plan wave:** Manual visual check at ≤599px and ≥600px viewport widths; manual doc-presence check against the 5 Success Criteria
- **Before `/gsd-verify-work`:** All 5 Success Criteria manually verified true
- **Max feedback latency:** N/A (manual verification, no automated suite)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-T1 (tracer) | 01 | 1 | SC-1, SC-3, SC-5 | T-05-01, T-05-02 | No raw-HTML sink introduced by the markup restructure; no credential in `05-DESIGN.md` | build + grep gates, then manual (visual) | `npm --prefix client run build`; `test -f client/dist/index.html`; `grep -cE '<table\|</table>\|colSpan' client/src/components/Project.js`; `grep -rc 'dangerouslySetInnerHTML' client/src/ \| grep -v ':0'` | ✅ commands ground out of Phase 02 Task 4 | ✅ green |
| 05-01-T2 | 01 | 1 | SC-2, SC-5 | T-05-04 | Freshness stays colour + label + tooltip, never colour alone (WCAG 1.4.1) | grep gates, then manual (visual) | `grep -oE '#[0-9a-fA-F]{3,8}' client/src/App.css \| wc -l`; `grep -c 'focus-visible' client/src/App.css`; `grep -c 'prefers-reduced-motion' client/src/App.css` | ✅ | ✅ green |
| 05-01-T3 | 01 | 1 | SC-1 | T-05-01 | Batch values render as plain JSX children | grep gates, then manual (visual) | `npm --prefix client run build`; `grep -cE '<table\|<thead\|<tbody' client/src/components/BatchList.js`; `grep -c 'MUST be rendered in the order' client/src/components/BatchList.js` | ✅ | ✅ green |
| 05-02-T1 | 02 | 2 | SC-4 | T-05-05, T-05-06 | JSDoc records no live-environment value; contract matches real destructuring | grep gates, then manual (doc review) | `grep -rc '@component' client/src/components/ \| awk -F: '{s+=$2} END {print s}'`; same for `Data source:` and `No hard-coded fallback:` (each must total 7) | ✅ | ✅ green |
| 05-02-T2 | 02 | 2 | SC-3, SC-4, SC-5 | T-05-02, T-05-06 | No credential or connection string in the committed doc; doc agrees with source | grep gates, then manual (doc review) | `grep -c '^### ' .planning/phases/05-ui-design/05-DESIGN.md`; token-coverage loop over `client/src/index.css`; `grep -rciE 'mongodb\+srv\|MONGO_URI\|SECRET_KEY' .planning/phases/05-ui-design/05-DESIGN.md` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Updated 2026-09-24 against `05-01-PLAN.md` and `05-02-PLAN.md`. The phase still has no unit-test framework — the automated commands above are build and grep gates over the artifacts the plans produce, not behavioural assertions. Each task additionally carries a `<human-check>` block, collected at the end-of-phase verification per `workflow.human_verify_mode: end-of-phase`.*

---

## Wave 0 Requirements

*None: this phase has no REQ-IDs (board items use `DESIGN` in place of a requirement ID) and its 5 Success Criteria are inherently visual/documentation checks, not logic under test. Installing a client-side test framework (Jest/Vitest/Testing Library) to automate them is explicitly out of scope for this phase's locked decisions (D-01–D-08) — flagged as a known gap, not a blocker.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions | Status |
|----------|-------------|------------|-------------------|--------|
| Inventory view has clear visual grouping/spacing, usable at phone width | SC-1 | No visual-regression tooling exists; out of scope to add for this PoC | Resize browser / DevTools device toolbar to ≤599px width; confirm card layout renders, no horizontal scroll, no bare HTML table | ✅ verified 2026-09-24 — live app at 500px width, no horizontal scroll, card layout intact (05-UAT.md test 3) |
| Freshness badges use consistent, recognizable color coding | SC-2 | Visual/perceptual judgment, no automated color-semantics check | Compare rendered badge colors against the documented token palette in `05-DESIGN.md`; confirm each freshness state maps to a distinct, consistent color | ✅ verified 2026-09-24 — seeded fresh/expiring/expired items in live app, badges rendered distinct green/amber/red matching token palette |
| `InventoryView`'s session-identity props documented at call site | SC-3 | Doc-presence check, no doc-linter configured | Confirm `App.js` has an inline comment/JSDoc referencing `05-DESIGN.md`, and `05-DESIGN.md` documents `householdId`/`userId`/`userName` | ✅ verified 2026-09-24 — `App.js:17` comment references 05-DESIGN.md; contract documented there |
| Every presentational component's data-only prop contract documented | SC-4 | Doc-presence check, no JSDoc-linter configured | Confirm a JSDoc block exists above each of the 6 components' function signatures, describing props with no internal fetch / no hard-coded fallback | ✅ verified 2026-09-24 — read all 5 modified component files directly; all 7 component functions' JSDoc @param lists match real destructuring exactly (05-UAT.md test 5) |
| Shared style-token set exists and is documented | SC-5 | Doc-presence + visual check, no tooling to automate | Confirm `:root` custom properties exist in `index.css` and are referenced/listed in `05-DESIGN.md` | ✅ verified 2026-09-24 — 05-DESIGN.md Design Tokens section cross-checked against index.css (05-UAT.md test 6) |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — every task row above carries build/grep gates, re-run 2026-09-24 and confirmed green (see Per-Task Verification Map)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — all 5 tasks have automated commands
- [x] Wave 0 covers all MISSING references — **N/A**, no Wave 0 gaps block this phase
- [x] No watch-mode flags — N/A, no test commands
- [x] Feedback latency < N/A s — N/A
- [ ] `nyquist_compliant: true` set in frontmatter — left `false`; this phase's locked decisions (D-01–D-08) explicitly scope out installing a client-side test framework (Jest/Vitest/Testing Library), so verification stays build+grep automation plus a manual visual/doc pass rather than a full behavioral test suite. This is a documented, intentional scope boundary, not an unaddressed gap — all 5 manual-only success criteria above are now verified.

**Approval:** approved 2026-09-24 (via /gsd-verify-work → /gsd-validate-phase audit)

## Validation Audit 2026-09-24

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

All 5 per-task automated commands (build + grep gates) re-run and confirmed green. All 5 manual-only success criteria (SC-1 through SC-5) verified via live browser session (claude-in-chrome against a locally seeded MongoDB + Flask + Vite dev stack) and direct source/doc cross-reads. No test-framework gap — out-of-scope per locked decisions D-01–D-08, not an oversight.
