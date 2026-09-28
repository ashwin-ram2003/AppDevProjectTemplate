# HaaS Resource Manager PoC (Group 2 Monday — ECE 461L Team Project)

## What This Is

A Proof-of-Concept web application implementing the assignment's Hardware-as-a-Service (HaaS)
system directly: users create secure accounts, create or join a project, and use it to view,
request, check out, and check in named hardware sets (HWSet1, HWSet2, ... — any number of
named sets, not hard-limited to two) — all backed by a live database. Each hardware set has a
total `capacity` and a remaining `available` count, matching the assignment's Figure 3 mockup
exactly. Built with a Flask/MongoDB backend and a React frontend (starter scaffold in `server/`
and `client/`).

**Domain note (mid-project pivot, 2026-09):** an earlier iteration of this project reframed the
generic HaaS domain as a household food-inventory tracker (PantryTrack) — food items instead of
hardware sets, pantry/fridge/freezer locations, freshness flags, purchase-batch history. That
reframing has been reverted; this document and the codebase now implement the assignment's
generic hardware-resource domain as originally specified. Prior Key Decisions below that
reference the food-domain era are kept for their still-valid *structural* content (architecture,
process decisions) with their subject matter generalized.

## Core Value

A project member can see what hardware sets a project has, request/check out units they need,
and check units back in — all from live shared data, with no hard-coded values anywhere in the
app.

## Business Context

- **Customer**: Course instructor (Dr. Samant) and TAs, grading against the Team Project rubric (ECE 461L, Fa26)
- **Revenue model**: N/A — academic PoC, not monetized
- **Success metric**: Phase 1 (5 pts) and Phase 2 (10 pts) rubric criteria fully met; app hosted and reachable via URL by end of Phase 2
- **Strategy notes**: See `Team Project_Fa26.pdf` in repo root for the full assignment spec. POWDER (cited in the PDF) is inspiration for the general HaaS shape only — nothing wireless/RF-specific applies here.
- **Team structure**: The team has 4 developers on 4 tracks (Track A: Account & Project Management, Track B: Hardware Resource Management, Track C: Data Integration & API, Track D: Deployment & Quality). Each track owns exactly one Phase 1 rubric item and one Phase 2 rubric item, except Track C, whose Phase 2 scope is a promoted stretch feature (STRETCH-02) instead of a numbered R2 item. **Rescoped 2026-09-28:** Track D was originally backloaded — real work (meaningful tests, actual deploy) mostly gated on every other track finishing first, leaving its developer largely idle mid-project. Rebalanced: Track D now also owns early CI/CD setup (real Day-1 work, not scaffolding), writes backend tests incrementally alongside each track's route work instead of in one end-of-project batch, and picks up the password-reset stretch feature (STRETCH-01, moved from Track C) as standalone feature work buildable once Track A's login lands.

## Requirements

### Validated

