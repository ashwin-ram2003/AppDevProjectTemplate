---
phase: "05"
slug: "ui-design"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-24"
---

# Phase 05 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| MongoDB → Flask JSON → React render | User-supplied strings (`item.itemName`, `entry.userName`, `batch.purchaseDate`, `batch.bestByDate`) cross into the DOM via the restyled card markup | Item/batch/reservation field values |
| Repository → planning docs | `05-DESIGN.md` is a committed artifact describing component props and example values | Prop shapes, dev placeholder identities (`H1`/`alice`/`Alice`) |
| Repository → committed documentation (JSDoc) | `05-DESIGN.md` and in-source JSDoc blocks are read and trusted by Track A/Track C without re-reading source | Documented prop contracts |
| npm / pip / cargo package installs | Both plans in this phase install zero new packages | N/A — supply-chain surface not touched |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-05-01 | Tampering | `Project.js` `LocationSection` card markup; `BatchList.js` batch card markup | high | mitigate | Every user-controlled value stays a plain JSX child (React auto-escaping); no raw-HTML injection prop introduced. Verified: `grep -rc 'dangerouslySetInnerHTML' client/src/` returns zero non-zero lines. | closed |
| T-05-02 | Information Disclosure | `.planning/phases/05-ui-design/05-DESIGN.md` | low | mitigate | Doc records prop shapes and existing dev placeholders (`H1`/`alice`/`Alice`) only. Verified: `grep -rciE 'mongodb\+srv\|MONGO_URI\|SECRET_KEY' 05-DESIGN.md` returns 0. | closed |
| T-05-04 | Tampering | `FreshnessBadge` visual encoding — a food-safety signal | medium | mitigate | D-08 palette pass changes only `background-color`/`color`/`border-color`; text label and `title` tooltip preserved (WCAG 1.4.1). `FreshnessBadge.js` untouched by 05-01. Verified: `git log` shows FreshnessBadge.js touched only by the phase-02 origin commit and 05-02's JSDoc-only commit (`4e66b64`, diff adds only a comment block above the function, zero logic/JSX changed). | closed |
| T-05-05 | Information Disclosure | JSDoc `@param` examples in `client/src/components/*.js` | low | mitigate | No example value drawn from a live environment; only the already-committed `H1`/`alice`/`Alice` placeholders appear. Verified by direct read of all 5 modified component files during UAT — no live secrets or connection data in any JSDoc block. | closed |
| T-05-06 | Repudiation | Divergence between JSDoc contract and `05-DESIGN.md` | medium | mitigate | Source is authoritative on disagreement; `Data source:` tallies and every documented prop cross-checked against each component's real destructuring pattern. Verified by direct read-through during UAT (05-UAT.md tests 5–6): all 7 components' `@param` lists match their destructured props exactly, and 05-DESIGN.md's Component Prop Contracts section matches source. | closed |
| T-05-SC | Tampering | npm / pip / cargo installs | high | mitigate | Zero packages installed by either plan in this phase. Verified: `git diff --stat` across all phase-05 commits shows no changes to `client/package.json`, `client/package-lock.json`, or `server/requirements.txt`. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on (high) count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-24 | 6 | 6 | 0 | /gsd-verify-work 05 → /gsd-secure-phase 05 (orchestrator verification against register authored at plan time in 05-01-PLAN.md/05-02-PLAN.md) |

register_authored_at_plan_time: true (both 05-01-PLAN.md and 05-02-PLAN.md carry parseable `<threat_model>` blocks). ASVS level 1, threats_open: 0 at plan-authored register → short-circuit per secure-phase workflow §3: no deep L2/L3 auditor pass required.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer) — all 6 are `mitigate`, all verified closed
- [x] Accepted risks documented in Accepted Risks Log — none needed
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-24