- ✓ Starter scaffold exists — Flask backend (`app.py`, `usersDatabase.py`, `projectsDatabase.py`, `hardwareDatabase.py`) and React frontend — pre-existing, generic naming matches the assignment's own "project"/"hardware set" vocabulary directly, no relabeling needed
- ✓ Backend route surface: `/login`, `/main`, `/join_project`, `/add_user`, `/get_user_projects_list`, `/create_project`, `/get_project_info`, `/api/hardware`, `/api/hardware/checkin`, `/api/hardware/checkout` (plus request/release if a project keeps the reservation concept — see Track B's own record for the exact final shape)
- ✓ View hardware set status — capacity and availability per named set (SN2) — Track B, Phase 2 (Track B), UAT passed
- ✓ Request available hardware resources (SN3) — Track B
- ✓ Checkout/manage hardware resources (SN4) — Track B, overbooking guard with optimistic concurrency (race-tested against a real MongoDB, not mongomock)
- ✓ Check-in hardware resources and see status (SN5) — Track B
- ✓ Persist hardware resources in MongoDB, no hard-coded data (SR5, R2-2 half) — Track B's half; user/project half remains Track A's responsibility
- ✓ REST API layer for hardware resource operations (SR2, R2-1 half) — Track B's half

### Active

**MVP (must satisfy SN1–SN6):**

- [ ] Secure sign-in / new-user creation (SN1)
- [ ] Userid/password encryption (SN1, SR3)
- [ ] Create new project (name, description, projectID) (SN1, SR4)
- [ ] Join / access existing project by projectID (SN1, SR4)
- [ ] Persist users and project membership in MongoDB — no hard-coded data on any page (SR5, R2-2 remainder — Track A's half; Track B's hardware-resource half is validated above)
- [ ] REST API layer for user/project operations (SR2, R2-1 remainder — Track A's half; Track B's hardware half is validated above)
- [ ] Cloud hosting reachable via URL for TAs/instructor (R2-3)
- [ ] Project board with all features + initial work items (user stories, tech debt, research items) (R1-2)
- [ ] High-level architecture sketch (R1-3)
- [ ] Password reset via the existing Forgot Password flow (STRETCH-01, Track D)
- [ ] Explicit hardware-set-type management — create/rename/deactivate a type without checking something in first (STRETCH-02, Track C; the base model already supports any number of named sets created implicitly on checkin — see RES-05, already validated)
- [ ] CI/CD pipeline running tests + client build on every PR, set up early rather than as a late add-on (part of Track D's rescoped Phase 2 work)

### Backlog / Research Items (explicitly NOT in this PoC's committed scope)

- Automatic hardware-usage capture via sensors/telemetry instead of manual checkout/checkin
- Usage analytics and forecasting (which hardware sets run low, when)
- Automated reordering/procurement suggestions
- Per-user behavior adaptation (e.g., typical checkout duration, frequent requesters)
- Notifications (checkout reminders, low-availability alerts)

### Out of Scope

- OAuth / third-party login — assignment scope is username/password only; SN1 only requires "secure user accounts"
- Real-time multi-user live sync (e.g. websockets) — refresh-based updates are sufficient for the PoC
- Mobile app — web-only PoC per SR2
- Any physical sensor/hardware integration — no hardware budget or timeline for this course project; see Backlog above
- Billing/payment — not a stakeholder need
- Per-location/storage grouping of hardware sets — the assignment's mockup shows a flat list of named hardware sets with no location dimension; not part of this PoC

## Context

- This is a graded academic team project (ECE 461L), delivered in phases with a shared grading rubric (`Team Project_Fa26.pdf`).
- Phase 1 (5 pts, due first) requires: all features + initial work items on a board, a high-level sketch of the app, and a stated tool/approach choice — plus a separate Project Plan (team members, sprint cadence, collaboration tools, methodology, toolchain), which is **owned by another team member and out of scope for this document**.
- Phase 2 (10 pts) requires all General Requirements satisfied: hardware resources stored in DB with an API, user/project info accessible from the app with no hard-coded data, and the app hosted on the cloud and reachable via URL.
- General requirements apply across all phases: issue tracker kept separate from the user-story board, all user stories defined by end of Phase 1 (refined later), each user story describable in ≤3 sentences.
- The assignment's "HWSet1/HWSet2, capacity/availability, request/checkout/check-in" UI mockup (Figures 2–3) is implemented directly, not reframed onto another domain: capacity = total units of that hardware set, availability = units not yet checked out.

## Constraints

- **Tech stack**: Flask + MongoDB + React — matches the existing scaffold (stack choice/toolchain is documented in the separate Project Plan)
- **Process**: User stories must be ≤3 sentences (Mountain Goat Software style); issues (bugs/improvements) tracked separately from user-story board, not combined
- **Security**: Userid and password must be encrypted at rest/in transit (SR3) — non-negotiable rubric item
- **Domain simplification**: No physical sensors are available or in scope — all hardware-set capture (checking in/out) is manual user input via the web UI, not automated detection

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Build on existing `server/`/`client/` scaffold rather than starting fresh | Scaffold already encodes the assignment's expected route surface and DB module boundaries | ✓ Good |
| Implement the assignment's generic HaaS/hardware-resource domain directly, after reverting an earlier food-inventory reframing | The food-domain reframing added scope (freshness rules, batch history, per-item fuzzy matching) beyond the assignment's actual ask; the generic domain is what's graded | ✓ Good |
| Skip formal research phase (stack/features/architecture) | Assignment PDF fully specifies stakeholder needs, requirements, and recommended stack — external research adds no value here | ✓ Good |
| Skip codebase-mapping subagent | Existing scaffold is small (4 backend files, handful of React pages); read directly instead of spawning a mapper | ✓ Good |
| Hardware sets live in a separate collection, not embedded in the project document (Track B execution checkpoint, one-way door) | Removes the Track A/Track B write-contention risk the roadmap had flagged; makes the overbooking guard a single conditional update instead of a nested-array update | ✓ Good |
| A hardware set's `available` count is a plain running total (capacity minus checked-out units), no per-checkin batch history | The generic domain has no need for FIFO/expiration ordering — that was a food-specific requirement (best-by dates) that doesn't apply to reusable hardware | ✓ Good |
| Track B's tracer plan (02-01) bootstrapped the React client (`package.json`, Vite) and fixed Flask's broken imports, since neither existed/worked before this phase | The scaffold could not run at all — no track could proceed without this; flagged as a cross-track coordination point so other tracks build into the same shell | ✓ Good |
| Phase 05/06 (Track E: UI Design) established a design-token system (color/spacing/typography) and a table-based resource-management layout for the frontend | Applies generically to any tabular resource-status view; only the food-specific *content* it originally carried needed to be dropped in the domain revert, not the underlying visual system or layout approach | ✓ Good |
| Rescoped Track D's workload — added early CI/CD ownership (TD-16), made backend test-writing incremental/paired with each track instead of one end-of-project batch (TD-09), and moved the password-reset stretch feature (STRETCH-01) from Track C to Track D | Track D's original scope was backloaded: thin Day-1 scaffolding, then real work (meaningful tests, actual deploy) gated on every other track finishing — leaving its developer largely idle for a class project with graded individual contribution expectations. STRETCH-01 gives it standalone feature work buildable once Track A's login exists (mid-project, not end-loaded) | — Pending |
| Narrowed STRETCH-02 (Track C's remaining stretch feature) from "arbitrary hardware sets" to "explicit hardware-set-type management" | The base data model built in Track B already supports any number of named sets, created implicitly on first checkin (RES-05) — the original stretch description was redundant with core scope already shipped; the real remaining gap is explicit type management (create/rename/deactivate without a checkin) | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-28 — reverted the food-inventory domain reframing back to the assignment's generic HaaS/hardware-resource domain, then rescoped Track D's workload (early CI/CD, incremental testing, moved password-reset stretch feature from Track C) so it isn't idle for most of the project*
